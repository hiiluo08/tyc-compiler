# Phase 3 CONTEXT — AST serialization and diagnostics contract

## Phase goal (from ROADMAP)
Implement AST text/JSON serialization and stable diagnostic/status contract for runner responses, preserving Phase 2 isolated execution model.

## Inputs applied
- Authority spec: `gsd/WEBAPP_SPEC.md`
- Prior phase outputs: `gsd/.planning/phases/2/*`
- Current implementation: `gsd/runner/app/main.py`, `gsd/runner/app/compiler_service.py`, `gsd/runner/app/schemas.py`
- User preference in this loop: continue with default spec unless ambiguity is critical.

## Locked decisions for Phase 3

### 1) Scope and files
Phase 3 changes are limited to `gsd/` only, primarily:
- `gsd/runner/app/ast_serializer.py`
- `gsd/runner/app/compiler_service.py`
- `gsd/runner/app/main.py`
- `gsd/runner/app/schemas.py` (only if contract types need tightening)
- `gsd/runner/tests/test_phase3_*`
- `gsd/.planning/phases/3/*`

### 2) AST serialization contract
- `astText = str(ast)`.
- `astJson` must follow recursive serializer shape:
  - primitive -> primitive
  - list -> serialized list
  - AST node -> `{ "kind": ClassName, "fields": { ... } }`
  - `None` -> `null`
  - unknown objects -> `str(value)`
- `/api/v1/run`: include `astText`/`astJson` when `includeAst=true` and source is parseable.
- `/api/v1/ast`: always return both `astText` and `astJson` on success.

### 3) Diagnostics/status mapping
For `/api/v1/run` and `/api/v1/ast`, map errors to spec statuses:
- lexical exception -> `lexical_error` (stage `lex`)
- parser listener syntax error -> `syntax_error` (stage `parse`)
- AST generation failure -> `ast_error` (stage `ast`)
- semantic checker failure -> `semantic_error` (stage `semantic`)
- codegen failure -> `codegen_error` (stage `codegen`)
- jasmin failure -> `assembly_error` (stage `assemble`)
- JVM non-zero -> `runtime_error` (stage `run`)
- subprocess timeout -> `timeout` (stage `run` or current stage)
- unexpected -> `internal_error` (stage `internal`)

Diagnostic object must follow spec exactly:
- `stage`, `severity`, `message`, `line`, `column`, `raw`
- `line/column` extracted when parser error format provides them; otherwise `null`.

### 4) Stage transition contract
- Stage keys remain fixed: `parse, ast, semantic, codegen, assemble, run`.
- Success path: all `success`.
- Failure path: current stage `failed`, later stages `skipped`.
- Earlier completed stages remain `success`.

### 5) includeAst behavior
- `includeAst=false`: run response may omit AST payload (`astText=null`, `astJson=null`) even if parse succeeds.
- `includeAst=true`: preserve AST on semantic failure and later failures when parse/AST stages succeeded.

### 6) Test scope for Phase 3
Must add backend tests for:
1. `/api/v1/ast` returns contract-compliant `astText` + non-empty structured `astJson`.
2. `/api/v1/run` semantic error returns `semantic_error` and preserves AST when `includeAst=true`.
3. `/api/v1/run` syntax error returns `syntax_error` with diagnostic stage `parse`.
4. `/api/v1/run` runtime error maps to `runtime_error` with stderr.
5. `/api/v1/run` timeout maps to `timeout`.
6. Stage-status transitions are consistent with failure stage.
7. Isolation guard remains green (no new non-`gsd/` mutations from phase execution).

### 7) Non-goals in Phase 3
- Frontend changes.
- Deployment docs/config.
- Rate-limit/CORS hardening expansions (Phase 5/6 scope).

### 8) Isolation enforcement
- No create/edit/delete outside `gsd/`.
- No generated artifacts under root `build/` or root `src/runtime/`.
- If any step appears to require root change, stop and ask user.

## Acceptance criteria for planning handoff
- Planner can enumerate exact files under `gsd/`.
- Plan includes explicit serializer implementation task.
- Plan includes status/diagnostic normalization task with stage transitions.
- Plan includes tests that prove semantic-error AST retention and syntax/timeout/runtime mappings.
