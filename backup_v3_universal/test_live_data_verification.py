"""
PhantomX Live Data Verification Test Suite
==========================================
test_live_data_verification.py

Ground-level verification of all live data components.
6 Test Categories, 18 individual tests.
All tests use REAL on-chain data (no mocks/simulations).
"""

import sys
import os
import json
import time
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from live_price_fetcher import (
    get_current_block, get_current_gas_gwei,
    get_univ3_price, get_quickv2_price, get_sushiv2_price,
    get_live_price_snapshot, is_price_sane,
    FREE_RPC_ENDPOINTS, QUICKV2_POOLS, UNIV3_POOLS, SUSHIV2_POOLS
)
from live_spread_analyzer import (
    compute_spread, select_permutation, compute_optimal_loan,
    compute_net_profit, analyze_v2_opportunity, analyze_v3_opportunity,
    estimate_gas_cost_usd
)

# ─────────────────────────────────────────────────────────────────
# Test Framework
# ─────────────────────────────────────────────────────────────────
PASSED = []
FAILED = []

def test(name: str, condition: bool, detail: str = ""):
    if condition:
        PASSED.append(name)
        print(f"  [PASS] {name}" + (f" — {detail}" if detail else ""))
    else:
        FAILED.append(name)
        print(f"  [FAIL] {name}" + (f" — {detail}" if detail else ""))
    return condition

def section(title: str):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

# ─────────────────────────────────────────────────────────────────
# Test Category 1: RPC Connectivity
# ─────────────────────────────────────────────────────────────────
section("Test 1: RPC Connectivity")

block, rpc_used, latency = get_current_block()
test("T1.1 Primary RPC Returns Block Number",
     block > 90_000_000,
     f"Block #{block:,} via {rpc_used} ({latency:.0f}ms)")

test("T1.2 Block Number is Recent (> 93M)",
     block > 93_000_000,
     f"Block #{block:,}")

gas, gas_rpc, gas_lat = get_current_gas_gwei()
test("T1.3 Gas Price Retrieved",
     gas > 0,
     f"{gas:.2f} Gwei via {gas_rpc} ({gas_lat:.0f}ms)")

test("T1.4 Gas Price Sane (1-1000 Gwei Polygon range)",
     1.0 <= gas <= 1000.0,
     f"{gas:.2f} Gwei")

# ─────────────────────────────────────────────────────────────────
# Test Category 2: Uniswap V3 slot0() Live Data
# ─────────────────────────────────────────────────────────────────
section("Test 2: Uniswap V3 slot0() Live Data")

for pair in ["WMATIC", "WETH", "WBTC"]:
    d = get_univ3_price(pair)
    price = d.get("price_usd")
    sqrt = d.get("sqrtPriceX96")
    tick = d.get("tick")
    err = d.get("error")
    sane = is_price_sane(pair, price) if price else False

    test(f"T2.{['WMATIC','WETH','WBTC'].index(pair)+1} UniV3 {pair} Price Valid",
         sane,
         f"${price:.4f}" if price else f"ERROR: {err}")

    if price:
        test(f"T2.{['WMATIC','WETH','WBTC'].index(pair)+4} UniV3 {pair} sqrtPriceX96 Non-Zero",
             sqrt is not None and sqrt > 0,
             f"sqrtPriceX96={sqrt}")

# ─────────────────────────────────────────────────────────────────
# Test Category 3: QuickSwap V2 getReserves() Live Data
# ─────────────────────────────────────────────────────────────────
section("Test 3: QuickSwap V2 getReserves() Live Data")

for pair in ["WMATIC", "WETH", "WBTC"]:
    d = get_quickv2_price(pair)
    price = d.get("price_usd")
    r0 = d.get("reserve0_raw")
    r1 = d.get("reserve1_raw")
    err = d.get("error")
    sane = is_price_sane(pair, price) if price else False

    test(f"T3.{['WMATIC','WETH','WBTC'].index(pair)+1} QuickV2 {pair} Price Valid",
         sane,
         f"${price:.4f}" if price else f"ERROR: {err}")

    if r0 and r1:
        test(f"T3.{['WMATIC','WETH','WBTC'].index(pair)+4} QuickV2 {pair} Reserves Non-Zero",
             r0 > 0 and r1 > 0,
             f"r0={r0:,} r1={r1:,}")

# ─────────────────────────────────────────────────────────────────
# Test Category 4: Spread Calculation & Sanity
# ─────────────────────────────────────────────────────────────────
section("Test 4: Spread Calculation Sanity")

for pair in ["WMATIC", "WETH", "WBTC"]:
    snap = get_live_price_snapshot(pair)
    univ3_p = snap.get("univ3", {}).get("price_usd")
    quickv2_p = snap.get("quickv2", {}).get("price_usd")

    if univ3_p and quickv2_p:
        spread_info = compute_spread(univ3_p, quickv2_p)
        sp = spread_info.get("spread_pct", 0.0)

        test(f"T4.{['WMATIC','WETH','WBTC'].index(pair)+1} {pair} Spread Computed",
             sp >= 0.0,
             f"UniV3=${univ3_p:.4f} QuickV2=${quickv2_p:.4f} Spread={sp:.4f}%")

        test(f"T4.{['WMATIC','WETH','WBTC'].index(pair)+4} {pair} Spread is Real-World Realistic (0-5%)",
             0.0 <= sp <= 5.0,
             f"Spread={sp:.4f}% (acceptable range: 0-5%)")
    else:
        test(f"T4.{['WMATIC','WETH','WBTC'].index(pair)+1} {pair} Spread Computed",
             False, f"Missing prices: UniV3={univ3_p} QuickV2={quickv2_p}")

# ─────────────────────────────────────────────────────────────────
# Test Category 5: V2 and V3 Analysis Outputs
# ─────────────────────────────────────────────────────────────────
section("Test 5: V2 and V3 Analysis Output Correctness")

snap_wmatic = get_live_price_snapshot("WMATIC")
snap_weth   = get_live_price_snapshot("WETH")

v2_result = analyze_v2_opportunity("WMATIC", snap_wmatic)
test("T5.1 V2 Analysis Returns Dict",
     isinstance(v2_result, dict), str(type(v2_result)))

test("T5.2 V2 Result Has Required Fields",
     all(f in v2_result for f in ["action", "spread_pct", "net_profit_usd", "is_simulated"]),
     str(list(v2_result.keys())[:8]))

test("T5.3 V2 Result is NOT Simulated",
     v2_result.get("is_simulated") == False,
     f"is_simulated={v2_result.get('is_simulated')}")

test("T5.4 V2 Result is Live Data",
     v2_result.get("is_live_data") == True,
     f"is_live_data={v2_result.get('is_live_data')}")

v3_result = analyze_v3_opportunity("WETH", snap_weth)
test("T5.5 V3 Analysis Returns Dict",
     isinstance(v3_result, dict), str(type(v3_result)))

test("T5.6 V3 Result Has Triangular Fields",
     all(f in v3_result for f in ["triangular_route", "hop1_spread_pct", "triangular_spread_pct"]),
     str({k: v3_result.get(k) for k in ["triangular_route", "hop1_spread_pct"]}))

test("T5.7 V3 Profit Calculation is Mathematically Valid",
     (v3_result.get("net_profit_usd", 0) <=
      v3_result.get("gross_profit_usd", 0)),
     f"Gross=${v3_result.get('gross_profit_usd',0):.4f} Net=${v3_result.get('net_profit_usd',0):.4f}")

# ─────────────────────────────────────────────────────────────────
# Test Category 6: JSONL Log File Write + Read-Back
# ─────────────────────────────────────────────────────────────────
section("Test 6: JSONL Log File Write and Read-Back")

test_log = os.path.join(os.path.dirname(__file__), "_test_jsonl_log.jsonl")

# Write test record
test_record = {
    "test_id": "T6_verification",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "pair": "WMATIC",
    "is_simulated": False,
    "is_live_data": True,
    "price": snap_wmatic.get("univ3", {}).get("price_usd"),
    "block_number": snap_wmatic.get("block_number"),
}

try:
    with open(test_log, 'w', encoding='utf-8') as f:
        f.write(json.dumps(test_record) + "\n")
    test("T6.1 JSONL Write Successful", os.path.exists(test_log), test_log)
except Exception as e:
    test("T6.1 JSONL Write Successful", False, str(e))

# Read back
try:
    with open(test_log, 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        loaded = json.loads(line)
    test("T6.2 JSONL Read-Back Successful", True, f"Record ID: {loaded.get('test_id')}")
    test("T6.3 JSONL Record Integrity (is_simulated=False)",
         loaded.get("is_simulated") == False,
         f"is_simulated={loaded.get('is_simulated')}")
    test("T6.4 JSONL Price Preserved Correctly",
         loaded.get("price") == test_record.get("price"),
         f"price={loaded.get('price')}")
except Exception as e:
    test("T6.2 JSONL Read-Back Successful", False, str(e))

# Cleanup
if os.path.exists(test_log):
    os.remove(test_log)

# ─────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"  VERIFICATION SUMMARY")
print(f"{'='*65}")
total = len(PASSED) + len(FAILED)
print(f"  Total Tests : {total}")
print(f"  PASSED      : {len(PASSED)}")
print(f"  FAILED      : {len(FAILED)}")
print(f"  Pass Rate   : {len(PASSED)/total*100:.1f}%" if total > 0 else "  Pass Rate   : N/A")

if FAILED:
    print(f"\n  FAILED TESTS:")
    for f in FAILED:
        print(f"    - {f}")

verdict = "ALL TESTS PASS" if not FAILED else f"{len(FAILED)} TESTS FAILED"
print(f"\n  VERDICT: {verdict}")
print(f"{'='*65}")

sys.exit(0 if not FAILED else 1)
