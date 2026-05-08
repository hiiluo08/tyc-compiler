from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import time

from antlr4 import CommonTokenStream, InputStream

from .ast_serializer import serialize_ast
from .limits import RunnerLimits, load_limits
from .runtime_workspace import request_workspace
from .schemas import Diagnostic, RunResponse, RunStatus, StageState, TruncatedFlags


BASE_DIR = Path(__file__).resolve().parent.parent
VENDOR_ROOT = BASE_DIR / "compiler_vendor"
VENDOR_BUILD_DIR = VENDOR_ROOT / "build"
VENDOR_SRC_ROOT = VENDOR_ROOT / "src"
RUNTIME_ASSETS_DIR = BASE_DIR / "runtime_assets"


def _bootstrap_vendor_paths() -> None:
    for path in [str(VENDOR_ROOT), str(VENDOR_BUILD_DIR), str(VENDOR_SRC_ROOT)]:
        if path not in sys.path:
            sys.path.insert(0, path)


_bootstrap_vendor_paths()

from build.TyCLexer import TyCLexer  # noqa: E402
from build.TyCParser import TyCParser  # noqa: E402
from lexererr import ErrorToken, IllegalEscape, UncloseString  # noqa: E402
from src.astgen.ast_generation import ASTGeneration  # noqa: E402
from src.codegen.codegen import CodeGenerator  # noqa: E402
from src.semantics.static_checker import StaticChecker  # noqa: E402
from src.utils.error_listener import NewErrorListener, SyntaxException  # noqa: E402


ALL_STAGES = ("parse", "ast", "semantic", "codegen", "assemble", "run")


def _new_stages() -> dict[str, StageState]:
    return {name: StageState.SKIPPED for name in ALL_STAGES}


def _duration_ms(start_time: float) -> int:
    return int((time.perf_counter() - start_time) * 1000)


def _parse_line_column(message: str) -> tuple[int | None, int | None]:
    match = re.search(r"line\s+(\d+)\s+col\s+(\d+)", message)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _truncate_text(text: str, max_bytes: int) -> tuple[str, bool]:
    raw = text.encode("utf-8")
    if len(raw) <= max_bytes:
        return text, False
    truncated = raw[:max_bytes].decode("utf-8", errors="ignore")
    return truncated, True


def _error_response(
    *,
    status: RunStatus,
    stage: str,
    message: str,
    raw: str,
    start_time: float,
    stages: dict[str, StageState],
    line: int | None = None,
    column: int | None = None,
    ast_text: str | None = None,
    ast_json=None,
    stderr: str = "",
    truncated: TruncatedFlags | None = None,
) -> RunResponse:
    return RunResponse(
        ok=False,
        status=status,
        stdout="",
        stderr=stderr,
        diagnostics=[
            Diagnostic(
                stage=stage,
                severity="error",
                message=message,
                line=line,
                column=column,
                raw=raw,
            )
        ],
        astText=ast_text,
        astJson=ast_json,
        stages=stages,
        durationMs=_duration_ms(start_time),
        truncated=truncated if truncated else TruncatedFlags(),
    )


def _copy_runtime_assets(dest_dir: Path) -> None:
    for filename in ("jasmin.jar", "io.class"):
        shutil.copy2(RUNTIME_ASSETS_DIR / filename, dest_dir / filename)


def _terminate_process_tree(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=False,
        )
    try:
        proc.kill()
    except Exception:
        pass


def _run_command(
    command: list[str],
    cwd: Path,
    timeout_seconds: int,
    input_data: str | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdin=subprocess.PIPE if input_data is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
    )
    try:
        stdout, stderr = proc.communicate(input=input_data, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_tree(proc)
        try:
            stdout, stderr = proc.communicate(timeout=3)
        except Exception:
            stdout = exc.output or ""
            stderr = exc.stderr or ""
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)


def _assemble_jasmin(workspace: Path, timeout_seconds: int) -> tuple[bool, str]:
    j_files = sorted(workspace.glob("*.j"))
    if not j_files:
        return False, "No Jasmin files generated"

    stderr_merged = []
    for j_file in j_files:
        proc = _run_command(["java", "-jar", "jasmin.jar", j_file.name], workspace, timeout_seconds)
        if proc.stderr:
            stderr_merged.append(proc.stderr)
        if proc.returncode != 0:
            return False, "\n".join(stderr_merged) if stderr_merged else "Jasmin assembly failed"
    return True, "\n".join(stderr_merged)


def _run_jvm(workspace: Path, stdin_data: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    return _run_command(["java", "-cp", str(workspace), "TyC"], workspace, timeout_seconds, input_data=stdin_data)


def run_tyc_program(
    source: str,
    stdin: str = "",
    timeout_seconds: int | None = None,
    include_ast: bool = True,
    limits: RunnerLimits | None = None,
) -> RunResponse:
    limits = limits or load_limits()
    timeout_seconds = timeout_seconds or limits.default_timeout_seconds
    start_time = time.perf_counter()
    stages = _new_stages()

    if len(source.encode("utf-8")) > limits.max_source_bytes:
        return _error_response(
            status=RunStatus.INPUT_TOO_LARGE,
            stage="internal",
            message="Source exceeds maximum allowed size.",
            raw="source_too_large",
            start_time=start_time,
            stages=stages,
        )

    if len(stdin.encode("utf-8")) > limits.max_stdin_bytes:
        return _error_response(
            status=RunStatus.INPUT_TOO_LARGE,
            stage="internal",
            message="Stdin exceeds maximum allowed size.",
            raw="stdin_too_large",
            start_time=start_time,
            stages=stages,
        )

    ast_text = None
    ast_json = None

    try:
        input_stream = InputStream(source)
        lexer = TyCLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = TyCParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(NewErrorListener.INSTANCE)
        parse_tree = parser.program()
        stages["parse"] = StageState.SUCCESS
    except (ErrorToken, UncloseString, IllegalEscape) as exc:
        stages["parse"] = StageState.FAILED
        return _error_response(
            status=RunStatus.LEXICAL_ERROR,
            stage="lex",
            message=str(exc),
            raw=str(exc),
            start_time=start_time,
            stages=stages,
        )
    except SyntaxException as exc:
        stages["parse"] = StageState.FAILED
        line, column = _parse_line_column(str(exc))
        return _error_response(
            status=RunStatus.SYNTAX_ERROR,
            stage="parse",
            message=str(exc),
            raw=str(exc),
            line=line,
            column=column,
            start_time=start_time,
            stages=stages,
        )
    except Exception as exc:
        stages["parse"] = StageState.FAILED
        return _error_response(
            status=RunStatus.INTERNAL_ERROR,
            stage="internal",
            message="Unexpected parser failure.",
            raw=str(exc),
            start_time=start_time,
            stages=stages,
        )

    try:
        ast = ASTGeneration().visit(parse_tree)
        stages["ast"] = StageState.SUCCESS
        if include_ast:
            ast_text = str(ast)
            ast_json = serialize_ast(ast)
    except Exception as exc:
        stages["ast"] = StageState.FAILED
        return _error_response(
            status=RunStatus.AST_ERROR,
            stage="ast",
            message="AST generation failed.",
            raw=str(exc),
            start_time=start_time,
            stages=stages,
        )

    try:
        StaticChecker().check_program(ast)
        stages["semantic"] = StageState.SUCCESS
    except Exception as exc:
        stages["semantic"] = StageState.FAILED
        return _error_response(
            status=RunStatus.SEMANTIC_ERROR,
            stage="semantic",
            message=str(exc),
            raw=str(exc),
            ast_text=ast_text,
            ast_json=ast_json,
            start_time=start_time,
            stages=stages,
        )

    try:
        with request_workspace() as workspace:
            _copy_runtime_assets(workspace)

            codegen = CodeGenerator(output_dir=str(workspace))
            try:
                codegen.visit(ast)
                stages["codegen"] = StageState.SUCCESS
            except Exception as exc:
                stages["codegen"] = StageState.FAILED
                return _error_response(
                    status=RunStatus.CODEGEN_ERROR,
                    stage="codegen",
                    message="Code generation failed.",
                    raw=str(exc),
                    ast_text=ast_text,
                    ast_json=ast_json,
                    start_time=start_time,
                    stages=stages,
                )

            try:
                assembled, asm_stderr = _assemble_jasmin(workspace, timeout_seconds)
                if not assembled:
                    stages["assemble"] = StageState.FAILED
                    err_text, stderr_truncated = _truncate_text(asm_stderr, limits.max_output_bytes)
                    return _error_response(
                        status=RunStatus.ASSEMBLY_ERROR,
                        stage="assemble",
                        message="Jasmin assembly failed.",
                        raw=asm_stderr or "Jasmin assembly failed",
                        stderr=err_text,
                        ast_text=ast_text,
                        ast_json=ast_json,
                        truncated=TruncatedFlags(stdout=False, stderr=stderr_truncated),
                        start_time=start_time,
                        stages=stages,
                    )
                stages["assemble"] = StageState.SUCCESS
            except subprocess.TimeoutExpired:
                stages["assemble"] = StageState.FAILED
                return _error_response(
                    status=RunStatus.TIMEOUT,
                    stage="assemble",
                    message=f"Program exceeded {timeout_seconds} seconds.",
                    raw="assembly_timeout",
                    ast_text=ast_text,
                    ast_json=ast_json,
                    start_time=start_time,
                    stages=stages,
                )

            try:
                run_result = _run_jvm(workspace, stdin, timeout_seconds)
            except subprocess.TimeoutExpired:
                stages["run"] = StageState.FAILED
                return _error_response(
                    status=RunStatus.TIMEOUT,
                    stage="run",
                    message=f"Program exceeded {timeout_seconds} seconds.",
                    raw="runtime_timeout",
                    ast_text=ast_text,
                    ast_json=ast_json,
                    start_time=start_time,
                    stages=stages,
                )

            stdout, stdout_truncated = _truncate_text(run_result.stdout or "", limits.max_output_bytes)
            stderr, stderr_truncated = _truncate_text(run_result.stderr or "", limits.max_output_bytes)
            trunc_flags = TruncatedFlags(stdout=stdout_truncated, stderr=stderr_truncated)

            if run_result.returncode != 0:
                stages["run"] = StageState.FAILED
                return _error_response(
                    status=RunStatus.RUNTIME_ERROR,
                    stage="run",
                    message="Program exited with runtime error.",
                    raw=run_result.stderr or f"exit_code={run_result.returncode}",
                    stderr=stderr,
                    ast_text=ast_text,
                    ast_json=ast_json,
                    truncated=trunc_flags,
                    start_time=start_time,
                    stages=stages,
                )

            stages["run"] = StageState.SUCCESS
            return RunResponse(
                ok=True,
                status=RunStatus.SUCCESS,
                stdout=stdout,
                stderr=stderr,
                diagnostics=[],
                astText=ast_text,
                astJson=ast_json,
                stages=stages,
                durationMs=_duration_ms(start_time),
                truncated=trunc_flags,
            )
    except Exception as exc:
        return _error_response(
            status=RunStatus.INTERNAL_ERROR,
            stage="internal",
            message="Unexpected internal error.",
            raw=str(exc),
            ast_text=ast_text,
            ast_json=ast_json,
            start_time=start_time,
            stages=stages,
        )


def build_ast_only(source: str, limits: RunnerLimits | None = None) -> RunResponse:
    limits = limits or load_limits()
    start_time = time.perf_counter()

    if len(source.encode("utf-8")) > limits.max_source_bytes:
        return _error_response(
            status=RunStatus.INPUT_TOO_LARGE,
            stage="internal",
            message="Source exceeds maximum allowed size.",
            raw="source_too_large",
            start_time=start_time,
            stages={"parse": StageState.SKIPPED, "ast": StageState.SKIPPED},
        )

    stages = {"parse": StageState.SKIPPED, "ast": StageState.SKIPPED}

    try:
        input_stream = InputStream(source)
        lexer = TyCLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = TyCParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(NewErrorListener.INSTANCE)
        parse_tree = parser.program()
        stages["parse"] = StageState.SUCCESS
    except (ErrorToken, UncloseString, IllegalEscape) as exc:
        stages["parse"] = StageState.FAILED
        return _error_response(
            status=RunStatus.LEXICAL_ERROR,
            stage="lex",
            message=str(exc),
            raw=str(exc),
            start_time=start_time,
            stages=stages,
        )
    except SyntaxException as exc:
        stages["parse"] = StageState.FAILED
        line, column = _parse_line_column(str(exc))
        return _error_response(
            status=RunStatus.SYNTAX_ERROR,
            stage="parse",
            message=str(exc),
            raw=str(exc),
            line=line,
            column=column,
            start_time=start_time,
            stages=stages,
        )

    try:
        ast = ASTGeneration().visit(parse_tree)
        stages["ast"] = StageState.SUCCESS
        return RunResponse(
            ok=True,
            status=RunStatus.SUCCESS,
            stdout="",
            stderr="",
            diagnostics=[],
            astText=str(ast),
            astJson=serialize_ast(ast),
            stages=stages,
            durationMs=_duration_ms(start_time),
            truncated=None,
        )
    except Exception as exc:
        stages["ast"] = StageState.FAILED
        return _error_response(
            status=RunStatus.AST_ERROR,
            stage="ast",
            message="AST generation failed.",
            raw=str(exc),
            start_time=start_time,
            stages=stages,
        )
