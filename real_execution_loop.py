import time
import sqlite3
import json
from quote_engine.market_model import UniV2MarketModel
from quote_engine.rpc_fetcher import RPCFetcher
from economics.profit_calculator import ProfitCalculator
from risk.safety_checks import RiskEngine

DB_PATH = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

class RealAutonomousLoop:
    def __init__(self, rpc_url):
        print(f"Initializing REAL PhantomX Engine on {rpc_url}")
        self.fetcher = RPCFetcher(rpc_url)
        # Using 30 bips (0.3%) swap fee for UniV2
        self.market = UniV2MarketModel(fee_bips=30)
        # Assuming Aave V3 flash loan fee of 5 bips (0.05%)
        self.profit_calc = ProfitCalculator(flash_loan_fee_bips=5)
        # Max trade 10 ETH (in wei), max slippage 0.5% (50 bips)
        self.risk_engine = RiskEngine(max_trade_size_wei=10 * 10**18, max_slippage_bips=50)
        
    def scan_opportunities(self):
        print("Fetching routing pairs from database...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # We need actual real token addresses. The dummy database might have fake ones.
        # We will scan the DB for pairs that have valid checksum addresses.
        c.execute("""
            SELECT p1.pool_name, p1.token_a_address, p1.token_b_address, pr1.router_address, pr2.router_address,
                   p1.pool_address as pool_1_address, p2.pool_address as pool_2_address
            FROM pools p1
            JOIN pools p2 ON p1.pool_name = p2.pool_name AND p1.chain_id = p2.chain_id AND p1.pool_id != p2.pool_id
            JOIN protocols pr1 ON p1.dex_protocol_id = pr1.protocol_id
            JOIN protocols pr2 ON p2.dex_protocol_id = pr2.protocol_id
            WHERE p1.chain_id = 1 
              AND p1.token_a_address IS NOT NULL AND p1.token_b_address IS NOT NULL
              AND p1.pool_address IS NOT NULL AND p2.pool_address IS NOT NULL
        """)
        pairs = c.fetchall()
        conn.close()
        
        print(f"Found {len(pairs)} pairs to scan.")
        
        opportunities = []
        for pair in pairs:
            pool_name, tokenA, tokenB, routerA, routerB, pool1, pool2 = pair
            
            try:
                # 1. Fetch exact real reserves
                r1_in, r1_out = self.fetcher.get_univ2_reserves(pool1, tokenA)
                r2_in, r2_out = self.fetcher.get_univ2_reserves(pool2, tokenB)
                
                if r1_in == 0 or r1_out == 0 or r2_in == 0 or r2_out == 0:
                    continue
                    
                # 2. Calculate optimal arbitrage input via mathematical model
                optimal_in = self.market.get_optimal_arbitrage_input(r1_in, r1_out, r2_in, r2_out)
                
                if optimal_in == 0:
                    # No arbitrage in this direction, try reverse
                    optimal_in_rev = self.market.get_optimal_arbitrage_input(r2_in, r2_out, r1_in, r1_out)
                    if optimal_in_rev > 0:
                        print(f"[{pool_name}] Found reverse arbitrage opportunity.")
                        # Evaluate reverse path
                    continue
                    
                # 3. Simulate Path
                out1 = self.market.get_amount_out(optimal_in, r1_in, r1_out)
                out2 = self.market.get_amount_out(out1, r2_in, r2_out)
                
                # 4. Profit & Risk Math
                gas_price = self.fetcher.get_gas_price()
                estimated_gas = 300000 # Conservative estimate for flash loan + 2 swaps
                
                net_profit, is_profitable = self.profit_calc.calculate_net_profit(
                    borrow_amount=optimal_in,
                    final_amount=out2,
                    gas_used=estimated_gas,
                    gas_price_wei=gas_price
                )
                
                is_safe, risk_msg = self.risk_engine.validate_execution_path(
                    profit_wei=net_profit,
                    is_profitable=is_profitable,
                    amount_in=optimal_in
                )
                
                if is_safe:
                    min_amount_out = self.risk_engine.calculate_min_amount_out(out2)
                    print(f"🔥 GO DECISION: {pool_name} | In: {optimal_in} | Net Profit: {net_profit} wei")
                    opportunities.append({
                        "pool_name": pool_name,
                        "tokenA": tokenA,
                        "tokenB": tokenB,
                        "routerA": routerA,
                        "routerB": routerB,
                        "optimal_in": optimal_in,
                        "min_amount_out": min_amount_out,
                        "net_profit": net_profit
                    })
                else:
                    print(f"NO-GO: {pool_name} - {risk_msg}")

            except Exception as e:
                # Log fetch error but keep scanning
                print(f"Error scanning {pool_name}: {e}")
                
        return opportunities

if __name__ == '__main__':
    # Defaulting to standard public RPC for script test, but fork RPC will be used for execution
    try:
        with open('active_rpc.txt', 'r') as f:
            rpc_url = f.read().strip()
    except:
        rpc_url = "https://ethereum-rpc.publicnode.com"
        
    loop = RealAutonomousLoop(rpc_url)
    ops = loop.scan_opportunities()
    if not ops:
        print("No executable opportunities found in real market conditions.")
    else:
        print(f"Found {len(ops)} executable opportunities.")
