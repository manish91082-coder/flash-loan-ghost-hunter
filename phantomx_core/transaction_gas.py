"""Fail-closed transaction-path gas estimation for PHANTOMX.

This module deliberately does not invent gas limits.  A route becomes
execution-cost-complete only when an actual transaction shape (to/data/from/
value) can be estimated against a pinned block.  Provider-specific failures
remain failures; there is no magic 150k-style fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Any

from .block_pinned_rpc import BlockPinnedRpc
from .economic_truth import EconomicTruthError

getcontext().prec = 60
D = Decimal


@dataclass(frozen=True)
class GasEstimate:
    gas_units: int
    block_number: int
    rpc_url: str
    gas_price_gwei: Decimal
    gas_token_price_usd: Decimal
    gas_cost_usd: Decimal

    def validate(self) -> None:
        if self.gas_units <= 0:
            raise EconomicTruthError("Transaction gas estimate must be positive")
        if self.block_number <= 0:
            raise EconomicTruthError("Gas estimate block must be positive")
        if self.gas_price_gwei <= 0 or self.gas_token_price_usd <= 0:
            raise EconomicTruthError("Gas pricing inputs must be positive")
        if self.gas_cost_usd <= 0:
            raise EconomicTruthError("Gas cost must be positive")


def _hex_quantity(value: int) -> str:
    if value < 0:
        raise EconomicTruthError("Transaction value cannot be negative")
    return hex(value)


def estimate_transaction_gas(
    *,
    rpc: BlockPinnedRpc,
    block_number: int,
    tx: dict[str, Any],
    gas_price_gwei: Decimal,
    gas_token_price_usd: Decimal,
    rpc_url: str,
) -> GasEstimate:
    """Estimate the full transaction path at one explicit block.

    The caller is responsible for supplying the real executor calldata.  This
    function never substitutes a generic swap estimate, a fixed gas limit, or a
    default gas price.
    """
    if block_number <= 0:
        raise EconomicTruthError("block_number must be positive")
    if not rpc_url:
        raise EconomicTruthError("rpc_url is required for coherent gas estimation")
    if not isinstance(tx, dict):
        raise EconomicTruthError("transaction must be a mapping")
    to = tx.get("to")
    data = tx.get("data", "0x")
    if not isinstance(to, str) or not to.startswith("0x") or len(to) != 42:
        raise EconomicTruthError("transaction.to must be a 20-byte hex address")
    if not isinstance(data, str) or not data.startswith("0x"):
        raise EconomicTruthError("transaction.data must be hex calldata")

    normalized = dict(tx)
    normalized.setdefault("value", _hex_quantity(0))
    if isinstance(normalized["value"], int):
        normalized["value"] = _hex_quantity(normalized["value"])

    result = rpc.call(
        "eth_estimateGas",
        [normalized, hex(block_number)],
        rpc_url=rpc_url,
    ).result
    if not isinstance(result, str) or not result.startswith("0x"):
        raise EconomicTruthError("eth_estimateGas returned malformed result")
    gas_units = int(result, 16)
    if gas_units <= 0:
        raise EconomicTruthError("eth_estimateGas returned zero gas")

    gas_price_gwei = D(str(gas_price_gwei))
    gas_token_price_usd = D(str(gas_token_price_usd))
    if gas_price_gwei <= 0 or gas_token_price_usd <= 0:
        raise EconomicTruthError("Gas pricing inputs must be positive")
    gas_cost_usd = gas_price_gwei * D("1e-9") * D(gas_units) * gas_token_price_usd
    estimate = GasEstimate(
        gas_units=gas_units,
        block_number=block_number,
        rpc_url=rpc_url,
        gas_price_gwei=gas_price_gwei,
        gas_token_price_usd=gas_token_price_usd,
        gas_cost_usd=gas_cost_usd,
    )
    estimate.validate()
    return estimate
