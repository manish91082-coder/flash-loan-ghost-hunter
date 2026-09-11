# PHANTOMX Automation

This directory is the deterministic control layer for the project-wide autonomous engineering loop.

## Entry points

- `phantomx_control_plane.json`: machine-readable mission state and atomic task graph.
- `validate_control_plane.py`: fail-closed validator used by GitHub Actions.

## Contract

The automation layer may orchestrate engineering work, tests, evidence collection, and task progression. It must never authorize live capital merely because an engineering task is green.

## Expected future extensions

1. Evidence collector for workflow runs/artifacts.
2. Gate evaluator for P0/P1 acceptance criteria.
3. Atomic task issuer for GitHub Issues/PRs.
4. Bounded repair loop with forensic failure classification.
5. Checkpoint writer that updates state only after evidence is verified.
6. Optional GitHub-hosted coding-agent integration when an explicitly enabled agent is available.

Any extension must preserve fail-closed behavior and the master goal.
