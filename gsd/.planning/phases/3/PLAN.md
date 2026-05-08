# Phase 3 PLAN — AST serialization and diagnostics contract

## Scope
Phase 3 only. Allowed write scope: `gsd/**`.

### In scope
- Add AST serializer module and wire it into run/ast endpoints.
- Normalize status + diagnostics per `gsd/WEBAPP_SPEC.md` for parse/ast/semantic/codegen/assemble/run paths.
- Enforce deterministic stage-transition contract for success/failure/skipped stages.
- Add Phase 3 tests for AST payload contract and status mapping.
- Add/update dirty-tree-safe isolation baseline/check for this phase.

### Out of scope (deferred)
- Frontend/UI changes.
- Deployment docs/config.
- New hardening areas outside Phase 3 contract work.

## Locked decisions to implement
- **D-01 (Scope/files):** only modify files under `gsd/` and keep implementation focused on runner app + phase3 tests.
- **D-02 (AST serialization):** implement recursive serializer exactly: primitive/list/AST node `{kind,fields}`/`None->null`/fallback `str(value)`; `/api/v1/run` includes AST only when `includeAst=true`; `/api/v1/ast` always returns `astText` and `astJson` on success.
- **D-03 (Diagnostics/status mapping):** map lexer/syntax/ast/semantic/codegen/assembly/runtime/timeout/internal to spec statuses and stages.
- **D-04 (Stage transitions):** fixed keys `parse, ast, semantic, codegen, assemble, run`; on failure mark current stage `failed`, later `skipped`, earlier completed stages `success`.
- **D-05 (includeAst behavior):** preserve AST on semantic and later failures when parse+AST succeeded and `includeAst=true`; allow null AST when `includeAst=false`.
- **D-06 (Testing):** add tests for `/api/v1/ast` contract, semantic AST retention, syntax mapping, runtime mapping, timeout mapping, stage transitions, and isolation guard.
- **D-07 (Isolation):** no writes outside `gsd/`; explicit guard against root `build/` and `src/runtime/` leakage; isolation check must tolerate pre-existing dirty non-`gsd` repo state.

## Task breakdown

### Task 1 — Implement AST serializer and pipeline result normalization (D-02, D-03, D-04, D-05)
**Create/Edit files**
- `gsd/runner/app/ast_serializer.py` (new)
- `gsd/runner/app/compiler_service.py`
- `gsd/runner/app/schemas.py`

**Implementation**
- Add `serialize_ast(value)` in `ast_serializer.py` with exact recursive contract from spec/decision D-02.
- Refactor compiler service to return a richer result payload (status, diagnostics, stages, optional ast payload, stdout/stderr, duration placeholder compatibility) so API layer does not guess failure stage.
- In compiler service, normalize exceptions by type/source into D-03 mapping:
  - lexer exceptions -> `lexical_error` + stage `lex`
  - parser/listener syntax exceptions -> `syntax_error` + stage `parse`
  - AST-generation errors -> `ast_error` + stage `ast`
  - checker errors -> `semantic_error` + stage `semantic`
  - codegen errors -> `codegen_error` + stage `codegen`
  - assembly returncode!=0 -> `assembly_error` + stage `assemble`
  - JVM returncode!=0 -> `runtime_error` + stage `run`
  - timeout -> `timeout` + stage of active subprocess (assemble/run)
  - fallback -> `internal_error` + stage `internal`
- Build deterministic stage transition helper in service (D-04): fixed stage keys, success path all success, failure path current failed/later skipped/earlier success.
- Ensure AST retention rules (D-05): keep `astText/astJson` for semantic/codegen/assembly/runtime failures only when parse+AST succeeded and caller requested includeAst.

**Acceptance**
- Service exposes enough structured data for API handlers to emit contract-compliant responses without hardcoded fake diagnostics/stages.
- AST serializer output for AST nodes is non-empty structured `{kind, fields}` form.

---

### Task 2 — Wire API endpoints to contract-compliant responses (D-02, D-03, D-04, D-05)
**Create/Edit files**
- `gsd/runner/app/main.py`
- `gsd/runner/app/schemas.py` (only if tightening response typing needed)

**Implementation**
- Update `/api/v1/run` to pass through `includeAst` to service and return real diagnostics, stages, stdout/stderr, and status from normalized result (D-03/D-04/D-05).
- Remove placeholder AST/stage fields currently hardcoded in `main.py`; map API payload directly from service result.
- Enforce includeAst behavior in HTTP response:
  - `includeAst=false` => `astText=null`, `astJson=null`.
  - `includeAst=true` + parse/AST success => preserve AST even on semantic+later failures.
- Update `/api/v1/ast` success response to always include `astText` and serializer-derived `astJson`; on error return mapped status+diagnostic (not generic internal-only shape) when classification is available.
- Keep `input_too_large` handling and other phase-2 limits unchanged.

**Acceptance**
- `/api/v1/run` and `/api/v1/ast` both return spec-conformant diagnostic objects (`stage,severity,message,line,column,raw`) and stable statuses.
- Stage status object reflects real pipeline progress instead of blanket failed/success placeholders.

---

### Task 3 — Add Phase 3 tests and robust dirty-repo isolation checks (D-06, D-07)
**Create/Edit files**
- `gsd/runner/tests/test_phase3_ast_endpoint.py`
- `gsd/runner/tests/test_phase3_run_status_mapping.py`
- `gsd/runner/tests/test_phase3_stage_transitions.py`
- `gsd/runner/tests/test_phase3_isolation.py`
- `gsd/.planning/phases/3/isolation-baseline.json`

**Implementation**
- Add tests covering D-06 minimums:
  1. `/api/v1/ast` returns non-empty `astText` and structured `astJson` with top-level `kind` + `fields`.
  2. `/api/v1/run` semantic failure returns `semantic_error` and retains AST when `includeAst=true`.
  3. `/api/v1/run` syntax failure returns `syntax_error` with diagnostic stage `parse`.
  4. `/api/v1/run` runtime non-zero maps `runtime_error` and exposes stderr.
  5. `/api/v1/run` timeout maps `timeout`.
  6. Stage transitions assert current failed / later skipped / prior success for semantic, assembly, and runtime failure fixtures.
- For runtime/timeout paths, use monkeypatch on workspace execute/assemble where necessary so tests stay deterministic and fast.
- Add robust isolation test for D-07 using phase-specific baseline file (`gsd/.planning/phases/3/isolation-baseline.json`) and delta logic that tolerates pre-existing dirty non-`gsd` changes:
  - Fail only for newly introduced non-`gsd` paths or changed hash of pre-existing dirty non-`gsd` tracked files.
  - Explicitly assert no new root `build/` or `src/runtime/` generated artifacts relative to baseline.
- Keep isolation assertions path-normalized and git-porcelain-based so checks remain stable on dirty baseline repos.

**Acceptance**
- Phase 3 test suite proves contract behavior and isolation without requiring clean repo.
- Isolation guard remains green even when unrelated non-`gsd` files were already dirty before Phase 3 execution.

## Verification commands (Phase 3)
Run from repository root:

1. `PYTHONPATH=gsd python gsd/runner/scripts/prepare_compiler_assets.py`
2. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_ast_endpoint.py -q`
3. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_run_status_mapping.py -q`
4. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_stage_transitions.py -q`
5. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase3_isolation.py -q`
6. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_phase2_pipeline_success.py gsd/runner/tests/test_phase3_*.py -q`

## Requirement traceability
- FR-06: stable status contract (`run` + `ast` status mapping, stage tracking)
- FR-07: normalized diagnostic object shape + parsing of line/column when available
- FR-08: `astText` + `astJson` contract and includeAst semantics
- VR-01/VR-02: backend/API tests for semantic/syntax/runtime/timeout/ast endpoint
- VR-04 + NFR-01: isolation checks with dirty-tree-safe baseline delta

## Isolation verification design note
Do not gate by global clean working tree. Compare against phase baseline and fail only on new/modified non-`gsd` deltas, plus explicit root `build/` and `src/runtime/` leak checks.

## Exit criteria
- `gsd/runner/app/ast_serializer.py` exists and serializer contract matches spec.
- `/api/v1/run` and `/api/v1/ast` return contract-compliant statuses, diagnostics, and stage transitions.
- Semantic and later failures preserve AST when `includeAst=true` and parse+AST succeeded.
- Phase 3 tests pass, including robust isolation checks for dirty baseline repositories.
- No create/edit/delete outside `gsd/`.
