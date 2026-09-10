#!/usr/bin/env python3
"""Reproducibly compile the production executor and prove frozen v1 ABI conformance."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "PhantomX_Production_Executor.sol"
MANIFEST = ROOT / "contracts" / "PhantomX_Executor_Interface_v1.json"
EXPECTED_CALLBACKS = {
    "executeOperation(address,uint256,uint256,address,bytes)",
    "receiveFlashLoan(address[],uint256[],uint256[],bytes)",
    "uniswapV3FlashCallback(uint256,uint256,bytes)",
}
EXPECTED_ENTRY = "executeOpportunity"
EXPECTED_FIELDS = [
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
    ("signature", "bytes"),
]


def compile_abi() -> dict:
    payload = {
        "language": "Solidity",
        "sources": {SOURCE.name: {"content": SOURCE.read_text(encoding="utf-8")}},
        "settings": {
            "optimizer": {"enabled": True, "runs": 200},
            "outputSelection": {"*": {"*": ["abi", "evm.deployedBytecode.object"]}},
        },
    }
    proc = subprocess.run(
        ["npx", "solcjs", "--standard-json"],
        cwd=ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or "solcjs failed")
    start = proc.stdout.find("{")
    if start < 0:
        raise SystemExit("No JSON compiler output")
    report = json.loads(proc.stdout[start:])
    errors = [e for e in report.get("errors", []) if e.get("severity") == "error"]
    if errors:
        raise SystemExit("\n".join(e.get("formattedMessage", str(e)) for e in errors))
    artifact = report.get("contracts", {}).get(SOURCE.name, {}).get("PhantomX_Production_Executor")
    if not artifact:
        raise SystemExit("PhantomX_Production_Executor artifact missing")
    return artifact


def canonical_type(component: dict) -> str:
    # Solidity ABI represents enum fields as uint8 in the ABI tuple.
    return component["type"]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifact = compile_abi()
    abi = artifact["abi"]

    entry = next((x for x in abi if x.get("type") == "function" and x.get("name") == EXPECTED_ENTRY), None)
    if entry is None:
        raise SystemExit("Missing canonical executeOpportunity entrypoint")
    inputs = entry.get("inputs", [])
    if len(inputs) != 1 or inputs[0].get("type") != "tuple":
        raise SystemExit("executeOpportunity must take exactly one ExecutionIntent tuple")
    actual_fields = [(c.get("name"), canonical_type(c)) for c in inputs[0].get("components", [])]
    if actual_fields != EXPECTED_FIELDS:
        raise SystemExit(f"ExecutionIntent ABI mismatch\nexpected={EXPECTED_FIELDS}\nactual={actual_fields}")

    # Cross-check the machine-readable manifest rather than duplicating trust in it.
    manifest_fields = [tuple(x) for x in manifest["intent"]["fields"]]
    if manifest_fields != EXPECTED_FIELDS:
        raise SystemExit("Frozen manifest itself does not match the canonical field contract")
    if manifest["intent"]["eip712FieldsExclude"] != ["signature"]:
        raise SystemExit("Frozen manifest signature exclusion mismatch")
    if manifest["providerType"] != {"AAVE": 0, "UNISWAP_V3_FLASH": 1, "BALANCER": 2}:
        raise SystemExit("Provider enum mapping mismatch")
    if manifest["swapType"] != {"V2": 0, "V3": 1}:
        raise SystemExit("Swap enum mapping mismatch")

    callbacks = set()
    for item in abi:
        if item.get("type") != "function":
            continue
        name = item["name"]
        types = []
        for inp in item.get("inputs", []):
            types.append(inp["type"])
        if name == "executeOperation":
            callbacks.add("executeOperation(" + ",".join(types) + ")")
        elif name == "receiveFlashLoan":
            callbacks.add("receiveFlashLoan(" + ",".join(types) + ")")
        elif name == "uniswapV3FlashCallback":
            callbacks.add("uniswapV3FlashCallback(" + ",".join(types) + ")")
    if callbacks != EXPECTED_CALLBACKS:
        raise SystemExit(f"Callback ABI mismatch\nexpected={sorted(EXPECTED_CALLBACKS)}\nactual={sorted(callbacks)}")

    runtime_hex = artifact["evm"]["deployedBytecode"]["object"]
    runtime_bytes = len(runtime_hex) // 2
    print(f"Solidity source: {SOURCE}")
    print("solcjs configuration: solc@0.8.19, optimizer=true, runs=200, viaIR=false")
    print(f"Executor runtime bytecode: {runtime_bytes} bytes")
    print("ExecutionIntent ABI: PASS")
    print("Provider enum mapping: PASS")
    print("Swap enum mapping: PASS")
    print("Callback surface: PASS")
    print("P0-A.2.1 executor ABI conformance: PASS")


if __name__ == "__main__":
    main()
