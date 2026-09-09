import unittest
from decimal import Decimal as D

from execution.gas_integration import estimate_executor_gas


class FakeRpc:
    def __init__(self, result="0x186a0"):
        self.result = result
        self.calls = []

    def call(self, method, params, *, rpc_url=None):
        self.calls.append((method, params, rpc_url))
        return type("Result", (), {"result": self.result})()


class FakeBuilder:
    def __init__(self, calldata=b"\x12\x34"):
        self.calldata = calldata
        self.calls = []

    def build_calldata(self, intent):
        self.calls.append(intent)
        return self.calldata


class GasIntegrationTests(unittest.TestCase):
    def test_exact_executor_calldata_is_estimated(self):
        rpc = FakeRpc()
        builder = FakeBuilder(b"\xaa\xbb\xcc")
        estimate = estimate_executor_gas(
            intent_builder=builder,
            intent={"executionId": "0x01"},
            executor_address="0x00000000000000000000000000000000000000aa",
            sender_address="0x00000000000000000000000000000000000000bb",
            rpc=rpc,
            block_number=321,
            gas_price_gwei=D("2"),
            gas_token_price_usd=D("0.25"),
            rpc_url="test://rpc",
        )
        self.assertEqual(estimate.gas_units, 100000)
        self.assertEqual(builder.calls, [{"executionId": "0x01"}])
        method, params, url = rpc.calls[0]
        self.assertEqual(method, "eth_estimateGas")
        self.assertEqual(params[0]["from"], "0x00000000000000000000000000000000000000bb")
        self.assertEqual(params[0]["to"], "0x00000000000000000000000000000000000000aa")
        self.assertEqual(params[0]["data"], "0xaabbcc")
        self.assertEqual(params[0]["value"], "0x0")
        self.assertEqual(params[1], hex(321))
        self.assertEqual(url, "test://rpc")

    def test_empty_calldata_fails_closed(self):
        with self.assertRaises(Exception):
            estimate_executor_gas(
                intent_builder=FakeBuilder(b""),
                intent={},
                executor_address="0x00000000000000000000000000000000000000aa",
                sender_address="0x00000000000000000000000000000000000000bb",
                rpc=FakeRpc(),
                block_number=321,
                gas_price_gwei=D("2"),
                gas_token_price_usd=D("0.25"),
                rpc_url="test://rpc",
            )


if __name__ == "__main__":
    unittest.main()
