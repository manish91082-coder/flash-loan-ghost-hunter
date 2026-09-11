# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-12-AUTONOMY-1.3
Status: LOCKED / ACTIVE MISSION BASELINE
Date: 2026-09-12

## MASTER GOAL
LIVE MARKET -> EXECUTABLE V2/V3 OPPORTUNITY -> ALL KNOWN/CONSERVATIVELY BOUNDED COSTS -> CONSERVATIVE NET PROFIT > $0.50 -> SAFE ATOMIC EXECUTION -> RECEIPT -> INDEPENDENT WALLET BALANCE RECONCILIATION -> REALIZED POSITIVE NET PnL.

The final success criterion is independently evidenced live realized positive net PnL under the verified safety envelope. Tests, simulation, AI prediction, generated calldata, expected PnL, or continuous uptime are not sufficient proof.

## HARD RULES
- One active engineering task at a time.
- Evidence before confidence.
- Verification before integration.
- Integration before optimization.
- Simulation before live execution.
- Receipt and independent balance evidence before realized-PnL claims.
- Never knowingly authorize conservative non-positive economics.
- Never bypass a hard safety/economic gate because an opportunity appears time-sensitive.
- No secrets, private keys, or seed material in repository history.
- Every material change must have deterministic validation, evidence, rollback reference, and state update.
- Engineering automation is non-capital and must never broadcast or authorize a live-capital transaction.

## DYNAMIC-ONLY HOT PATH
Do not preserve unjustified fixed economic assumptions where exact live/on-chain values are available. This includes fixed loan size, fixed economic gas, fixed slippage, synthetic spread/multipliers, stale pool universes, first-two-venue shortcuts, or generic fallback gas used as economic truth.

## CANONICAL HOT PATH
DISCOVER -> PIN SNAPSHOT -> VERIFY CHAIN/RPC -> VERIFY TOKENS/POOLS/VENUES -> ENUMERATE V2/V3 ROUTES -> EXECUTABLE QUOTES -> LIQUIDITY/PRICE IMPACT -> DYNAMIC LOAN SIZE -> EXACT INTENT -> EXACT GAS -> ALL COSTS -> MEV/RISK -> PROFIT CERTIFICATE (> $0.50) -> FINAL REQUOTE/STATE LOCK -> EXECUTOR IDENTITY/SECURITY -> ATOMIC EXECUTION -> RECEIPT -> BALANCE/PnL RECONCILIATION -> LEARNING -> CHECKPOINT -> LOOP.

## AI AUTHORITY
AI proposes. Deterministic verification decides. Executor executes.
AI may rank market regime, V2/V3, route, timing, size, gas-aware opportunity quality, liquidity/price impact, short-horizon forecast, MEV-risk probability, RPC quality and learning parameters. AI cannot override identity, route validity, exact gas, repayment, minOut/slippage, allowlists, signer/authentication, safety caps, or final authorization.

## CURRENT MACHINE STATE AUTHORITY
Current live state is runtime-derived from the GitHub default branch HEAD plus `automation/PHANTOMX_AUTOMATION_STATE.json` and `automation/phantomx_control_plane.json`.
Do not pin the current repository HEAD inside this policy lock. A pinned SHA here is evidence of a historical checkpoint only, not the live current state.
If state files and current HEAD disagree on authoritative task state, automation must fail closed and mark the state STALE until reconciled.

## CURRENT ENGINEERING GATE
- Current task: `P0-A.2.2.3-B — Balancer repayment semantics`
- Gate: `P0-A.2.2.3`
- Controller: `IN_PROGRESS`
- Live capital: `BLOCKED`
- Next dependency after GREEN: `P0-A.2.2.3-C`
- Automatic repair budget: 3 evidence-driven attempts per atomic task

## VERIFIED PRIOR GATE
### P0-A.2.2.3-A AAVE REPAYMENT LIFECYCLE — GREEN
PR #11 was merged to `main` as `98fd53a362911c1900602a001c1adda27df68a1a` after current-head verification showed successful P0-B Security, P0-B Compile, P0-A.2.1 Conformance, and Mission State Validation. Acceptance covered exact repayment approval/pull, allowance cleanup, post-provider balance reconciliation, short-pull rejection, and adversarial reentrancy.

### P0-A.2.2 SEMANTIC HARDENING
P0-A.2.2.1 callback intent integrity binding is GREEN on certified evidence.
P0-A.2.2.2 callback invocation completeness is GREEN on certified evidence.

## P0-A.2.2.3-B BALANCER REPAYMENT SEMANTICS — ACTIVE
Required evidence:
- Balancer callback/provider binding
- exact callback shape and one-asset binding
- borrowed asset receipt
- exact repayment transfer
- balance invariant before repayment
- active execution cleanup
- adversarial malformed callback semantics
- adversarial reentrancy
- relevant P0-B regression

## LIVE MARKET / ECONOMIC PROOF
Block-pinned live reads exist, but executable opportunity certification, exact executor-path gas, conservative all-cost profit certification, receipt evidence, independent wallet reconciliation, and realized positive PnL remain unproven.

## AUTOMATION BASELINE
Operational components include deterministic control-plane validation, live-status collection, workflow compilation validation, Copilot auth smoke testing, issue/artifact reporting, and event-driven/scheduled status triggers.
The Mission Driver source exists as an agentic-workflow definition but must have a verified compiled operational workflow before it is treated as an autonomous worker.

## CONTINUITY / RESUME PROTOCOL
On reconnect:
1. Read current GitHub default-branch HEAD.
2. Read `automation/PHANTOMX_AUTOMATION_STATE.json`.
3. Read `automation/phantomx_control_plane.json`.
4. Validate state consistency and current task prerequisites.
5. Inspect latest relevant workflow conclusions and evidence.
6. Resume exactly one eligible atomic task.
7. Never replay completed GREEN work and never declare GREEN without current evidence.

END STATE LOCK
