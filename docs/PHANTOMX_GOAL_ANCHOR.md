# PHANTOMX Goal Anchor

**Authority:** outcome goal and safety constraints outrank all legacy V2/V3 documentation, prior reports, model names, and existing implementation structure.

## Mission outcome
Build PHANTOMX into a continuously operating, evidence-first flash-loan arbitrage system whose decisions are driven by real executable market state and whose economic gate is based on conservative **realizable net PnL**.

The system may redesign, replace, merge, delete, or extend legacy V2/V3 components whenever that materially improves the path to the mission outcome.

## Locked operating rules
- Legacy code/docs are **baseline evidence and reusable material**, not architectural authority.
- V2 and V3 remain strategy surfaces over a shared truth/economics/risk/execution substrate unless evidence shows a better decomposition.
- No modeled/backtest/synthetic profit may be represented as realized profit.
- Every trade candidate must be evaluated from block-pinned, executable quotes and complete transaction economics.
- Conservative net PnL must include flash-loan cost, swap costs as applicable, transaction-path gas, MEV/adverse-execution allowance, slippage/price-impact effects, and other material costs.
- The tactical execution threshold is **conservative net PnL > $0.50 USD**. Otherwise the system must WAIT.
- Gas loss is not an acceptable silent failure. Missing, stale, estimated-only, or fallback gas state blocks execution when it can materially affect profitability.
- No forced trade exists merely to maintain frequency. "24/7/profit every minute" means continuously scan and execute only opportunities that clear the safety/economic gate.
- Atomic revert is not equivalent to guaranteed no-loss operation; failed transactions can consume gas.
- AI is an optimizer/fusion layer inside a hard safety envelope, never the final authority over truth or execution safety.
- Online learning/tuning may improve parameters only through a controlled learning path with validation, rollback, and promotion gates.
- No live execution authorization is implied by analytical or read-only gates.
- **RPC redundancy is mandatory infrastructure:** no single RPC provider is an operational dependency. The system must maintain multiple candidate endpoints, health-score them, rotate traffic, cool failed endpoints, and fail over automatically. Endpoint lists must be configurable at runtime; verified zero-cost public endpoints are the default safety pool.
- **RPC state coherence is mandatory:** a complete economic snapshot (block header, gas state, and required market reads) must be captured from a coherent endpoint/state context. Switching endpoints for a new snapshot is allowed; mixing independently observed states inside one certificate is not.
- Runtime route, venue, loan size, quote source, gas strategy, and RPC selection are dynamic decisions. Immutable protocol facts may be stored as verified configuration/seed data, but must not become silent runtime assumptions.
- Safety > Truth > Executability > Latency > Profitability > Scale.

## Decision freedom
The implementation is free to change route topology, venue selection, loan sizing, quote mechanisms, gas strategy, MEV strategy, model architecture, learning architecture, contract interfaces, telemetry, RPC topology, and deployment topology when required by evidence and the mission outcome.

## Completion standard
A phase is complete only when its claims are supported by reproducible evidence from the relevant runtime layer. Reports, labels such as EXECUTE, simulations, and documentation alone are never sufficient proof.

## Current strategic path
1. Establish shared economic truth and block-pinned market state.
2. Establish adaptive multi-RPC transport and prove coherent snapshot acquisition/failover.
3. Prove real executable quotes on Polygon from the same captured state.
4. Replace diagnostic/fallback economics with transaction-path gas and complete cost modeling.
5. Drive dynamic loan sizing and route selection from real quote surfaces.
6. Build genuine V2 and graph/multi-hop V3 strategy execution on the shared substrate.
7. Integrate bounded online tuning into the active decision path.
8. Prove adversarial/MEV/slippage/revert behavior in simulation and controlled execution gates.
9. Only after all evidence gates pass, enable live execution and realized-PnL accounting.

**Lock statement:** From this point forward, when legacy documentation conflicts with the mission outcome, the mission outcome wins and the conflict must be logged rather than silently inherited. RPC provider choice is likewise subordinate to measured health, latency, capability, and evidence.
