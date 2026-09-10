import unittest

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import keccak

from execution.intent import ExecutionIntentBuilder


class ExecutionIntentEIP712Tests(unittest.TestCase):
    def setUp(self):
        self.private_key = "0x0123456789012345678901234567890123456789012345678901234567890123"
        self.contract = "0x1111111111111111111111111111111111111111"
        self.chain_id = 137
        self.builder = ExecutionIntentBuilder(self.private_key, self.contract, self.chain_id)
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

    @staticmethod
    def _word_uint(value):
        return int(value).to_bytes(32, "big")

    @staticmethod
    def _word_address(value):
        return bytes.fromhex(value[2:]).rjust(32, b"\x00")

    def test_python_typed_data_hash_matches_solidity_word_encoding(self):
        typed = self.builder.build_typed_data(self.intent)
        signable = encode_typed_data(full_message=typed)

        type_hash = keccak(text=(
            "ExecutionIntent(bytes32 executionId,uint8 providerType,address providerAddress,"
            "address tokenBorrow,uint256 amountBorrow,uint8 swap1Type,address routerA,bytes pathA,"
            "uint256 minAmountOut1,uint8 swap2Type,address routerB,bytes pathB,uint256 minAmountOutFinal,"
            "uint256 minimumOnChainSurplus,uint256 maximumGasLimit,uint256 deadline)"
        ))
        words = [
            type_hash,
            bytes.fromhex(self.intent["executionId"][2:]),
            self._word_uint(self.intent["providerType"]),
            self._word_address(self.intent["providerAddress"]),
            self._word_address(self.intent["tokenBorrow"]),
            self._word_uint(self.intent["amountBorrow"]),
            self._word_uint(self.intent["swap1Type"]),
            self._word_address(self.intent["routerA"]),
            keccak(self.intent["pathA"]),
            self._word_uint(self.intent["minAmountOut1"]),
            self._word_uint(self.intent["swap2Type"]),
            self._word_address(self.intent["routerB"]),
            keccak(self.intent["pathB"]),
            self._word_uint(self.intent["minAmountOutFinal"]),
            self._word_uint(self.intent["minimumOnChainSurplus"]),
            self._word_uint(self.intent["maximumGasLimit"]),
            self._word_uint(self.intent["deadline"]),
        ]
        solidity_equivalent_struct_hash = keccak(b"".join(words))
        self.assertEqual(signable.body, solidity_equivalent_struct_hash)

        domain_type_hash = keccak(text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
        domain_hash = keccak(
            domain_type_hash
            + keccak(text="PhantomX Executor")
            + keccak(text="1")
            + self._word_uint(self.chain_id)
            + self._word_address(self.contract)
        )
        solidity_equivalent_digest = keccak(b"\x19\x01" + domain_hash + solidity_equivalent_struct_hash)
        self.assertEqual(signable.version + signable.header + signable.body, b"\x01" + domain_hash + solidity_equivalent_struct_hash)
        self.assertEqual(keccak(b"\x19" + signable.version + signable.header + signable.body), solidity_equivalent_digest)

    def test_signature_recovers_from_canonical_digest(self):
        signed = self.builder.sign_intent(self.intent)
        typed = self.builder.build_typed_data(self.intent)
        signable = encode_typed_data(full_message=typed)
        recovered = Account.recover_message(signable, signature=signed["signature"])
        self.assertEqual(recovered.lower(), self.builder.account.address.lower())


if __name__ == "__main__":
    unittest.main()
