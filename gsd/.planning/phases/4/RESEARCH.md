# Phase 4: React + Vite frontend experience - Research

**Researched:** 2026-05-07  
**Domain:** TyC frontend implementation (editor, tabs, samples, API integration)  
**Confidence:** HIGH

## Summary

Phase 4 should implement a thin, typed frontend over the already-stable backend contract from Phase 1-3. The safest path is to keep API mapping centralized in `src/api.ts`, keep transport/contract types in `src/types.ts`, and make UI components presentational where possible to reduce state coupling.

The backend now provides stable `status`, `diagnostics`, `stages`, `astText`, `astJson`, `stdout`, `stderr`, and `durationMs`, so frontend scope is mainly state orchestration and rendering quality. No backend contract changes are needed in this phase.

## Locked Constraints Applied

- Write scope strictly `gsd/**`.
- Frontend stack: React + Vite + TypeScript.
- Required components: CodeEditor, Toolbar, StdinPanel, ResultPanel, OutputPanel, ErrorsPanel, AstPanel.
- Required UI states: `idle`, `running`, `success`, `error`, `timeout`, `api_offline`.
- Required samples: Hello, Read integer, Syntax error, Semantic error, Timeout.

## Recommended Architecture

```text
gsd/frontend/src/
  main.tsx
  App.tsx
  api.ts
  types.ts
  samples.ts
  components/
    CodeEditor.tsx
    Toolbar.tsx
    StdinPanel.tsx
    ResultPanel.tsx
    OutputPanel.tsx
    ErrorsPanel.tsx
    AstPanel.tsx
```

### State ownership
- `App.tsx` owns source/stdin/uiState/activeTab/latestResult/errorMessage.
- `api.ts` owns fetch + response parsing + offline/timeout transport classification.
- Panels receive typed props and avoid side effects.

### API typing pattern
- Define request/response types mirroring backend contract in `types.ts`.
- `api.ts` exports:
  - `runProgram(payload)` for `/api/v1/run`
  - `getAst(source)` for `/api/v1/ast`
- Surface transport failures distinctly so `App.tsx` can set `api_offline`.

## Implementation Risks and Mitigation

1. **State drift between tabs and latest run result**
   - Mitigation: single `latestResult` object in `App.tsx`; tabs only render projections.

2. **Monaco integration complexity**
   - Mitigation: keep `CodeEditor` wrapper minimal (value + onChange + height/options).

3. **Missing env var in production**
   - Mitigation: fail fast in `api.ts` when `import.meta.env.VITE_TYC_API_BASE_URL` is absent in production mode.

4. **Large AST render cost**
   - Mitigation: render collapsed tree nodes by default; fallback to `astText` when needed.

## Verification Guidance for Phase 4

Minimum checks during execute/verify:
1. App bootstraps via Vite and renders default sample.
2. Run success sample -> `success` + stdout visible.
3. Syntax sample -> `error` + parse diagnostic visible.
4. Semantic sample -> `error` + semantic diagnostic + AST visible.
5. Timeout sample -> `timeout` state and Run re-enabled.
6. Simulated offline API -> `api_offline` state.
7. No non-`gsd/` file mutations.

## Tools and Dependencies

- `react`, `react-dom`, `typescript`, `vite`.
- `@monaco-editor/react` for editor.
- Optional lightweight CSS only (no heavy UI framework required).

## Exit signal for planning handoff

Research is sufficient to produce an executable plan with:
- scaffold tasks,
- typed API integration,
- component implementation,
- state machine wiring,
- build/test/isolation verification.
