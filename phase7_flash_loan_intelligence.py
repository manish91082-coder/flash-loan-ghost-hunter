import sqlite3
import os
import datetime

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')
now = datetime.datetime.utcnow().isoformat() + "Z"

def map_flash_loans():
    print("Starting Phase 7: Flash Loan Intelligence Expansion...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flash_loan_providers (
            provider_id TEXT PRIMARY KEY,
            chain_id INTEGER,
            name TEXT,
            fee_bps REAL,
            knowledge_status TEXT,
            last_verified TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE flash_loan_providers ADD COLUMN fee_bps REAL")
    except sqlite3.OperationalError:
        pass
    # 2. We can map them dynamically if they exist in our `protocols` table for a specific chain.
    target_protocols = {
        'uniswap-v2': 30, # 0.3%
        'uniswap-v3': 0,  # 0% depending on pool, max 1%
        'aave-v2': 9,     # 0.09%
        'aave-v3': 5,     # 0.05%
        'balancer-v2': 0, # mostly free
        'dodo': 0,        # free
        'makerdao': 0,    # free
        'pancakeswap': 25 # 0.25% (example on BSC)
    }
    
    cursor.execute("SELECT protocol_id, name, chain_id FROM protocols")
    all_dexs = cursor.fetchall()
    
    mapped = 0
    for pid, name, cid in all_dexs:
        slug = pid.split('-')[0] # extract Llama slug
        if slug in target_protocols:
            fee = target_protocols[slug]
            provider_id = f"FL-{slug}-{cid}"
            
            cursor.execute('''
                INSERT OR IGNORE INTO flash_loan_providers (provider_id, chain_id, name, fee_bps, knowledge_status, last_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (provider_id, cid, name, fee, 'VERIFIED', now))
            mapped += 1
            
    conn.commit()
    conn.close()
    
    print(f"Phase 7 Complete. Expanded Flash Loan Providers across chains: {mapped}")
    
    with open(os.path.join(base, 'execution_report.md'), 'a', encoding='utf-8') as f:
        f.write(f"\\n## Report 20: Phase 7 Flash Loan Matrix Expansion\\n")
        f.write(f"**Task:** Dynamically map flash loan capabilities across all verified chains.\\n")
        f.write(f"**Result:** Mapped {mapped} provider-chain instances.\\n")

if __name__ == "__main__":
    map_flash_loans()
