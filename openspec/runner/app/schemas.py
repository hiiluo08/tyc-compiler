from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
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


class StageState(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Diagnostic(BaseModel):
    stage: str
    severity: str = "error"
    message: str
    line: int | None = None
    column: int | None = None
    raw: str


class TruncatedFlags(BaseModel):
    stdout: bool = False
    stderr: bool = False


class RunRequest(BaseModel):
    source: str = Field(min_length=1)
    stdin: str = ""
    timeoutSeconds: int | None = Field(default=None, ge=1)
    includeAst: bool = True


class AstRequest(BaseModel):
    source: str = Field(min_length=1)


class RunResponse(BaseModel):
    ok: bool
    status: RunStatus
    stdout: str = ""
    stderr: str = ""
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    astText: str | None = None
    astJson: dict | list | str | int | float | bool | None = None
    stages: dict[str, StageState] | None = None
    durationMs: int
    truncated: TruncatedFlags | None = None


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "tyc-runner-openspec"
    version: str = "0.1.0"
