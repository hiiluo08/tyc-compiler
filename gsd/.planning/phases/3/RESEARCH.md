# Phase 3: AST serialization and diagnostics contract - Research

**Researched:** 2026-05-07
**Domain:** TyC runner response contract (AST serialization, diagnostics normalization, stage transitions)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### 1) Scope and files
Phase 3 changes are limited to `gsd/` only, primarily:
- `gsd/runner/app/ast_serializer.py`
- `gsd/runner/app/compiler_service.py`
- `gsd/runner/app/main.py`
- `gsd/runner/app/schemas.py` (only if contract types need tightening)
- `gsd/runner/tests/test_phase3_*`
- `gsd/.planning/phases/3/*`

### 2) AST serialization contract
- `astText = str(ast)`.
- `astJson` must follow recursive serializer shape:
  - primitive -> primitive
  - list -> serialized list
  - AST node -> `{ "kind": ClassName, "fields": { ... } }`
  - `None` -> `null`
  - unknown objects -> `str(value)`
- `/api/v1/run`: include `astText`/`astJson` when `includeAst=true` and source is parseable.
- `/api/v1/ast`: always return both `astText` and `astJson` on success.

### 3) Diagnostics/status mapping
For `/api/v1/run` and `/api/v1/ast`, map errors to spec statuses:
- lexical exception -> `lexical_error` (stage `lex`)
- parser listener syntax error -> `syntax_error` (stage `parse`)
- AST generation failure -> `ast_error` (stage `ast`)
- semantic checker failure -> `semantic_error` (stage `semantic`)
- codegen failure -> `codegen_error` (stage `codegen`)
- jasmin failure -> `assembly_error` (stage `assemble`)
- JVM non-zero -> `runtime_error` (stage `run`)
- subprocess timeout -> `timeout` (stage `run` or current stage)
- unexpected -> `internal_error` (stage `internal`)

Diagnostic object must follow spec exactly:
- `stage`, `severity`, `message`, `line`, `column`, `raw`
- `line/column` extracted when parser error format provides them; otherwise `null`.

### 4) Stage transition contract
- Stage keys remain fixed: `parse, ast, semantic, codegen, assemble, run`.
- Success path: all `success`.
- Failure path: current stage `failed`, later stages `skipped`.
- Earlier completed stages remain `success`.

### 5) includeAst behavior
- `includeAst=false`: run response may omit AST payload (`astText=null`, `astJson=null`) even if parse succeeds.
- `includeAst=true`: preserve AST on semantic failure and later failures when parse/AST stages succeeded.

### 6) Test scope for Phase 3
Must add backend tests for:
1. `/api/v1/ast` returns contract-compliant `astText` + non-empty structured `astJson`.
2. `/api/v1/run` semantic error returns `semantic_error` and preserves AST when `includeAst=true`.
3. `/api/v1/run` syntax error returns `syntax_error` with diagnostic stage `parse`.
4. `/api/v1/run` runtime error maps to `runtime_error` with stderr.
5. `/api/v1/run` timeout maps to `timeout`.
6. Stage-status transitions are consistent with failure stage.
7. Isolation guard remains green (no new non-`gsd/` mutations from phase execution).

### 7) Non-goals in Phase 3
- Frontend changes.
- Deployment docs/config.
- Rate-limit/CORS hardening expansions (Phase 5/6 scope).

### 8) Isolation enforcement
- No create/edit/delete outside `gsd/`.
- No generated artifacts under root `build/` or root `src/runtime/`.
- If any step appears to require root change, stop and ask user.

### Claude's Discretion
None explicitly listed in `3-CONTEXT.md`. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]

### Deferred Ideas (OUT OF SCOPE)
None explicitly listed in `3-CONTEXT.md`. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FR-06 | Stable status contract | Status mapping table + stage transition policy below. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/REQUIREMENTS.md] |
| FR-07 | Diagnostic contract | Diagnostic normalization pattern + parser line/column extraction policy. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| FR-08 | AST output contract | Serializer algorithm + includeAst behavior matrix. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
</phase_requirements>

## Summary

Phase 3 should be implemented as a contract-hardening phase, not a compiler-feature phase. The current runner already has status enums and basic pipeline wiring, but response shaping is still stub-like (`astJson={}`, diagnostics empty, and failure-stage transitions currently marked `failed` for multiple downstream stages). This diverges from the locked contract that requires exact error normalization and deterministic stage progression semantics. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/main.py] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]

Primary implementation responsibility should be centralized in `compiler_service.py` for stage-aware execution and normalized failure objects, with `main.py` mostly validating payload size and returning typed responses. AST serialization should be isolated in `ast_serializer.py` and reused by both `/api/v1/run` and `/api/v1/ast` to prevent schema drift. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]

Phase-3 test additions should target behavior-level contracts (status/stage/diagnostic/AST retention) and not overfit implementation details. Current tests mostly validate top-level keys and a timeout monkeypatch; they do not yet prove semantic-error AST retention, parser-stage diagnostics, or stage skipping semantics. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/tests/test_run_validation.py] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/tests/test_phase2_pipeline_cases.py]

**Primary recommendation:** Implement a single internal `RunResultDetailed` contract in `compiler_service.py` that always carries `status`, `diagnostics`, `stages`, `astText`, `astJson`, `stdout`, `stderr`, then map directly to API schema objects. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Parse + AST generation | API / Backend | — | Requires ANTLR runtime and compiler visitor classes on server side. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/compiler_service.py] |
| AST serialization (`astJson`) | API / Backend | Frontend (render only) | Serialization format must be canonical from runner; frontend should only visualize. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| Diagnostic normalization | API / Backend | — | Error-class-to-status mapping occurs where exceptions are caught. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md] |
| Stage transition policy | API / Backend | — | Stages reflect pipeline execution order in service runtime. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| includeAst behavior | API /Backend | Frontend (consumes null/non-null) | Request flag is API input and controls AST payload inclusion. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py] |
| Contract verification tests | API / Backend test tier | — | All required checks are runner API/service tests in Phase 3 context. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md] |

## Project Constraints (from CLAUDE.md)

- Prefer `python run.py ...` wrappers generally, but direct pytest should be used when failing exit code matters. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/CLAUDE.md]
- Grammar outputs are generated into `build/` and generated files should not be hand-edited. For GSD variant, keep analogous generated assets under `gsd/runner/build/` only. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/CLAUDE.md] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]
- Compiler flow is parse -> ASTGeneration -> StaticChecker -> CodeGenerator -> Jasmin -> JVM; Phase 3 changes must preserve this sequence while improving response contract semantics. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/CLAUDE.md]
- Root codegen normally writes to `src/runtime/`; GSD variant must avoid root writes and keep output in temp workspace under `gsd/`. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/CLAUDE.md] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.136.1 | HTTP API layer (`/health`, `/api/v1/run`, `/api/v1/ast`) | Existing runner already uses it and tests are built around TestClient. [VERIFIED: python import version check] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/main.py] |
| Pydantic | 2.13.4 | Request/response schema enforcement and enum contracts | Already defines Status/Diagnostic/StageStatus models with validation constraints. [VERIFIED: python import version check] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py] |
| ANTLR4 Python runtime | installed (version string not exposed) | Lexing/parsing for TyC grammar in runner | Required by `CommonTokenStream`/`InputStream` usage in service. [VERIFIED: import antlr4 succeeds] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/compiler_service.py] |
| Java runtime | 23 | Jasmin assembly + JVM execution | Required for `jasmin.jar` and `java -cp ... TyC` execution path. [VERIFIED: java -version] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/runtime_workspace.py] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Uvicorn | 0.46.0 | Local/production ASGI serving | Runner service process startup and deployment. [VERIFIED: python import version check] |
| pytest | 9.0.2 | Phase contract verification | Add phase-3 API/service behavior tests. [VERIFIED: python import version check] |
| httpx | 0.28.1 | Test transport dependency for FastAPI client stack | Needed by existing API tests. [VERIFIED: python import version check] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| In-service serializer module | Inline serializer in endpoint | Faster initial coding but high drift risk between `/run` and `/ast`. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md] |
| Exception-to-status mapping in endpoints | Mapping inside CompilerService | Endpoint mapping duplicates logic for API + service tests; service-centralized mapping is cleaner. [ASSUMED] |

**Installation:**
```bash
pip install -r gsd/runner/requirements-web.txt
```

**Version verification note:** `gsd/runner/requirements-web.txt` is currently unpinned; versions above are from this environment and should be locked later for reproducibility. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/requirements-web.txt]

## Architecture Patterns

### System Architecture Diagram

```text
POST /api/v1/run
  |
  v
Input validation (size, timeout bounds)
  | ok
  v
Parse stage (lexer + parser + listener)
  |--> lexical exception -> status lexical_error, stage lex failed, downstream skipped
  |--> syntax exception  -> status syntax_error, stage parse failed, downstream skipped
  v
AST stage (ASTGeneration)
  |--> ast exception     -> status ast_error, stage ast failed, downstream skipped
  v
(Optional AST payload generation when includeAst=true)
  |
  v
Semantic stage (StaticChecker)
  |--> semantic exception -> status semantic_error, keep AST if available
  v
Codegen stage
  |--> exception -> status codegen_error
  v
Assemble stage (jasmin)
  |--> returncode!=0 -> status assembly_error
  v
Run stage (JVM)
  |--> timeout -> status timeout
  |--> returncode!=0 -> status runtime_error
  v
RunResponse with fixed stage keys + diagnostics + (optional) astText/astJson
```

### Recommended Project Structure
```text
gsd/runner/app/
├── ast_serializer.py      # canonical astText/astJson generation
├── compiler_service.py    # stage execution + normalized internal result
├── main.py                # request validation + response translation
├── schemas.py             # request/response enums/models
└── runtime_workspace.py   # isolated assemble/run subprocess boundary
```

### Pattern 1: Canonical recursive AST serializer
**What:** One serializer function for primitives/lists/AST-node/None/fallback-string.
**When to use:** Any endpoint returning AST payloads.
**Example:**
```python
# Source: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md (§11)
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

### Pattern 2: Stage-aware failure finalization
**What:** Mark exactly one stage `failed`, downstream as `skipped`, upstream as `success`.
**When to use:** Any non-success status in `/run` pipeline.
**Example:**
```python
# Source: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md
# fixed order: parse, ast, semantic, codegen, assemble, run
```

### Anti-Patterns to Avoid
- **Multi-stage failed flags:** marking semantic/codegen/assemble/run all as `failed` for one error; this violates locked transition policy. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]
- **Endpoint-specific serializer logic:** duplicate AST conversion rules in `/run` and `/ast`; leads to drift. [ASSUMED]
- **Swallowing exception class into `internal_error`:** loses required status mapping granularity. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP schema validation | Manual dict checks | Pydantic models in `schemas.py` | Already provides constraints and strict bool behavior. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py] |
| Temp runtime cleanup | Custom ad-hoc path cleanup per call | `RuntimeWorkspace` context manager | Existing isolation and cleanup boundary already implemented. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/runtime_workspace.py] |
| AST JSON formatting | Special-case per node type manually | Generic recursive serializer contract | Avoid missing new node fields and keeps shape stable. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |

**Key insight:** Phase 3 is contract consistency work; reuse existing typed boundaries instead of introducing parallel response logic. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py]

## Common Pitfalls

### Pitfall 1: Incorrect status-to-stage mapping
**What goes wrong:** `timeout`, `runtime_error`, and `assembly_error` all collapse into generic error status.
**Why it happens:** Single broad `except Exception` or returncode checks without stage context.
**How to avoid:** Catch and map at stage boundaries with explicit normalized diagnostics.
**Warning signs:** Diagnostics always show `internal` stage.
[VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]

### Pitfall 2: AST omitted on semantic failures even with includeAst=true
**What goes wrong:** User loses AST tab for parseable programs with semantic errors.
**Why it happens:** AST payload generation delayed until only success path.
**How to avoid:** Generate/retain AST immediately after AST stage when includeAst=true.
**Warning signs:** semantic_error responses contain null AST fields despite parse success.
[VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]

### Pitfall 3: Stage progression marked as all failed
**What goes wrong:** Downstream observability cannot identify first failing stage.
**Why it happens:** Current implementation sets failed for semantic/codegen/assemble/run whenever not ok.
**How to avoid:** Build helper that finalizes stage vector from `failure_stage` index.
**Warning signs:** One failure produces multiple failed stages.
[VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/main.py]

## Code Examples

### Diagnostic normalization payload shape
```python
# Source: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py
Diagnostic(
    stage=DiagnosticStage.PARSE,
    severity=DiagnosticSeverity.ERROR,
    message="Error on line 1 col 10: ...",
    line=1,
    column=10,
    raw="Error on line 1 col 10: ...",
)
```

### includeAst behavior matrix
```text
# Source: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md
includeAst=false: astText=null, astJson=null (even if parse+ast succeeded)
includeAst=true:  keep AST on semantic/codegen/assemble/run failures after ast success
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stub response with empty diagnostics/astJson and coarse failure stages | Normalized, stage-specific diagnostics and AST retention contract | Phase 3 scope | Enables frontend to render accurate errors and AST tab behavior. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/ROADMAP.md] |

**Deprecated/outdated:**
- Treating all non-success outcomes as generic internal failure behavior is outdated for this phase contract. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Service-centralized mapping is cleaner than endpoint-level mapping | Standard Stack / Alternatives | Low; mostly maintainability preference |
| A2 | Duplicated endpoint serializer logic is likely to drift | Architecture Patterns / Anti-Patterns | Medium; could still be manageable in small codebase |

## Open Questions

1. **Parser error raw format stability**
   - What we know: line/column should be extracted when parser string includes them. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md]
   - What's unclear: exact regex needed for all parser/lexer error variants in current vendor code.
   - Recommendation: define parser extraction helper with tests for at least 3 representative error strings.

2. **Timeout stage attribution for compile vs run**
   - What we know: timeout should map to `timeout` and stage `run` or current stage. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md]
   - What's unclear: whether assembler timeout should report `assemble` and JVM timeout `run` (recommended), or always `run`.
   - Recommendation: lock policy in tests now: timeout stage equals currently executing stage.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runner service/tests | ✓ | 3.12.10 | — |
| Java | Jasmin assembly and JVM run | ✓ | 23 | — |
| FastAPI | API layer | ✓ | 0.136.1 | — |
| Pydantic | Schema contracts | ✓ | 2.13.4 | — |
| pytest | Phase-3 verification | ✓ | 9.0.2 | — |
| ANTLR4 runtime | Parser integration | ✓ | version not exposed | Use installed runtime as-is |

**Missing dependencies with no fallback:**
- None identified. [VERIFIED: local command probes]

**Missing dependencies with fallback:**
- None identified. [VERIFIED: local command probes]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + FastAPI TestClient [VERIFIED: python import version check] |
| Config file | none detected in `gsd/runner/` [VERIFIED: file listing] |
| Quick run command | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_*.py -q` [ASSUMED] |
| Full suite command | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests -q` [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FR-08 | `/api/v1/ast` returns non-empty `astText` + structured `astJson` | API integration | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_ast_contract.py -q` | ❌ Wave 0 |
| FR-08 + FR-06 | semantic_error preserves AST when `includeAst=true` | API integration | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_run_semantic_ast.py -q` | ❌ Wave 0 |
| FR-06 + FR-07 | syntax_error maps to parse-stage diagnostic | API integration | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_run_syntax_diag.py -q` | ❌ Wave 0 |
| FR-06 | runtime_error and timeout mapping | service/api integration | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_run_runtime_timeout.py -q` | ❌ Wave 0 |
| FR-06 | stage transition consistency | unit/integration | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_stage_transitions.py -q` | ❌ Wave 0 |
| NFR-01 / VR-04 | no non-`gsd/` mutation regression | isolation test | `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_isolation.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests/test_phase3_*.py -q`
- **Per wave merge:** `PYTHONPATH=gsd/runner python -m pytest gsd/runner/tests -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `gsd/runner/tests/test_phase3_ast_contract.py` — validates `/api/v1/ast` payload correctness
- [ ] `gsd/runner/tests/test_phase3_run_semantic_ast.py` — validates semantic failure + AST retention
- [ ] `gsd/runner/tests/test_phase3_run_syntax_diag.py` — validates parse-stage diagnostics
- [ ] `gsd/runner/tests/test_phase3_run_runtime_timeout.py` — validates runtime/timeout mappings
- [ ] `gsd/runner/tests/test_phase3_stage_transitions.py` — validates failed/skipped progression
- [ ] `gsd/runner/tests/test_phase3_isolation.py` — validates no out-of-scope writes in phase execution

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Public anonymous endpoint in v1 scope. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| V3 Session Management | no | No login/session in v1 scope. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| V4 Access Control | yes | CORS allowlist and future rate limit/concurrency constraints. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| V5 Input Validation | yes | Pydantic constraints + source/stdin byte limits. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/schemas.py] [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/main.py] |
| V6 Cryptography | no | No cryptographic operations in this phase scope. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/3-CONTEXT.md] |

### Known Threat Patterns for FastAPI + subprocess runner

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Oversized input DoS | Denial of Service | Hard byte caps and timeout bounds in request handling. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/main.py] |
| Hanging subprocess | Denial of Service | `subprocess.run(..., timeout=...)` and timeout status mapping. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |
| Host filesystem contamination | Tampering | Per-request temp workspace and cleanup in `finally` via context manager. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/runner/app/runtime_workspace.py] |
| Internal path/error leakage | Information Disclosure | Normalize diagnostics and avoid exposing internal absolute paths in message text. [VERIFIED: /d/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md] |

## Sources

### Primary (HIGH confidence)
- `gsd/WEBAPP_SPEC.md` - API, status/diagnostic, AST serializer, limits, tests.
- `gsd/.planning/phases/3-CONTEXT.md` - locked decisions for Phase 3 implementation.
- `gsd/.planning/REQUIREMENTS.md` - FR-06/07/08 requirement IDs.
- `gsd/.planning/ROADMAP.md` - phase deliverables and traceability.
- `gsd/runner/app/main.py` - current response shaping and stage behavior.
- `gsd/runner/app/compiler_service.py` - current pipeline and exception handling.
- `gsd/runner/app/schemas.py` - current enum/model contract.
- `gsd/runner/tests/*.py` - existing coverage and phase-3 gaps.

### Secondary (MEDIUM confidence)
- Local runtime probes (`python --version`, package imports, `java -version`) for environment availability and concrete versions.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - based on live environment imports and current code dependencies.
- Architecture: HIGH - locked by phase context and spec-defined pipeline.
- Pitfalls: HIGH - directly observed from current implementation/spec gaps.

**Research date:** 2026-05-07
**Valid until:** 2026-06-06
