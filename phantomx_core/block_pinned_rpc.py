"""PHANTOMX block-pinned JSON-RPC transport (P0-A).

This adapter intentionally accepts an explicit block number for every stateful
`eth_call`. It does not silently downgrade to `latest`.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping

from .economic_truth import EconomicTruthError


@dataclass(frozen=True)
class RpcResult:
    result: Any
    rpc_url: str
    latency_ms: float


class BlockPinnedRpc:
    """Small dependency-free JSON-RPC adapter for deterministic block reads."""

    def __init__(self, endpoints: list[str], timeout: float = 5.0):
        if not endpoints:
            raise EconomicTruthError("At least one RPC endpoint is required")
        self.endpoints = tuple(endpoints)
        self.timeout = timeout
        self._cursor = 0

    @staticmethod
    def _quantity(value: int) -> str:
        if value <= 0:
            raise EconomicTruthError("block number must be positive")
        return hex(value)

    def call(self, method: str, params: list[Any], *, rpc_url: str | None = None) -> RpcResult:
        urls = (rpc_url,) if rpc_url else self.endpoints
        last_error: Exception | None = None
        for url in urls:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1,
            }).encode("utf-8")
            request = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            try:
                import time
                started = time.perf_counter()
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                elapsed = (time.perf_counter() - started) * 1000.0
                if "error" in body:
                    raise EconomicTruthError(str(body["error"]))
                if "result" not in body:
                    raise EconomicTruthError("RPC response missing result")
                return RpcResult(body["result"], url, round(elapsed, 2))
            except Exception as exc:
                last_error = exc
        raise EconomicTruthError(f"All RPC endpoints failed: {last_error}")

    def eth_call_at_block(self, to: str, data: str, block_number: int) -> RpcResult:
        """Perform eth_call at exactly block_number, never `latest`."""
        if not to or not data.startswith("0x"):
            raise EconomicTruthError("eth_call target/data invalid")
        return self.call(
            "eth_call",
            [{"to": to, "data": data}, self._quantity(block_number)],
        )

    def get_block(self, block_tag: str = "latest") -> RpcResult:
        """Read a block header. Used only for snapshot acquisition."""
        if block_tag != "latest" and not block_tag.startswith("0x"):
            raise EconomicTruthError("block_tag must be latest or a hex quantity")
        return self.call("eth_getBlockByNumber", [block_tag, False])

    def gas_price(self) -> RpcResult:
        return self.call("eth_gasPrice", [])
