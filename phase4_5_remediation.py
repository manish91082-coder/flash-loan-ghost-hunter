import os
import json
import sqlite3
import urllib.request
import datetime

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')
now = datetime.datetime.utcnow().isoformat() + "Z"

def fetch_json_secure(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/1.1'})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode())

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure token resolution queue exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS token_resolution_queue (
        queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_symbol TEXT,
        chain_id INTEGER,
        status TEXT,
        queued_at TEXT
    )
''')
conn.commit()

print("Starting Phase 4 & 5 Remediation: Token and Pool Intelligence...")
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

# Fetch verified protocols and map by slug (since yields API uses slug)
# Protocol ID is slug-cid. We can just store protocol_id.
cursor.execute("SELECT protocol_id FROM protocols")
verified_protocols_ids = set(row[0] for row in cursor.fetchall())

pools_data = fetch_json_secure('https://yields.llama.fi/pools')
raw_pools = pools_data.get('data', [])

processed_tokens = set()
pool_count = 0
token_count = 0

for p in raw_pools:
    chain_name = str(p.get('chain', '')).lower()
    project_slug = str(p.get('project', '')).lower()
    
    if chain_name in llama_to_cid:
        cid = llama_to_cid[chain_name]
        dex_id = f"{project_slug}-{cid}"
        
        if dex_id in verified_protocols_ids:
            pool_id = p.get('pool')
            symbol = p.get('symbol', 'UNKNOWN')
            tvl = p.get('tvlUsd', 0)
            apy = p.get('apyBase', 0)
            
            cursor.execute('''
                INSERT OR IGNORE INTO pools (pool_id, dex_protocol_id, chain_id, pool_name, tvl, base_apy, knowledge_status, last_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pool_id, dex_id, cid, symbol, tvl, apy, 'OBSERVED', now))
            pool_count += 1
            
            tokens = symbol.split('-')
            for t in tokens:
                t_clean = t.strip()
                if not t_clean or len(t_clean) > 15: continue
                tok_id = f"{t_clean}-{cid}"
                if tok_id not in processed_tokens:
                    processed_tokens.add(tok_id)
                    token_count += 1
                    # FORENSIC FIX: Do NOT insert into tokens table if address is unknown.
                    # Send to resolution queue instead.
                    cursor.execute('''
                        INSERT OR IGNORE INTO token_resolution_queue (token_symbol, chain_id, status, queued_at)
                        VALUES (?, ?, ?, ?)
                    ''', (t_clean, cid, 'PENDING_RESOLUTION', now))
                    
conn.commit()
conn.close()

out_md = f"""# Phase 4 & 5 Remediation Results
**Timestamp:** {now}

## Token Intelligence (Phase 4)
- **Unique Tokens Queued for Resolution:** {token_count}
- **Status:** PENDING_RESOLUTION. Identity defect fixed; unknown addresses are no longer falsely persisted as canonical tokens.

## Pool & Liquidity Intelligence (Phase 5)
- **Global Pools Mapped:** {pool_count}
- **Data Source:** `yields.llama.fi/pools`
- **Status:** COMPLETED. Secure TLS used, entity matching bug fixed.
"""
with open(os.path.join(base, 'phase4_5_remediation_results.md'), 'w', encoding='utf-8') as f:
    f.write(out_md)

with open(os.path.join(base, 'execution_report.md'), 'a', encoding='utf-8') as f:
    f.write(f"\\n## Report 18: Phase 4 & 5 Remediation\\n")
    f.write(f"**Task:** Securely fetch pools and strictly enforce Token Identity.\\n")
    f.write(f"**Result:** Added {pool_count} Pools. Queued {token_count} Tokens for resolution.\\n")

print(f"Phase 4 & 5 Remediation Complete. Mapped {pool_count} Pools. Queued {token_count} tokens.")
