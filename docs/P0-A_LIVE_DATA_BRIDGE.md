# P0-A Live Data Bridge

## Purpose
Bind the existing Polygon pool-reading configuration to the shared block-pinned core without changing the legacy shadow runner yet.

## Contract
1. Acquire one `BlockSnapshot` from a trusted RPC.
2. Pass its `block_number` into every configured pool read.
3. Accept a pool observation only when its returned read is associated with that same block.
4. Missing/invalid RPC data produces no price and therefore no executable certificate.
5. The legacy `live_price_fetcher.py` remains unchanged until a dedicated integration gate replaces its implicit `latest` calls.

## Current implementation
- `phantomx_core/block_pinned_rpc.py`: explicit-block JSON-RPC transport.
- `phantomx_core/live_pool_snapshot.py`: V2/V3 configured-pool adapters.
- `tests/test_live_pool_snapshot.py`: verifies block propagation and fail-closed behavior.

## Verification status
The adapter tests prove block propagation and parser behavior using deterministic stubs. They do not prove that the live Polygon RPC is reachable from every deployment environment, and they do not yet prove executable swap quotes.

## Freeze condition
P0-A.2 freezes only after an integration test demonstrates that the production live data path reads all required pools at the captured snapshot block and records the block identity alongside every observation.
