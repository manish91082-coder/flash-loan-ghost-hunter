import os
d = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
def w(n, c): open(os.path.join(d, n), 'w', encoding='utf-8').write(c)

w('agent_contracts.md', """# Agent Contracts

## Role-Specific Directives

1. **Mission Governor**
   - **Mission:** Enforce global invariants and approve policy exceptions.
   - **Inputs:** Alert escalations, Policy bypass requests.
   - **Outputs:** Approved exception / Emergency stop signal.
   - **Evidence:** Requires human confirmation for critical state changes.
   - **Authority:** Highest within AI scope.
   - **Escalation:** To Human Operator.

2. **Chain Intelligence**
   - **Mission:** Monitor canonical chain state.
   - **Inputs:** RPC Endpoints.
   - **Outputs:** Canonical block headers, base fees.
   - **Evidence:** Cross-verified RPC responses.
   - **Forbidden:** Cannot issue transactions.

3. **Risk Sub-Roles (Smart Contract, Liquidity, Execution, Regulatory)**
   - **Mission:** Provide NO-GO vectors.
   - **Authority:** Security Veto (Absolute dominance).

4. **Execution Supervisor**
   - **Mission:** Build and simulate final transaction.
   - **Inputs:** Validated Opportunity + Risk GO.
   - **Forbidden:** Cannot override Risk NO-GO.
""")

w('agent_permission_matrix.md', """# Agent Permission Matrix

| Agent | Read Canonical | Analyze | Propose | Write Derived | Write Canonical | Approve Policy | Execute Tx |
|---|---|---|---|---|---|---|---|
| **Mission Governor** | YES | YES | YES | YES | YES | **YES** | NO |
| **Discovery Agent** | YES | YES | YES | YES | NO | NO | NO |
| **Knowledge Agent** | YES | YES | YES | YES | **YES** (w/ Ev) | NO | NO |
| **Risk Agent** | YES | YES | **YES (NO-GO)** | YES | NO | NO | NO |
| **Execution Sup.** | YES | YES | YES | YES | NO | NO | **YES** (w/ Auth) |

*Rule: Lower-order roles cannot bypass higher-order safety/policy gates.*
""")

w('evidence_precedence_matrix.md', """# Evidence Precedence Matrix

**Rule: Precedence is Claim-Specific.**

1. **Claim: Contract State**
   - Tier 1: Direct On-Chain Query (RPC)
   - Tier 2: Subgraph (The Graph)
2. **Claim: Market Pricing**
   - Tier 1: Aggregator Median (DefiLlama)
   - Tier 2: Single Source (Coingecko)
3. **Claim: Execution Safety**
   - Tier 1: Local Node Simulation
   - Tier 2: Public Simulator API (Tenderly)
""")

w('master_control_matrix.md', """# Master Control Matrix

| ID | Requirement | Rule | Agent | Evidence | Gate |
|---|---|---|---|---|---|
| `CTRL-001` | Zero-Data Loss | SQLite + MD | Knowledge | SQLite DB exists | Phase 0 |
| `CTRL-002` | Source Verification| URL + Evidence | Discovery | Registry populated | Phase 0 |
| `CTRL-003` | Security Veto | Risk NO-GO dominance | Risk | Simulation Log | Phase 14 |
""")

w('retention_and_archival_policy.md', """# Retention and Archival Policy

- **Operational State (Hot):** Live opportunities (Purged < 24h).
- **Permanent Knowledge:** Verified Tokens, DEXes (Never deleted).
- **Historical Data:** Time-series (Compressed > 30 days).
- **Incident Data:** Retained permanently for Learning.
""")

w('jurisdiction_scope_policy.md', """# Jurisdiction Scope Policy

- **Operator Jurisdiction:** Bound by deployment region.
- **Counterparty Context:** Sanctioned addresses strictly prohibited.
- **Unresolved Jurisdiction:** Requires Human REVIEW/HOLD.
""")

w('adversarial_test_plan.md', """# Adversarial Test Plan

1. **False Data:** TVL spoofed -> Liquidity Risk NO-GO.
2. **Stale Data:** Oracle > 1 hr -> STALE status.
3. **Source Conflict:** DefiLlama vs Graph -> Precedence matrix applied.
4. **RPC Failure:** Ankr down -> Fallback to Cloudflare.
5. **Security Failure:** Unrecognized error -> Incident Log, halt contract interact.
""")

w('execution_security_protocol.md', """# Execution Security Protocol

- **Circuit Breakers:** Tripped on 5 consecutive RPC fails or 3 consecutive reverted simulations.
- **Emergency Stop:** Can be initiated by Mission Governor or Human. Halts all active TX building.
- **No Autonomous Signing:** Without Human Policy matrix clearance.
""")

w('rate_limiter_backoff_policy.md', """# Rate Limiter & Backoff Policy

- **Retryable:** 429, 500, 502.
- **Non-Retryable:** 401, 404.
- **Backoff:** Bounded Exponential (1000ms base, 30000ms max) with Jitter.
- **Retry Ceiling:** 3 retries max.
""")

w('state_persistence_protocol.md', """# State Persistence Protocol

- **Structured Authority:** SQLite Database.
- **Readable Representation:** Markdown files.
- **Triggers:** Material change, Error, 10-min interval, Shutdown.
- **Rule:** Reconcile on boot (SQLite overwrites Markdown).
""")

w('open_questions.md', """# Persistent Open Questions Registry

| ID | Question | Status | Owner | Evidence Req |
|---|---|---|---|---|
| OQ-001 | Final Cloudflare Tier mapping for zero-cost execution? | PENDING | Human | Testing metrics |
""")

w('project_description.md', """# Flash Loan Ghost Hunter (Architecture: PhantomX)

## Master Mission
Global, multi-chain, persistent, evidence-backed DeFi intelligence ecosystem.

## Universal Invariants
- UNKNOWN ≠ PASS
- ABSENCE OF EVIDENCE ≠ EVIDENCE OF ABSENCE
- FREE ≠ AVAILABLE ≠ RELIABLE ≠ QUALIFIED
- OBSERVED ≠ VERIFIED ≠ CANONICAL
- DECISION ≠ EXECUTION
- OPPORTUNITY ≠ TRADE

*Refer to the complete registry artifacts for granular role, policy, and execution controls.*
""")

print("Part 2: Remaining 12 files saturated.")
