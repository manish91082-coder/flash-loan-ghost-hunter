import os
import json
import sqlite3
from web3 import Web3
import concurrent.futures

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def get_rpc():
    try:
        with open("active_rpc.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return "https://ethereum-rpc.publicnode.com"

RPC_URL = get_rpc()
w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 10}))

# We need the ABI for the router to find out the output amounts
ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]')

def check_route(w3_conn, routerA, routerB, tokenIn, tokenOut, amount_in):
    try:
        contractA = w3_conn.eth.contract(address=w3_conn.to_checksum_address(routerA), abi=ROUTER_ABI)
        contractB = w3_conn.eth.contract(address=w3_conn.to_checksum_address(routerB), abi=ROUTER_ABI)
        
        path_forward = [w3_conn.to_checksum_address(tokenIn), w3_conn.to_checksum_address(tokenOut)]
        path_backward = [w3_conn.to_checksum_address(tokenOut), w3_conn.to_checksum_address(tokenIn)]
        
        # Simulating the exact on-chain router logic instead of relying just on getReserves math
        outA = contractA.functions.getAmountsOut(amount_in, path_forward).call()
        outB = contractB.functions.getAmountsOut(outA[-1], path_backward).call()
        
        profit = outB[-1] - amount_in
        return profit
    except Exception as e:
        return -1 # Router reverted, insufficient liquidity or fee on transfer

def live_hunting_engine():
    print(f"--- PHANTOMX: LIVE BLOCKCHAIN RPC HUNTING ---")
    print(f"Connecting to: {RPC_URL}")
    if not w3.is_connected():
        print("CRITICAL: Cannot connect to blockchain RPC.")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # We grab known routers and pairs from our knowledge base
    # We'll specifically search for high-value tokens overlapping across Uniswap V2 forks
    c.execute("""
        SELECT p1.pool_name, p1.token_a_address, p1.token_b_address, pr1.router_address, pr2.router_address
        FROM pools p1
        JOIN pools p2 ON p1.pool_name = p2.pool_name AND p1.chain_id = p2.chain_id AND p1.pool_id != p2.pool_id
        JOIN protocols pr1 ON p1.dex_protocol_id = pr1.protocol_id
        JOIN protocols pr2 ON p2.dex_protocol_id = pr2.protocol_id
        WHERE p1.chain_id = 1 AND pr1.router_address IS NOT NULL AND pr2.router_address IS NOT NULL
          AND p1.token_a_address IS NOT NULL AND p1.token_b_address IS NOT NULL
        LIMIT 50
    """)
    pairs = c.fetchall()
    
    print(f"Testing {len(pairs)} cross-DEX routes on-chain...")
    
    # Let's say we flash loan 1 ETH (10**18 wei)
    amount_in = int(1 * 10**18)
    
    successful = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for pair in pairs:
            pool_name, tokenA, tokenB, routerA, routerB = pair
            # We test A -> B and B -> A
            futures.append(executor.submit(check_route, w3, routerA, routerB, tokenA, tokenB, amount_in))
            futures.append(executor.submit(check_route, w3, routerB, routerA, tokenA, tokenB, amount_in))
            
        for future in concurrent.futures.as_completed(futures):
            profit = future.result()
            if profit > 0:
                print(f"[OPPORTUNITY] 🟢 Found Profitable Route! Expected Net: {profit}")
                successful += 1
                
    print(f"Scan complete. Found {successful} executable opportunities on the live blockchain.")

if __name__ == '__main__':
    live_hunting_engine()
