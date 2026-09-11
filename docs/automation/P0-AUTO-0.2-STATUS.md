# P0-AUTO-0.2 Status

## Task
`P0-AUTO-0.2 — Reconcile autonomous state and head-aware health reporting`

## Objective
Remove stale runtime SHA pins, align the canonical mission lock with machine state, isolate historical workflow failures from current-head failures, and add a deterministic fail-closed mission-state validation gate before autonomous task progression.

## Changes in this task
- `automation/PHANTOMX_AUTOMATION_STATE.json`
  - schema `AEC-1.1`
  - current/automation heads are runtime-derived rather than statically pinned
  - adds explicit state authority and repair-attempt field
  - extends Aave acceptance requirements with short-pull/noncompliant-provider evidence
- `PHANTOMX_PROJECT_STATE_LOCK.md`
  - converted from stale current-head/status assertions into a policy lock plus runtime-derived state contract
  - current task explicitly reflects the active P0-AUTO-0.2 prerequisite
- `automation/phantomx_control_plane.json`
  - schema `AEC-1.1`
  - adds P0-AUTO-0.2 as an explicit prerequisite task
  - blocks Aave until automation truth is reconciled
- `automation/phantomx_status_collector.py`
  - compares workflow failures against runtime HEAD
  - reports historical failures separately
  - surfaces missing/drifted workflow names
  - fails the engineering verdict on state inconsistency
- `automation/validate_mission_state.py`
  - validates schema, single-task invariants, state/graph agreement, runtime-derived heads, and hard capital block
- `.github/workflows/phantomx-mission-state-validation.yml`
  - scheduled and change-triggered fail-closed validation

## Safety boundary
This task performs repository engineering and reporting only. It does not deploy contracts, sign transactions, broadcast live transactions, access secrets, or authorize live capital.

## Required evidence for GREEN
1. Mission state validator succeeds on exact PR/main HEAD.
2. Control-plane/state schema validation succeeds.
3. Live-status workflow succeeds without historical-failure contamination of current verdicts.
4. Workflow-name drift is either absent or explicitly surfaced.
5. Live capital remains blocked.

## Next task after GREEN
`P0-A.2.2.3-A — Aave repayment lifecycle`
