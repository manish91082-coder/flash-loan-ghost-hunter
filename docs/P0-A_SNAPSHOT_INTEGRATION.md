# PHANTOMX P0-A: Block-Pinned Snapshot Integration

## Purpose

The live market layer must stop treating independent `latest` calls as one economic state. A candidate quote is valid only when it is tied to a captured Polygon block identity.

## Current boundary

The shared core now accepts an immutable snapshot containing:

- chain ID
- block number
- block hash
- gas price in wei/Gwei
- gas-token USD reference
- source RPC
- deterministic snapshot ID

The snapshot builder fails closed when block identity or gas state is missing.

## Integration rule

The existing live price fetcher remains the transport layer. The next integration stage must add a block-aware call path so pool reads for an opportunity are made against the captured block number, not independent `latest` state.

Until that adapter is integrated and live-read verified, the P0-A gate remains **IN_PROGRESS**.

## Safety rule

No code path may interpret a generic spot-price snapshot as an executable profit certificate. A final execution decision must perform a fresh state/quote validation immediately before submission.
