# Phase 6 PLAN — Tests, verification hardening, retrospective

## Scope
Phase 6 only. Allowed write scope: `gsd/**`.

### In scope
- Re-run final verification command set.
- Produce `gsd/docs/verification.md` with evidence matrix.
- Produce `gsd/docs/retrospective.md` with workflow assessment.
- Add/update phase artifacts under `gsd/.planning/phases/6/`.

### Out of scope
- New product features.
- Remote deploy/push/PR actions.

## Task breakdown

### Task 1 — Execute final verification command set
- Run frontend build/tests.
- Run relevant runner API/isolation tests.
- Capture pass/fail evidence and command outputs.

### Task 2 — Write final verification report
- Create `gsd/docs/verification.md`.
- Map acceptance criteria to evidence and verdict.
- Highlight any uncovered edge cases.

### Task 3 — Write retrospective report
- Create `gsd/docs/retrospective.md`.
- Summarize what worked in the GSD loop.
- Summarize frictions and concrete improvements for next cycle.

### Task 4 — Phase artifacts and state updates
- Write `6-1-SUMMARY.md`, `6-UAT.md`, `6-SHIP.md`.
- Update `STATE.md` to milestone-closure status.

## Verification commands (Phase 6)
- `cd gsd/frontend && npm run build && npm run test`
- `PYTHONPATH=gsd python -m pytest gsd/runner/tests -q`

## Exit criteria
- Final verification report written with explicit PASS/FAIL for acceptance criteria.
- Retrospective report written with actionable recommendations.
- Phase 6 local ship artifacts complete under `gsd/.planning/phases/6/`.
