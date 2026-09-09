# ==============================================================================
# PHANTOMX SURGICAL AUDITOR: TODAY'S LIVE SESSION (09:00 AM - 15:30 PM IST)
# ==============================================================================
# Architecture Discipline: Surgical | Aviation | Military
# Filter: Strictly records from TODAY (2026-09-08 09:00:00 to current time)
# ==============================================================================

import json
import os
import sys
from datetime import datetime

# Safe stdout UTF-8 encoding configuration
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

v2_file = "shadow_metrics_v2_live.jsonl"
v3_file = "shadow_metrics_v3_live.jsonl"

def audit_today_session(filepath, engine_name):
    if not os.path.exists(filepath):
        return None

    today_records = []
    actions = {}
    spreads = []
    loans = []
    gas_prices = []
    pairs = {}
    
    start_ts = None
    end_ts = None
    start_blk = None
    end_blk = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                ts = rec.get("timestamp", "")
                
                # Filter strictly for today's session (09:00:00 AM IST onwards)
                if ts.startswith("2026-09-08") and ts[11:] >= "09:00:00":
                    blk = rec.get("block_number")
                    if not start_ts:
                        start_ts = ts
                        start_blk = blk
                    end_ts = ts
                    end_blk = blk
                    
                    today_records.append(rec)
                    
                    act = rec.get("action", "UNKNOWN")
                    actions[act] = actions.get(act, 0) + 1
                    
                    pair = rec.get("pair") or rec.get("route", "UNKNOWN")
                    pairs[pair] = pairs.get(pair, 0) + 1
                    
                    sp = rec.get("spread_pct", 0.0)
                    loan = rec.get("optimal_loan_usd", 0.0)
                    gas = rec.get("gas_gwei", 0.0)
                    
                    if sp > 0: spreads.append(sp)
                    if loan > 0: loans.append(loan)
                    if gas > 0: gas_prices.append(gas)
            except Exception:
                continue

    avg_spread = sum(spreads) / len(spreads) if spreads else 0.0
    max_spread = max(spreads) if spreads else 0.0
    avg_loan = sum(loans) / len(loans) if loans else 0.0
    max_loan = max(loans) if loans else 0.0
    avg_gas = sum(gas_prices) / len(gas_prices) if gas_prices else 0.0

    return {
        "engine": engine_name,
        "today_blocks_scanned": len(today_records),
        "time_window": f"{start_ts} ➔ {end_ts}",
        "block_range": f"#{start_blk:,} ➔ #{end_blk:,}",
        "actions_breakdown": actions,
        "avg_spread_pct": round(avg_spread, 4),
        "max_spread_pct": round(max_spread, 4),
        "avg_loan_usd": round(avg_loan, 2),
        "max_loan_usd": round(max_loan, 2),
        "avg_gas_gwei": round(avg_gas, 2),
        "top_pairs": dict(sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:5]),
        "latest_5_records": today_records[-5:] if today_records else []
    }

print("================================================================================")
print("🔍 SURGICAL FORENSIC AUDIT: TODAY'S LIVE TESTING SESSION (09:00 AM - 15:30 PM)")
print("================================================================================")

v2_today = audit_today_session(v2_file, "V2_MVP_ENGINE")
v3_today = audit_today_session(v3_file, "V3_UNIVERSAL_ENGINE")

print("\n📊 1. TODAY'S V2 MVP LIVE SESSION TELEMETRY:")
if v2_today:
    print(f"  • Total Blocks Audited Today: {v2_today['today_blocks_scanned']:,}")
    print(f"  • Time Horizon: {v2_today['time_window']}")
    print(f"  • Block Range: {v2_today['block_range']}")
    print(f"  • Actions Breakdown: {v2_today['actions_breakdown']}")
    print(f"  • Average Spread: {v2_today['avg_spread_pct']}% | Max Spread: {v2_today['max_spread_pct']}%")
    print(f"  • Average Loan: ${v2_today['avg_loan_usd']} | Max Loan: ${v2_today['max_loan_usd']}")
    print(f"  • Top Monitored Pairs: {v2_today['top_pairs']}")
else:
    print("  ⚠️ No today records found for V2.")

print("\n📊 2. TODAY'S V3 UNIVERSAL LIVE SESSION TELEMETRY:")
if v3_today:
    print(f"  • Total Blocks Audited Today: {v3_today['today_blocks_scanned']:,}")
    print(f"  • Time Horizon: {v3_today['time_window']}")
    print(f"  • Block Range: {v3_today['block_range']}")
    print(f"  • Actions Breakdown: {v3_today['actions_breakdown']}")
    print(f"  • Average Spread: {v3_today['avg_spread_pct']}% | Max Spread: {v3_today['max_spread_pct']}%")
    print(f"  • Average Loan: ${v3_today['avg_loan_usd']} | Max Loan: ${v3_today['max_loan_usd']}")
    print(f"  • Top Monitored Pairs: {v3_today['top_pairs']}")
else:
    print("  ⚠️ No today records found for V3.")

print("\n================================================================================")
