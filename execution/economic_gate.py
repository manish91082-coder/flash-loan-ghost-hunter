"""Single execution-cost gate from exact executor calldata to economic truth."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Sequence

from phantomx_core.economic_truth import EconomicSnapshot, ProfitCertificate, QuoteLeg, evaluate_route
from phantomx_core.transaction_gas import GasEstimate

from .gas_integration import estimate_executor_gas


def certify_executor_path(
    *,
    opportunity_id: str,
    snapshot: EconomicSnapshot,
    route: Sequence[QuoteLeg],
    loan_usd: Decimal,
    flash_loan_fee_usd: Decimal,
    intent_builder: Any,
    intent: dict[str, Any],
    executor_address: str,
    sender_address: str,
    rpc: Any,
    gas_rpc_url: str,
    mev_buffer_usd: Decimal = Decimal("0"),
    other_costs_usd: Decimal = Decimal("0"),
    min_profit_usd: Decimal = Decimal("0.50"),
) -> tuple[ProfitCertificate, GasEstimate]:
    """Build exact signed calldata, estimate it at the snapshot block, then certify.

    The certificate cannot be produced from quote-layer gas. Gas estimation must
    succeed at exactly ``snapshot.block_number`` and the resulting units are the
    only gas input passed to the economic truth engine.
    """
    gas = estimate_executor_gas(
        intent_builder=intent_builder,
        intent=intent,
        executor_address=executor_address,
        sender_address=sender_address,
        rpc=rpc,
        block_number=snapshot.block_number,
        gas_price_gwei=snapshot.gas_price_gwei,
        gas_token_price_usd=snapshot.gas_token_price_usd,
        rpc_url=gas_rpc_url,
    )
    if gas.block_number != snapshot.block_number:
        raise ValueError("Gas estimate block does not match economic snapshot")
    certificate = evaluate_route(
        opportunity_id=opportunity_id,
        snapshot=snapshot,
        route=route,
        loan_usd=loan_usd,
        flash_loan_fee_usd=flash_loan_fee_usd,
        execution_gas_units=gas.gas_units,
        mev_buffer_usd=mev_buffer_usd,
        other_costs_usd=other_costs_usd,
        min_profit_usd=min_profit_usd,
    )
    return certificate, gas
