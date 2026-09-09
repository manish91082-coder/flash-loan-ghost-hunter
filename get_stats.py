import sqlite3
import os

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def get_count(query):
    try:
        return c.execute(query).fetchone()[0]
    except Exception as e:
        return 0

chains = get_count('SELECT count(*) FROM chains')
ver_chains = get_count("SELECT count(*) FROM chains WHERE knowledge_status='VERIFIED'")
rpcs = get_count('SELECT count(*) FROM rpcs')
act_rpcs = get_count('SELECT count(*) FROM rpcs WHERE is_active=1')
dexs = get_count('SELECT count(*) FROM protocols')
pools = get_count('SELECT count(*) FROM pools')
tok_q = get_count('SELECT count(*) FROM token_resolution_queue')
tok_r = get_count("SELECT count(*) FROM tokens WHERE contract_address != 'UNKNOWN'")
flash = get_count('SELECT count(*) FROM flash_loan_providers')
market = get_count('SELECT count(*) FROM market_state')

print('--- DATA COUNTS ---')
print(f"Total Chains: {chains}")
print(f"Verified Chains: {ver_chains}")
print(f"Total RPCs: {rpcs}")
print(f"Active RPCs: {act_rpcs}")
print(f"Total DEXs (Protocols): {dexs}")
print(f"Total Pools: {pools}")
print(f"Tokens in Queue: {tok_q}")
print(f"Tokens Resolved: {tok_r}")
print(f"Flash Loan Providers: {flash}")
print(f"Market States: {market}")
