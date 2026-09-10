# PHANTOMX P0-A.1 LINEAGE EXECUTION — 2026-09-10

Status: IN PROGRESS / LIVE EXECUTION BLOCKED

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

## P0-A.1 action executed
Added CI workflow:
`.github/workflows/p0-a1-executor-lineage.yml`

The workflow:
1. installs `solc@0.8.20`;
2. compiles `flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol` using Standard JSON with optimizer disabled, `viaIR=false`, matching the default historical compiler intent;
3. extracts deployed runtime bytecode;
4. computes Ethereum Keccak-256;
5. compares against deployed runtime hash `0x84d804...`;
6. preserves runtime, creation bytecode, ABI and result text as a workflow artifact.

The workflow is triggered on `main` pushes and can also be manually dispatched.

## Current evidence boundary
Commit containing the lineage workflow:
`a61dff30144a6defc8c785570c88cbe5c0d9e2f6`

As of this log entry, GitHub commit status for this new commit is still pending with no completed status contexts observed. Therefore the reproduced compiler result is NOT yet claimed as verified.

## Decision
- Live capital execution: BLOCKED.
- Deployed executor: NOT accepted as current hardened production executor.
- P0-A.1 remains active until the CI reproduction result is observed and compared.

## Next deterministic step
Observe the P0-A.1 workflow result. If the exact hash matches, identify the historical source/build as the deployed artifact and assess capability gap versus current mission. If it does not match, broaden the matrix across historically plausible compiler/build settings and inspect deployed selector/interface fingerprints before selecting a replacement path.

END
