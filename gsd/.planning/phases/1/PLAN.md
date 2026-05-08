# Phase 1 PLAN — Runner backend foundation and API schemas

## Scope
Phase 1 only. Allowed write scope: `gsd/**`.

### In scope
- FastAPI app skeleton for runner
- Contract-first schemas for `/health`, `/api/v1/run`, `/api/v1/ast`
- Centralized limits/constants for request bounds
- Smoke tests for health + validation + response top-level shape
- Verification-only isolation baseline/delta guard artifact under `gsd/.planning/phases/1/` (non-product, does not expand feature scope)

### Out of scope (deferred)
- ANTLR generation
- Compiler vendor copy/adaptation
- Jasmin/JVM compile-run
- Frontend implementation

## Locked decisions from discuss/research
1. Use spec defaults from `gsd/WEBAPP_SPEC.md`.
2. Phase 1 test depth = smoke only.
3. API endpoints must exist now: `GET /health`, `POST /api/v1/run`, `POST /api/v1/ast`.
4. Response shapes must be compatible with final contract (top-level keys reserved now).
5. Validation policy for Phase 1:
   - FastAPI/Pydantic validation errors may return HTTP 422.
   - For size-bound violations detected by custom byte checks, return contract body with `ok=false`, `status="input_too_large"`.
   - Full error/status normalization for compiler stages is finalized in Phase 3.

## Task breakdown

### Task 1 — Scaffold runner foundation files
**Create/Edit files**
- `gsd/runner/requirements-web.txt`
- `gsd/runner/app/__init__.py`
- `gsd/runner/app/limits.py`
- `gsd/runner/app/schemas.py`
- `gsd/runner/app/main.py`

**Implementation**
- Add FastAPI dependencies and test dependencies (`fastapi`, `uvicorn`, `pytest`, `httpx`).
- Define constants/defaults in `limits.py` matching spec:
  - source max: 65536 bytes
  - stdin max: 16384 bytes
  - default timeout: 3 sec
  - max timeout: 5 sec
  - max output bytes (reserved field usage): 32768
- Define contract enums/models in `schemas.py`:
  - status vocabulary including `success`, `syntax_error`, `semantic_error`, `runtime_error`, `timeout`, `input_too_large`, `internal_error` and other spec statuses
  - diagnostic model fields (`stage`, `severity`, `message`, `line`, `column`, `raw`)
  - stage-status keys (`parse`, `ast`, `semantic`, `codegen`, `assemble`, `run`)
  - run/ast request and response models
- Implement routes in `main.py`:
  - `GET /health` exact response contract
  - `POST /api/v1/run` and `POST /api/v1/ast` as Phase 1 stubs with contract-shaped top-level fields
  - byte-size checks (`source`, `stdin`) with deterministic `input_too_large` response

**Acceptance**
- App imports without errors.
- Endpoints are reachable and return schema-compatible responses.

---

### Task 2 — Add Phase 1 smoke tests
**Create files**
- `gsd/runner/tests/test_health.py`
- `gsd/runner/tests/test_run_validation.py`
- `gsd/runner/tests/test_ast_validation.py`
- `gsd/runner/tests/test_stub_shapes.py`

**Implementation**
- `test_health.py`: assert exact JSON for `/health`.
- `test_run_validation.py`:
  - missing `source` rejected
  - `timeoutSeconds` out of [1,5] rejected
  - non-boolean `includeAst` rejected
  - omitted `includeAst` uses schema default and returns contract-shaped response
  - oversized `source` rejected with `input_too_large`
  - oversized `stdin` rejected with `input_too_large`
  - valid stub request accepted with required top-level keys
- `test_ast_validation.py`:
  - missing `source` rejected
  - valid request accepted and returns ast top-level keys
- `test_stub_shapes.py`:
  - assert required response keys exist for run/ast success stub payloads

**Acceptance**
- Smoke suite passes from repo root with `PYTHONPATH=gsd`.

---

### Task 3 — Add isolation baseline/delta verification for this phase
**Create files**
- `gsd/.planning/phases/1/isolation-baseline.txt`
- `gsd/runner/tests/test_isolation_phase1.py`

**Implementation**
- During execute start, capture baseline into `isolation-baseline.txt` including:

  - `git status --porcelain` lines
  - content fingerprints for already-dirty non-`gsd/` tracked files using `git hash-object <path>`

- Implement delta test with two checks:

  1) newly introduced changed paths outside `gsd/` are forbidden
  2) already-dirty non-`gsd/` files from baseline must keep identical fingerprint after Phase 1
- Add explicit assertions that this phase does not create/update files under root `build/` or root `src/runtime/`, including already-dirty files.

**Acceptance**
- Isolation test passes even when repo already has pre-existing non-`gsd/` changes.

## Verification commands (Phase 1)
Run from repository root:

1. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_health.py -q`
2. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_run_validation.py gsd/runner/tests/test_ast_validation.py gsd/runner/tests/test_stub_shapes.py -q`
3. `PYTHONPATH=gsd python -m pytest gsd/runner/tests/test_isolation_phase1.py -q`
4. `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`

Isolation delta guard script (post-execute):

```bash
python - <<'PY'
import json, subprocess, pathlib, sys
base = pathlib.Path('gsd/.planning/phases/1/isolation-baseline.txt')
if not base.exists():
    print('missing baseline file')
    sys.exit(1)
data = json.loads(base.read_text(encoding='utf-8'))
base_status = set(data.get('status_lines', []))
base_hashes = data.get('dirty_non_gsd_hashes', {})
now_status = set(subprocess.check_output(['git','status','--porcelain'], text=True).splitlines())

added_lines = sorted([ln for ln in (now_status - base_status) if ln.strip()])
new_outside = []
for ln in added_lines:
    path = ln[3:].split(' -> ')[-1]
    if not path.startswith('gsd/'):
        new_outside.append(ln)

if new_outside:
    print('New non-gsd changes introduced:')
    print('\n'.join(new_outside))
    sys.exit(1)

for path, old_hash in base_hashes.items():
    p = pathlib.Path(path)
    if not p.exists():
        print(f'Pre-existing non-gsd file removed: {path}')
        sys.exit(1)
    new_hash = subprocess.check_output(['git','hash-object',path], text=True).strip()
    if new_hash != old_hash:
        print(f'Pre-existing non-gsd file content changed: {path}')
        sys.exit(1)

for blocked_prefix in ('build/', 'src/runtime/'):
    for ln in now_status:
        path = ln[3:].split(' -> ')[-1]
        if path.startswith(blocked_prefix):
            print(f'Blocked root artifact path changed: {ln}')
            sys.exit(1)

print('OK: no new or mutated non-gsd changes introduced in this phase')
PY
```

## Exit criteria
- All created/edited implementation files are under `gsd/` only.
- `/health`, `/api/v1/run`, `/api/v1/ast` exist and follow Phase 1 contract requirements.
- Smoke tests pass.
- Isolation delta check passes.
- No compiler integration/frontend work included.
