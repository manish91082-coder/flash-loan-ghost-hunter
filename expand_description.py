import os

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
filepath = os.path.join(base, 'project_description.md')

# Read existing to preserve locked rules
with open(filepath, 'r', encoding='utf-8') as f:
    existing = f.read()

# Extract Rule 15 and 16 to keep them perfectly intact
rules_section = ""
if "## Reporting Enforcement Protocol (LOCKED)" in existing:
    rules_section = "## Reporting Enforcement Protocol (LOCKED)" + existing.split("## Reporting Enforcement Protocol (LOCKED)")[1]

new_content = f"""# Flash Loan Ghost Hunter (Architecture: PhantomX)
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

{rules_section}
"""

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Append to log
log_path = os.path.join(base, 'project_log.md')
with open(log_path, 'a', encoding='utf-8') as f:
    f.write("- **[2026-08-31T18:28:00+05:30]** Expanded `project_description.md` into a full end-to-end Master Architecture document, preserving Rule 15 and 16.\\n")

print("Project Description Successfully Expanded and Merged.")
