# GStack Variant Spec: TyC Web Compiler

## 1. Goal

Build the GStack-managed version of the TyC Web Compiler as a fully isolated webapp implementation under `gstack/`.

The webapp must let a public user:

1. Enter TyC source code in a browser.
2. Provide optional stdin for `readInt`, `readFloat`, and `readString`.
3. Run the compiler pipeline and execute the program.
4. See syntax, semantic, codegen, assembly, runtime, and timeout errors with a stable error shape.
5. See stdout when the program succeeds.
6. Display the AST generated from the same source code.
7. Deploy the frontend publicly on Vercel using React + Vite.

This variant exists to evaluate the GStack workflow. The implementation should intentionally produce planning, review, QA, and retrospective artifacts so the workflow can be compared against the GSD and OpenSpec variants.

## 2. Absolute isolation rule

This is the highest-priority implementation constraint for this variant.

- All files created, edited, deleted, moved, generated, configured, formatted, or tested for this variant must be inside `gstack/`.
- Do not modify anything outside `gstack/`, including root `src/`, `tests/`, `run.py`, `requirements.txt`, `CLAUDE.md`, `WEB_COMPILER_SPEC.md`, `.gitignore`, root lockfiles, root package files, root Docker/Vercel config, or any workflow artifacts outside `gstack/`.
- Reading files outside `gstack/` is allowed only to understand the existing TyC compiler behavior.
- Copying files from outside `gstack/` into `gstack/` is allowed only when the destination is inside `gstack/` and the copy is needed to keep the variant isolated.
- Generated ANTLR files, generated Jasmin files, `.class` files, lockfiles, reports, docs, and review artifacts for this variant must not appear outside `gstack/`.
- If a GStack command or agent suggests cross-repo cleanup, root config changes, or shared compiler edits, reject that scope unless the user explicitly approves it.
- If a change outside `gstack/` appears truly necessary, stop and ask the user before making that change.

## 3. Why Vercel needs a separate runner

The frontend should deploy on Vercel, but the compiler runner should not run directly inside Vercel serverless functions.

Reasons:

- The TyC compiler currently depends on Python, ANTLR-generated modules, Jasmin, and Java/JVM execution.
- The product runs user-submitted code, so it needs a sandboxed execution environment.
- Vercel serverless functions are not a good fit for arbitrary JVM subprocess execution with per-request isolation.
- Public execution requires CPU/memory/time limits, output truncation, and possibly network isolation.

Required architecture:

```text
Vercel
  gstack/frontend/ React + Vite app
  |
  | HTTPS JSON API
  v
External Docker-capable runner host
  gstack/runner/ FastAPI service
  |
  | per-request temp workspace
  v
Vendored/adapted TyC compiler + Jasmin + JVM
```

If the user later insists on Vercel-only deployment, the scope must be reduced to parse/AST/semantic checks only. This spec assumes full run support, so it requires an external runner.

## 4. Scope

### 4.1. In scope

- React + Vite + TypeScript frontend under `gstack/frontend/`.
- Monaco editor for TyC code.
- Optional stdin textarea.
- Output/Error/AST result panels.
- Sample programs.
- FastAPI runner under `gstack/runner/`.
- Production-shaped API contracts.
- AST text and JSON serialization.
- Dockerfile for runner.
- Deployment notes for Vercel frontend and Docker runner.
- Tests under `gstack/tests/` or colocated under `gstack/runner/tests/`.
- Public safety limits: source size, stdin size, timeout, output truncation, CORS allowlist, concurrency limit.
- GStack artifacts under `gstack/docs/`, including plan, architecture review, design review, security review, QA report, and retrospective.

### 4.2. Out of scope for v1

- Login/accounts.
- Saving user history.
- Share links.
- Multi-file TyC projects.
- Interactive debugger.
- Autocomplete based on compiler internals.
- Real-time collaboration.
- A production queue system.
- Full browser-based terminal.

## 5. Recommended isolated layout

```text
gstack/
  WEBAPP_SPEC.md
  WORKFLOW_AUTOMATION_PROMPT.md
  docs/
    design-doc.md
    architecture-review.md
    design-review.md
    devex-review.md
    qa-report.md
    security-review.md
    deployment.md
    retro.md
  frontend/
    package.json
    package-lock.json
    index.html
    vite.config.ts
    tsconfig.json
    src/
      main.tsx
      App.tsx
      api.ts
      types.ts
      samples.ts
      components/
        CodeEditor.tsx
        Toolbar.tsx
        StdinPanel.tsx
        ResultPanel.tsx
        OutputPanel.tsx
        ErrorsPanel.tsx
        AstPanel.tsx
  runner/
    Dockerfile
    requirements-web.txt
    app/
      __init__.py
      main.py
      schemas.py
      compiler_service.py
      ast_serializer.py
      limits.py
      runtime_workspace.py
    compiler_vendor/
      # copied/adapted compiler code if needed
    build/
      # ANTLR output generated for this variant only
    runtime_assets/
      jasmin.jar
      io.java
      io.class
  tests/
    test_runner_service.py
    test_runner_api.py
```

## 6. User flows

### 6.1. Successful program

Source:

```c
void main() {
    printString("Hello TyC");
}
```

Expected UI:

```text
Status: Success
Output:
Hello TyC
```

AST tab should show an AST tree or raw AST text.

### 6.2. Syntax error

Source:

```c
void main( {
}
```

Expected UI:

```text
Status: Syntax Error
Stage: parse
Message: Error on line 1 col ...
```

No output. AST may be empty because parsing failed.

### 6.3. Semantic error with AST retained

Source:

```c
void main() {
    int x = "abc";
}
```

Expected UI:

```text
Status: Semantic Error
Stage: semantic
Message: TypeMismatchInStatement(...)
```

AST tab should still show AST because parse and AST generation succeeded.

### 6.4. Program with stdin

Source:

```c
void main() {
    int x = readInt();
    printInt(x + 1);
}
```

Stdin:

```text
41
```

Expected output:

```text
42
```

### 6.5. Timeout

Source:

```c
void main() {
    while (1) {}
}
```

Expected UI:

```text
Status: Timeout
Stage: run
Message: Program exceeded 3 seconds.
```

Run button must be re-enabled after timeout.

### 6.6. Runtime error

If JVM execution exits non-zero, UI should show:

```text
Status: Runtime Error
Stage: run
Stderr:
<captured JVM stderr>
```

## 7. Frontend spec

### 7.1. Stack

- React.
- Vite.
- TypeScript.
- Monaco editor via `@monaco-editor/react`.
- CSS modules, plain CSS, or Tailwind are acceptable, but all config must live inside `gstack/frontend/`.

### 7.2. Environment variables

```text
VITE_TYC_API_BASE_URL=https://<gstack-runner-api-origin>
VITE_DEFAULT_TIMEOUT_SECONDS=3
```

Frontend should fail clearly at runtime if `VITE_TYC_API_BASE_URL` is missing in production mode.

### 7.3. Layout

```text
+----------------------------------------------------------------+
| TyC Web Compiler - GStack Variant                              |
| [Run] [Load Sample] [Clear]                                    |
+----------------------------------+-----------------------------+
| Code Editor                      | Result Panel                |
|                                  | Tabs: Output | Errors | AST |
| void main() {                    |                             |
|   printString("Hello TyC");     |                             |
| }                                |                             |
+----------------------------------+-----------------------------+
| Stdin textarea                                                 |
+----------------------------------------------------------------+
```

### 7.4. Components

- `CodeEditor`: Monaco editor, tab size 4, monospace, minimum height 400px.
- `Toolbar`: Run, Clear, Load Sample.
- `StdinPanel`: textarea for stdin.
- `ResultPanel`: owns tabs and displays current response.
- `OutputPanel`: stdout and duration.
- `ErrorsPanel`: diagnostics, stderr, stage statuses.
- `AstPanel`: expandable AST JSON tree; raw `astText` fallback.

### 7.5. UI states

- `idle`: no run yet.
- `running`: disable Run, show progress text.
- `success`: show green status badge and stdout.
- `error`: show red status badge and diagnostics.
- `timeout`: show timeout status and re-enable Run.
- `api_offline`: show friendly connection error.

### 7.6. Samples

Minimum samples:

```ts
export const samples = [
  {
    name: "Hello TyC",
    source: `void main() {\n    printString("Hello TyC");\n}`,
    stdin: ""
  },
  {
    name: "Read integer",
    source: `void main() {\n    int x = readInt();\n    printInt(x + 1);\n}`,
    stdin: "41\n"
  },
  {
    name: "Syntax error",
    source: `void main( {\n}`,
    stdin: ""
  },
  {
    name: "Semantic error",
    source: `void main() {\n    int x = "abc";\n}`,
    stdin: ""
  },
  {
    name: "Timeout",
    source: `void main() {\n    while (1) {}\n}`,
    stdin: ""
  }
];
```

## 8. Runner API spec

### 8.1. GET `/health`

Response:

```json
{
  "ok": true,
  "service": "tyc-runner-gstack",
  "version": "0.1.0"
}
```

### 8.2. POST `/api/v1/run`

Runs full pipeline: parse -> AST -> semantic check -> codegen -> assemble -> execute.

Request:

```json
{
  "source": "void main() { printString(\"Hello\"); }",
  "stdin": "",
  "timeoutSeconds": 3,
  "includeAst": true
}
```

Validation:

| Field | Type | Required | Rule |
| --- | ---: | ---: | --- |
| `source` | string | yes | 1 to 65536 bytes |
| `stdin` | string | no | default `""`, max 16384 bytes |
| `timeoutSeconds` | integer | no | min 1, max 5, default 3 |
| `includeAst` | boolean | no | default true |

Success response:

```json
{
  "ok": true,
  "status": "success",
  "stdout": "Hello",
  "stderr": "",
  "diagnostics": [],
  "astText": "Program([...])",
  "astJson": { "kind": "Program", "fields": {} },
  "stages": {
    "parse": "success",
    "ast": "success",
    "semantic": "success",
    "codegen": "success",
    "assemble": "success",
    "run": "success"
  },
  "durationMs": 742,
  "truncated": { "stdout": false, "stderr": false }
}
```

Error response:

```json
{
  "ok": false,
  "status": "semantic_error",
  "stdout": "",
  "stderr": "",
  "diagnostics": [
    {
      "stage": "semantic",
      "severity": "error",
      "message": "TypeMismatchInStatement(...)" ,
      "line": null,
      "column": null,
      "raw": "TypeMismatchInStatement(...)"
    }
  ],
  "astText": "Program([...])",
  "astJson": { "kind": "Program", "fields": {} },
  "stages": {
    "parse": "success",
    "ast": "success",
    "semantic": "failed",
    "codegen": "skipped",
    "assemble": "skipped",
    "run": "skipped"
  },
  "durationMs": 31,
  "truncated": { "stdout": false, "stderr": false }
}
```

### 8.3. POST `/api/v1/ast`

Parses and generates AST only. Does not semantic-check or execute.

Request:

```json
{
  "source": "void main() {}"
}
```

Response:

```json
{
  "ok": true,
  "status": "success",
  "diagnostics": [],
  "astText": "Program([FuncDecl(VoidType(), main, [], BlockStmt([]))])",
  "astJson": {
    "kind": "Program",
    "fields": {
      "decls": [
        {
          "kind": "FuncDecl",
          "fields": {
            "return_type": { "kind": "VoidType", "fields": {} },
            "name": "main",
            "params": [],
            "body": { "kind": "BlockStmt", "fields": { "statements": [] } }
          }
        }
      ]
    }
  },
  "durationMs": 10
}
```

## 9. Status and diagnostic contract

### 9.1. Statuses

| Status | Meaning |
| --- | --- |
| `success` | requested operation completed |
| `lexical_error` | lexer raised `ErrorToken`, `UncloseString`, or `IllegalEscape` |
| `syntax_error` | parser listener raised syntax error |
| `ast_error` | AST generation failed |
| `semantic_error` | static checker failed |
| `codegen_error` | code generation failed |
| `assembly_error` | Jasmin assembly failed |
| `runtime_error` | JVM execution returned non-zero |
| `timeout` | compile/run exceeded timeout |
| `input_too_large` | source/stdin exceeds limit |
| `internal_error` | unexpected backend error |

### 9.2. Diagnostic object

```ts
type Diagnostic = {
  stage: "lex" | "parse" | "ast" | "semantic" | "codegen" | "assemble" | "run" | "internal";
  severity: "error" | "warning";
  message: string;
  line: number | null;
  column: number | null;
  raw: string;
};
```

Line and column are required when the parser error string exposes them. Otherwise they may be `null`.

## 10. Compiler service pipeline

### 10.1. Service function

```python
def run_tyc_program(
    source: str,
    stdin: str = "",
    timeout_seconds: int = 3,
    include_ast: bool = True,
) -> RunResult:
    ...
```

### 10.2. Parse stage

Use ANTLR generated lexer/parser copied or generated inside `gstack/runner/`.

Pseudo-flow:

```python
input_stream = InputStream(source)
lexer = TyCLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = TyCParser(token_stream)
parser.removeErrorListeners()
parser.addErrorListener(NewErrorListener.INSTANCE)
parse_tree = parser.program()
```

Return `lexical_error` for custom lexer exceptions and `syntax_error` for parser listener exceptions.

### 10.3. AST stage

```python
ast = ASTGeneration().visit(parse_tree)
```

If `includeAst` is true, return both `astText = str(ast)` and `astJson = serialize_ast(ast)`.

### 10.4. Semantic stage

```python
StaticChecker().check_program(ast)
```

Public run must perform semantic checking before codegen. If semantic checking fails, return `semantic_error` and preserve AST in the response.

### 10.5. Codegen stage

Codegen must write only inside a per-request temp workspace. Do not allow root `src/runtime/` writes.

Preferred implementation for this isolated variant:

- Copy/adapt codegen into `gstack/runner/compiler_vendor/`.
- Modify the copied `Emitter` to accept `output_dir`.
- Modify the copied `CodeGenerator` to pass that output directory.
- Keep the root compiler unchanged.

### 10.6. Runtime workspace stage

For each request:

1. Create temp directory.
2. Copy `jasmin.jar` and `io.class` from `gstack/runner/runtime_assets/`.
3. Generate `TyC.j` into temp directory.
4. Run Jasmin in temp directory.
5. Run JVM class in temp directory.
6. Delete temp directory in `finally`.

### 10.7. Jasmin assembly

```python
subprocess.run(
    ["java", "-jar", "jasmin.jar", "TyC.j"],
    cwd=temp_dir,
    capture_output=True,
    text=True,
    timeout=timeout_seconds,
)
```

### 10.8. JVM execution

```python
subprocess.run(
    ["java", "-cp", temp_dir, "TyC"],
    input=stdin,
    cwd=temp_dir,
    capture_output=True,
    text=True,
    timeout=timeout_seconds,
)
```

## 11. AST serialization

`astText` is `str(ast)`.

`astJson` recursively serializes AST nodes:

```python
def serialize_ast(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [serialize_ast(item) for item in value]
    if isinstance(value, ASTNode):
        fields = {
            key: serialize_ast(val)
            for key, val in value.__dict__.items()
            if not key.startswith("_")
        }
        return {"kind": value.__class__.__name__, "fields": fields}
    return str(value)
```

Frontend should render `astJson` as an expandable tree and provide `astText` as fallback.

## 12. Public security requirements

### 12.1. Limits

| Limit | Value |
| --- | ---: |
| Source size | 64 KB |
| Stdin size | 16 KB |
| Timeout | default 3s, max 5s |
| Stdout returned | 32 KB max |
| Stderr returned | 32 KB max |
| Concurrent runs per runner | configurable, default 2 |

### 12.2. Process safety

- Use `subprocess.run([...], shell=False)`.
- Always set timeouts.
- Always run in a temp directory.
- Always cleanup.
- Do not allow user-supplied filenames.
- Do not expose internal filesystem paths in user-facing messages.

### 12.3. Container safety

- Runner Docker image should run as non-root.
- Deployment should set CPU and memory limits.
- Network access for user-executed code should be disabled if platform supports it.
- No host directory should be mounted writable.

### 12.4. API safety

- CORS allowlist must use the deployed Vercel origin.
- Add rate limiting before public launch.
- Add concurrency limit before public launch.
- Log request ID, stage, status, and duration; do not log full source by default.

## 13. Deployment spec

### 13.1. Frontend on Vercel

If deploying from `gstack/frontend/`:

```text
Framework Preset: Vite
Root Directory: gstack/frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm ci
```

### 13.2. Runner Dockerfile outline

```dockerfile
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY gstack/runner/requirements-web.txt ./requirements-web.txt
RUN pip install --no-cache-dir -r requirements-web.txt
COPY gstack/runner ./runner

RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "runner.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Actual Dockerfile must remain under `gstack/runner/Dockerfile`.

### 13.3. Runner environment variables

```text
TYC_ALLOWED_ORIGINS=https://<gstack-vercel-origin>
TYC_DEFAULT_TIMEOUT_SECONDS=3
TYC_MAX_TIMEOUT_SECONDS=5
TYC_MAX_SOURCE_BYTES=65536
TYC_MAX_STDIN_BYTES=16384
TYC_MAX_OUTPUT_BYTES=32768
TYC_MAX_CONCURRENT_RUNS=2
```

## 14. Test plan

### 14.1. Backend service tests

Required tests:

1. Valid `printString` program returns `success` and stdout.
2. Valid `printInt` program returns stdout.
3. `readInt` with stdin returns correct output.
4. Syntax error returns `syntax_error`.
5. Semantic error returns `semantic_error` and includes AST.
6. Infinite loop returns `timeout`.
7. Oversized source is rejected.
8. Sequential runs do not leak generated files.
9. No generated files appear outside `gstack/`.

### 14.2. API tests

Required tests:

1. `GET /health` returns ok.
2. `POST /api/v1/run` success.
3. `POST /api/v1/run` syntax error.
4. `POST /api/v1/run` semantic error.
5. `POST /api/v1/ast` returns `astText` and `astJson`.
6. Invalid timeout rejected.
7. Missing source rejected.

### 14.3. Frontend/manual tests

Required manual checks:

1. App loads.
2. Default sample runs.
3. Output tab displays stdout.
4. Errors tab displays syntax error.
5. Errors tab displays semantic error.
6. AST tab displays AST for parseable source.
7. Stdin sample works.
8. Timeout sample returns timeout.
9. API offline state is user-friendly.

## 15. GStack workflow mapping

GStack should be used as a staged, role-reviewed process. All artifacts must stay inside `gstack/docs/` or other `gstack/` subfolders.

### 15.1. Think

Expected artifact: `gstack/docs/design-doc.md`.

The Think stage should clarify:

- primary user: student/demo user running TyC code in browser
- key risk: public execution of untrusted code
- key architecture constraint: Vercel frontend plus external Docker runner
- key comparison goal: evaluate GStack workflow quality and friction

### 15.2. Plan

Expected artifacts:

- `gstack/docs/architecture-review.md`
- `gstack/docs/design-review.md`
- `gstack/docs/devex-review.md`

Planning reviews should cover:

- product scope and non-goals
- backend API contract
- isolated compiler integration strategy
- UI layout and AST display
- deployment model
- tests and QA plan

### 15.3. Build

Implementation should proceed in this order:

1. runner schemas and health endpoint
2. compiler service with parse/AST/semantic stages
3. temp workspace and codegen/run stages
4. AST serializer
5. frontend API client and UI components
6. deployment docs/config under `gstack/`
7. tests

### 15.4. Review

Expected artifacts:

- `gstack/docs/security-review.md`
- optional code review notes in `gstack/docs/review.md`

Review must check:

- no writes outside `gstack/`
- no `shell=True`
- timeouts exist
- temp workspace cleanup exists
- stdout/stderr truncation exists
- CORS is configurable
- frontend handles API errors

### 15.5. Test and QA

Expected artifact: `gstack/docs/qa-report.md`.

QA must include:

- success sample
- syntax error sample
- semantic error sample
- stdin sample
- timeout sample
- AST display
- offline runner behavior

### 15.6. Ship

Expected artifact: `gstack/docs/deployment.md`.

Ship prep should include:

- Vercel settings
- runner Docker build/run commands
- required environment variables
- known limitations

Do not push, create PR, or deploy unless the user explicitly asks.

### 15.7. Reflect

Expected artifact: `gstack/docs/retro.md`.

Retrospective should compare:

- workflow clarity
- amount of useful review output
- implementation friction
- defect prevention
- overhead compared to GSD and OpenSpec

## 16. Acceptance criteria

- All files for this variant are inside `gstack/`.
- No file outside `gstack/` is modified.
- Frontend builds with Vite.
- Runner exposes `/health`, `/api/v1/run`, and `/api/v1/ast`.
- Valid TyC source displays stdout.
- Syntax errors display `syntax_error`.
- Semantic errors display `semantic_error` and preserve AST when available.
- Runtime errors display `runtime_error`.
- Infinite loop sample returns `timeout`.
- AST tab displays AST tree or raw AST for parseable source.
- Backend tests cover success, syntax error, semantic error, AST, stdin, and timeout.
- GStack docs exist under `gstack/docs/`.
- Final retrospective compares GStack workflow strengths and weaknesses for this task.
