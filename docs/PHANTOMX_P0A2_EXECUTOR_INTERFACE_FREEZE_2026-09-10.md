# PHANTOMX P0-A.2 EXECUTOR INTERFACE FREEZE — 2026-09-10

Status: INTERFACE FROZEN / IMPLEMENTATION ACTIVE / LIVE CAPITAL BLOCKED

## Purpose
Freeze the minimum executor interface required by the master mission before changing contract semantics. Historical documentation is evidence only; this interface is derived from the current mission, current economic authority, and current V2/V3 execution requirements.

## 1. Canonical authorization entry point

`executeOpportunity(ExecutionIntent intent)` is the only intended externally callable trade-authorization entry point for the production executor.

The off-chain system must construct and sign the exact same `ExecutionIntent` that is submitted on-chain. Calldata must be generated from the signed intent, and the exact transaction must be used for gas estimation and simulation before authorization.

## 2. Frozen ExecutionIntent fields

The struct has exactly these ordered fields:

1. `bytes32 executionId`
2. `uint8 providerType`
3. `address providerAddress`
4. `address tokenBorrow`
5. `uint256 amountBorrow`
6. `uint8 swap1Type`
7. `address routerA`
8. `bytes pathA`
9. `uint256 minAmountOut1`
10. `uint8 swap2Type`
11. `address routerB`
12. `bytes pathB`
13. `uint256 minAmountOutFinal`
14. `uint256 minimumOnChainSurplus`
15. `uint256 maximumGasLimit`
16. `uint256 deadline`
17. `bytes signature`

`signature` is transport data for calldata/callback binding and is not part of the EIP-712 struct hash.

## 3. Enumerations

`providerType`:
- `0 = AAVE`
- `1 = UNISWAP_V3_FLASH`
- `2 = BALANCER`

`swapType`:
- `0 = V2`
- `1 = V3`

No other values are valid. Invalid enum values must fail closed before external swap execution.

## 4. Route model

The executor supports exactly two swap legs at the authorization layer.

Each leg may itself be multi-hop:
- V2 path: ABI-encoded `address[]`, minimum two tokens.
- V3 path: packed `token | fee | token [| fee | token ...]`, minimum one pool hop.

The first leg must begin with `tokenBorrow`.
The second leg must terminate at `tokenBorrow`.
The output token of leg 1 must equal the input token of leg 2.

This permits:
- V2 -> V2
- V2 -> V3
- V3 -> V2
- V3 -> V3
- multi-hop V2 or V3 legs
- triangular or longer V3 paths when representable inside a leg

The executor must not embed a fixed market route, pool, token universe, V3 fee tier, spread, loan size, gas cost, or slippage percentage.

## 5. Dynamic values versus deterministic safety values

Dynamic market/economic values are supplied by the verified off-chain pipeline:
- provider address
- borrow token
- borrow amount
- route and V2/V3 selection
- exact path(s)
- minimum output values
- minimum on-chain surplus
- maximum gas limit derived from the exact transaction path
- deadline

The executor enforces these values; it does not invent them from stale or hardcoded market assumptions.

## 6. EIP-712 identity

Frozen domain:
- name: `PhantomX Executor`
- version: `1`
- chainId: runtime chain ID
- verifyingContract: executor address

Frozen primary type:
`ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)`

The signature must recover to the executor's configured authorization key. Signature mutation, cross-domain replay, and reused `executionId` must fail closed.

## 7. Mandatory safety invariants

Before any external flash-loan/swap action:
- contract is not paused;
- intent signature is valid;
- deadline has not expired;
- execution ID has not already been used;
- borrow amount is positive;
- both minimum outputs are positive;
- flash provider is explicitly allowlisted;
- borrow token is allowlisted;
- both routers are explicitly allowlisted;
- every route token is allowlisted;
- route encoding is valid;
- route continuity is valid;
- first route input equals borrowed token;
- final route output equals borrowed token;
- flash callback sender and initiator/provider identity are validated;
- repayment plus `minimumOnChainSurplus` is satisfied atomically.

## 8. Economic authority boundary

The contract is not the source of truth for USD economics.

The canonical off-chain economic authority remains `phantomx_core.economic_truth.evaluate_route()` and the exact-executor gas gate in `execution/economic_gate.py`. That gate requires exact transaction calldata and exact `eth_estimateGas` at the pinned economic snapshot block before it can issue a profit certificate. The conservative authorization floor remains strictly greater than `$0.50`. 

`minimumOnChainSurplus` is an on-chain token-denominated invariant. It does not replace the off-chain USD-denominated gas/MEV/other-cost certificate.

## 9. Flash-provider callback surface

The implementation must support the frozen provider families:
- Aave `executeOperation(...)`
- Balancer `receiveFlashLoan(...)`
- Uniswap V3 pool `uniswapV3FlashCallback(...)`

Every callback must be bound to the active execution ID and the originally signed intent, and must reject untrusted senders/providers.

## 10. Administrative surface

Administrative controls are deterministic configuration/safety controls only:
- ownership transfer to non-zero address;
- pause/unpause;
- provider allowlists;
- router allowlist;
- token allowlist.

No administrative function may inject a synthetic market quote or bypass execution invariants.

## 11. Non-goals of the frozen interface

The executor does not:
- discover pools or prices;
- choose a route from incomplete state;
- calculate USD profit from spot spread;
- estimate gas using fixed fallback values;
- decide MEV safety from a hardcoded constant alone;
- replace the off-chain economic truth engine;
- claim realized profit before receipt and wallet reconciliation.

## 12. Replacement criteria

A production replacement artifact may not be deployed until all of the following are proven for the same build:
1. source identity;
2. compiler/build settings identity;
3. reproducible creation and runtime bytecode;
4. exact runtime hash;
5. ABI/interface conformance to this freeze;
6. unit/integration/adversarial security tests;
7. exact V2/V3 route execution tests;
8. exact gas-estimation and simulation integration;
9. callback/repayment/profit invariants;
10. deployment-address and runtime identity verification after deployment.

## Decision
This document freezes the interface boundary, not the final implementation details. Implementation may be refactored aggressively behind this boundary when evidence shows a stronger design is required, but any interface-breaking change requires a new versioned freeze and a fresh verification chain.

END
