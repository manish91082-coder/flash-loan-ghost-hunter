import json
import unittest
from pathlib import Path


class P0A2ExecutorInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(Path("contracts/PhantomX_Executor_Interface_v1.json").read_text(encoding="utf-8"))
        self.expected_fields = [
            ("executionId", "bytes32"),
            ("providerType", "uint8"),
            ("providerAddress", "address"),
            ("tokenBorrow", "address"),
            ("amountBorrow", "uint256"),
            ("swap1Type", "uint8"),
            ("routerA", "address"),
            ("pathA", "bytes"),
            ("minAmountOut1", "uint256"),
            ("swap2Type", "uint8"),
            ("routerB", "address"),
            ("pathB", "bytes"),
            ("minAmountOutFinal", "uint256"),
            ("minimumOnChainSurplus", "uint256"),
            ("maximumGasLimit", "uint256"),
            ("deadline", "uint256"),
        ]

    def test_canonical_executor_interface_manifest_is_valid(self):
        fields = self.manifest["intent"]["fields"]
        self.assertEqual([name for name, _ in fields], [name for name, _ in self.expected_fields] + ["signature"])
        self.assertEqual(self.manifest["intent"]["eip712FieldsExclude"], ["signature"])
        self.assertEqual(self.manifest["providerType"], {"AAVE": 0, "UNISWAP_V3_FLASH": 1, "BALANCER": 2})
        self.assertEqual(self.manifest["swapType"], {"V2": 0, "V3": 1})
        self.assertEqual(self.manifest["route"]["legs"], 2)
        self.assertEqual(self.manifest["economicBoundary"]["offchainAuthority"], "phantomx_core.economic_truth.evaluate_route")
        self.assertEqual(self.manifest["economicBoundary"]["gasAuthority"], "execution.economic_gate.certify_executor_path")
        self.assertFalse(self.manifest["capabilities"]["hardcodedMarketEconomics"])

    def test_canonical_intent_signature_schema_matches_manifest(self):
        schema = {name: typ for name, typ in self.manifest["intent"]["fields"] if name != "signature"}
        self.assertEqual(list(schema.items()), self.expected_fields)


if __name__ == "__main__":
    unittest.main()
