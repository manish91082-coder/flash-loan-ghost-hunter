# PHANTOMX Agent Handoff Protocol

This file is the canonical handoff contract for any future coding agent, including GitHub-hosted agents.

## Required startup sequence
1. Read `PHANTOMX_PROJECT_STATE_LOCK.md`.
2. Read `automation/PHANTOMX_AUTOMATION_STATE.json`.
3. Read `automation/phantomx_control_plane.json`.
4. Verify the repository HEAD against the state checkpoint.
5. Identify exactly one active task.
6. Inspect only the task's declared scope plus the minimum dependency context required for correctness.

## Required completion sequence
1. Implement the smallest goal-aligned change.
2. Add/update deterministic tests.
3. Add adversarial tests for security-sensitive changes.
4. Run the required CI workflows.
5. Inspect exact logs and artifacts.
6. Record commit SHA, workflow IDs, job IDs, test counts, and verdict.
7. Update the checkpoint.
8. Do not unlock a dependent task until the current task is GREEN.

## Failure protocol
- Preserve the failing state and evidence.
- Diagnose before changing code.
- Automatic repair is capped at three evidence-driven iterations.
- Repeated or ambiguous failure becomes BLOCKED.
- Never suppress, weaken, delete, or bypass a failing security/economic test merely to obtain GREEN.

## Goal boundary
The final project goal is realized positive net PnL on live market execution under the verified safety envelope. Engineering automation is successful only when it advances that goal without violating safety or evidence requirements.
