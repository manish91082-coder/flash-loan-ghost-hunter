# ==============================================================================
# PHANTOMX DEEP PROFITABILITY & SHADOW TELEMETRY INSPECTOR
# ==============================================================================
# Architecture Discipline: Surgical | Aviation | Military
# Description: Parses 100% of shadow_metrics_v2_live.jsonl & shadow_metrics_v3_live.jsonl.
#              Generates timestamp-by-timestamp profit breakdown, DEX fee impact audit,
#              and SGD Auto-Tuner calibration verification.
# ==============================================================================

import json
import os
import sys
from datetime import datetime
from auto_tuner_engine import OnlineSGDAutoTuner

# Safe stdout UTF-8 encoding configuration
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

v2_file = "shadow_metrics_v2_live.jsonl"
v3_file = "shadow_metrics_v3_live.jsonl"

def inspect_engine_telemetry(filepath, engine_name):
    if not os.path.exists(filepath):
        return None

    total_records = 0
    start_time = None
    end_time = None
    start_block = None
    end_block = None
    
    actions = {}
    pairs = {}
    spreads = []
    loans = []
    theo_profits = []
    
    timestamped_opportunities = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                total_records += 1
                
                ts = rec.get("timestamp")
                blk = rec.get("block_number")
                if not start_time:
                    start_time = ts
                    start_block = blk
                end_time = ts
                end_block = blk
                
                act = rec.get("action", "UNKNOWN")
                actions[act] = actions.get(act, 0) + 1
                
                pair = rec.get("pair") or rec.get("route", "UNKNOWN")
                pairs[pair] = pairs.get(pair, 0) + 1
                
                sp = rec.get("spread_pct", 0.0)
                loan = rec.get("optimal_loan_usd", 0.0)
                if sp > 0:
                    spreads.append(sp)
                if loan > 0:
                    loans.append(loan)

                # Calculate gross yield and theoretical net yield after fees (0.60% DEX + 0.05% Aave)
                if sp >= 0.15 and loan > 0:
                    gross_yield = loan * (sp / 100.0)
                    total_fee = loan * (0.60 / 100.0) + (loan * 0.0005)  # 0.60% DEX fee + 0.05% Aave flash fee
                    net_yield = max(0.0, gross_yield - total_fee)
                    
                    if net_yield >= 0.15:
                        theo_profits.append(net_yield)
                        timestamped_opportunities.append({
                            "timestamp": ts,
                            "block_number": blk,
                            "pair_or_route": pair,
                            "spread_pct": sp,
                            "loan_usd": loan,
                            "gross_yield_usd": round(gross_yield, 4),
                            "net_yield_usd": round(net_yield, 4),
                            "action_taken": act,
                            "reason": "Yield below $0.50 floor" if act == "WAIT" else "Eligible"
                        })
            except Exception:
                continue

    return {
        "engine": engine_name,
        "total_blocks_scanned": total_records,
        "time_range": f"{start_time} ➔ {end_time}",
        "block_range": f"#{start_block:,} ➔ #{end_block:,}",
        "actions_breakdown": actions,
        "avg_spread_pct": round(sum(spreads)/len(spreads), 4) if spreads else 0.0,
        "max_spread_pct": round(max(spreads), 4) if spreads else 0.0,
        "avg_loan_usd": round(sum(loans)/len(loans), 2) if loans else 0.0,
        "max_loan_usd": round(max(loans), 2) if loans else 0.0,
        "total_opportunities_detected": len(timestamped_opportunities),
        "total_theoretical_net_profit_usd": round(sum(theo_profits), 4),
        "max_single_trade_net_profit_usd": round(max(theo_profits), 4) if theo_profits else 0.0,
        "timestamped_opportunities_sample": timestamped_opportunities[-15:] if timestamped_opportunities else []
    }

print("================================================================================")
print("🔍 PHANTOMX LIVE TELEMETRY & PROFITABILITY FORENSIC INSPECTOR")
print("================================================================================")

v2_data = inspect_engine_telemetry(v2_file, "V2_MVP_ENGINE")
v3_data = inspect_engine_telemetry(v3_file, "V3_UNIVERSAL_ENGINE")

print("\n📊 1. V2 MVP Engine Profitability Telemetry:")
if v2_data:
    print(f"  • Total Blocks Audited: {v2_data['total_blocks_scanned']:,} | Range: {v2_data['block_range']}")
    print(f"  • Time Horizon: {v2_data['time_range']}")
    print(f"  • Actions Breakdown: {v2_data['actions_breakdown']}")
    print(f"  • Average Spread: {v2_data['avg_spread_pct']}% | Max Spread: {v2_data['max_spread_pct']}%")
    print(f"  • Average Loan: ${v2_data['avg_loan_usd']} | Max Loan: ${v2_data['max_loan_usd']}")
    print(f"  • Micro-Opportunities Detected ($0.15+ Net Yield): {v2_data['total_opportunities_detected']}")
    print(f"  • Cumulative Theoretical Net Yield: ${v2_data['total_theoretical_net_profit_usd']} USDC")
    print(f"  • Max Single Trade Net Yield: ${v2_data['max_single_trade_net_profit_usd']} USDC")
else:
    print("  ⚠️ V2 Telemetry log missing.")

print("\n📊 2. V3 Universal Engine Profitability Telemetry:")
if v3_data:
    print(f"  • Total Blocks Audited: {v3_data['total_blocks_scanned']:,} | Range: {v3_data['block_range']}")
    print(f"  • Time Horizon: {v3_data['time_range']}")
    print(f"  • Actions Breakdown: {v3_data['actions_breakdown']}")
    print(f"  • Average Spread: {v3_data['avg_spread_pct']}% | Max Spread: {v3_data['max_spread_pct']}%")
    print(f"  • Average Loan: ${v3_data['avg_loan_usd']} | Max Loan: ${v3_data['max_loan_usd']}")
    print(f"  • Micro-Opportunities Detected ($0.15+ Net Yield): {v3_data['total_opportunities_detected']}")
    print(f"  • Cumulative Theoretical Net Yield: ${v3_data['total_theoretical_net_profit_usd']} USDC")
    print(f"  • Max Single Trade Net Yield: ${v3_data['max_single_trade_net_profit_usd']} USDC")
else:
    print("  ⚠️ V3 Telemetry log missing.")

print("\n🎯 3. Online SGD Auto-Tuner Calibration & Threshold Shift:")
tuner = OnlineSGDAutoTuner()
print(f"  • Tuner Active Version: {tuner.version}")
print(f"  • Pre-Tuning Minimum Profit Floor: $0.50 USDC")

# Run post-block audit on sample
all_samples = (v2_data['timestamped_opportunities_sample'] if v2_data else []) + (v3_data['timestamped_opportunities_sample'] if v3_data else [])
missed = tuner.audit_missed_opportunities(all_samples)
calib = tuner.auto_tune_parameters(missed, current_gas_gwei=35.0)

print(f"  • Post-Tuning Calibrated Profit Floor: ${tuner.dynamic_min_profit_usd} USDC")
print(f"  • Calibrated Loan Scaler Multiplier ($L^*): {tuner.loan_scaler_multiplier:.3f}x")
print(f"  • Calibrated MEV Bribe Multiplier: {tuner.mev_bribe_multiplier:.3f}x")

print("\n================================================================================")
