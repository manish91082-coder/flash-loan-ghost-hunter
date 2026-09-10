# PHANTOMX FORENSIC REPOSITORY + GOAL MAP — 2026-09-10

Status: BASELINE FORENSIC MAP RECORDED / ACTIVE
Purpose: Map the project goal to the repository's current V2/V3/data/execution architecture without treating historical documentation as verified runtime truth.

## 1. Master mission

PHANTOMX must become a live, autonomous, zero-trust arbitrage system operating on supported live blockchain markets.

For every candidate:

`LIVE STATE -> EXECUTABLE ROUTE -> DYNAMIC LOAN SIZE -> EXACT GAS -> ALL COSTS -> CONSERVATIVE NET > USD 0.50 -> FINAL RECHECK -> SAFE ATOMIC EXECUTION -> RECEIPT -> WALLET DELTA -> REALIZED PnL`

The final execution path must not knowingly use fixed economic assumptions where live data or exact on-chain calculation is available.

## 2. Conceptual V2 / V3 model

### V2
Direct/spatial same-asset round-trip arbitrage across real venues.

`Asset A -> venue X -> Asset B -> venue Y -> Asset A`

Selection must be across all eligible verified venues/pools, not merely the first two configured venues. Trade size must be optimized against real liquidity, price impact, fees and exact execution gas.

### V3
Genuine graph/multi-hop/triangular routing using actual executable pool state and valid packed paths.

`A -> B -> C -> A` is only one route shape. The engine must enumerate valid paths and fee tiers from verified live pool metadata, then produce calldata that exactly matches the executor ABI.

### Shared authority
V2 and V3 remain distinct strategy families but converge on one deterministic economic/security authority.

`AI proposes -> deterministic verifier decides -> executor executes`

## 3. Repository map

### Control / mission / continuity
- `PHANTOMX_PROJECT_STATE_LOCK.md` — recovery and non-drift anchor.
- `docs/PHANTOMX_MASTER_OPERATING_DOCTRINE.md` — locked operating doctrine.
- `docs/PHANTOMX_CHAT_CONTINUITY_PROTOCOL.md` — durable cross-thread state/change protocol.
- `docs/PHANTOMX_CURRENT_STATE_2026-09-10.md` — current state snapshot.
- `docs/PHANTOMX_RESUME_CHECKPOINT.md` — exact last known technical gate.
- `docs/PHANTOMX_EXECUTOR_DEPLOYMENT_RECORD.md` — supplied deployment evidence classification.
- `docs/PHANTOMX_WALLET_DEPLOYMENT_EVIDENCE_2026-09-10.md` — screenshot evidence captured in this session.

### Core truth / market infrastructure
`phantomx_core/`
- `block_snapshot.py` — immutable block/gas snapshot; rejects missing gas and fallback assumptions.
- `block_pinned_rpc.py` — block-pinned RPC infrastructure.
- `economic_truth.py` — `EconomicSnapshot`, `QuoteLeg`, `ProfitCertificate`, conservative economics.
- `exact_quote_engine.py` — executable V2/V3 quote primitives and on-chain token/pool metadata.
- `executor_identity.py` — fail-closed deployed runtime identity probes.
- `live_data_bridge.py` — live-data bridge.
- `live_pool_snapshot.py` — live pool-state structures.
- `loan_optimizer.py` — quote-driven dynamic loan search/refinement.
- `rpc_pool.py` — adaptive public RPC candidate pool.
- `transaction_gas.py` — exact transaction-path gas primitive.

### Execution
`execution/`
- `agent.py` — execution agent component.
- `discovery_engine.py` — opportunity discovery integration.
- `economic_gate.py` — exact calldata -> exact gas -> economic certificate gate.
- `gas_integration.py` — gas integration adapter.
- `historical_golden_trade_finder.py` — historical analysis/fixture utility.
- `intent.py` — exact EIP-712 intent and calldata construction.
- `lifecycle.py` — autonomous orchestration/strategy lifecycle.
- `pipeline.py` — older execution pipeline requiring convergence onto canonical economics.
- `state_machine.py` — strict sequential lifecycle including verification, simulation, final requote, receipt and reconcile states.
- `vertical_slice_base.py` — shared vertical-slice execution base.

### Strategy layer
`strategies/`
- `spatial.py` — current V2/direct spatial implementation, presently legacy/partial.
- `triangular.py` — current V3/triangular implementation, presently legacy/partial.
- `statistical.py`, `yield_strat.py`, `crosschain.py`, `mev.py` — additional strategy prototypes/paths requiring separate goal-aligned verification before inclusion in the final hot path.
- `base_strategy.py` — common strategy interface.

### Quote layer
`quote_engine/`
- `adapters.py` — V2/V3 adapter factory.
- `market_model.py` — market model.
- `rpc_fetcher.py` — RPC data retrieval.

### Contracts
`contracts/`
- `PhantomX_Executor.sol`
- `PhantomX_Master_Executor.sol`
- `PhantomX_Production_Executor.sol` — current hardened executor artifact and the runtime identity comparison target.

`phantomx_v3_universal_engine/contracts/`
- `PhantomUniversalAdapter.sol` — V3-side adapter artifact.

### V3 universal engine
`phantomx_v3_universal_engine/`
- live Polygon harvester and stream runner.
- checkpoint/metrics/logging directories.
- historical data extractor.
- `ai_engines/` containing horizon oracle, online tuner, micro-loan optimizer, historical trainer, triangular router and universal brain.
- `test_universal_engine.py` — current local V3 harness.
- `START_UNIVERSAL_ENGINE.bat` — local launcher artifact; not a production-hosting proof.

### Tests / CI
`tests/`
- block snapshot / pinned RPC tests
- cross-venue quote tests
- economic gate / economic truth tests
- exact quote tests
- EIP-712 / calldata immutability tests
- executor identity tests
- gas integration tests
- live data / live pool tests
- adversarial tests under `tests/adversarial/`

`.github/workflows/`
- economic truth tests
- live quote probe
- executor compile
- executor security
- CI failure alert

## 4. Historical scope currently documented

The historical MVP scope repeatedly identifies:
- Polygon Mainnet / chain ID 137
- Aave v3 flash liquidity
- QuickSwap v2
- Uniswap v3
- USDC base asset
- WETH/USDC
- WMATIC(POL)/USDC
- WBTC/USDC

Historical project documents also contain older fee barriers, $2 thresholds, fixed slippage and older executor addresses. Those claims are retained as history, not current authority.

## 5. Confirmed historical pair/pool blueprint requiring live re-verification

Historical documentation lists:
- USDC: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- WETH: `0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619`
- WMATIC/POL: `0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270`
- WBTC: `0x1BFD67037B42cF73acF2047067bd4F2C47D9BfD6`

Historical pool examples are retained in `PROJECT_DETAILS.md` and `STRATEGY_DETAILS.md`, but exact pool existence/identity/fee tier must be re-read from chain before economic certification.

## 6. Major dependency graph

`RPC pool`
-> `block snapshot`
-> `token/pool identity`
-> `live pool state`
-> `exact executable quote`
-> `route graph`
-> `loan optimizer`
-> `exact intent`
-> `exact transaction gas`
-> `cost/risk model`
-> `ProfitCertificate`
-> `final requote/state lock`
-> `executor identity/security`
-> `simulation`
-> `controlled execution`
-> `receipt`
-> `balance/PnL`
-> `learning/tuning`
-> `checkpoint`

AI is connected to route/ranking/optimization layers but is outside the final deterministic safety authority.

## 7. Current strongest foundations

### VERIFIED / STRONG FOUNDATION
- block-pinned snapshot primitive exists.
- fail-closed economic truth exists.
- exact quote engine exists.
- quote-driven loan optimizer exists.
- exact executor gas integration exists.
- EIP-712 intent construction exists.
- fail-closed executor identity probes exist.
- hardened executor source artifact exists.
- adaptive public RPC pool foundation exists.
- V3 live-harvester/checkpoint/tuner infrastructure exists.
- adversarial and unit test scaffolding exists.
- durable state/continuity doctrine exists.

## 8. Current blockers / non-production areas

### P0 — Runtime identity
Deployed executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` is not yet proven byte-for-byte equivalent to the current hardened source artifact.

### P0 — V2 convergence
`strategies/spatial.py` still contains first-two-venue selection, fixed one-unit initial sizing, hardcoded 50 bps slippage, fallback/rough gas and rough token-decimal economics.

### P0 — V3 convergence
`strategies/triangular.py` still uses fixed three-anchor-token logic, fixed fee assumptions and an executor-incompatible empty second leg for its single-router triangular path.

### P0 — AI economic truth
`universal_ai_brain.py` still uses fixed 320,000 gas and synthetic triangular input in the current harvester-driven path.

### P0 — Orchestration
`execution/pipeline.py` remains a second economic authority instead of being fully subordinate to the canonical economic gate.

### P0 — Requote / state lock
Final just-before-submission state consistency is not yet proven end-to-end.

### P0 — Realized PnL
No wallet-level realized positive net profit has been independently proven.

### P0 — Current CI proof
The latest state-lock commit has no status entries exposed by the combined-status endpoint, so CI green status for that exact state is not certified.

## 9. Critical contradictions discovered

1. Historical `STRATEGY_DETAILS.md` records old executor `0x36623Fbc918ceFf4d28691477D3006091987ED59`.
2. Current deployment evidence and screenshot record current shared executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`.
3. Historical documents use a 0.44% combined fee barrier and, in places, a $2 threshold; current locked mission requires conservative net strictly greater than $0.50 and requires exact current fees.
4. Historical documents claim 100% completion, but newer forensic work identified concrete blockers; those older completion labels are therefore historical claims only.
5. Historical V3/local artifacts use synthetic/fixed assumptions that conflict with the newer dynamic-only final-path doctrine.

## 10. Evidence policy

For each future claim:
- chain -> RPC proof;
- token/pool -> on-chain metadata at pinned state;
- price -> executable quote;
- gas -> exact transaction-path estimate;
- route -> path continuity + executor compatibility;
- contract -> deployed runtime/interface identity;
- simulation -> transaction simulation evidence;
- execution -> receipt;
- realized profit -> independent wallet balance reconciliation.

No screenshot, model prediction, historical report or prior assistant statement can override this hierarchy.

## 11. Build order from the goal

A. Runtime/chain/executor truth
B. Universal live data and RPC consistency
C. V2 executable economics and route generation
D. V3 genuine graph routing and executor-compatible paths
E. Unified economic certification
F. Dynamic loan optimization under exact transaction costs
G. Final requote/state lock + MEV/slippage gate
H. AI and online tuner integration behind deterministic controls
I. Simulation/adversarial/regression
J. Autonomous orchestration + serverless/24x7 resilience
K. Controlled live execution
L. Receipt/balance/realized PnL proof
M. production certification

## 12. Scan coverage and limitations

This baseline scan covered the repository root structure and the principal control, core, execution, strategies, quotes, contracts, V3 engine, AI, tests/adversarial and master-plan areas, plus targeted deep reads of the critical modules listed above.

The repository also contains many historical reports and very large consolidated artifacts. They are indexed/preserved but are not all line-by-line reread in this baseline map. They remain candidates for targeted deep forensic review when a future task depends on their details.

This document therefore records a **goal-to-architecture forensic baseline**, not a claim that every historical byte/document has been exhaustively interpreted.

## 13. Current mission state

Phase: `PHASE 0 — GLOBAL FORENSIC INTEGRATION / GOAL-FIRST RE-ARCHITECTURE`

Active task after this mapping checkpoint: `P0-A deployed executor on-chain identity verification`.

Live mainnet unrestricted execution: `BLOCKED`.

Completion requires ground evidence through realized wallet-level positive net PnL, not merely code/tests/simulation.

END OF FORENSIC REPOSITORY + GOAL MAP
