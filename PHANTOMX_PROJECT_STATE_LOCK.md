# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-10-GOAL-LOCK-1.4
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
Current main SHA at this lock update is recorded by Git immediately after this commit.

## CURRENT P0-A FINDING
The deployed executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` on Polygon chain ID 137 was probed through multiple public RPCs in the read-only CI workflow.

Ground evidence from decisive run `34505796013` recorded:
- deployment tx: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- deployment block: `93519165`
- deployed runtime: `6528` bytes
- deployed runtime hash: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- current hardened `PhantomX_Production_Executor` runtime: `14665` bytes
- current hardened runtime hash: `0xef0fa19dd4ae8b810b873485137372c45c50a4ac3ed68311e95ed8c747de2660`
- runtime mismatch
- owner matched recorded deployer
- deployment sender and created contract matched recorded evidence
- deployment receipt succeeded
- `DOMAIN_SEPARATOR()` and `paused()` reverted on the deployed runtime
- no transaction was signed or broadcast

Therefore the deployed runtime is NOT yet accepted as the current hardened production executor.

A historical `PhantomXMVP.sol` source candidate is known to have been deployed by `live_mainnet_deployer.py` using `solcx.compile_source(source, output_values=['abi','bin'], solc_version='0.8.20')`. The exact compiler/package/build metadata still requires reproduction and comparison to the deployed runtime.

## CURRENT ACTIVE TASK
`P0-A.1 — Resolve deployed-executor build lineage and exact artifact identity.`

Required evidence:
1. recover exact historical compiler/package/version/settings used by the deployment;
2. reproduce the historical compile path exactly, including source-key behavior where relevant;
3. compute Ethereum Keccak-256 of runtime bytecode, not NIST SHA3-256, for every candidate;
4. enumerate historical executor source candidates and configurations;
5. compare candidate runtime hashes against deployed `0x84d804...`;
6. inspect deployed runtime selectors/interfaces for family identification;
7. determine whether deployed executor is salvageable for the current goal or whether a new verified executor artifact must later replace it;
8. preserve append-only evidence and keep live execution blocked until resolved.

## DOWNSTREAM PHASES
After executor identity is resolved: live chain/RPC/data truth -> V2 convergence -> V3 graph/executor convergence -> unified economic authority -> dynamic loan optimization -> final requote/MEV -> AI/tuner integration -> adversarial/simulation -> autonomous orchestration -> serverless/24x7 -> controlled live execution -> receipt/balance/PnL -> final regression/certification.

## CONTINUITY
On reconnect: load this state lock -> verify current main SHA -> inspect latest P0-A.1 evidence -> recheck critical CI -> resume P0-A.1. Never restart the project.

END STATE LOCK
