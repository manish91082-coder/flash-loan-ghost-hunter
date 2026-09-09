"""PHANTOMX live-data bridge for P0-A.

One selected RPC endpoint provides the snapshot header and gas state. All
stateful pool reads are then pinned to the captured block on that same
endpoint. A failed read never becomes a synthetic price.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from .block_pinned_rpc import BlockPinnedRpc
from .block_snapshot import BlockSnapshot, build_block_snapshot
from .economic_truth import EconomicTruthError
from .live_pool_snapshot import PoolRead, read_configured_pool


@dataclass(frozen=True)
class LiveDataSnapshot:
    snapshot: BlockSnapshot
    pools: tuple[PoolRead, ...]

    @property
    def block_number(self) -> int:
        return self.snapshot.block_number

    @property
    def block_hash(self) -> str:
        return self.snapshot.block_hash

    @property
    def source_rpc(self) -> str:
        return self.snapshot.source_rpc

    def require_all_pools_healthy(self) -> None:
        failed = [p for p in self.pools if p.error or p.price_usd is None]
        if failed:
            names = ", ".join(f"{p.venue}:{p.pool}" for p in failed)
            raise EconomicTruthError(f"Pool snapshot incomplete: {names}")


def _rpc_call_at(rpc: BlockPinnedRpc, rpc_url: str):
    def call(pool: str, selector: str, block_number: int) -> str:
        result = rpc.eth_call_at_block(
            to=pool,
            data=selector,
            block_number=block_number,
            rpc_url=rpc_url,
        )
        return result.result
    return call


def collect_live_data_snapshot(
    *,
    rpc: BlockPinnedRpc,
    gas_token_price_usd: Decimal,
    pool_groups: tuple[tuple[str, str, Mapping[str, Any]], ...],
    chain_id: int = 137,
) -> LiveDataSnapshot:
    """Capture one coherent block/gas state and read every pool at that block."""
    last_error: Exception | None = None
    for endpoint in rpc.endpoints:
        try:
            block_result = rpc.get_block("latest", rpc_url=endpoint)
            gas_result = rpc.gas_price(rpc_url=endpoint)
            block = block_result.result
            gas_hex = gas_result.result
            if not isinstance(block, Mapping):
                raise EconomicTruthError("RPC returned no block object")
            if not isinstance(gas_hex, str) or not gas_hex.startswith("0x"):
                raise EconomicTruthError("RPC returned invalid gas price")
            snapshot = build_block_snapshot(
                chain_id=chain_id,
                block=block,
                gas_price_wei=int(gas_hex, 16),
                gas_token_price_usd=gas_token_price_usd,
                source_rpc=endpoint,
            )
            pinned_call = _rpc_call_at(rpc, endpoint)
            pools = tuple(
                read_configured_pool(
                    snapshot=snapshot,
                    config=config,
                    venue=venue,
                    rpc_call_at_block=pinned_call,
                    kind=kind,
                )
                for kind, venue, config in pool_groups
            )
            return LiveDataSnapshot(snapshot=snapshot, pools=pools)
        except Exception as exc:
            last_error = exc
    raise EconomicTruthError(f"All RPC endpoints failed for live snapshot: {last_error}")
