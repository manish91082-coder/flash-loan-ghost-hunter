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

# Triangular Arbitrage Tokens (A -> B -> C -> A)
# Token A = USDC, Token B = Native, Token C = WETH
TOKENS = {
    137: {"USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270", "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    8453: {"USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "WETH": "0x4200000000000000000000000000000000000006", "cbBTC": "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    10: {"USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "WETH": "0x4200000000000000000000000000000000000006", "OP": "0x4200000000000000000000000000000000000042", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    42161: {"USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    1: {"USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    43114: {"USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", "WAVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", "WETH": "0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    250: {"USDC": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75", "WFTM": "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83", "WETH": "0x74b23882a30290451A17c44f4F05243b6b58C76d", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"},
    42220: {"cUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a", "CELO": "0x471EcE3750Da237f93B8E339c536989b8978a438", "WETH": "0x122013fd7dF1C6F636a5bb8f03108E876548b4C5", "poolAB": "0x00001", "poolBC": "0x00002", "poolCA": "0x00003"}
}

class DummyProvider:
    def calculate_premium(self, amt):
        return amt * 5 // 10000

def run_sprint_2():
    print("=== STARTING SPRINT 2: TRIANGULAR ARBITRAGE ===")
    config_data = load_chain_config()
    report_file = os.path.join("PhantomX_Massive_Test_Reports", "Sprint_2_Triangular_Arbitrage.csv")
    
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Blockchain", "Path (A->B->C->A)", "Strategy", "Input A", "Output A", "Gross Profit", "Gas Fees (Wei)", "Other Expenses", "Net Exact Profit"])
        
        for chain_id_str, config in config_data.items():
            if not isinstance(config, dict) or "chain_id" not in config:
                continue
            chain_id = int(chain_id_str)
            chain_name = config.get("name", str(chain_id))
            print(f"\n[Scout] Inspecting Triangular Paths on {chain_name} ({chain_id})")
            
            if chain_id not in TOKENS:
                print(f"  -> Tokens not defined for {chain_name}, skipping.")
                continue
                
            token_dict = TOKENS[chain_id]
            tokenA = list(token_dict.values())[0]
            tokenB = list(token_dict.values())[1]
            tokenC = list(token_dict.values())[2]
            path_name = f"{list(token_dict.keys())[0]} -> {list(token_dict.keys())[1]} -> {list(token_dict.keys())[2]} -> {list(token_dict.keys())[0]}"
            
            dexes = config.get("dexes", {})
            v3_dex = dexes.get("uniswap_v3")
            if not v3_dex:
                print(f"  -> No V3 config found on {chain_name}, skipping.")
                continue
                
            quoter = v3_dex.get("quoter")
            rpc_manager = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
            adapter = QuoteAdapterFactory.get_adapter('v3', rpc_manager)
            profit_calc = ProfitCalculator(DummyProvider())
            
            borrow_amount = 1000 * 10**6
            
            try:
                # Hop 1: A -> B
                state1 = adapter.fetch_market_state(quoter, tokenA, tokenB, borrow_amount, 500)
                amount_b = adapter.calculate_out_given_in(state1, borrow_amount)
                
                # Hop 2: B -> C (Using same quoter for testing logic flow)
                state2 = adapter.fetch_market_state(quoter, tokenB, tokenC, amount_b, 500)
                amount_c = adapter.calculate_out_given_in(state2, amount_b)
                
                # Hop 3: C -> A
                state3 = adapter.fetch_market_state(quoter, tokenC, tokenA, amount_c, 500)
                amount_a_out = adapter.calculate_out_given_in(state3, amount_c)
                
                gross_profit = amount_a_out - borrow_amount
                
                # Gas Estimation (1.5x for 3 hops as defined in docs)
                gas_cost_wei = profit_calc.estimate_l2_gas(rpc_manager.w3, {"to": tokenA, "data": b'\x00'*300}, config)
                gas_cost_wei = int(gas_cost_wei * 1.5)
                
                net_profit_tokens, is_safe, msg = profit_calc.calculate_net_profit(
                    borrow_amount, amount_a_out, gas_cost_wei, 6, 3000 * 10**6, 1.0, 1.0
                )
                
                print(f"  -> Tested {path_name}: Gross {gross_profit}, Net {net_profit_tokens}")
                writer.writerow([
                    datetime.now().isoformat(),
                    chain_name,
                    path_name,
                    "Triangular",
                    borrow_amount,
                    amount_a_out,
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
                    path_name,
                    "Triangular",
                    borrow_amount,
                    0,
                    -borrow_amount,
                    0,
                    0,
                    -borrow_amount
                ])
                
            time.sleep(2)
            
    print("\n=== SPRINT 2 COMPLETE ===")

if __name__ == "__main__":
    run_sprint_2()
