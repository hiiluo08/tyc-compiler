import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunArtifacts:
    stdout: str
    stderr: str


class RuntimeWorkspace:
    def __init__(self, runtime_assets_dir: Path):
        self.runtime_assets_dir = runtime_assets_dir
        self.temp_dir: Path | None = None

    def __enter__(self) -> "RuntimeWorkspace":
        temp_root = self.runtime_assets_dir.parent / "tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tyc-run-", dir=str(temp_root)))
        self._copy_runtime_assets()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _copy_runtime_assets(self) -> None:
        assert self.temp_dir is not None
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.runtime_assets_dir / "jasmin.jar", self.temp_dir / "jasmin.jar")
        shutil.copy2(self.runtime_assets_dir / "io.class", self.temp_dir / "io.class")

    @property
    def path(self) -> Path:
        if self.temp_dir is None:
            raise RuntimeError("Workspace not initialized")
        return self.temp_dir

    def assemble(self, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["java", "-jar", "jasmin.jar", "TyC.j"],
            cwd=self.path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )

    def execute(self, stdin: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["java", "-cp", str(self.path), "TyC"],
            cwd=self.path,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
