import unittest
from decimal import Decimal as D

from phantomx_core.economic_truth import (
    EconomicSnapshot,
    EconomicTruthError,
    QuoteLeg,
    evaluate_route,
    select_best_loan,
)


class EconomicTruthTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = EconomicSnapshot(
            chain_id=137,
            block_number=100,
            block_hash="0xabc",
            snapshot_id="snap-100",
            gas_price_gwei=D("30"),
            gas_token_price_usd=D("0.25"),
        )

    def leg(self, venue, tin, tout, amount_in, amount_out, fee, block=100):
        return QuoteLeg(
            venue=venue,
            token_in=tin,
            token_out=tout,
            amount_in_usd=D(str(amount_in)),
            amount_out_usd=D(str(amount_out)),
            swap_fee_usd=D(str(fee)),
            gas_units=100_000,
            quoted_block=block,
            quote_id=f"{venue}-{tin}-{tout}-{amount_in}",
        )

    def test_profit_floor_must_be_exceeded(self):
        cert = evaluate_route(
            opportunity_id="ok-1",
            snapshot=self.snapshot,
            route=[
                self.leg("DEX-A", "USDC", "WETH", 1000, 1003, 0.5),
                self.leg("DEX-B", "WETH", "USDC", 1003, 1004, 0.5),
            ],
            loan_usd=D("1000"),
            flash_loan_fee_usd=D("0.05"),
            mev_buffer_usd=D("0.05"),
        )
        self.assertTrue(cert.executable)
        self.assertGreater(cert.conservative_net_profit_usd, D("0.50"))
        self.assertEqual(cert.swap_fees_usd, D("1.0"))

    def test_cross_block_quote_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            evaluate_route(
                opportunity_id="bad-block",
                snapshot=self.snapshot,
                route=[self.leg("DEX-A", "USDC", "WETH", 1000, 1003, 0.1, block=101)],
                loan_usd=D("1000"),
                flash_loan_fee_usd=D("0.05"),
            )

    def test_broken_route_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            evaluate_route(
                opportunity_id="bad-route",
                snapshot=self.snapshot,
                route=[
                    self.leg("DEX-A", "USDC", "WETH", 1000, 1003, 0.1),
                    self.leg("DEX-B", "WBTC", "USDC", 1003, 1008, 0.1),
                ],
                loan_usd=D("1000"),
                flash_loan_fee_usd=D("0.05"),
            )

    def test_amount_continuity_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            evaluate_route(
                opportunity_id="bad-amounts",
                snapshot=self.snapshot,
                route=[
                    self.leg("DEX-A", "USDC", "WETH", 1000, 1003, 0.1),
                    self.leg("DEX-B", "WETH", "USDC", 1002, 1005, 0.1),
                ],
                loan_usd=D("1000"),
                flash_loan_fee_usd=D("0.05"),
            )

    def test_profit_below_floor_blocks(self):
        cert = evaluate_route(
            opportunity_id="wait-1",
            snapshot=self.snapshot,
            route=[
                self.leg("DEX-A", "USDC", "WETH", 1000, 1000.1, 0.1),
                self.leg("DEX-B", "WETH", "USDC", 1000.1, 1000.4, 0.1),
            ],
            loan_usd=D("1000"),
            flash_loan_fee_usd=D("0.05"),
            mev_buffer_usd=D("0.05"),
        )
        self.assertFalse(cert.executable)
        self.assertLessEqual(cert.conservative_net_profit_usd, D("0.50"))

    def test_best_loan_uses_verified_quotes_only(self):
        def samples():
            yield D("1000"), [
                self.leg("A", "USDC", "WETH", 1000, 1002.5, 0.1),
                self.leg("B", "WETH", "USDC", 1002.5, 1004, 0.1),
            ], D("0.05")
            yield D("2000"), [
                self.leg("A", "USDC", "WETH", 2000, 2004.5, 0.2),
                self.leg("B", "WETH", "USDC", 2004.5, 2008, 0.2),
            ], D("0.10")
            yield D("3000"), [
                self.leg("A", "USDC", "WETH", 3000, 3005, 0.3, block=99),
                self.leg("B", "WETH", "USDC", 3005, 3010, 0.3, block=99),
            ], D("0.15")

        cert = select_best_loan(snapshot=self.snapshot, quote_sampler=samples())
        self.assertIsNotNone(cert)
        self.assertEqual(cert.loan_usd, D("2000"))


if __name__ == "__main__":
    unittest.main()
