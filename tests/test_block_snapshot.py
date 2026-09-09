import unittest
from decimal import Decimal as D

from phantomx_core.block_snapshot import build_block_snapshot, collect_block_snapshot
from phantomx_core.economic_truth import EconomicTruthError


class RpcStub:
    source_rpc = "test://polygon"

    def __init__(self, block, gas):
        self.block = block
        self.gas = gas

    def __call__(self, method, params):
        if method == "eth_getBlockByNumber":
            self.assert_latest(params)
            return self.block
        if method == "eth_gasPrice":
            return self.gas
        raise AssertionError(method)

    @staticmethod
    def assert_latest(params):
        if params != ["latest", False]:
            raise AssertionError(params)


class BlockSnapshotTests(unittest.TestCase):
    def test_builds_deterministic_snapshot_id(self):
        block = {"number": "0x64", "hash": "0xABCDEF"}
        a = build_block_snapshot(
            chain_id=137, block=block, gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"), source_rpc="test://rpc")
        b = build_block_snapshot(
            chain_id=137, block=block, gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"), source_rpc="test://rpc")
        self.assertEqual(a.snapshot_id, b.snapshot_id)
        self.assertEqual(a.block_number, 100)
        self.assertEqual(a.gas_price_gwei, D("30"))

    def test_missing_hash_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            build_block_snapshot(
                chain_id=137,
                block={"number": "0x64"},
                gas_price_wei=30_000_000_000,
                gas_token_price_usd=D("0.25"),
                source_rpc="test://rpc",
            )

    def test_zero_gas_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            build_block_snapshot(
                chain_id=137,
                block={"number": "0x64", "hash": "0xabc"},
                gas_price_wei=0,
                gas_token_price_usd=D("0.25"),
                source_rpc="test://rpc",
            )

    def test_collect_uses_latest_block_and_real_gas(self):
        stub = RpcStub({"number": "0x2a", "hash": "0xdeadbeef"}, "0x6fc23ac00")
        snap = collect_block_snapshot(
            rpc_call=stub, chain_id=137, gas_token_price_usd=D("0.30"))
        self.assertEqual(snap.block_number, 42)
        self.assertEqual(snap.block_hash, "0xdeadbeef")
        self.assertEqual(snap.gas_price_wei, int("0x6fc23ac00", 16))
        self.assertEqual(snap.source_rpc, "test://polygon")


if __name__ == "__main__":
    unittest.main()
