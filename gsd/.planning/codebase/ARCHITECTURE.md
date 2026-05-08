<!-- refreshed: 2026-05-07 -->
# Architecture

**Analysis Date:** 2026-05-07

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                 Frontend / Orchestration Layer              │
├──────────────────┬──────────────────┬───────────────────────┤
│  Build/Test CLI  │   Test Harness   │     ANTLR Grammar     │
│   `run.py`       │ `tests/utils.py` │ `src/grammar/TyC.g4`  │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Compiler Pipeline Layer                      │
│  `src/astgen/ast_generation.py`                              │
│  `src/semantics/static_checker.py`                           │
│  `src/codegen/codegen.py` + `src/codegen/emitter.py`         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│               Runtime Artifacts / External Tools             │
│  `src/runtime/*.j`, `src/runtime/*.class`, `src/runtime/io.java` 
│  and `src/runtime/jasmin.jar`                                │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Grammar | Defines lexer/parser rules and lexer error actions | `src/grammar/TyC.g4` |
| AST generator | Converts ANTLR parse tree contexts into AST node objects | `src/astgen/ast_generation.py` |
| AST model | Defines canonical compiler IR used by later phases | `src/utils/nodes.py` |
| Visitor contracts | Declares traversal API used by checker and codegen | `src/utils/visitor.py` |
| Static checker | Enforces semantic constraints and type inference | `src/semantics/static_checker.py` |
| Semantic errors | Stable semantic exception surface | `src/semantics/static_error.py` |
| Code generator | Traverses AST and emits Jasmin for TyC + structs | `src/codegen/codegen.py` |
| Emitter | Low-level JVM/Jasmin emission and file write | `src/codegen/emitter.py` |
| Runtime bridge | Built-in I/O function mappings and Java runtime support | `src/codegen/io.py`, `src/runtime/io.java` |
| Build/test orchestration | Setup/build/test entrypoint and wrappers | `run.py`, `tests/utils.py` |

## Pattern Overview

**Overall:** Staged compiler pipeline with visitor-based phase isolation.

**Key Characteristics:**
- Single AST contract between phases (`src/utils/nodes.py`).
- Visitors separate traversal from phase-specific logic (`src/utils/visitor.py`).
- Global-first registration then declaration emission in codegen (`src/codegen/codegen.py`).

## Layers

**Grammar + Parse Layer:**
- Purpose: Tokenize and parse TyC source, normalize syntax errors.
- Location: `src/grammar/TyC.g4`, `src/utils/error_listener.py`, generated `build/` modules consumed via `tests/utils.py`.
- Contains: Grammar rules, lexer actions, parser error listener.
- Depends on: ANTLR runtime and generated parser/lexer modules.
- Used by: AST generation wrapper in `tests/utils.py` and downstream compiler phases.

**AST Construction Layer:**
- Purpose: Convert parse tree contexts into typed AST nodes.
- Location: `src/astgen/ast_generation.py`.
- Contains: `ASTGeneration(TyCVisitor)` methods for program/decl/stmt/expr trees.
- Depends on: `build.TyCParser`, `build.TyCVisitor`, `src/utils/nodes.py`.
- Used by: Static checker and code generator.

**Semantic Analysis Layer:**
- Purpose: Resolve symbols, infer `auto`, validate all semantic constraints.
- Location: `src/semantics/static_checker.py`.
- Contains: `CheckerContext`, `StaticChecker`, helper inference methods.
- Depends on: AST nodes and visitor interface.
- Used by: Checker wrapper (`tests/utils.py`) and any future API compiler service.

**Code Generation Layer:**
- Purpose: Emit JVM-targeted Jasmin from AST.
- Location: `src/codegen/codegen.py`, `src/codegen/emitter.py`, `src/codegen/frame.py`, `src/codegen/utils.py`.
- Contains: symbol registration, control-flow lowering, stack/local tracking, Jasmin output.
- Depends on: AST nodes, visitor base, runtime I/O symbols.
- Used by: Codegen wrapper in `tests/utils.py` and runtime execution pipeline.

**Runtime Execution Layer:**
- Purpose: Assemble/run generated classes and provide I/O functions.
- Location: `src/runtime/io.java`, `src/runtime/jasmin.jar`, runtime invocation in `tests/utils.py`.
- Contains: Java static I/O methods, jasmin assembler jar, generated `.j/.class` files.
- Depends on: Java/JVM toolchain.
- Used by: code generation tests and any web runner execution sandbox.

## Data Flow

### Primary Request Path

1. Parse source using generated lexer/parser and custom error listener (`tests/utils.py:60`, `tests/utils.py:65`).
2. Build AST by visiting parse tree (`tests/utils.py:91`, `src/astgen/ast_generation.py:16`).
3. Run semantic checks and type inference (`tests/utils.py:123`, `src/semantics/static_checker.py:165`).
4. Emit Jasmin classes from AST (`src/codegen/codegen.py:143`, `src/codegen/emitter.py:671`).
5. Write `.j` files then assemble/run JVM program (`src/codegen/emitter.py:687`, `tests/utils.py:209`, `tests/utils.py:226`).

### Build/Regeneration Flow

1. Build script resolves grammar files and ANTLR jar (`run.py:335`, `run.py:341`).
2. ANTLR generates parser/visitor Python modules into `build/` (`run.py:352`, `run.py:363`).
3. Test harness imports generated modules from `build/` (`tests/utils.py:14`, `tests/utils.py:15`).

**State Management:**
- Semantic state lives in mutable `CheckerContext` (`src/semantics/static_checker.py:88`).
- Codegen state lives in `CodeGenerator` fields and per-function `Frame` (`src/codegen/codegen.py:24`, `src/codegen/frame.py:28`).
- Test runner state uses per-request filesystem cleanup in `tests/utils.py:138`.

## Key Abstractions

**AST Node Graph:**
- Purpose: Phase-neutral representation of TyC programs.
- Examples: `Program`, `FuncDecl`, `BinaryOp`, `StructLiteral` in `src/utils/nodes.py`.
- Pattern: Algebraic class hierarchy + visitor `accept` dispatch.

**Visitor Interface Contract:**
- Purpose: Keep each phase implementation decoupled from AST data classes.
- Examples: `ASTVisitor` and `BaseVisitor` in `src/utils/visitor.py`.
- Pattern: Double-dispatch with overridable per-node methods.

**Semantic Context:**
- Purpose: Carry symbol tables, scopes, control stack, and return-type inference state.
- Examples: `CheckerContext` fields in `src/semantics/static_checker.py:89`-`src/semantics/static_checker.py:97`.
- Pattern: Explicit context object threaded through visitor calls.

**Emission Context:**
- Purpose: Carry stack depth, labels, local indices, loop labels while lowering AST.
- Examples: `Frame` and `Access/SubBody` in `src/codegen/frame.py`, `src/codegen/utils.py`.
- Pattern: Mutable frame model plus symbolic environment list.

## Entry Points

**Build/Test CLI:**
- Location: `run.py`
- Triggers: `python run.py <command>`.
- Responsibilities: setup, ANTLR generation, runtime compile, pytest wrappers.

**Compiler Test Harness API:**
- Location: `tests/utils.py`
- Triggers: test suites import wrappers.
- Responsibilities: source→AST, AST→semantic result, AST→runtime output.

**Codegen Program Emit Entry:**
- Location: `src/codegen/codegen.py` (`visit_program`)
- Triggers: `CodeGenerator().visit(ast)`.
- Responsibilities: register symbols, emit class files, close outputs.

## Architectural Constraints

- **Threading:** Single-threaded Python execution with subprocess calls for Java/Jasmin (`tests/utils.py:177`, `tests/utils.py:208`).
- **Global state:** Singleton error listener `NewErrorListener.INSTANCE` in `src/utils/error_listener.py:11`; mutable `CodeGenerator` instance state in `src/codegen/codegen.py:24`-`src/codegen/codegen.py:31`.
- **Circular imports:** Not detected across `src/*` modules in current layout.
- **Generated-code boundary:** `build/` is generated from `src/grammar/TyC.g4` and should be treated as derived artifacts.

## Anti-Patterns

### Pipeline Bypass in Runtime Path

**What happens:** Codegen tests run `AST -> codegen -> run` without enforcing semantic pass first (`tests/test_codegen.py:20`-`tests/test_codegen.py:21`).
**Why it's wrong:** Invalid AST/type states can reach codegen, creating hidden assumptions and fragile failures.
**Do this instead:** For service/runtime entrypoints, enforce staged contract `parse -> AST -> semantic -> codegen` using `Checker.check_from_source` in `tests/utils.py:116` before `CodeGenerator.generate_and_run`.

### Hard-Coded Runtime Working Directory

**What happens:** Harness changes process cwd to `src/runtime` during generation (`tests/utils.py:189`).
**Why it's wrong:** Shared cwd mutation complicates embedding into concurrent web workers.
**Do this instead:** Encapsulate workspace paths in a runner adapter under `gsd/runner/` and invoke subprocesses with explicit `cwd` per call.

## Error Handling

**Strategy:** Raise structured exceptions per stage and convert to stable strings at harness boundary.

**Patterns:**
- Lexer/parser errors raised as exceptions from grammar actions and `NewErrorListener` (`src/grammar/TyC.g4:8`, `src/utils/error_listener.py:13`).
- Semantic failures use typed exceptions with deterministic `__str__` formats (`src/semantics/static_error.py`).

## Cross-Cutting Concerns

**Logging:** Minimal; mostly return strings/exceptions, no structured logger in `src/*`.
**Validation:** Static checker enforces type/scope/control constraints before codegen (`src/semantics/static_checker.py`).
**Authentication:** Not applicable in current compiler codebase.

## Extension Points for Isolated Web Runner under `gsd/`

- **Compiler service boundary:** Reuse `ASTGeneration` + `StaticChecker` + `CodeGenerator` as pure components by adding a thin adapter in `gsd/runner/app/compiler_service.py` that maps stages to API response schema.
- **Workspace isolation:** Replace direct `src/runtime` writes by copying runtime assets into per-request temp directories under `gsd/runner/` and instantiating `Emitter` with path-configurable output root.
- **Error envelope normalization:** Wrap parser (`SyntaxException`), semantic (`StaticError`), assembly/runtime subprocess failures (`tests/utils.py:217`, `tests/utils.py:234`) into a single JSON contract in `gsd/runner/app/schemas.py`.
- **AST serialization boundary:** Keep `src/utils/nodes.py` untouched and add serializer-only logic in `gsd/runner/app/ast_serializer.py`.
- **Execution limits boundary:** Move timeout/output-size enforcement from ad hoc subprocess usage to centralized limiter module in `gsd/runner/app/limits.py`.

---

*Architecture analysis: 2026-05-07*
