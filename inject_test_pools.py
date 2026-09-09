import sqlite3
import datetime

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def get_utc_now():
    return datetime.datetime.utcnow().isoformat()

def inject_test_pools():
    print("--- INJECTING HIGH-CONFIDENCE TEST POOLS ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # We will ensure these pools exist with exact addresses
    # Format: (pool_name, dex_protocol_id, pool_address)
    test_pools = [
        # USDC-WETH
        ('USDC-WETH', 'uniswap-v2-1', '0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc'),
        ('USDC-WETH', 'sushiswap-1', '0x397ff1542f962076d0bfe58ea045ffa2d347aca0'),
        
        # WBTC-WETH
        ('WBTC-WETH', 'uniswap-v2-1', '0xbb2b8038a1640196fbe3e38816f3e67cba72d940'),
        ('WBTC-WETH', 'sushiswap-1', '0xceff51756c56ceffca006cd410b034c46fa1c092'),
        
        # DAI-WETH
        ('DAI-WETH', 'uniswap-v2-1', '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'),
        ('DAI-WETH', 'sushiswap-1', '0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f')
    ]
    
    for name, dex, addr in test_pools:
        # Check if pair exists in DB
        c.execute("SELECT pool_id FROM pools WHERE pool_name = ? AND dex_protocol_id = ? AND chain_id = 1", (name, dex))
        result = c.fetchone()
        
        if result:
            c.execute("UPDATE pools SET pool_address = ?, confidence = 'CONFIRMED', observed_at = ? WHERE pool_id = ?", 
                      (addr, get_utc_now(), result[0]))
        else:
            # Insert if missing
            pool_id = f"test-{dex}-{name}"
            c.execute("""
                INSERT INTO pools (pool_id, dex_protocol_id, chain_id, pool_name, pool_address, confidence, observed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pool_id, dex, 1, name, addr, 'CONFIRMED', get_utc_now()))
            
        print(f"Injected {name} on {dex} -> {addr}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    inject_test_pools()
