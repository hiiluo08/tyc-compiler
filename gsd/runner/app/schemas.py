from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, StrictBool, field_validator

from .limits import DEFAULT_TIMEOUT_SECONDS, MAX_TIMEOUT_SECONDS


class Status(str, Enum):
    SUCCESS = "success"
    LEXICAL_ERROR = "lexical_error"
    SYNTAX_ERROR = "syntax_error"
    AST_ERROR = "ast_error"
    SEMANTIC_ERROR = "semantic_error"
    CODEGEN_ERROR = "codegen_error"
    ASSEMBLY_ERROR = "assembly_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    INPUT_TOO_LARGE = "input_too_large"
    INTERNAL_ERROR = "internal_error"


class DiagnosticStage(str, Enum):
    LEX = "lex"
    PARSE = "parse"
    AST = "ast"
    SEMANTIC = "semantic"
    CODEGEN = "codegen"
    ASSEMBLE = "assemble"
    RUN = "run"
    INTERNAL = "internal"


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class StageResult(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Diagnostic(BaseModel):
    stage: DiagnosticStage
    severity: DiagnosticSeverity
    message: str
    line: int | None = None
    column: int | None = None
    raw: str


class StageStatus(BaseModel):
    parse: StageResult = StageResult.SKIPPED
    ast: StageResult = StageResult.SKIPPED
    semantic: StageResult = StageResult.SKIPPED
    codegen: StageResult = StageResult.SKIPPED
    assemble: StageResult = StageResult.SKIPPED
    run: StageResult = StageResult.SKIPPED


class TruncatedFlags(BaseModel):
    stdout: bool = False
    stderr: bool = False


class HealthResponse(BaseModel):
    ok: bool
    service: str
    version: str


class RunRequest(BaseModel):
    source: str
    stdin: str = ""
    timeoutSeconds: int = Field(default=DEFAULT_TIMEOUT_SECONDS, ge=1, le=MAX_TIMEOUT_SECONDS)
    includeAst: StrictBool = True

    @field_validator("source")
    @classmethod
    def validate_source_not_empty(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("source must not be empty")
        return value


class AstRequest(BaseModel):
    source: str

    @field_validator("source")
    @classmethod
    def validate_source_not_empty(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("source must not be empty")
        return value


class RunResponse(BaseModel):
    ok: bool
    status: Status
    stdout: str = ""
    stderr: str = ""
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    astText: str | None = None
    astJson: Any | None = None
    stages: StageStatus = Field(default_factory=StageStatus)
    durationMs: int = 0
    truncated: TruncatedFlags = Field(default_factory=TruncatedFlags)


class AstResponse(BaseModel):
    ok: bool
    status: Status
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    astText: str | None = None
    astJson: Any | None = None
    durationMs: int = 0
