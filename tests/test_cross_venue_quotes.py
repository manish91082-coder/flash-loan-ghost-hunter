import unittest
from decimal import Decimal as D

from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.exact_quote_engine import (
    DECIMALS, FEE, GET_AMOUNTS_OUT, QUOTE_EXACT_INPUT_SINGLE, SYMBOL, TOKEN0, TOKEN1,
    TokenMeta, quote_cross_venue_roundtrip,
)


class CrossVenueQuoteTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = build_block_snapshot(
            chain_id=137,
            block={"number": "0x64", "hash": "0xabc"},
            gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"),
            source_rpc="test://polygon",
        )
        self.usdc = "0x0000000000000000000000000000000000000001"
        self.asset = "0x0000000000000000000000000000000000000002"

    def rpc(self, target, data, block):
        self.assertEqual(block, 100)
        if target in {"v3pool", "v2pool"}:
            if data == TOKEN0:
                return "0x" + self.usdc[2:].rjust(64, "0")
            if data == TOKEN1:
                return "0x" + self.asset[2:].rjust(64, "0")
            if target == "v3pool" and data == FEE:
                return "0x" + f"{500:064x}"
        if target in {self.usdc, self.asset}:
            if data == DECIMALS:
                return "0x" + f"{(6 if target == self.usdc else 18):064x}"
            if data == SYMBOL:
                symbol = b"USDC" if target == self.usdc else b"WMATIC"
                return "0x" + (32).to_bytes(32, "big").hex() + len(symbol).to_bytes(32, "big").hex() + symbol.ljust(32, b"\x00").hex()
        if target == "quoter" and data.startswith(QUOTE_EXACT_INPUT_SINGLE):
            return "0x" + f"{500000000000000000:064x}" + f"{1:064x}" + f"{2:064x}" + f"{125000:064x}"
        if target == "router" and data.startswith(GET_AMOUNTS_OUT):
            # Decode the second query's amountIn from the last calldata word pair.
            amount_in_raw = int(data[-64:], 16)
            return "0x" + f"{32:064x}" + f"{2:064x}" + f"{amount_in_raw:064x}" + f"{510000:064x}"
        raise AssertionError((target, data))

    def test_cross_venue_v3_to_v2_uses_first_output_as_second_input(self):
        first, second = quote_cross_venue_roundtrip(
            snapshot=self.snapshot,
            v3_pool="v3pool",
            v2_pool="v2pool",
            loan_usd=D("1"),
            rpc_call_at_block=self.rpc,
            v2_gas_units=90_000,
            direction="V3_TO_V2",
        )
        self.assertEqual(first.venue, "UniswapV3")
        self.assertEqual(second.venue, "QuickSwapV2")
        self.assertEqual(second.amount_in_raw, first.amount_out_raw)
        self.assertEqual(first.quoted_block, second.quoted_block,)

    def test_incompatible_pools_are_rejected(self):
        original = self.rpc
        def incompatible(target, data, block):
            if target == "v2pool" and data == TOKEN1:
                return "0x" + "3".rjust(64, "0")
            return original(target, data, block)
        with self.assertRaises(Exception):
            quote_cross_venue_roundtrip(
                snapshot=self.snapshot,
                v3_pool="v3pool",
                v2_pool="v2pool",
                loan_usd=D("1"),
                rpc_call_at_block=incompatible,
                v2_gas_units=90_000,
            )


if __name__ == "__main__":
    unittest.main()
