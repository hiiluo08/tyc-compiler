# Phase 1 UAT — Runner foundation and API schemas

## Scope verified
- Phase 1 goal from roadmap: runner backend foundation + API schemas.
- Verification source: `gsd/WEBAPP_SPEC.md`, `gsd/.planning/phases/1-CONTEXT.md`, `gsd/.planning/phases/1/PLAN.md`.

## Test results

### UAT-1: Health endpoint contract
- Check: `GET /health` returns exact fields and values.
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_health.py -q`
- Result: **PASS** (1 passed)

### UAT-2: `/api/v1/run` validation bounds and typing
- Check:
  - missing `source` rejected
  - `timeoutSeconds` outside [1,5] rejected
  - non-boolean `includeAst` rejected
  - omitted `includeAst` uses default
  - oversized `source` and `stdin` map to `input_too_large`
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_run_validation.py -q`
- Result: **PASS**

### UAT-3: `/api/v1/ast` validation + contract shape
- Check:
  - missing `source` rejected
  - oversized `source` -> `input_too_large`
  - valid request returns required top-level keys
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_ast_validation.py -q`
- Result: **PASS**

### UAT-4: Stub response contract shape
- Check:
  - run response includes: `ok,status,stdout,stderr,diagnostics,astText,astJson,stages,durationMs,truncated`
  - ast response includes: `ok,status,diagnostics,astText,astJson,durationMs`
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_stub_shapes.py -q`
- Result: **PASS**

### UAT-5: Isolation guard
- Check:
  - no new/modified non-`gsd/` file introduced by Phase 1 execution
  - no root `build/` or root `src/runtime/` artifact touched by Phase 1
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_isolation_phase1.py -q`
  - post-execute delta guard script from `PLAN.md`
- Result: **PASS**

## Aggregate verification run
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`
- Result: **PASS** (15 passed)

## Goal-backward verdict
**PASS** — Phase 1 objective is achieved:
- foundational runner API exists,
- schema-first validation is active,
- smoke test coverage exists and passes,
- isolation rule remains intact.

## Gaps found
- None at Phase 1 scope.

## Fix plan needed?
- No.
