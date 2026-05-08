# QA Report

## Scope
- Variant under test: `gstack/` only.
- Runner endpoint: `http://127.0.0.1:8000`.
- Frontend dev endpoint: `http://127.0.0.1:5173`.

## Automated test results

### Backend tests
Command:
```bash
PYTHONPATH=gstack venv/Scripts/python.exe -m pytest gstack/tests -q
```
Result:
- `22 passed in 2.58s`

### Frontend unit tests
Command:
```bash
npm --prefix gstack/frontend run test -- --run
```
Result:
- `1 passed` test file
- `6 passed` tests

### Frontend production build
Command:
```bash
npm --prefix gstack/frontend run build
```
Result:
- Build success
- Bundle generated in `gstack/frontend/dist`

## API contract probes (manual script)

### 1) Health
- Request: `GET /health`
- Result: `200` with `{"ok": true, "service": "tyc-runner-gstack", "version": "0.1.0"}`

### 2) Run success
- Source: `printString("Hello TyC")`
- Result: `status=success`, `stdout=Hello TyC`, AST present when `includeAst=true`

### 3) Run syntax error
- Source: `void main( { }`
- Result: `status=syntax_error`, diagnostics present, parse-stage failure

### 4) Run semantic error
- Source: `int x = "abc";`
- Result: `status=semantic_error`, diagnostics present, AST preserved (`astText` + `astJson`)

### 5) Run with stdin
- Source: readInt + printInt
- Stdin: `41`
- Result: `status=success`, `stdout=42`

### 6) Run timeout
- Source: `while (1) {}`
- Result: `status=timeout`, request returned normally with timeout diagnostic

### 7) AST endpoint
- Request: `POST /api/v1/ast`
- Result: `status=success`, `astText` and `astJson` returned

## Regression note
- During QA, timeout case was initially reproduced as hanging request.
- Root cause was in runtime subprocess handling.
- After fix in `gstack/runner/app/runtime_workspace.py`, timeout response is stable.

## Remaining manual browser checks
- API contract and backend behavior are verified.
- If strict visual/browser evidence is required for submission, run one interactive pass in browser for each sample (`Hello`, `Syntax error`, `Semantic error`, `Read integer`, `Timeout`) and capture screenshots.
