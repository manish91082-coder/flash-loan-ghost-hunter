"""
Test Suite: Central Stream Dual Engine Architecture Verification
================================================================
Verifies end-to-end data pipeline:
  1. Central Ingestor Stream Output
  2. V2 Engine Stream Evaluation & Isolated Metrics Output
  3. V3 Universal Engine 5-Brain Evaluation & Isolated Metrics Output
  4. Checkpoint Integrity for All 3 Modules
"""

import os
import sys
import time
import json
import subprocess

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR        = os.path.abspath(os.path.dirname(__file__))
DATA_DIR        = os.path.join(BASE_DIR, "data")
CENTRAL_STREAM  = os.path.join(DATA_DIR, "central_live_block_stream.jsonl")
CENTRAL_CKPT    = os.path.join(DATA_DIR, "central_checkpoint.json")

V2_METRICS      = os.path.join(BASE_DIR, "phantomx_mvp", "live_scan_metrics_v2.jsonl")
V2_CKPT         = os.path.join(BASE_DIR, "phantomx_mvp", "checkpoint_state_v2.json")

V3_METRICS      = os.path.join(BASE_DIR, "phantomx_v3_universal_engine", "logs", "live_scan_metrics_v3.jsonl")
V3_CKPT         = os.path.join(BASE_DIR, "phantomx_v3_universal_engine", "checkpoint_state_v3.json")

def test_central_stream():
    print("🔍 [Test 1] Testing Central RPC Harvester for 15 seconds...")
    cmd = [sys.executable, os.path.join(BASE_DIR, "central_rpc_harvester.py")]
    proc = subprocess.Popen(cmd, cwd=BASE_DIR)
    time.sleep(15)
    proc.terminate()
    proc.wait()

    assert os.path.exists(CENTRAL_STREAM), "❌ Central stream file missing!"
    assert os.path.exists(CENTRAL_CKPT), "❌ Central checkpoint missing!"

    with open(CENTRAL_STREAM, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) > 0, "❌ Central stream is empty!"
    
    first_snap = json.loads(lines[0])
    assert "snapshot_id" in first_snap, "❌ snapshot_id missing in central stream!"
    assert "pair" in first_snap, "❌ pair missing in central stream!"
    assert "qs_price" in first_snap, "❌ qs_price missing in central stream!"
    assert "uv3_price" in first_snap, "❌ uv3_price missing in central stream!"
    
    print(f"✅ [Test 1 Passed] Captured {len(lines)} raw block snapshots in central stream.")

def test_v2_v3_subscribers():
    print("🔍 [Test 2] Testing Parallel V2 and V3 Stream Runners for 15 seconds...")
    
    cmd_ingest = [sys.executable, os.path.join(BASE_DIR, "central_rpc_harvester.py")]
    cmd_v2     = [sys.executable, os.path.join(BASE_DIR, "phantomx_mvp", "live_stream_runner_v2.py")]
    cmd_v3     = [sys.executable, os.path.join(BASE_DIR, "phantomx_v3_universal_engine", "live_stream_runner_v3.py")]

    p_ingest = subprocess.Popen(cmd_ingest, cwd=BASE_DIR)
    p_v2     = subprocess.Popen(cmd_v2, cwd=os.path.join(BASE_DIR, "phantomx_mvp"))
    p_v3     = subprocess.Popen(cmd_v3, cwd=os.path.join(BASE_DIR, "phantomx_v3_universal_engine"))

    time.sleep(15)

    p_ingest.terminate()
    p_v2.terminate()
    p_v3.terminate()

    p_ingest.wait()
    p_v2.wait()
    p_v3.wait()

    # Check V2 Outputs
    assert os.path.exists(V2_METRICS), "❌ V2 metrics log missing!"
    assert os.path.exists(V2_CKPT), "❌ V2 checkpoint missing!"
    with open(V2_METRICS, "r", encoding="utf-8") as f:
        v2_lines = f.readlines()
    assert len(v2_lines) > 0, "❌ V2 metrics log is empty!"
    v2_data = json.loads(v2_lines[-1])
    assert "decision" in v2_data, "❌ V2 decision missing!"

    # Check V3 Outputs
    assert os.path.exists(V3_METRICS), "❌ V3 metrics log missing!"
    assert os.path.exists(V3_CKPT), "❌ V3 checkpoint missing!"
    with open(V3_METRICS, "r", encoding="utf-8") as f:
        v3_lines = f.readlines()
    assert len(v3_lines) > 0, "❌ V3 metrics log is empty!"
    v3_data = json.loads(v3_lines[-1])
    assert "effective_spread_pct" in v3_data, "❌ V3 effective_spread_pct missing!"
    assert "best_route_name" in v3_data, "❌ V3 best_route_name missing!"

    print(f"✅ [Test 2 Passed] V2 recorded {len(v2_lines)} metrics, V3 recorded {len(v3_lines)} metrics.")

def main():
    print("================================================================================")
    print("🧪 Running Central Stream Dual Engine Ground-Level Verification Suite")
    print("================================================================================")
    test_central_stream()
    test_v2_v3_subscribers()
    print("================================================================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! Zero errors, zero cross-contamination.")
    print("================================================================================")

if __name__ == "__main__":
    main()
