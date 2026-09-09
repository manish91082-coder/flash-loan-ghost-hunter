"""PHANTOMX Economic Truth Engine (P0-A).

This module refuses to price an opportunity from spot spread alone.
A candidate is executable only when every required route-leg quote is present
for one coherent, block-pinned snapshot and exact transaction-path gas is known.

Quote convention: amount_out_usd is the executable post-fee, post-price-impact
output returned by the quote source. swap_fee_usd is retained for the audit
certificate and is NOT subtracted a second time.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Iterable, Optional, Sequence, Tuple

getcontext().prec = 60
D = Decimal
ZERO = D("0")
MIN_REQUIRED_PROFIT_USD = D("0.50")


class EconomicTruthError(ValueError):
    """Raised when an economic certificate cannot be produced safely."""


@dataclass(frozen=True)
class QuoteLeg:
    venue: str
    token_in: str
    token_out: str
    amount_in_usd: Decimal
    amount_out_usd: Decimal
    swap_fee_usd: Decimal
    gas_units: Optional[int]
    quoted_block: int
    quote_id: str
    price_impact_pct: Decimal = ZERO
    amount_in_raw: Optional[int] = None
    amount_out_raw: Optional[int] = None

    def validate(self, snapshot_block: int) -> None:
        if not self.venue or not self.token_in or not self.token_out or not self.quote_id:
            raise EconomicTruthError("Quote identity is incomplete")
        if self.amount_in_usd <= ZERO or self.amount_out_usd <= ZERO:
            raise EconomicTruthError("Quote amounts must be positive")
        if self.swap_fee_usd < ZERO or self.price_impact_pct < ZERO:
            raise EconomicTruthError("Quote costs/impact cannot be negative")
        if self.gas_units is not None and self.gas_units <= 0:
            raise EconomicTruthError("Quote gas_units must be positive when supplied")
        if (self.amount_in_raw is None) != (self.amount_out_raw is None):
            raise EconomicTruthError("Raw input/output quantities must be supplied together")
        if self.amount_in_raw is not None and (self.amount_in_raw <= 0 or self.amount_out_raw <= 0):
            raise EconomicTruthError("Raw quote amounts must be positive")
        if self.quoted_block != snapshot_block:
            raise EconomicTruthError(
                f"Cross-block quote rejected: quote={self.quoted_block}, snapshot={snapshot_block}"
            )


@dataclass(frozen=True)
class EconomicSnapshot:
    chain_id: int
    block_number: int
    block_hash: str
    snapshot_id: str
    gas_price_gwei: Decimal
    gas_token_price_usd: Decimal

    def validate(self) -> None:
        if self.chain_id <= 0 or self.block_number <= 0:
            raise EconomicTruthError("Invalid chain/block identity")
        if not self.block_hash or not self.snapshot_id:
            raise EconomicTruthError("Snapshot identity is incomplete")
        if self.gas_price_gwei <= ZERO or self.gas_token_price_usd <= ZERO:
            raise EconomicTruthError("Gas state must be positive")


@dataclass(frozen=True)
class ProfitCertificate:
    opportunity_id: str
    chain_id: int
    block_number: int
    block_hash: str
    snapshot_id: str
    route: Tuple[str, ...]
    loan_usd: Decimal
    gross_profit_usd: Decimal
    swap_fees_usd: Decimal
    flash_loan_fee_usd: Decimal
    gas_cost_usd: Decimal
    execution_gas_units: int
    mev_buffer_usd: Decimal
    other_costs_usd: Decimal
    conservative_net_profit_usd: Decimal
    executable: bool
    reason: str


def _as_decimal(value: Decimal | int | float | str) -> Decimal:
    return value if isinstance(value, Decimal) else D(str(value))


def evaluate_route(
    *,
    opportunity_id: str,
    snapshot: EconomicSnapshot,
    route: Sequence[QuoteLeg],
    loan_usd: Decimal,
    flash_loan_fee_usd: Decimal,
    execution_gas_units: int,
    mev_buffer_usd: Decimal = ZERO,
    other_costs_usd: Decimal = ZERO,
    min_profit_usd: Decimal = MIN_REQUIRED_PROFIT_USD,
) -> ProfitCertificate:
    """Evaluate a route using exact executor transaction gas, never quote gas."""
    snapshot.validate()
    loan_usd = _as_decimal(loan_usd)
    flash_loan_fee_usd = _as_decimal(flash_loan_fee_usd)
    mev_buffer_usd = _as_decimal(mev_buffer_usd)
    other_costs_usd = _as_decimal(other_costs_usd)
    min_profit_usd = _as_decimal(min_profit_usd)

    if not opportunity_id or not route:
        raise EconomicTruthError("Opportunity and route are required")
    if loan_usd <= ZERO:
        raise EconomicTruthError("Loan must be positive")
    if execution_gas_units <= 0:
        raise EconomicTruthError("Exact executor transaction gas is required")
    if flash_loan_fee_usd < ZERO or mev_buffer_usd < ZERO or other_costs_usd < ZERO:
        raise EconomicTruthError("Costs cannot be negative")
    if min_profit_usd < ZERO:
        raise EconomicTruthError("Minimum profit cannot be negative")

    validated = list(route)
    for leg in validated:
        leg.validate(snapshot.block_number)

    for prev, nxt in zip(validated, validated[1:]):
        if prev.token_out.lower() != nxt.token_in.lower():
            raise EconomicTruthError(
                f"Broken route continuity: {prev.token_out} -> {nxt.token_in}"
            )
        if prev.amount_out_raw is not None and nxt.amount_in_raw is not None:
            if nxt.amount_in_raw != prev.amount_out_raw:
                raise EconomicTruthError(
                    "Route raw amount continuity violated: next input != previous raw output"
                )
        elif nxt.amount_in_usd != prev.amount_out_usd:
            raise EconomicTruthError(
                "Route amount continuity violated: next input != previous executable output"
            )

    first = validated[0]
    final = validated[-1]
    if first.amount_in_usd != loan_usd:
        raise EconomicTruthError(
            f"First-leg input {first.amount_in_usd} != requested loan {loan_usd}"
        )

    gross_profit = final.amount_out_usd - loan_usd
    swap_fees = sum((leg.swap_fee_usd for leg in validated), ZERO)
    gas_cost = (
        snapshot.gas_price_gwei
        * D("1e-9")
        * D(execution_gas_units)
        * snapshot.gas_token_price_usd
    )
    conservative_net = (
        gross_profit
        - flash_loan_fee_usd
        - gas_cost
        - mev_buffer_usd
        - other_costs_usd
    )
    executable = conservative_net > min_profit_usd
    reason = (
        "PASS: conservative net profit exceeds minimum execution floor"
        if executable
        else "BLOCK: conservative net profit does not exceed minimum execution floor"
    )

    return ProfitCertificate(
        opportunity_id=opportunity_id,
        chain_id=snapshot.chain_id,
        block_number=snapshot.block_number,
        block_hash=snapshot.block_hash,
        snapshot_id=snapshot.snapshot_id,
        route=tuple(f"{leg.venue}:{leg.token_in}->{leg.token_out}" for leg in validated),
        loan_usd=loan_usd,
        gross_profit_usd=gross_profit,
        swap_fees_usd=swap_fees,
        flash_loan_fee_usd=flash_loan_fee_usd,
        gas_cost_usd=gas_cost,
        execution_gas_units=execution_gas_units,
        mev_buffer_usd=mev_buffer_usd,
        other_costs_usd=other_costs_usd,
        conservative_net_profit_usd=conservative_net,
        executable=executable,
        reason=reason,
    )


def select_best_loan(
    *,
    snapshot: EconomicSnapshot,
    quote_sampler: Iterable[tuple[Decimal, Sequence[QuoteLeg], Decimal, int]],
    min_profit_usd: Decimal = MIN_REQUIRED_PROFIT_USD,
) -> Optional[ProfitCertificate]:
    """Return the best verified sampled loan that clears the profit floor.

    Each sample must include exact executor transaction gas. No spot-spread
    extrapolation and no quote-layer gas substitution is performed.
    """
    candidates: list[ProfitCertificate] = []
    for idx, (loan_usd, route, flash_fee_usd, execution_gas_units) in enumerate(quote_sampler):
        try:
            cert = evaluate_route(
                opportunity_id=f"sample-{snapshot.block_number}-{idx}",
                snapshot=snapshot,
                route=route,
                loan_usd=loan_usd,
                flash_loan_fee_usd=flash_fee_usd,
                execution_gas_units=execution_gas_units,
                min_profit_usd=min_profit_usd,
            )
        except EconomicTruthError:
            continue
        if cert.executable:
            candidates.append(cert)

    return max(candidates, key=lambda c: c.conservative_net_profit_usd) if candidates else None
