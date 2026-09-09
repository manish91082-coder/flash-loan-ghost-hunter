import json
import urllib.request
import sqlite3

# This is the stateless Cloudflare / AWS Lambda handler format.
# When deployed, it acts as the distributed compute layer.

class ServerlessDataStore:
    def __init__(self, env):
        self.env = env
        # Mocking connection for local test. 
        # In prod, this uses Cloudflare D1 HTTP bindings.
        self.conn = sqlite3.connect('phantomx_knowledge.db')
        self.cursor = self.conn.cursor()
        
    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()
        
    def execute(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()

def fetch_json_secure(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/Serverless'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except:
        return None

def phantomx_sync_handler(event, context):
    print("Executing Stateless Sync Worker...")
    db = ServerlessDataStore(context.get('env', 'local'))
    
    # Example Serverless Execution Task: Fetch Live Prices
    weth_price_url = "https://api.dexscreener.com/latest/dex/search?q=WETH"
    data = fetch_json_secure(weth_price_url)
    
    if data and 'pairs' in data:
        pairs = data['pairs']
        print(f"Serverless Edge node fetched {len(pairs)} pairs.")
        # Store in abstracted db
        for p in pairs:
            db.execute('''
                INSERT OR REPLACE INTO market_state (pair_address, base_token, quote_token, price_usd, liquidity_usd, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (p.get('pairAddress'), 'WETH', p.get('quoteToken', {}).get('symbol'), p.get('priceUsd'), p.get('liquidity', {}).get('usd', 0), 'NOW'))
            
    return {"status": "SYNC_COMPLETE", "pairs_processed": len(data['pairs']) if data else 0}

# Mock entrypoint for local testing of serverless handler
if __name__ == "__main__":
    event = {}
    context = {'env': 'local'}
    result = phantomx_sync_handler(event, context)
    print("Handler Result:", result)
