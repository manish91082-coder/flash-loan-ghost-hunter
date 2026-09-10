import unittest
from decimal import Decimal as D

from execution.economic_gate import certify_executor_path
from execution.intent import ExecutionIntentBuilder
from phantomx_core.economic_truth import EconomicSnapshot, QuoteLeg


PRIVATE_KEY = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
EXECUTOR = "0x00000000000000000000000000000000000000aa"
SENDER = "0x00000000000000000000000000000000000000bb"


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
    def _snapshot_and_route(self):
        snapshot = EconomicSnapshot(137, 321, "0xblock", "snap-321", D("2"), D("0.25"))
        route = [
            QuoteLeg("V2-A", "USDC", "WMATIC", D("1000"), D("1010"), D("3"), 999999, 321, "q1"),
            QuoteLeg("V2-B", "WMATIC", "USDC", D("1010"), D("1002"), D("3"), None, 321, "q2"),
        ]
        return snapshot, route

    def _signed_intent(self, builder):
        unsigned = {
            "executionId": "0x" + "ab" * 32,
            "providerType": 0,
            "providerAddress": "0x2222222222222222222222222222222222222222",
            "tokenBorrow": "0x3333333333333333333333333333333333333333",
            "amountBorrow": 123456789,
            "swap1Type": 0,
            "routerA": "0x4444444444444444444444444444444444444444",
            "pathA": b"v2-path",
            "minAmountOut1": 120000000,
            "swap2Type": 1,
            "routerB": "0x5555555555555555555555555555555555555555",
            "pathB": b"v3-path",
            "minAmountOutFinal": 125000000,
            "minimumOnChainSurplus": 500000,
            "maximumGasLimit": 500000,
            "deadline": 2000000000,
        }
        return builder.sign_intent(unsigned)

    def test_exact_gas_flows_into_certificate(self):
        snapshot, route = self._snapshot_and_route()
        rpc = FakeRpc()
        cert, gas = certify_executor_path(
            opportunity_id="opp-1", snapshot=snapshot, route=route,
            loan_usd=D("1000"), flash_loan_fee_usd=D("1"),
            intent_builder=FakeBuilder(), intent={"executionId": "0x01"},
            executor_address=EXECUTOR, sender_address=SENDER,
            rpc=rpc, gas_rpc_url="test://rpc",
        )
        self.assertEqual(gas.gas_units, 100000)
        self.assertEqual(cert.execution_gas_units, 100000)
        self.assertEqual(cert.gas_cost_usd, D("0.00005"))
        self.assertEqual(cert.block_number, 321)
        self.assertTrue(cert.executable)
        self.assertEqual(cert.gross_profit_usd, D("2"))
        self.assertEqual(cert.conservative_net_profit_usd, D("0.99995"))

    def test_exact_signed_intent_calldata_is_the_transaction_being_estimated(self):
        snapshot, route = self._snapshot_and_route()
        builder = ExecutionIntentBuilder(PRIVATE_KEY, EXECUTOR, 137)
        signed = self._signed_intent(builder)
        expected_calldata = builder.build_calldata(signed)
        rpc = FakeRpc()

        cert, gas = certify_executor_path(
            opportunity_id="opp-signed-1", snapshot=snapshot, route=route,
            loan_usd=D("1000"), flash_loan_fee_usd=D("1"),
            intent_builder=builder, intent=signed,
            executor_address=EXECUTOR, sender_address=SENDER,
            rpc=rpc, gas_rpc_url="test://rpc",
        )

        self.assertTrue(cert.executable)
        self.assertEqual(gas.gas_units, 100000)
        self.assertEqual(len(rpc.calls), 1)
        method, params, rpc_url = rpc.calls[0]
        self.assertEqual(method, "eth_estimateGas")
        self.assertEqual(rpc_url, "test://rpc")
        self.assertEqual(params[0]["from"], SENDER)
        self.assertEqual(params[0]["to"], EXECUTOR)
        self.assertEqual(params[0]["data"], "0x" + expected_calldata.hex())
        self.assertEqual(params[0]["value"], "0x0")
        self.assertEqual(params[1], "0x141")

    def test_zero_gas_estimate_fails_closed(self):
        snapshot, route = self._snapshot_and_route()
        with self.assertRaises(Exception):
            certify_executor_path(
                opportunity_id="opp-2", snapshot=snapshot, route=route,
                loan_usd=D("1000"), flash_loan_fee_usd=D("1"),
                intent_builder=FakeBuilder(), intent={"executionId": "0x02"},
                executor_address=EXECUTOR, sender_address=SENDER,
                rpc=FakeRpc("0x0"), gas_rpc_url="test://rpc",
            )


if __name__ == "__main__":
    unittest.main()
