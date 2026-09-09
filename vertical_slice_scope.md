# PFLC-REAL-MISSION-2.3: BASE VERTICAL SLICE SCOPE

## Core Directives
This document defines the exact boundaries of the first proven vertical slice for PhantomX.
The system MUST NOT expand beyond this scope until this exact slice is proven with real evidence on a real Base mainnet fork.

## Scope Parameters

- **CHAIN:** Base
- **CHAIN ID:** 8453
- **STRATEGY:** Spatial Arbitrage
- **PRIMARY BORROW PROVIDER:** Aave V3
- **PRIMARY BORROW ASSET:** USDC
- **PRIMARY INTERMEDIATE ASSET:** WETH
- **PRIMARY ROUTE:** USDC -> WETH -> USDC

## Venue Model
- **VENUE 1:** Uniswap V3 (or compatible fork like Aerodrome Slipstream if more liquid)
- **VENUE 2:** Secondary compatible V3 or V2 venue with independently verified liquidity.
- **EXECUTION:** Single atomic transaction via PhantomX_Production_Executor.sol.

## Testing & Validation Rules
- **TEST ENVIRONMENT:** Real Base fork using Anvil connected to an official/reliable Base RPC.
- **LIVE EXECUTION:** Only permitted after ALL simulation and capability-bounded gates pass. For this vertical slice, NO LIVE BROADCAST is expected since spatial arbitrage on USDC/WETH on Base is likely highly efficient, leading to a legitimate `NO TRADE` decision. We will record the exact `NO TRADE` reason and evidence.

## Capability-Bound Policy
Every execution MUST bind exactly to:
- `poolA`
- `poolB`
- `maximumGasLimit`
- `minimumOnChainSurplus`
- Real `EIP-712` Intent Hash
- Explicit `activeExecutionId` State Machine

Any deviation from this scope constitutes a mission failure.
