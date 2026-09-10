# PHANTOMX PROJECT STATE LOCK
Version: PFLC-STATE-2026-09-10-GOAL-LOCK-1.2
Status: LOCKED / ACTIVE MISSION BASELINE
Date: 2026-09-10

## 0. Purpose
This file is the recovery and continuity anchor for the PHANTOMX Flash Loan Ghost Hunter project. It records the authoritative mission goal, operating doctrine, verified repository state, known implementation gaps, and execution path. It prevents goal drift, state loss, and accidental restart after runtime/thread disconnection.

## 1. MASTER GOAL
Final success criterion:
LIVE MARKET -> EXECUTABLE OPPORTUNITY -> ALL COSTS SUBTRACTED -> CONSERVATIVE NET PROFIT > $0.50 -> SAFE ATOMIC EXECUTION -> RECEIPT -> BALANCE RECONCILIATION -> REALIZED PROFIT PROOF.

The system is successful only when it produces real positive net profit in the live market under the verified safety envelope. Continuous running, model predictions, simulations, logs, or expected PnL alone are NOT success.

Hard economic objectives:
- O1: conservative fully-costed net profit must be strictly greater than $0.50 for every accepted trade.
- O2: never knowingly execute a negative-conservative-economics trade; reject uncertainty and fail closed rather than gambling on it.

"No opportunity missed" is an optimization objective subordinate to safety and O1. It must never be used to bypass a hard gate.

Target operating behavior:
- Fully autonomous, with no routine manual decision-making.
- 24/7 operation.
- Real-time live blockchain market data.
- Dynamic runtime calculation; no fixed economic assumptions where values can be discovered/calculated from current state.
- Dynamically choose V2 or V3 strategy and route according to current market conditions.
- Dynamically size flash loans and optimize trade size.
- Dynamically price gas and include exact transaction gas in economics.
- Dynamically account for swap fees, flash-loan fees, slippage, price impact, MEV risk/buffer, and other execution costs.
- Execute only when conservative net profit clears the $0.50 execution floor and all safety gates are green.
- Seek low-latency decisions and execution, with millisecond/fractional-second architecture where infrastructure permits. Do not claim latency targets are achieved until measured.
- Preserve zero-cost architecture: no mandatory paid always-on server and no permanent dependence on the user's desktop as the production host.
- Use multiple free/public RPCs with health scoring, rolling failover, and per-request selection.
- Automated Telegram/mobile reporting.
- AI brains and online tuner continuously improve from live outcomes, but learned output never overrides hard safety gates.

Mathematical interpretation of "zero loss": the engineering requirement is that PHANTOMX does not knowingly authorize a transaction whose conservative, fully-costed economics are non-positive. Absolute zero realized loss against arbitrary external blockchain failures cannot be guaranteed, so the system must fail closed whenever safety, identity, quote freshness, gas, or execution conditions are uncertain.

## 2. V2 / V3 ROLE SEPARATION
V2 and V3 remain distinct execution architectures.

V2:
- Direct/spatial arbitrage across distinct venues.
- Same base asset returns after two venue legs.
- Genuine live executable quotes and liquidity only.

V3:
- Multi-hop / graph / triangular routing.
- Genuine path continuity and actual executable liquidity only.
- Multi-hop paths must match executor ABI and validation exactly.

Both use the same zero-trust economic/security authority, but may be redesigned beyond legacy documentation when the master goal requires it.

## 3. GOAL-FIRST CHANGE RULE
Legacy documents are evidence and design history, NOT immutable specifications.

Rule: GOAL > SAFETY > REALITY/EVIDENCE > MATHEMATICAL CORRECTNESS > CURRENT ARCHITECTURE > HISTORICAL DOCUMENTATION.

Any module may be redesigned, replaced, split, merged, or removed when evidence shows it blocks the master goal or violates safety. Preserve useful prior work as evidence/history before destructive change.

Eliminate from the final execution path any unjustified fixed loan size, fee, gas, slippage, synthetic spread, synthetic triangular multiplier, stale token/pool set, first-two-venue shortcut, or generic fallback gas assumption.

## 4. CANONICAL EXECUTION PIPELINE
WORLD/CHAIN/RPC DISCOVERY
 -> LIVE SNAPSHOT
 -> POOL/VENUE/ROUTE DISCOVERY
 -> V2/V3 ROUTE ENUMERATION
 -> EXECUTABLE QUOTES
 -> LIQUIDITY / PRICE-IMPACT MODEL
 -> DYNAMIC FLASH-LOAN SIZING
 -> EXACT EXECUTOR INTENT
 -> EXACT TRANSACTION GAS ESTIMATE AT PINNED BLOCK
 -> FEES + GAS + SLIPPAGE + MEV + RISK
 -> CONSERVATIVE PROFIT CERTIFICATE
 -> FINAL REQUOTE / STATE RECHECK
 -> EXECUTOR IDENTITY + SECURITY GATE
 -> ATOMIC EXECUTION
 -> RECEIPT
 -> BALANCE DELTA / REALIZED PnL RECONCILIATION
 -> ONLINE LEARNING / TUNING
 -> AUDIT LOG / CHECKPOINT
 -> CONTINUOUS LOOP

Failure at any hard gate => STOP / NO TRADE.

## 5. AI ARCHITECTURE
AI is a decision-intelligence layer, not the final security authority.

Responsibilities include market regime detection, V2/V3 strategy ranking, route ranking, dynamic loan-size optimization, timing, gas-aware optimization, liquidity/price-impact estimation, short-horizon forecasting, anomaly detection, RPC health prediction, MEV-risk prediction, parameter tuning, post-trade learning, and model evaluation.

Hard deterministic controls remain authoritative for executor identity, provider/router/token allowlists, quote freshness, route continuity, exact gas, minOut/slippage, repayment, minimum surplus, deadline, signer/authentication, and balance reconciliation.

Online learning path:
outcome -> error attribution -> candidate update -> validation -> bounded promotion -> rollback capability.

Unvalidated tuner output MUST NOT directly loosen safety constraints.

## 6. DYNAMIC ECONOMIC MODEL
For every candidate, use one coherent market snapshot.

NET = FINAL_EXECUTABLE_VALUE - INITIAL_BORROW_VALUE - FLASH_LOAN_COST - SWAP_COSTS - GAS_COST - MEV_BUFFER - OTHER_COSTS.

Execute only when CONSERVATIVE_NET > $0.50 and every safety gate is green.

Trade-size optimizer target: find L* that maximizes executable net profit subject to liquidity, price impact, route capacity, flash-loan availability, fees, exact gas, slippage bounds, MEV risk, executor limits, and safety ceilings.

## 7. RPC / DATA PLANE
RPC availability is assumed unreliable.

Required behavior:
- maintain many free/public RPC endpoints per supported chain where usable
- health-check and score latency, error rate, freshness, rate limits, and consistency
- rolling failover and automatic recovery
- pin economically related reads to a coherent block/snapshot
- detect divergent responses
- reject stale/inconsistent state
- isolate failing providers

RPCs are infrastructure, not truth. Cross-RPC consistency and pinned-block evidence determine truth.

## 8. LOW-LATENCY TARGET
Minimize RPC round trips, duplicate reads, process handoffs, unnecessary model calls, stale recomputation, and transaction construction overhead.
Prefer batched reads, multicall, persistent/pre-warmed state where safe, parallel quote collection, fast route pruning, and deterministic hot paths.

Measure p50/p95/p99 decision, quote, simulation, signing, and submission latency. Never substitute a target for evidence.

## 9. SERVERLESS / ZERO-COST TARGET
Target production architecture is distributed/serverless, not a permanently running local server.

Must tolerate cold starts, time limits, stateless workers, public-RPC rate limits, retries, duplicate events, and ephemeral storage.

Use durable low-cost/free state and append-only evidence/checkpoints where possible. Production readiness requires measured 24/7 survivability, wake/retry semantics, duplicate suppression, persistent state, and fault recovery.

## 10. TELEGRAM OPERATIONS
Automated mobile reporting must include system health, chain/RPC health, evaluated opportunities, accept/reject decisions and reasons, predicted vs realized PnL, gas paid, latency, errors/incidents, recovery events, and rolling summaries.
Telegram is observability, not the execution control plane.

## 11. VERIFIED REPOSITORY BASELINE
Repository: manish91082-coder/flash-loan-ghost-hunter
Visibility: public
Current main SHA before this state-lock commit: 2368728adcf838bd1dea914ffb76890bce2d2f58
Previous state-lock commit: e0595bfd660f1278d196dc8bbaa8bbd141333d91

New durable evidence/state files added in this continuation:
- docs/PHANTOMX_MASTER_OPERATING_DOCTRINE.md
- docs/PHANTOMX_CHAT_CONTINUITY_PROTOCOL.md
- docs/PHANTOMX_CURRENT_STATE_2026-09-10.md
- docs/PHANTOMX_FORENSIC_REPOSITORY_AND_GOAL_MAP_2026-09-10.md
- docs/PHANTOMX_WALLET_DEPLOYMENT_EVIDENCE_2026-09-10.md
- docs/chat_continuity/2026-09-10-goal-and-forensic-scan-session.md

Relevant verified components:
- phantomx_core/block_snapshot.py
- phantomx_core/economic_truth.py
- phantomx_core/exact_quote_engine.py
- phantomx_core/executor_identity.py
- phantomx_core/loan_optimizer.py
- phantomx_core/rpc_pool.py
- phantomx_core/transaction_gas.py
- execution/economic_gate.py
- execution/intent.py
- execution/lifecycle.py
- execution/pipeline.py
- execution/state_machine.py
- strategies/spatial.py
- strategies/triangular.py
- strategies/statistical.py
- strategies/yield_strat.py
- strategies/crosschain.py
- strategies/mev.py
- quote_engine/adapters.py
- quote_engine/market_model.py
- quote_engine/rpc_fetcher.py
- contracts/PhantomX_Production_Executor.sol
- phantomx_v3_universal_engine/live_real_rpc_harvester_v3.py
- phantomx_v3_universal_engine/live_stream_runner_v3.py
- phantomx_v3_universal_engine/ai_engines/*
- tests/* and tests/adversarial/*
- .github/workflows/*

## 12. CURRENT VERIFIED STATE
Strong foundation:
- economic truth types and fail-closed validation
- exact transaction-path gas primitive
- executable quote foundation
- quote-driven dynamic loan optimization
- EIP-712 intent signing and recovery
- hardened executor protections
- executor identity preflight code
- live V3 harvesting infrastructure
- V3 checkpointing, metrics and online tuner infrastructure
- multiple RPC failover foundations
- strict opportunity state-machine scaffolding
- durable goal/continuity doctrine and forensic map committed to Git

Partial / not production-complete:
- V2 legacy strategy economics is not fully integrated with the canonical economic-truth gate.
- V3 triangular strategy interface is not fully reconciled with the hardened executor ABI; current strategy can place the triangular route in pathA while leaving routerB/pathB empty, conflicting with current two-leg executor validation expectations.
- V3 AI brain still has fixed prototype assumptions, including fixed 320,000 gas and synthetic triangular multipliers. These cannot remain in final execution economics.
- V3 live harvester still has fallback gas behavior and synthetic triangular-price construction in the current source path.
- Spatial strategy still contains first-two-venue selection, fixed 1-token candidate sizing, 0.5% hardcoded slippage, and rough token-decimal threshold logic.
- execution/pipeline.py still has an older self-contained flow and does not yet use economic_gate as the sole certification authority.
- final requote/state locking is required but not yet proven end-to-end through the current strategy path.
- deployed executor runtime identity is not yet fully proven against the hardened artifact.
- realized live PnL has not been proven.
- latest-state CI evidence is not yet declared green because the GitHub combined-status endpoint exposed no status entries for the prior state-lock commit; fresh critical workflow results must be observed for the current state.

## 13. CURRENT EVIDENCE ADDED
The 2026-09-10 user-supplied PolygonScan/MetaMask screenshots are preserved in the evidence record `docs/PHANTOMX_WALLET_DEPLOYMENT_EVIDENCE_2026-09-10.md`.

They evidence at capture time:
- public wallet `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- displayed PolygonScan POL balance `68.647911091455766246 POL`
- deployed executor `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- creator relationship between that executor and the public wallet
- deployment transaction `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- MetaMask portfolio snapshot approximately `$7.38`, with approximately `68.648 POL` and approximately `0.00133 BNB` visible.

These screenshots are not current live-chain balance proof, bytecode-equivalence proof, or realized-PnL proof.

## 14. CRITICAL CONTRADICTION REGISTER
Historical MVP documentation contains executor address `0x36623Fbc...91987ED59`, while current deployment evidence identifies `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`.

This contradiction is now a formal P0 investigation item. Runtime identity and deployment lineage must be resolved from live on-chain evidence before any historical execution claim is reused.

Other historical contradictions:
- old 0.44% combined-fee barrier vs current exact live-fee requirement;
- old $2 minimum vs current strict $0.50 conservative-net floor;
- old fixed 50 bps slippage vs current dynamic/bounded slippage requirement;
- old fixed gas estimates vs current exact transaction-path gas requirement;
- historical “100% complete” statements vs newer forensic evidence showing open blockers.

## 15. EXACT LAST KNOWN RESUME POINT
The active technical gate remains deployed-executor identity verification.

Required gate:
1. eth_chainId
2. eth_getCode
3. exact runtime bytecode hash
4. owner()
5. DOMAIN_SEPARATOR()
6. required executor interface probes
7. compare deployed identity with hardened artifact
8. only after identity passes, construct exact signed calldata
9. pinned eth_estimateGas
10. ProfitCertificate

Recorded deployed executor: 0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286
Polygon PoS / chain ID 137
Deployment tx: 0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a

Do not treat explorer screenshots alone as bytecode-equivalence proof.

## 16. MISSION PHASE POLICY
Current phase: GLOBAL FORENSIC INTEGRATION / GOAL-FIRST RE-ARCHITECTURE.

Order:
A. chain/runtime truth
B. data/chain/RPC truth
C. V2 exact economics and execution
D. V3 genuine graph routing and execution
E. AI brain integration as bounded intelligence
F. dynamic tuner verification
G. contract/security verification
H. simulation/adversarial testing
I. complete autonomous loop
J. serverless/24x7 endurance and failover
K. controlled live execution
L. receipt/balance/realized-PnL proof
M. regression and production certification

Do not move to the next major stage while the active stage has unverified blockers.

## 17. SATURATION / COMPLETION RULE
A phase is complete only when implementation, tests, ground-level execution, adversarial failures, evidence, no known P0 blocker, rollback, and V2/V3/shared-core impact are all addressed.

Saturation coverage must include source, runtime, chain, data, RPC, quotes, liquidity, V2, V3, economics, gas, loan sizing, slippage, MEV, security, AI, tuner, simulation, execution, receipt, balance deltas, realized PnL, telemetry, serverless resilience, recovery, and regression.

A numeric saturation score can track progress but can never override an open truth/safety blocker.

## 18. CHANGE CONTROL
Every material change records Change ID, reason, files/modules, previous behavior, new behavior, risk, tests, evidence, rollback, V2 impact, V3 impact, and shared-core impact.

## 19. RECOVERY / PERSISTENCE
On every material event update current phase, current task, verified facts, open gaps, last tested commit, test evidence, next task, rollback point, and timestamp.

Recovery rule:
LOAD THIS STATE -> VERIFY CURRENT GIT SHA -> RECHECK CRITICAL RUNTIME/CI STATUS -> RECONCILE NEW CHANGES -> RESUME CURRENT TASK.

Never restart from zero after a conversation or runtime disconnect.

## 20. NEXT-TASK SELECTION
Select one highest-value unresolved task using:
Priority = safety impact + truth uncertainty + dependency centrality + evidence value + V2/V3 shared impact + goal proximity.

Depth-first rule: do not start another task while the active task has unresolved verification blockers.

## 21. SAFETY STOP CONDITIONS
STOP immediately on uncertain chain/token/pool identity, stale/inconsistent quote, unknown deployed runtime identity, missing exact gas, missing slippage/minOut, unbounded MEV exposure, route discontinuity, signer/caller uncertainty, conservative economics <= $0.50, unresolved P0 security, or unverified live-execution assumptions.

## 22. NON-DRIFT COMMANDMENT
Never optimize for more code, more documents, more AI, more complexity, or more reports by themselves.

Optimize only for the master goal:
REAL LIVE POSITIVE NET PROFIT ABOVE $0.50 PER ACCEPTED TRADE, with complete safety/evidence, autonomous operation, dynamic economics, and no routine manual decision-making.

If a feature does not materially improve this path, it is lower priority.

## 23. CURRENT DECISION
Project is NOT complete.
Project is NOT authorized for unrestricted live mainnet execution.
The forensic repository/goal map and wallet/deployment evidence have now been durably recorded.
Immediate next technical gate remains deployed executor identity verification.
After that, converge V2/V3 onto one exact economic certification and execution truth path, remove legacy fixed assumptions from the execution hot path, and build the measured autonomous loop.

## 24. CONTINUITY ACKNOWLEDGEMENT
When this file is loaded after disconnect, treat the project as the same continuous mission, not a new project.

PRIMARY INSTRUCTION: CONTINUE THE MISSION. DO NOT RESTART IT.

END OF STATE LOCK
