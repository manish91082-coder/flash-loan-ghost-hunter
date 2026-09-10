"""Fail-closed deployed-executor identity preflight primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ExecutorIdentity:
    address: str
    chain_id: int
    block_number: int | None
    code_hash: str
    code_size: int
    owner: str
    domain_separator: str


def _rpc(rpc: Any, method: str, params: list[Any], rpc_url: str) -> Any:
    result = rpc.call(method, params, rpc_url=rpc_url)
    return getattr(result, "result", result)


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
    block_number: int | None = None,
    expected_code_hash: str | None = None,
    expected_owner: str | None = None,
    expected_domain_separator: str | None = None,
    owner_selector: str = "0x8da5cb5b",
    domain_separator_selector: str = "0x3644e515",
    keccak: Callable[[bytes], bytes],
) -> ExecutorIdentity:
    """Prove chain, deployed bytecode, and EIP-712 identity before execution.

    ``block_number`` should be the same immutable block used by the economic
    snapshot. Omitting it is permitted for generic diagnostics only. Any failed
    probe raises, so callers cannot silently continue into gas estimation or
    execution with an unknown executor identity.
    """
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError("executor address is invalid")
    if block_number is not None and block_number <= 0:
        raise ValueError("block number must be positive")

    chain_hex = _rpc(rpc, "eth_chainId", [], rpc_url)
    if not isinstance(chain_hex, str):
        raise ValueError("eth_chainId returned invalid data")
    chain_id = int(chain_hex, 16)
    if chain_id != expected_chain_id:
        raise ValueError(f"unexpected chain id: {chain_id}")

    block_tag = hex(block_number) if block_number is not None else "latest"
    code_hex = _rpc(rpc, "eth_getCode", [address, block_tag], rpc_url)
    code = _hex_bytes(code_hex, "executor bytecode")
    if not code:
        raise ValueError("executor has no deployed bytecode")
    code_hash = "0x" + keccak(code).hex()
    if expected_code_hash is not None and code_hash.lower() != expected_code_hash.lower():
        raise ValueError("deployed executor bytecode hash mismatch")

    owner_hex = _rpc(
        rpc,
        "eth_call",
        [{"to": address, "data": owner_selector}, block_tag],
        rpc_url,
    )
    owner_bytes = _hex_bytes(owner_hex, "owner() result")
    if len(owner_bytes) != 32:
        raise ValueError("owner() result must be exactly 32 bytes")
    owner = "0x" + owner_bytes[-20:].hex()
    if expected_owner is not None and owner.lower() != expected_owner.lower():
        raise ValueError("deployed executor owner mismatch")

    domain_hex = _rpc(
        rpc,
        "eth_call",
        [{"to": address, "data": domain_separator_selector}, block_tag],
        rpc_url,
    )
    domain_bytes = _hex_bytes(domain_hex, "DOMAIN_SEPARATOR() result")
    if len(domain_bytes) != 32:
        raise ValueError("DOMAIN_SEPARATOR() result must be exactly 32 bytes")
    domain = "0x" + domain_bytes.hex()
    if expected_domain_separator is not None and domain.lower() != expected_domain_separator.lower():
        raise ValueError("deployed executor domain separator mismatch")

    return ExecutorIdentity(
        address=address,
        chain_id=chain_id,
        block_number=block_number,
        code_hash=code_hash,
        code_size=len(code),
        owner=owner,
        domain_separator=domain,
    )
