# Phase 2 UAT — Isolated compiler integration and runtime workspace

## Scope verified
- Phase 2 goal from roadmap: isolated compiler integration + ANTLR/build/runtime assets + request-scoped workspace lifecycle.
- Verification sources: `gsd/WEBAPP_SPEC.md`, `gsd/.planning/phases/2-CONTEXT.md`, `gsd/.planning/phases/2/PLAN.md`.

## Test results

### UAT-2.1: Build-time assets prepared inside gsd scope
- Check:
  - ANTLR artifacts generated under `gsd/runner/build/`
  - runtime assets prepared under `gsd/runner/runtime_assets/`
- Evidence:
  - `PYTHONPATH=gsd python gsd/runner/scripts/prepare_compiler_assets.py`
- Result: **PASS**

### UAT-2.2: Vendor codegen output isolation
- Check:
  - vendored codegen writes `.j` only to provided workspace (`output_dir`)
  - no implicit write to root runtime path
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_vendor_output_dir.py -q`
- Result: **PASS**

### UAT-2.3: Workspace lifecycle (create/copy/cleanup)
- Check:
  - workspace created per run context
  - runtime assets copied into workspace
  - cleanup performed on exit
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_workspace_lifecycle.py -q`
- Result: **PASS**

### UAT-2.4: Minimal E2E pipeline success path
- Check:
  - compile→assemble→run success for hello sample
  - stdin path success for `readInt` sample
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_pipeline_success.py -q`
- Result: **PASS**

### UAT-2.5: Timeout/error path coverage for phase scope
- Check:
  - timeout case mapped to `timeout` status
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_pipeline_cases.py -q`
- Result: **PASS**

### UAT-2.6: Isolation guard under dirty repository baseline
- Check:
  - no new non-`gsd/` changes introduced by Phase 2 work
  - no new root `build/` or root `src/runtime/` generated artifacts from Phase 2 flows
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_isolation.py -q`
  - baseline file: `gsd/.planning/phases/2/isolation-baseline.json`
- Result: **PASS**

## Aggregate verification run
- Evidence:
  - `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`
- Result: **PASS** (`22 passed`)

## Goal-backward verdict
**PASS** — Phase 2 objective is achieved:
- isolated vendor-core integration is active,
- runtime workspace lifecycle is enforced,
- assets are prepared under `gsd/runner/` only,
- integration/isolation tests pass.

## Gaps found
- None at Phase 2 scope.

## Fix plan needed?
- No.
