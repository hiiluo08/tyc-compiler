import os


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def utf8_size(value: str) -> int:
    return len(value.encode("utf-8"))


MAX_SOURCE_BYTES = _int_env("TYC_MAX_SOURCE_BYTES", 65536)
MAX_STDIN_BYTES = _int_env("TYC_MAX_STDIN_BYTES", 16384)
DEFAULT_TIMEOUT_SECONDS = max(1, _int_env("TYC_DEFAULT_TIMEOUT_SECONDS", 3))
MAX_TIMEOUT_SECONDS = max(DEFAULT_TIMEOUT_SECONDS, _int_env("TYC_MAX_TIMEOUT_SECONDS", 5))
MAX_OUTPUT_BYTES = _int_env("TYC_MAX_OUTPUT_BYTES", 32768)
MAX_CONCURRENT_RUNS = max(1, _int_env("TYC_MAX_CONCURRENT_RUNS", 2))
