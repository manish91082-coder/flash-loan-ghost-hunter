# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-10-GOAL-LOCK-1.8
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
Checkpoint parent main SHA: `0c1798fc51307769252357fa1234cc6ebf3e65e6`
State-lock update creates the next checkpoint commit from that parent.

## P0-A DEPLOYED RUNTIME FINDING
The deployed Polygon executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` was compared through read-only multi-RPC evidence.

Deployment:
- tx: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- block: `93519165`
- chain ID: `137`

Decisive P0-A evidence:
- deployed runtime: `6528` bytes
- deployed runtime Keccak-256: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- current hardened `PhantomX_Production_Executor` previously measured: `14665` bytes
- current hardened runtime Keccak previously recorded: `0xef0fa19dd4ae8b810b873485137372c45c50a4ac3ed68311e95ed8c747de2660`
- runtime mismatch with legacy deployed artifact
- deployed owner matches recorded deployer
- deployment sender and created address match recorded evidence
- deployment receipt succeeded
- `DOMAIN_SEPARATOR()` and `paused()` revert on deployed legacy runtime
- no live transaction was signed or broadcast during identity work

## P0-A.1 LINEAGE RESOLUTION — COMPLETE
Historical source/build path was reproduced with ground evidence.

Source:
`flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol`

Historical deployer path:
`live_mainnet_deployer.py` -> `solcx.compile_source(source, output_values=['abi','bin'], solc_version='0.8.20')` with no explicit optimizer setting.

Observed exact reproduction:
- workflow: `PHANTOMX P0-A.1 Executor Lineage`
- run: `34507813800`
- job: `reproduce-historical-build`
- job ID: `102974218167`
- conclusion: `success`
- py-solc-x: `2.0.5`
- solc binary: `0.8.20`
- compile API: `py-solc-x compile_source`
- optimizer explicitly configured: `false`
- viaIR explicitly configured: `false`
- reproduced runtime: `6528` bytes
- reproduced creation bytecode: `8233` bytes
- reproduced runtime Keccak: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- deployed runtime Keccak: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- exact runtime match: `true`
- evidence artifact: `10164530653`

## CAPABILITY DECISION
The deployed runtime is exactly the historical `PhantomXMVP` lineage, but that artifact is archival/evidence only and is not production-authorized for the master mission because it contains fixed market/provider/token assumptions and lacks the required generalized hardened execution model.

Therefore unrestricted live execution remains blocked.

## P0-A.2 — INTERFACE FREEZE CHECKPOINT
Canonical executor interface is frozen before semantic implementation changes.

Frozen entry point:
`executeOpportunity(ExecutionIntent intent)`

Frozen ordered intent fields:
`executionId, providerType, providerAddress, tokenBorrow, amountBorrow, swap1Type, routerA, pathA, minAmountOut1, swap2Type, routerB, pathB, minAmountOutFinal, minimumOnChainSurplus, maximumGasLimit, deadline, signature`

Frozen provider enums:
`AAVE=0, UNISWAP_V3_FLASH=1, BALANCER=2`

Frozen swap enums:
`V2=0, V3=1`

Frozen route model:
- two authorization legs;
- each leg may be multi-hop;
- V2 path = ABI encoded `address[]`;
- V3 path = packed `token|fee|token...`;
- leg 1 starts with `tokenBorrow`;
- leg 2 ends with `tokenBorrow`;
- leg 1 output equals leg 2 input.

Frozen EIP-712 domain:
`PhantomX Executor / 1 / chainId / verifyingContract`

Frozen authority boundary:
- USD economic truth = `phantomx_core.economic_truth.evaluate_route`
- exact executor gas gate = `execution.economic_gate.certify_executor_path`
- conservative authorization floor = strictly `> $0.50`
- `minimumOnChainSurplus` remains a token-denominated atomic invariant and does not replace USD gas/MEV certification.

Machine-readable manifest:
`contracts/PhantomX_Executor_Interface_v1.json`

Conformance tests:
`tests/test_p0a2_executor_interface.py`

Interface freeze evidence:
`docs/PHANTOMX_P0A2_EXECUTOR_INTERFACE_FREEZE_2026-09-10.md`

Continuity checkpoint:
`docs/chat_continuity/2026-09-10-p0a2-interface-freeze.md`

## P0-A.2.1 — ACTIVE: EXECUTOR ABI CONFORMANCE
Implementation added:
- `scripts/p0a21_executor_conformance.py` reproducibly compiles `PhantomX_Production_Executor.sol` with solcjs `0.8.19`, optimizer enabled, runs 200, viaIR false, then compares the generated ABI against the frozen field order/types and callback signatures.
- `.github/workflows/p0-a21-executor-conformance.yml` runs the compile/ABI probe and canonical interface tests on main/PR.

Parent commit containing these changes:
`0c1798fc51307769252357fa1234cc6ebf3e65e6`

Current CI observation at checkpoint creation:
- run `34509320620` (`PHANTOMX P0-A.2.1 Executor Conformance`) was in progress.
- job `102979219389` had completed checkout and was still in `Set up Node`.
- no green/failed conclusion had been established at checkpoint time.

Required completion evidence remains:
1. fresh successful compile/ABI conformance result;
2. successful canonical interface tests;
3. successful existing P0-B compile gate;
4. successful existing P0-B executor security/callback/EIP712 gates;
5. review of actual logs for any semantic/security mismatch;
6. fix, retest and state update before leaving P0-A.2.1.

No deployment or live-capital authorization is permitted from this checkpoint.

## NEXT PHASES
After P0-A.2.1: executor semantic hardening -> exact V2/V3 route integration -> unified economic authority -> dynamic loan optimization -> final requote/MEV -> AI/tuner integration -> adversarial/simulation -> autonomous orchestration -> serverless/24x7 -> controlled live execution -> receipt/balance/PnL -> final regression/certification.

## CONTINUITY
On reconnect: load this state lock -> verify current main SHA -> inspect `scripts/p0a21_executor_conformance.py` and `.github/workflows/p0-a21-executor-conformance.yml` -> recheck active CI -> resume P0-A.2.1. Never restart the project.

END STATE LOCK
