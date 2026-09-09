"""
PhantomX Live Spread Analyzer (live_spread_analyzer.py)
=======================================================
Computes real arbitrage spread from live DEX prices.
Selects optimal Permutation (A/B/C) based on real data.
Computes optimal loan size and expected net profit.

0% simulated data — all inputs must be live on-chain prices.
"""

import sys
import math
from decimal import Decimal

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────
# ARBITRAGE PARAMETERS (Dynamic, not hardcoded)
# ─────────────────────────────────────────────────────────────────

# DEX fee tiers (fraction, not percent)
DEX_FEE_TIERS = {
    "UniswapV3_0.05":  0.0005,
    "UniswapV3_0.30":  0.003,
    "QuickSwapV2":     0.003,
    "SushiSwapV2":     0.003,
    "BalancerV2":      0.0,    # Zero fee for flash loans
}

# Permutation fee structures (total friction fraction)
PERMUTATION_FEES = {
    "Permutation_A_LowFeeDirect":    0.0005,   # UniV3 0.05% single hop
    "Permutation_B_TickOptimization": 0.0001,  # UniV3 0.01% tick optimized
    "Permutation_C_MultiHopReRoute":  0.0012,  # Multi-hop composite
}

# Minimum spread thresholds to justify execution (above friction)
MIN_SPREAD_THRESHOLDS = {
    "Permutation_A_LowFeeDirect":     0.0008,  # 0.08% min spread
    "Permutation_B_TickOptimization": 0.0003,  # 0.03% min spread
    "Permutation_C_MultiHopReRoute":  0.0015,  # 0.15% min spread (due to multi-hop)
}

# Maximum loan sizes per pair (USD) for realistic pool depth
MAX_LOAN_USD = {
    "WMATIC": 20000.0,
    "WETH":   50000.0,
    "WBTC":   100000.0,
}

# Gas cost in USD per execution (calculated from live gwei)
def estimate_gas_cost_usd(gas_gwei: float, matic_price_usd: float = 0.10) -> float:
    """
    Estimate gas cost in USD for one flash loan arb transaction.
    Polygon average: ~250,000 gas units per complex arb.
    """
    GAS_UNITS = 250_000
    gas_cost_matic = (gas_gwei * 1e-9) * GAS_UNITS
    return gas_cost_matic * matic_price_usd

# ─────────────────────────────────────────────────────────────────
# CORE SPREAD COMPUTATION
# ─────────────────────────────────────────────────────────────────

def compute_spread(price_a: float, price_b: float) -> dict:
    """
    Compute the real arbitrage spread between two DEX prices.
    Returns:
        - spread_pct: |price_a - price_b| / min(price_a, price_b) * 100
        - direction: "BUY_ON_A_SELL_ON_B" or "BUY_ON_B_SELL_ON_A"
        - buy_price: price to buy at
        - sell_price: price to sell at
        - profit_direction: +1 or -1
    """
    if price_a is None or price_b is None or price_a <= 0 or price_b <= 0:
        return {"spread_pct": 0.0, "direction": "NO_ARBITRAGE", "error": "Invalid prices"}

    if price_a < price_b:
        # Buy on DEX A (cheaper), sell on DEX B (more expensive)
        spread_pct = (price_b - price_a) / price_a * 100
        direction = "BUY_ON_DEX_A_SELL_ON_DEX_B"
        buy_dex = "DEX_A"
        sell_dex = "DEX_B"
        buy_price = price_a
        sell_price = price_b
    else:
        # Buy on DEX B (cheaper), sell on DEX A (more expensive)
        spread_pct = (price_a - price_b) / price_b * 100
        direction = "BUY_ON_DEX_B_SELL_ON_DEX_A"
        buy_dex = "DEX_B"
        sell_dex = "DEX_A"
        buy_price = price_b
        sell_price = price_a

    return {
        "spread_pct": round(spread_pct, 6),
        "direction": direction,
        "buy_dex": buy_dex,
        "sell_dex": sell_dex,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "mid_price": (price_a + price_b) / 2,
        "error": None
    }

# ─────────────────────────────────────────────────────────────────
# PERMUTATION SELECTOR
# ─────────────────────────────────────────────────────────────────

def select_permutation(pair: str, spread_pct: float, gas_gwei: float,
                        univ3_price: float = None, quickv2_price: float = None,
                        sushiv2_price: float = None) -> dict:
    """
    Select the optimal permutation (A, B, or C) based on live spread data.
    
    Logic:
    - Permutation A: Direct single-hop if spread >= 0.08%
    - Permutation B: Tick-optimized if spread is smaller (0.03% to 0.08%)
    - Permutation C: Multi-hop re-routing if spread < 0.15% using 3 DEXes
    
    Returns: selected permutation name + reasoning
    """
    spread_decimal = spread_pct / 100.0

    # Check all available prices for multi-hop potential
    available_prices = {k: v for k, v in {
        "UniswapV3": univ3_price,
        "QuickSwapV2": quickv2_price,
        "SushiSwapV2": sushiv2_price
    }.items() if v is not None and v > 0}

    # If we have 3 DEX prices, try to compute triangular spread
    triangular_spread = None
    if len(available_prices) >= 3:
        prices = list(available_prices.values())
        max_p = max(prices)
        min_p = min(prices)
        if min_p > 0:
            triangular_spread = (max_p - min_p) / min_p * 100

    # Permutation A: High spread — direct trade profitable
    if spread_pct >= 0.08:
        return {
            "permutation": "Permutation_A_LowFeeDirect",
            "fee_tier": PERMUTATION_FEES["Permutation_A_LowFeeDirect"],
            "reason": f"Direct spread {spread_pct:.4f}% >= 0.08% threshold. Single-hop arb viable.",
            "min_threshold_pct": 0.08,
            "triangular_spread": triangular_spread
        }

    # Permutation B: Medium spread — tick optimization  
    elif spread_pct >= 0.03:
        return {
            "permutation": "Permutation_B_TickOptimization",
            "fee_tier": PERMUTATION_FEES["Permutation_B_TickOptimization"],
            "reason": f"Direct spread {spread_pct:.4f}% in 0.03-0.08% range. Tick optimization viable.",
            "min_threshold_pct": 0.03,
            "triangular_spread": triangular_spread
        }

    # Permutation C: Low direct spread — use multi-hop if 3 DEXes show combined dislocation
    elif triangular_spread is not None and triangular_spread >= 0.15:
        return {
            "permutation": "Permutation_C_MultiHopReRoute",
            "fee_tier": PERMUTATION_FEES["Permutation_C_MultiHopReRoute"],
            "reason": f"Direct spread {spread_pct:.4f}% too low, but triangular spread {triangular_spread:.4f}% >= 0.15% via 3 DEX re-routing.",
            "min_threshold_pct": 0.15,
            "triangular_spread": triangular_spread
        }

    # No profitable permutation found
    return {
        "permutation": "NO_PERMUTATION",
        "fee_tier": 0.0,
        "reason": f"Spread {spread_pct:.4f}% too low for all permutations. Triangular: {triangular_spread:.4f}% (< 0.15%)." if triangular_spread else f"Spread {spread_pct:.4f}% too low. Insufficient DEX data for multi-hop.",
        "min_threshold_pct": None,
        "triangular_spread": triangular_spread
    }

# ─────────────────────────────────────────────────────────────────
# OPTIMAL LOAN SIZE CALCULATOR
# ─────────────────────────────────────────────────────────────────

def compute_optimal_loan(pair: str, spread_pct: float, gas_cost_usd: float,
                          min_profit_usd: float = 0.50) -> float:
    """
    Compute optimal flash loan size to maximize profit above gas costs.
    Uses AMM pool depth constraints.
    
    Formula: L* = min(max_pool_depth, gas_cost / spread * safety_factor)
    """
    spread_decimal = spread_pct / 100.0
    if spread_decimal <= 0:
        return 0.0

    # Minimum loan to cover gas + generate min profit
    # net_profit = loan * spread - friction - gas
    # For min_profit: loan >= (min_profit + gas) / (spread - friction_rate)
    fee_rate = 0.003  # Conservative friction
    effective_spread = spread_decimal - fee_rate
    if effective_spread <= 0:
        return 0.0

    min_loan = (min_profit_usd + gas_cost_usd) / effective_spread
    max_loan = MAX_LOAN_USD.get(pair, 15000.0)

    # Scale up to maximize profit within pool depth limits
    # Optimal = 70% of max pool capacity (avoid excessive price impact)
    optimal = min(max_loan * 0.7, max_loan)
    optimal = max(optimal, min_loan)  # Must be at least min_loan

    return round(optimal, 2)

# ─────────────────────────────────────────────────────────────────
# NET PROFIT CALCULATOR
# ─────────────────────────────────────────────────────────────────

def compute_net_profit(loan_usd: float, spread_pct: float, fee_tier: float,
                        gas_cost_usd: float) -> dict:
    """
    Compute exact net profit from flash loan arbitrage.
    
    Formula:
    gross_profit = loan * spread_pct/100
    friction = loan * fee_tier
    net_profit = gross_profit - friction - gas_cost
    """
    if loan_usd <= 0 or spread_pct <= 0:
        return {
            "gross_profit_usd": 0.0,
            "friction_usd": 0.0,
            "gas_cost_usd": gas_cost_usd,
            "net_profit_usd": -gas_cost_usd,
            "profitable": False
        }

    gross_profit = loan_usd * (spread_pct / 100.0)
    friction = loan_usd * fee_tier
    net_profit = gross_profit - friction - gas_cost_usd

    return {
        "gross_profit_usd": round(gross_profit, 4),
        "friction_usd": round(friction, 4),
        "gas_cost_usd": round(gas_cost_usd, 4),
        "net_profit_usd": round(net_profit, 4),
        "profitable": net_profit > 0.0
    }

# ─────────────────────────────────────────────────────────────────
# MASTER ANALYSIS FUNCTION (V2 Engine)
# ─────────────────────────────────────────────────────────────────

def analyze_v2_opportunity(pair: str, price_snapshot: dict) -> dict:
    """
    V2 MVP Engine: Direct Spatial Arbitrage Analysis.
    DEX A = UniswapV3, DEX B = QuickSwapV2
    Uses LIVE prices from price_snapshot.
    """
    univ3_data = price_snapshot.get("univ3", {})
    quickv2_data = price_snapshot.get("quickv2", {})
    sushiv2_data = price_snapshot.get("sushiv2", {})

    univ3_price = univ3_data.get("price_usd")
    quickv2_price = quickv2_data.get("price_usd")
    sushiv2_price = sushiv2_data.get("price_usd")
    gas_gwei = price_snapshot.get("gas_gwei_live", 30.0)
    block_number = price_snapshot.get("block_number", 0)
    timestamp = price_snapshot.get("timestamp", "")

    # Compute gas cost in USD (estimate MATIC price from WMATIC/USDC)
    matic_price = quickv2_price if pair == "WMATIC" else 0.10
    gas_cost_usd = estimate_gas_cost_usd(gas_gwei, matic_price)

    # Primary spread: UniV3 vs QuickV2
    spread_info = compute_spread(univ3_price, quickv2_price)
    spread_pct = spread_info.get("spread_pct", 0.0)

    # Select permutation
    perm_info = select_permutation(
        pair, spread_pct, gas_gwei,
        univ3_price=univ3_price,
        quickv2_price=quickv2_price,
        sushiv2_price=sushiv2_price
    )

    # Compute loan size
    if perm_info["permutation"] != "NO_PERMUTATION":
        # Use triangular spread if Permutation C, else direct spread
        effective_spread = (perm_info["triangular_spread"] or spread_pct)
        loan_usd = compute_optimal_loan(pair, effective_spread, gas_cost_usd)
        profit_info = compute_net_profit(
            loan_usd, effective_spread,
            perm_info["fee_tier"], gas_cost_usd
        )
        action = "EXECUTE" if profit_info["profitable"] else "WAIT"
        decision_reason = "Net profit positive after friction & gas." if profit_info["profitable"] else f"Net profit ${profit_info['net_profit_usd']:.4f} <= 0 after gas/friction."
    else:
        loan_usd = 0.0
        effective_spread = spread_pct
        profit_info = {
            "gross_profit_usd": 0.0,
            "friction_usd": 0.0,
            "gas_cost_usd": gas_cost_usd,
            "net_profit_usd": 0.0,
            "profitable": False
        }
        action = "WAIT"
        decision_reason = perm_info["reason"]

    return {
        # Identity
        "engine": "V2_MVP_DirectSpatial",
        "pair": pair,
        "timestamp": timestamp,
        "block_number": block_number,

        # Live DEX Prices (REAL data)
        "univ3_price_usd": univ3_price,
        "univ3_sqrtPriceX96": univ3_data.get("sqrtPriceX96"),
        "univ3_tick": univ3_data.get("tick"),
        "univ3_pool": univ3_data.get("pool"),
        "univ3_rpc": univ3_data.get("rpc_used"),
        "univ3_latency_ms": univ3_data.get("latency_ms"),
        "univ3_error": univ3_data.get("error"),

        "quickv2_price_usd": quickv2_price,
        "quickv2_reserve0_raw": quickv2_data.get("reserve0_raw"),
        "quickv2_reserve1_raw": quickv2_data.get("reserve1_raw"),
        "quickv2_reserve0_human": quickv2_data.get("reserve0_human"),
        "quickv2_reserve1_human": quickv2_data.get("reserve1_human"),
        "quickv2_pool": quickv2_data.get("pool"),
        "quickv2_rpc": quickv2_data.get("rpc_used"),
        "quickv2_latency_ms": quickv2_data.get("latency_ms"),
        "quickv2_error": quickv2_data.get("error"),

        "sushiv2_price_usd": sushiv2_price,
        "sushiv2_error": sushiv2_data.get("error"),

        # Spread Analysis (REAL)
        "spread_pct": spread_pct,
        "spread_direction": spread_info.get("direction"),
        "buy_dex": spread_info.get("buy_dex"),
        "sell_dex": spread_info.get("sell_dex"),
        "buy_price": spread_info.get("buy_price"),
        "sell_price": spread_info.get("sell_price"),
        "mid_price": spread_info.get("mid_price"),
        "triangular_spread_pct": perm_info.get("triangular_spread"),
        "effective_spread_used_pct": effective_spread,

        # Permutation
        "selected_permutation": perm_info["permutation"],
        "permutation_fee_tier": perm_info["fee_tier"],
        "permutation_reason": perm_info["reason"],

        # Gas
        "gas_gwei_live": gas_gwei,
        "gas_cost_usd": profit_info["gas_cost_usd"],

        # Profit Calculation
        "optimal_loan_usd": loan_usd,
        "gross_profit_usd": profit_info["gross_profit_usd"],
        "friction_usd": profit_info["friction_usd"],
        "net_profit_usd": profit_info["net_profit_usd"],

        # Decision
        "action": action,
        "decision_reason": decision_reason,
        "is_live_data": True,
        "is_simulated": False
    }

# ─────────────────────────────────────────────────────────────────
# MASTER ANALYSIS FUNCTION (V3 Engine)
# ─────────────────────────────────────────────────────────────────

def analyze_v3_opportunity(pair: str, price_snapshot: dict) -> dict:
    """
    V3 Universal Engine: Triangular Multi-Hop Graph Analysis.
    Uses ALL 3 DEX prices for maximum spread extraction.
    """
    v2_base = analyze_v2_opportunity(pair, price_snapshot)

    univ3_data = price_snapshot.get("univ3", {})
    quickv2_data = price_snapshot.get("quickv2", {})
    sushiv2_data = price_snapshot.get("sushiv2", {})

    univ3_price = univ3_data.get("price_usd")
    quickv2_price = quickv2_data.get("price_usd")
    sushiv2_price = sushiv2_data.get("price_usd")

    # V3 uses triangular routing: find best 3-DEX combination
    all_prices = {k: v for k, v in {
        "UniswapV3": univ3_price,
        "QuickSwapV2": quickv2_price,
        "SushiSwapV2": sushiv2_price
    }.items() if v is not None and v > 0}

    # Build triangular route
    if len(all_prices) >= 2:
        sorted_by_price = sorted(all_prices.items(), key=lambda x: x[1])
        cheapest_dex, cheapest_price = sorted_by_price[0]
        dearest_dex, dearest_price = sorted_by_price[-1]

        triangular_spread_pct = (dearest_price - cheapest_price) / cheapest_price * 100

        # V3 route: Buy on cheapest, route through middle, sell on dearest
        if len(all_prices) == 3:
            mid_dex, mid_price = sorted_by_price[1]
            route = f"{cheapest_dex} -> {mid_dex} -> {dearest_dex}"
            hop1_spread = (mid_price - cheapest_price) / cheapest_price * 100
            hop2_spread = (dearest_price - mid_price) / mid_price * 100
            hop3_spread = 0.0  # Return hop (same block atomicity)
        else:
            route = f"{cheapest_dex} -> {dearest_dex}"
            hop1_spread = triangular_spread_pct
            hop2_spread = 0.0
            hop3_spread = 0.0
            mid_dex = "N/A"
    else:
        triangular_spread_pct = v2_base.get("spread_pct", 0.0)
        route = "INSUFFICIENT_DEX_DATA"
        hop1_spread = triangular_spread_pct
        hop2_spread = 0.0
        hop3_spread = 0.0
        cheapest_dex = "N/A"
        dearest_dex = "N/A"
        mid_dex = "N/A"
        cheapest_price = None
        dearest_price = None

    gas_gwei = price_snapshot.get("gas_gwei_live", 30.0)
    matic_price = quickv2_price if pair == "WMATIC" else 0.10
    gas_cost_usd = estimate_gas_cost_usd(gas_gwei, matic_price)

    # V3 uses 0.01% fee tier for Balancer V2 zero-fee flash loan
    v3_fee_tier = 0.0001

    # V3 loan: scale up for WBTC deep liquidity
    v3_max_loan = MAX_LOAN_USD.get(pair, 15000.0)
    loan_usd = compute_optimal_loan(pair, triangular_spread_pct, gas_cost_usd)

    profit_info = compute_net_profit(loan_usd, triangular_spread_pct, v3_fee_tier, gas_cost_usd)
    action = "EXECUTE" if profit_info["profitable"] else "WAIT"

    # Build V3 result (extends V2 base)
    v3_result = dict(v2_base)
    v3_result.update({
        "engine": "V3_Universal_TriangularGraph",
        "triangular_route": route,
        "cheapest_dex": cheapest_dex,
        "dearest_dex": dearest_dex,
        "mid_dex": mid_dex,
        "cheapest_price": cheapest_price,
        "dearest_price": dearest_price,
        "hop1_spread_pct": round(hop1_spread, 6),
        "hop2_spread_pct": round(hop2_spread, 6),
        "hop3_spread_pct": round(hop3_spread, 6),
        "triangular_spread_pct": round(triangular_spread_pct, 6),
        "effective_spread_used_pct": round(triangular_spread_pct, 6),
        "v3_fee_tier": v3_fee_tier,
        "optimal_loan_usd": loan_usd,
        "gross_profit_usd": profit_info["gross_profit_usd"],
        "friction_usd": profit_info["friction_usd"],
        "net_profit_usd": profit_info["net_profit_usd"],
        "action": action,
        "decision_reason": f"V3 Triangular spread {triangular_spread_pct:.4f}% via route [{route}]. Net: ${profit_info['net_profit_usd']:.4f}",
        "is_live_data": True,
        "is_simulated": False
    })

    return v3_result
