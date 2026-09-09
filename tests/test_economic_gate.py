import unittest
from decimal import Decimal as D

from execution.economic_gate import certify_executor_path
from phantomx_core.economic_truth import EconomicSnapshot, QuoteLeg


class FakeRpc:
    def __init__(self, result="0x186a0"):
        self.result = result
        self.calls = []

    def call(self, method, params, *, rpc_url=None):
        self.calls.append((method, params, rpc_url))
        return type("Result", (), {"result": self.result})()


class FakeBuilder:
    def build_calldata(self, intent):
        return b"\xaa\xbb"


class EconomicGateTests(unittest.TestCase):
    def test_exact_gas_flows_into_certificate(self):
        snapshot = EconomicSnapshot(
            chain_id=137,
            block_number=321,
            block_hash="0xblock",
            snapshot_id="snap-321",
            gas_price_gwei=D("2"),
            gas_token_price_usd=D("0.25"),
        )
        route = [
            QuoteLeg("V2-A", "USDC", "WMATIC", D("1000"), D("1010"), D("3"), 999999, 321, "q1"),
            QuoteLeg("V2-B", "WMATIC", "USDC", D("1010"), D("1002"), D("3"), None, 321, "q2"),
        ]
        cert, gas = certify_executor_path(
            opportunity_id="opp-1",
            snapshot=snapshot,
            route=route,
            loan_usd=D("1000"),
            flash_loan_fee_usd=D("1"),
            intent_builder=FakeBuilder(),
            intent={"executionId": "0x01"},
            executor_address="0x00000000000000000000000000000000000000aa",
            sender_address="0x00000000000000000000000000000000000000bb",
            rpc=FakeRpc(),
            gas_rpc_url="test://rpc",
        )
        self.assertEqual(gas.gas_units, 100000)
        self.assertEqual(cert.execution_gas_units, 100000)
        self.assertEqual(cert.gas_cost_usd, D("0.00005"))
        self.assertEqual(cert.block_number, 321)
        self.assertTrue(cert.executable)
        self.assertEqual(cert.gross_profit_usd, D("2"))
        self.assertEqual(cert.conservative_net_profit_usd, D("0.99995"))

    def test_zero_gas_estimate_fails_closed(self):
        snapshot = EconomicSnapshot(137, 321, "0xblock", "snap-321", D("2"), D("0.25"))
        route = [QuoteLeg("V2", "USDC", "USDC", D("1000"), D("1001"), D("0"), None, 321, "q")]
        with self.assertRaises(Exception):
            certify_executor_path(
                opportunity_id="opp-2", snapshot=snapshot, route=route,
                loan_usd=D("1000"), flash_loan_fee_usd=D("1"),
                intent_builder=FakeBuilder(), intent={"executionId": "0x02"},
                executor_address="0x00000000000000000000000000000000000000aa",
                sender_address="0x00000000000000000000000000000000000000bb",
                rpc=FakeRpc("0x0"), gas_rpc_url="test://rpc",
            )


if __name__ == "__main__":
    unittest.main()
