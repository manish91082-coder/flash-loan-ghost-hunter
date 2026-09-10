# PHANTOMX Project State

## Canonical state

- Branch: `mission/p0-a-economic-truth-engine`
- Last verified commit before repository cleanup: `e5d03be3f787031fefafbc5158ef2ca83e46eb03`
- Current cleanup commit: `36fee7532c8451d94c2ca7b6924d7d6edb97a00c`
- Pre-cleanup backup branch: `backup/pre-cleanup-2026-09-10`
- Chain: Polygon PoS Mainnet, chain ID 137
- Shared deployed executor address evidenced by owner-provided PolygonScan screenshots: `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- Deployment creator/public wallet shown in evidence: `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- Deployment transaction shown in evidence: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`

## Gate state

| Gate | State |
|---|---|
| Economic Truth | PASS |
| Block-pinned RPC | PASS |
| Exact V2/V3 quoting | PASS |
| Genuine V3 multi-hop quote primitive | PASS |
| Exact executor calldata | PASS |
| Pinned transaction-path gas estimate | PASS |
| EIP-712 canonical verification | PASS |
| Executor adversarial callback matrix | PASS |
| Deployed executor existence | EVIDENCED by supplied PolygonScan screenshots |
| Deployed bytecode identity vs hardened source | PENDING ON-CHAIN PREFLIGHT |
| Real transaction authorization | BLOCKED |
| Realized PnL | NO CLAIM |

## Repository cleanup state

Removed from the active branch because they were stale operational scaffolding, redundant local backup copies, or obsolete helper scripts:

- legacy `1_CLICK_*.bat` launchers
- `backup_v2_mvp/`
- `backup_v3_universal/`
- obsolete local scratch/debug/report-generation helpers such as `debug.py`, `verify.py`, `get_stats.py`, `fix_files.py`, `gatekeeper.py`, `log_rule16.py`, `export_full.py`, `append_logs.py`, `update_1_3_0.py`, `check_schema.py`, `verify_pools.py`
- obsolete local backup-maintenance scripts
- `100x_speed_test.py`

Historical repository state is preserved by the pre-cleanup backup branch. V2/V3 code, economic core, executor security code, tests, workflows, and training data were not intentionally removed.

## Resume point

The previous stopping point was deployed-executor identity verification. The owner then supplied direct PolygonScan screenshots proving that a shared V2/V3 contract is already deployed. The next technical gate is to query Polygon mainnet for the deployed address's bytecode, hash, owner, EIP-712 domain separator, and required executor interface, then compare the runtime against the hardened executor artifact before allowing any execution-path certification.

## Discipline

Mission priority remains:

**Safety → Truth → Executability → Latency → Profitability → Scale**

No explorer label, model output, historical report, or `EXECUTE` decision is treated as proof of execution. Real execution requires an on-chain transaction receipt and realized wallet balance delta.
