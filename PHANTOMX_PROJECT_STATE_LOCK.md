# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-11-GOAL-LOCK-2.2
Status: LOCKED / ACTIVE MISSION BASELINE
Date: 2026-09-11

## MASTER GOAL
LIVE MARKET -> EXECUTABLE V2/V3 OPPORTUNITY -> ALL KNOWN/CONSERVATIVELY BOUNDED COSTS -> CONSERVATIVE NET PROFIT > $0.50 -> SAFE ATOMIC EXECUTION -> RECEIPT -> INDEPENDENT WALLET BALANCE RECONCILIATION -> REALIZED POSITIVE NET PnL.

Project completion is not established by continuous running, AI prediction, simulation, expected PnL, tests alone, or generated calldata. The final success criterion is live realized positive net PnL under the verified safety envelope.

## HARD RULES
- One active task at a time.
- Depth first.
- Evidence before confidence.
- Verification before integration.
- Integration before optimization.
- Simulation before execution.
- Receipt/balance evidence before realized-PnL claims.
- GOAL > SAFETY > GROUND EVIDENCE > MATHEMATICAL CORRECTNESS > CURRENT CODE > HISTORICAL DOCUMENTATION.
- Never knowingly authorize conservative non-positive economics.
- Never use opportunity pressure to bypass a hard gate.
- No secrets/private keys/seeds in the public repository.
- Every material change must have tests, evidence, rollback reference and state update.

## DYNAMIC-ONLY HOT PATH
No unjustified fixed economic assumption may survive in the final authorization path where live state or exact on-chain calculation can provide the value. This includes fixed loan size, fixed economic gas, fixed slippage, synthetic spread/multipliers, stale pool universes, first-two-venue shortcuts and generic fallback gas used as truth.

## CANONICAL HOT PATH
DISCOVER -> PIN SNAPSHOT -> VERIFY CHAIN/RPC -> VERIFY TOKENS/POOLS/VENUES -> ENUMERATE V2/V3 ROUTES -> EXECUTABLE QUOTES -> LIQUIDITY/PRICE IMPACT -> DYNAMIC LOAN SIZE -> EXACT INTENT -> EXACT GAS -> ALL COSTS -> MEV/RISK -> PROFIT CERTIFICATE (> $0.50) -> FINAL REQUOTE/STATE LOCK -> EXECUTOR IDENTITY/SECURITY -> ATOMIC EXECUTION -> RECEIPT -> BALANCE/PnL RECONCILIATION -> LEARNING -> CHECKPOINT -> LOOP.

## AI AUTHORITY
AI proposes. Deterministic verification decides. Executor executes.
AI may rank market regime, V2/V3, route, timing, size, gas-aware opportunity quality, liquidity/price impact, short-horizon forecast, MEV-risk probability, RPC quality and learning parameters. AI cannot override identity, route validity, exact gas, repayment, minOut/slippage, allowlists, signer/authentication, safety caps or final authorization.

## CURRENT REPOSITORY
Repository: manish91082-coder/flash-loan-ghost-hunter
Visibility: public
Current main SHA at this checkpoint: `754b1f82516424710b5f319c96de17e52ecc9750`

## P0-A DEPLOYED RUNTIME FINDING
The deployed Polygon executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` was compared through read-only multi-RPC evidence.

Deployment:
- tx: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- block: `93519165`
- chain ID: `137`

Decisive P0-A evidence:
- deployed runtime: `6528` bytes
- deployed runtime Keccak-256: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- current hardened executor is a separate source/runtime lineage and is not this deployed legacy artifact
- deployed owner matches recorded deployer
- deployment sender and created address match recorded evidence
- deployment receipt succeeded
- `DOMAIN_SEPARATOR()` and `paused()` revert on deployed legacy runtime
- no live transaction was signed or broadcast during identity work

## P0-A.1 LINEAGE RESOLUTION — COMPLETE
Historical source/build path was reproduced with ground evidence.

## P0-A.2 — INTERFACE FREEZE — COMPLETE
Canonical executor interface remains frozen as previously established.

## P0-A.2.1 — EXECUTOR ABI CONFORMANCE — GREEN
Fresh exact-head CI on `1d564954178ce598749fd11d7805f8d04840be5b` passed frozen ABI conformance and the two canonical Python interface tests. Optimized runtime measured `18,239` bytes.

Evidence:
- P0-A.2.1 run: `34516965619`
- job: `103004668586`
- `ExecutionIntent ABI: PASS`
- provider enum mapping: PASS
- swap enum mapping: PASS
- callback surface: PASS
- canonical interface tests: 2 passed, 0 failed

## P0-A.2.2 SEMANTIC HARDENING — IN PROGRESS
### P0-A.2.2.1 CALLBACK INTENT INTEGRITY BINDING — GREEN
Finding resolved: callbacks previously bound only to `activeExecutionId`, allowing a theoretical same-ID mutated callback payload. The hardened executor now stores `activeIntentHash = _intentStructHash(intent)` alongside `activeExecutionId` and requires full 16-field intent-hash equality in Aave, Balancer and Uniswap V3 callbacks. Signature is excluded from the struct hash exactly as required by the frozen EIP-712 schema. Active bindings are cleared after the provider call on successful completion.

### P0-A.2.2.2 CALLBACK INVOCATION COMPLETENESS — GREEN ON CERTIFIED HEAD
Finding resolved: `executeOpportunity()` now proves that the selected flash provider actually invoked its required callback. After each provider invocation it requires `activeCallbackConsumed`; callback entrypoints set it and reject a second callback.

Regression evidence on certified head `1d564954178ce598749fd11d7805f8d04840be5b`:
- P0-B security run: `34516965651`
- job: `103004669218`
- conclusion: success
- security suite: 8/8 passed
- callback matrix: 9/9 passed
- EIP712 cross-check: 2/2 passed
- semantic hardening: 10/10 passed
- callback invocation: 3/3 passed
- total: 32/32 tests passed, 0 failed, 0 skipped
- optimized compile on exact head: runtime `18,239` bytes; EIP-170 gate passed

Source-diff note:
- Commit `1d564954...` modifies only `contracts/PhantomX_Production_Executor.sol`, with 33 additions and 97 deletions because the file was reformatted/minified while isolating the V3 validation helper. Passing suites are not treated as proof of semantic equivalence; further source audit remains required before deployment authorization.

### P0-AUTO-0 AUTONOMOUS ENGINEERING CONTROL PLANE — VERIFYING
Implemented on main as a fail-closed, non-capital orchestration layer:
- `docs/automation/PHANTOMX_AUTONOMOUS_ENGINEERING_CONTROL_PLANE.md`
- `automation/phantomx_control_plane.json`
- `automation/PHANTOMX_AUTOMATION_STATE.json`
- `automation/validate_control_plane.py`
- `.github/workflows/phantomx-control-plane.yml`
- `.github/copilot-instructions.md`
- `docs/automation/P0-AUTO-0.1-CHECKPOINT.md`

The control plane enforces one atomic task, bounded repair attempts, explicit dependencies, evidence requirements, fail-closed behavior, and a hard prohibition on live capital authorization. Its CI workflow uses minimal read-only repository permissions. GitHub Actions supports explicit workflow/job permissions, so this layer intentionally requests only `contents: read`. citeturn0search0turn0search3

Current automation checkpoint:
- automation implementation head: `754b1f82516424710b5f319c96de17e52ecc9750`
- status: VERIFYING
- reason: exact-head GitHub Actions success evidence has not yet been observed through the connected GitHub status surface
- no claim of GREEN is made until that evidence exists

### NEXT ACTIVE ENGINEERING TASK AFTER AUTOMATION GREEN
`P0-A.2.2.3-A — Aave repayment lifecycle: realistic provider transfer/borrow path, callback execution, exact repayment pull, post-provider allowance cleanup, active-state cleanup, and adversarial reentrancy.`

## P0-A.2.2.3 PROVIDER AUTHENTICITY / REPAYMENT SEMANTICS — BLOCKED BY AUTOMATION BOOTSTRAP VERIFICATION
The underlying semantic mission remains active. No live deployment/capital work is permitted. The current task graph is machine-readable and must advance only after the automation bootstrap is GREEN.

## DEPLOYMENT / CAPITAL GATE
Live deployment and live capital execution remain BLOCKED.

## CONTINUITY
On reconnect: load this state lock -> verify exact main SHA -> load `automation/PHANTOMX_AUTOMATION_STATE.json` and `automation/phantomx_control_plane.json` -> verify the control-plane workflow evidence -> resume the single active task. Never restart the project and never replay completed work.

END STATE LOCK
