# Security Review

## Scope
- Reviewed only `gstack/runner` and `gstack/frontend` against `gstack/WEBAPP_SPEC.md` security requirements.
- Focus: process execution safety, resource limits, API exposure, and isolation.

## Checks

### 1) Process execution safety
- `shell=False` subprocess execution is used for both assemble and run stages.
- Hard timeout is enforced for assemble/run and now includes explicit process-tree kill on timeout in `gstack/runner/app/runtime_workspace.py`.
- Timeout reproduction case (`while (1) {}`) now returns `status: timeout` instead of hanging.

### 2) Workspace isolation
- Runtime artifacts are generated per request in temp workspace under `gstack/runner/tmp` and cleaned in `__exit__`.
- Codegen output is directed into request workspace, not root runtime folders.

### 3) API guardrails
- Input limits are enforced in `gstack/runner/app/main.py` using `MAX_SOURCE_BYTES` and `MAX_STDIN_BYTES`.
- Output truncation is enforced in `gstack/runner/app/compiler_service.py` using `MAX_OUTPUT_BYTES`.
- Concurrency is bounded by semaphore (`MAX_CONCURRENT_RUNS`).
- CORS allowlist is configurable via `TYC_ALLOWED_ORIGINS`.

### 4) Error-contract safety
- Errors are stage-mapped and returned as structured diagnostics.
- Semantic errors preserve AST when requested.

## Findings
- Fixed high-impact issue: timeout case could hang because subprocess timeout was not reliably terminating the JVM process in this environment.
- No direct shell injection path found in current runner command construction.
- No out-of-scope write path found in reviewed variant code.

## Residual risks before public production launch
1. No auth/rate limiting layer yet (spec noted as follow-up).
2. Network egress policy for executed programs depends on container runtime configuration.
3. Observability is minimal (no request ID correlation yet).

## Verdict
- **Pass for assignment/demo scope** with current controls.
- **Needs hardening for internet-scale public usage**: add rate limit, stronger sandbox policy, and structured audit logs.
