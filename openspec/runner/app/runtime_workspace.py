from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile


@contextmanager
def request_workspace(prefix: str = "tyc-run-"):
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
