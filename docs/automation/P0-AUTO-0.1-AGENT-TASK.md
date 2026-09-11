# P0-AUTO-0.1 Agent Task

This document is the exact atomic task contract for the first autonomous engineering loop.

## Objective
Verify the newly installed PHANTOMX control plane against the exact repository state, then leave the repository in a deterministic GREEN or BLOCKED state with evidence. Do not modify production executor behavior in this task.

## Required checks
- Validate `automation/phantomx_control_plane.json`.
- Run `automation/validate_control_plane.py`.
- Verify the control-plane GitHub Actions workflow executes on the exact head.
- Inspect the workflow log and artifact.
- Confirm the state lock, automation state, task graph, and handoff protocol are mutually consistent.
- Confirm no secret material is present in the new automation files.
- Do not enable live capital, deployment, or transaction broadcast.

## Acceptance
GREEN only when exact-head CI and validator evidence are present and consistent.

## Failure
Preserve all evidence, diagnose the first failure, and mark BLOCKED. Do not weaken the validator or bypass a failing check.

## Next task after GREEN
`P0-A.2.2.3-A — Aave repayment lifecycle`
