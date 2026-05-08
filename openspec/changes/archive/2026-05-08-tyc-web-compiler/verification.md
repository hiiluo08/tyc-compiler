# Verification: tyc-web-compiler

Date: 2026-05-08

## 1) Completeness

### Artifact coverage
- Proposal: `openspec/changes/tyc-web-compiler/proposal.md`
- Delta spec: `openspec/changes/tyc-web-compiler/specs/web-compiler/spec.md`
- Design: `openspec/changes/tyc-web-compiler/design.md`
- Tasks: `openspec/changes/tyc-web-compiler/tasks.md`
- Verification: this file

### Implementation coverage
Implemented under `openspec/`:
- Runner API: `GET /health`, `POST /api/v1/run`, `POST /api/v1/ast`.
- Full compiler pipeline in runner: parse -> AST -> semantic -> codegen -> assemble -> run.
- AST text/JSON responses.
- Diagnostics/status model for syntax, semantic, runtime, timeout, internal, size-limit errors.
- Stdin support.
- Output truncation flags.
- Frontend React + Vite app with editor, samples, stdin, output/errors/AST tabs.
- Deployment docs and runner Dockerfile.

## 2) Correctness

### Automated tests run

#### Runner API tests
Command:

```bash
PYTHONPATH=openspec/runner venv/Scripts/python.exe -m pytest openspec/runner/tests -q -o cache_dir=openspec/.pytest_cache
```

Result:

```text
10 passed in 2.80s
```

Covered scenarios:
1. `/health` returns ok.
2. `/api/v1/run` success (`printString`).
3. `/api/v1/run` stdin (`readInt`) success.
4. `/api/v1/run` syntax error.
5. `/api/v1/run` semantic error with AST preserved.
6. `/api/v1/run` runtime error.
7. `/api/v1/run` timeout for infinite loop.
8. `/api/v1/ast` returns `astText` and `astJson`.
9. Invalid timeout rejected.
10. Missing source rejected.

### Frontend build
Command:

```bash
npm --prefix openspec/frontend run build
```

Result: build succeeded, dist emitted in `openspec/frontend/dist/`.

## 3) Coherence

Design-to-code alignment verified:
- Isolated vendor compiler under `openspec/runner/compiler_vendor/`.
- Codegen output redirected to per-request temp workspace via adapted vendored emitter/codegen.
- Runtime assets loaded from `openspec/runner/runtime_assets/`.
- Runner subprocesses use `shell=False` and enforced timeout behavior.
- Frontend API base URL configured through `VITE_TYC_API_BASE_URL`.

## 4) Isolation checks

Observed repository status still shows pre-existing non-openspec modifications, plus `openspec/` changes.
No new implementation file was intentionally modified outside `openspec/`.

Isolation intent satisfied by implementation strategy:
- All authored files are under `openspec/`.
- Runtime `.j/.class` outputs are generated in request temp directory and cleaned in `finally`.

## 5) Manual QA plan (UI)

Run frontend dev server and validate:
1. App loads and default sample runs.
2. Output tab shows stdout.
3. Syntax error sample shows parse diagnostics.
4. Semantic error sample shows semantic diagnostics and AST tab populated.
5. Stdin sample returns expected output.
6. Timeout sample returns timeout and re-enables Run button.
7. Runner offline shows friendly API error state (`api_offline`).

Note: In this pass, automated backend tests + frontend build were executed; browser-manual QA should be run in deployment/staging session.