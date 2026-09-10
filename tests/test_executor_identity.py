from phantomx_core.executor_identity import verify_deployed_executor


class FakeRpc:
    def __init__(self, chain_id="0x89", code="0x60016000f3", owner_word=None, domain_word=None):
        self.calls = []
        self.chain_id = chain_id
        self.code = code
        self.owner_word = owner_word or ("00" * 12 + "11" * 20)
        self.domain_word = domain_word or ("22" * 32)

    def call(self, method, params, rpc_url=None):
        self.calls.append((method, params, rpc_url))
        if method == "eth_chainId":
            return self.chain_id
        if method == "eth_getCode":
            return self.code
        if method == "eth_call":
            data = params[0]["data"]
            if data == "0x8da5cb5b":
                return "0x" + self.owner_word
            if data == "0x3644e515":
                return "0x" + self.domain_word
        raise AssertionError(method)


def fake_keccak(data: bytes) -> bytes:
    return bytes.fromhex("33" * 32)


def test_identity_preflight_proves_chain_code_owner_and_domain():
    rpc = FakeRpc()
    result = verify_deployed_executor(
        rpc=rpc,
        rpc_url="https://rpc.example",
        address="0x" + "aa" * 20,
        keccak=fake_keccak,
    )
    assert result.chain_id == 137
    assert result.code_size == 6
    assert result.code_hash == "0x" + "33" * 32
    assert result.owner == "0x" + "11" * 20
    assert result.domain_separator == "0x" + "22" * 32


def test_identity_preflight_rejects_wrong_chain():
    rpc = FakeRpc(chain_id="0x1")
    try:
        verify_deployed_executor(
            rpc=rpc,
            rpc_url="https://rpc.example",
            address="0x" + "aa" * 20,
            keccak=fake_keccak,
        )
    except ValueError as exc:
        assert "chain id" in str(exc)
    else:
        raise AssertionError("wrong chain accepted")


def test_identity_preflight_rejects_missing_code():
    rpc = FakeRpc(code="0x")
    try:
        verify_deployed_executor(
            rpc=rpc,
            rpc_url="https://rpc.example",
            address="0x" + "aa" * 20,
            keccak=fake_keccak,
        )
    except ValueError as exc:
        assert "bytecode" in str(exc)
    else:
        raise AssertionError("empty bytecode accepted")


def test_identity_preflight_rejects_code_hash_mismatch():
    rpc = FakeRpc()
    try:
        verify_deployed_executor(
            rpc=rpc,
            rpc_url="https://rpc.example",
            address="0x" + "aa" * 20,
            expected_code_hash="0x" + "44" * 32,
            keccak=fake_keccak,
        )
    except ValueError as exc:
        assert "bytecode hash" in str(exc)
    else:
        raise AssertionError("wrong bytecode hash accepted")
