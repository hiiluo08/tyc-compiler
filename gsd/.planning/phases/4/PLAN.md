# Phase 4 PLAN — React + Vite frontend experience

## Scope
Phase 4 only. Allowed write scope: `gsd/**`.

### In scope
- Create frontend app under `gsd/frontend/` using React + Vite + TypeScript.
- Implement editor + toolbar + stdin + result tabs + samples.
- Integrate with existing runner API (`/health`, `/api/v1/run`, `/api/v1/ast`).
- Implement required UI states and error/status rendering.
- Add phase-4 verification tests/checks and isolation guard.

### Out of scope
- Backend contract changes.
- Deployment and Docker changes (Phase 5).
- Auth/history/share/multi-file/debugger features.

## Locked decisions to implement
- **D4-01**: All files remain inside `gsd/`.
- **D4-02**: Stack is React + Vite + TypeScript + Monaco (`@monaco-editor/react`).
- **D4-03**: Components are `CodeEditor`, `Toolbar`, `StdinPanel`, `ResultPanel`, `OutputPanel`, `ErrorsPanel`, `AstPanel`.
- **D4-04**: UI states are fixed: `idle`, `running`, `success`, `error`, `timeout`, `api_offline`.
- **D4-05**: Use typed API layer in `src/api.ts` and shared contract types in `src/types.ts`.
- **D4-06**: Required samples: Hello, Read integer, Syntax error, Semantic error, Timeout.
- **D4-07**: Keep backend contract unchanged; frontend adapts to Phase 3 responses.

## Task breakdown

### Task 1 — Scaffold frontend app structure (D4-01, D4-02)
**Create/Edit files**
- `gsd/frontend/package.json`
- `gsd/frontend/tsconfig.json`
- `gsd/frontend/tsconfig.node.json`
- `gsd/frontend/vite.config.ts`
- `gsd/frontend/index.html`
- `gsd/frontend/src/main.tsx`
- `gsd/frontend/src/App.tsx`
- `gsd/frontend/src/index.css` (or equivalent)

**Implementation**
- Initialize Vite React TS project layout in `gsd/frontend/`.
- Configure scripts: `dev`, `build`, `preview`, `test` (if test runner added in this phase).
- Ensure app boots with a minimal shell and no dependency on root configs.

**Acceptance**
- `npm run build` succeeds under `gsd/frontend/`.
- App renders baseline shell locally.

---

### Task 2 — Implement typed API client and shared contracts (D4-05, D4-07)
**Create/Edit files**
- `gsd/frontend/src/types.ts`
- `gsd/frontend/src/api.ts`

**Implementation**
- Define TypeScript types for run/ast requests and responses aligned with backend.
- Implement `runProgram()` and `getAst()` with fetch-based client.
- Add API base resolution from `VITE_TYC_API_BASE_URL`.
- Map transport/network failures into a frontend-consumable offline error.

**Acceptance**
- API methods return strongly typed result objects.
- Missing API base URL in production causes explicit error path.

---

### Task 3 — Implement sample catalog and UI components (D4-03, D4-06)
**Create/Edit files**
- `gsd/frontend/src/samples.ts`
- `gsd/frontend/src/components/CodeEditor.tsx`
- `gsd/frontend/src/components/Toolbar.tsx`
- `gsd/frontend/src/components/StdinPanel.tsx`
- `gsd/frontend/src/components/ResultPanel.tsx`
- `gsd/frontend/src/components/OutputPanel.tsx`
- `gsd/frontend/src/components/ErrorsPanel.tsx`
- `gsd/frontend/src/components/AstPanel.tsx`

**Implementation**
- Add minimum 5 samples from spec.
- Build each component with typed props and clear responsibility.
- `AstPanel` renders `astJson` tree and `astText` fallback.

**Acceptance**
- Load Sample updates source/stdin correctly.
- Tabs render output/errors/AST from latest result.

---

### Task 4 — Wire app state machine and run flow (D4-04, D4-05)
**Create/Edit files**
- `gsd/frontend/src/App.tsx`
- `gsd/frontend/src/index.css` (or component CSS)

**Implementation**
- Keep central state in `App.tsx`: source, stdin, uiState, activeTab, latestResult.
- Implement Run flow:
  - set `running`, disable Run.
  - call `runProgram`.
  - map backend status to `success` / `error` / `timeout`.
  - map transport failure to `api_offline`.
  - always re-enable Run on terminal state.
- Implement Clear flow to reset state.

**Acceptance**
- Required UI states transition correctly.
- Timeout and offline cases are user-visible and recoverable.

---

### Task 5 — Add verification coverage and isolation checks
**Create/Edit files**
- `gsd/frontend/src/*.test.*` and/or `gsd/frontend/tests/*` (if test setup chosen)
- `gsd/runner/tests/test_phase4_isolation.py` (or `gsd/tests/test_phase4_isolation.py`)
- `gsd/.planning/phases/4/isolation-baseline.json`

**Implementation**
- Add deterministic checks for:
  1. sample load behavior,
  2. run button disabled during running,
  3. success rendering,
  4. syntax/semantic error rendering,
  5. timeout/offline state handling.
- Add phase-4 isolation check proving no new mutations outside `gsd/`.

**Acceptance**
- Frontend checks pass with stable outputs.
- Isolation guard passes on dirty baseline strategy.

## Verification commands (Phase 4)
Run from repository root (or noted directory):

1. `cd gsd/frontend && npm install`
2. `cd gsd/frontend && npm run build`
3. `cd gsd/frontend && npm run test` (if test runner configured)
4. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase4_isolation.py -q` (or chosen isolation test path)

## Requirement traceability
- FR-01/FR-02: browser editor + stdin + run UX.
- FR-09/FR-10/FR-11: output/error/AST tabs and sample-driven UX.
- VR-03: frontend manual/automated behavior checks.
- VR-04 + NFR-01: isolation validation (no out-of-scope writes).

## Exit criteria
- Frontend exists and builds under `gsd/frontend/`.
- Run flow works against existing runner API contract.
- Required states/tabs/samples are implemented.
- Verification checks pass for core UX and isolation.
- No create/edit/delete outside `gsd/`.
