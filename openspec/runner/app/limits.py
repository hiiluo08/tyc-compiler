from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class RunnerLimits:
    default_timeout_seconds: int
    max_timeout_seconds: int
    max_source_bytes: int
    max_stdin_bytes: int
    max_output_bytes: int
    max_concurrent_runs: int


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw)


def load_limits() -> RunnerLimits:
    default_timeout = _int_env("TYC_DEFAULT_TIMEOUT_SECONDS", 3)
    max_timeout = _int_env("TYC_MAX_TIMEOUT_SECONDS", 5)
    return RunnerLimits(
        default_timeout_seconds=default_timeout,
        max_timeout_seconds=max_timeout,
        max_source_bytes=_int_env("TYC_MAX_SOURCE_BYTES", 65536),
        max_stdin_bytes=_int_env("TYC_MAX_STDIN_BYTES", 16384),
        max_output_bytes=_int_env("TYC_MAX_OUTPUT_BYTES", 32768),
        max_concurrent_runs=_int_env("TYC_MAX_CONCURRENT_RUNS", 2),
    )
