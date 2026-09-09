import sqlite3
import json
import urllib.request
import time
from datetime import datetime

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def get_utc_now():
    return datetime.utcnow().isoformat()

def resolve_major_infrastructure():
    print("--- RESOLVING MAJOR DEFI INFRASTRUCTURE (ROUTERS & FLASH LOANS) ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Hardcoded highly-verified major infrastructure (The Canonical Truth)
    # Format: (protocol_id, router_address, factory_address)
    major_dexs = [
        # Ethereum (Chain 1)
        ('uniswap-v2-1', '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'),
        ('uniswap-v3-1', '0xE592427A0AEce92De3Edee1F18E0157C05861564', '0x1F98431c8aD98523631AE4a59f267346ea31F984'),
        ('sushiswap-1', '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F', '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'),
        # Base (Chain 8453)
        ('uniswap-v3-8453', '0x2626664c2603336E57B271c5C0b26F421741e481', '0x33128a8fC17869897dcE68Ed026d694621f6FDfD'),
        ('uniswap-v2-8453', '0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24', '0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6'), # BaseSwap/Uniswap V2 fork
        ('aerodrome-v1-8453', '0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43', '0x420DD381b31aEf6683db6B902084cB0FFeCE40Da')
    ]
    
    for protocol_id, router, factory in major_dexs:
        c.execute("""
            UPDATE protocols 
            SET router_address = ?, factory_address = ?, confidence = 'CONFIRMED', observed_at = ?
            WHERE protocol_id = ?
        """, (router, factory, get_utc_now(), protocol_id))
        print(f"Resolved DEX {protocol_id} -> Router: {router}")
        
    major_fl = [
        # Ethereum Flash Loans
        ('FL-aave-v3-1', '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2', 'WETH,USDC,DAI,WBTC'),
        ('FL-balancer-v2-1', '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'WETH,USDC,DAI,WBTC'),
        # Base Flash Loans
        ('aave-v3-8453', '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5', 'WETH,USDC,cbBTC'),
        ('balancer-v2-8453', '0xBA12222222228d8Ba445958a75a0704d566BF2C8', 'WETH,USDC,cbBTC')
    ]
    
    for provider_id, contract, assets in major_fl:
        c.execute("""
            UPDATE flash_loan_providers 
            SET contract_address = ?, supported_assets = ?, confidence = 'CONFIRMED', observed_at = ?
            WHERE provider_id = ?
        """, (contract, assets, get_utc_now(), provider_id))
        print(f"Resolved Flash Loan Provider {provider_id} -> Contract: {contract}")

    conn.commit()
    conn.close()

def fetch_coingecko_tokens():
    print("\n--- RESOLVING TOKEN IDENTITIES VIA COINGECKO ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Fetch token metadata from CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/coins/list?include_platform=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        print(f"Fetched {len(data)} tokens from CoinGecko.")
        
        # We map standard CoinGecko platform names to our Chain IDs
        platform_to_chain = {
            'ethereum': 1,
            'binance-smart-chain': 56,
            'polygon-pos': 137,
            'arbitrum-one': 42161,
            'optimistic-ethereum': 10,
            'base': 8453,
            'avalanche': 43114,
            'solana': 0 # not evm
        }
        
        resolved_count = 0
        for token in data:
            symbol = token.get('symbol', '').upper()
            platforms = token.get('platforms', {})
            
            for platform, address in platforms.items():
                if not address:
                    continue
                chain_id = platform_to_chain.get(platform)
                if not chain_id:
                    continue
                    
                # Update token if it exists in our DB
                c.execute("""
                    UPDATE tokens 
                    SET contract_address = ?, confidence = 'CONFIRMED', observed_at = ?
                    WHERE symbol = ? AND chain_id = ? AND (contract_address IS NULL OR contract_address = 'Pending')
                """, (address, get_utc_now(), symbol, chain_id))
                
                if c.rowcount > 0:
                    resolved_count += c.rowcount
                    
        print(f"Successfully resolved addresses for {resolved_count} tokens in the DB.")
        
    except Exception as e:
        print(f"Error fetching tokens from CoinGecko: {e}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    resolve_major_infrastructure()
    fetch_coingecko_tokens()
