"""Fail-closed deployed-executor identity preflight primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ExecutorIdentity:
    address: str
    chain_id: int
    code_hash: str
    code_size: int
    owner: str
    domain_separator: str


def _rpc(rpc: Any, method: str, params: list[Any], rpc_url: str) -> Any:
    return rpc.call(method, params, rpc_url=rpc_url)


def _hex_bytes(value: Any, field: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{field} must be a hex string")
    try:
        return bytes.fromhex(value[2:])
    except ValueError as exc:
        raise ValueError(f"{field} is invalid hex") from exc


def verify_deployed_executor(
    *,
    rpc: Any,
    rpc_url: str,
    address: str,
    expected_chain_id: int = 137,
    expected_code_hash: str | None = None,
    owner_selector: str = "0x8da5cb5b",
    domain_separator_selector: str = "0x3644e515",
    keccak: Callable[[bytes], bytes],
) -> ExecutorIdentity:
    """Prove chain, bytecode presence/hash, and EIP-712 identity before execution.

    No execution/gas estimate is authorized by this helper. Any failed probe raises.
    """
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError("executor address is invalid")
    chain_hex = _rpc(rpc, "eth_chainId", [], rpc_url)
    chain_id = int(chain_hex, 16)
    if chain_id != expected_chain_id:
        raise ValueError(f"unexpected chain id: {chain_id}")

    code_hex = _rpc(rpc, "eth_getCode", [address, "latest"], rpc_url)
    code = _hex_bytes(code_hex, "executor bytecode")
    if not code:
        raise ValueError("executor has no deployed bytecode")
    code_hash = "0x" + keccak(code).hex()
    if expected_code_hash is not None and code_hash.lower() != expected_code_hash.lower():
        raise ValueError("deployed executor bytecode hash mismatch")

    owner_hex = _rpc(rpc, "eth_call", [{"to": address, "data": owner_selector}, "latest"], rpc_url)
    owner = "0x" + _hex_bytes(owner_hex, "owner() result")[-20:].hex()
    domain_hex = _rpc(rpc, "eth_call", [{"to": address, "data": domain_separator_selector}, "latest"], rpc_url)
    domain = "0x" + _hex_bytes(domain_hex, "DOMAIN_SEPARATOR() result").hex()
    if len(domain) != 66:
        raise ValueError("DOMAIN_SEPARATOR() result must be bytes32")

    return ExecutorIdentity(
        address=address,
        chain_id=chain_id,
        code_hash=code_hash,
        code_size=len(code),
        owner=owner,
        domain_separator=domain,
    )
