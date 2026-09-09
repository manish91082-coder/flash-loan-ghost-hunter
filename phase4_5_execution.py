import os
import json
import sqlite3
import urllib.request
import datetime
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')
now = datetime.datetime.utcnow().isoformat() + "Z"

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/1.0'})
    with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
        return json.loads(response.read().decode())

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Init new tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        token_id TEXT PRIMARY KEY,
        symbol TEXT,
        chain_id INTEGER,
        contract_address TEXT,
        knowledge_status TEXT,
        last_verified TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pools (
        pool_id TEXT PRIMARY KEY,
        dex_protocol_id TEXT,
        chain_id INTEGER,
        pool_name TEXT,
        tvl REAL,
        base_apy REAL,
        knowledge_status TEXT,
        last_verified TEXT
    )
''')
conn.commit()

print("Starting Phase 4 & 5: Token and Pool Intelligence...")
cursor.execute("SELECT chain_id, name FROM chains WHERE knowledge_status='VERIFIED'")
verified_chains = {row[1].lower(): row[0] for row in cursor.fetchall()}
# Aliases
verified_chains['bsc'] = 56
verified_chains['polygon'] = 137
verified_chains['arbitrum'] = 42161
verified_chains['optimism'] = 10
verified_chains['avalanche'] = 43114

cursor.execute("SELECT protocol_id, name FROM protocols")
verified_protocols = {row[1].lower(): row[0] for row in cursor.fetchall()}

# Fetch DeFiLlama Yields API for pool data
pools_data = fetch_json('https://yields.llama.fi/pools')
raw_pools = pools_data.get('data', [])

processed_tokens = set()
pool_count = 0
token_count = 0

for p in raw_pools:
    chain_name = str(p.get('chain', '')).lower()
    project_name = str(p.get('project', '')).lower()
    
    if chain_name in verified_chains and project_name in verified_protocols:
        cid = verified_chains[chain_name]
        dex_id = verified_protocols[project_name]
        pool_id = p.get('pool')
        symbol = p.get('symbol', 'UNKNOWN')
        tvl = p.get('tvlUsd', 0)
        apy = p.get('apyBase', 0)
        
        # Insert Pool
        cursor.execute('''
            INSERT OR IGNORE INTO pools (pool_id, dex_protocol_id, chain_id, pool_name, tvl, base_apy, knowledge_status, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pool_id, dex_id, cid, symbol, tvl, apy, 'OBSERVED', now))
        pool_count += 1
        
        # Parse Tokens (e.g., "USDC-USDT" -> ["USDC", "USDT"])
        tokens = symbol.split('-')
        for t in tokens:
            t_clean = t.strip()
            if not t_clean or len(t_clean) > 15: continue
            tok_id = f"{t_clean}-{cid}"
            if tok_id not in processed_tokens:
                processed_tokens.add(tok_id)
                token_count += 1
                cursor.execute('''
                    INSERT OR IGNORE INTO tokens (token_id, symbol, chain_id, contract_address, knowledge_status, last_verified)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (tok_id, t_clean, cid, 'UNKNOWN', 'OBSERVED', now))
                
conn.commit()
conn.close()

# Generate Outputs
out_md = f"""# Phase 4 & 5 Execution Results
**Timestamp:** {now}

## Token Intelligence (Phase 4)
- **Unique Tokens Discovered:** {token_count}
- **Status:** OBSERVED (Pending Smart Contract address verification in Phase 7).

## Pool & Liquidity Intelligence (Phase 5)
- **Global Pools Mapped:** {pool_count}
- **Data Source:** `yields.llama.fi/pools` -> Mapped to internal verified DEXs and Chains.

*All data successfully canonicalized into `phantomx_knowledge.db`.*
"""
with open(os.path.join(base, 'phase4_5_results.md'), 'w', encoding='utf-8') as f:
    f.write(out_md)

# Append to Project Log and State
with open(os.path.join(base, 'execution_report.md'), 'a', encoding='utf-8') as f:
    f.write(f"\\n## Report 11: Phase 4 & Phase 5 Autonomous Execution\\n")
    f.write(f"**Timestamp:** {now}\\n")
    f.write(f"**Task:** Discovered liquidity pools and token pairs across verified DEXs.\\n")
    f.write(f"**Result:** Added {pool_count} Pools and {token_count} Tokens to SQLite DB.\\n")
    f.write(f"**Status:** COMPLETED (Status: OBSERVED)\\n")

with open(os.path.join(base, 'project_log.md'), 'a', encoding='utf-8') as f:
    f.write(f"- **[{now}]** Executed Phase 4 (Token) and Phase 5 (Pool Intelligence). Mapped {pool_count} pools.\\n")

with open(os.path.join(base, 'project_state.md'), 'a', encoding='utf-8') as f:
    f.write(f"\\n### State Post-Phase 5 ({now})\\n")
    f.write(f"**Current Phase:** Phase 5 (Completed)\\n")
    f.write(f"**Next Phase:** Phase 6 (Flash-Loan Intelligence)\\n")

print("Phase 4 & 5 Execution Complete.")
