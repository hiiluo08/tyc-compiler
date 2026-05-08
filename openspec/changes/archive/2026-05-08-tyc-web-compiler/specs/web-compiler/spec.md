# Delta Spec: tyc-web-compiler

## ADDED Requirements

### Requirement: Source editing and sample programs
Frontend MUST provide a code editor and predefined samples (`Hello TyC`, `Read integer`, `Syntax error`, `Semantic error`, `Timeout`) that can be loaded into editor + stdin.

#### Scenario: Load sample
- **Given** user opens web compiler
- **When** user selects sample `Read integer`
- **Then** editor source is replaced by sample code and stdin area is set to sample stdin

### Requirement: Compile/run success returns stdout
Runner MUST execute full pipeline for valid TyC source and return `status=success` with stdout.

#### Scenario: Hello TyC
- **Given** source `void main() { printString("Hello TyC"); }`
- **When** client calls `POST /api/v1/run`
- **Then** response has `ok=true`, `status=success`, and `stdout=Hello TyC`

### Requirement: Syntax error diagnostics
Runner MUST return stable syntax diagnostics for parse failure.

#### Scenario: Parse fails
- **Given** source `void main( { }`
- **When** client calls `POST /api/v1/run`
- **Then** response has `ok=false`, `status=syntax_error`, at least one diagnostic with `stage=parse`

### Requirement: Semantic error diagnostics and AST preservation
Runner MUST run semantic checker before codegen and preserve AST for parseable source even when semantic check fails.

#### Scenario: Type mismatch
- **Given** source `void main() { int x = "abc"; }`
- **When** client calls `POST /api/v1/run` with `includeAst=true`
- **Then** response has `status=semantic_error` and non-empty `astText` + `astJson`

### Requirement: Runtime error diagnostics
Runner MUST return `runtime_error` when JVM execution exits non-zero.

#### Scenario: Runtime failure
- **Given** parseable and semantically valid program that fails at runtime
- **When** client calls `POST /api/v1/run`
- **Then** response has `status=runtime_error`, `stage=run` diagnostic, and captured stderr (possibly truncated)

### Requirement: Timeout diagnostics
Runner MUST terminate compile/run request that exceeds configured timeout.

#### Scenario: Infinite loop
- **Given** source `void main() { while (1) {} }`
- **When** client calls `POST /api/v1/run` with timeout within allowed range
- **Then** response has `status=timeout` and diagnostic message indicating timeout exceeded

### Requirement: AST endpoint
Runner MUST expose AST-only endpoint returning both text and JSON AST for parseable source.

#### Scenario: AST request success
- **Given** source `void main() {}`
- **When** client calls `POST /api/v1/ast`
- **Then** response has `ok=true`, `status=success`, `astText` and `astJson`

### Requirement: Stdin support
Runner MUST pass provided stdin into TyC runtime for built-ins `readInt`, `readFloat`, `readString`.

#### Scenario: readInt from stdin
- **Given** source reads an integer and prints `x + 1`
- **And** stdin is `41\n`
- **When** user runs program
- **Then** response stdout is `42`

### Requirement: Output truncation
Runner MUST truncate oversized stdout/stderr and report truncation flags in response.

#### Scenario: Output exceeds limit
- **Given** program generates output larger than configured max bytes
- **When** user runs program
- **Then** response includes truncated stdout/stderr and `truncated.stdout=true` and/or `truncated.stderr=true`

### Requirement: Runner health and API contract
Runner MUST expose `GET /health`, `POST /api/v1/run`, `POST /api/v1/ast` with request/response schema aligned to `openspec/WEBAPP_SPEC.md`.

#### Scenario: Health check
- **Given** runner is running
- **When** client calls `GET /health`
- **Then** response contains `ok=true` and service metadata

### Requirement: Strict isolation under openspec
Implementation MUST not create/modify/generated files outside `openspec/`.

#### Scenario: Isolation check after tests/build
- **Given** all tasks and tests finished
- **When** maintainer inspects repository changes
- **Then** all modified/generated files belong to `openspec/` only

### Requirement: Deployment notes for split architecture
Docs MUST describe Vercel frontend + external Docker runner deployment model and required environment variables.

#### Scenario: Deployment handoff
- **Given** a maintainer needs to deploy v1
- **When** maintainer reads deployment docs in `openspec/docs/`
- **Then** maintainer can configure frontend API base URL, runner env vars, and CORS allowlist without guessing