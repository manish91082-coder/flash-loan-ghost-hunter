# PHANTOMX P0-A.1 LINEAGE EXECUTION — 2026-09-10

Status: RESOLVED AS HISTORICAL LEGACY LINEAGE / CURRENT PRODUCTION BLOCKED

## Objective
Resolve the exact build lineage of the deployed Polygon executor at `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` by reproducing historical compiler/build behavior and comparing Ethereum Keccak-256 of deployed runtime bytecode.

## Ground evidence carried forward
The decisive P0-A read-only probe recorded deployed runtime size 6528 bytes and runtime Keccak `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`. The current hardened `PhantomX_Production_Executor` artifact was 14665 bytes with runtime Keccak `0xef0fa19dd4ae8b810b873485137372c45c50a4ac3ed68311e95ed8c747de2660`. The deployed runtime therefore does not match the current hardened artifact.

## Historical deployment path recovered
`live_mainnet_deployer.py` explicitly records:
- Solidity compiler: `0.8.20`
- source: `contracts/src/PhantomXMVP.sol`
- compiler API: `solcx.compile_source`
- output values: `abi`, `bin`
- no explicit optimizer setting in the deployment compiler call

The historical `04_compile_and_dry_run.py` also uses `solcx` compiler `0.8.20` for the same `PhantomXMVP.sol` source.

## P0-A.1 exact reproduction
Workflow:
`.github/workflows/p0-a1-executor-lineage.yml`

Reproducer:
`scripts/p0a1_reproduce_historical_py_solcx.py`

Observed GitHub Actions run:
- Run ID: `34507813800`
- Head commit: `71e4891b19c282c41e808277b3574e4752d3e482`
- Job: `reproduce-historical-build`
- Job ID: `102974218167`
- Conclusion: `success`
- Artifact ID: `10164530653`

Ground compilation result:
- py-solc-x: `2.0.5`
- solc binary: `0.8.20`
- exact historical API: `compile_source`
- optimizer explicitly configured: `false`
- viaIR explicitly configured: `false`
- reproduced runtime: `6528` bytes
- reproduced creation bytecode: `8233` bytes
- reproduced runtime Keccak-256: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- deployed runtime Keccak-256: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- exact runtime match: `true`

The ABI-derived Ethereum selectors also match the deployed selector fingerprint recorded in the preceding P0-A runtime evidence, including:
- `executeArbitrage(address,address,uint256,bool,uint256,uint256)` -> `0x275565c7`
- `executeOperation(address,uint256,uint256,address,bytes)` -> `0x1b11d0ff`
- `owner()` -> `0x8da5cb5b`
- `withdrawTokens(address)` -> `0x49df728c`

This establishes that the deployed contract is exactly the historical `PhantomXMVP` lineage, not the current hardened `PhantomX_Production_Executor` lineage.

## Capability conclusion
The lineage is now resolved, but the deployed legacy artifact is NOT acceptable for the current master mission. Its source contains fixed Polygon/Aave/QuickSwap/Uniswap/token assumptions, fixed Uniswap V3 fee `500`, fixed two-venue execution structure, a simple only-owner entry point, and lacks the current hardened executor's EIP-712 identity, generalized allowlists, route validation and current dynamic execution architecture.

The historical source therefore has archival/evidence value only. It must not be promoted as the production executor for the current goal.

## Safety decision
- Exact historical lineage: RESOLVED.
- Current hardened runtime equivalence: FALSE.
- Deployed contract accepted for production: NO.
- Unrestricted live execution: BLOCKED.
- No live transaction signed or broadcast during this task.

## Next deterministic task
`P0-A.2 — Define and implement the replacement executor artifact contract against the canonical V2/V3 intent/economic model, then prove its compile/runtime identity and integration surface before any deployment.`

END
