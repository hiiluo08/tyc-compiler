import os
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .compiler_service import CompilerService
from .limits import MAX_CONCURRENT_RUNS, MAX_SOURCE_BYTES, MAX_STDIN_BYTES, utf8_size
from .schemas import (
    AstRequest,
    AstResponse,
    Diagnostic,
    DiagnosticSeverity,
    DiagnosticStage,
    HealthResponse,
    RunRequest,
    RunResponse,
    StageStatus,
    Status,
    TruncatedFlags,
)

app = FastAPI(title="TyC Runner GStack", version="0.1.0")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "TYC_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = CompilerService()
run_semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_RUNS)


def _input_too_large_run_response(message: str) -> RunResponse:
    return RunResponse(
        ok=False,
        status=Status.INPUT_TOO_LARGE,
        diagnostics=[
            Diagnostic(
                stage=DiagnosticStage.INTERNAL,
                severity=DiagnosticSeverity.ERROR,
                message=message,
                line=None,
                column=None,
                raw=message,
            )
        ],
        stages=StageStatus(),
        durationMs=0,
        truncated=TruncatedFlags(stdout=False, stderr=False),
        astText=None,
        astJson=None,
    )


def _input_too_large_ast_response(message: str) -> AstResponse:
    return AstResponse(
        ok=False,
        status=Status.INPUT_TOO_LARGE,
        diagnostics=[
            Diagnostic(
                stage=DiagnosticStage.INTERNAL,
                severity=DiagnosticSeverity.ERROR,
                message=message,
                line=None,
                column=None,
                raw=message,
            )
        ],
        durationMs=0,
        astText=None,
        astJson=None,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, service="tyc-runner-gstack", version="0.1.0")


@app.post("/api/v1/run", response_model=RunResponse)
def run(payload: RunRequest) -> RunResponse:
    source_bytes = utf8_size(payload.source)
    if source_bytes > MAX_SOURCE_BYTES:
        return _input_too_large_run_response(f"source exceeds {MAX_SOURCE_BYTES} bytes")

    stdin_bytes = utf8_size(payload.stdin)
    if stdin_bytes > MAX_STDIN_BYTES:
        return _input_too_large_run_response(f"stdin exceeds {MAX_STDIN_BYTES} bytes")

    run_semaphore.acquire()
    try:
        result = service.run_pipeline(
            source=payload.source,
            stdin=payload.stdin,
            timeout_seconds=payload.timeoutSeconds,
            include_ast=payload.includeAst,
        )
    finally:
        run_semaphore.release()

    return RunResponse(
        ok=result.status == Status.SUCCESS,
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        diagnostics=result.diagnostics,
        astText=result.astText,
        astJson=result.astJson,
        stages=result.stages,
        durationMs=result.durationMs,
        truncated=TruncatedFlags(stdout=result.truncatedStdout, stderr=result.truncatedStderr),
    )


@app.post("/api/v1/ast", response_model=AstResponse)
def ast(payload: AstRequest) -> AstResponse:
    source_bytes = utf8_size(payload.source)
    if source_bytes > MAX_SOURCE_BYTES:
        return _input_too_large_ast_response(f"source exceeds {MAX_SOURCE_BYTES} bytes")

    result = service.build_ast(payload.source)
    return AstResponse(
        ok=result.status == Status.SUCCESS,
        status=result.status,
        diagnostics=result.diagnostics,
        astText=result.astText,
        astJson=result.astJson,
        durationMs=result.durationMs,
    )
