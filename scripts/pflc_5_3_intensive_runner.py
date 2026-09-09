import os
import sys
import csv
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from economics.flash_loan import load_chain_config
from quote_engine.rpc_fetcher import RPCFallbackManager
from quote_engine.adapters import QuoteAdapterFactory
from economics.profit_calculator import ProfitCalculator
from risk.risk_guard import RiskGuard
from execution.pipeline import ExecutionPipeline
from data.live_chain_verifier import LiveChainVerifier

class LiveFlashProvider:
    def __init__(self, fee_bips=5):
        self.fee_bips = fee_bips
        
    def calculate_premium(self, amt):
        return amt * self.fee_bips // 10000

def run_intensive_mode():
    print("\n=== STARTING 30-MINUTE INTENSIVE MODE ===")
    config_data = load_chain_config()
    
    os.makedirs("PFLC_5.3_Reports", exist_ok=True)
    report_file = "PFLC_5.3_Reports/Intensive_30Min_Report.csv"
    
    headers = [
        "minute_id", "chains_checked", "pairs_checked", "routes_checked", 
        "valid_quotes", "data_failures", "quote_failures", "liquidity_failures", 
        "risk_rejections", "simulation_failures", "candidates", "best_candidate", "final_result"
    ]
    
    with open(report_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for minute in range(1, 31):
            print(f"\n--- Minute {minute}/30 ---")
            stats = {
                "minute_id": minute,
                "chains_checked": 0,
                "pairs_checked": 0,
                "routes_checked": 0,
                "valid_quotes": 0,
                "data_failures": 0,
                "quote_failures": 0,
                "liquidity_failures": 0,
                "risk_rejections": 0,
                "simulation_failures": 0,
                "candidates": 0,
                "best_candidate": "None",
                "final_result": "NO_CONFIRMED_OPPORTUNITY"
            }
            
            for chain_id_str, config in config_data.items():
                if not isinstance(config, dict) or "chain_id" not in config:
                    continue
                stats["chains_checked"] += 1
                
                try:
                    verifier = LiveChainVerifier(int(chain_id_str), config)
                    cap = verifier.verify()
                    if cap["status"] != "READY":
                        stats["data_failures"] += 1
                        continue
                        
                    rpc = RPCFallbackManager(config.get("rpc_urls", []), int(chain_id_str))
                    
                    # Actual route checking logic
                    v3_quoter = config.get("dexes", {}).get("uniswap_v3", {}).get("quoter")
                    tokenA = config.get("stablecoins", {}).get("USDC")
                    tokenB = config.get("wrapped_native")
                    
                    if not (v3_quoter and tokenA and tokenB):
                        stats["data_failures"] += 1
                        continue
                        
                    stats["pairs_checked"] += 1
                    stats["routes_checked"] += 1
                    
                    adapter_v3 = QuoteAdapterFactory.get_adapter('v3', rpc)
                    borrow_amount = 1000 * 10**6
                    
                    v3_state = adapter_v3.fetch_market_state(v3_quoter, tokenA, tokenB, borrow_amount, 500)
                    if v3_state.get("status") == "VALID":
                        stats["valid_quotes"] += 1
                    else:
                        stats["quote_failures"] += 1
                        
                except Exception as e:
                    print(f"Exception on chain {chain_id_str}: {e}")
                    stats["data_failures"] += 1
            
            if stats["valid_quotes"] == 0:
                stats["final_result"] = "DATA_ERROR"
                
            writer.writerow([stats[k] for k in headers])
            f.flush()
            
            print(f"Minute {minute} complete. {stats['valid_quotes']} valid quotes.")
            
            # Real 30-minute intensive mode
            time.sleep(60)
            
    print("\n=== 30-MINUTE INTENSIVE MODE COMPLETE ===")

if __name__ == "__main__":
    run_intensive_mode()
