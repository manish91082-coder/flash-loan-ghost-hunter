# PHANTOMX Project State

## Canonical state

- Branch: `mission/p0-a-economic-truth-engine`
- Current commit: `48257a8b78025ec51a60ec900738161bd2c30961`
- Pre-cleanup backup branch: `backup/pre-cleanup-2026-09-10` → `e5d03be3f787031fefafbc5158ef2ca83e46eb03`
- Clean-state backup branch: `backup/clean-state-2026-09-10` → `48257a8b78025ec51a60ec900738161bd2c30961`
- Chain: Polygon PoS Mainnet, chain ID 137
- Shared deployed executor address evidenced by owner-provided PolygonScan screenshots: `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- Deployment creator/public wallet shown in evidence: `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- Deployment transaction shown in evidence: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`

## Gate state

| Gate | State |
|---|---|
| Economic Truth | PASS on prior verified commit |
| Block-pinned RPC | PASS on prior verified commit |
| Exact V2/V3 quoting | PASS on prior verified commit |
| Genuine V3 multi-hop quote primitive | PASS on prior verified commit |
| Exact executor calldata | PASS on prior verified commit |
| Pinned transaction-path gas estimate | PASS on prior verified commit |
| EIP-712 canonical verification | PASS on prior verified commit |
| Executor adversarial callback matrix | PASS on prior verified commit |
| Deployed executor existence | EVIDENCED by supplied PolygonScan screenshots |
| Deployed bytecode identity vs hardened source | PENDING ON-CHAIN PREFLIGHT |
| Real transaction authorization | BLOCKED |
| Realized PnL | NO CLAIM |

## Repository cleanup

Removed from the active branch because they were stale operational scaffolding, redundant local backup copies, obsolete scratch/maintenance helpers, or misleading legacy control material:

- legacy `1_CLICK_*.bat` launchers
- `backup_v2_mvp/`
- `backup_v3_universal/`
- obsolete local scratch/debug/maintenance helpers
- obsolete local backup-maintenance scripts
- `100x_speed_test.py`
- stale `PROJECT_LIVE.md`
- stale `phantomx_mvp` gitlink

Preserved: current V2/V3 core implementation, economic truth engine, execution/security code, tests, workflows, and training data including the 5-year training checkpoint and master trainer.

## CI verification after cleanup

The push triggered the four existing PHANTOMX workflows. The runs for commit `48257a8b78025ec51a60ec900738161bd2c30961` completed with `failure` before useful job-step logs were exposed by the GitHub connector. This is an unresolved verification gate, not a PASS. The stale `phantomx_mvp` gitlink was removed after the earlier run failures to eliminate a known checkout/repository-hygiene defect. Fresh workflow results must be observed before calling the cleaned branch fully verified.

## Resume point

The exact technical resume point remains **deployed executor on-chain identity preflight**. The repository cleanup is complete, and the clean-state rollback branch is frozen. Next technical work must query Polygon mainnet for the deployed address's bytecode, runtime hash, owner, EIP-712 domain separator, and required executor interface, then compare the runtime against the hardened executor artifact.

## Discipline

Mission priority:

**Safety → Truth → Executability → Latency → Profitability → Scale**

No explorer label, model output, historical report, or `EXECUTE` decision is proof of execution. Real execution requires an on-chain transaction receipt and realized wallet balance delta.
