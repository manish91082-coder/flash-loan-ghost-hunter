import sqlite3
import json
from web3 import Web3
import concurrent.futures

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

# Standard Uniswap V2 Pair ABI for getReserves()
PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]')

# A known active Uniswap V2 pool on Ethereum (USDC/WETH) to test
TEST_POOL = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"

def test_rpc(url):
    try:
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 2}))
        if not w3.is_connected():
            return None
        contract = w3.eth.contract(address=w3.to_checksum_address(TEST_POOL), abi=PAIR_ABI)
        reserves = contract.functions.getReserves().call()
        if reserves and len(reserves) == 3:
            return url
    except Exception:
        return None
    return None

def find_working_rpcs():
    print("=== PHANTOMX INTELLIGENT RPC ROUTER ===")
    print("Testing internal RPC list to find ultra-fast, unrestricted nodes...")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT rpc_url FROM rpc_endpoints WHERE chain_id = 1")
        rows = c.fetchall()
        rpc_urls = [row[0] for row in rows]
    except sqlite3.OperationalError:
        rpc_urls = []
    finally:
        conn.close()
    
    # If the DB is empty or missing Ethereum RPCs, we use a fallback list of 20 top public RPCs
    if not rpc_urls:
        rpc_urls = [
            "https://eth.llamarpc.com", "https://rpc.ankr.com/eth", "https://1rpc.io/eth",
            "https://cloudflare-eth.com", "https://ethereum-rpc.publicnode.com",
            "https://eth.rpc.blxrbdn.com", "https://rpc.mevblocker.io", "https://eth.drpc.org",
            "https://rpc.builder0x69.com", "https://rpc.payload.de", "https://api.securerpc.com/v1",
            "https://eth-mainnet.public.blastapi.io", "https://rpc.flashbots.net",
            "https://eth.api.onfinality.io/public", "https://mainnet.gateway.tenderly.co"
        ]
        
    print(f"Loaded {len(rpc_urls)} RPCs for testing.")
    
    working_rpcs = []
    # Test concurrently to save time
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(test_rpc, rpc_urls)
        for res in results:
            if res:
                working_rpcs.append(res)
                print(f"[SUCCESS] Valid RPC Found: {res}")
                if len(working_rpcs) >= 3: # Stop after finding a few good ones
                    break
                    
    if working_rpcs:
        print(f"\n[ROUTER ACTIVE] Selected Primary RPC: {working_rpcs[0]}")
        with open("active_rpc.txt", "w") as f:
            f.write(working_rpcs[0])
    else:
        print("CRITICAL FAILURE: No working RPCs found in the list.")

if __name__ == '__main__':
    find_working_rpcs()
