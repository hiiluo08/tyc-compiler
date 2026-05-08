# Phase 2 CONTEXT — Isolated compiler integration and runtime workspace

## Phase goal (from ROADMAP)
Integrate TyC compile/run pipeline into runner under `gsd/runner/` with strict isolation and per-request workspace, without any write to root compiler/runtime paths.

## Inputs applied
- Authority spec: `gsd/WEBAPP_SPEC.md`
- Prior phase state: `gsd/.planning/STATE.md`
- Prior phase decisions: `gsd/.planning/phases/1-CONTEXT.md`
- User discuss decisions on 2026-05-07:
  - Use spec defaults for unresolved gray areas.
  - Vendor scope = core pipeline modules only.
  - ANTLR/runtime assets strategy = build-time generate/copy under `gsd/runner/`.
  - Timeout policy = single request budget for full compile+run pipeline.

## Locked decisions for Phase 2

### 1) File layout inside `gsd/runner/`
Phase 2 implementation is constrained to:
- `gsd/runner/compiler_vendor/`
  - `astgen/`
  - `semantics/`
  - `codegen/`
  - `utils/`
  - `grammar/lexererr.py` (or equivalent needed lexer error helper)
- `gsd/runner/build/` (ANTLR generated lexer/parser/visitor for this variant)
- `gsd/runner/runtime_assets/`
  - `jasmin.jar`
  - `io.java`
  - `io.class` (generated within gsd scope)
- `gsd/runner/app/compiler_service.py`
- `gsd/runner/app/runtime_workspace.py`
- tests under `gsd/runner/tests/`

No writes outside `gsd/` are allowed.

### 2) Integration boundaries
- Root compiler is read-only reference only.
- Runner must use vendorized pipeline modules from `gsd/runner/compiler_vendor/`.
- Codegen output must be parameterized to per-request workspace output directory.
- Absolutely no generation into root `src/runtime/` or root `build/`.

### 3) ANTLR/build/runtime asset strategy
- Build-time step inside `gsd/runner/` will:
  1) generate parser/lexer/visitor into `gsd/runner/build/`
  2) copy required runtime assets (`jasmin.jar`, `io.java`) into `gsd/runner/runtime_assets/`
  3) compile `io.java` to `io.class` in `gsd/runner/runtime_assets/`
- No per-request ANTLR generation.

### 4) Runtime workspace and timeout policy
- Each request creates a unique temp workspace under gsd-controlled temp root.
- Workspace flow:
  1) create temp dir
  2) copy runtime assets into temp dir
  3) generate `.j` outputs in temp dir
  4) assemble with Jasmin in temp dir
  5) run JVM in temp dir
  6) cleanup in `finally`
- Timeout policy: single request timeout budget (`timeoutSeconds`) applied consistently to compile/assemble/run subprocess calls.

### 5) Error handling and diagnostics for Phase 2
- Preserve Phase 1 response envelope and status vocabulary.
- Map integration failures to contract statuses where feasible in Phase 2:
  - assembly failure -> `assembly_error`
  - missing Java/toolchain/runtime assets -> `internal_error`
  - subprocess timeout -> `timeout`
- Full normalization breadth (all compiler stages) continues in Phase 3.

### 6) Test scope for Phase 2
Phase 2 tests focus on integration safety and minimal E2E backend path:
1. Build/runtime assets generated/copied only under `gsd/runner/*`.
2. Vendorized codegen writes outputs only into provided workspace dir.
3. Per-request workspace cleanup executes on success and failure.
4. Run sample program path works through compile→assemble→run in isolated temp dir.
5. Isolation test confirms no new root `build/`/`src/runtime/` writes.

### 7) Isolation enforcement
- Allowed: read root files for behavior parity.
- Forbidden: any create/edit/delete/move/generate outside `gsd/`.
- Forbidden: root `.planning/` artifacts.
- If any plan step requires root modification, stop and ask user.

## Non-goals in Phase 2
- Frontend work.
- Full diagnostics/AST contract completion (Phase 3 scope).
- Deployment configuration (Phase 5 scope).

## Acceptance criteria for planning handoff
- Planner can name exact Phase 2 files under `gsd/runner/`.
- Planner includes concrete task(s) to parameterize emitter/codegen output_dir in vendor copy.
- Planner includes build-time generation/copy flow for ANTLR + runtime assets under gsd scope.
- Planner includes workspace lifecycle tests and root-write isolation guards.
