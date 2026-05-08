from runner.app.compiler_service import CompilerService
from runner.app.schemas import StageResult, Status


def test_semantic_failure_stage_transitions() -> None:
    service = CompilerService()
    result = service.run_pipeline(
        source='void main() { int x = "abc"; }',
        stdin="",
        timeout_seconds=2,
        include_ast=True,
    )
    assert result.status == Status.SEMANTIC_ERROR
    assert result.stages.parse == StageResult.SUCCESS
    assert result.stages.ast == StageResult.SUCCESS
    assert result.stages.semantic == StageResult.FAILED
    assert result.stages.codegen == StageResult.SKIPPED
    assert result.stages.assemble == StageResult.SKIPPED
    assert result.stages.run == StageResult.SKIPPED


def test_success_stage_transitions() -> None:
    service = CompilerService()
    result = service.run_pipeline(
        source='void main() { printString("ok"); }',
        stdin="",
        timeout_seconds=2,
        include_ast=False,
    )
    assert result.status == Status.SUCCESS
    assert result.stages.parse == StageResult.SUCCESS
    assert result.stages.ast == StageResult.SUCCESS
    assert result.stages.semantic == StageResult.SUCCESS
    assert result.stages.codegen == StageResult.SUCCESS
    assert result.stages.assemble == StageResult.SUCCESS
    assert result.stages.run == StageResult.SUCCESS
