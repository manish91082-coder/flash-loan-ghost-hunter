import json
import os
import time
from auto_tuner_engine import OnlineSGDAutoTuner

v2_file = "shadow_metrics_v2_live.jsonl"
v3_file = "shadow_metrics_v3_live.jsonl"

def audit_jsonl(filepath):
    total = 0
    actions = {}
    spreads = []
    gas_list = []
    profits = []
    pairs = {}
    records = []

    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                records.append(data)
                total += 1
                act = data.get("action", "UNKNOWN")
                actions[act] = actions.get(act, 0) + 1
                
                sp = data.get("spread_pct", 0.0)
                if sp > 0:
                    spreads.append(sp)
                
                gas = data.get("gas_gwei", 0.0)
                if gas > 0:
                    gas_list.append(gas)
                    
                prof = data.get("expected_profit_usd", 0.0)
                profits.append(prof)
                
                pair = data.get("pair", "UNKNOWN")
                pairs[pair] = pairs.get(pair, 0) + 1
            except Exception:
                continue

    avg_spread = sum(spreads) / len(spreads) if spreads else 0.0
    max_spread = max(spreads) if spreads else 0.0
    avg_gas = sum(gas_list) / len(gas_list) if gas_list else 0.0
    max_profit = max(profits) if profits else 0.0

    return {
        "total_records": total,
        "actions_breakdown": actions,
        "avg_spread_pct": round(avg_spread, 4),
        "max_spread_pct": round(max_spread, 4),
        "avg_gas_gwei": round(avg_gas, 2),
        "max_profit_usd": round(max_profit, 4),
        "top_pairs": dict(sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:5]),
        "sample_records": records[-100:] if len(records) >= 100 else records
    }

print("================================================================================")
print("🔍 PHANTOMX LIVE TESTING & ONLINE SGD AUTO-TUNER FORENSIC AUDITOR")
print("================================================================================")

v2_audit = audit_jsonl(v2_file)
v3_audit = audit_jsonl(v3_file)

print("\n📊 1. V2 MVP Live Testing Telemetry Summary:")
if v2_audit:
    print(f"  • Total Blocks Audited: {v2_audit['total_records']:,}")
    print(f"  • Actions Breakdown: {v2_audit['actions_breakdown']}")
    print(f"  • Average Spread: {v2_audit['avg_spread_pct']}% | Max Spread: {v2_audit['max_spread_pct']}%")
    print(f"  • Average Gas Fee: {v2_audit['avg_gas_gwei']} Gwei")
    print(f"  • Top Monitored Pairs: {v2_audit['top_pairs']}")
else:
    print("  ⚠️ V2 Telemetry log empty or missing.")

print("\n📊 2. V3 Universal Live Testing Telemetry Summary:")
if v3_audit:
    print(f"  • Total Blocks Audited: {v3_audit['total_records']:,}")
    print(f"  • Actions Breakdown: {v3_audit['actions_breakdown']}")
    print(f"  • Average Spread: {v3_audit['avg_spread_pct']}% | Max Spread: {v3_audit['max_spread_pct']}%")
    print(f"  • Average Gas Fee: {v3_audit['avg_gas_gwei']} Gwei")
    print(f"  • Top Monitored Pairs: {v3_audit['top_pairs']}")
else:
    print("  ⚠️ V3 Telemetry log empty or missing.")

# Test Online SGD Auto-Tuner on actual live records
print("\n🎯 3. Executing Online SGD Auto-Tuner on Live Telemetry Data...")
tuner = OnlineSGDAutoTuner()
print(f"  • SGD Tuner Active Version: {tuner.version}")

all_sample = (v2_audit['sample_records'] if v2_audit else []) + (v3_audit['sample_records'] if v3_audit else [])
missed = tuner.audit_missed_opportunities(all_sample)

print(f"  • Scanned {len(all_sample)} Recent Block Records.")
print(f"  • Missed Micro-Opportunities Detected ($0.15-$0.45 Spreads): {len(missed)}")

if missed:
    print(f"  • Sample Missed Record: {missed[0]}")

current_gas = (v2_audit['avg_gas_gwei'] if v2_audit else 50.0)
tuning_result = tuner.auto_tune_parameters(missed, current_gas_gwei=current_gas)

print("\n🔧 4. Online SGD Auto-Tuning Calibration Result:")
print(json.dumps(tuning_result, indent=2))

print("\n================================================================================")
