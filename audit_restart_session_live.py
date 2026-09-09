import os
import json
import statistics
from datetime import datetime

def run_live_log_audit():
    base_dir = r"c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter"
    v2_file = os.path.join(base_dir, "phantomx_v2_realtime_transactions.jsonl")
    v3_file = os.path.join(base_dir, "phantomx_v3_realtime_transactions.jsonl")

    report_lines = []
    report_lines.append("================================================================================")
    report_lines.append("PHANTOMX LIVE SESSION REAL-TIME DATA FORENSIC AUDIT REPORT")
    report_lines.append(f"Audit Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append("================================================================================")

    for name, filepath in [("V2 MVP Direct Engine", v2_file), ("V3 Universal Triangular Engine", v3_file)]:
        report_lines.append(f"\n--- {name} ({os.path.basename(filepath)}) ---")
        if not os.path.exists(filepath):
            report_lines.append("Status: FILE NOT FOUND")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        total_recs = len(records)
        live_recs = sum(1 for r in records if r.get("is_live_data") is True)
        sim_recs = sum(1 for r in records if r.get("is_simulated") is True)
        
        blocks = [r.get("block_number") for r in records if r.get("block_number")]
        min_block = min(blocks) if blocks else 0
        max_block = max(blocks) if blocks else 0
        unique_blocks = len(set(blocks))

        spreads = [r.get("spread_pct", 0) for r in records if r.get("spread_pct") is not None]
        avg_spread = statistics.mean(spreads) if spreads else 0
        max_spread = max(spreads) if spreads else 0

        profits = [r.get("net_profit_usd", 0) for r in records if r.get("net_profit_usd") is not None]
        total_profit = sum(p for p in profits if p > 0)
        exec_count = sum(1 for r in records if r.get("action") == "EXECUTE")
        wait_count = sum(1 for r in records if r.get("action") == "WAIT")

        report_lines.append(f"Total Logged Records : {total_recs}")
        report_lines.append(f"Live Data Percentage  : {(live_recs/total_recs)*100:.2f}% ({live_recs}/{total_recs})")
        report_lines.append(f"Simulated Percentage  : {(sim_recs/total_recs)*100:.2f}% ({sim_recs}/{total_recs})")
        report_lines.append(f"Block Range Scanned   : #{min_block:,} -> #{max_block:,} ({unique_blocks} unique blocks)")
        report_lines.append(f"Average Spread (%)    : {avg_spread:.4f}% (Max: {max_spread:.4f}%)")
        report_lines.append(f"Execution Decisions   : EXECUTE: {exec_count} | WAIT: {wait_count}")
        report_lines.append(f"Cumulative Gross Arb  : ${total_profit:,.2f} USD")

    report_content = "\n".join(report_lines)
    print(report_content)

    # Write audit report file
    audit_out = os.path.join(base_dir, "PhantomX_Live_Session_Audit_Summary.txt")
    with open(audit_out, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"\nSaved forensic audit summary to: {audit_out}")

if __name__ == "__main__":
    run_live_log_audit()
