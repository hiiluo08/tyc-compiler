import subprocess

from runner.app.compiler_service import CompilerService
from runner.app.schemas import Status


def test_pipeline_timeout_case(monkeypatch) -> None:
    service = CompilerService()

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["java"], timeout=1)

    monkeypatch.setattr("runner.app.runtime_workspace.RuntimeWorkspace.execute", _raise_timeout)

    result = service.run_pipeline(
        source='void main() { printString("x"); }',
        stdin="",
        timeout_seconds=1,
    )
    assert result.status == Status.TIMEOUT
