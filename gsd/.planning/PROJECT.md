# PROJECT — TyC Web Compiler (GSD Variant)

## Project Identity
- Name: TyC Web Compiler (GSD-isolated variant)
- Scope root: `gsd/`
- Spec authority: `gsd/WEBAPP_SPEC.md`
- Workflow: Initialize → Discuss → Plan → Execute → Verify → Ship → Repeat

## Product Goal
Build a public web compiler for TyC that:
1. Accepts TyC source in browser
2. Accepts optional stdin
3. Runs parse → AST → semantic → codegen → assemble → JVM execution
4. Returns stable diagnostics for syntax/semantic/runtime/timeout and related failures
5. Returns stdout on success
6. Returns AST text + JSON for parseable source
7. Uses React + Vite frontend deployable on Vercel and external Docker-capable runner

## Hard Constraints
1. Absolute isolation: all create/edit/delete/generate/config/test actions must stay inside `gsd/`.
2. Read-only access to root compiler (`src/`, `tests/`, `run.py`, etc.) is allowed only for understanding behavior.
3. No root `.planning/`; all workflow artifacts must be under `gsd/.planning/`.
4. No generated ANTLR/Jasmin/.class/build artifacts outside `gsd/`.
5. Any needed adaptation of compiler must be copied/vendorized into `gsd/runner/`.

## Architecture Direction
- Frontend: `gsd/frontend/` (React + Vite + TypeScript + Monaco)
- Runner API: `gsd/runner/` (FastAPI)
- Execution model: per-request temp workspace, timeout, truncation, cleanup
- Runtime host: external Docker-capable environment (not Vercel serverless)

## Out of Scope (v1)
- Auth/account/history/share links
- Multi-file projects
- Debugger/autocomplete based on internals
- Collaboration and queue system

## Success Criteria (milestone)
- APIs available: `GET /health`, `POST /api/v1/run`, `POST /api/v1/ast`
- Contract-compliant statuses/diagnostics
- Frontend build passes under `gsd/frontend`
- Backend tests cover success/syntax/semantic/ast/stdin/timeout
- No modified files outside `gsd/`

## Known Risks
- Root compiler codegen writes to root runtime by default; must be isolated in vendorized runner path
- Subprocess execution for public input requires strict limits and cleanup
- Tooling defaults may try writing root `.planning/`; must stay under `gsd/.planning/`

## Working Rule
When a required action appears to need modification outside `gsd/`, stop and ask user before proceeding.
