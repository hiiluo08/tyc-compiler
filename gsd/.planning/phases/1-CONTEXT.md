# Phase 1 CONTEXT — Runner backend foundation and API schemas

## Phase goal (from ROADMAP)
Create FastAPI service skeleton with config/limits, core schemas, and baseline endpoints under `gsd/runner/`, with strict isolation to `gsd/` only.

## Inputs applied
- Authority spec: `gsd/WEBAPP_SPEC.md`
- Project constraints: `gsd/.planning/PROJECT.md`
- Requirements trace: `gsd/.planning/REQUIREMENTS.md`
- User discuss decisions on 2026-05-07:
  - Use spec defaults for unresolved gray areas.
  - Phase 1 test scope = smoke tests only.

## Locked decisions for Phase 1

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

## Non-goals in Phase 1
- No ANTLR generation.
- No compiler vendor copy/adaptation.
- No Jasmin/JVM execution.
- No frontend work.

## Acceptance criteria for planning handoff
- Planner can name exact Phase 1 files under `gsd/runner/`.
- Planner can define request/response schema tasks without reopening API contract questions.
- Planner can include smoke tests only, with deep tests deferred by design.
- Planner includes explicit isolation checks in verification tasks.
