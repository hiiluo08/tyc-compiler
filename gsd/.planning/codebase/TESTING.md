# Testing Patterns

**Analysis Date:** 2026-05-07

## Test Framework

**Runner:**
- `pytest` (version not pinned in `requirements.txt`)
- Config: Not detected (`pytest.ini`/`pyproject.toml` pytest section not present). Runtime options are passed via CLI in `run.py` and optional `__main__` blocks in test files.

**Assertion Library:**
- Built-in `pytest` assert introspection using plain `assert`.

**Run Commands:**
```bash
python run.py test-lexer      # Wrapper run + HTML report (non-failing exit on test failures)
python run.py test-checker    # Wrapper run + HTML report (non-failing exit on test failures)
PYTHONPATH=. venv/Scripts/python.exe -m pytest tests/test_codegen.py -q   # Direct failing exit code
```

## Test File Organization

**Location:**
- Separate `tests/` directory with shared harness at `tests/utils.py`.
- Test modules by phase: `tests/test_lexer.py`, `tests/test_parser.py`, `tests/test_ast_gen.py`, `tests/test_checker.py`, `tests/test_codegen.py`.

**Naming:**
- File names use `test_*.py`.
- Test functions use zero-padded numeric names (`test_001`, `test_142`) to stabilize ordering and referencing (`tests/test_codegen.py`, `tests/test_checker.py`).

**Structure:**
```
tests/
  utils.py
  test_lexer.py
  test_parser.py
  test_ast_gen.py
  test_checker.py
  test_codegen.py
```

## Test Structure

**Suite Organization:**
```python
from tests.utils import Checker

def test_001():
    source = "void main() { int x = 5; }"
    assert Checker(source).check_from_source() == "Static checking passed"
```
(Observed in `tests/test_checker.py`.)

**Patterns:**
- Setup pattern: central wrappers in `tests/utils.py` perform parse/check/codegen setup and normalize outputs.
- Teardown pattern: explicit runtime artifact cleanup in `CodeGenerator._cleanup_generated_files()` in `tests/utils.py` before each codegen run.
- Assertion pattern: exact string equality for stable contracts, with selective substring/prefix checks when message detail may vary (`"Redeclared" in ...`, `.startswith("TypeMismatchInStatement")`) in `tests/test_checker.py`.

## Mocking

**Framework:**
- Not used.

**Patterns:**
```python
# Integration-style execution without mocks
ast = ASTGenerator(src).generate()
return CodeGenerator().generate_and_run(ast, input_data=input_data)
```
(Observed in `tests/test_codegen.py`.)

**What to Mock:**
- Not applicable in current suite; tests intentionally exercise real ANTLR parser, checker, Jasmin assembly, and JVM execution.

**What NOT to Mock:**
- Do not mock generated ANTLR modules (`build.TyCLexer`, `build.TyCParser`) or runtime subprocess path in `tests/utils.py`; current compatibility relies on end-to-end behavior.

## Fixtures and Factories

**Test Data:**
```python
source = "void main() { printInt(42); }"
assert run(source) == "42"
```
(Observed across `tests/test_codegen.py`.)

**Location:**
- No fixture/factory modules detected. Inputs are inline source strings in each test function.

## Coverage

**Requirements:** None enforced (no coverage config/threshold detected).

**View Coverage:**
```bash
PYTHONPATH=. venv/Scripts/python.exe -m pytest --cov=src --cov-report=term-missing
```
(Manual command; not configured in `run.py`.)

## Test Types

**Unit Tests:**
- AST generation tests compare deterministic `str(AST)` representations in `tests/test_ast_gen.py`.
- Checker tests validate semantic diagnostics by exact message contract in `tests/test_checker.py`.

**Integration Tests:**
- Lexer/parser wrappers in `tests/utils.py` invoke generated lexer/parser + custom error listener (`src/utils/error_listener.py`).
- Codegen tests run full pipeline to JVM stdout via Jasmin + Java subprocess calls in `tests/utils.py` and assertions in `tests/test_codegen.py`.

**E2E Tests:**
- Compiler-runtime E2E style present for backend codegen (`tests/test_codegen.py`).
- Web compiler (gsd) E2E tests: Not used yet.

## Common Patterns

**Async Testing:**
```python
# No async tests; subprocess timeouts guard long-running commands
result = subprocess.run([...], timeout=10, capture_output=True, text=True)
```
(From `tests/utils.py`.)

**Error Testing:**
```python
assert Checker(source).check_from_source() == "UndeclaredFunction(run)"
assert Checker(source).check_from_source().startswith("TypeMismatchInExpression")
```
(Observed in `tests/test_checker.py`.)

## Compatibility Notes for Web Compiler Work in `gsd/`

- Preserve wrapper return contracts in `tests/utils.py` (`"success"`, `"Static checking passed"`, exact error-string forms, stripped stdout). Web compiler integration should map UI/backend diagnostics to these existing strings to avoid regression in legacy tests.
- Preserve dependency on generated grammar artifacts under `build/` and runtime artifacts under `src/runtime/` because tests inject both repo root and `build/` into `sys.path` in `tests/utils.py`.
- Preserve `run.py test-*` semantics where pytest failures do not fail the wrapper process (`check=False`), since assignment workflows rely on HTML report generation in `reports/*/index.html`.
- Keep direct pytest path available for CI/automation that requires failing exit codes, as documented by commands used with `venv/Scripts/python.exe -m pytest`.

---

*Testing analysis: 2026-05-07*
