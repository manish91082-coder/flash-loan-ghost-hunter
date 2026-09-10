# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-10-GOAL-LOCK-2.0
Status: LOCKED / ACTIVE MISSION BASELINE
Date: 2026-09-10

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
Current main SHA at this checkpoint: `97f6f61ca75905a25662253658e36b396819e4ea`

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
Frozen v1 executor ABI was compiled and checked in CI; optimized compile/EIP-170 and prior executor security/callback/EIP712 evidence were green before semantic hardening.

## P0-A.2.2 SEMANTIC HARDENING — IN PROGRESS
### P0-A.2.2.1 CALLBACK INTENT INTEGRITY BINDING — GREEN
Finding resolved: callbacks previously bound only to `activeExecutionId`, allowing a theoretical same-ID mutated callback payload. The hardened executor now stores `activeIntentHash = _intentStructHash(intent)` alongside `activeExecutionId` and requires full 16-field intent-hash equality in Aave, Balancer and Uniswap V3 callbacks. Signature is excluded from the struct hash exactly as required by the frozen EIP-712 schema. Active bindings are cleared after the provider call on successful completion.

Regression evidence:
- `test/PhantomXExecutorSemanticHardening.t.sol` includes malicious Aave, Balancer and Uniswap V3 mocks that mutate `routerA` while retaining the original executionId/provider.
- First test attempt failed because the mock interface omitted Balancer/V3 callback declarations. This was a test-harness defect, not executor logic failure.
- Fix commit: `b499250cce95cae5cb565d78f9ec03502f108650`.
- Fresh P0-B security run: `34513582843`.
- Head SHA: `b499250cce95cae5cb565d78f9ec03502f108650`.
- Final job: `102993406909`.
- Conclusion: `success`.
- All required suites, including the new semantic-hardening suite, executed successfully.

CI observability finding also resolved:
- Earlier `ci-failure-alert` failure was caused by `gh` being invoked without explicit repository targeting outside a git checkout.
- Commit `e3acd863eaab6db97a5e6ac33a22df15714b4c95` supplied explicit `--repo ${GITHUB_REPOSITORY}` targeting.

Live market probe evidence remains separate from this semantic gate. A prior read-only Polygon quote probe succeeded at block `93572001`, while its historical compiler-install substep failed because the runner could not resolve `solc-bin.ethereum.org`. No transaction was broadcast.

### NEXT ACTIVE TASK
`P0-A.2.2.2 — Flash-provider callback semantic audit: prove provider authenticity, callback initiator/recipient semantics, UniV3 single-asset flash/fee accounting, Balancer callback shape/repayment semantics, Aave callback binding, active-intent lifecycle, and nested/reentrancy behavior.`

This task must finish with implementation changes/tests/evidence as required before any V2/V3 route-integration authorization.

## DEPLOYMENT / CAPITAL GATE
Live deployment and live capital execution remain BLOCKED.

## CONTINUITY
On reconnect: load this state lock -> verify current main SHA -> inspect the frozen interface, production executor and active semantic tests -> resume exactly at P0-A.2.2.2. Never restart the project.

END STATE LOCK
