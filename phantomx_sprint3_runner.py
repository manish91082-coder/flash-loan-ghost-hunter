import os
import sys
import csv
import time
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from economics.flash_loan import load_chain_config
from quote_engine.rpc_fetcher import RPCFallbackManager
from quote_engine.adapters import QuoteAdapterFactory
from economics.profit_calculator import ProfitCalculator

# Statistical Arbitrage Tokens (Stablecoins USDC <-> USDT)
TOKENS = {
    1: {"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7"},
    10: {"USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"},
    137: {"USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"},
    42161: {"USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"},
    8453: {"USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"} # Base bridged USDT
}

class DummyProvider:
    def calculate_premium(self, amt):
        return amt * 5 // 10000

def run_sprint_3():
    print("=== STARTING SPRINT 3: STATISTICAL ARBITRAGE (MEAN REVERSION) ===")
    config_data = load_chain_config()
    report_file = os.path.join("PhantomX_Massive_Test_Reports", "Sprint_3_Statistical_Arbitrage.csv")
    
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Blockchain", "Pair", "Strategy", "Input (USDC)", "Target Value (USDT)", "Reversion Gap", "Gross Profit", "Gas Fees (Wei)", "Other Expenses", "Net Exact Profit"])
        
        for chain_id_str, config in config_data.items():
            if not isinstance(config, dict) or "chain_id" not in config:
                continue
            chain_id = int(chain_id_str)
            chain_name = config.get("name", str(chain_id))
            print(f"\n[Scout] Inspecting Stablecoin Pegs on {chain_name} ({chain_id})")
            
            if chain_id not in TOKENS:
                print(f"  -> Tokens not defined for {chain_name}, skipping.")
                continue
                
            token_dict = TOKENS[chain_id]
            tokenA = token_dict.get("USDC")
            tokenB = token_dict.get("USDT")
            pair_name = "USDC / USDT"
            
            dexes = config.get("dexes", {})
            v3_dex = dexes.get("uniswap_v3")
            if not v3_dex:
                print(f"  -> No V3 config found on {chain_name}, skipping.")
                continue
                
            quoter = v3_dex.get("quoter")
            rpc_manager = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
            adapter = QuoteAdapterFactory.get_adapter('v3', rpc_manager)
            profit_calc = ProfitCalculator(DummyProvider())
            
            borrow_amount = 10000 * 10**6 # 10k USDC
            
            try:
                # Get real V3 Quote for USDC -> USDT
                state = adapter.fetch_market_state(quoter, tokenA, tokenB, borrow_amount, 100) # 1bp fee tier for stables
                amount_b = adapter.calculate_out_given_in(state, borrow_amount)
                
                # Mean Reversion Logic: Assume 1 USDT = 1 USDC eventually.
                # If amount_b > borrow_amount, we hold USDT and wait for reversion.
                reversion_gap = amount_b - borrow_amount
                gross_profit = reversion_gap
                
                gas_cost_wei = profit_calc.estimate_l2_gas(rpc_manager.w3, {"to": tokenA, "data": b'\x00'}, config)
                net_profit_tokens, is_safe, msg = profit_calc.calculate_net_profit(
                    borrow_amount, borrow_amount + gross_profit, gas_cost_wei, 6, 3000 * 10**6, 1.0, 1.0
                )
                
                print(f"  -> Tested {pair_name}: Reversion Gap {reversion_gap}, Net {net_profit_tokens}")
                writer.writerow([
                    datetime.now().isoformat(),
                    chain_name,
                    pair_name,
                    "Statistical/Mean Reversion",
                    borrow_amount,
                    amount_b,
                    reversion_gap,
                    gross_profit,
                    gas_cost_wei,
                    0,
                    net_profit_tokens
                ])
                
            except Exception as e:
                print(f"  -> [Execution Engine Failed] {e}")
                writer.writerow([
                    datetime.now().isoformat(),
                    chain_name,
                    pair_name,
                    "Statistical/Mean Reversion",
                    borrow_amount,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0
                ])
                
            time.sleep(2)
            
    print("\n=== SPRINT 3 COMPLETE ===")

if __name__ == "__main__":
    run_sprint_3()
