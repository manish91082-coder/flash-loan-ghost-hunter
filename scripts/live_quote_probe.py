"""PHANTOMX read-only Polygon live quote probe (P0-A).

The probe proves connectivity, block-pinned state reads and exact cross-venue
quotes without signing or broadcasting. RPC selection is adaptive and uses a
zero-cost-first candidate pool; no single provider is an architectural dependency.
"""
from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phantomx_core.block_pinned_rpc import BlockPinnedRpc
from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.exact_quote_engine import quote_cross_venue_roundtrip
from phantomx_core.live_pool_snapshot import parse_v2_price_usd

QUICK_V2_WMATIC_POOL = "0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827"
UNIV3_WMATIC_POOL = "0xA374094527e1673A86dE625aa59517c5dE346d32"
GET_RESERVES = "0x0902f1ac"


def rpc_result(rpc: BlockPinnedRpc, method: str, params: list[Any], endpoint: str):
    return rpc.call(method, params, rpc_url=endpoint).result


def classify_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "timed out" in text or "timeout" in text:
        return "TRANSPORT_TIMEOUT"
    if "urlopen error" in text or "connection" in text or "name or service" in text:
        return "TRANSPORT_CONNECTION"
    if "rpc" in text and ("error" in text or "failed" in text):
        return "JSON_RPC_ERROR"
    if "snapshot" in text or "block_header" in text:
        return "SNAPSHOT_INVALID"
    if "short abi" in text or "abi" in text:
        return "ABI_DECODE_ERROR"
    return "UNCLASSIFIED"


def main() -> int:
    # Environment override is supported by AdaptiveRpcPool through PHANTOMX_RPC_URLS.
    rpc = BlockPinnedRpc(timeout=8.0)
    diagnostics: list[dict[str, Any]] = []
    selected = None

    # A complete snapshot must come from one endpoint so block and gas state are coherent.
    for endpoint in rpc.candidate_endpoints():
        diag: dict[str, Any] = {"endpoint": endpoint, "stage": "snapshot", "status": "FAILED"}
        try:
            block = rpc_result(rpc, "eth_getBlockByNumber", ["latest", False], endpoint)
            gas = rpc_result(rpc, "eth_gasPrice", [], endpoint)
            if not isinstance(block, dict) or not block.get("number") or not block.get("hash"):
                raise RuntimeError("BLOCK_HEADER_INVALID")
            if not isinstance(gas, str) or not gas.startswith("0x"):
                raise RuntimeError("GAS_PRICE_INVALID")
            diag.update({"block_rpc_ok": True, "gas_rpc_ok": True, "block_number": block["number"]})

            reserves = rpc.call(
                "eth_call",
                [{"to": QUICK_V2_WMATIC_POOL, "data": GET_RESERVES}, block["number"]],
                rpc_url=endpoint,
            ).result
            diag["wmatic_pool_rpc_ok"] = True
            reserve_price = parse_v2_price_usd(reserves, 18, 6, True)
            snapshot = build_block_snapshot(
                chain_id=137,
                block=block,
                gas_price_wei=int(gas, 16),
                gas_token_price_usd=reserve_price,
                source_rpc=endpoint,
            )
            snapshot.validate()
            diag.update({"snapshot_valid": True, "status": "SELECTED"})
            diagnostics.append(diag)
            selected = (endpoint, snapshot)
            rpc.pool.record_success(endpoint)
            break
        except Exception as exc:
            diag["error_class"] = classify_error(exc)
            diag["error"] = repr(exc)
            diagnostics.append(diag)
            rpc.pool.record_failure(endpoint, exc)

    if selected is None:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": "NO_VALID_RPC_SNAPSHOT",
            "rpc_diagnostics": diagnostics,
            "rpc_health": rpc.health_snapshot(),
            "transactions_broadcast": False,
        }, indent=2))
        return 2

    endpoint, snapshot = selected

    def pinned_call(target: str, data: str, block_number: int) -> str:
        if block_number != snapshot.block_number:
            raise RuntimeError("CROSS_BLOCK_CALL_ATTEMPTED")
        return rpc.eth_call_at_block(target, data, block_number, rpc_url=endpoint).result

    results: dict[str, dict[str, Any]] = {}
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
            results[direction] = {"error_class": classify_error(exc), "error": repr(exc)}

    passed = any("final_out_usd" in x for x in results.values())
    status = "LIVE_QUOTE_READ_PASS" if passed else "LIVE_QUOTE_READ_BLOCKED"
    print(json.dumps({
        "status": status,
        "chain_id": snapshot.chain_id,
        "block_number": snapshot.block_number,
        "block_hash": snapshot.block_hash,
        "snapshot_id": snapshot.snapshot_id,
        "source_rpc": endpoint,
        "rpc_candidate_count": len(rpc.endpoints),
        "rpc_health": rpc.health_snapshot(),
        "gas_price_gwei": str(snapshot.gas_price_gwei),
        "wmatic_usd_reference": str(snapshot.gas_token_price_usd),
        "rpc_diagnostics": diagnostics,
        "quotes": results,
        "transactions_broadcast": False,
    }, indent=2))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
