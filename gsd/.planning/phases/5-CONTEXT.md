# Phase 5 CONTEXT — Deployment docs/config for Vercel frontend and Docker runner

## Phase goal (from ROADMAP)
Provide deployable configuration and documentation for public hosting shape:
- Vercel frontend deployment from `gsd/frontend/`
- Dockerized runner deployment from `gsd/runner/`

## Inputs applied
- Authority spec: `gsd/WEBAPP_SPEC.md`
- Roadmap scope: `gsd/.planning/ROADMAP.md` (Phase 5)
- Prior phase outputs: `gsd/.planning/phases/4/*`
- Current implementation roots: `gsd/frontend/`, `gsd/runner/`
- User preference: continue automatically, ask only when strictly necessary.

## Locked decisions for Phase 5

### 1) Scope and boundaries
Phase 5 changes are limited to `gsd/` and primarily:
- `gsd/runner/Dockerfile`
- `gsd/docs/deployment.md`
- `gsd/frontend/.env.example` (if needed)
- `gsd/runner/.env.example` (if needed)
- `gsd/.planning/phases/5/*`

No create/edit/delete outside `gsd/`.

### 2) Frontend deployment target (Vercel)
- Framework preset: Vite.
- Root directory: `gsd/frontend`.
- Build command: `npm run build`.
- Output directory: `dist`.
- Install command: `npm ci`.
- Required env var: `VITE_TYC_API_BASE_URL`.

### 3) Runner deployment target (Docker-capable host)
- Runner must remain external to Vercel.
- Docker image includes Python runtime + Java runtime for Jasmin/JVM pipeline.
- Container runs non-root user.
- Expose runner service at port 8000.

### 4) Runtime environment contract
Document runner env keys (from spec):
- `TYC_ALLOWED_ORIGINS`
- `TYC_DEFAULT_TIMEOUT_SECONDS`
- `TYC_MAX_TIMEOUT_SECONDS`
- `TYC_MAX_SOURCE_BYTES`
- `TYC_MAX_STDIN_BYTES`
- `TYC_MAX_OUTPUT_BYTES`
- `TYC_MAX_CONCURRENT_RUNS`

### 5) Security/deployment guidance to include
- CORS allowlist bound to deployed Vercel origin.
- Resource limits (CPU/RAM) for runner host.
- No writable host mounts for user execution workspace.
- Optional/no-network execution recommendation where platform supports it.

### 6) Non-goals in Phase 5
- No frontend feature changes.
- No backend API contract changes.
- No production infra provisioning scripts (Terraform/K8s) unless explicitly required.

### 7) Verification expectations for planning handoff
Plan must include:
1. Runner Dockerfile implementation and sanity build command.
2. Deployment guide for Vercel frontend + runner host.
3. Env variable documentation/examples for both tiers.
4. Basic deploy-readiness checks (frontend build, docker build syntax, doc completeness).
5. Isolation check proving no non-`gsd/` mutations.

## Acceptance criteria for discuss completion
- Deployment architecture is explicit: Vercel frontend + external Docker runner.
- Required config/env/documentation set is locked.
- Scope excludes infra overreach and stays in `gsd/`.
- Ready for `/gsd-plan-phase 5`.
