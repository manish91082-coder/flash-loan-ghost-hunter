"""Block-pinned adapters for the existing Polygon pool configuration.

This layer reads Uniswap V3 slot0() and Uniswap V2-style getReserves() against
one explicit block. It does not use the legacy `latest` default and it never
substitutes a synthetic price when a read fails.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Callable, Mapping, Any

from .block_snapshot import BlockSnapshot
from .economic_truth import EconomicTruthError

getcontext().prec = 60
D = Decimal
SLOT0_SELECTOR = "0x3850c7bd"
GET_RESERVES_SELECTOR = "0x0902f1ac"


@dataclass(frozen=True)
class PoolRead:
    pool: str
    venue: str
    token0: str
    token1: str
    block_number: int
    price_usd: Decimal | None
    raw_result: str | None
    error: str | None


def _word(data: str, index: int) -> int:
    raw = data[2:] if data.startswith("0x") else data
    start = index * 64
    end = start + 64
    if len(raw) < end:
        raise EconomicTruthError("ABI response is shorter than required")
    return int(raw[start:end], 16)


def parse_slot0_price_usd(result: str, token0_decimals: int, token1_decimals: int,
                          token0_is_base: bool) -> Decimal:
    sqrt_x96 = _word(result, 0)
    if sqrt_x96 <= 0:
        raise EconomicTruthError("slot0 sqrtPriceX96 is zero")
    raw_price = (D(sqrt_x96) / D(2**96)) ** 2
    human_price = raw_price * (D(10) ** token0_decimals) / (D(10) ** token1_decimals)
    return human_price if token0_is_base else (D(1) / human_price)


def parse_v2_price_usd(result: str, token0_decimals: int, token1_decimals: int,
                       token0_is_base: bool) -> Decimal:
    r0 = _word(result, 0)
    r1 = _word(result, 1)
    if r0 <= 0 or r1 <= 0:
        raise EconomicTruthError("V2 pool has zero liquidity reserve")
    h0 = D(r0) / (D(10) ** token0_decimals)
    h1 = D(r1) / (D(10) ** token1_decimals)
    return h1 / h0 if token0_is_base else h0 / h1


def read_configured_pool(
    *,
    snapshot: BlockSnapshot,
    config: Mapping[str, Any],
    venue: str,
    rpc_call_at_block: Callable[[str, str, int], str],
    kind: str,
) -> PoolRead:
    """Read one configured pool at the exact snapshot block."""
    pool = str(config["address"])
    token0 = str(config["token0"])
    token1 = str(config["token1"])
    t0d = int(config["token0_decimals"])
    t1d = int(config["token1_decimals"])
    token0_is_base = config.get("price_formula") in {
        "token0_per_token1_inverted", "direct", "reserve1_per_reserve0"
    }
    try:
        selector = SLOT0_SELECTOR if kind == "v3" else GET_RESERVES_SELECTOR
        raw = rpc_call_at_block(pool, selector, snapshot.block_number)
        if kind == "v3":
            price = parse_slot0_price_usd(raw, t0d, t1d, token0_is_base)
        else:
            price = parse_v2_price_usd(raw, t0d, t1d, token0_is_base)
        return PoolRead(pool, venue, token0, token1, snapshot.block_number, price, raw, None)
    except Exception as exc:
        return PoolRead(pool, venue, token0, token1, snapshot.block_number, None, None, str(exc))
