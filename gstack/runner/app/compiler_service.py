import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from antlr4 import CommonTokenStream, InputStream

from runner.build.TyCLexer import TyCLexer
from runner.build.TyCParser import TyCParser
from runner.compiler_vendor.astgen.ast_generation import ASTGeneration
from runner.compiler_vendor.codegen.codegen import CodeGenerator
from runner.compiler_vendor.grammar.lexererr import ErrorToken, IllegalEscape, UncloseString
from runner.compiler_vendor.semantics.static_checker import StaticChecker
from runner.compiler_vendor.semantics.static_error import StaticError
from runner.compiler_vendor.utils.error_listener import NewErrorListener, SyntaxException

from .ast_serializer import serialize_ast
from .limits import MAX_OUTPUT_BYTES
from .runtime_workspace import RuntimeWorkspace
from .schemas import (
    Diagnostic,
    DiagnosticSeverity,
    DiagnosticStage,
    StageResult,
    StageStatus,
    Status,
)

STAGE_ORDER = ["parse", "ast", "semantic", "codegen", "assemble", "run"]


@dataclass
class ServiceResult:
    status: Status
    diagnostics: list[Diagnostic] = field(default_factory=list)
    stages: StageStatus = field(default_factory=StageStatus)
    stdout: str = ""
    stderr: str = ""
    astText: str | None = None
    astJson: dict | list | str | int | float | bool | None = None
    durationMs: int = 0
    truncatedStdout: bool = False
    truncatedStderr: bool = False


def _diag(stage: DiagnosticStage, message: str, raw: str, line: int | None = None, column: int | None = None) -> Diagnostic:
    return Diagnostic(
        stage=stage,
        severity=DiagnosticSeverity.ERROR,
        message=message,
        line=line,
        column=column,
        raw=raw,
    )


def _stages_for_failure(failed_stage: str) -> StageStatus:
    mapping: dict[str, StageResult] = {}
    seen_failed = False
    for stage in STAGE_ORDER:
        if seen_failed:
            mapping[stage] = StageResult.SKIPPED
            continue
        if stage == failed_stage:
            mapping[stage] = StageResult.FAILED
            seen_failed = True
        else:
            mapping[stage] = StageResult.SUCCESS
    return StageStatus(**mapping)


def _stages_success() -> StageStatus:
    return StageStatus(
        parse=StageResult.SUCCESS,
        ast=StageResult.SUCCESS,
        semantic=StageResult.SUCCESS,
        codegen=StageResult.SUCCESS,
        assemble=StageResult.SUCCESS,
        run=StageResult.SUCCESS,
    )


def _parse_line_col(raw: str) -> tuple[int | None, int | None]:
    m = re.search(r"line\s+(\d+)\s+col\s+(\d+)", raw)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def _truncate_text(value: str) -> tuple[str, bool]:
    payload = value.encode("utf-8")
    if len(payload) <= MAX_OUTPUT_BYTES:
        return value, False
    truncated_bytes = payload[:MAX_OUTPUT_BYTES]
    truncated_text = truncated_bytes.decode("utf-8", errors="ignore")
    return truncated_text, True


def _elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


class CompilerService:
    def __init__(self) -> None:
        runner_dir = Path(__file__).resolve().parents[1]
        self.runtime_assets_dir = runner_dir / "runtime_assets"

    def _parse_to_ast(self, source: str):
        input_stream = InputStream(source)
        lexer = TyCLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = TyCParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(NewErrorListener.INSTANCE)
        parse_tree = parser.program()
        return ASTGeneration().visit(parse_tree)

    def run_pipeline(self, source: str, stdin: str, timeout_seconds: int, include_ast: bool = True) -> ServiceResult:
        started_at = time.perf_counter()
        ast = None
        ast_text = None
        ast_json = None

        try:
            ast = self._parse_to_ast(source)
            ast_text = str(ast)
            ast_json = serialize_ast(ast)
        except (ErrorToken, UncloseString, IllegalEscape) as exc:
            msg = str(exc)
            return ServiceResult(
                status=Status.LEXICAL_ERROR,
                diagnostics=[_diag(DiagnosticStage.LEX, msg, msg)],
                stages=_stages_for_failure("parse"),
                durationMs=_elapsed_ms(started_at),
            )
        except SyntaxException as exc:
            raw = str(exc)
            line, col = _parse_line_col(raw)
            return ServiceResult(
                status=Status.SYNTAX_ERROR,
                diagnostics=[_diag(DiagnosticStage.PARSE, raw, raw, line, col)],
                stages=_stages_for_failure("parse"),
                durationMs=_elapsed_ms(started_at),
            )
        except Exception as exc:
            raw = str(exc)
            return ServiceResult(
                status=Status.AST_ERROR,
                diagnostics=[_diag(DiagnosticStage.AST, "ast generation failed", raw)],
                stages=_stages_for_failure("ast"),
                durationMs=_elapsed_ms(started_at),
            )

        ast_payload_text = ast_text if include_ast else None
        ast_payload_json = ast_json if include_ast else None

        try:
            StaticChecker().check_program(ast)
        except StaticError as exc:
            raw = str(exc)
            return ServiceResult(
                status=Status.SEMANTIC_ERROR,
                diagnostics=[_diag(DiagnosticStage.SEMANTIC, raw, raw)],
                stages=_stages_for_failure("semantic"),
                astText=ast_payload_text,
                astJson=ast_payload_json,
                durationMs=_elapsed_ms(started_at),
            )
        except Exception as exc:
            raw = str(exc)
            return ServiceResult(
                status=Status.INTERNAL_ERROR,
                diagnostics=[_diag(DiagnosticStage.INTERNAL, "internal error", raw)],
                stages=_stages_for_failure("semantic"),
                astText=ast_payload_text,
                astJson=ast_payload_json,
                durationMs=_elapsed_ms(started_at),
            )

        try:
            with RuntimeWorkspace(self.runtime_assets_dir) as workspace:
                try:
                    CodeGenerator(output_dir=str(workspace.path)).visit(ast)
                except Exception as exc:
                    raw = str(exc)
                    return ServiceResult(
                        status=Status.CODEGEN_ERROR,
                        diagnostics=[_diag(DiagnosticStage.CODEGEN, raw, raw)],
                        stages=_stages_for_failure("codegen"),
                        astText=ast_payload_text,
                        astJson=ast_payload_json,
                        durationMs=_elapsed_ms(started_at),
                    )

                try:
                    assembly = workspace.assemble(timeout_seconds)
                except subprocess.TimeoutExpired:
                    message = f"Program exceeded {timeout_seconds} seconds."
                    return ServiceResult(
                        status=Status.TIMEOUT,
                        diagnostics=[_diag(DiagnosticStage.ASSEMBLE, message, "timeout")],
                        stages=_stages_for_failure("assemble"),
                        astText=ast_payload_text,
                        astJson=ast_payload_json,
                        durationMs=_elapsed_ms(started_at),
                    )

                assembly_stderr, assembly_truncated = _truncate_text(assembly.stderr or "")
                if assembly.returncode != 0:
                    return ServiceResult(
                        status=Status.ASSEMBLY_ERROR,
                        diagnostics=[_diag(DiagnosticStage.ASSEMBLE, "assembly error", assembly_stderr)],
                        stages=_stages_for_failure("assemble"),
                        stderr=assembly_stderr,
                        astText=ast_payload_text,
                        astJson=ast_payload_json,
                        durationMs=_elapsed_ms(started_at),
                        truncatedStderr=assembly_truncated,
                    )

                try:
                    run = workspace.execute(stdin=stdin, timeout_seconds=timeout_seconds)
                except subprocess.TimeoutExpired:
                    message = f"Program exceeded {timeout_seconds} seconds."
                    return ServiceResult(
                        status=Status.TIMEOUT,
                        diagnostics=[_diag(DiagnosticStage.RUN, message, "timeout")],
                        stages=_stages_for_failure("run"),
                        astText=ast_payload_text,
                        astJson=ast_payload_json,
                        durationMs=_elapsed_ms(started_at),
                    )

                stdout, stdout_truncated = _truncate_text(run.stdout or "")
                stderr, stderr_truncated = _truncate_text(run.stderr or "")

                if run.returncode != 0:
                    return ServiceResult(
                        status=Status.RUNTIME_ERROR,
                        diagnostics=[_diag(DiagnosticStage.RUN, "runtime error", stderr)],
                        stages=_stages_for_failure("run"),
                        stdout=stdout,
                        stderr=stderr,
                        astText=ast_payload_text,
                        astJson=ast_payload_json,
                        durationMs=_elapsed_ms(started_at),
                        truncatedStdout=stdout_truncated,
                        truncatedStderr=stderr_truncated,
                    )

                return ServiceResult(
                    status=Status.SUCCESS,
                    diagnostics=[],
                    stages=_stages_success(),
                    stdout=stdout,
                    stderr=stderr,
                    astText=ast_payload_text,
                    astJson=ast_payload_json,
                    durationMs=_elapsed_ms(started_at),
                    truncatedStdout=stdout_truncated,
                    truncatedStderr=stderr_truncated,
                )
        except Exception as exc:
            raw = str(exc)
            return ServiceResult(
                status=Status.INTERNAL_ERROR,
                diagnostics=[_diag(DiagnosticStage.INTERNAL, "internal error", raw)],
                stages=_stages_for_failure("run"),
                astText=ast_payload_text,
                astJson=ast_payload_json,
                durationMs=_elapsed_ms(started_at),
            )

    def build_ast(self, source: str) -> ServiceResult:
        started_at = time.perf_counter()
        try:
            ast = self._parse_to_ast(source)
            return ServiceResult(
                status=Status.SUCCESS,
                diagnostics=[],
                stages=StageStatus(
                    parse=StageResult.SUCCESS,
                    ast=StageResult.SUCCESS,
                    semantic=StageResult.SKIPPED,
                    codegen=StageResult.SKIPPED,
                    assemble=StageResult.SKIPPED,
                    run=StageResult.SKIPPED,
                ),
                astText=str(ast),
                astJson=serialize_ast(ast),
                durationMs=_elapsed_ms(started_at),
            )
        except (ErrorToken, UncloseString, IllegalEscape) as exc:
            msg = str(exc)
            return ServiceResult(
                status=Status.LEXICAL_ERROR,
                diagnostics=[_diag(DiagnosticStage.LEX, msg, msg)],
                stages=_stages_for_failure("parse"),
                durationMs=_elapsed_ms(started_at),
            )
        except SyntaxException as exc:
            raw = str(exc)
            line, col = _parse_line_col(raw)
            return ServiceResult(
                status=Status.SYNTAX_ERROR,
                diagnostics=[_diag(DiagnosticStage.PARSE, raw, raw, line, col)],
                stages=_stages_for_failure("parse"),
                durationMs=_elapsed_ms(started_at),
            )
        except Exception as exc:
            raw = str(exc)
            return ServiceResult(
                status=Status.AST_ERROR,
                diagnostics=[_diag(DiagnosticStage.AST, "ast generation failed", raw)],
                stages=_stages_for_failure("ast"),
                durationMs=_elapsed_ms(started_at),
            )
