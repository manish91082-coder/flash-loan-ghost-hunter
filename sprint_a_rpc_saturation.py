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
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def saturate_rpcs():
    print("--- PHANTOMX EXTREME SATURATION: SPRINT A (RPCs) ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    chain_data = fetch_json_secure('https://chainid.network/chains.json')
    if not chain_data:
        print("Failed to pull chainid network.")
        return
        
    total_inserted = 0
    
    for chain in chain_data:
        cid = chain.get('chainId')
        rpcs = chain.get('rpc', [])
        
        for rpc_url in rpcs:
            # Clean RPCs to remove variables like ${INFURA_API_KEY}
            if "${" in rpc_url or "API_KEY" in rpc_url:
                continue
                
            cursor.execute('''
                INSERT OR IGNORE INTO rpcs (chain_id, url, latency_ms, is_active, last_verified)
                VALUES (?, ?, ?, ?, ?)
            ''', (cid, rpc_url, 0, 0, now))
            
            # 1 row inserted if new
            if cursor.rowcount > 0:
                total_inserted += 1
                
    conn.commit()
    conn.close()
    
    print(f"RPC Saturation Complete. Inserted {total_inserted} new RPC endpoints into the global graph.")
    
if __name__ == "__main__":
    saturate_rpcs()
