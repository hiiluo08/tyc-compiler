# Phase 4 CONTEXT — React + Vite frontend experience

## Phase goal (from ROADMAP)
Build frontend web app with editor, toolbar, result tabs, samples, and runner API integration under `gsd/frontend/` only.

## Inputs applied
- Authority spec: `gsd/WEBAPP_SPEC.md`
- Roadmap scope: `gsd/.planning/ROADMAP.md` (Phase 4)
- Prior phase outputs: `gsd/.planning/phases/3/*`
- Current backend contracts already available from Phase 1-3: `/health`, `/api/v1/run`, `/api/v1/ast`
- User preference in this loop: continue by default and ask only if truly necessary.

## Locked decisions for Phase 4

### 1) Scope and file boundaries
Phase 4 implementation is limited to `gsd/` and primarily:
- `gsd/frontend/package.json`
- `gsd/frontend/vite.config.ts`
- `gsd/frontend/tsconfig*.json`
- `gsd/frontend/index.html`
- `gsd/frontend/src/main.tsx`
- `gsd/frontend/src/App.tsx`
- `gsd/frontend/src/types.ts`
- `gsd/frontend/src/api.ts`
- `gsd/frontend/src/samples.ts`
- `gsd/frontend/src/components/*`
- `gsd/frontend/src/styles/*` (if needed)
- `gsd/.planning/phases/4/*`

No create/edit/delete outside `gsd/`.

### 2) Frontend stack and baseline
- Use React + Vite + TypeScript.
- Monaco editor via `@monaco-editor/react`.
- Keep styling lightweight (plain CSS/CSS modules acceptable); no extra UI framework unless required.
- Maintain a simple, readable component structure aligned to spec components.

### 3) API contract consumption
Frontend must consume existing runner API without changing backend contracts:
- `GET /health`
- `POST /api/v1/run`
- `POST /api/v1/ast`

`VITE_TYC_API_BASE_URL` is required as API base.
- In dev: allow fallback to local origin if explicitly coded in phase plan.
- In production mode: missing base URL must surface a clear runtime error state.

### 4) Required UI layout and components
Implement these components with clear boundaries:
- `CodeEditor` (Monaco, tab size 4, min-height ~400px)
- `Toolbar` (Run, Load Sample, Clear)
- `StdinPanel` (textarea)
- `ResultPanel` (tab host)
- `OutputPanel` (stdout + duration + status)
- `ErrorsPanel` (diagnostics, stderr, stage statuses)
- `AstPanel` (render `astJson`, fallback `astText`)

Layout target: two-column editor/result area + stdin block below, matching spec structure.

### 5) UI state machine (locked)
State set for Phase 4:
- `idle`
- `running`
- `success`
- `error`
- `timeout`
- `api_offline`

Behavior constraints:
- `running`: disable Run.
- Any terminal state: re-enable Run.
- Timeout maps to visible timeout status.
- Network/API failure maps to `api_offline` with friendly message.

### 6) Samples (minimum set)
Phase 4 must include at least these samples:
1. Hello TyC
2. Read integer
3. Syntax error
4. Semantic error
5. Timeout

Sample source/stdin follows `gsd/WEBAPP_SPEC.md` section 7.6.

### 7) Result rendering rules
- Output tab: show `stdout` and `durationMs` on success.
- Errors tab: show `status`, diagnostics list, `stderr` if present, and stage map.
- AST tab:
  - if `astJson` exists, show structured tree view.
  - fallback to `astText` when needed.
  - for non-parseable source, show empty/notice state.

### 8) Non-goals in Phase 4
- No runner deployment/Docker/CORS hardening expansion (Phase 5/6).
- No auth, persistence, sharing, or multi-file project support.
- No backend contract redesign.

### 9) Verification expectations for Phase 4 planning handoff
Plan must include:
1. Frontend scaffold + dependency setup under `gsd/frontend/`.
2. Typed API layer (`types.ts`, `api.ts`) aligned to current runner contract.
3. Component implementation and app composition.
4. Sample loading and run workflow wiring.
5. UI-state handling (`idle/running/success/error/timeout/api_offline`).
6. Basic frontend tests and/or deterministic checks for key state/render transitions.
7. Isolation check proving no non-`gsd/` mutations.

## Acceptance criteria for discuss completion
- Frontend architecture and component boundaries are explicit.
- API integration assumptions are locked without reopening Phase 1-3 contracts.
- Required sample set and UI states are fixed for planner/executor.
- Scope is strict to `gsd/` and ready for `/gsd-plan-phase 4`.
