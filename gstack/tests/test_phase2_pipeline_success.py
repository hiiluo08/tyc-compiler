from runner.app.compiler_service import CompilerService
from runner.app.schemas import Status


def test_pipeline_success_hello() -> None:
    service = CompilerService()
    result = service.run_pipeline(
        source='void main() { printString("Hello TyC"); }',
        stdin="",
        timeout_seconds=3,
    )
    assert result.status == Status.SUCCESS
    assert "Hello TyC" in result.stdout


def test_pipeline_success_with_stdin() -> None:
    service = CompilerService()
    result = service.run_pipeline(
        source='void main() { int x = readInt(); printInt(x + 1); }',
        stdin="41\n",
        timeout_seconds=3,
    )
    assert result.status == Status.SUCCESS
    assert "42" in result.stdout
