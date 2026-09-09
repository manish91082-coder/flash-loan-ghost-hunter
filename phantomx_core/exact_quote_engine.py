"""PHANTOMX exact executable quote engine for Polygon P0-A.

Quotes are produced from protocol contracts at an explicit block. No spot-price
spread is used to infer output. For direct spatial arbitrage, each leg is quoted
against its real venue and the second leg consumes the first leg's raw output.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Callable

from .block_snapshot import BlockSnapshot
from .economic_truth import EconomicTruthError, QuoteLeg

getcontext().prec = 60
D = Decimal
ZERO = D("0")

# Polygon PoS protocol deployment addresses.
QUICKSWAP_V2_ROUTER = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
UNISWAP_V3_QUOTER_V2 = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"

TOKEN0 = "0x0dfe1681"
TOKEN1 = "0xd21220a7"
DECIMALS = "0x313ce567"
SYMBOL = "0x95d89b41"
FEE = "0xddca3f43"
GET_AMOUNTS_OUT = "0xd06ca61f"
QUOTE_EXACT_INPUT_SINGLE = "0xc6a5026a"


@dataclass(frozen=True)
class TokenMeta:
    address: str
    symbol: str
    decimals: int


@dataclass(frozen=True)
class ExactQuote:
    venue: str
    token_in: TokenMeta
    token_out: TokenMeta
    amount_in_raw: int
    amount_out_raw: int
    amount_in_usd: Decimal
    amount_out_usd: Decimal
    swap_fee_usd: Decimal
    gas_units: int
    quoted_block: int
    quote_id: str
    price_impact_pct: Decimal | None = None
    pool: str | None = None
    fee_bps: Decimal | None = None

    def to_quote_leg(self) -> QuoteLeg:
        return QuoteLeg(
            venue=self.venue,
            token_in=self.token_in.address,
            token_out=self.token_out.address,
            amount_in_usd=self.amount_in_usd,
            amount_out_usd=self.amount_out_usd,
            swap_fee_usd=self.swap_fee_usd,
            gas_units=self.gas_units,
            quoted_block=self.quoted_block,
            quote_id=self.quote_id,
            price_impact_pct=self.price_impact_pct or ZERO,
        )


def _decode_word(result: str, index: int = 0) -> int:
    raw = result[2:] if result.startswith("0x") else result
    start = index * 64
    if len(raw) < start + 64:
        raise EconomicTruthError("ABI response shorter than requested word")
    return int(raw[start:start + 64], 16)


def _decode_address(result: str) -> str:
    raw = result[2:] if result.startswith("0x") else result
    if len(raw) < 64:
        raise EconomicTruthError("ABI address response too short")
    return "0x" + raw[24:64]


def _decode_symbol(result: str) -> str:
    raw = bytes.fromhex(result[2:] if result.startswith("0x") else result)
    if len(raw) >= 64:
        length = int.from_bytes(raw[:32], "big")
        if 32 + length <= len(raw):
            return raw[32:32 + length].decode("utf-8", errors="strict")
    return raw.rstrip(b"\x00").decode("utf-8", errors="strict")


def _encode_u256(value: int) -> str:
    if value < 0:
        raise EconomicTruthError("uint256 cannot be negative")
    return f"{value:064x}"


def _encode_address(address: str) -> str:
    if not isinstance(address, str) or not address.startswith("0x") or len(address) != 42:
        raise EconomicTruthError(f"Invalid address: {address}")
    return address[2:].lower().rjust(64, "0")


def discover_token_meta(*, snapshot: BlockSnapshot, token_address: str,
                        rpc_call_at_block: Callable[[str, str, int], str]) -> TokenMeta:
    decimals = _decode_word(rpc_call_at_block(token_address, DECIMALS, snapshot.block_number))
    symbol = _decode_symbol(rpc_call_at_block(token_address, SYMBOL, snapshot.block_number))
    if decimals > 36:
        raise EconomicTruthError(f"Invalid token decimals: {decimals}")
    return TokenMeta(address=token_address, symbol=symbol, decimals=decimals)


def discover_v2_pair_tokens(*, snapshot: BlockSnapshot, pool: str,
                            rpc_call_at_block: Callable[[str, str, int], str]) -> tuple[TokenMeta, TokenMeta]:
    token0 = _decode_address(rpc_call_at_block(pool, TOKEN0, snapshot.block_number))
    token1 = _decode_address(rpc_call_at_block(pool, TOKEN1, snapshot.block_number))
    return (
        discover_token_meta(snapshot=snapshot, token_address=token0, rpc_call_at_block=rpc_call_at_block),
        discover_token_meta(snapshot=snapshot, token_address=token1, rpc_call_at_block=rpc_call_at_block),
    )


def discover_v3_pool_meta(*, snapshot: BlockSnapshot, pool: str,
                          rpc_call_at_block: Callable[[str, str, int], str]) -> tuple[TokenMeta, TokenMeta, int]:
    token0 = _decode_address(rpc_call_at_block(pool, TOKEN0, snapshot.block_number))
    token1 = _decode_address(rpc_call_at_block(pool, TOKEN1, snapshot.block_number))
    fee = _decode_word(rpc_call_at_block(pool, FEE, snapshot.block_number))
    if fee <= 0 or fee >= 1_000_000:
        raise EconomicTruthError(f"Invalid V3 fee tier: {fee}")
    return (
        discover_token_meta(snapshot=snapshot, token_address=token0, rpc_call_at_block=rpc_call_at_block),
        discover_token_meta(snapshot=snapshot, token_address=token1, rpc_call_at_block=rpc_call_at_block),
        fee,
    )


def _find_stable_and_asset(tokens: tuple[TokenMeta, TokenMeta], stable_symbols: set[str]) -> tuple[TokenMeta, TokenMeta]:
    for token in tokens:
        if token.symbol.upper() in stable_symbols:
            other = tokens[1] if token.address.lower() == tokens[0].address.lower() else tokens[0]
            return token, other
    raise EconomicTruthError(f"No configured stablecoin token in pool; symbols={[t.symbol for t in tokens]}")


def _assert_pair_compatibility(a: tuple[TokenMeta, TokenMeta], b: tuple[TokenMeta, TokenMeta]) -> None:
    aset = {x.address.lower() for x in a}
    bset = {x.address.lower() for x in b}
    if aset != bset:
        raise EconomicTruthError(f"Cross-venue pools expose different token pairs: {aset} != {bset}")


def quote_v2_single(*, snapshot: BlockSnapshot, router: str, token_in: TokenMeta, token_out: TokenMeta,
                    amount_in_raw: int, rpc_call_at_block: Callable[[str, str, int], str],
                    gas_units: int, fee_rate: Decimal = D("0.003")) -> ExactQuote:
    if amount_in_raw <= 0 or gas_units <= 0:
        raise EconomicTruthError("V2 quote amount/gas must be positive")
    path = _encode_address(token_in.address) + _encode_address(token_out.address)
    calldata = GET_AMOUNTS_OUT + _encode_u256(amount_in_raw) + _encode_u256(64) + _encode_u256(2) + path
    raw = rpc_call_at_block(router, calldata, snapshot.block_number)
    amount_out = _decode_word(raw, 2)
    if amount_out <= 0:
        raise EconomicTruthError("V2 quote returned zero output")
    amount_in_usd = D(amount_in_raw) / (D(10) ** token_in.decimals)
    amount_out_usd = D(amount_out) / (D(10) ** token_out.decimals)
    return ExactQuote(
        venue="QuickSwapV2",
        token_in=token_in,
        token_out=token_out,
        amount_in_raw=amount_in_raw,
        amount_out_raw=amount_out,
        amount_in_usd=amount_in_usd,
        amount_out_usd=amount_out_usd,
        swap_fee_usd=amount_in_usd * fee_rate,
        gas_units=gas_units,
        quoted_block=snapshot.block_number,
        quote_id=f"qs-v2-{snapshot.block_number}-{token_in.address}-{token_out.address}-{amount_in_raw}",
        pool=None,
        fee_bps=fee_rate * D(10_000),
    )


def quote_v3_single(*, snapshot: BlockSnapshot, quoter: str, token_in: TokenMeta, token_out: TokenMeta,
                    amount_in_raw: int, fee: int, rpc_call_at_block: Callable[[str, str, int], str]) -> ExactQuote:
    if amount_in_raw <= 0:
        raise EconomicTruthError("V3 quote amount must be positive")
    encoded_tuple = (
        _encode_address(token_in.address)
        + _encode_address(token_out.address)
        + _encode_u256(amount_in_raw)
        + _encode_u256(fee)
        + _encode_u256(0)
    )
    raw = rpc_call_at_block(quoter, QUOTE_EXACT_INPUT_SINGLE + encoded_tuple, snapshot.block_number)
    amount_out = _decode_word(raw, 0)
    gas_estimate = _decode_word(raw, 3)
    if amount_out <= 0 or gas_estimate <= 0:
        raise EconomicTruthError("V3 quote returned invalid output/gas")
    amount_in_usd = D(amount_in_raw) / (D(10) ** token_in.decimals)
    amount_out_usd = D(amount_out) / (D(10) ** token_out.decimals)
    fee_usd = amount_in_usd * D(fee) / D(1_000_000)
    return ExactQuote(
        venue="UniswapV3",
        token_in=token_in,
        token_out=token_out,
        amount_in_raw=amount_in_raw,
        amount_out_raw=amount_out,
        amount_in_usd=amount_in_usd,
        amount_out_usd=amount_out_usd,
        swap_fee_usd=fee_usd,
        gas_units=gas_estimate,
        quoted_block=snapshot.block_number,
        quote_id=f"uni-v3-{snapshot.block_number}-{token_in.address}-{token_out.address}-{fee}-{amount_in_raw}",
        pool=None,
        fee_bps=D(fee) / D(100),
    )


def quote_cross_venue_roundtrip(
    *, snapshot: BlockSnapshot, v3_pool: str, v2_pool: str, loan_usd: Decimal,
    rpc_call_at_block: Callable[[str, str, int], str], v2_gas_units: int,
    stable_symbols: set[str] | None = None, direction: str = "V3_TO_V2",
) -> tuple[ExactQuote, ExactQuote]:
    """Quote a true two-venue roundtrip: V3→V2 or V2→V3, using exact raw outputs."""
    stable_symbols = stable_symbols or {"USDC", "USDC.E", "USDC.EC"}
    v3_pair = discover_v3_pool_meta(snapshot=snapshot, pool=v3_pool, rpc_call_at_block=rpc_call_at_block)
    v2_pair = discover_v2_pair_tokens(snapshot=snapshot, pool=v2_pool, rpc_call_at_block=rpc_call_at_block)
    _assert_pair_compatibility(v3_pair[:2], v2_pair)
    stable, asset = _find_stable_and_asset(v3_pair[:2], stable_symbols)
    amount_in_raw = int((loan_usd * (D(10) ** stable.decimals)).to_integral_exact())
    if amount_in_raw <= 0:
        raise EconomicTruthError("Loan is below token raw precision")

    if direction == "V2_TO_V3":
        first = quote_v2_single(snapshot=snapshot, router=QUICKSWAP_V2_ROUTER,
                                token_in=stable, token_out=asset, amount_in_raw=amount_in_raw,
                                rpc_call_at_block=rpc_call_at_block, gas_units=v2_gas_units)
        second = quote_v3_single(snapshot=snapshot, quoter=UNISWAP_V3_QUOTER_V2,
                                 token_in=asset, token_out=stable, amount_in_raw=first.amount_out_raw,
                                 fee=v3_pair[2], rpc_call_at_block=rpc_call_at_block)
    elif direction == "V3_TO_V2":
        first = quote_v3_single(snapshot=snapshot, quoter=UNISWAP_V3_QUOTER_V2,
                                token_in=stable, token_out=asset, amount_in_raw=amount_in_raw,
                                fee=v3_pair[2], rpc_call_at_block=rpc_call_at_block)
        second = quote_v2_single(snapshot=snapshot, router=QUICKSWAP_V2_ROUTER,
                                 token_in=asset, token_out=stable, amount_in_raw=first.amount_out_raw,
                                 rpc_call_at_block=rpc_call_at_block, gas_units=v2_gas_units)
    else:
        raise EconomicTruthError(f"Unknown cross-venue direction: {direction}")
    return first, second


def quote_v2_roundtrip(*, snapshot: BlockSnapshot, pool: str, loan_usd: Decimal,
                       rpc_call_at_block: Callable[[str, str, int], str], gas_units_leg1: int,
                       gas_units_leg2: int, stable_symbols: set[str] | None = None) -> tuple[ExactQuote, ExactQuote]:
    stable_symbols = stable_symbols or {"USDC", "USDC.E", "USDC.EC"}
    tokens = discover_v2_pair_tokens(snapshot=snapshot, pool=pool, rpc_call_at_block=rpc_call_at_block)
    stable, asset = _find_stable_and_asset(tokens, stable_symbols)
    amount_in_raw = int((loan_usd * (D(10) ** stable.decimals)).to_integral_exact())
    leg1 = quote_v2_single(snapshot=snapshot, router=QUICKSWAP_V2_ROUTER, token_in=stable,
                           token_out=asset, amount_in_raw=amount_in_raw,
                           rpc_call_at_block=rpc_call_at_block, gas_units=gas_units_leg1)
    leg2 = quote_v2_single(snapshot=snapshot, router=QUICKSWAP_V2_ROUTER, token_in=asset,
                           token_out=stable, amount_in_raw=leg1.amount_out_raw,
                           rpc_call_at_block=rpc_call_at_block, gas_units=gas_units_leg2)
    return leg1, leg2


def quote_v3_roundtrip(*, snapshot: BlockSnapshot, pool: str, loan_usd: Decimal,
                       rpc_call_at_block: Callable[[str, str, int], str],
                       stable_symbols: set[str] | None = None) -> tuple[ExactQuote, ExactQuote]:
    stable_symbols = stable_symbols or {"USDC", "USDC.E", "USDC.EC"}
    token0, token1, fee = discover_v3_pool_meta(snapshot=snapshot, pool=pool, rpc_call_at_block=rpc_call_at_block)
    stable, asset = _find_stable_and_asset((token0, token1), stable_symbols)
    amount_in_raw = int((loan_usd * (D(10) ** stable.decimals)).to_integral_exact())
    leg1 = quote_v3_single(snapshot=snapshot, quoter=UNISWAP_V3_QUOTER_V2, token_in=stable,
                           token_out=asset, amount_in_raw=amount_in_raw, fee=fee,
                           rpc_call_at_block=rpc_call_at_block)
    leg2 = quote_v3_single(snapshot=snapshot, quoter=UNISWAP_V3_QUOTER_V2, token_in=asset,
                           token_out=stable, amount_in_raw=leg1.amount_out_raw, fee=fee,
                           rpc_call_at_block=rpc_call_at_block)
    return leg1, leg2
