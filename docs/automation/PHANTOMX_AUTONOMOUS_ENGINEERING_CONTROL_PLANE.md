# PHANTOMX Autonomous Engineering Control Plane

Version: AEC-1.0
Status: ACTIVE / FAIL-CLOSED
Mission: drive the complete PHANTOMX implementation roadmap toward the master goal without losing state, evidence, safety, or continuity.

## Master goal
LIVE MARKET -> EXECUTABLE V2/V3 OPPORTUNITY -> ALL KNOWN/CONSERVATIVELY BOUNDED COSTS -> CONSERVATIVE NET PROFIT > $0.50 -> SAFE ATOMIC EXECUTION -> RECEIPT -> INDEPENDENT WALLET BALANCE RECONCILIATION -> REALIZED POSITIVE NET PnL.

## Operating doctrine
1. One atomic task at a time.
2. Goal > safety > ground evidence > mathematical correctness > current code > historical documentation.
3. Evidence before confidence; verification before integration; integration before optimization; simulation before execution; receipt/balance evidence before realized-PnL claims.
4. Never advance a dependent gate while an upstream P0/P1 blocker remains unresolved.
5. AI proposes. Deterministic verification decides. Executor executes.
6. No live-capital action is authorized by this control plane. Production execution remains separately gated by the mission-control L1-L8 sequence.
7. Every material change requires implementation evidence, tests, CI evidence, rollback reference, and state update.
8. No secrets, private keys, seeds, or credentials may be written to the repository or artifacts.
9. Fail closed on missing, stale, contradictory, or unverifiable evidence.
10. Do not claim completion from tests, simulation, expected PnL, generated calldata, or continuous running alone.

## State machine
A task may be exactly one of:
- LOCKED: dependency not satisfied.
- READY: dependency satisfied and task may start.
- IN_PROGRESS: exactly one task is actively being worked.
- VERIFYING: implementation exists and required evidence is being collected.
- GREEN: all acceptance criteria and evidence requirements pass.
- FAILED: implementation/test/evidence failure requires diagnosis.
- BLOCKED: external dependency, missing evidence, infrastructure, security, or policy blocker.

Only GREEN unlocks dependent tasks.

## Atomic task contract
Every task record must define:
- task_id
- phase / subphase / gate
- objective tied directly to the master goal
- scope and explicit non-scope
- prerequisites
- required implementation changes
- deterministic tests
- adversarial tests where applicable
- acceptance criteria
- evidence artifacts
- rollback reference
- maximum repair attempts
- next-task dependencies

## Automation loop
READ STATE -> VERIFY HEAD -> SELECT ONE READY TASK -> CREATE/USE ISOLATED BRANCH -> IMPLEMENT -> RUN LOCAL/CI VALIDATION -> COLLECT EVIDENCE -> CLASSIFY RESULT -> REPAIR ONLY WITHIN ATTEMPT BUDGET -> REVERIFY -> CHECKPOINT -> UNLOCK NEXT TASK.

## Repair policy
- Maximum automatic repair iterations per atomic task: 3.
- A repair iteration must address a concrete observed failure.
- No blind retries that change code without a new diagnosis.
- Repeated identical failures become BLOCKED and require forensic escalation.
- Security, authorization, economic, or evidence regressions are never auto-overridden.

## Merge policy
The controller may prepare branches and PRs. Merge is permitted only when the required CI checks and task gate evidence are GREEN and no higher-priority blocker exists. Live deployment/capital remains outside autonomous merge authority.

## Evidence bundle
Each completed task should emit a machine-readable evidence record containing at minimum:
- task_id
- source commit SHA
- parent SHA
- changed paths
- workflow run IDs
- job IDs
- test counts
- failure counts
- compiler/toolchain identity where applicable
- artifact references
- verdict
- timestamp
- rollback commit

## Phase orchestration
The controller treats the project as a dependency graph, not a blind 16-step linear checklist. Macro phases may contain subphases, gates, verification loops, and multiple atomic tasks. The controller must select the highest-priority unresolved task whose prerequisites are GREEN.

Canonical macro sequence:
0 Foundation / mission-control / certification
1 Ecosystem intelligence
2 Connectivity / RPC
3 Protocol / DEX intelligence
4 Token / asset intelligence
5 Pool / liquidity intelligence
6 Flash-loan infrastructure
7 Knowledge fabric / graph
8 Live market intelligence
9 Opportunity discovery
10 Economics / profit truth
11 Risk / MEV / safety
12 Simulation / adversarial validation
13 Decision / AI brain
14 Controlled execution
15 Outcome / realized PnL
16 Learning / continuous evolution

The numbering is an orchestration spine, not permission to skip dependencies. Goal-driven gap discovery may add atomic tasks inside any phase.

## Current boot task
P0-AUTO-0.1 — establish and verify the control-plane state machine, task graph, evidence schema, and CI entrypoint. This task must remain non-capital and fail-closed.

## Safety boundary
The control plane must never:
- broadcast a transaction with project capital;
- expose or request private keys/seeds;
- bypass executor authorization gates;
- treat expected PnL as realized PnL;
- replace exact live gas/economic verification with a generic fallback;
- authorize a conservative non-positive opportunity;
- silently rewrite or delete historical evidence.

## Continuity
At every checkpoint, persist enough state for a fresh agent/session to resume from the exact task and exact evidence boundary without replaying completed work.
