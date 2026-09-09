# PHANTOMX P0-A Status

**State:** IN_PROGRESS

## Verified
- Shared fail-closed economic truth primitives are present.
- Quotes are tied to a snapshot block.
- Route token and amount continuity are enforced.
- Flash-loan fee, gas, MEV buffer and other costs are explicit.
- Minimum conservative net-profit floor is `$0.50`.
- Verified sampled quotes are required for loan selection.
- Block snapshot includes chain ID, block number, block hash, gas state, source RPC and deterministic snapshot ID.
- Block-pinned RPC transport can force stateful `eth_call` to an explicit block.
- Live-data bridge captures block + gas from one selected RPC endpoint and uses that endpoint for pinned pool reads.
- Regression CI has passed for the original P0-A suite.

## Not yet verified
- Existing `live_price_fetcher.py` public interface has not yet been replaced with the new bridge end-to-end.
- Real Polygon executable AMM quote acquisition at the captured block.
- Dynamic loan optimization against real executable quotes.
- Real gas estimation for the actual transaction call path.
- MEV cost/buffer calibration from live execution evidence.
- Live Polygon end-to-end economic certificate.

## Freeze gate
P0-A may be frozen only after the production data path uses the bridge for a live block-pinned snapshot, every required quote is executable at that snapshot, and a live-read test demonstrates the full evidence chain. No live execution authorization is implied by this gate.
