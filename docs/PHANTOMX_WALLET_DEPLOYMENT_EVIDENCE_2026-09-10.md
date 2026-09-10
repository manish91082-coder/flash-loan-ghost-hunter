# PHANTOMX WALLET + DEPLOYMENT EVIDENCE — 2026-09-10

Status: EVIDENCE CAPTURED / NOT LIVE-STATE AUTHORITY
Source: five user-supplied screenshots from PolygonScan and MetaMask, supplied in the PHANTOMX continuity session on 2026-09-10.

## 1. Public wallet evidence

Observed PolygonScan address:
`0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`

Observed displayed POL balance:
`68.647911091455766246 POL`

Observed displayed approximate value:
`$6.64` at about `$0.10/POL` on the PolygonScan screenshot.

Observed PolygonScan transaction section:
- latest 25 from a total of 58 transactions
- first visible transaction is a contract-creation transaction beginning `0x92bc4dc8b3...`
- visible creation block: `93519165`
- visible creation amount: `0 POL`
- visible transaction fee: approximately `0.53307486 POL` (UI precision shown in screenshot)
- several visible failed outgoing transactions four days earlier to a contract beginning `0x36623Fbc...91987ED59`

## 2. Deployed shared executor evidence

Observed PolygonScan contract page:
`0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`

Observed creator on contract page:
`0x6c32820FC0fEd00E9CF28b67425ba1Ca753bd69e`

Observed deployment transaction:
`0x92bc4dc8b3450332c281445fb4443f8725586b18e880a063e0892af2c28c595a`

Observed contract displayed POL balance:
`0 POL`

## 3. MetaMask evidence

Observed portfolio screenshot:
- total portfolio: `$7.38`
- displayed daily change: `-$0.28 (-3.65%)`
- POL: approximately `68.648 POL`, displayed value approximately `$6.37`
- BNB: approximately `0.00133 BNB`, displayed value approximately `$0.94`
- additional dust balances across Ethereum/network entries were visible

A second MetaMask view displayed POL at approximately `$6.37` with the same approximately 68.648 POL balance.

## 4. Evidence classification

These screenshots are ground evidence of what the user interface displayed at capture time.

They are NOT sufficient by themselves to establish:
- current live wallet balance at a later time;
- exact current market value;
- deployed bytecode equivalence to the repository contract source;
- current contract ownership after the screenshot time;
- transaction success semantics beyond what the visible UI states;
- realized trading PnL.

The screenshots do establish a consistent creator/deployment relationship between the supplied public wallet address and deployed executor address.

## 5. Screenshot integrity fingerprints

SHA-256 of the five uploaded screenshot files as received in this session:

1. `9801866c-cfbf-487b-aaa0-212955ac864e.png` — `8ab638a24cb935c5975c0c4369aa2f26faf65ff4fc26aa66c49d0be1bf908360`
2. `cf39eb79-e292-47e4-9d31-02eff455789f.png` — `19379cf04151ccc9bef9c16e748ee4a8930058038d42cad1fa4ac78ef982a433`
3. `294e336f-70fd-42f8-9dda-5a492caef7b5.png` — `ae12b2387033f1eeb40d82880964f581dd8826e73380393ea255a723fb6855c2`
4. `e1ff187f-83ed-40d8-b200-aaf2834e2d1c.png` — `667d0be7e92f509082c452898ec57ab48e80a836a649a64c6b123b7c6eb4d85e`
5. `9a2ebb32-f886-4cf3-bceb-75485247b64a.png` — `108f204f5f36dcfbc508ca0b59768f095a7ef8c5a4aad34480afd1e84f990e5f`

The hashes identify the exact uploaded files used for this evidence extraction. The image files themselves remain in the conversation artifacts; this Git record stores their fingerprints and extracted evidence rather than copying binary images into the public repository.

## 6. Critical historical contradiction recorded for investigation

Older repository documentation contains a different deployed contract address beginning:
`0x36623Fbc...91987ED59`

The current user-supplied PolygonScan contract screenshot and the current deployment record identify the shared executor as:
`0x24056bCA6538693aE94Cc97E82f21Ee4EC7f1286`

Therefore deployment lineage must be resolved from on-chain transaction/runtime evidence before any execution authority is inferred from historical documents.

## 7. Secret-hygiene rule

No private key, seed phrase, signing credential, authentication token, or secret environment value is included in this record. Only public addresses and user-visible UI evidence are retained.

## 8. Required next verification

Use the deployed executor address and the exact Polygon state to obtain:
1. `eth_chainId`
2. `eth_getCode`
3. exact runtime bytecode hash
4. `owner()`
5. `DOMAIN_SEPARATOR()`
6. required executor interface probes
7. comparison against the intended hardened artifact

Until that evidence is complete, deployed-runtime identity remains PENDING and live execution remains BLOCKED.
