import unittest
from decimal import Decimal as D

from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.economic_truth import EconomicTruthError
from phantomx_core.live_pool_snapshot import (
    parse_slot0_price_usd,
    parse_v2_price_usd,
    read_configured_pool,
)


class PinnedCallRecorder:
    def __init__(self, result: str):
        self.result = result
        self.calls = []

    def __call__(self, pool: str, selector: str, block: int) -> str:
        self.calls.append((pool, selector, block))
        return self.result


def word(value: int) -> str:
    return value.to_bytes(32, "big").hex()


class LivePoolSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = build_block_snapshot(
            chain_id=137,
            block={"number": "0x64", "hash": "0xabc"},
            gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"),
            source_rpc="test://polygon",
        )

    def test_v2_reader_passes_exact_snapshot_block(self):
        # 1000 base units vs 2000000 quote units with 18/6 decimals = 2 quote/base.
        result = "0x" + word(10**18 * 1000) + word(2_000_000 * 1000) + word(1)
        rpc = PinnedCallRecorder(result)
        cfg = {
            "address": "0xpool",
            "token0": "WMATIC",
            "token1": "USDC",
            "token0_decimals": 18,
            "token1_decimals": 6,
            "price_formula": "reserve1_per_reserve0",
        }
        read = read_configured_pool(
            snapshot=self.snapshot,
            config=cfg,
            venue="QuickSwapV2",
            rpc_call_at_block=rpc,
            kind="v2",
        )
        self.assertEqual(read.block_number, 100)
        self.assertEqual(read.price_usd, D("2"))
        self.assertEqual(rpc.calls[0][2], 100)
        self.assertEqual(rpc.calls[0][1], "0x0902f1ac")

    def test_v3_reader_passes_exact_snapshot_block(self):
        sqrt_x96 = 2**96
        rpc = PinnedCallRecorder("0x" + word(sqrt_x96) + word(0) * 6)
        cfg = {
            "address": "0xpool",
            "token0": "WMATIC",
            "token1": "USDC",
            "token0_decimals": 18,
            "token1_decimals": 6,
            "price_formula": "token0_per_token1_inverted",
        }
        read = read_configured_pool(
            snapshot=self.snapshot,
            config=cfg,
            venue="UniswapV3",
            rpc_call_at_block=rpc,
            kind="v3",
        )
        self.assertEqual(read.block_number, 100)
        self.assertEqual(read.price_usd, D("1000000000000"))
        self.assertEqual(rpc.calls[0][2], 100)
        self.assertEqual(rpc.calls[0][1], "0x3850c7bd")

    def test_missing_or_invalid_read_fails_closed_at_adapter_boundary(self):
        def boom(pool, selector, block):
            raise RuntimeError("RPC unavailable")
        cfg = {
            "address": "0xpool",
            "token0": "WMATIC",
            "token1": "USDC",
            "token0_decimals": 18,
            "token1_decimals": 6,
            "price_formula": "reserve1_per_reserve0",
        }
        read = read_configured_pool(
            snapshot=self.snapshot,
            config=cfg,
            venue="QuickSwapV2",
            rpc_call_at_block=boom,
            kind="v2",
        )
        self.assertIsNone(read.price_usd)
        self.assertIn("RPC unavailable", read.error)

    def test_v2_zero_reserves_fail_closed(self):
        result = "0x" + word(0) + word(1000) + word(1)
        with self.assertRaises(EconomicTruthError):
            parse_v2_price_usd(result, 18, 6, True)

    def test_v3_zero_sqrt_price_fails_closed(self):
        result = "0x" + word(0) + word(0) * 6
        with self.assertRaises(EconomicTruthError):
            parse_slot0_price_usd(result, 18, 6, True)


if __name__ == "__main__":
    unittest.main()
