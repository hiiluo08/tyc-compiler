# Retrospective: tyc-web-compiler

Date: 2026-05-08

## 1) OpenSpec/OPSX impact on clarity

OpenSpec artifacts improved clarity in this brownfield task by forcing explicit intent/scope before implementation:
- `proposal.md` locked split architecture (Vercel frontend + external runner).
- Delta spec made error/AST/stdin/timeout behavior testable.
- `design.md` captured isolation-critical decision: vendored compiler + temp workspace output.
- `tasks.md` enabled continuous apply/verify progress without phase-gate rigidity.

## 2) Strengths observed

- Strong traceability from product contract (`openspec/WEBAPP_SPEC.md`) to implementation and tests.
- Isolation rule stayed enforceable because artifact boundaries were explicit from start.
- Requirement-level scenarios translated directly into backend API tests.

## 3) Weaknesses / friction

- Brownfield vendoring adds overhead (copy + adapt codegen/emitter path behavior).
- Timeout behavior on Windows/JVM required extra runtime engineering (process-tree termination).
- Manual sync/archive steps can drift if CLI automation is unavailable or unsafe-scoped.

## 4) Lessons learned

1. For public code execution, timeout/process control details should be designed as first-class requirements, not deferred.
2. In strict-isolation workflows, explicitly modeling output directories in design prevents accidental writes to legacy runtime paths.
3. Delta specs are most effective when scenarios map 1:1 to API tests.

## 5) Comparison with GSD / GStack

- Compared to GSD: OpenSpec here felt lighter and more contract-driven; less orchestration overhead for a single focused change.
- Compared to GStack staged workflows: this approach gave better local control under isolation constraints, but required more manual discipline for verify/archive.
- Net result for this project: OpenSpec variant was effective for brownfield web-compiler integration where strict file-scope isolation mattered most.