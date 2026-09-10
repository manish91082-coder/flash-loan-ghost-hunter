# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-10-GOAL-LOCK-1.6
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
Current main SHA for this checkpoint will be the commit created by this state update.

## P0-A DEPLOYED RUNTIME FINDING
The deployed Polygon executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` was compared through read-only multi-RPC evidence.

Deployment:
- tx: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- block: `93519165`
- chain ID: `137`

Decisive P0-A evidence:
- deployed runtime: `6528` bytes
- deployed runtime Keccak-256: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- current hardened `PhantomX_Production_Executor`: `14665` bytes
- current hardened runtime Keccak-256: `0xef0fa19dd4ae8b810b873485137372c45c50a4ac3ed68311e95ed8c747de2660`
- runtime mismatch with hardened artifact
- deployed owner matches recorded deployer
- deployment sender and created address match recorded evidence
- deployment receipt succeeded
- `DOMAIN_SEPARATOR()` and `paused()` revert on deployed legacy runtime
- no transaction was signed or broadcast during identity work

## P0-A.1 LINEAGE RESOLUTION — COMPLETE
Historical source/build path was reproduced with ground evidence.

Source:
`flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol`

Historical deployer path:
`live_mainnet_deployer.py` -> `solcx.compile_source(source, output_values=['abi','bin'], solc_version='0.8.20')` with no explicit optimizer setting.

Observed exact reproduction:
- GitHub Actions workflow: `PHANTOMX P0-A.1 Executor Lineage`
- run: `34507813800`
- job: `reproduce-historical-build`
- job ID: `102974218167`
- conclusion: `success`
- head commit: `71e4891b19c282c41e808277b3574e4752d3e482`
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

ABI-derived selector evidence also aligned with the deployed legacy family, including:
- `executeArbitrage(address,address,uint256,bool,uint256,uint256)` -> `0x275565c7`
- `executeOperation(address,uint256,uint256,address,bytes)` -> `0x1b11d0ff`
- `owner()` -> `0x8da5cb5b`
- `withdrawTokens(address)` -> `0x49df728c`

## CAPABILITY DECISION
Lineage is resolved as the historical `PhantomXMVP` artifact, but the deployed artifact is NOT accepted as the production executor for the master mission.

The historical artifact contains fixed Aave/QuickSwap/Uniswap/token assumptions, fixed Uniswap V3 fee `500`, a narrow two-venue execution structure, and does not provide the current hardened EIP-712/allowlist/route-validation/dynamic execution model required by the master goal.

Therefore:
- historical artifact = archival/evidence only
- current deployed executor = NOT production-authorized
- unrestricted live execution = BLOCKED

## CURRENT ACTIVE TASK
`P0-A.2 — Define and implement the verified replacement executor artifact against the canonical V2/V3 intent and economic model.`

P0-A.2 must first freeze the executor interface contract for the final mission, then implement it, compile it reproducibly, prove source/runtime identity, run security/adversarial tests, and only later consider deployment. It must support the canonical V2/V3 routes without embedding dynamic market/economic values that should come from live state.

## NEXT PHASES
After P0-A.2: live chain/RPC/data truth -> V2 convergence -> V3 graph/executor convergence -> unified economic authority -> dynamic loan optimization -> final requote/MEV -> AI/tuner integration -> adversarial/simulation -> autonomous orchestration -> serverless/24x7 -> controlled live execution -> receipt/balance/PnL -> final regression/certification.

## CONTINUITY
On reconnect: load this state lock -> verify current main SHA -> inspect `docs/PHANTOMX_P0A1_LINEAGE_EXECUTION_2026-09-10.md` and `docs/chat_continuity/2026-09-10-p0a1-lineage-resolution.md` -> recheck critical CI -> resume P0-A.2. Never restart the project.

END STATE LOCK
