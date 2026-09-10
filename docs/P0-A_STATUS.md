# PHANTOMX P0-A STATUS

**State:** IN_PROGRESS / RUNTIME IDENTITY BLOCKED

## Mission
P0-A proves that chain, runtime, live data and economic foundations are grounded before unrestricted execution. No live capital execution is authorized by this phase.

## Verified foundation
- Shared fail-closed economic truth primitives are present.
- Quotes are tied to a snapshot block.
- Route token and amount continuity are enforced.
- Flash-loan fee, gas, MEV buffer and other costs are explicit.
- Minimum conservative net-profit floor is `$0.50`.
- Verified sampled quotes are required for loan selection.
- Block snapshot includes chain ID, block number, block hash, gas state, source RPC and deterministic snapshot ID.
- Block-pinned RPC transport can force stateful `eth_call` to an explicit block.
- Live-data bridge captures block + gas from one selected RPC endpoint and uses that endpoint for pinned pool reads.
- Exact quote engine supports V2 `getAmountsOut` and Uniswap V3 QuoterV2 exact-input calls at the captured block.
- Token metadata and V3 fee tier can be discovered from the pool at the captured block.
- Exact quote regression suite covers ABI parsing, block propagation, V2 output decoding, V3 output/gas decoding and malformed-response fail-closed behavior.
- Original P0-A regression suite has passed.
- A live Polygon quote probe has produced current mainnet block/quote evidence in CI without broadcasting a transaction.

## Runtime identity finding — BLOCKING
The deployed executor at `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286` is **not** byte-for-byte equivalent to the current hardened `contracts/PhantomX_Production_Executor.sol` artifact.

Ground evidence from CI run `34505796013`:
- chain ID: `137`
- deployment block: `93519165`
- deployed runtime: `6528` bytes
- deployed runtime hash: `0x84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb`
- current hardened runtime: `14665` bytes
- current hardened runtime hash: `0xef0fa19dd4ae8b810b873485137372c45c50a4ac3ed68311e95ed8c747de2660`
- owner(): matched recorded deployer
- deployment sender and deployment contract address matched the recorded evidence
- deployment receipt succeeded
- `DOMAIN_SEPARATOR()` reverted on the deployed runtime
- `paused()` reverted on the deployed runtime
- multiple RPC attempts were made before the identity conclusion
- no transaction was signed or broadcast

A historical `PhantomXMVP` candidate was also compiled under the recorded 0.8.20 compiler family, but its compiled runtime hash did not equal the deployed hash. The exact deployment artifact/configuration therefore remains unresolved.

## Active follow-up
`P0-A.1 — Resolve deployed-executor build lineage and exact artifact identity.`

Required evidence:
1. enumerate historical executor source candidates;
2. recover deployment compiler/version and optimizer/IR settings;
3. compile candidates under exact configurations;
4. compare runtime bytecode hashes against the deployed runtime;
5. inspect deployed selectors/interfaces to identify the actual implementation family;
6. determine whether the deployed runtime can satisfy the current mission or whether a separately verified replacement is required;
7. preserve all findings as append-only evidence;
8. keep live capital execution blocked until identity is resolved and the selected executor is fully re-verified.

## Not yet verified / downstream
- Existing `live_price_fetcher.py` public interface has not yet been replaced with the new bridge end-to-end.
- Dynamic loan optimization against real executable quotes.
- Real gas estimation for the actual final transaction path for every supported route.
- MEV cost/buffer calibration from live execution evidence.
- Live Polygon end-to-end economic certificate.
- V2/V3 final-path convergence.
- Final requote/state lock.
- Realized live PnL.

## Freeze rule
P0-A may be frozen only after the relevant identity/data gates are proven with ground evidence and the selected production executor artifact is exactly identified. No live execution authorization is implied by P0-A completion alone.
