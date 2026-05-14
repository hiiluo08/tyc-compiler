# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Prefer the Python build script over the Makefile because it is cross-platform and includes the code generation test target.

```bash
python run.py check        # verify Python/Java prerequisites
python run.py setup        # create venv, download ANTLR, install requirements
python run.py build        # generate ANTLR lexer/parser/visitor into build/
python run.py clean        # remove build/ and Python caches
```

Assignment test wrappers generate HTML reports under `reports/`:

```bash
python run.py test-lexer
python run.py test-parser
python run.py test-ast
python run.py test-checker
python run.py test-codegen
```

The `run.py test-*` commands invoke pytest with `check=False`, so use direct pytest commands when a failing exit code matters. Build the grammar first because test utilities import generated modules from `build/`.

```bash
python run.py build
PYTHONPATH=. venv/Scripts/python.exe -m pytest tests/test_ast_gen.py::test_001 -q
PYTHONPATH=. venv/Scripts/python.exe -m pytest tests/test_checker.py -q
PYTHONPATH=. venv/Scripts/python.exe -m pytest tests/test_codegen.py::test_001 -q
```

If the virtual environment is already activated, `python -m pytest ...` is equivalent. There is no configured lint or formatter command in this repository.

## Architecture

This is a Python/ANTLR4 compiler for the TyC teaching language. The main flow is:

```text
TyC source -> ANTLR lexer/parser -> ASTGeneration -> StaticChecker -> CodeGenerator -> Jasmin .j -> JVM .class
```

- `src/grammar/TyC.g4` is the grammar source. `python run.py build` runs ANTLR with `-visitor -no-listener`, writes generated Python files to `build/`, creates `build/__init__.py`, and copies `src/grammar/lexererr.py` so generated lexer imports resolve. Do not edit generated files in `build/`; update the grammar or lexer error source instead.
- Lexing errors are raised from embedded lexer actions in `TyC.g4` using `ErrorToken`, `UncloseString`, and `IllegalEscape`. Parser tests use `src/utils/error_listener.py` to convert syntax errors into stable strings.
- `src/astgen/ast_generation.py` subclasses generated `build.TyCVisitor` and maps parse tree contexts to AST node classes in `src/utils/nodes.py`. ANTLR Python renames grammar rule `type` to `type_()`, so visitor methods call `ctx.type_()`.
- `src/utils/nodes.py` defines the AST shape; `src/utils/visitor.py` defines `ASTVisitor` and `BaseVisitor`. Later phases consume these nodes rather than parse tree contexts.
- In the AST, inferred `auto` variable types and omitted function return types are represented as `None`. `src/semantics/static_checker.py` converts those to its internal `AutoType` while checking.
- `src/semantics/static_checker.py` uses `CheckerContext` for `global_funcs`, `global_structs`, nested `local_env` scopes, loop/control tracking, and current function return inference. Semantic error classes and output strings are defined in `src/semantics/static_error.py`.
- Built-in I/O functions are duplicated in the checker and codegen layers: `readInt`, `readFloat`, `readString`, `printInt`, `printFloat`, and `printString`. Keep `CheckerContext.initialize_builtins()` and `src/codegen/io.py` consistent when changing built-ins.
- `src/codegen/codegen.py` subclasses `BaseVisitor`, registers structs/functions, emits a fixed `TyC` class for the program, and delegates Jasmin text generation to `src/codegen/emitter.py`. `src/codegen/frame.py` tracks local indexes, operand stack size, labels, and loop labels; `src/codegen/jasmin_code.py` contains low-level JVM instruction strings.
- Code generation writes `.j` and `.class` artifacts into `src/runtime/`. `src/runtime/io.java` and `src/runtime/jasmin.jar` provide runtime support; generated `*.j` and `*.class` files are ignored by git.

## Tests and harness details

- `tests/utils.py` is the shared harness. It adds the repository root and `build/` to `sys.path`, then exposes `Tokenizer`, `Parser`, `ASTGenerator`, `Checker`, and codegen `CodeGenerator` wrappers.
- Lexer/parser tests compare token or parser-result strings. Many lexer/parser examples are currently commented out, so check active test functions before assuming coverage.
- AST tests compare `str(ASTGenerator(source).generate())` against expected AST node strings.
- Checker tests call `Checker(source).check_from_source()` and usually compare either `"Static checking passed"` or semantic error strings/substrings.
- Codegen tests call `ASTGenerator` directly and then `CodeGenerator().generate_and_run(...)`; they do not run the static checker first, so codegen assumes semantically valid input. The harness assembles generated Jasmin with `src/runtime/jasmin.jar`, runs `java -cp src/runtime TyC`, and strips stdout.

Do not skip skills, ignore gstack errors, or work around missing gstack.

Using gstack skills: After install, skills like /qa, /ship, /review, /investigate,
and /browse are available. Use /browse for all web browsing.
Use ~/.claude/skills/gstack/... for gstack file paths (the global path).
