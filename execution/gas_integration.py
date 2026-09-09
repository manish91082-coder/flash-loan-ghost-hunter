"""Bridge exact ExecutionIntent calldata into fail-closed transaction gas truth."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from phantomx_core.economic_truth import EconomicTruthError
from phantomx_core.transaction_gas import GasEstimate, estimate_transaction_gas


def estimate_executor_gas(
    *,
    intent_builder: Any,
    intent: dict[str, Any],
    executor_address: str,
    sender_address: str,
    rpc: Any,
    block_number: int,
    gas_price_gwei: Decimal,
    gas_token_price_usd: Decimal,
    rpc_url: str,
) -> GasEstimate:
    """Estimate the real PhantomX executor transaction at a pinned block.

    The builder must return the exact signed ``executeOpportunity`` calldata.
    No generic swap gas estimate or fixed fallback is permitted.
    """
    if not isinstance(executor_address, str) or len(executor_address) != 42 or not executor_address.startswith("0x"):
        raise EconomicTruthError("executor_address must be a 20-byte hex address")
    if not isinstance(sender_address, str) or len(sender_address) != 42 or not sender_address.startswith("0x"):
        raise EconomicTruthError("sender_address must be a 20-byte hex address")

    calldata = intent_builder.build_calldata(intent)
    if not isinstance(calldata, (bytes, bytearray)) or len(calldata) == 0:
        raise EconomicTruthError("ExecutionIntent builder returned empty calldata")

    tx = {
        "from": sender_address,
        "to": executor_address,
        "data": "0x" + bytes(calldata).hex(),
        "value": "0x0",
    }
    return estimate_transaction_gas(
        rpc=rpc,
        block_number=block_number,
        tx=tx,
        gas_price_gwei=gas_price_gwei,
        gas_token_price_usd=gas_token_price_usd,
        rpc_url=rpc_url,
    )
