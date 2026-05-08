from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from .compiler_service import build_ast_only, run_tyc_program
from .limits import load_limits
from .schemas import AstRequest, HealthResponse, RunRequest, RunResponse


limits = load_limits()
run_semaphore = asyncio.Semaphore(limits.max_concurrent_runs)

app = FastAPI(title="tyc-runner-openspec", version="0.1.0")

allowed_origins_raw = os.getenv("TYC_ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/api/v1/run", response_model=RunResponse)
async def run_program(payload: RunRequest) -> RunResponse:
    timeout_seconds = payload.timeoutSeconds or limits.default_timeout_seconds
    if timeout_seconds > limits.max_timeout_seconds:
        raise HTTPException(
            status_code=422,
            detail=f"timeoutSeconds must be <= {limits.max_timeout_seconds}",
        )

    async with run_semaphore:
        return await run_in_threadpool(
            run_tyc_program,
            payload.source,
            payload.stdin,
            timeout_seconds,
            payload.includeAst,
            limits,
        )


@app.post("/api/v1/ast", response_model=RunResponse)
async def ast_only(payload: AstRequest) -> RunResponse:
    return await run_in_threadpool(build_ast_only, payload.source, limits)
