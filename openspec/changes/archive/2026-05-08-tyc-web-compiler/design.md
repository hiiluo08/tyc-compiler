# Design: tyc-web-compiler

## 1. Architecture overview

```text
openspec/frontend (React + Vite)
  -> calls runner JSON API over HTTPS
openspec/runner (FastAPI)
  -> parse/AST/semantic/codegen/assemble/run pipeline
  -> per-request temp workspace for generated artifacts
```

Planned layout:
- `openspec/frontend/`: web UI, API client, samples, result tabs.
- `openspec/runner/app/`: FastAPI app, schemas, compiler service, AST serializer, limits, workspace helpers.
- `openspec/runner/compiler_vendor/`: copied/adapted compiler + ANTLR artifacts required for isolated execution.
- `openspec/runner/runtime_assets/`: `jasmin.jar`, `io.java`, `io.class`.
- `openspec/runner/tests/`: API/service tests.
- `openspec/docs/`: deployment + QA notes.

## 2. API design

### GET `/health`
Response:
- `ok: true`
- `service: "tyc-runner-openspec"`
- `version: "0.1.0"`

### POST `/api/v1/run`
Request:
- `source: string`
- `stdin?: string` (default `""`)
- `timeoutSeconds?: int` (default from env)
- `includeAst?: bool` (default `true`)

Response:
- `ok: bool`
- `status: success | lexical_error | syntax_error | ast_error | semantic_error | codegen_error | assembly_error | runtime_error | timeout | input_too_large | internal_error`
- `stdout: string`
- `stderr: string`
- `diagnostics: Diagnostic[]`
- `astText: string | null`
- `astJson: object | null`
- `stages: parse/ast/semantic/codegen/assemble/run status map`
- `durationMs: int`
- `truncated: { stdout: bool, stderr: bool }`

### POST `/api/v1/ast`
Request:
- `source: string`

Response:
- `ok, status, diagnostics, astText, astJson, durationMs`

## 3. Diagnostics model

Diagnostic shape:
- `stage: lex | parse | ast | semantic | codegen | assemble | run | internal`
- `severity: error | warning`
- `message: string`
- `line: number | null`
- `column: number | null`
- `raw: string`

Status mapping:
- lexer exception -> `lexical_error`
- parser listener exception -> `syntax_error`
- AST visitor exception -> `ast_error`
- static checker exception -> `semantic_error`
- codegen exception -> `codegen_error`
- jasmin non-zero -> `assembly_error`
- JVM non-zero -> `runtime_error`
- timeout -> `timeout`
- validation size overflow -> `input_too_large`
- unhandled exception -> `internal_error`

## 4. Compiler integration strategy (brownfield-safe)

- Root compiler (`src/`, `build/`) is read-only reference.
- Runner will use vendored copy under `openspec/runner/compiler_vendor/`.
- ANTLR artifacts are copied/generated inside vendored area and never used from root at runtime.
- Vendored codegen is adapted so emitter output directory is injectable.
- `run` flow generates `.j/.class` only in request temp workspace.

### Key adaptation
Current codegen writes to hardcoded `src/runtime`. In vendored copy:
1. `Emitter` accepts optional `output_dir`.
2. `CodeGenerator` accepts `output_dir` and passes it to every `Emitter` instance.
3. Runner calls codegen with workspace output dir.

## 5. Pipeline flow

For `/api/v1/run`:
1. Validate `source/stdin/timeoutSeconds` against limits.
2. Parse via ANTLR lexer/parser + custom error listener.
3. AST generation (`ASTGeneration().visit(parse_tree)`).
4. Serialize AST (`astText`, `astJson`) if requested.
5. Static semantic check.
6. Create temp workspace.
7. Copy runtime assets to workspace (`jasmin.jar`, `io.class`).
8. Run vendored codegen to produce `TyC.j` (+ struct `.j` if any) in workspace.
9. Run Jasmin assembly (`java -jar jasmin.jar ...`) in workspace.
10. Run JVM main (`java -cp <workspace> TyC`) with stdin.
11. Truncate stdout/stderr per limits.
12. Cleanup workspace in `finally`.

For `/api/v1/ast`:
- Steps 1-4 only (no semantic/codegen/run).

## 6. AST serialization

`astText = str(ast)`.

`astJson` uses recursive serializer:
- primitive -> direct
- list -> mapped
- AST node -> `{ kind, fields }` from public attributes (excluding private)
- fallback -> `str(value)`

## 7. Security/runtime policy

- `subprocess.run([...], shell=False)` only.
- Timeout enforced for assembly and runtime subprocess.
- Request-level combined timeout budget in v1 (same configured timeout for each stage execution call).
- Limits from env:
  - max source bytes
  - max stdin bytes
  - max timeout
  - max output bytes
- CORS allowlist from `TYC_ALLOWED_ORIGINS`.
- Optional concurrency limiter via semaphore (`TYC_MAX_CONCURRENT_RUNS`).
- Cleanup temp directory in `finally`.
- No user-controlled file paths.
- Error messages avoid leaking absolute host paths.

## 8. Frontend design

- React + Vite + TypeScript.
- Main features:
  - Monaco editor (`CodeEditor`).
  - Toolbar (`Run`, `Load Sample`, `Clear`).
  - Stdin panel.
  - Result panel tabs: `Output`, `Errors`, `AST`.
- UI states: `idle`, `running`, `success`, `error`, `timeout`, `api_offline`.
- API base URL via `VITE_TYC_API_BASE_URL`.

## 9. Deployment design

- Frontend deploy on Vercel (`openspec/frontend` root).
- Runner deploy as Docker container on external host supporting Java + Python.
- Frontend points to runner origin through env var.
- CORS allowlist includes deployed Vercel origin only.

## 10. Isolation verification strategy

- All writes constrained to `openspec/` paths.
- Runner-generated execution artifacts produced only in OS temp dir and removed after request.
- Tests/verification include repository change check to confirm no modified/generated files outside `openspec/`.

## 11. Rejected alternatives

1. **Run compile/execute directly inside Vercel serverless**
   - Rejected due poor fit for JVM subprocess sandboxing/time limits.
2. **Reuse root compiler runtime output path**
   - Rejected because violates strict isolation and risks polluting root `src/runtime`.
3. **Skip semantic check in `/run`**
   - Rejected because spec requires semantic diagnostics before codegen/run.