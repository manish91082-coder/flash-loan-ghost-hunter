# Flash Loan Ghost Hunter (Architecture: PhantomX)
**Master Architecture & Project Description Document**

## 1. Master Mission & Scope
PhantomX is a **Global, multi-chain, persistent, evidence-backed DeFi intelligence ecosystem**. 
It is not merely a "Flash Loan Bot". Flash loans are merely a specific execution capability within a much broader intelligence framework. 
The system is designed to autonomously discover, analyze, verify, simulate, and execute DeFi opportunities across multiple blockchains, ensuring zero intent loss, zero data loss, and absolute evidence-based execution.

## 2. Core Operational Philosophy
- **Zero-Cost Governance:** The system strictly prohibits mandatory paid infrastructure dependencies. It falls back to conditional-free or public RPCs and APIs (e.g., Ankr, Cloudflare) while maintaining reliability.
- **Evidence-First Execution:** No decision is made without ground-level, verifiable evidence. Data is authoritative only when cross-referenced and validated against the Canonical Schema.
- **Data Before Action:** Discover once, reuse many times. The system builds a persistent knowledge graph before attempting any live market interactions.
- **Simulation-First:** No live transaction is ever executed without a prior successful local or API-based simulation.

## 3. The 15-Phase Linear Derivation Graph
The system operates on a strictly ordered, non-bypassable phase architecture:
1. **World:** The raw, unstructured multi-chain ecosystem.
2. **Data:** Raw observation from RPCs and APIs.
3. **Knowledge:** Normalization into the Canonical Schema.
4. **Graph:** Mapping token, pool, and protocol relationships.
5. **Live State:** Real-time liquidity and reserve tracking.
6. **Opportunity:** Mathematical identification of arbitrage/liquidation vectors.
7. **Economics:** Profitability, gas, and fee modeling.
8. **Risk:** Multi-dimensional risk assessment (Slippage, MEV, Smart Contract).
9. **Confidence:** Scoring the viability of the opportunity.
10. **Simulation:** Dry-running the transaction against live state.
11. **Decision:** The absolute GO/NO-GO gate.
12. **Controlled Execution:** Building and broadcasting the signed transaction.
13. **Outcome:** On-chain verification of success or failure.
14. **Learning:** Updating the strategy memory based on the outcome.
15. **Continuous Improvement:** Auto-refinement of parameters.

## 4. Universal Invariants (LOCKED)
- **UNKNOWN ≠ PASS**
- **ABSENCE OF EVIDENCE ≠ EVIDENCE OF ABSENCE** (Not finding a router doesn't mean it doesn't exist).
- **FREE ≠ AVAILABLE ≠ RELIABLE ≠ QUALIFIED**
- **OBSERVED ≠ VERIFIED ≠ CANONICAL**
- **DECISION ≠ EXECUTION**
- **OPPORTUNITY ≠ TRADE**

## 5. Agent Architecture & Role Dominance
The system is governed by 6 High-Level Agent Domains mapping to 20+ Canonical Granular Roles:
- **Governance & Control (Mission Governor):** Enforces global invariants. Has human-escalation authority.
- **Discovery (Chain/Network/Pool Intelligence):** Polls and discovers raw data.
- **Knowledge Fabric (Deduplicator, Provenance):** Normalizes and commits data to SQLite.
- **Market & Opportunity (Quote Analyst, Route Finder):** Identifies the mathematical edge.
- **Risk & Safety (Risk Agent):** Possesses **Absolute Security Veto**. Economic optimization cannot override a Risk NO-GO.
- **Execution & Learning (Execution Supervisor):** Builds the TX. Strictly bound by Risk vetos.

## 6. Persistence & Continuity Model
- **Dual-State Architecture:** SQLite serves as the *Authoritative Structured Persistent State*, while Markdown (`.md`) files serve as the readable, derived representation and human-interface layer.
- **Append-Only History:** The system strictly maintains historical logs. Overwriting state without maintaining a lineage chain is a violation of the zero-data-loss protocol.

## Reporting Enforcement Protocol (LOCKED)
- **Rule 15 (Mandatory Response Footer):** The AI MUST append clickable markdown links to the core tracking files (`project_log.md`, `project_state.md`, `execution_report.md`, `project_description.md`) at the very end of EVERY single chat response. This is a non-negotiable directive for maintaining memory continuity and human oversight.
- **Rule 16 (Strict Append-Only Tracking):** The AI MUST NEVER overwrite any historical tracking file (`execution_report.md`, `project_state.md`, `project_log.md`, `project_description.md`, `memory_continuity.md`). The AI MUST ALWAYS append or merge the new state to the existing file to preserve a flawless historical chain. Overwriting these files is strictly prohibited.

*Refer to the complete registry artifacts for granular role, policy, and execution controls.*

