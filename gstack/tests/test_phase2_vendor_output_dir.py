from pathlib import Path

from runner.app.compiler_service import CompilerService
from runner.compiler_vendor.codegen.codegen import CodeGenerator


def test_vendor_codegen_writes_only_to_provided_output_dir(tmp_path: Path) -> None:
    service = CompilerService()
    ast = service._parse_to_ast('void main() { printString("Hello"); }')

    out_dir = tmp_path / "workspace"
    out_dir.mkdir(parents=True, exist_ok=True)

    CodeGenerator(output_dir=str(out_dir)).visit(ast)

    assert (out_dir / "TyC.j").exists()
    root_runtime_file = Path("src/runtime/TyC.j")
    if root_runtime_file.exists():
        content = root_runtime_file.read_text(encoding="utf-8", errors="ignore")
        assert 'Hello' not in content
