# Phase 1: Runner backend foundation and API schemas - Research

**Researched:** 2026-05-07  
**Domain:** FastAPI backend foundation + API contract scaffolding for isolated TyC runner  
**Confidence:** HIGH (for scope/contract), MEDIUM (for package pinning details)

## User Constraints (from CONTEXT.md)

### Locked Decisions

### 1) File layout inside `gsd/`
Phase 1 implementation is limited to foundational backend files:
- `gsd/runner/requirements-web.txt`
- `gsd/runner/app/__init__.py`
- `gsd/runner/app/main.py`
- `gsd/runner/app/schemas.py`
- `gsd/runner/app/limits.py`
- `gsd/runner/tests/` (smoke tests only)

No writes outside `gsd/` are allowed.

### 2) API shape to establish now
Endpoints to expose now:
- `GET /health`
- `POST /api/v1/run`
- `POST /api/v1/ast`

Phase 1 behavior:
- Enforce request validation and limit checks per spec (`source`, `stdin`, `timeoutSeconds`, `includeAst`).
- Return contract-oriented top-level response fields for run/ast endpoints.
- Pipeline internals (ANTLR/semantic/codegen/runtime execution) are deferred to Phases 2-3.

`GET /health` response contract (exact fields):
```json
{
  "ok": true,
  "service": "tyc-runner-gsd",
  "version": "0.1.0"
}
```

### 3) Error handling and diagnostics direction
- Keep status/diagnostic vocabulary aligned with spec §9.
- Do not expose internal filesystem paths in user-facing messages.
- Validation failures must be deterministic and bounded by configured limits.
- Full stage-level failure mapping is completed in Phase 3, but Phase 1 schema must already reserve compatible fields.

### 4) Data structures to lock in Phase 1
Define schema models compatible with final contract:
- Request models: run request, ast request
- Response envelope for run/ast with fields needed by final contract
- Diagnostic model shape:
  - `stage`, `severity`, `message`, `line`, `column`, `raw`
- Stage-status object keys:
  - `parse`, `ast`, `semantic`, `codegen`, `assemble`, `run`

### 5) Phase 1 test scope (user-selected)
Smoke tests only in this phase:
1. `GET /health` returns expected JSON.
2. `POST /api/v1/run` request validation for missing/invalid fields and bounds.
3. `POST /api/v1/ast` request validation for required source.
4. Run/AST success-path stubs return expected top-level shape (not full compiler execution).

Deep pipeline tests are intentionally deferred to Phases 2, 3, and final verification phase.

### 6) Isolation enforcement for all downstream tasks
- Allowed: read root compiler files for reference.
- Forbidden: create/edit/delete/move/generate files outside `gsd/`.
- Forbidden: root `.planning/` artifacts.
- If any plan step requires outside-`gsd` modification, stop and ask user.

### Claude's Discretion
- Use spec defaults for unresolved gray areas.
- Phase 1 test scope = smoke tests only.

### Deferred Ideas (OUT OF SCOPE)
- No ANTLR generation.
- No compiler vendor copy/adaptation.
- No Jasmin/JVM execution.
- No frontend work.

## Project Constraints (from CLAUDE.md)
- Prefer `python run.py ...` helper commands for root compiler workflows, though Phase 1 work remains under `gsd/`. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/CLAUDE.md]
- Root compiler pipeline order is `lexer/parser -> ASTGeneration -> StaticChecker -> CodeGenerator -> Jasmin/JVM`; Phase 1 schemas should pre-allocate this stage model even before implementation. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/CLAUDE.md]
- Root codegen currently writes artifacts into root `src/runtime/`; Phase 1 must avoid coupling to that path and reserve isolated workspace strategy for later phases. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/CLAUDE.md][VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/tests/utils.py]

## Summary
Phase 1 should lock API contracts and validation boundaries now, while intentionally returning stubbed execution results for `/api/v1/run` and `/api/v1/ast`. This keeps frontend and later backend phases unblocked without prematurely binding to compiler internals. [VERIFIED: gsd/.planning/phases/1-CONTEXT.md][VERIFIED: gsd/WEBAPP_SPEC.md]

The most important design choice is to make request/response schemas final-contract-compatible on day one (status enum, diagnostics shape, stage keys, truncation flags, ast fields), so Phases 2-3 only swap internal implementation behind stable models. [VERIFIED: gsd/WEBAPP_SPEC.md]

**Primary recommendation:** Implement strict Pydantic request models + canonical response envelopes in `schemas.py`, wire only validation + shape stubs in `main.py`, and enforce limits via centralized constants/settings in `limits.py`. [CITED: https://fastapi.tiangolo.com/tutorial/body/][CITED: https://docs.pydantic.dev/latest/concepts/models/]

## Recommended FastAPI package/module structure (`gsd/runner/app`)

```text
gsd/runner/app/
  __init__.py
  main.py               # FastAPI app factory, routes, exception handlers, CORS wiring
  schemas.py            # Pydantic request/response and enums for contract
  limits.py             # byte/time/output/concurrency constants + env-backed settings
```

Implementation guidance:
- `main.py` should own route registration and HTTP status mapping only; no compiler pipeline logic in Phase 1. [VERIFIED: gsd/.planning/phases/1-CONTEXT.md]
- `schemas.py` should be treated as contract source-of-truth for frontend + future service layer. [VERIFIED: gsd/WEBAPP_SPEC.md]
- `limits.py` should expose defaults matching spec (`source=65536`, `stdin=16384`, `timeout default=3 max=5`, output cap=32768) and allow env override. [VERIFIED: gsd/WEBAPP_SPEC.md]

Suggested dependencies for `requirements-web.txt`:
- `fastapi` (API framework) [CITED: https://fastapi.tiangolo.com/]
- `uvicorn` (ASGI server) [CITED: https://www.uvicorn.org/]
- `pydantic` (schema/validation, transitively used by FastAPI) [CITED: https://docs.pydantic.dev/latest/]
- `pytest`, `httpx` (API smoke tests via TestClient/http client style) [CITED: https://fastapi.tiangolo.com/tutorial/testing/]

## Request/response schema design (final-contract compatible)

### Request models
- `RunRequest`
  - `source: str` (required)
  - `stdin: str = ""`
  - `timeoutSeconds: int = 3`
  - `includeAst: bool = True`
- `AstRequest`
  - `source: str` (required)

Validation details:
- Validate byte length with UTF-8 encoding (`len(value.encode("utf-8"))`) because spec limits are in bytes, not characters. [VERIFIED: gsd/WEBAPP_SPEC.md]
- Constrain `timeoutSeconds` to `[1, 5]` with default `3`. [VERIFIED: gsd/WEBAPP_SPEC.md]

### Response models
Define reusable envelope pieces now:
- `Diagnostic` with exact keys: `stage`, `severity`, `message`, `line`, `column`, `raw`. [VERIFIED: gsd/WEBAPP_SPEC.md]
- `StageStatus` object with exact keys: `parse`, `ast`, `semantic`, `codegen`, `assemble`, `run`. [VERIFIED: gsd/WEBAPP_SPEC.md][VERIFIED: gsd/.planning/phases/1-CONTEXT.md]
- `TruncatedFlags` with `stdout`, `stderr` booleans. [VERIFIED: gsd/WEBAPP_SPEC.md]

For `/api/v1/run`, include all top-level fields now (`ok`, `status`, `stdout`, `stderr`, `diagnostics`, `astText`, `astJson`, `stages`, `durationMs`, `truncated`) even if stage internals are stubbed in Phase 1. [VERIFIED: gsd/WEBAPP_SPEC.md]

For `/api/v1/ast`, include final keys (`ok`, `status`, `diagnostics`, `astText`, `astJson`, `durationMs`). [VERIFIED: gsd/WEBAPP_SPEC.md]

## Validation strategy for `source` / `stdin` / `timeoutSeconds` / `includeAst`

1. **Schema-level type validation**
   - Reject non-string `source/stdin`, non-int `timeoutSeconds`, non-bool `includeAst`. [CITED: https://docs.pydantic.dev/latest/concepts/models/]

2. **Semantic bounds validation**
   - `source` byte size: `1..65536`.
   - `stdin` byte size: `0..16384`.
   - `timeoutSeconds`: `1..5`.
   - `includeAst`: default `true`. [VERIFIED: gsd/WEBAPP_SPEC.md]

3. **Deterministic error projection**
   - Convert validation failures into stable contract-style failure body (prefer `status=input_too_large` for size violations; use consistent message text). [VERIFIED: gsd/WEBAPP_SPEC.md]

4. **Isolation-safe messages**
   - Do not leak filesystem paths or subprocess details in validation responses. [VERIFIED: gsd/WEBAPP_SPEC.md]

## Error/diagnostic shaping strategy for foundation phase

Phase 1 should establish the **taxonomy**, not full compiler mapping:
- Reserve status enum including `success`, `lexical_error`, `syntax_error`, `ast_error`, `semantic_error`, `codegen_error`, `assembly_error`, `runtime_error`, `timeout`, `input_too_large`, `internal_error`. [VERIFIED: gsd/WEBAPP_SPEC.md]
- Return `diagnostics: []` for happy-path stubs; on validation failures include at least one diagnostic with `stage="internal"` or a deterministic validation stage convention documented in code comments. [ASSUMED]
- For parse-related compatibility, keep parser-like message style capable of carrying `Error on line X col Y: token`, matching root listener behavior in later phases. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/src/utils/error_listener.py]
- Keep lexical error message compatibility with root error classes (`Error Token ...`, `Unclosed String: ...`, `Illegal Escape In String: ...`) for future normalization mapping. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/src/grammar/lexererr.py]

## Smoke test strategy for Phase 1

Place smoke tests under `gsd/runner/tests/` only. [VERIFIED: gsd/.planning/phases/1-CONTEXT.md]

Recommended smoke set:
1. `GET /health` exact JSON equality.
2. `POST /api/v1/run` missing `source` -> validation error shape.
3. `POST /api/v1/run` `timeoutSeconds=0` and `6` -> rejected.
4. `POST /api/v1/run` oversized `source/stdin` -> deterministic rejection/status.
5. `POST /api/v1/ast` missing `source` -> rejected.
6. `/api/v1/run` valid stub request -> returns top-level contract keys.
7. `/api/v1/ast` valid stub request -> returns top-level contract keys.

Tooling:
- FastAPI TestClient/pytest smoke tests are standard for route/validation checks. [CITED: https://fastapi.tiangolo.com/tutorial/testing/]

## Risks + mitigation (isolation and future-phase compatibility)

1. **Risk: Contract drift between stubbed Phase 1 and real Phase 2-3 outputs**
   - Mitigation: Contract-first Pydantic response models with tests asserting key presence/types. [VERIFIED: gsd/WEBAPP_SPEC.md]

2. **Risk: Character-count validation instead of byte-count validation**
   - Mitigation: enforce UTF-8 byte checks in validators and add multibyte test case. [VERIFIED: gsd/WEBAPP_SPEC.md]

3. **Risk: Accidentally coupling to root compiler runtime paths (`src/runtime`, root `build/`)**
   - Mitigation: no imports from root codegen in Phase 1; keep execution service absent/stubbed until isolated vendor phase. [VERIFIED: gsd/.planning/ROADMAP.md][VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/tests/utils.py]

4. **Risk: Error payload inconsistency later (stage names/status typo)**
   - Mitigation: centralize enums in `schemas.py` and reference everywhere. [ASSUMED]

5. **Risk: Isolation violation by test artifacts**
   - Mitigation: run tests from `gsd/runner` scope and ensure generated caches/reports remain under `gsd/`. [VERIFIED: gsd/WEBAPP_SPEC.md]

## Root compiler behavior notes relevant to Phase 1 API compatibility

- Parser error listener currently throws `Error on line {line} col {column}: {token}`; preserve this message field shape compatibility. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/src/utils/error_listener.py]
- Semantic checker errors are stringified typed exceptions (e.g., `TypeMismatchInStatement(...)`), so diagnostic `raw` should preserve full original string. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/src/semantics/static_error.py]
- Root test harness codegen path writes into `src/runtime`; future runner integration must never reuse this location in web variant. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/tests/utils.py][VERIFIED: gsd/WEBAPP_SPEC.md]

## Open Questions

1. Should Phase 1 validation failures return FastAPI default 422 payload or custom contract-shaped body with `ok=false/status=...`?
   - Recommendation: choose one now and lock with tests; prefer custom contract wrapper for frontend stability. [ASSUMED]
2. Should `POST /api/v1/ast` also include `stages` and `truncated` for cross-endpoint uniformity?
   - Recommendation: follow spec strictly for now (no extra keys), unless frontend asks for shared envelope. [VERIFIED: gsd/WEBAPP_SPEC.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Using `stage="internal"` for validation diagnostics is acceptable in Phase 1 | Error/diagnostic shaping | Could force refactor of validation error mapping later |
| A2 | Centralized enums in `schemas.py` will be used consistently across future phases | Risks + mitigation | Divergence if later code bypasses model types |
| A3 | Custom contract wrapper for validation is preferable to raw 422 | Open Questions | Frontend may need adjustment if decision changes |

## Sources

### Primary
- `D:/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md`
- `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/PROJECT.md`
- `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/REQUIREMENTS.md`
- `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/ROADMAP.md`
- `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/1-CONTEXT.md`
- `D:/HK252/PPL/BTL/tyc-compiler/CLAUDE.md`
- `D:/HK252/PPL/BTL/tyc-compiler/src/utils/error_listener.py`
- `D:/HK252/PPL/BTL/tyc-compiler/src/semantics/static_error.py`
- `D:/HK252/PPL/BTL/tyc-compiler/src/grammar/lexererr.py`
- `D:/HK252/PPL/BTL/tyc-compiler/tests/utils.py`

### Secondary
- FastAPI request body and validation: https://fastapi.tiangolo.com/tutorial/body/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- Pydantic models: https://docs.pydantic.dev/latest/concepts/models/
- Uvicorn docs: https://www.uvicorn.org/
