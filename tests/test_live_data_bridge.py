import unittest
from decimal import Decimal as D
from unittest.mock import patch

from phantomx_core.block_pinned_rpc import BlockPinnedRpc, RpcResult
from phantomx_core.live_data_bridge import collect_live_data_snapshot


class LiveBridgeTests(unittest.TestCase):
    def test_all_pool_reads_use_captured_block_and_same_rpc(self):
        rpc = BlockPinnedRpc(["https://rpc.test"])
        calls = []

        def fake_call(method, params, rpc_url=None):
            calls.append((method, params, rpc_url))
            if method == "eth_getBlockByNumber":
                return RpcResult({"number": "0x64", "hash": "0xabc"}, rpc_url, 1.0)
            if method == "eth_gasPrice":
                return RpcResult("0x6fc23ac00", rpc_url, 1.0)
            if method == "eth_call":
                return RpcResult("0x" + "01".zfill(64) + "00" * 10, rpc_url, 1.0)
            raise AssertionError(method)

        with patch.object(rpc, "call", side_effect=fake_call):
            from phantomx_core import live_data_bridge
            pools = (
                ("v2", "QuickSwapV2", {
                    "address": "0xpool1", "token0": "WMATIC", "token1": "USDC",
                    "token0_decimals": 18, "token1_decimals": 6,
                    "price_formula": "reserve1_per_reserve0",
                }),
            )
            snap = collect_live_data_snapshot(
                rpc=rpc,
                gas_token_price_usd=D("0.25"),
                pool_groups=pools,
            )

        self.assertEqual(snap.block_number, 100)
        self.assertEqual(snap.source_rpc, "https://rpc.test")
        pool_calls = [c for c in calls if c[0] == "eth_call"]
        self.assertTrue(pool_calls)
        self.assertEqual(pool_calls[0][2], "https://rpc.test")
        self.assertEqual(pool_calls[0][1][1], "0x64")

    def test_pool_failure_does_not_create_fake_price(self):
        rpc = BlockPinnedRpc(["https://rpc.test"])

        def fake_call(method, params, rpc_url=None):
            if method == "eth_getBlockByNumber":
                return RpcResult({"number": "0x64", "hash": "0xabc"}, rpc_url, 1.0)
            if method == "eth_gasPrice":
                return RpcResult("0x6fc23ac00", rpc_url, 1.0)
            if method == "eth_call":
                raise RuntimeError("pool unavailable")
            raise AssertionError(method)

        with patch.object(rpc, "call", side_effect=fake_call):
            snap = collect_live_data_snapshot(
                rpc=rpc,
                gas_token_price_usd=D("0.25"),
                pool_groups=(("v3", "UniswapV3", {
                    "address": "0xpool1", "token0": "WMATIC", "token1": "USDC",
                    "token0_decimals": 18, "token1_decimals": 6,
                    "price_formula": "token0_per_token1_inverted",
                }),),
            )
        self.assertIsNone(snap.pools[0].price_usd)
        with self.assertRaises(Exception):
            snap.require_all_pools_healthy()


if __name__ == "__main__":
    unittest.main()
