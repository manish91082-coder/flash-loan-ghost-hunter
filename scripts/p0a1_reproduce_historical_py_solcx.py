from __future__ import annotations

import json
import pathlib
from typing import Any

import solcx
from Crypto.Hash import keccak

SOURCE = pathlib.Path("flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol")
SOLC_VERSION = "0.8.20"
DEPLOYED_RUNTIME_HASH = "84d804402ada3bac76426aad699fcc5d95bc39d6237a7f15eda238eff606d2fb"
OUT_DIR = pathlib.Path("/tmp/phantomx-p0a1-lineage")


def eth_keccak256(data: bytes) -> str:
    digest = keccak.new(digest_bits=256)
    digest.update(data)
    return digest.hexdigest()


def canonical_type(item: dict[str, Any]) -> str:
    typ = item["type"]
    if typ.startswith("tuple"):
        suffix = typ[len("tuple") :]
        components = item.get("components", [])
        return "(" + ",".join(canonical_type(c) for c in components) + ")" + suffix
    return typ


def selector_from_abi(item: dict[str, Any]) -> str:
    signature = item["name"] + "(" + ",".join(canonical_type(x) for x in item.get("inputs", [])) + ")"
    return eth_keccak256(signature.encode())[:8]


def main() -> int:
    if not SOURCE.is_file():
        raise SystemExit(f"missing source: {SOURCE}")

    installed = {str(v) for v in solcx.get_installed_solc_versions()}
    if SOLC_VERSION not in installed:
        solcx.install_solc(SOLC_VERSION)

    source = SOURCE.read_text(encoding="utf-8")
    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin", "bin-runtime"],
        solc_version=SOLC_VERSION,
    )

    contract_id = next(k for k in compiled if k.rsplit(":", 1)[-1] == "PhantomXMVP")
    artifact = compiled[contract_id]
    runtime_hex = artifact["bin-runtime"].removeprefix("0x")
    creation_hex = artifact["bin"].removeprefix("0x")
    runtime_hash = eth_keccak256(bytes.fromhex(runtime_hex))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "runtime.hex").write_text(runtime_hex + "\n", encoding="utf-8")
    (OUT_DIR / "creation.hex").write_text(creation_hex + "\n", encoding="utf-8")
    (OUT_DIR / "abi.json").write_text(json.dumps(artifact["abi"], indent=2), encoding="utf-8")

    functions = []
    for item in artifact["abi"]:
        if item.get("type") == "function":
            signature = item["name"] + "(" + ",".join(canonical_type(x) for x in item.get("inputs", [])) + ")"
            functions.append({"signature": signature, "selector": "0x" + selector_from_abi(item)})
    functions.sort(key=lambda x: x["signature"])
    (OUT_DIR / "function_selectors.json").write_text(json.dumps(functions, indent=2), encoding="utf-8")

    result = {
        "source": str(SOURCE),
        "compiler": SOLC_VERSION,
        "compiler_binary": str(solcx.get_solc_version()),
        "compile_api": "py-solc-x compile_source",
        "optimizer_explicitly_configured": False,
        "viaIR_explicitly_configured": False,
        "runtime_bytes": len(bytes.fromhex(runtime_hex)),
        "creation_bytes": len(bytes.fromhex(creation_hex)),
        "reproduced_runtime_keccak": "0x" + runtime_hash,
        "deployed_runtime_keccak": "0x" + DEPLOYED_RUNTIME_HASH,
        "exact_runtime_match": runtime_hash == DEPLOYED_RUNTIME_HASH,
        "function_selectors": functions,
    }
    (OUT_DIR / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    # Mismatch is a valid forensic result. A separate CI gate decides pass/fail.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
