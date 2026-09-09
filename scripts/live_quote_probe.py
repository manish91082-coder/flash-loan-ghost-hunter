"""PHANTOMX read-only Polygon live quote probe (P0-A).

Purpose: prove that the P0-A block snapshot and exact quote layers can reach
real Polygon mainnet contracts, read a captured block, and obtain real
cross-venue quote outputs. This script never signs or broadcasts a transaction.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phantomx_core.block_pinned_rpc import BlockPinnedRpc
from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.exact_quote_engine import quote_cross_venue_roundtrip
from phantomx_core.live_pool_snapshot import parse_v2_price_usd

FREE_RPCS = [
    "https://polygon-rpc.com",
    "https://polygon-mainnet.public.blastapi.io",
    "https://polygon.blockpi.network/v1/rpc/public",
]

QUICK_V2_WMATIC_POOL = "0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827"
UNIV3_WMATIC_POOL = "0xA374094527e1673A86dE625aa59517c5dE346d32"
GET_RESERVES = "0x0902f1ac"


def rpc_result(rpc: BlockPinnedRpc, method: str, params: list, endpoint: str):
    return rpc.call(method, params, rpc_url=endpoint).result


def word(result: str, index: int) -> int:
    raw = result[2:] if result.startswith("0x") else result
    start = index * 64
    end = start + 64
    if len(raw) < end:
        raise RuntimeError("short ABI response")
    return int(raw[start:end], 16)


def main() -> int:
    endpoints = [os.getenv("POLYGON_RPC_URL")] if os.getenv("POLYGON_RPC_URL") else FREE_RPCS
    endpoints = [x for x in endpoints if x]
    rpc = BlockPinnedRpc(endpoints, timeout=8.0)

    selected = None
    for endpoint in endpoints:
        try:
            block = rpc_result(rpc, "eth_getBlockByNumber", ["latest", False], endpoint)
            gas = rpc_result(rpc, "eth_gasPrice", [], endpoint)
            if not isinstance(block, dict) or not isinstance(gas, str) or not gas.startswith("0x"):
                continue
            # First capture a real WMATIC/USDC spot state at the same block to price gas in USD.
            reserves = rpc.call(
                "eth_call",
                [{"to": QUICK_V2_WMATIC_POOL, "data": GET_RESERVES}, block["number"]],
                rpc_url=endpoint,
            ).result
            reserve_price = parse_v2_price_usd(reserves, 18, 6, True)
            snapshot = build_block_snapshot(
                chain_id=137,
                block=block,
                gas_price_wei=int(gas, 16),
                gas_token_price_usd=reserve_price,
                source_rpc=endpoint,
            )
            selected = (endpoint, snapshot)
            break
        except Exception:
            continue

    if selected is None:
        print(json.dumps({"status": "BLOCKED", "reason": "No Polygon RPC produced a valid block+gas+WMATIC snapshot"}))
        return 2

    endpoint, snapshot = selected

    def pinned_call(target: str, data: str, block_number: int) -> str:
        if block_number != snapshot.block_number:
            raise RuntimeError("cross-block call attempted")
        return rpc.eth_call_at_block(target, data, block_number, rpc_url=endpoint).result

    # Read-only quote probe. V2 gas is deliberately a diagnostic constant here;
    # production economics still requires transaction-path gas estimation.
    results = {}
    for direction in ("V3_TO_V2", "V2_TO_V3"):
        try:
            legs = quote_cross_venue_roundtrip(
                snapshot=snapshot,
                v3_pool=UNIV3_WMATIC_POOL,
                v2_pool=QUICK_V2_WMATIC_POOL,
                loan_usd=Decimal("1000"),
                rpc_call_at_block=pinned_call,
                v2_gas_units=150_000,
                direction=direction,
            )
            results[direction] = {
                "leg1_out_raw": str(legs[0].amount_out_raw),
                "leg2_out_raw": str(legs[1].amount_out_raw),
                "final_out_usd": str(legs[1].amount_out_usd),
                "quoted_block": legs[1].quoted_block,
                "venue_path": [legs[0].venue, legs[1].venue],
            }
        except Exception as exc:
            results[direction] = {"error": str(exc)}

    passed = any("final_out_usd" in x for x in results.values())
    print(json.dumps({
        "status": "LIVE_QUOTE_READ_PASS" if passed else "LIVE_QUOTE_READ_BLOCKED",
        "chain_id": snapshot.chain_id,
        "block_number": snapshot.block_number,
        "block_hash": snapshot.block_hash,
        "snapshot_id": snapshot.snapshot_id,
        "source_rpc": endpoint,
        "gas_price_gwei": str(snapshot.gas_price_gwei),
        "wmatic_usd_reference": str(snapshot.gas_token_price_usd),
        "quotes": results,
        "transactions_broadcast": False,
    }, indent=2))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
