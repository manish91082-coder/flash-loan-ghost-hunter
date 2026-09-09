import unittest
from decimal import Decimal as D

from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.economic_truth import QuoteLeg
from phantomx_core.loan_optimizer import LoanSearchConfig, geometric_candidates, optimize_loan


class LoanOptimizerTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = build_block_snapshot(
            chain_id=137,
            block={"number": "0x64", "hash": "0xabc"},
            gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"),
            source_rpc="test://polygon",
        )

    def leg(self, venue, tin, tout, amount_in, amount_out, fee):
        return QuoteLeg(
            venue=venue,
            token_in=tin,
            token_out=tout,
            amount_in_usd=D(str(amount_in)),
            amount_out_usd=D(str(amount_out)),
            swap_fee_usd=D(str(fee)),
            gas_units=1,
            quoted_block=100,
            quote_id=f"{venue}-{amount_in}",
        )

    def test_candidates_are_broad_and_non_linear(self):
        values = geometric_candidates(LoanSearchConfig(
            min_loan_usd=D("1000"), max_loan_usd=D("100000"), initial_points=6
        ))
        self.assertEqual(values[0], D("1000.00"))
        self.assertEqual(values[-1], D("100000"))
        self.assertEqual(len(values), 6)
        self.assertGreater(values[2] / values[1], D("1"))

    def test_selects_best_real_quote_not_max_allowed_loan(self):
        def sampler(loan):
            # The implemented surface has its mathematical maximum near $40k.
            gain = D("0.004") * loan - D("0.0000001") * (loan - D("20000")) ** 2
            out = loan + gain
            return [
                self.leg("A", "USDC", "WETH", loan, loan + gain / D("2"), "0.5"),
                self.leg("B", "WETH", "USDC", loan + gain / D("2"), out, "0.5"),
            ], D("0.05"), 100_000

        cert = optimize_loan(
            snapshot=self.snapshot,
            route_sampler=sampler,
            config=LoanSearchConfig(
                min_loan_usd=D("1000"), max_loan_usd=D("100000"), initial_points=12,
                refinement_rounds=3, refinement_points=7,
            ),
        )
        self.assertIsNotNone(cert)
        self.assertGreater(cert.loan_usd, D("30000"))
        self.assertLess(cert.loan_usd, D("50000"))

    def test_sampler_failure_is_blocked(self):
        def sampler(_):
            raise RuntimeError("quote reverted")

        cert = optimize_loan(
            snapshot=self.snapshot,
            route_sampler=sampler,
            config=LoanSearchConfig(min_loan_usd=D("100"), max_loan_usd=D("1000")),
        )
        self.assertIsNone(cert)


if __name__ == "__main__":
    unittest.main()
