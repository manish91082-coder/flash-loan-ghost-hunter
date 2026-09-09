"""Adaptive, zero-cost-first Polygon RPC pool for PHANTOMX.

Endpoints are candidates, not authorities. The pool continuously health-checks,
penalizes failures, cools unhealthy endpoints, and prefers lower-latency healthy
providers. Operators can override/extend the candidate set with
PHANTOMX_RPC_URLS (comma/newline separated) without code changes.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Iterable

from .economic_truth import EconomicTruthError

DEFAULT_PUBLIC_POLYGON_RPCS = (
    "https://polygon.drpc.org",
    "https://tenderly.rpc.polygon.community/",
    "https://polygon.publicnode.com",
    "https://polygon-public.nodies.app/",
    "https://1rpc.io/matic",
    "https://polygon.api.onfinality.io/public",
    "https://polygon-mainnet.gateway.tatum.io/",
    "https://rpc-mainnet.matic.quiknode.pro",
)


@dataclass
class RpcHealth:
    failures: int = 0
    successes: int = 0
    last_latency_ms: float | None = None
    unhealthy_until: float = 0.0
    last_error: str | None = None

    @property
    def penalty(self) -> float:
        failure_penalty = min(self.failures * 100.0, 5000.0)
        latency = self.last_latency_ms if self.last_latency_ms is not None else 250.0
        return failure_penalty + latency


class AdaptiveRpcPool:
    """Ordered failover pool with health memory and deterministic selection."""

    def __init__(self, endpoints: Iterable[str] | None = None, *, cooldown_seconds: float = 30.0):
        raw = list(endpoints or load_polygon_rpc_endpoints())
        cleaned: list[str] = []
        for endpoint in raw:
            value = endpoint.strip()
            if value and value not in cleaned:
                cleaned.append(value)
        if not cleaned:
            raise EconomicTruthError("No Polygon RPC endpoints configured")
        self.endpoints = tuple(cleaned)
        self.cooldown_seconds = max(1.0, cooldown_seconds)
        self.health = {endpoint: RpcHealth() for endpoint in self.endpoints}
        self._cursor = -1

    def ordered(self) -> list[str]:
        now = time.monotonic()
        healthy = [u for u in self.endpoints if self.health[u].unhealthy_until <= now]
        candidates = healthy or list(self.endpoints)
        ranked = sorted(candidates, key=lambda u: (self.health[u].penalty, u))
        if not ranked:
            raise EconomicTruthError("RPC pool has no candidates")
        # Rotate equal-ranked candidates to avoid pinning all traffic to one RPC.
        self._cursor = (self._cursor + 1) % len(ranked)
        return ranked[self._cursor:] + ranked[:self._cursor]

    def record_success(self, endpoint: str, latency_ms: float | None = None) -> None:
        state = self.health[endpoint]
        state.successes += 1
        state.failures = max(0, state.failures - 1)
        state.unhealthy_until = 0.0
        state.last_error = None
        if latency_ms is not None:
            state.last_latency_ms = float(latency_ms)

    def record_failure(self, endpoint: str, error: Exception) -> None:
        state = self.health[endpoint]
        state.failures += 1
        state.last_error = repr(error)
        state.unhealthy_until = time.monotonic() + self.cooldown_seconds


def load_polygon_rpc_endpoints() -> tuple[str, ...]:
    """Load explicit operator endpoints first, then public zero-cost fallbacks."""
    raw = os.getenv("PHANTOMX_RPC_URLS", "")
    configured = tuple(x.strip() for x in raw.replace("\n", ",").split(",") if x.strip())
    return configured + DEFAULT_PUBLIC_POLYGON_RPCS
