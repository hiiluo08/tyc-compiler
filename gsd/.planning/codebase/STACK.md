# Technology Stack

**Analysis Date:** 2026-05-07

## Languages

**Primary:**
- Python 3.12 - Compiler pipeline orchestration and implementation in `run.py`, `src/astgen/ast_generation.py`, `src/semantics/static_checker.py`, `src/codegen/codegen.py`

**Secondary:**
- ANTLR4 grammar (targeting Python3) - Language definition in `src/grammar/TyC.g4`
- Java (JVM runtime/Jasmin tooling) - Runtime support in `src/runtime/io.java`, assembly/execution via `src/runtime/jasmin.jar`

## Runtime

**Environment:**
- Python 3.12 (required by build script) in `run.py`
- Java runtime + `javac` required for ANTLR/Jasmin/runtime compile in `run.py` and `tests/utils.py`

**Package Manager:**
- pip (inside project venv) via `run.py setup`
- Lockfile: missing (`requirements.txt` only)

## Frameworks

**Core:**
- ANTLR 4.13.2 - Generates lexer/parser/visitor to `build/` from `src/grammar/TyC.g4`

**Testing:**
- pytest - Test runner invoked by `run.py test-*`
- pytest-html - HTML report generation under `reports/`
- pytest-timeout - Per-test timeout guards

**Build/Dev:**
- Custom Python build CLI (`run.py`) - setup, grammar build, runtime compile, test wrappers
- Jasmin assembler (`src/runtime/jasmin.jar`) - `.j` to `.class` in codegen test flow

## Key Dependencies

**Critical:**
- `antlr4-python3-runtime==4.13.2` - Runtime for generated lexer/parser visitors (`requirements.txt`, imported in `tests/utils.py`)

**Infrastructure:**
- `pytest` / `pytest-html` / `pytest-timeout` - Verification harness (`requirements.txt`, `run.py`)
- Java tools (`java`, `javac`) - Grammar generation, runtime compile, class execution (`run.py`, `tests/utils.py`)

## Configuration

**Environment:**
- Python path is set for tests to include repo root and `build/` in `tests/utils.py`
- Build artifacts expected in `build/` (`TyCLexer.py`, `TyCParser.py`, `TyCVisitor.py`)
- Runtime artifacts expected in `src/runtime/` (`*.j`, `TyC.class`, `io.class`)

**Build:**
- `run.py` defines canonical commands:
  - `python run.py check`
  - `python run.py setup`
  - `python run.py build`
  - `python run.py test-lexer|test-parser|test-ast|test-checker|test-codegen`
- Grammar build command in `run.py` uses: `java -jar external/antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor -no-listener -o build src/grammar/*.g4`

## Platform Requirements

**Development:**
- Python 3.12 + venv
- Java runtime and compiler (`java`, `javac`)
- Network access on first setup to download ANTLR JAR from `https://www.antlr.org/download/antlr-4.13.2-complete.jar` (`run.py`)

**Production:**
- Not detected as packaged service; current target is local CLI/test execution pipeline (`run.py`, `tests/utils.py`)

---

*Stack analysis: 2026-05-07*
