# Coding Conventions

**Analysis Date:** 2026-05-07

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python modules across compiler layers, e.g. `src/semantics/static_checker.py`, `src/astgen/ast_generation.py`, `src/codegen/jasmin_code.py`.
- Use `test_*.py` for pytest modules, e.g. `tests/test_checker.py`, `tests/test_codegen.py`.

**Functions:**
- Use `snake_case` for compiler/runtime methods and helpers, e.g. `check_program`, `visit_program`, `generate_and_run` in `src/semantics/static_checker.py`, `src/codegen/codegen.py`, `tests/utils.py`.
- Keep ANTLR-generated visitor override names in `visitCamelCase` form where required by generated parser APIs, e.g. `visitProgram`, `visitStruct_decl`, `visitFor_update` in `src/astgen/ast_generation.py`.

**Variables:**
- Use `snake_case` for Python locals/fields (`current_func_return_type`, `local_env`, `runtime_dir`) in `src/semantics/static_checker.py` and `tests/utils.py`.
- Use concise single-letter temporaries only for short-scoped arithmetic or examples (`i`, `j`, `o`) in `src/codegen/codegen.py` and tests.

**Types:**
- Use `PascalCase` for AST and type classes (`Program`, `FuncDecl`, `IntType`, `StructType`) in `src/utils/nodes.py` and usages in `src/astgen/ast_generation.py`.
- Use exception/type class names in `PascalCase` with semantic meaning (`TypeMismatchInExpression`, `MustInLoop`) in `src/semantics/static_error.py`.

## Code Style

**Formatting:**
- Tool used: Not detected (no configured formatter in repo root; no `.prettierrc*`, `pyproject.toml`, or `setup.cfg` formatter sections detected).
- Key settings: Not applicable. Preserve existing 4-space indentation, docstring-first module layout, and vertical import grouping seen in `src/semantics/static_checker.py` and `run.py`.

**Linting:**
- Tool used: Not detected (no `.eslintrc*`, `eslint.config.*`, `biome.json`, `ruff.toml`, `mypy.ini`, or `pyrightconfig.json` detected).
- Key rules: Convention is enforced by existing file style and tests.

## Import Organization

**Order:**
1. Standard library imports (`os`, `sys`, `typing`, `subprocess`) in files like `run.py`, `tests/utils.py`, `src/semantics/static_checker.py`.
2. Third-party imports (`antlr4`, `pytest`) in `tests/utils.py`, `tests/test_*.py`.
3. Project-local imports (`from src...`, `from ..utils...`) in `src/*` and `tests/*`.

**Path Aliases:**
- None. Use package-relative imports inside `src/` (e.g. `from ..utils.nodes import ...` in `src/semantics/static_checker.py`) and root-qualified imports in tests (`from tests.utils import Checker` in `tests/test_checker.py`).
- Compatibility note for web compiler work: keep `build/` and repo root path insertion behavior unchanged in `tests/utils.py` (`sys.path.insert(0, project_root)` and `sys.path.insert(0, build_dir)`) because test wrappers depend on generated ANTLR modules at runtime.

## Error Handling

**Patterns:**
- Raise domain-specific semantic exceptions from `src/semantics/static_error.py` (e.g. `raise UndeclaredStruct(...)`, `raise TypeCannotBeInferred(...)`) in checker visitor logic (`src/semantics/static_checker.py`).
- In test harness wrappers, catch broad exceptions and convert to canonical strings for snapshot-style assertions, e.g. `except Exception as e: return str(e)` in `Checker.check_from_source` (`tests/utils.py`).
- In codegen harness, convert subprocess/runtime failures to stable message strings (`"Runtime compile error: ..."`, `"Assembly error for ..."`, `"Timeout"`) in `tests/utils.py`.

## Logging

**Framework:** `print`/console output only.

**Patterns:**
- Build/test orchestration logs via ANSI-colored helper methods in `run.py` (`Colors.red/green/yellow/blue`).
- Core compiler phases in `src/` do not use runtime logging; behavior is validated through return values and raised exceptions.

## Comments

**When to Comment:**
- Use section dividers and short intent comments in tests to group behavior matrices, e.g. headings in `tests/test_checker.py` and `tests/test_codegen.py`.
- Keep inline comments for compatibility-sensitive runtime behavior, e.g. cleanup and Java/Jasmin execution notes in `tests/utils.py`.

**JSDoc/TSDoc:**
- Not applicable (Python project).
- Python docstrings are used at module/class/function level (`run.py`, `tests/utils.py`, `src/codegen/codegen.py`).

## Function Design

**Size:**
- Visitor methods are small and single-responsibility where possible (`visit_*` methods in `src/astgen/ast_generation.py`), with large coordinator classes acceptable for phase logic (`StaticChecker` in `src/semantics/static_checker.py`, `TyCBuilder` in `run.py`).

**Parameters:**
- Visitor signatures conventionally include context object (`node, o`) for state threading in `src/semantics/static_checker.py` and `src/codegen/codegen.py`.
- Wrapper APIs keep plain source/AST inputs to preserve test compatibility (`Checker(source).check_from_source()`, `CodeGenerator().generate_and_run(ast, input_data="")` in `tests/utils.py`).

**Return Values:**
- Compiler/checker internals return AST/type objects or mutate context and raise on error.
- Test-facing wrappers return deterministic strings (`"success"`, `"Static checking passed"`, stripped stdout, or error text) in `tests/utils.py`; preserve this contract for web compiler integration compatibility.

## Module Design

**Exports:**
- Modules expose classes/functions directly; no explicit `__all__` export policy detected.
- `__init__.py` files are present in `src/` packages and `tests/` for importability.

**Barrel Files:**
- Not used as a pattern. Imports target concrete modules directly (`from src.semantics.static_checker import StaticChecker`, `from src.astgen.ast_generation import ASTGeneration` in `tests/utils.py`).

---

*Convention analysis: 2026-05-07*
