import unittest
from decimal import Decimal as D

from phantomx_core.transaction_gas import GasEstimate, estimate_transaction_gas
from phantomx_core.economic_truth import EconomicTruthError


class FakeRpc:
    def __init__(self, result="0x01"):
        self.result = result
        self.calls = []

    def call(self, method, params, *, rpc_url=None):
        self.calls.append((method, params, rpc_url))
        return type("Result", (), {"result": self.result})()


class TransactionGasTests(unittest.TestCase):
    def test_estimate_uses_real_transaction_and_pinned_block(self):
        rpc = FakeRpc("0x1e848")
        estimate = estimate_transaction_gas(
            rpc=rpc,
            block_number=123,
            tx={
                "to": "0x00000000000000000000000000000000000000aa",
                "data": "0xabcdef",
                "from": "0x00000000000000000000000000000000000000bb",
            },
            gas_price_gwei=D("30"),
            gas_token_price_usd=D("0.25"),
            rpc_url="test://rpc",
        )
        self.assertEqual(estimate.gas_units, int("0x1e848", 16))
        self.assertEqual(estimate.block_number, 123)
        self.assertEqual(estimate.rpc_url, "test://rpc")
        # 125,000 gas × 30 gwei × $0.25/POL = $0.0009375.
        self.assertEqual(estimate.gas_cost_usd, D("0.0009375"))
        self.assertEqual(rpc.calls[0][0], "eth_estimateGas")
        self.assertEqual(rpc.calls[0][1][1], hex(123))
        self.assertEqual(rpc.calls[0][1][0]["value"], "0x0")

    def test_invalid_transaction_is_blocked(self):
        with self.assertRaises(EconomicTruthError):
            estimate_transaction_gas(
                rpc=FakeRpc(),
                block_number=123,
                tx={"to": "bad", "data": "0x01"},
                gas_price_gwei=D("30"),
                gas_token_price_usd=D("0.25"),
                rpc_url="test://rpc",
            )

    def test_zero_gas_result_is_blocked(self):
        with self.assertRaises(EconomicTruthError):
            estimate_transaction_gas(
                rpc=FakeRpc("0x0"),
                block_number=123,
                tx={"to": "0x00000000000000000000000000000000000000aa", "data": "0x01"},
                gas_price_gwei=D("30"),
                gas_token_price_usd=D("0.25"),
                rpc_url="test://rpc",
            )

    def test_gas_estimate_object_rejects_non_positive_values(self):
        estimate = GasEstimate(
            gas_units=0,
            block_number=1,
            rpc_url="test://rpc",
            gas_price_gwei=D("1"),
            gas_token_price_usd=D("1"),
            gas_cost_usd=D("0"),
        )
        with self.assertRaises(EconomicTruthError):
            estimate.validate()


if __name__ == "__main__":
    unittest.main()
