import sqlite3

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
conn = sqlite3.connect(base + '\\phantomx_knowledge.db')
cursor = conn.cursor()
cursor.execute("SELECT chain_id, name FROM chains WHERE knowledge_status='VERIFIED'")
db_chains = cursor.fetchall()

alias_map = {
    'ethereum mainnet': 'ethereum',
    'binance smart chain mainnet': 'bsc',
    'polygon pos': 'polygon',
    'avalanche c-chain': 'avalanche',
    'op mainnet': 'optimism',
    'arbitrum one': 'arbitrum',
    'gnosis chain': 'xdai',
    'fantom opera': 'fantom',
    'base': 'base',
    'zksync era mainnet': 'zksync era',
    'linea mainnet': 'linea'
}
llama_to_cid = {}
for cid, db_name in db_chains:
    db_name_lower = str(db_name).lower()
    llama_slug = alias_map.get(db_name_lower, db_name_lower)
    llama_to_cid[llama_slug] = cid

print(f"Mapped {len(llama_to_cid)} chains to Llama slugs.")
print(f"Sample: {list(llama_to_cid.keys())[:5]}")
import urllib.request
import json
def fetch_json_secure(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/1.1 (Security Remediated)'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None

data = fetch_json_secure('https://api.llama.fi/protocols')
print(f"Llama Data Length: {len(data) if data else 0}")
print(set(p.get('category') for p in data))
