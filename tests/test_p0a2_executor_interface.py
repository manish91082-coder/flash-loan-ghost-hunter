import json
from pathlib import Path


def test_canonical_executor_interface_manifest_is_valid():
    manifest = json.loads(Path("contracts/PhantomX_Executor_Interface_v1.json").read_text())
    fields = manifest["intent"]["fields"]
    assert [name for name, _ in fields] == [
        "executionId",
        "providerType",
        "providerAddress",
        "tokenBorrow",
        "amountBorrow",
        "swap1Type",
        "routerA",
        "pathA",
        "minAmountOut1",
        "swap2Type",
        "routerB",
        "pathB",
        "minAmountOutFinal",
        "minimumOnChainSurplus",
        "maximumGasLimit",
        "deadline",
        "signature",
    ]
    assert manifest["intent"]["eip712FieldsExclude"] == ["signature"]
    assert manifest["providerType"] == {"AAVE": 0, "UNISWAP_V3_FLASH": 1, "BALANCER": 2}
    assert manifest["swapType"] == {"V2": 0, "V3": 1}
    assert manifest["route"]["legs"] == 2
    assert manifest["economicBoundary"]["offchainAuthority"] == "phantomx_core.economic_truth.evaluate_route"
    assert manifest["economicBoundary"]["gasAuthority"] == "execution.economic_gate.certify_executor_path"
    assert manifest["capabilities"]["hardcodedMarketEconomics"] is False


def test_canonical_intent_signature_schema_matches_manifest():
    manifest = json.loads(Path("contracts/PhantomX_Executor_Interface_v1.json").read_text())
    schema = {name: typ for name, typ in manifest["intent"]["fields"] if name != "signature"}
    assert list(schema.items()) == [
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
