# Verification Report — TyC Web Compiler (GSD Variant)

## Final command evidence

### Frontend
- `cd gsd/frontend && npm run build` → PASS
- `cd gsd/frontend && npm run test` → PASS (`5 passed`)

### Runner
- `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q` (from repo root) → PASS (`35 passed`)

## Acceptance criteria matrix

| Acceptance criterion | Evidence | Verdict |
| --- | --- | --- |
| All variant files stay inside `gsd/` | Phase isolation tests and artifact paths under `gsd/**` | PASS |
| Frontend builds with Vite | `npm run build` in `gsd/frontend` | PASS |
| Runner exposes `/health`, `/api/v1/run`, `/api/v1/ast` | Prior phase API tests and current runner suite pass | PASS |
| Valid TyC source displays stdout | Phase 2/3 pipeline tests | PASS |
| Syntax errors map to `syntax_error` | Phase 3 status mapping tests | PASS |
| Semantic errors preserve AST | Phase 3 mapping/AST tests | PASS |
| Runtime non-zero maps `runtime_error` | Phase 3 mapping tests | PASS |
| Infinite loop maps `timeout` | Phase 3 timeout tests | PASS |
| AST tab input (`astJson`/`astText`) available for parseable source | Frontend + runner contract tests | PASS |
| Deployment docs/config provided | `gsd/docs/deployment.md`, `gsd/runner/Dockerfile`, `.env.example` files | PASS |

## Final verdict

**PASS** — The GSD variant meets the scoped acceptance criteria at local verification level.
