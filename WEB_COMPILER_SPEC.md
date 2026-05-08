# TyC Web Compiler Specification

## 1. Mục tiêu

Xây dựng một web app public cho compiler TyC để người dùng có thể:

1. Nhập source code TyC trên trình duyệt.
2. Bấm chạy để compile và execute chương trình.
3. Xem lỗi theo từng giai đoạn nếu có:
   - lexical error
   - syntax error
   - AST generation error
   - semantic error
   - code generation error
   - Jasmin assembly error
   - JVM runtime error
   - timeout
4. Nếu không có lỗi, xem output của chương trình.
5. Xem cây AST được sinh ra từ source code.
6. Deploy frontend public lên Vercel bằng React + Vite.

Compiler hiện tại là Python + ANTLR4 + Jasmin/JVM, nên không rewrite compiler sang JavaScript trong bản đầu.

## 2. Quyết định kiến trúc quan trọng

### 2.1. Vercel chỉ host frontend

Vercel phù hợp để host React + Vite frontend, nhưng không phù hợp để trực tiếp chạy toàn bộ compiler/runtime hiện tại vì:

- Codegen hiện tại cần Java/JVM để chạy Jasmin và execute `TyC.class`.
- Public web app sẽ chạy code do người dùng nhập, cần sandbox bằng container hoặc môi trường cô lập.
- Vercel Serverless Functions không cung cấp Docker sandbox tùy ý cho từng request và không nên dùng để chạy untrusted code lâu dài.
- File system của serverless là ephemeral, không phù hợp với flow hiện tại nếu vẫn ghi shared `.j` / `.class`.

Vì vậy kiến trúc bắt buộc cho requirement “deploy public + chạy chương trình” là:

```text
Vercel
  React + Vite frontend
  |
  | HTTPS JSON API
  v
External TyC Runner API
  Python FastAPI service trong Docker sandbox-capable host
  |
  | per-request temp workspace
  v
TyC compiler + Jasmin + JVM
```

Nếu bắt buộc “Vercel-only”, hệ thống chỉ nên hỗ trợ parse / AST / semantic check, không nên hỗ trợ run JVM. Vì yêu cầu hiện tại cần runtime output và runtime error, spec này dùng mô hình Vercel frontend + external runner backend.

### 2.2. Runner backend phải containerized

TyC Runner API nên deploy lên một platform hỗ trợ Docker container và Java runtime, ví dụ một service container bất kỳ có thể chạy Python + Java. Vercel frontend gọi service này qua HTTPS.

Runner backend không nên chạy trực tiếp trên host không giới hạn tài nguyên nếu public.

## 3. Phạm vi bản đầu

### Trong scope

- React + Vite frontend deploy lên Vercel.
- Code editor cho TyC source.
- Nút Run để compile + run.
- Nút hoặc tab AST để xem cây AST.
- Output panel hiển thị stdout nếu success.
- Error panel hiển thị lỗi syntax / semantic / runtime / timeout.
- Optional stdin textarea cho `readInt`, `readFloat`, `readString`.
- FastAPI runner backend.
- Tách compiler pipeline production khỏi `tests/utils.py`.
- Chạy codegen trong temp directory riêng cho từng request.
- Dockerfile cho runner backend.
- Timeout, source size limit, stdout/stderr truncation, cleanup temp files.

### Ngoài scope bản đầu

- User account / login.
- Lưu lịch sử code.
- Share link.
- Multi-file TyC project.
- Debugger step-by-step.
- Semantic autocomplete.
- Real-time collaborative editing.
- Queue job phức tạp.

## 4. User flows

### 4.1. Run chương trình hợp lệ

Input source:

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

AST tab hiển thị AST tương ứng.

### 4.2. Syntax error

Input source:

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

Output rỗng. AST rỗng vì parse thất bại.

### 4.3. Semantic error

Input source:

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

AST tab vẫn hiển thị AST vì parse và AST generation đã thành công.

### 4.4. Runtime error

Nếu generated JVM program trả non-zero exit code hoặc JVM stderr có exception, UI hiển thị:

```text
Status: Runtime Error
Stage: run
Stderr:
<jvm stderr>
```

### 4.5. Timeout

Input source:

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

### 4.6. Chương trình có stdin

Assumption: bản đầu hỗ trợ stdin vì runtime hiện có `readInt`, `readFloat`, `readString`.

Input source:

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

Nếu sau này không muốn hỗ trợ stdin, frontend có thể ẩn stdin textarea và backend dùng `stdin = ""`.

## 5. Frontend spec

### 5.1. Stack

- React.
- Vite.
- TypeScript.
- Monaco editor via `@monaco-editor/react`.
- CSS thường hoặc Tailwind đều được, nhưng bản đầu không bắt buộc Tailwind.

### 5.2. Suggested folder structure

```text
web/frontend/
  package.json
  index.html
  vite.config.ts
  src/
    main.tsx
    App.tsx
    api.ts
    types.ts
    samples.ts
    components/
      CodeEditor.tsx
      StdinPanel.tsx
      Toolbar.tsx
      ResultPanel.tsx
      AstPanel.tsx
      DiagnosticsPanel.tsx
```

### 5.3. Environment variables trên Vercel

```text
VITE_TYC_API_BASE_URL=https://<runner-api-origin>
VITE_DEFAULT_TIMEOUT_SECONDS=3
```

`VITE_TYC_API_BASE_URL` trỏ tới external TyC Runner API.

### 5.4. Vercel build settings

Nếu frontend nằm trong `web/frontend/`:

```text
Framework Preset: Vite
Root Directory: web/frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm ci
```

Nếu deploy từ repo root, có thể dùng `vercel.json` ở root:

```json
{
  "buildCommand": "cd web/frontend && npm ci && npm run build",
  "outputDirectory": "web/frontend/dist",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Nếu muốn frontend gọi API cùng origin, có thể thêm Vercel rewrite/proxy tới runner API sau khi có domain thật. Bản đầu đơn giản hơn: frontend gọi trực tiếp `VITE_TYC_API_BASE_URL` và runner bật CORS đúng origin Vercel.

### 5.5. Layout UI

```text
+--------------------------------------------------------------+
| TyC Web Compiler                                             |
| [Run] [Show AST] [Clear] [Load Sample]                       |
+--------------------------------+-----------------------------+
| Code Editor                    | Result Panel                |
|                                | Tabs: Output | Errors | AST |
| void main() {                  |                             |
|   printString("Hello TyC");   | Output: Hello TyC           |
| }                              |                             |
+--------------------------------+-----------------------------+
| Stdin textarea                                               |
+--------------------------------------------------------------+
```

### 5.6. Required UI states

- `idle`: chưa chạy.
- `running`: disable Run button, show spinner/text `Compiling and running...`.
- `success`: show stdout and duration.
- `error`: show status badge, diagnostic message, stage, stderr if any.
- `timeout`: show timeout message.

### 5.7. Result panel behavior

Tabs:

1. `Output`
   - Hiển thị stdout nếu success.
   - Nếu stdout rỗng, hiển thị `(no output)`.
2. `Errors`
   - Hiển thị diagnostics theo stage.
   - Nếu không lỗi, hiển thị `(no errors)`.
3. `AST`
   - Hiển thị tree view nếu backend trả `astJson`.
   - Hiển thị raw AST text nếu tree view chưa implement.

### 5.8. Sample programs

Frontend nên có ít nhất các sample:

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
    name: "Semantic error",
    source: `void main() {\n    int x = "abc";\n}`,
    stdin: ""
  }
];
```

## 6. Backend runner API spec

### 6.1. Stack

- Python 3.12.
- FastAPI.
- Pydantic.
- Uvicorn.
- Java JDK/JRE available in container.
- Existing ANTLR generated Python parser in `build/`.
- Existing Jasmin runtime assets from `src/runtime/`.

### 6.2. Suggested folder structure

```text
web/runner/
  Dockerfile
  requirements-web.txt
  app/
    __init__.py
    main.py
    schemas.py
    compiler_service.py
    ast_serializer.py
    limits.py
```

`compiler_service.py` must not import from `tests/utils.py`; it should use compiler modules directly.

### 6.3. Required endpoints

#### GET `/health`

Used by deployment platform health checks.

Response:

```json
{
  "ok": true,
  "service": "tyc-runner",
  "version": "0.1.0"
}
```

#### POST `/api/v1/run`

Full pipeline: parse -> AST -> semantic check -> codegen -> assemble -> run.

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
|---|---:|---:|---|
| `source` | string | yes | 1 byte to 65536 bytes |
| `stdin` | string | no | default `""`, max 16384 bytes |
| `timeoutSeconds` | number | no | integer, min 1, max 5, default 3 |
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
  "astJson": {
    "kind": "Program",
    "fields": {
      "decls": []
    }
  },
  "stages": {
    "parse": "success",
    "ast": "success",
    "semantic": "success",
    "codegen": "success",
    "assemble": "success",
    "run": "success"
  },
  "durationMs": 742,
  "truncated": {
    "stdout": false,
    "stderr": false
  }
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
      "message": "TypeMismatchInStatement(...)\n",
      "line": null,
      "column": null,
      "raw": "TypeMismatchInStatement(...)"
    }
  ],
  "astText": "Program([...])",
  "astJson": {
    "kind": "Program",
    "fields": {}
  },
  "stages": {
    "parse": "success",
    "ast": "success",
    "semantic": "failed",
    "codegen": "skipped",
    "assemble": "skipped",
    "run": "skipped"
  },
  "durationMs": 31,
  "truncated": {
    "stdout": false,
    "stderr": false
  }
}
```

#### POST `/api/v1/ast`

Parse source and return AST only. This endpoint does not semantic check or run code.

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

### 6.4. Status taxonomy

| Status | Meaning |
|---|---|
| `success` | Full requested operation completed |
| `lexical_error` | Lexer raised `ErrorToken`, `UncloseString`, or `IllegalEscape` |
| `syntax_error` | Parser error listener raised syntax exception |
| `ast_error` | ASTGeneration failed |
| `semantic_error` | StaticChecker raised `StaticError` |
| `codegen_error` | CodeGenerator or Emitter failed |
| `assembly_error` | Jasmin failed to assemble `.j` into `.class` |
| `runtime_error` | JVM returned non-zero or produced runtime exception |
| `timeout` | Compile/run exceeded configured timeout |
| `input_too_large` | Source or stdin exceeded public limits |
| `internal_error` | Unexpected backend error |

### 6.5. Diagnostic object

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

Line/column are required only when available. Parser errors from `NewErrorListener` should be parsed into line/column when possible.

## 7. Compiler service pipeline

### 7.1. Public service function

```python
def run_tyc_program(
    source: str,
    stdin: str = "",
    timeout_seconds: int = 3,
    include_ast: bool = True,
) -> RunResult:
    ...
```

### 7.2. Pipeline stages

#### Stage 1: Lex + parse

Implementation should use:

- `antlr4.InputStream`
- generated `build.TyCLexer`
- generated `build.TyCParser`
- `antlr4.CommonTokenStream`
- `src.utils.error_listener.NewErrorListener`

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

If lexer raises one of the custom lexer errors, return `lexical_error`.
If parser listener raises syntax exception, return `syntax_error`.

#### Stage 2: AST generation

```python
ast = ASTGeneration().visit(parse_tree)
```

If this succeeds and `includeAst = true`, backend should return both:

- `astText = str(ast)`
- `astJson = serialize_ast(ast)`

If AST generation fails, return `ast_error`.

#### Stage 3: Semantic checking

```python
StaticChecker().check_program(ast)
```

If this fails with any error from `src/semantics/static_error.py`, return `semantic_error` and keep `astText` / `astJson` in response.

Web run must perform semantic checking before codegen. Existing codegen tests may skip checker, but public run must not.

#### Stage 4: Code generation

Generate Jasmin into a per-request temp directory, not into shared `src/runtime/`.

Required codebase change:

```python
class Emitter:
    def __init__(self, filename: str, output_dir: str | None = None):
        if output_dir is None:
            self.filepath = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "runtime", filename
            )
        else:
            self.filepath = os.path.join(output_dir, filename)
```

And:

```python
class CodeGenerator(BaseVisitor):
    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir
        ...

    def visit_program(self, node: Program, o=None):
        self.emit = Emitter(f"{self.class_name}.j", output_dir=self.output_dir)
        ...
```

Backward compatibility: if `output_dir` is omitted, current tests should keep working.

#### Stage 5: Runtime workspace setup

For each request:

1. Create a temp directory.
2. Copy `src/runtime/jasmin.jar` into temp directory.
3. Copy `src/runtime/io.class` into temp directory.
4. If `io.class` does not exist at startup, compile `src/runtime/io.java` once.
5. Run codegen with `output_dir = temp_dir`.
6. Assemble `TyC.j` inside temp directory.
7. Run `TyC.class` from temp directory.
8. Delete temp directory in `finally`.

No request should write `TyC.j`, `TyC.class`, or other generated files into shared `src/runtime/`.

#### Stage 6: Assemble Jasmin

Use subprocess with argument array, not `shell=True`.

```python
subprocess.run(
    ["java", "-jar", "jasmin.jar", "TyC.j"],
    cwd=temp_dir,
    capture_output=True,
    text=True,
    timeout=timeout_seconds,
)
```

If return code is non-zero, return `assembly_error`.

#### Stage 7: Run JVM program

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

If timeout, return `timeout`.
If return code is non-zero, return `runtime_error`.
Otherwise return `success` with stdout.

## 8. AST serialization spec

### 8.1. Text AST

`astText` is `str(ast)`. This is enough for the first UI version.

### 8.2. JSON AST

Backend should recursively serialize AST nodes into:

```json
{
  "kind": "NodeClassName",
  "fields": {
    "fieldName": "value"
  }
}
```

Rules:

- If value is an AST node, serialize recursively.
- If value is a list, serialize each item.
- If value is `None`, return `null`.
- If value is `str`, `int`, or `float`, return as-is.
- If value is a type node such as `IntType`, return `{ "kind": "IntType", "fields": {} }`.
- Do not include private fields beginning with `_`.

Pseudo-code:

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

Frontend can render `astJson` as an expandable tree and keep `astText` as raw fallback.

## 9. Public security requirements

Because this is public and runs user-provided code, these are required, not optional.

### 9.1. Request limits

| Limit | Value |
|---|---:|
| Source size | 64 KB |
| Stdin size | 16 KB |
| Timeout per compile step | 3s default, 5s max |
| Stdout returned | 32 KB max, then truncate |
| Stderr returned | 32 KB max, then truncate |
| Concurrent requests per runner instance | configurable, default low |

### 9.2. Process safety

- Use `subprocess.run([...], shell=False)` only.
- Always set timeout for Jasmin and JVM subprocesses.
- Always run in a request-specific temp directory.
- Always cleanup temp directory in `finally`.
- Do not expose filesystem paths in public error messages except controlled stage names.
- Do not allow user-supplied filenames or command arguments.

### 9.3. Container safety

Runner container should:

- Run as non-root user.
- Use memory limit in deployment platform.
- Use CPU limit in deployment platform.
- Disable outbound network for execution if platform supports it.
- Avoid mounting host directories writable into the runner.
- Keep temp workspace under `/tmp` or another isolated runtime path.

### 9.4. API protection

- CORS allow only the Vercel frontend origin in production.
- Add rate limit by IP.
- Add simple concurrency limit to prevent too many JVM processes.
- Return generic `internal_error` for unexpected exceptions.
- Log request ID, status, duration, and stage, but do not log full source code by default.

## 10. Deployment spec

### 10.1. Runner Dockerfile requirements

Runner image must include:

- Python 3.12.
- Java JDK or JRE plus `javac` if `io.java` is compiled during build/startup.
- Python dependencies from `requirements.txt` plus web dependencies.
- Generated ANTLR parser in `build/`.
- Runtime assets `src/runtime/io.class` and `src/runtime/jasmin.jar`.

Suggested Dockerfile outline:

```dockerfile
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY web/runner/requirements-web.txt ./web-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web-requirements.txt

COPY . .

RUN python run.py build
RUN javac src/runtime/io.java

RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "web.runner.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

If `python run.py build` needs `external/antlr-4.13.2-complete.jar`, ensure that jar exists in the image before build. Either keep it in repo or download it during image build.

### 10.2. Runner environment variables

```text
TYC_ALLOWED_ORIGINS=https://<vercel-frontend-origin>
TYC_DEFAULT_TIMEOUT_SECONDS=3
TYC_MAX_TIMEOUT_SECONDS=5
TYC_MAX_SOURCE_BYTES=65536
TYC_MAX_STDIN_BYTES=16384
TYC_MAX_OUTPUT_BYTES=32768
TYC_MAX_CONCURRENT_RUNS=2
```

### 10.3. Frontend deployment on Vercel

Vercel env:

```text
VITE_TYC_API_BASE_URL=https://<runner-api-origin>
VITE_DEFAULT_TIMEOUT_SECONDS=3
```

Frontend build must fail if required env var is missing in production.

## 11. Required codebase changes

### 11.1. Add web frontend

Add `web/frontend/` React + Vite app.

Minimum dependencies:

```json
{
  "dependencies": {
    "@monaco-editor/react": "latest",
    "react": "latest",
    "react-dom": "latest"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "latest",
    "typescript": "latest",
    "vite": "latest"
  }
}
```

### 11.2. Add runner backend

Add `web/runner/` FastAPI app.

`requirements-web.txt`:

```text
fastapi
uvicorn[standard]
pydantic
```

### 11.3. Modify codegen output handling

Update:

- `src/codegen/emitter.py`
- `src/codegen/codegen.py`

Goal: allow per-request output directory while preserving old behavior for tests.

### 11.4. Add compiler service

Create production service module, for example:

```text
web/runner/app/compiler_service.py
```

This service should import directly from:

- `build.TyCLexer`
- `build.TyCParser`
- `src.astgen.ast_generation.ASTGeneration`
- `src.semantics.static_checker.StaticChecker`
- `src.codegen.codegen.CodeGenerator`

Do not import from `tests.utils`.

### 11.5. Add AST serializer

Create:

```text
web/runner/app/ast_serializer.py
```

Return `astText` and `astJson`.

## 12. Test plan

### 12.1. Backend unit tests

Create `tests/test_web_compiler_service.py`.

Required cases:

1. Valid program prints string.
2. Valid program prints int.
3. Valid program with stdin using `readInt`.
4. Syntax error returns `syntax_error`.
5. Semantic error returns `semantic_error` and includes AST.
6. Infinite loop returns `timeout`.
7. Runtime/Jasmin failure returns structured error instead of crashing API.
8. Oversized source returns `input_too_large` or HTTP 413.
9. Generated files are written only to temp directory, not shared `src/runtime/`.
10. Sequential runs do not leak previous output/classes.

### 12.2. Backend API tests

Create `tests/test_web_api.py` using FastAPI TestClient.

Required cases:

1. `GET /health` returns ok.
2. `POST /api/v1/run` valid source returns success.
3. `POST /api/v1/run` syntax error returns `ok=false`.
4. `POST /api/v1/run` semantic error returns `ok=false`.
5. `POST /api/v1/ast` returns `astText` and `astJson`.
6. Invalid timeout is rejected.
7. Missing source is rejected.

### 12.3. Frontend tests

Minimum manual tests:

1. App loads on Vercel preview URL.
2. Default sample runs successfully.
3. Syntax error sample displays error stage and message.
4. Semantic error sample displays semantic error.
5. AST tab shows AST after valid source.
6. Stdin sample works.
7. Infinite loop returns timeout and Run button is re-enabled.
8. API offline state shows friendly message.

Optional automated tests:

- Vitest for API client mapping.
- Playwright for main UI flow.

## 13. Acceptance criteria

The feature is complete when:

1. React + Vite frontend is deployable to Vercel.
2. Frontend can call public runner API through `VITE_TYC_API_BASE_URL`.
3. User can enter TyC code and run it.
4. Valid code displays stdout.
5. Syntax errors are displayed with `syntax_error` status.
6. Semantic errors are displayed with `semantic_error` status.
7. Runtime/JVM errors are displayed with `runtime_error` status.
8. Infinite loops or long-running programs are stopped by timeout.
9. AST is visible for source code that parses successfully.
10. Runner does not write request-generated `.j` / `.class` into shared `src/runtime/`.
11. Runner has request size limits, timeout, temp workspace cleanup, and production CORS.
12. Backend tests cover success, syntax error, semantic error, AST, stdin, and timeout.

## 14. Implementation milestones

### Milestone 1: Runner service foundation

- Add FastAPI app.
- Add schemas.
- Add `/health`.
- Add validation limits.
- Add unit test skeleton.

### Milestone 2: Compiler pipeline wrapper

- Implement parse stage.
- Implement AST stage.
- Implement semantic stage.
- Implement structured diagnostics.
- Implement `/api/v1/ast`.

### Milestone 3: Safe codegen/run workspace

- Modify `Emitter` to support `output_dir`.
- Modify `CodeGenerator` to support `output_dir`.
- Implement temp workspace.
- Copy runtime assets.
- Assemble and run with subprocess timeout.
- Cleanup temp files.

### Milestone 4: React + Vite frontend

- Create frontend app.
- Add Monaco editor.
- Add Run button.
- Add stdin textarea.
- Add Output / Errors / AST tabs.
- Add samples.
- Wire API client to runner.

### Milestone 5: Public deployment

- Add runner Dockerfile.
- Deploy runner on Docker-capable host.
- Configure CORS with Vercel frontend origin.
- Deploy frontend on Vercel.
- Configure Vercel env vars.
- Run manual acceptance tests.

### Milestone 6: Hardening

- Add rate limiting.
- Add concurrency limit.
- Add output truncation.
- Ensure logs avoid full source by default.
- Add API offline/error handling in frontend.

## 15. Open questions

1. Bạn có muốn stdin textarea hiển thị mặc định không? Spec hiện đang assume “có” vì TyC có `readInt`, `readFloat`, `readString`.
2. Bạn đã chọn platform nào cho external runner backend chưa? Nếu chưa, implementation nên giữ Dockerfile generic để deploy được trên nhiều host.
