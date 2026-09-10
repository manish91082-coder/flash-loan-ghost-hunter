# PHANTOMX MASTER OPERATING DOCTRINE

Version: PMOD-2026-09-10-1.0
Status: LOCKED / ACTIVE
Date: 2026-09-10

## 1. MISSION

PHANTOMX Flash Loan Ghost Hunter is to become a continuously operating, autonomous, zero-trust arbitrage system that searches live blockchain markets, evaluates V2 and V3 opportunities with exact current-state economics, executes only a fully costed conservative opportunity whose net profit is strictly greater than USD 0.50, and proves the realized result from receipt and wallet balance deltas.

Success is NOT:
- running continuously;
- finding theoretical spreads;
- model-predicted PnL;
- expected PnL accumulated by a harvester;
- passing unit tests alone;
- generating transactions without settlement proof.

Success is live executable opportunity -> all costs -> conservative net > $0.50 -> safe atomic execution -> receipt -> independent balance reconciliation -> realized positive net PnL.

## 2. TWO HARD ECONOMIC OBJECTIVES

### O1 — Positive fully-costed profit
For every accepted trade:

CONSERVATIVE_NET_PROFIT_USD > 0.50

after all known and conservatively bounded costs.

### O2 — No knowingly negative trade / no avoidable gas loss
PHANTOMX must fail closed whenever the transaction can reasonably be expected to produce non-positive conservative economics or when the cost/safety state cannot be proven.

Absolute zero realized loss against arbitrary external blockchain failures is not mathematically guaranteeable. The engineering requirement is therefore: never knowingly authorize an economically negative transaction, and reject uncertainty instead of gambling on it.

Opportunity capture is a secondary optimization objective subject to O1 and all safety gates. "No missed opportunity" is not treated as a license to relax a hard gate.

## 3. V2 / V3 SCOPE

V2 and V3 remain separate strategy/execution families.

V2 target:
- direct/spatial arbitrage;
- multiple real venues;
- same-asset round trip;
- live executable quotes and liquidity.

V3 target:
- genuine multi-hop/graph/triangular routing;
- route continuity proven at raw-amount level where available;
- executor ABI/path semantics exactly matched;
- live executable liquidity only.

Both must converge on one shared deterministic economic/security certification authority.

## 4. GOAL-FIRST DESIGN AUTHORITY

Priority order:

GOAL > SAFETY > GROUND EVIDENCE > MATHEMATICAL CORRECTNESS > CURRENT CODE > HISTORICAL DOCUMENTATION

Historical documents are preserved as evidence and design history. They do not freeze implementation choices.

Any component may be redesigned, replaced, split, merged, or removed if evidence shows it blocks the mission or violates safety. Useful legacy artifacts must be preserved before destructive change.

## 5. ZERO-TRUST RULE

No model, document, previous answer, prior test, explorer screenshot, or self-generated assumption is trusted as truth without ground evidence appropriate to the claim.

Examples:
- chain identity -> RPC proof;
- token/pool identity -> on-chain metadata;
- executable price -> executable quote at pinned state;
- gas -> exact transaction-path eth_estimateGas at pinned state;
- executor identity -> on-chain runtime bytecode and interface identity;
- execution success -> transaction receipt;
- realized profit -> independent wallet balance reconciliation.

## 6. AI AUTHORITY BOUNDARY

AI proposes. Deterministic verification decides. The executor executes.

AI may rank:
- market regimes;
- V2 vs V3;
- route candidates;
- trade size;
- timing;
- gas-aware opportunity quality;
- liquidity/price-impact estimates;
- short-horizon prediction;
- MEV-risk probability;
- RPC provider quality;
- online parameters.

AI may NOT directly override:
- chain identity;
- token/pool identity;
- exact gas arithmetic;
- repayment arithmetic;
- route continuity;
- signer/caller authentication;
- minOut/slippage gates;
- executor security allowlists;
- safety caps;
- final trade authorization.

## 7. DYNAMIC-ONLY HOT PATH

No unjustified fixed economic value may remain in the final execution path when the value can be discovered or calculated from live state.

Forbidden final-path assumptions include:
- fixed loan amount;
- fixed gas units used as an economic substitute for exact transaction gas;
- fixed slippage percentage;
- synthetic spread/multiplier;
- stale token/pool universe;
- first-two-venue shortcut;
- prototype quote economics that are not executable.

Dynamic engine requirements:
- live block/snapshot;
- live pool state;
- executable V2/V3 quotes;
- live liquidity and price impact;
- flash-loan fee calculation;
- exact transaction gas;
- gas token price;
- bounded slippage;
- MEV risk/buffer;
- dynamic loan-size optimization;
- conservative profit certificate.

## 8. CANONICAL HOT PATH

DISCOVER
-> PIN BLOCK/SNAPSHOT
-> VERIFY CHAIN/RPC
-> DISCOVER/VERIFY VENUES/POOLS/TOKENS
-> ENUMERATE V2/V3 ROUTES
-> EXECUTABLE QUOTES
-> LIQUIDITY + PRICE IMPACT
-> OPTIMIZE LOAN SIZE
-> BUILD EXACT EXECUTOR INTENT
-> EXACT GAS AT PINNED BLOCK
-> COST MODEL
-> MEV/RISK GATE
-> PROFIT CERTIFICATE (> $0.50)
-> FINAL REQUOTE / STATE RECHECK
-> EXECUTOR IDENTITY + SECURITY PRELIGHT
-> ATOMIC EXECUTION
-> RECEIPT
-> BALANCE DELTA / REALIZED PNL
-> LEARNING / TUNING
-> AUDIT / CHECKPOINT
-> LOOP

## 9. RPC/DATA PLANE

Use multiple usable public/free RPCs per chain.

Each provider must have health telemetry covering, where measurable:
- latency;
- error rate;
- response freshness;
- rate-limit behavior;
- block-height consistency;
- capability availability;
- divergence from peer providers.

Economically related reads should be pinned to one coherent block/snapshot. Divergent or stale state is rejected. Providers are disposable infrastructure, never the sole source of truth.

## 10. SERVERLESS / ZERO-COST TARGET

Production architecture must not require a permanently running paid server or permanent dependence on the user's desktop.

The system must tolerate:
- cold starts;
- stateless workers;
- retries;
- duplicate events;
- ephemeral storage;
- public-RPC limits;
- worker interruption;
- partial provider failure.

State and evidence must survive worker replacement.

## 11. SPEED TARGET

Optimize for minimum end-to-end decision latency using batching, multicall, parallel quote collection, cached-but-validated metadata, deterministic hot paths, and minimal unnecessary handoffs.

Measure p50/p95/p99 for quote, decision, simulation, signing and submission latency. No performance claim is valid until measured.

## 12. ONLINE LEARNING / TUNER

Learning loop:

LIVE OUTCOME
-> ERROR ATTRIBUTION
-> CANDIDATE UPDATE
-> VALIDATION
-> BOUNDED PROMOTION
-> MONITOR
-> ROLLBACK IF REGRESSION

The tuner may improve ranking/optimization, but it may never silently loosen a deterministic safety boundary.

## 13. CHAT / CONTINUITY PROTOCOL

The project is one continuous mission across conversation threads and runtime sessions.

After any disconnect:
1. load the latest Git state lock;
2. verify current main SHA;
3. verify critical CI/runtime status;
4. reconcile recent changes;
5. resume the active task, not a new project.

Every material project response/event should be represented in Git as a compact canonical state/change record containing:
- timestamp;
- current phase;
- active task;
- facts newly verified;
- evidence references;
- changes made;
- tests/results;
- unresolved blockers;
- rollback point;
- next task.

Do not promise that every conversational token will be archived verbatim. The canonical requirement is complete recoverable project state, decisions, evidence and change history. Source artifacts themselves remain preserved where practical.

## 14. CHANGE CONTROL

Every material change requires:
- Change ID;
- reason;
- affected files/modules;
- old behavior;
- new behavior;
- risk;
- tests;
- evidence;
- rollback method;
- V2 impact;
- V3 impact;
- shared-core impact.

Append history. Do not erase useful evidence merely to make the tree look cleaner.

## 15. SINGLE ACTIVE TASK / DEPTH-FIRST RULE

One active task at a time.

A task is closed only after implementation (when required), ground-level verification, negative/adversarial verification, evidence capture, rollback point, and state update.

Task priority:
SAFETY + TRUTH UNCERTAINTY + DEPENDENCY CENTRALITY + EVIDENCE VALUE + V2/V3 SHARED IMPACT + GOAL PROXIMITY

No task hopping merely because another feature looks interesting.

## 16. HARD STOP CONDITIONS

STOP / NO TRADE on:
- uncertain chain identity;
- uncertain executor runtime identity;
- uncertain token/pool identity;
- stale or inconsistent quote;
- synthetic route;
- missing exact gas;
- missing slippage/minOut protection;
- broken route continuity;
- uncertain signer/caller;
- bounded-mev requirement not satisfied;
- conservative net <= $0.50;
- unresolved P0 security issue;
- inability to reconcile realized PnL independently;
- any attempt to bypass an earlier failed gate.

## 17. WALLET/SECRET HYGIENE

The repository is public. Never commit private keys, seed phrases, raw secrets, signing credentials, or secret-bearing environment files.

Public addresses may be recorded when required for reproducibility. Secret material must remain in runtime secret storage only.

## 18. COMPLETION / SATURATION

PHANTOMX is complete only when all critical stages are evidenced:
- source;
- runtime identity;
- chain/data truth;
- RPC resilience;
- V2;
- V3;
- executable quotes;
- liquidity/price impact;
- dynamic loan sizing;
- exact gas;
- slippage;
- MEV risk control;
- contract security;
- AI integration;
- bounded tuner/learning;
- simulation;
- adversarial tests;
- autonomous orchestration;
- serverless/24x7 resilience;
- controlled live execution;
- receipts;
- wallet balance deltas;
- realized net PnL;
- regression.

A numerical saturation score may track progress, but it can never override an open safety/truth blocker.

## 19. FINAL COMMAND

CONTINUE THE MISSION. DO NOT RESTART IT.

The only real finish line is verified live positive net profit above $0.50 per accepted trade under the safety envelope, with no knowingly negative execution and independently reconciled settlement evidence.
