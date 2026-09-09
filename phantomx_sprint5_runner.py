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

# For Cross-Chain we compare L2s against Ethereum L1
L1_CHAIN_ID = 1
L2_CHAINS = [10, 8453, 42161, 137]

# Standardize on ETH/USDC
WETH_ADDRS = {
    1: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    10: "0x4200000000000000000000000000000000000006",
    8453: "0x4200000000000000000000000000000000000006",
    42161: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    137: "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"
}

USDC_ADDRS = {
    1: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    10: "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
    8453: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    42161: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    137: "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
}

class LiveFlashProvider:
    def __init__(self, fee_bips=5):
        self.fee_bips = fee_bips
        
    def calculate_premium(self, amt):
        return amt * self.fee_bips // 10000

def run_sprint_5():
    print("=== STARTING SPRINT 5: CROSS-CHAIN ARBITRAGE ===")
    config_data = load_chain_config()
    report_file = os.path.join("PhantomX_Massive_Test_Reports", "Sprint_5_Cross_Chain.csv")
    
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "L1 Chain", "L2 Chain", "Pair", "Strategy", "L1 Price", "L2 Price", "Price Gap", "Bridge Delay (Mins)", "Bridge Fees (USD)", "Net Exact Profit"])
        
        l1_config = config_data.get(str(L1_CHAIN_ID))
        if not l1_config:
            print("L1 Config missing")
            return
            
        rpc_manager_l1 = RPCFallbackManager(l1_config.get("rpc_urls", []), L1_CHAIN_ID)
        adapter_l1 = QuoteAdapterFactory.get_adapter('v3', rpc_manager_l1)
        
        quoter_l1 = l1_config.get("dexes", {}).get("uniswap_v3", {}).get("quoter")
        borrow_amount = 1000 * 10**6 # 1000 USDC
        
        # Get L1 Price
        try:
            state_l1 = adapter_l1.fetch_market_state(quoter_l1, USDC_ADDRS[1], WETH_ADDRS[1], borrow_amount, 500)
            l1_output_eth = adapter_l1.calculate_out_given_in(state_l1, borrow_amount)
        except Exception as e:
            print(f"[Scout L1 Failed] {e}")
            l1_output_eth = 0
            
        profit_calc = ProfitCalculator(LiveFlashProvider())
        
        for l2_id in L2_CHAINS:
            l2_config = config_data.get(str(l2_id))
            chain_name = l2_config.get("name", str(l2_id))
            print(f"\n[Scout] Inspecting Cross-Chain Arbitrage on L1 -> {chain_name} ({l2_id})")
            
            rpc_manager_l2 = RPCFallbackManager(l2_config.get("rpc_urls", []), l2_id)
            adapter_l2 = QuoteAdapterFactory.get_adapter('v3', rpc_manager_l2)
            quoter_l2 = l2_config.get("dexes", {}).get("uniswap_v3", {}).get("quoter")
            
            try:
                state_l2 = adapter_l2.fetch_market_state(quoter_l2, USDC_ADDRS[l2_id], WETH_ADDRS[l2_id], borrow_amount, 500)
                l2_output_eth = adapter_l2.calculate_out_given_in(state_l2, borrow_amount)
                
                # Gap is diff between what 1000 USDC gets you on L1 vs L2
                price_gap = l2_output_eth - l1_output_eth
                
                # Instead of simulated $15, we must fetch actual bridge economics.
                # If unverified, we set to NULL and fail.
                # In a real setup, we would call across-api or stargate.
                bridge_fees_usd = None 
                delay_mins = None
                
                if bridge_fees_usd is None:
                    raise ValueError("BRIDGE_DATA_MISSING")
                # We calculate if this is profitable
                gross_profit_usd = (price_gap / 10**18) * 3000 # Assume ETH $3000
                
                print(f"  -> Tested L1 -> {chain_name}: Gap {price_gap} Wei, Net Profit (USD) {gross_profit_usd - bridge_fees_usd}")
                writer.writerow([
                    datetime.now().isoformat(),
                    "Ethereum",
                    chain_name,
                    "USDC/WETH",
                    "Cross-Chain",
                    l1_output_eth,
                    l2_output_eth,
                    price_gap,
                    delay_mins,
                    bridge_fees_usd,
                    gross_profit_usd - bridge_fees_usd
                ])
                
            except Exception as e:
                print(f"  -> [Execution Engine Failed] {e}")
                writer.writerow([
                    datetime.now().isoformat(),
                    "Ethereum",
                    chain_name,
                    "USDC/WETH",
                    "Cross-Chain",
                    l1_output_eth,
                    0,
                    0,
                    0,
                    0,
                    0
                ])
                
            time.sleep(2)
            
    print("\n=== SPRINT 5 COMPLETE ===")

if __name__ == "__main__":
    run_sprint_5()
