# REQUIREMENTS — TyC Web Compiler (GSD Variant)

Source of truth: `gsd/WEBAPP_SPEC.md`.

## Functional Requirements

### FR-01 Source input
System must accept TyC source code from browser editor.
- Trace: Spec §1, §4.1, §7

### FR-02 Optional stdin
System must accept optional stdin string for runtime I/O builtins.
- Trace: Spec §1, §4.1, §6.4

### FR-03 Full run pipeline endpoint
System must expose `POST /api/v1/run` executing parse → AST → semantic → codegen → assemble → run.
- Trace: Spec §8.2, §10

### FR-04 AST endpoint
System must expose `POST /api/v1/ast` for parse + AST generation without execute.
- Trace: Spec §8.3

### FR-05 Health endpoint
System must expose `GET /health`.
- Trace: Spec §8.1

### FR-06 Stable status contract
System responses must use defined status enum (`success`, `syntax_error`, `semantic_error`, `runtime_error`, `timeout`, etc.) and stage tracking.
- Trace: Spec §8.2, §9

### FR-07 Diagnostic contract
System must return normalized diagnostics with stage/severity/message/line/column/raw.
- Trace: Spec §9.2

### FR-08 AST output contract
For parseable source and `includeAst=true`, system must return both `astText` and `astJson`.
- Trace: Spec §8.2, §8.3, §11

### FR-09 Frontend interface
Frontend must provide Monaco editor, toolbar (Run/Clear/Load Sample), stdin panel, and result tabs (Output/Errors/AST).
- Trace: Spec §7.3, §7.4

### FR-10 Samples
Frontend must include minimum samples: hello, read integer, syntax error, semantic error, timeout.
- Trace: Spec §7.6

### FR-11 UI state model
Frontend must support states: idle/running/success/error/timeout/api_offline.
- Trace: Spec §7.5

## Non-Functional Requirements

### NFR-01 Isolation
All writes and generated artifacts for this variant must stay inside `gsd/`.
- Trace: Spec §2, §16

### NFR-02 Runner safety limits
Enforce source/stdin size caps, timeout bounds, output truncation, and concurrency limit.
- Trace: Spec §12.1

### NFR-03 Process safety
Use non-shell subprocess, temp workspace per request, cleanup in finally, no user filenames.
- Trace: Spec §12.2, §10.6

### NFR-04 Deployment shape
Frontend deployable on Vercel; runner deployable as Docker service with non-root user.
- Trace: Spec §3, §13

### NFR-05 Observability baseline
Log request ID/stage/status/duration without logging full source by default.
- Trace: Spec §12.4

## Verification Requirements

### VR-01 Backend tests
Must cover success, printInt, stdin path, syntax error, semantic error with AST, timeout, oversized input, no leakage outside gsd.
- Trace: Spec §14.1

### VR-02 API tests
Must cover `/health`, `/api/v1/run` success+errors, `/api/v1/ast`, invalid timeout, missing source.
- Trace: Spec §14.2

### VR-03 Frontend checks
Must validate successful run output, syntax/semantic display, AST tab, stdin sample, timeout, API offline UX.
- Trace: Spec §14.3

### VR-04 Isolation verification
No changed files outside `gsd/`; no generated artifacts leaked to root `build/` or `src/runtime/`.
- Trace: Spec §2, §16
