import unittest
from decimal import Decimal as D

from phantomx_core.block_snapshot import build_block_snapshot
from phantomx_core.economic_truth import EconomicTruthError
from phantomx_core.exact_quote_engine import (
    DECIMALS,
    FEE,
    GET_AMOUNTS_OUT,
    QUOTE_EXACT_INPUT_SINGLE,
    SYMBOL,
    TOKEN0,
    TOKEN1,
    TokenMeta,
    discover_token_meta,
    discover_v2_pair_tokens,
    discover_v3_pool_meta,
    quote_v2_single,
    quote_v3_single,
)


class ExactQuoteEngineTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = build_block_snapshot(
            chain_id=137,
            block={"number": "0x64", "hash": "0xabc"},
            gas_price_wei=30_000_000_000,
            gas_token_price_usd=D("0.25"),
            source_rpc="test://polygon",
        )
        self.usdc = "0x0000000000000000000000000000000000000001"
        self.wmatic = "0x0000000000000000000000000000000000000002"

    def rpc(self, target, data, block):
        self.assertEqual(block, 100)
        if target == "pool":
            if data == TOKEN0:
                return "0x" + self.usdc[2:].rjust(64, "0")
            if data == TOKEN1:
                return "0x" + self.wmatic[2:].rjust(64, "0")
            if data == FEE:
                return "0x" + f"{500:064x}"
        if target in {self.usdc, self.wmatic}:
            if data == DECIMALS:
                value = 6 if target == self.usdc else 18
                return "0x" + f"{value:064x}"
            if data == SYMBOL:
                symbol = b"USDC" if target == self.usdc else b"WMATIC"
                payload = b"".join([
                    (32).to_bytes(32, "big"),
                    len(symbol).to_bytes(32, "big"),
                    symbol.ljust(32, b"\x00"),
                ])
                return "0x" + payload.hex()
        raise AssertionError((target, data))

    def test_symbol_string_abi_decoding(self):
        meta = discover_token_meta(
            snapshot=self.snapshot,
            token_address=self.usdc,
            rpc_call_at_block=self.rpc,
        )
        self.assertEqual(meta.symbol, "USDC")
        self.assertEqual(meta.decimals, 6)

    def test_pair_metadata_and_v3_fee_are_read_at_snapshot_block(self):
        tokens = discover_v2_pair_tokens(
            snapshot=self.snapshot,
            pool="pool",
            rpc_call_at_block=self.rpc,
        )
        self.assertEqual(tokens[0].symbol, "USDC")
        self.assertEqual(tokens[1].symbol, "WMATIC")

        token0, token1, fee = discover_v3_pool_meta(
            snapshot=self.snapshot,
            pool="pool",
            rpc_call_at_block=self.rpc,
        )
        self.assertEqual(token0.address, self.usdc)
        self.assertEqual(token1.address, self.wmatic)
        self.assertEqual(fee, 500)

    def test_v2_quote_decodes_amounts_out_without_invented_gas(self):
        amount_in = 1_000_000
        expected_out = 10**18

        def rpc(target, data, block):
            if target == "router":
                self.assertEqual(block, 100)
                self.assertTrue(data.startswith(GET_AMOUNTS_OUT))
                return "0x" + (
                    f"{32:064x}" + f"{2:064x}" +
                    f"{amount_in:064x}" + f"{expected_out:064x}"
                )
            raise AssertionError(target)

        quote = quote_v2_single(
            snapshot=self.snapshot,
            router="router",
            token_in=TokenMeta(self.usdc, "USDC", 6),
            token_out=TokenMeta(self.wmatic, "WMATIC", 18),
            amount_in_raw=amount_in,
            rpc_call_at_block=rpc,
        )
        self.assertEqual(quote.amount_out_raw, expected_out)
        self.assertEqual(quote.amount_in_usd, D("1"))
        self.assertEqual(quote.amount_out_usd, D("1"))
        self.assertEqual(quote.gas_units, None)
        self.assertEqual(quote.quoted_block, 100)

    def test_v2_quote_can_carry_explicit_verified_execution_gas(self):
        def rpc(target, data, block):
            return "0x" + f"{32:064x}" + f"{2:064x}" + f"{1_000_000:064x}" + f"{10**18:064x}"

        quote = quote_v2_single(
            snapshot=self.snapshot,
            router="router",
            token_in=TokenMeta(self.usdc, "USDC", 6),
            token_out=TokenMeta(self.wmatic, "WMATIC", 18),
            amount_in_raw=1_000_000,
            rpc_call_at_block=rpc,
            gas_units=90_000,
        )
        self.assertEqual(quote.gas_units, 90_000)
        self.assertEqual(quote.to_quote_leg().gas_units, 90_000)

    def test_v3_quoter_gas_is_not_execution_gas(self):
        amount_in = 1_000_000
        amount_out = 500_000_000_000_000_000
        quoter_gas = 125_000

        def rpc(target, data, block):
            self.assertEqual(target, "quoter")
            self.assertEqual(block, 100)
            self.assertTrue(data.startswith(QUOTE_EXACT_INPUT_SINGLE))
            return "0x" + (
                f"{amount_out:064x}" +
                f"{1:064x}" +
                f"{2:064x}" +
                f"{quoter_gas:064x}"
            )

        quote = quote_v3_single(
            snapshot=self.snapshot,
            quoter="quoter",
            token_in=TokenMeta(self.usdc, "USDC", 6),
            token_out=TokenMeta(self.wmatic, "WMATIC", 18),
            amount_in_raw=amount_in,
            fee=500,
            rpc_call_at_block=rpc,
        )
        self.assertEqual(quote.amount_out_raw, amount_out)
        self.assertIsNone(quote.gas_units)
        self.assertEqual(quote.swap_fee_usd, D("0.0005"))
        with self.assertRaises(EconomicTruthError):
            quote.to_quote_leg()

    def test_malformed_rpc_result_fails_closed(self):
        with self.assertRaises(EconomicTruthError):
            quote_v3_single(
                snapshot=self.snapshot,
                quoter="quoter",
                token_in=TokenMeta(self.usdc, "USDC", 6),
                token_out=TokenMeta(self.wmatic, "WMATIC", 18),
                amount_in_raw=1_000_000,
                fee=500,
                rpc_call_at_block=lambda *_: "0x01",
            )


if __name__ == "__main__":
    unittest.main()
