# Tasks: tyc-web-compiler

## 1) OpenSpec artifacts

- [x] Create `proposal.md` with intent, scope, risks, split-deployment decision.
- [x] Create delta spec under `specs/web-compiler/spec.md` with testable requirements/scenarios.
- [x] Create `design.md` covering API, pipeline, isolation, security/runtime policy.
- [x] Keep proposal/spec/design updated if implementation reveals drift.

## 2) Runner API foundation (`openspec/runner/`)

- [x] Scaffold Python package and dependencies (`requirements-web.txt`).
- [x] Implement FastAPI app with `GET /health`.
- [x] Implement request/response schemas and status enums.
- [x] Add CORS setup from environment allowlist.

## 3) Compiler integration + runtime assets (isolated)

- [x] Vendor/copy required compiler modules into `openspec/runner/compiler_vendor/`.
- [x] Vendor/copy ANTLR artifacts into `openspec/runner/compiler_vendor/build/`.
- [x] Vendor/copy runtime assets (`jasmin.jar`, `io.java`, `io.class`) into `openspec/runner/runtime_assets/`.
- [x] Adapt vendored emitter/codegen to support configurable output directory.

## 4) Compiler service + AST serializer

- [x] Implement parse/AST stage with lexer/parser + custom error listener.
- [x] Implement semantic checking stage before codegen.
- [x] Implement AST serializer (text + JSON).
- [x] Implement `/api/v1/ast` endpoint.
- [x] Implement `/api/v1/run` full pipeline endpoint.

## 5) Workspace, timeout, cleanup, truncation policy

- [x] Add per-request temp workspace helper.
- [x] Run Jasmin assembly and JVM execution inside workspace only.
- [x] Enforce source/stdin/timeout limits.
- [x] Enforce stdout/stderr truncation with flags.
- [x] Ensure workspace cleanup in `finally`.

## 6) Frontend React + Vite (`openspec/frontend/`)

- [x] Scaffold Vite React TypeScript app structure.
- [x] Implement API client and shared response types.
- [x] Implement editor, toolbar, stdin panel, result tabs (Output/Errors/AST).
- [x] Add sample programs and load-sample behavior.
- [x] Implement UI states: idle/running/success/error/timeout/api_offline.

## 7) Deployment docs/config

- [x] Add runner Dockerfile under `openspec/runner/Dockerfile` (non-root user).
- [x] Add deployment guide under `openspec/docs/deployment.md` for Vercel + external runner.
- [x] Document required frontend/runner env vars.

## 8) Tests and verification

- [x] Add backend tests for success, syntax, semantic, runtime/timeout, stdin, AST.
- [x] Add API tests for `/health`, `/api/v1/run`, `/api/v1/ast`, validation errors.
- [x] Build frontend successfully.
- [x] Create `verification.md` with completeness/correctness/coherence and test evidence.
- [x] Verify no modified/generated files outside `openspec/`.

## 9) Sync + archive + retrospective

- [x] Merge delta spec into `openspec/specs/web-compiler/spec.md`.
- [x] Archive change to `openspec/changes/archive/YYYY-MM-DD-tyc-web-compiler/`.
- [x] Add retrospective on OPSX effectiveness vs friction.
