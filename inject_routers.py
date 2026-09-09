import sqlite3
import datetime

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def get_utc_now():
    return datetime.datetime.utcnow().isoformat()

def update_routers():
    print("--- INJECTING ROUTER ADDRESSES ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # We need to make sure the protocols have router addresses so the live_onchain_hunter can use them
    # Uniswap V2 Router
    c.execute("UPDATE protocols SET router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D' WHERE protocol_id = 'uniswap-v2-1'")
    # SushiSwap Router
    c.execute("UPDATE protocols SET router_address = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F' WHERE protocol_id = 'sushiswap-1'")
    
    # Also ensure test pools have token_a and token_b addresses set
    # USDC
    usdc = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
    # WETH
    weth = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    # WBTC
    wbtc = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'
    # DAI
    dai = '0x6b175474e89094c44da98b954eedeac495271d0f'
    
    # USDC-WETH
    c.execute("UPDATE pools SET token_a_address = ?, token_b_address = ? WHERE pool_name = 'USDC-WETH'", (usdc, weth))
    # WBTC-WETH
    c.execute("UPDATE pools SET token_a_address = ?, token_b_address = ? WHERE pool_name = 'WBTC-WETH'", (wbtc, weth))
    # DAI-WETH
    c.execute("UPDATE pools SET token_a_address = ?, token_b_address = ? WHERE pool_name = 'DAI-WETH'", (dai, weth))
    
    conn.commit()
    conn.close()
    print("Routers and tokens updated successfully.")

if __name__ == '__main__':
    update_routers()
