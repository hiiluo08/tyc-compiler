# Retrospective — TyC Web Compiler (GSD Variant)

## What worked well

1. **Strict isolation strategy**
   - Keeping all work inside `gsd/` prevented accidental cross-impact on root compiler code.
   - Baseline-delta isolation tests provided repeatable guardrails.

2. **Phase-by-phase contract hardening**
   - Splitting backend foundation, integration, and contract normalization reduced debugging complexity.
   - Explicit status/diagnostic/stage contracts improved frontend integration clarity.

3. **Typed frontend integration**
   - Centralized `types.ts` + `api.ts` reduced UI/API drift and stabilized testing.

## Friction points

1. **Working-directory-sensitive tests**
   - Isolation tests initially depended on CWD assumptions; this created false negatives when run outside repo root.

2. **Tooling/version alignment in new frontend scaffold**
   - Initial dependency/version config required quick corrections (`@monaco-editor/react`, Vite/Vitest config split).

3. **Parallel command failure coupling**
   - In some steps, one failing command cancelled sibling operations, causing extra reruns.

## Improvements for next cycle

1. Normalize all isolation tests to use repo-root absolute paths.
2. Add a single canonical test entry command in docs that always runs from repo root.
3. Add a lightweight preflight checklist before parallel command batches.
4. Pin frontend dependency versions deliberately after first green build/test pass.

## Overall assessment

The GSD loop worked effectively for this project shape: it enforced scope, improved traceability, and kept execution aligned to explicit phase goals. Most overhead came from path/tooling nuances rather than architectural uncertainty.
