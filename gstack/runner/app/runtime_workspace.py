import os
import shutil
import signal
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

    def _kill_process_tree(self, process: subprocess.Popen[str]) -> None:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

        if process.poll() is None:
            process.kill()

    def _run_with_timeout(
        self,
        command: list[str],
        timeout_seconds: int,
        stdin: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        popen_kwargs: dict = {
            "cwd": self.path,
            "stdin": subprocess.PIPE if stdin is not None else None,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
        }

        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["preexec_fn"] = os.setsid

        process = subprocess.Popen(command, **popen_kwargs)
        try:
            stdout, stderr = process.communicate(input=stdin, timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            self._kill_process_tree(process)
            stdout, stderr = process.communicate()
            raise subprocess.TimeoutExpired(
                cmd=command,
                timeout=timeout_seconds,
                output=stdout,
                stderr=stderr,
            ) from exc

        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)

    def assemble(self, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return self._run_with_timeout(["java", "-jar", "jasmin.jar", "TyC.j"], timeout_seconds)

    def execute(self, stdin: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
        return self._run_with_timeout(["java", "-cp", str(self.path), "TyC"], timeout_seconds, stdin=stdin)
