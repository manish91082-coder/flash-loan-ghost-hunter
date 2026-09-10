# PHANTOMX Resume Checkpoint

**Checkpoint date:** 2026-09-10

## Exact resume position

The workflow was paused after adding fail-closed deployed-executor identity preflight and before on-chain runtime identity verification.

The owner then supplied PolygonScan screenshots showing an already deployed shared contract used by the V2/V3 project:

- Executor: `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- Creator/public deployment wallet: `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- Deployment transaction: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- Chain: Polygon PoS, chain ID 137

## Completed repository task

1. Preserved the exact pre-cleanup state in `backup/pre-cleanup-2026-09-10` at commit `e5d03be3f787031fefafbc5158ef2ca83e46eb03`.
2. Recorded deployment evidence in `docs/PHANTOMX_EXECUTOR_DEPLOYMENT_RECORD.md`.
3. Removed stale one-click launchers, redundant local V2/V3 backup folders, obsolete scratch/maintenance scripts, stale `PROJECT_LIVE.md`, and the stale `phantomx_mvp` gitlink.
4. Preserved V2/V3 core code, tests, security harnesses, workflows, and training data. The top-level 5-year trainer and training checkpoint remain present.
5. Replaced stale `project_state.md` claims with the current fail-closed state.
6. Created `backup/clean-state-2026-09-10` at clean commit `48257a8b78025ec51a60ec900738161bd2c30961`.

## Backup status

- Pre-cleanup Git rollback branch: **PASS**
- Clean-state Git rollback branch: **PASS**
- Separate backup repository: **PENDING**. The connected GitHub integration exposes branch/commit/tree operations but no repository-creation administration. Do not call either backup branch a separate repository.

## CI verification status

The cleanup push triggered the four existing PHANTOMX workflows, but the resulting runs for commit `48257a8b78025ec51a60ec900738161bd2c30961` completed as `failure` without useful step logs being exposed by the connector. This remains an unresolved verification gate. The stale `phantomx_mvp` gitlink was removed because it was a known repository-hygiene defect and fresh CI must be observed before the cleaned branch is declared fully verified.

## Next technical gate

Perform a real Polygon mainnet preflight against the deployed executor address:

1. `eth_chainId`
2. `eth_getCode`
3. exact runtime bytecode hash
4. `owner()`
5. `DOMAIN_SEPARATOR()`
6. required executor interface probes
7. compare deployed runtime identity against the hardened executor artifact
8. only if identity passes, continue to exact signed calldata and pinned `eth_estimateGas`
9. then issue an economic `ProfitCertificate`

Real transaction broadcast remains disabled until the complete safety/economic gate is explicitly satisfied.

## Resume command semantics

When the user says **"resume from the last step"**, start at **deployed executor on-chain identity preflight**. Do not restart repository cleanup, do not repeat backup creation, and do not treat the supplied explorer screenshots as bytecode equivalence proof.
