# Retrospective (GStack Variant)

## What went well
1. Isolated implementation target (`gstack/`) kept scope clear and avoided accidental root-coupling.
2. Reusing an existing isolated runner/frontend baseline reduced implementation risk.
3. Contract-first QA (status/stage/AST fields) made backend verification fast and objective.

## What went wrong
1. Timeout behavior looked correct in code but failed in real runtime: infinite-loop program caused request hang.
2. Browser QA flow via skill tooling added friction, so API-level verification became the primary signal.
3. Multi-stage workflow docs add overhead when many artifacts are mandatory.

## Defect prevented by workflow
- Review/QA stage explicitly included timeout case, which exposed a production-impacting hang before ship.
- Fix was applied in runtime executor by enforcing process-tree termination on timeout.

## GStack workflow assessment

### Clarity
- Strong for stage-by-stage deliverables (`design`, `review`, `qa`, `deployment`, `retro`).
- Slightly heavy for small/medium changes because each phase requires an artifact.

### Review quality
- Good at forcing explicit security and contract checks.
- Works best when combined with concrete executable probes, not only static review.

### Implementation friction
- Main friction was operational: skill preambles and orchestration overhead can interrupt direct execution flow.
- Once work switched to direct tooling inside `gstack/`, throughput improved.

## Comparison with other variants (high-level)
- **Vs GSD**: GStack gives stronger explicit phase artifacts, but higher process overhead.
- **Vs OpenSpec**: GStack is more execution-oriented with practical QA loops; OpenSpec tends to be lighter on execution rigor unless enforced.

## Next iteration improvements
1. Add a dedicated timeout regression test that executes real infinite-loop source through API path.
2. Add lightweight rate-limit middleware for runner.
3. Add request IDs in API logs to simplify cross-step tracing.
