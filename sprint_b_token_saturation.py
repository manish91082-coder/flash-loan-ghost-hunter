import sqlite3
import os
import json
import urllib.request
import datetime

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')
now = datetime.datetime.utcnow().isoformat() + "Z"

def fetch_json_secure(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/ExtremeSaturation'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def saturate_tokens():
    print("--- PHANTOMX EXTREME SATURATION: SPRINT B (Tokens) ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check pending tokens
    cursor.execute("SELECT queue_id, token_symbol, chain_id FROM token_resolution_queue WHERE status='PENDING_RESOLUTION'")
    pending = cursor.fetchall()
    
    if not pending:
        print("No tokens pending. Saturation is 100%.")
        return
        
    print(f"Hunting {len(pending)} pending tokens across global registries...")
    
    # Build a massive multi-repo token dictionary
    global_dict = {}
    
    sources = [
        # SushiSwap Default List
        "https://token-list.sushi.com",
        # TrustWallet Assets (Usually structured differently, but some mirrors exist)
        # We will use public community lists for maximum coverage
        "https://tokens.coingecko.com/uniswap/all.json",
        "https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/tokenlist.json",
        "https://raw.githubusercontent.com/pangolindex/tokenlists/main/pangolin.tokenlist.json" # Avalanche
    ]
    
    for url in sources:
        print(f"Scraping {url}...")
        data = fetch_json_secure(url)
        if data and 'tokens' in data:
            for t in data['tokens']:
                sym = str(t.get('symbol')).lower()
                cid = t.get('chainId')
                addr = t.get('address')
                if sym not in global_dict:
                    global_dict[sym] = {}
                # Prioritize the first address found for a given chain
                if cid not in global_dict[sym]:
                    global_dict[sym][cid] = addr
                    
    resolved_count = 0
    
    for queue_id, symbol, cid in pending:
        sym_lower = symbol.lower()
        contract_addr = None
        
        # Exact match
        if sym_lower in global_dict and cid in global_dict[sym_lower]:
            contract_addr = global_dict[sym_lower][cid]
            
        if contract_addr:
            tok_id = f"{symbol}-{cid}"
            cursor.execute('''
                INSERT OR IGNORE INTO tokens (token_id, symbol, chain_id, contract_address, knowledge_status, last_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tok_id, symbol, cid, contract_addr, 'VERIFIED', now))
            
            cursor.execute("UPDATE token_resolution_queue SET status='RESOLVED' WHERE queue_id=?", (queue_id,))
            resolved_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"Sprint B Token Saturation Complete. Resolved {resolved_count} out of {len(pending)} tokens.")
    
if __name__ == "__main__":
    saturate_tokens()
