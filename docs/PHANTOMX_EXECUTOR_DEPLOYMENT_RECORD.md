# PHANTOMX Executor Deployment Record

## Ground evidence

This record captures deployment evidence supplied by the project owner on 2026-09-10.

- Chain: Polygon PoS Mainnet
- Chain ID: 137
- Deployed shared executor address: `0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`
- Contract creator / public deployment wallet shown in PolygonScan evidence: `0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`
- Deployment transaction shown in the evidence: `0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`
- Intended role: shared executor surface for V2 and V3.
- Real transaction execution remains separately gated by bytecode/interface identity, exact calldata, pinned gas estimation, economic certification, and explicit authorization.

## Evidence classification

The PolygonScan screenshots prove that a contract address exists and show the creator/deployment relationship. They do **not**, by themselves, prove that the deployed bytecode is identical to the current hardened `PhantomX_Production_Executor.sol` source.

Therefore:

- Deployment existence: `EVIDENCED`
- Address ownership/creator relationship: `EVIDENCED`
- Current hardened-runtime identity: `PENDING ON-CHAIN PREFLIGHT`
- Real execution authorization: `BLOCKED UNTIL ALL GATES PASS`
- Realized PnL: `NO CLAIM`

## Safety rule

Never substitute an address, explorer label, or historical deployment report for bytecode/interface proof. The runtime deployed at the address is the authority for execution eligibility.
