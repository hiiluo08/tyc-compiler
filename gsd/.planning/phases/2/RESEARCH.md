# Phase 2: Isolated compiler integration and runtime workspace - Research

**Researched:** 2026-05-07
**Domain:** TyC compiler vendoring + isolated compile/assemble/run orchestration in FastAPI runner
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### 1) File layout inside `gsd/runner/`
Phase 2 implementation is constrained to:
- `gsd/runner/compiler_vendor/`
  - `astgen/`
  - `semantics/`
  - `codegen/`
  - `utils/`
  - `grammar/lexererr.py` (or equivalent needed lexer error helper)
- `gsd/runner/build/` (ANTLR generated lexer/parser/visitor for this variant)
- `gsd/runner/runtime_assets/`
  - `jasmin.jar`
  - `io.java`
  - `io.class` (generated within gsd scope)
- `gsd/runner/app/compiler_service.py`
- `gsd/runner/app/runtime_workspace.py`
- tests under `gsd/runner/tests/`

No writes outside `gsd/` are allowed.

### 2) Integration boundaries
- Root compiler is read-only reference only.
- Runner must use vendorized pipeline modules from `gsd/runner/compiler_vendor/`.
- Codegen output must be parameterized to per-request workspace output directory.
- Absolutely no generation into root `src/runtime/` or root `build/`.

### 3) ANTLR/build/runtime asset strategy
- Build-time step inside `gsd/runner/` will:
  1) generate parser/lexer/visitor into `gsd/runner/build/`
  2) copy required runtime assets (`jasmin.jar`, `io.java`) into `gsd/runner/runtime_assets/`
  3) compile `io.java` to `io.class` in `gsd/runner/runtime_assets/`
- No per-request ANTLR generation.

### 4) Runtime workspace and timeout policy
- Each request creates a unique temp workspace under gsd-controlled temp root.
- Workspace flow:
  1) create temp dir
  2) copy runtime assets into temp dir
  3) generate `.j` outputs in temp dir
  4) assemble with Jasmin in temp dir
  5) run JVM in temp dir
  6) cleanup in `finally`
- Timeout policy: single request timeout budget (`timeoutSeconds`) applied consistently to compile/assemble/run subprocess calls.

### 5) Error handling and diagnostics for Phase 2
- Preserve Phase 1 response envelope and status vocabulary.
- Map integration failures to contract statuses where feasible in Phase 2:
  - assembly failure -> `assembly_error`
  - missing Java/toolchain/runtime assets -> `internal_error`
  - subprocess timeout -> `timeout`
- Full normalization breadth (all compiler stages) continues in Phase 3.

### 6) Test scope for Phase 2
Phase 2 tests focus on integration safety and minimal E2E backend path:
1. Build/runtime assets generated/copied only under `gsd/runner/*`.
2. Vendorized codegen writes outputs only into provided workspace dir.
3. Per-request workspace cleanup executes on success and failure.
4. Run sample program path works through compile→assemble→run in isolated temp dir.
5. Isolation test confirms no new root `build/`/`src/runtime/` writes.

### 7) Isolation enforcement
- Allowed: read root files for behavior parity.
- Forbidden: any create/edit/delete/move/generate outside `gsd/`.
- Forbidden: root `.planning/` artifacts.
- If any plan step requires root modification, stop and ask user.

### Claude's Discretion
- Use spec defaults for unresolved gray areas.
- Vendor scope = core pipeline modules only.
- ANTLR/runtime assets strategy = build-time generate/copy under `gsd/runner/`.
- Timeout policy = single request budget for full compile+run pipeline.

### Deferred Ideas (OUT OF SCOPE)
- Frontend work.
- Full diagnostics/AST contract completion (Phase 3 scope).
- Deployment configuration (Phase 5 scope).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FR-03 | Full run pipeline endpoint parse→AST→semantic→codegen→assemble→run | Vendor-core module map, output_dir injection points, workspace subprocess contract |
| NFR-01 | Isolation: all writes inside `gsd/` | Path rewrite strategy + isolation guard tests + temp workspace under gsd-controlled root |
| NFR-03 | Process safety: shell=False, timeout, temp workspace, cleanup | subprocess.run timeout behavior, TemporaryDirectory/finally cleanup pattern |
| VR-01 | Backend tests include success/stdin/syntax/semantic/timeout/no leakage | Phase-2 integration-focused test matrix and isolation checks |
| VR-04 | No generated artifacts leaked to root `build/` or `src/runtime/` | Explicit negative assertions + baseline git-status checks in test plan |
</phase_requirements>

## Summary

Phase 2 should vendor only the compiler modules that directly participate in parse→AST→semantic→codegen and then rewire imports to local `gsd/runner` packages, not root `src/*`. [VERIFIED: repo source grep/read] The current root compiler hardcodes runtime output in `Emitter.__init__` to `src/runtime` and therefore must be adapted in vendor copy to accept an explicit `output_dir`; this is the key technical change that enforces isolation. [VERIFIED: D:/HK252/PPL/BTL/tyc-compiler/src/codegen/emitter.py]

Runtime execution should be orchestrated per request in an ephemeral workspace with copied `jasmin.jar` and `io.class`, then `java -jar jasmin.jar *.j`, then `java -cp <workspace> TyC`, with timeout and cleanup in all paths. [CITED: https://docs.python.org/3/library/subprocess.html] [CITED: https://docs.python.org/3/library/tempfile.html] The safest implementation for Phase 2 is a small orchestration layer in `runtime_workspace.py` plus a thin compiler pipeline adapter in `compiler_service.py`. [ASSUMED]

**Primary recommendation:** Implement a vendorized `CodeGenerator(output_dir=...)` + `Emitter(filename, output_dir=...)` API first, then build all Phase-2 pipeline tasks and tests around that contract.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Parse/AST/semantic/codegen execution | API / Backend | — | Compiler pipeline is server-side and requires Python modules + generated ANTLR code. [VERIFIED: gsd/WEBAPP_SPEC.md] |
| ANTLR artifact generation | Build-time backend tooling | Filesystem storage | Generated parser/visitor are build artifacts under `gsd/runner/build/`. [VERIFIED: gsd/.planning/phases/2-CONTEXT.md] |
| Jasmin assembly + JVM execution | API / Backend | OS process layer | Needs subprocess execution (`java`, `javac`) with timeout + cwd isolation. [VERIFIED: tests/utils.py] |
| Per-request workspace lifecycle | API / Backend | Filesystem storage | Workspace create/copy/run/cleanup must be controlled by runner service. [VERIFIED: gsd/WEBAPP_SPEC.md §10.6] |
| Isolation verification | Test tier | Git working tree state | Isolation requirements are validated by tests guarding root paths. [VERIFIED: gsd/runner/tests/test_isolation_phase1.py] |

## Project Constraints (from CLAUDE.md)

- Prefer `python run.py` orchestration commands over Makefile in root workflows. [VERIFIED: CLAUDE.md]
- Build ANTLR before tests that import generated `build/*` modules. [VERIFIED: CLAUDE.md]
- Root generated `build/` files are not hand-edited; grammar or source helpers are edited instead. [VERIFIED: CLAUDE.md]
- Built-in IO function sets in checker and codegen must remain consistent (`readInt/readFloat/readString/printInt/printFloat/printString`). [VERIFIED: CLAUDE.md]
- Root codegen currently writes to `src/runtime/`; Phase 2 must avoid this by vendor adaptation under `gsd/`. [VERIFIED: CLAUDE.md + src/codegen/emitter.py]

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.10 | Runner implementation and orchestration | Already active runtime and aligns with existing codebase. [VERIFIED: local python --version] |
| FastAPI | 0.136.1 | HTTP API service layer | Already used in `gsd/runner/app/main.py`. [VERIFIED: local import version + repo read] |
| Pydantic | 2.13.4 | Request/response schema validation | Already used for Phase-1 contracts. [VERIFIED: local import version + repo read] |
| antlr4-python3-runtime | 4.13.2 | Runtime for generated parser/lexer | Matches root ANTLR generation version. [VERIFIED: pip show + run.py] |
| Java/Javac | 23 | Jasmin assembly + JVM runtime + io.java compile | Required by existing TyC codegen flow. [VERIFIED: local java/javac --version + tests/utils.py] |

### Supporting
| Library/Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Uvicorn | 0.46.0 | ASGI serving | Local/dev runner process execution. [VERIFIED: local import version] |
| pytest | 9.0.2 | Integration/isolation tests | Phase-2 regression and isolation gates. [VERIFIED: local pytest --version] |
| httpx | 0.28.1 | API test client support | Existing runner test dependency. [VERIFIED: requirements-web.txt + local import version] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Direct module import from root `src/*` | Vendored copy in `gsd/runner/compiler_vendor/*` | Root import is simpler short-term but violates strict isolation boundary and couples phase to mutable root paths. [VERIFIED: phase context + WEBAPP spec] |
| `finally + shutil.rmtree` manual cleanup | `tempfile.TemporaryDirectory()` context | Both valid; context manager reduces cleanup omission risk. [CITED: https://docs.python.org/3/library/tempfile.html] |

**Installation:**
```bash
python -m pip install -r gsd/runner/requirements-web.txt
```

## Architecture Patterns

### System Architecture Diagram
```text
POST /api/v1/run
   |
   v
compiler_service.run_tyc_program(source, stdin, timeout)
   |
   +--> parse (TyCLexer/TyCParser from gsd/runner/build)
   |       fail -> syntax/lexical status
   |
   +--> ast (ASTGeneration from compiler_vendor)
   |       fail -> ast_error
   |
   +--> semantic (StaticChecker from compiler_vendor)
   |       fail -> semantic_error
   |
   +--> runtime_workspace.execute(ast, stdin, timeout)
           |
           +--> create workspace (gsd temp root)
           +--> copy runtime_assets (jasmin.jar, io.class)
           +--> codegen to workspace/*.j
           +--> java -jar jasmin.jar *.j
           +--> java -cp workspace TyC
           +--> cleanup workspace (always)
```

### Recommended Project Structure
```text
gsd/runner/
├── app/
│   ├── compiler_service.py      # parse→ast→semantic orchestration
│   ├── runtime_workspace.py     # workspace + subprocess orchestration
│   ├── main.py                  # endpoint binding
│   └── schemas.py               # contract models
├── compiler_vendor/
│   ├── astgen/
│   ├── semantics/
│   ├── codegen/
│   ├── utils/
│   └── grammar/lexererr.py
├── build/                       # generated TyCLexer/TyCParser/TyCVisitor
└── runtime_assets/              # jasmin.jar, io.java, io.class
```

### Pattern 1: Output-directory injection in codegen
**What:** Make output location an explicit dependency instead of implicit repo-relative path. [VERIFIED: src/codegen/emitter.py]
**When to use:** Any file-emitting compiler stage that currently writes to fixed paths.
**Example:**
```python
# Source basis: D:/HK252/PPL/BTL/tyc-compiler/src/codegen/emitter.py
class Emitter:
    def __init__(self, filename: str, output_dir: str):
        self.filename = filename
        self.filepath = os.path.join(output_dir, filename)
```

### Pattern 2: Workspace executor boundary
**What:** Keep subprocess + filesystem operations in `runtime_workspace.py`; keep compiler semantics in `compiler_service.py`. [ASSUMED]
**When to use:** Multi-stage execution with strict isolation requirements.

### Anti-Patterns to Avoid
- **Global `os.chdir` as control flow:** root harness changes cwd before codegen; service code should avoid process-global cwd mutations in concurrent server context. [VERIFIED: tests/utils.py]
- **Hardcoded `src/runtime` paths:** leaks artifacts outside phase scope. [VERIFIED: src/codegen/emitter.py]
- **Reusing one shared workspace across requests:** creates cross-request artifact leakage and race conditions. [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Temp workspace lifecycle | Custom ad-hoc tmp naming/cleanup logic | `tempfile.TemporaryDirectory` or `mkdtemp` + `finally` | Standard lib handles robust temp dir semantics. [CITED: https://docs.python.org/3/library/tempfile.html] |
| Process timeout mechanics | Manual polling loops | `subprocess.run(..., timeout=...)` | Built-in timeout raises `TimeoutExpired` cleanly. [CITED: https://docs.python.org/3/library/subprocess.html] |
| AST parser code generation | Custom parser scaffolding | ANTLR generation (`-visitor -no-listener`) | Keeps parity with existing compiler architecture. [VERIFIED: run.py + ANTLR docs] |

**Key insight:** Isolation succeeds only when output paths and process cwd are treated as explicit inputs, never inferred from repository-relative defaults.

## Common Pitfalls

### Pitfall 1: Partial import rewrite
**What goes wrong:** Vendor modules still import `src.*` or `build.*` root paths and silently bypass isolated copies.
**Why it happens:** Copy-only migration without import audit.
**How to avoid:** Enforce package-root import policy in `compiler_vendor` (`from ..utils...`, `from gsd.runner.build...` as final canonical form). [ASSUMED]
**Warning signs:** Tests pass locally but root `build/` becomes required or root `src/runtime` changes.

### Pitfall 2: Timeout budget drift across stages
**What goes wrong:** Different subprocess calls use unrelated timeout values.
**Why it happens:** Hardcoded per-step defaults.
**How to avoid:** Pass one request budget into assemble and run calls consistently. [VERIFIED: phase context timeout policy]
**Warning signs:** Same input sometimes returns timeout, sometimes runtime_error depending on stage order.

### Pitfall 3: Cleanup not guaranteed on error
**What goes wrong:** Temporary directories remain after subprocess failure/timeout.
**Why it happens:** Cleanup only on success path.
**How to avoid:** Context manager or `finally` cleanup guard. [CITED: https://docs.python.org/3/library/tempfile.html]
**Warning signs:** Temp root grows across repeated failed requests.

## Code Examples

### Safe subprocess contract
```python
# Source: https://docs.python.org/3/library/subprocess.html
result = subprocess.run(
    ["java", "-jar", "jasmin.jar", "TyC.j"],
    cwd=workspace,
    capture_output=True,
    text=True,
    timeout=timeout_seconds,
    shell=False,
)
```

### Build-time ANTLR generation pattern
```bash
# Source basis: D:/HK252/PPL/BTL/tyc-compiler/run.py
java -jar <antlr-jar> -Dlanguage=Python3 -visitor -no-listener -o gsd/runner/build src/grammar/TyC.g4
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Root compiler writes to `src/runtime` implicitly | Isolated runner requires explicit workspace output_dir | Introduced by GSD variant isolation requirements | Prevents root artifact leakage and enables multi-request isolation. [VERIFIED: WEBAPP spec + emitter code] |

**Deprecated/outdated:**
- Process-global cwd switching in server execution paths: acceptable in local test harness, not recommended for concurrent API worker paths. [VERIFIED: tests/utils.py] [ASSUMED]

## Open Questions

1. **Canonical import root for vendored modules**
   - What we know: vendor copy is required under `gsd/runner/compiler_vendor`. [VERIFIED: phase context]
   - What's unclear: whether final imports should be relative-only or absolute from `runner.*` package root.
   - Recommendation: lock one strategy in Phase-2 plan and add an import smoke test that fails on `src.` imports.

2. **ANTLR jar sourcing inside gsd**
   - What we know: root build uses `external/antlr-4.13.2-complete.jar`. [VERIFIED: run.py]
   - What's unclear: whether Phase 2 copies jar into `gsd/runner/runtime_assets` or fetches at build step.
   - Recommendation: prefer explicit copy/download step under `gsd/runner/` with deterministic path + checksum validation. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runner app/tests | ✓ | 3.12.10 | — |
| Java runtime (`java`) | Jasmin + JVM execution | ✓ | 23 | — |
| Java compiler (`javac`) | Build `io.class` from `io.java` | ✓ | 23 | Prebuild `io.class` in repo if compile unavailable |
| pytest | Phase-2 tests | ✓ | 9.0.2 | `python -m pytest` from venv |

**Missing dependencies with no fallback:**
- None found.

**Missing dependencies with fallback:**
- None found.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none — use direct `python -m pytest` |
| Quick run command | `PYTHONPATH=D:/HK252/PPL/BTL/tyc-compiler python -m pytest D:/HK252/PPL/BTL/tyc-compiler/gsd/runner/tests/test_health.py -q` |
| Full suite command | `PYTHONPATH=D:/HK252/PPL/BTL/tyc-compiler python -m pytest D:/HK252/PPL/BTL/tyc-compiler/gsd/runner/tests -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FR-03 | compile→assemble→run happy path in isolated workspace | integration | `python -m pytest gsd/runner/tests/test_phase2_pipeline_success.py -q` | ❌ Wave 0 |
| NFR-01 | no writes outside gsd during phase-2 flow | integration/isolation | `python -m pytest gsd/runner/tests/test_phase2_isolation.py -q` | ❌ Wave 0 |
| NFR-03 | timeout + cleanup on subprocess failure | integration | `python -m pytest gsd/runner/tests/test_phase2_workspace_cleanup.py -q` | ❌ Wave 0 |
| VR-01 | stdin success + timeout path covered | integration | `python -m pytest gsd/runner/tests/test_phase2_pipeline_cases.py -q` | ❌ Wave 0 |
| VR-04 | root `build/` and `src/runtime/` unchanged | integration | `python -m pytest gsd/runner/tests/test_phase2_isolation.py::test_no_root_artifacts -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest gsd/runner/tests/test_health.py -q`
- **Per wave merge:** `python -m pytest gsd/runner/tests -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `gsd/runner/tests/test_phase2_pipeline_success.py` — covers FR-03
- [ ] `gsd/runner/tests/test_phase2_workspace_cleanup.py` — covers NFR-03
- [ ] `gsd/runner/tests/test_phase2_isolation.py` — covers NFR-01/VR-04

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Public endpoint in this phase; auth deferred |
| V3 Session Management | no | Stateless request handling |
| V4 Access Control | yes | CORS allowlist + endpoint-level constraints from limits/config [VERIFIED: WEBAPP spec] |
| V5 Input Validation | yes | Pydantic request models + explicit byte limits [VERIFIED: gsd/runner/app/schemas.py + limits.py] |
| V6 Cryptography | no | No crypto introduced in phase 2 |

### Known Threat Patterns for Python subprocess runner

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Command injection | Tampering | `subprocess.run` with argument list + `shell=False` [CITED: https://docs.python.org/3/library/subprocess.html] |
| Resource exhaustion via infinite loops | Denial of Service | Per-request timeout + max concurrent runs + output truncation [VERIFIED: WEBAPP spec §12] |
| Cross-request data leakage | Information Disclosure | Unique per-request workspace + guaranteed cleanup [CITED: https://docs.python.org/3/library/tempfile.html] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Separate `runtime_workspace.py` boundary is optimal split for maintainability | Architecture Patterns | Medium: task split may need refactor later |
| A2 | Reusing one workspace across requests is likely to cause race/leak issues in API context | Anti-Patterns | Medium: if serialized single worker, risk is lower |
| A3 | Deterministic checksum validation for copied ANTLR jar should be added | Open Questions | Low: can still proceed without checksum |

## Sources

### Primary (HIGH confidence)
- Local repository sources via Read tool:
  - `D:/HK252/PPL/BTL/tyc-compiler/gsd/WEBAPP_SPEC.md`
  - `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/ROADMAP.md`
  - `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/REQUIREMENTS.md`
  - `D:/HK252/PPL/BTL/tyc-compiler/gsd/.planning/phases/2-CONTEXT.md`
  - `D:/HK252/PPL/BTL/tyc-compiler/src/codegen/emitter.py`
  - `D:/HK252/PPL/BTL/tyc-compiler/src/codegen/codegen.py`
  - `D:/HK252/PPL/BTL/tyc-compiler/tests/utils.py`
  - `D:/HK252/PPL/BTL/tyc-compiler/run.py`

### Secondary (MEDIUM confidence)
- Python subprocess documentation: https://docs.python.org/3/library/subprocess.html
- Python tempfile documentation: https://docs.python.org/3/library/tempfile.html
- ANTLR tool options (`-visitor`, `-no-listener`): https://chromium.googlesource.com/external/github.com/antlr/antlr4/%2B/15720d1e33d7e03b2ca22f65f9260cfefae46505/doc/tool-options.md

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified against local environment and current project files.
- Architecture: HIGH - driven by locked Phase-2 constraints and direct code inspection.
- Pitfalls: MEDIUM - some concurrency/isolation operational risks are inferred from common backend behavior.

**Research date:** 2026-05-07
**Valid until:** 2026-06-06
