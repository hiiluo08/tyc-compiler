# Phase 3 UAT — AST serialization and diagnostics contract

## Scope verified
- Phase 3 goal: AST serialization + diagnostics/status/stage contract completion for runner API.
- Verification sources: `gsd/WEBAPP_SPEC.md`, `gsd/.planning/phases/3-CONTEXT.md`, `gsd/.planning/phases/3/PLAN.md`.

## Test results

### UAT-3.1: AST endpoint returns contract payload
- Check: `/api/v1/ast` returns non-empty `astText` and structured `astJson` (`kind`, `fields`).
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_ast_endpoint.py -q`
- Result: **PASS**

### UAT-3.2: Run status mapping and diagnostics
- Check:
  - semantic mismatch -> `semantic_error` and AST preserved when `includeAst=true`
  - syntax error -> `syntax_error` + diagnostic stage `parse`
  - runtime non-zero -> `runtime_error` with stderr
  - timeout -> `timeout`
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_run_status_mapping.py -q`
- Result: **PASS**

### UAT-3.3: Deterministic stage transitions
- Check:
  - semantic failure: prior `success`, current `failed`, later `skipped`
  - success path: all stages `success`
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_stage_transitions.py -q`
- Result: **PASS**

### UAT-3.4: Isolation guard under dirty baseline
- Check:
  - no new/changed non-`gsd` files introduced by Phase 3 execution
  - no new root `build/` or root `src/runtime/` generated artifacts
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_isolation.py -q`
  - baseline: `gsd/.planning/phases/3/isolation-baseline.json`
- Result: **PASS**

### UAT-3.5: Regression/compatibility
- Check: Phase 2 pipeline success tests still pass with Phase 3 refactor.
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_pipeline_success.py gsd/runner/tests/test_phase3_*.py -q`
- Result: **PASS**

## Aggregate verification run
- Evidence: `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`
- Result: **PASS** (`31 passed`)

## Goal-backward verdict
**PASS** — Phase 3 objective is achieved:
- AST serializer contract implemented,
- `/run` and `/ast` response contracts normalized,
- diagnostic/stage behavior verified by tests,
- isolation preserved.

## Gaps found
- None at Phase 3 scope.

## Fix plan needed?
- No.
