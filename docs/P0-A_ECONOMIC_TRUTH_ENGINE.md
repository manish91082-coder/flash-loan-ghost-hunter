# P0-A: Economic Truth Engine

## Mission gate
A route is not executable because a spot-price spread exists. The engine requires a coherent block-pinned snapshot and an executable quote for every route leg.

## Required proof chain
`LIVE BLOCK -> SNAPSHOT -> EXECUTABLE QUOTES -> FEES -> GAS -> MEV BUFFER -> FLASH FEE -> CONSERVATIVE NET PNL -> EXECUTE/WAIT`

## Hard rules
- Polygon chain identity is explicit in the certificate.
- Every quote must match the snapshot block.
- Route token continuity is mandatory.
- Route amount continuity is mandatory.
- Loan size must equal the first-leg input.
- Every swap leg records its own fee and gas units.
- Flash-loan fee is separate from DEX swap fees.
- Quote output is defined as executable post-fee/post-price-impact output, so swap fees are not subtracted twice.
- Gas is calculated from the pinned gas state, never from a silent fallback value.
- Candidates that do not clear the minimum conservative net-profit floor are blocked.
- Loan selection uses only verified sampled quotes and never extrapolates from spot spread.

## Scope of this gate
This commit introduces shared economic-truth primitives and regression tests. It does not yet replace the live runner or smart-contract execution path. Those integrations remain separate gates so the existing shadow engine cannot silently inherit production behavior before verification.
