from __future__ import annotations

from typing import Any


def serialize_ast(value: Any):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [serialize_ast(item) for item in value]
    if hasattr(value, "__dict__"):
        fields = {
            key: serialize_ast(val)
            for key, val in value.__dict__.items()
            if not key.startswith("_")
        }
        return {"kind": value.__class__.__name__, "fields": fields}
    return str(value)
