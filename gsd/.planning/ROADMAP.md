# ROADMAP — TyC Web Compiler (GSD Variant)

All phases are scoped to `gsd/` only and trace to `gsd/WEBAPP_SPEC.md`.

## Phase 1 — Runner backend foundation and API schemas
**Goal**
Create FastAPI service skeleton with config/limits, core schemas, and baseline endpoints.

**Deliverables**
- `gsd/runner/app/main.py`
- `gsd/runner/app/schemas.py`
- `gsd/runner/app/limits.py`
- `gsd/runner/requirements-web.txt`
- health endpoint + request validation

**Trace**
FR-03, FR-04, FR-05, FR-06, NFR-02

**Exit Criteria**
- `/health` and API stubs respond with contract-compliant top-level fields.
- Input size + timeout validation implemented.

## Phase 2 — Isolated compiler integration and runtime workspace
**Goal**
Integrate TyC compiler pipeline in isolated runner path without root writes.

**Deliverables**
- `gsd/runner/compiler_vendor/` (copied/adapted compiler pieces)
- `gsd/runner/build/` (ANTLR generated artifacts for variant)
- `gsd/runner/runtime_assets/` (jasmin/io assets)
- `gsd/runner/app/runtime_workspace.py`
- `gsd/runner/app/compiler_service.py`

**Trace**
FR-03, NFR-01, NFR-03

**Exit Criteria**
- End-to-end compile/assemble/run works for success sample.
- Generated files stay inside per-request temp dir under gsd-controlled area.

## Phase 3 — AST serialization and diagnostics contract
**Goal**
Implement AST JSON/text serialization and stable diagnostic/status mapping.

**Deliverables**
- `gsd/runner/app/ast_serializer.py`
- Diagnostic normalization in runner service
- Stage status transitions for partial-failure paths

**Trace**
FR-06, FR-07, FR-08

**Exit Criteria**
- semantic_error preserves AST for parseable source.
- syntax_error and timeout/runtime paths return contract shape.

## Phase 4 — React + Vite frontend experience
**Goal**
Build frontend web app with editor, toolbar, result tabs, samples, and API integration.

**Deliverables**
- `gsd/frontend/` Vite + React + TS app
- components: editor/toolbar/stdin/output/errors/ast
- `api.ts`, `types.ts`, `samples.ts`

**Trace**
FR-01, FR-02, FR-09, FR-10, FR-11

**Exit Criteria**
- Run flow works against runner API.
- UI states and sample behaviors match spec.

## Phase 5 — Deployment docs/config for Vercel frontend and Docker runner
**Goal**
Provide deployable configuration/docs for public hosting shape.

**Deliverables**
- `gsd/runner/Dockerfile`
- `gsd/docs/deployment.md`
- frontend env documentation for Vercel
- runner env/CORS/concurrency guidance

**Trace**
NFR-04, NFR-05

**Exit Criteria**
- Frontend build settings for Vercel documented.
- Runner Docker image builds with required runtime dependencies.

## Phase 6 — Tests, verification, hardening, retrospective
**Goal**
Complete required tests and final verification, then document workflow learnings.

**Deliverables**
- `gsd/tests/` and/or `gsd/runner/tests/`
- `gsd/docs/verification.md`
- `gsd/docs/retrospective.md`
- phase-level verify artifacts under `gsd/.planning/`

**Trace**
VR-01, VR-02, VR-03, VR-04

**Exit Criteria**
- Required backend/API/frontend verification passes.
- Explicit confirmation that no files outside `gsd/` were modified by this variant.

## Execution Order
1 → 2 → 3 → 4 → 5 → 6

For each phase, run strict loop:
- Discuss (`/gsd-discuss-phase N`)
- Plan (`/gsd-plan-phase N`)
- Execute (`/gsd-execute-phase N`)
- Verify (`/gsd-verify-work N`)
- Ship (`/gsd-ship N`)
