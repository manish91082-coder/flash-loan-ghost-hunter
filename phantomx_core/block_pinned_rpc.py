"""PHANTOMX block-pinned JSON-RPC transport (P0-A).

Stateful reads require an explicit block number. Snapshot acquisition may use
``latest`` only for the block header itself. All later pool/quoter calls must
use ``eth_call_at_block`` with the captured block number.

When no endpoint is explicitly supplied, calls use the adaptive multi-RPC pool:
failing endpoints are cooled down and healthy/low-latency endpoints are rotated.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from typing import Any

from .economic_truth import EconomicTruthError
from .rpc_pool import AdaptiveRpcPool


@dataclass(frozen=True)
class RpcResult:
    result: Any
    rpc_url: str
    latency_ms: float


class BlockPinnedRpc:
    """Dependency-free JSON-RPC adapter with adaptive endpoint selection."""

    def __init__(
        self,
        endpoints: list[str] | None = None,
        timeout: float = 5.0,
        rpc_pool: AdaptiveRpcPool | None = None,
    ):
        self.pool = rpc_pool or AdaptiveRpcPool(endpoints)
        self.endpoints = self.pool.endpoints
        self.timeout = timeout

    @staticmethod
    def _quantity(value: int) -> str:
        if value <= 0:
            raise EconomicTruthError("block number must be positive")
        return hex(value)

    def candidate_endpoints(self) -> tuple[str, ...]:
        """Return currently preferred endpoints in adaptive order."""
        return tuple(self.pool.ordered())

    def health_snapshot(self) -> dict[str, dict[str, object]]:
        """Expose transport health for telemetry/forensics without secrets."""
        return {
            url: {
                "failures": state.failures,
                "successes": state.successes,
                "last_latency_ms": state.last_latency_ms,
                "unhealthy_until": state.unhealthy_until,
                "last_error": state.last_error,
            }
            for url, state in self.pool.health.items()
        }

    def call(self, method: str, params: list[Any], *, rpc_url: str | None = None) -> RpcResult:
        urls = [rpc_url] if rpc_url else self.pool.ordered()
        last_errors: list[str] = []
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
                started = time.perf_counter()
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                elapsed = (time.perf_counter() - started) * 1000.0
                if "error" in body:
                    raise EconomicTruthError(str(body["error"]))
                if "result" not in body:
                    raise EconomicTruthError("RPC response missing result")
                self.pool.record_success(url, elapsed)
                return RpcResult(body["result"], url, round(elapsed, 2))
            except Exception as exc:
                last_errors.append(f"{url}: {exc!r}")
                if rpc_url is None:
                    self.pool.record_failure(url, exc)
                    continue
                raise EconomicTruthError(f"RPC endpoint failed: {url}: {exc}") from exc
        raise EconomicTruthError("All RPC endpoints failed: " + " | ".join(last_errors))

    def eth_call_at_block(self, to: str, data: str, block_number: int, *, rpc_url: str | None = None) -> RpcResult:
        """Perform eth_call against exactly ``block_number``."""
        if not to or not data.startswith("0x"):
            raise EconomicTruthError("eth_call target/data invalid")
        return self.call(
            "eth_call",
            [{"to": to, "data": data}, self._quantity(block_number)],
            rpc_url=rpc_url,
        )

    def get_block(self, block_tag: str = "latest", *, rpc_url: str | None = None) -> RpcResult:
        """Read a block header. ``latest`` is permitted only for snapshot capture."""
        if block_tag != "latest" and not block_tag.startswith("0x"):
            raise EconomicTruthError("block_tag must be latest or a hex quantity")
        return self.call("eth_getBlockByNumber", [block_tag, False], rpc_url=rpc_url)

    def gas_price(self, *, rpc_url: str | None = None) -> RpcResult:
        return self.call("eth_gasPrice", [], rpc_url=rpc_url)
