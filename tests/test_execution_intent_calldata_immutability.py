import unittest

from eth_account import Account
from eth_account.messages import encode_typed_data

from execution.intent import ExecutionIntentBuilder


class ExecutionIntentCalldataImmutabilityTests(unittest.TestCase):
    def setUp(self):
        self.private_key = "0x0123456789012345678901234567890123456789012345678901234567890123"
        self.contract = "0x1111111111111111111111111111111111111111"
        self.builder = ExecutionIntentBuilder(self.private_key, self.contract, 137)
        self.intent = {
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

    def test_build_calldata_does_not_resign_existing_signature(self):
        signed = self.builder.sign_intent(self.intent)
        calldata_a = self.builder.build_calldata(signed)
        calldata_b = self.builder.build_calldata(signed)
        self.assertEqual(calldata_a, calldata_b)
        signature = signed["signature"]
        typed = encode_typed_data(full_message=self.builder.build_typed_data(self.intent))
        self.assertEqual(Account.recover_message(typed, signature=signature).lower(), self.builder.account.address.lower())

    def test_build_calldata_requires_existing_signature(self):
        with self.assertRaises(ValueError):
            self.builder.build_calldata(self.intent)

    def test_mutated_intent_with_old_signature_fails_closed(self):
        signed = self.builder.sign_intent(self.intent)
        mutated = dict(signed)
        mutated["amountBorrow"] += 1
        with self.assertRaises(ValueError):
            self.builder.build_calldata(mutated)
        self.assertEqual(mutated["signature"], signed["signature"])


if __name__ == "__main__":
    unittest.main()
