from __future__ import annotations

import hashlib
import json
from pathlib import Path

import solcx

SOURCE = Path("flash loan ghost hunter antigravity MVP/contracts/src/PhantomXMVP.sol")
SOLC_VERSION = "0.8.20"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if not solcx.get_installed_solc_versions() or solcx.SemVer(SOLC_VERSION) not in solcx.get_installed_solc_versions():
        solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)

    # Mirror the historical deployer's actual compilation call exactly first.
    original = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    contract_id, interface = original.popitem()

    # Same compile_source pipeline, requesting runtime bytecode so we can hash
    # the deployed portion without changing compiler/version/settings.
    runtime_result = solcx.compile_source(
        source,
        output_values=["bin-runtime"],
        solc_version=SOLC_VERSION,
    )
    runtime = runtime_result[contract_id]["bin-runtime"]

    payload = {
        "compiler": solcx.get_solc_version().version,
        "contract_id": contract_id,
        "creation_bytecode_bytes": len(interface["bin"]) // 2,
        "runtime_bytes": len(runtime) // 2,
        "runtime_keccak256": "0x" + hashlib.sha3_256(bytes.fromhex(runtime)).hexdigest(),
        "runtime_keccak_note": "sha3_256 is recorded only as a secondary local digest; the execution probe uses Ethereum Keccak-256.",
        "abi_items": len(interface["abi"]),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
    }
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/p0a-historical-py-solc-x.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
