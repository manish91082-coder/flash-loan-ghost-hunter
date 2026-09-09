"""PHANTOMX quote-driven dynamic loan optimizer (P0-A).

The optimizer never derives PnL from spot spread, reserve percentage, or a
fixed friction assumption. A caller supplies an executable quote sampler that
returns the complete route for each candidate loan size. The economic truth
engine then evaluates every candidate under the same pinned snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Callable, Sequence

from .economic_truth import EconomicSnapshot, ProfitCertificate, QuoteLeg, select_best_loan

D = Decimal


@dataclass(frozen=True)
class LoanSearchConfig:
    min_loan_usd: Decimal = D("1")
    max_loan_usd: Decimal = D("500000")
    initial_points: int = 12
    refinement_rounds: int = 3
    refinement_points: int = 5
    step_precision: Decimal = D("0.01")

    def validate(self) -> None:
        if self.min_loan_usd <= 0 or self.max_loan_usd < self.min_loan_usd:
            raise ValueError("invalid loan bounds")
        if self.initial_points < 2 or self.refinement_rounds < 0 or self.refinement_points < 3:
            raise ValueError("invalid search configuration")
        if self.step_precision <= 0:
            raise ValueError("step_precision must be positive")


def _quantize(value: Decimal, precision: Decimal) -> Decimal:
    return value.quantize(precision, rounding=ROUND_DOWN)


def geometric_candidates(config: LoanSearchConfig) -> list[Decimal]:
    """Create a broad multiplicative first-pass candidate set."""
    config.validate()
    if config.min_loan_usd == config.max_loan_usd:
        return [config.min_loan_usd]
    ratio = (config.max_loan_usd / config.min_loan_usd) ** (D(1) / D(config.initial_points - 1))
    values = []
    current = config.min_loan_usd
    for _ in range(config.initial_points):
        values.append(_quantize(min(current, config.max_loan_usd), config.step_precision))
        current *= ratio
    values[-1] = config.max_loan_usd
    return sorted(set(values))


def _refinement_grid(lo: Decimal, hi: Decimal, points: int, precision: Decimal) -> list[Decimal]:
    width = hi - lo
    return sorted({
        _quantize(max(lo, min(hi, lo + width * D(i) / D(points - 1))), precision)
        for i in range(points)
    })


def optimize_loan(*, snapshot: object,
                  route_sampler: Callable[[Decimal], tuple[Sequence[QuoteLeg], Decimal]],
                  config: LoanSearchConfig = LoanSearchConfig(),
                  ) -> ProfitCertificate | None:
    """Optimize loan size from executable quotes only.

    route_sampler(loan_usd) returns ``(route, flash_loan_fee_usd)``. Any quote
    failure should raise or return an invalid route; invalid candidates are
    ignored by the economic truth engine. The search refines around the best
    verified neighborhood instead of assuming a fixed reserve ratio.
    """
    config.validate()
    # Normalize adapter snapshots while retaining the public function's simple API.
    economic_snapshot = (
        snapshot if isinstance(snapshot, EconomicSnapshot)
        else snapshot.as_economic_snapshot() if callable(getattr(snapshot, "as_economic_snapshot", None))
        else None
    )
    if not isinstance(economic_snapshot, EconomicSnapshot):
        raise ValueError("Unsupported snapshot type")

    samples: dict[Decimal, tuple[Sequence[QuoteLeg], Decimal]] = {}
    candidates: list[tuple[Decimal, Sequence[QuoteLeg], Decimal]] = []

    def evaluate_sizes(sizes: list[Decimal]) -> ProfitCertificate | None:
        nonlocal candidates
        for size in sizes:
            if size in samples:
                continue
            try:
                route, flash_fee = route_sampler(size)
                samples[size] = (route, flash_fee)
                candidates.append((size, route, flash_fee))
            except Exception:
                continue
        return select_best_loan(snapshot=economic_snapshot, quote_sampler=list(candidates))

    best = evaluate_sizes(geometric_candidates(config))
    for _ in range(config.refinement_rounds):
        if best is None:
            break
        ordered = sorted(samples)
        idx = ordered.index(best.loan_usd)
        lo = ordered[max(0, idx - 1)]
        hi = ordered[min(len(ordered) - 1, idx + 1)]
        if hi <= lo:
            break
        refined = _refinement_grid(lo, hi, config.refinement_points, config.step_precision)
        new_best = evaluate_sizes(refined)
        if new_best is not None and new_best.conservative_net_profit_usd > best.conservative_net_profit_usd:
            best = new_best
    return best
