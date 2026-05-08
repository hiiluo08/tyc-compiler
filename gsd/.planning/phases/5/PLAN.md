# Phase 5 PLAN — Deployment docs/config for Vercel frontend and Docker runner

## Scope
Phase 5 only. Allowed write scope: `gsd/**`.

### In scope
- Add runner Dockerfile under `gsd/runner/`.
- Write deployment guide under `gsd/docs/deployment.md`.
- Add env examples for frontend/runner if needed.
- Add Phase 5 isolation baseline/check.

### Out of scope
- Frontend feature work.
- Backend API contract changes.
- Infra automation stacks (Terraform/K8s).

## Locked decisions to implement
- **D5-01**: Vercel hosts frontend only.
- **D5-02**: Runner is external Docker deployment.
- **D5-03**: Docker image must run non-root and include Java runtime.
- **D5-04**: Deployment docs must include env config and CORS guidance.
- **D5-05**: All writes remain in `gsd/`.

## Task breakdown

### Task 1 — Add runner Dockerfile (D5-02, D5-03)
**Create/Edit files**
- `gsd/runner/Dockerfile`

**Implementation**
- Use `python:3.12-slim`.
- Install OpenJDK headless.
- Copy/install `requirements-web.txt`.
- Copy runner source under `/app/runner`.
- Create non-root user and run uvicorn on port 8000.

**Acceptance**
- Dockerfile is syntactically valid and aligned with runtime dependencies.

---

### Task 2 — Write deployment documentation (D5-01, D5-04)
**Create/Edit files**
- `gsd/docs/deployment.md`

**Implementation**
- Document Vercel project settings for `gsd/frontend`.
- Document runner Docker build/run instructions.
- Document frontend and runner env keys.
- Document CORS and public safety notes.

**Acceptance**
- Docs are enough to deploy both tiers consistently.

---

### Task 3 — Add env examples and isolation artifacts (D5-04, D5-05)
**Create/Edit files**
- `gsd/frontend/.env.example`
- `gsd/runner/.env.example`
- `gsd/runner/tests/test_phase5_isolation.py`
- `gsd/.planning/phases/5/isolation-baseline.json`

**Implementation**
- Add env example files with required keys.
- Add phase-5 isolation test reusing baseline-delta approach.

**Acceptance**
- Isolation test fails on non-`gsd` mutations and root artifact leakage.

## Verification commands (Phase 5)
1. `cd gsd/frontend && npm run build`
2. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase5_isolation.py -q`
3. Optional local Docker syntax/build check if Docker available.

## Exit criteria
- Dockerfile and deployment docs are complete and consistent with spec.
- Env example files are present and aligned with runtime contract.
- Isolation checks pass.
- No create/edit/delete outside `gsd/`.
