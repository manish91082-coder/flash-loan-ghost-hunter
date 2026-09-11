# PHANTOMX NEW-CHAT BOOTSTRAP / CROSS-THREAD CONTINUITY

Status: CANONICAL CONTINUITY HANDSHAKE
Purpose: Resume PHANTOMX work in a fresh ChatGPT thread without relying on the previous chat transcript.

## 1. SOURCE OF TRUTH
GitHub repository:
`manish91082-coder/flash-loan-ghost-hunter`

The repository is the durable project memory and execution source of truth. A chat thread is a working session, not the canonical project state.

At the start of every new chat, read the CURRENT default-branch HEAD and then load, in this order:
1. `PHANTOMX_PROJECT_STATE_LOCK.md`
2. `automation/PHANTOMX_AUTOMATION_STATE.json`
3. `automation/phantomx_control_plane.json`
4. relevant current PRs, Issues, workflow runs, and evidence artifacts
5. the latest task-specific code/tests only after the state is reconciled

Never rely on an old SHA, old chat summary, cached status, stale PR label, or expected future result as current truth.

## 2. MASTER MISSION
The mission is fixed:

LIVE MARKET
-> EXECUTABLE V2/V3 OPPORTUNITY
-> ALL KNOWN/CONSERVATIVELY BOUNDED COSTS
-> CONSERVATIVE NET PROFIT > $0.50
-> SAFE ATOMIC EXECUTION
-> RECEIPT
-> INDEPENDENT WALLET BALANCE RECONCILIATION
-> REALIZED POSITIVE NET PnL

No intermediate milestone is final success.

## 3. NON-NEGOTIABLE OPERATING PROTOCOL
- Evidence before confidence.
- Verification before integration.
- Integration before optimization.
- Simulation before live execution.
- Receipt + independent balance evidence before realized-PnL claims.
- Exactly ONE active engineering task at a time.
- Fail closed on uncertainty or conflicting state.
- Preserve goal-relevant work; do not replay proven work without a regression reason.
- Never weaken a production invariant merely to make a test pass.
- AI proposes; deterministic verification decides; executor executes.
- No secrets, private keys, seed phrases, signing material, or credentials in repository/chat artifacts.
- Live capital remains BLOCKED until the mission-control gates independently prove authorization.

## 4. FREEZE / CHANGE CONTROL
Treat every verified repository state as a checkpoint.

Before a material change:
- identify the single task and acceptance criteria;
- record the current branch/HEAD from GitHub;
- inspect the relevant failure/evidence;
- make the smallest correct change;
- add or update deterministic regression coverage;
- run targeted checks, then required regressions;
- preserve the prior SHA as rollback/reference evidence;
- update authoritative state only after evidence supports the transition.

Never silently rewrite historical evidence. Historical failures stay historical; current-head verdicts must be head-aware.

## 5. AUTO-SAVE / CHECKPOINT RULE
Every material engineering step must leave durable evidence in GitHub through commits, tests, workflow results, PR state, or explicit state/evidence artifacts.

The chat does NOT need to retain giant logs. Summarize only:
TASK / STATUS / ROOT CAUSE / CHANGE / EVIDENCE / NEXT SINGLE TASK.

When a chat approaches platform length limits, stop expanding the transcript and continue from this file in a fresh chat.

## 6. CROSS-THREAD HANDSHAKE
A new chat must begin by treating itself as a continuation, not a new project.

Use this exact bootstrap message:

`Continue PHANTOMX from GitHub canonical state. Read PHANTOMX_NEW_CHAT_BOOTSTRAP.md first, then PHANTOMX_PROJECT_STATE_LOCK.md, automation/PHANTOMX_AUTOMATION_STATE.json, automation/phantomx_control_plane.json, current main HEAD, active PRs and latest CI/evidence. Reconcile state before acting. Maintain one active task, preserve all frozen protocols, fail closed, keep live capital BLOCKED, and proceed with the single highest-value goal-relevant action without repeating already-proven work.`

After the bootstrap, the assistant should inspect current GitHub truth itself. Do not paste the previous conversation or giant CI logs unless a specific artifact is unavailable in GitHub.

## 7. CURRENT-STATE RULE
This file deliberately does NOT pin the live task SHA. Current task, gate, branch, PR, CI status, and live-capital authorization must always be recovered from the current GitHub state files and live workflow evidence.

A historical SHA may be cited only as evidence of a completed checkpoint, never as the current state unless freshly verified.

## 8. SAFETY / CAPITAL RULE
No chat continuity mechanism authorizes capital.

Tests, simulation, expected PnL, generated calldata, uptime, AI confidence, or deployment labels are not proof of realized profit.

Live authorization requires the independent mission-control gates and final receipt + wallet reconciliation evidence defined by the repository's canonical protocol.

## 9. END-OF-THREAD HANDOFF
When a thread is ending because of length, summarize only the latest durable facts and commit/evidence references. Do not attempt to transfer the whole conversation.

Preferred handoff format:
`PHANTOMX CONTINUATION: GitHub is canonical. Read PHANTOMX_NEW_CHAT_BOOTSTRAP.md and current state files. Resume the current atomic task from verified evidence. Do not assume any stale status. Keep live capital BLOCKED.`

## 10. IMPORTANT LIMITATION
A fresh chat cannot inherit the full old transcript automatically merely because this file exists. The reliable solution is durable externalized state + a tiny bootstrap message. This prevents protocol/state drift without depending on thread memory.
