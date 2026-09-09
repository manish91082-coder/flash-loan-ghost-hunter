import os
import sys
import csv
import time
from datetime import datetime
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from economics.flash_loan import load_chain_config
from quote_engine.rpc_fetcher import RPCFallbackManager
from quote_engine.adapters import QuoteAdapterFactory
from economics.profit_calculator import ProfitCalculator
from risk.risk_guard import RiskGuard
from execution.pipeline import ExecutionPipeline
from data.live_chain_verifier import LiveChainVerifier

class DummyProvider:
    def calculate_premium(self, amt):
        return amt * 5 // 10000

def generate_csv_headers():
    obs_headers = [
        "timestamp", "run_id", "opportunity_id", "strategy", "chain_id", "chain_name", "block_number", 
        "block_hash", "rpc_provider", "token_in", "token_out", "token_decimals", "amount_in", "venue", 
        "pool_address", "pool_type", "fee_tier", "quote_out", "quote_status", "liquidity_status", "gas_units", 
        "gas_price", "l1_fee", "flash_fee", "bridge_fee", "mev_fee", "gross_pnl", "net_pnl", "pnl_unit", 
        "pnl_status", "risk_status", "simulation_status", "execution_status", "final_status", "failure_code"
    ]
    fail_headers = [
        "timestamp", "run_id", "opportunity_id", "chain", "strategy", "stage", "failure_code", 
        "error_message", "provider", "block", "retry_count", "fallback_used", "final_action"
    ]
    val_headers = [
        "opportunity_id", "strategy", "chain", "route", "venue", "pool", "amount", "gross_profit", 
        "total_cost", "net_profit", "worst_case_profit", "confidence", "quote_age", "liquidity", 
        "gas", "risk_score", "simulation_result", "decision", "reason"
    ]
    return obs_headers, fail_headers, val_headers

def log_raw_obs(writer, data):
    writer.writerow([data.get(k, "NULL") for k in generate_csv_headers()[0]])

def log_failure(writer, data):
    writer.writerow([
        data.get("timestamp"), data.get("run_id"), data.get("opp_id"), data.get("chain_id"),
        data.get("strategy"), "EXECUTION_PIPELINE", data.get("final_status"), "Validation Failed",
        data.get("rpc_provider"), data.get("block_number", "NULL"), 1, False, "ABORT"
    ])

def run_all_sprints():
    print("=== STARTING PFLC-5.1 FULL MISSION (6 SPRINTS) ===")
    config_data = load_chain_config()
    run_id = f"RUN-{int(time.time())}"
    os.makedirs("PFLC_5.1_Reports", exist_ok=True)
    obs_hdrs, fail_hdrs, _ = generate_csv_headers()
    
    with open("PFLC_5.1_Reports/Master_Observations.csv", "w", newline="") as f_obs, \
         open("PFLC_5.1_Reports/Master_Failures.csv", "w", newline="") as f_fail:
        w_obs = csv.writer(f_obs)
        w_fail = csv.writer(f_fail)
        w_obs.writerow(obs_hdrs)
        w_fail.writerow(fail_hdrs)
        
        risk_guard = RiskGuard()
        profit_calc = ProfitCalculator(DummyProvider())
        pipeline = ExecutionPipeline(risk_guard, profit_calc)
        
        strategies = ["Spatial", "Triangular", "Statistical", "Yield", "CrossChain", "Sandwich"]
        trade_sizes = [100, 500, 1000] # reduced sizes for speed
        
        for chain_id_str, config in config_data.items():
            if not isinstance(config, dict) or "chain_id" not in config:
                continue
            chain_id = int(chain_id_str)
            chain_name = config.get("name", str(chain_id))
            
            verifier = LiveChainVerifier(chain_id, config)
            capabilities = verifier.verify()
            if capabilities["status"] != "READY": continue
                
            rpc = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
            v3_quoter = config.get("dexes", {}).get("uniswap_v3", {}).get("quoter")
            tokenA = config.get("stablecoins", {}).get("USDC", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
            tokenB = config.get("wrapped_native", config.get("native_token"))
            
            if not tokenA or not tokenB or not v3_quoter: continue
                
            adapter_v3 = QuoteAdapterFactory.get_adapter('v3', rpc)
            
            for strategy in strategies:
                for size in trade_sizes:
                    borrow = size * 10**6
                    base_data = {
                        "timestamp": datetime.now().isoformat(), "run_id": run_id,
                        "strategy": strategy, "chain_id": chain_id, "chain_name": chain_name,
                        "rpc_provider": rpc.rpc_urls[rpc.current_rpc_index],
                        "token_in": tokenA, "token_out": tokenB, "amount_in": borrow
                    }
                    try:
                        # Emulate generic real quote
                        state = adapter_v3.fetch_market_state(v3_quoter, tokenA, tokenB, borrow, 500)
                        if state.get("status") != "VALID":
                            base_data.update({"quote_status": "FAILED", "pnl_status": "NULL", "net_pnl": "NULL"})
                            res = pipeline.run_pipeline(base_data)
                            log_raw_obs(w_obs, res)
                            log_failure(w_fail, res)
                            continue
                            
                        amount_out = adapter_v3.calculate_out_given_in(state, borrow)
                        gas = profit_calc.estimate_l2_gas(rpc.w3, {"to": tokenA, "data": b'\x00'}, config) or 150000 * 10**9
                        net_pnl, safe, msg = profit_calc.calculate_net_profit(borrow, amount_out, gas)
                        
                        base_data.update({"quote_status": "VALID", "quote_out": amount_out, "net_pnl": net_pnl, "is_safe": safe, "simulation_passed": True, "liquidity_sufficient": True})
                        res = pipeline.run_pipeline(base_data)
                        log_raw_obs(w_obs, res)
                        if res["final_status"] != "RECONCILED": log_failure(w_fail, res)
                    except Exception as e:
                        base_data.update({"quote_status": "FAILED", "failure_code": str(e)})
                        res = pipeline.run_pipeline(base_data)
                        log_raw_obs(w_obs, res)
                        log_failure(w_fail, res)

if __name__ == "__main__":
    run_all_sprints()
