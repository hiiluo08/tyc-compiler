# Phase 2 PLAN — Isolated compiler integration and runtime workspace

## Scope
Phase 2 only. Allowed write scope: `gsd/**`.

### In scope
- Vendor-core compiler copy/adaptation under `gsd/runner/compiler_vendor/`
- Codegen output path parameterization (`output_dir`) in vendorized emitter/codegen
- Build-time ANTLR generation and runtime asset setup under `gsd/runner/`
- Per-request runtime workspace lifecycle (create/copy/generate/assemble/run/cleanup)
- Phase-2 backend integration/isolation tests under `gsd/runner/tests/`

### Out of scope (deferred)
- Frontend implementation and UI checks
- Deployment config/docs
- Full diagnostics normalization breadth targeted for Phase 3

## Locked decisions to implement
1. File layout must stay inside `gsd/runner/**` and tests in `gsd/runner/tests/`.
2. Root compiler is read-only reference; runner uses `compiler_vendor` modules.
3. ANTLR/runtime assets prepared at build time in `gsd/runner/build` + `gsd/runner/runtime_assets`.
4. Request-scoped workspace lifecycle with cleanup in `finally` and single timeout budget.
5. Integration failure mapping in Phase 2: `assembly_error`, `timeout`, `internal_error`.
6. Phase-2 tests must cover vendor output isolation, workspace lifecycle, minimal E2E run path, and root-write isolation.

## Task breakdown

### Task 1 — Vendor core compiler modules and inject output_dir contract
**Create/Edit files**
- `gsd/runner/compiler_vendor/astgen/__init__.py`
- `gsd/runner/compiler_vendor/astgen/ast_generation.py`
- `gsd/runner/compiler_vendor/semantics/__init__.py`
- `gsd/runner/compiler_vendor/semantics/static_checker.py`
- `gsd/runner/compiler_vendor/semantics/static_error.py`
- `gsd/runner/compiler_vendor/codegen/__init__.py`
- `gsd/runner/compiler_vendor/codegen/codegen.py`
- `gsd/runner/compiler_vendor/codegen/emitter.py`
- `gsd/runner/compiler_vendor/codegen/frame.py`
- `gsd/runner/compiler_vendor/codegen/jasmin_code.py`
- `gsd/runner/compiler_vendor/codegen/io.py`
- `gsd/runner/compiler_vendor/utils/__init__.py`
- `gsd/runner/compiler_vendor/utils/nodes.py`
- `gsd/runner/compiler_vendor/utils/visitor.py`
- `gsd/runner/compiler_vendor/grammar/lexererr.py`

**Implementation**
- Copy/adapt only core pipeline modules required for parse→AST→semantic→codegen (per locked decisions 1 and 2).
- Rewrite imports so vendored modules resolve only through `gsd/runner` package context (no runtime dependency on root `src/*` modules).
- Adapt vendorized `Emitter` constructor to accept `output_dir` and emit `.j` files only into that directory.
- Adapt vendorized `CodeGenerator` API to receive and forward `output_dir` into emitter construction.
- Keep built-in I/O function definitions in checker/codegen copies consistent with existing compiler behavior.
- Add a small import-policy guard in tests (Task 4) to fail if `src.` imports remain in vendor core.

**Acceptance**
- Vendor compiler modules import successfully from `gsd/runner` context.
- Vendor codegen cannot write to root `src/runtime/` by default because output directory is explicit input.

---

### Task 2 — Add build-time isolated ANTLR/runtime asset setup and workspace lifecycle runner
**Create/Edit files**
- `gsd/runner/scripts/prepare_compiler_assets.py`
- `gsd/runner/build/__init__.py`
- `gsd/runner/runtime_assets/.gitkeep`
- `gsd/runner/app/runtime_workspace.py`
- `gsd/runner/app/compiler_service.py`

**Implementation**
- Implement `prepare_compiler_assets.py` to perform build-time setup inside `gsd/runner/` (per locked decision 3):
  1) generate ANTLR lexer/parser/visitor into `gsd/runner/build/`
  2) copy required runtime assets (`jasmin.jar`, `io.java`) into `gsd/runner/runtime_assets/`
  3) compile `io.java` to `io.class` in `gsd/runner/runtime_assets/`
- Keep this setup idempotent and path-anchored to `gsd/runner` absolute paths.
- Implement `runtime_workspace.py` to manage per-request workspace (per locked decision 4): create unique temp dir under gsd-controlled root, copy runtime assets, call vendor codegen with `output_dir`, run Jasmin assembly, run JVM class, and always cleanup in `finally`.
- Enforce one timeout budget input (`timeoutSeconds`) consistently across assemble/run subprocess calls.
- Implement `compiler_service.py` pipeline adapter using generated parser/lexer from `gsd/runner/build` and vendor modules from `compiler_vendor`; map errors for this phase to contract statuses (`assembly_error`, `timeout`, `internal_error`) per locked decision 5.

**Acceptance**
- A valid sample program can pass through compile→assemble→run using isolated workspace.
- ANTLR and runtime assets are generated/prepared only under `gsd/runner/**`.
- Workspace directories are removed in both success and failure paths.

---

### Task 3 — Add Phase-2 integration tests and dirty-tree-safe isolation verification
**Create/Edit files**
- `gsd/runner/tests/test_phase2_vendor_output_dir.py`
- `gsd/runner/tests/test_phase2_workspace_lifecycle.py`
- `gsd/runner/tests/test_phase2_pipeline_success.py`
- `gsd/runner/tests/test_phase2_pipeline_cases.py`
- `gsd/runner/tests/test_phase2_isolation.py`
- `gsd/.planning/phases/2/isolation-baseline.json`

**Implementation**
- Add tests for locked decision 6 coverage:
  - Vendor codegen writes `.j` only to provided workspace path.
  - Workspace cleanup executes on success and on simulated failure/timeout paths.
  - Minimal E2E backend compile→assemble→run succeeds for sample (`printString`), including stdin case.
  - Timeout path maps to `timeout`.
- Add robust isolation verification that tolerates pre-existing dirty non-`gsd` files:
  - Capture baseline of current dirty non-`gsd` tracked file hashes into `gsd/.planning/phases/2/isolation-baseline.json`.
  - In isolation test, compare post-run state against baseline and fail only when:
    1) new changed paths outside `gsd/` are introduced, or
    2) content hash of pre-existing dirty non-`gsd` tracked files changed.
  - Add explicit negative assertions that root `build/` and root `src/runtime/` gain no new generated artifacts from Phase-2 flows.

**Acceptance**
- Isolation test passes even when repository starts with unrelated non-`gsd` dirty files.
- Phase-2 test suite proves vendor output isolation, workspace lifecycle correctness, and minimal pipeline execution.

## Verification commands (Phase 2)
Run from repository root:

1. `PYTHONPATH=gsd python gsd/runner/scripts/prepare_compiler_assets.py`
2. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_vendor_output_dir.py -q`
3. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_workspace_lifecycle.py -q`
4. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_pipeline_success.py gsd/runner/tests/test_phase2_pipeline_cases.py -q`
5. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_isolation.py -q`
6. `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`

## Isolation verification design note
Do not gate isolation by plain global `git status` cleanliness. Use baseline/delta comparison scoped to non-`gsd` paths so checks remain deterministic with pre-existing root dirty files.

## Exit criteria
- All implementation/test artifacts for this phase are under `gsd/` only.
- Vendor-core adaptation is complete and codegen output is parameterized by `output_dir`.
- Build-time ANTLR/runtime asset preparation under `gsd/runner/` is executable.
- Runtime workspace lifecycle is enforced with guaranteed cleanup.
- Phase-2 integration + isolation tests pass.
- No frontend/deploy scope is included.
