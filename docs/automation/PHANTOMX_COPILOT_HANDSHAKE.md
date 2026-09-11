# PHANTOMX Copilot <-> GitHub <-> Controller Handshake

## Purpose
Give the coding agent one stable, repository-native contract so the user does not need to repeatedly restate tasks.

## Roles
- Copilot: inspect, implement, test, diagnose, create focused PRs, and publish evidence-backed handoff data.
- GitHub Actions: deterministic compile/test/security/evidence execution.
- PHANTOMX control plane: state, dependency, gate, and progression authority.
- Human: only handle credentials/permissions/approvals that cannot be performed by repository automation.

## Required handoff
Every material PR must include a machine-readable status block in the PR body or a generated artifact:

```text
PHANTOMX-HANDOFF
TASK_ID=<id>
STATUS=<GREEN|RED|BLOCKED>
BASE_SHA=<sha>
HEAD_SHA=<sha>
TESTS_PASSED=<n>
TESTS_FAILED=<n>
CI_RUNS=<comma-separated ids>
BLOCKERS=<none or concise list>
NEXT_TASK=<id or STOP>
LIVE_CAPITAL=BLOCKED
```

The controller reads this information only as evidence to correlate with actual CI results. It never trusts agent text alone.

## Continuation
When a task is GREEN and all required evidence is present, the next task must be selected from `automation/phantomx_control_plane.json`. Do not ask the user for a next-task prompt unless an explicit human-only permission/credential/approval is required.

## Human-only interruptions
Ask the user only for:
- a required secret/credential that the agent cannot access;
- an unavoidable GitHub/Copilot approval or permission action;
- an external legal/financial/operational authorization that cannot be automated.

Never ask for user intervention merely to choose the next engineering task when the dependency graph already determines it.
