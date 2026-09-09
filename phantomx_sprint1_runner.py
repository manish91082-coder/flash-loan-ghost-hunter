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

# Hardcoded major tokens per chain for testing Spatial Arbitrage (V3 Quoter vs V2 Pair)
# Note: Since finding real active V2 pairs dynamically requires a subgraph/indexer,
# we will use known token pairs and dummy pair addresses for V2 to verify architecture stability.
TOKENS = {
    8453: {"WETH": "0x4200000000000000000000000000000000000006", "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "v2_pair": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"},
    10: {"WETH": "0x4200000000000000000000000000000000000006", "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "v2_pair": "0x0000000000000000000000000000000000001234"},
    42161: {"WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "v2_pair": "0x0000000000000000000000000000000000001234"},
    1: {"WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "v2_pair": "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"},
    137: {"WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270", "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "v2_pair": "0x0000000000000000000000000000000000001234"},
    43114: {"WAVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", "v2_pair": "0x0000000000000000000000000000000000001234"},
    250: {"WFTM": "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83", "USDC": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75", "v2_pair": "0x0000000000000000000000000000000000001234"},
    42220: {"CELO": "0x471EcE3750Da237f93B8E339c536989b8978a438", "cUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a", "v2_pair": "0x0000000000000000000000000000000000001234"}
}

class DummyProvider:
    def calculate_premium(self, amt):
        return amt * 5 // 10000 # 0.05%

def run_sprint_1():
    print("=== STARTING SPRINT 1: SPATIAL ARBITRAGE ===")
    config_data = load_chain_config()
    report_file = os.path.join("PhantomX_Massive_Test_Reports", "Sprint_1_Spatial_Arbitrage.csv")
    
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Blockchain", "Pair", "Strategy", "Dex A Input", "Dex B Output", "Price Gap", "Gross Profit", "Gas Fees (Wei)", "Other Expenses", "Net Exact Profit (Tokens)"])
        
        for chain_id_str, config in config_data.items():
            if not isinstance(config, dict) or "chain_id" not in config:
                continue
            chain_id = int(chain_id_str)
            chain_name = config.get("name", str(chain_id))
            print(f"\n[Scout] Inspecting {chain_name} ({chain_id})")
            
            if chain_id not in TOKENS:
                print(f"  -> Tokens not defined for {chain_name}, skipping.")
                continue
                
            token_dict = TOKENS[chain_id]
            tokenA = list(token_dict.values())[1] # e.g. USDC
            tokenB = list(token_dict.values())[0] # e.g. WETH
            pair_name = f"{list(token_dict.keys())[1]}/{list(token_dict.keys())[0]}"
            v2_pair_address = token_dict.get("v2_pair")
            
            dexes = config.get("dexes", {})
            v3_dex = dexes.get("uniswap_v3")
            if not v3_dex:
                print(f"  -> No V3 Quoter config found on {chain_name}, skipping.")
                continue
                
            quoter_v3 = v3_dex.get("quoter")
            rpc_manager = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
            adapter_v2 = QuoteAdapterFactory.get_adapter('v2', rpc_manager)
            adapter_v3 = QuoteAdapterFactory.get_adapter('v3', rpc_manager)
            profit_calc = ProfitCalculator(DummyProvider())
            
            borrow_amount = 1000 * 10**6 # Assuming 6 decimals for TokenA (USDC)
            
            try:
                # DEX A: Quote V3 (TokenA -> TokenB)
                v3_state = adapter_v3.fetch_market_state(quoter_v3, tokenA, tokenB, borrow_amount, 500)
                amount_b = adapter_v3.calculate_out_given_in(v3_state, borrow_amount)
                
                # DEX B: Quote V2 (TokenB -> TokenA)
                v2_state = adapter_v2.fetch_market_state(v2_pair_address, tokenB)
                amount_a_out = adapter_v2.calculate_out_given_in(v2_state, amount_b, fee_bips=30)
                
                gross_profit = amount_a_out - borrow_amount
                
                # Gas Estimation
                gas_cost_wei = profit_calc.estimate_l2_gas(rpc_manager.w3, {"to": tokenA, "data": b'\x00'}, config)
                net_profit_tokens, is_safe, msg = profit_calc.calculate_net_profit(
                    borrow_amount, amount_a_out, gas_cost_wei, 6, 3000 * 10**6, config.get("zero_loss_guard", {}).get("min_profit_usd", 1.0), 1.0
                )
                
                print(f"  -> Tested {pair_name}: Gross {gross_profit}, Net {net_profit_tokens}")
                writer.writerow([
                    datetime.now().isoformat(),
                    chain_name,
                    pair_name,
                    "Spatial Arbitrage",
                    borrow_amount,
                    amount_a_out,
                    f"{gross_profit}",
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
                    "Spatial Arbitrage",
                    borrow_amount,
                    0,
                    0,
                    -borrow_amount,
                    0,
                    0,
                    -borrow_amount
                ])
                
            time.sleep(2) # Rate limit respect
            
    print("\n=== SPRINT 1 COMPLETE ===")

if __name__ == "__main__":
    run_sprint_1()
