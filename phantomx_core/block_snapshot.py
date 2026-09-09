"""PHANTOMX block-pinned snapshot primitives (P0-A).

This module defines the minimum chain-state identity required before a live
opportunity can be priced. It deliberately fails closed on missing block hash,
gas state, or chain identity and never invents a fallback gas price.

The RPC adapter is injected so this layer stays deterministic in tests and can
later be wired to the existing live_price_fetcher without coupling the core to
HTTP implementation details.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Any, Callable, Mapping

from .economic_truth import EconomicSnapshot, EconomicTruthError


@dataclass(frozen=True)
class BlockSnapshot:
    chain_id: int
    block_number: int
    block_hash: str
    gas_price_wei: int
    gas_price_gwei: Decimal
    gas_token_price_usd: Decimal
    source_rpc: str
    snapshot_id: str

    def as_economic_snapshot(self) -> EconomicSnapshot:
        return EconomicSnapshot(
            chain_id=self.chain_id,
            block_number=self.block_number,
            block_hash=self.block_hash,
            snapshot_id=self.snapshot_id,
            gas_price_gwei=self.gas_price_gwei,
            gas_token_price_usd=self.gas_token_price_usd,
        )


def _hex_int(value: Any, field: str) -> int:
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.startswith("0x"):
        result = int(value, 16)
    else:
        raise EconomicTruthError(f"{field} is not a valid hex quantity")
    if result < 0:
        raise EconomicTruthError(f"{field} cannot be negative")
    return result


def build_block_snapshot(
    *,
    chain_id: int,
    block: Mapping[str, Any],
    gas_price_wei: int,
    gas_token_price_usd: Decimal,
    source_rpc: str,
) -> BlockSnapshot:
    """Build an immutable snapshot from one block and its gas state."""
    if chain_id <= 0:
        raise EconomicTruthError("chain_id must be positive")
    number = _hex_int(block.get("number"), "block.number")
    block_hash = block.get("hash")
    if number <= 0 or not isinstance(block_hash, str) or not block_hash:
        raise EconomicTruthError("block number/hash are required")
    if not source_rpc:
        raise EconomicTruthError("source_rpc is required")
    if gas_price_wei <= 0:
        raise EconomicTruthError("gas price must be positive; fallback gas is forbidden")
    gas_token_price_usd = Decimal(str(gas_token_price_usd))
    if gas_token_price_usd <= 0:
        raise EconomicTruthError("gas token USD price must be positive")

    gas_price_gwei = Decimal(gas_price_wei) / Decimal(10**9)
    canonical = f"{chain_id}|{number}|{block_hash.lower()}|{gas_price_wei}|{gas_token_price_usd}"
    snapshot_id = "block-snapshot-" + sha256(canonical.encode("utf-8")).hexdigest()[:32]
    return BlockSnapshot(
        chain_id=chain_id,
        block_number=number,
        block_hash=block_hash,
        gas_price_wei=gas_price_wei,
        gas_price_gwei=gas_price_gwei,
        gas_token_price_usd=gas_token_price_usd,
        source_rpc=source_rpc,
        snapshot_id=snapshot_id,
    )


def collect_block_snapshot(
    *,
    rpc_call: Callable[[str, list[Any]], Any],
    chain_id: int,
    gas_token_price_usd: Decimal,
) -> BlockSnapshot:
    """Collect block and gas state through an injected JSON-RPC callable.

    Both reads use the node's latest state at collection time; callers that need
    a stricter execution boundary should perform final quote validation against
    the returned block hash/number immediately before submission.
    """
    block = rpc_call("eth_getBlockByNumber", ["latest", False])
    if not isinstance(block, Mapping):
        raise EconomicTruthError("eth_getBlockByNumber returned no block")
    gas_hex = rpc_call("eth_gasPrice", [])
    gas_price_wei = _hex_int(gas_hex, "eth_gasPrice")
    source_rpc = getattr(rpc_call, "source_rpc", "injected-rpc")
    return build_block_snapshot(
        chain_id=chain_id,
        block=block,
        gas_price_wei=gas_price_wei,
        gas_token_price_usd=gas_token_price_usd,
        source_rpc=source_rpc,
    )
