# PHANTOMX Resume Checkpoint

**Checkpoint date:** 2026-09-10

## Exact resume position

The workflow was paused after adding fail-closed deployed-executor identity preflight and before on-chain runtime identity verification.

The owner then supplied PolygonScan screenshots showing an already deployed shared contract used by the V2/V3 project:

- Executor: `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- Creator/public deployment wallet: `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- Deployment transaction: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- Chain: Polygon PoS, chain ID 137

## Completed in this task

1. Preserved the exact pre-cleanup state in branch `backup/pre-cleanup-2026-09-10`, starting at commit `e5d03be3f787031fefafbc5158ef2ca83e46eb03`.
2. Recorded deployment evidence in `docs/PHANTOMX_EXECUTOR_DEPLOYMENT_RECORD.md`.
3. Removed stale one-click launchers, local backup folders, obsolete scratch/maintenance scripts, and the stale `PROJECT_LIVE.md` control hub from the active branch.
4. Preserved V2/V3 core code, tests, security harnesses, workflows, and training data.
5. Replaced stale `project_state.md` claims with the current fail-closed state.

## Backup status

- Git backup branch: **PASS**
- Separate backup repository: **PENDING**. The connected GitHub tool can create branches/commits but does not expose repository-creation administration. Do not mislabel the backup branch as a separate repository.

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

When the user says **"resume from the last step"**, start at **deployed executor on-chain identity preflight**. Do not restart repository cleanup, do not repeat the backup branch creation, and do not treat the supplied explorer screenshots as bytecode equivalence proof.
