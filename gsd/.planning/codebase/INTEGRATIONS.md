# External Integrations

**Analysis Date:** 2026-05-07

## APIs & External Services

**Toolchain download:**
- ANTLR download endpoint (`antlr.org`) - Bootstraps parser toolchain during setup
  - SDK/Client: Python stdlib `urllib.request` in `run.py`
  - Auth: Not applicable

**JVM toolchain invocation (local process boundary):**
- Java/Javac/Jasmin CLI - Invoked by Python via subprocess for compile/assemble/run
  - SDK/Client: Python `subprocess` in `run.py` and `tests/utils.py`
  - Auth: Not applicable

## Data Storage

**Databases:**
- Not detected

**File Storage:**
- Local filesystem only
  - Grammar outputs to `build/` in `run.py`
  - Codegen outputs (`.j`, `.class`) under `src/runtime/` via `src/codegen/emitter.py` and `tests/utils.py`
  - Test HTML reports under `reports/` via `run.py`

**Caching:**
- None (only local Python caches cleaned by `run.py clean-cache`)

## Authentication & Identity

**Auth Provider:**
- Custom/None (no user auth layer in compiler core)
  - Implementation: Not applicable

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry/hosted tracker detected)

**Logs:**
- CLI stdout/stderr from Python and subprocess commands (`run.py`, `tests/utils.py`)

## CI/CD & Deployment

**Hosting:**
- Not detected (repository is compiler project, not deployed service)

**CI Pipeline:**
- Not detected in repository root (no GitHub Actions/GitLab CI config found in scanned files)

## Environment Configuration

**Required env vars:**
- None required by core compiler flow
- `PYTHONPATH` is set in test wrappers (`run.py`) and test harness import path logic is in `tests/utils.py`

**Secrets location:**
- Not detected

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- HTTP fetch to ANTLR download URL during setup (`run.py`)

## Integration Touchpoints for Web Compiler Variant

- Parser/AST boundary: call ANTLR-generated lexer/parser (`build/TyCLexer.py`, `build/TyCParser.py`) then `ASTGeneration` in `src/astgen/ast_generation.py`.
- Semantic boundary: invoke `StaticChecker.check_program()` in `src/semantics/static_checker.py` before codegen.
- Code execution boundary: isolate subprocess usage currently in `tests/utils.py` (`javac`, `java -jar jasmin.jar`, `java -cp ... TyC`) behind a sandboxed worker/API in web context.
- Artifact boundary: avoid shared writes to `src/runtime/`; current emitter writes there by default (`src/codegen/emitter.py`). Multi-user web usage needs per-request temp directories.

---

*Integration audit: 2026-05-07*
