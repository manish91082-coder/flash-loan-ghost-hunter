import sqlite3
import pandas as pd
import os

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
conn = sqlite3.connect(db_path)

# Extract Data
df_chains = pd.read_sql_query("SELECT * FROM chains WHERE knowledge_status='VERIFIED'", conn)
df_rpcs = pd.read_sql_query("SELECT * FROM rpcs", conn)
df_dexs = pd.read_sql_query("SELECT * FROM protocols", conn)
df_pools = pd.read_sql_query("SELECT * FROM pools", conn)
df_tokens = pd.read_sql_query("SELECT * FROM tokens WHERE contract_address != 'UNKNOWN'", conn)
df_flash = pd.read_sql_query("SELECT * FROM flash_loan_providers", conn)

# Basic tabular representation string
report = f"""
===================================================
PHANTOMX OFFLINE EXECUTION - RAW TABULAR REPORT
===================================================

1. VERIFIED CHAINS (Sample of {len(df_chains)} total):
{df_chains.head(10).to_string()}

2. ACTIVE RPCs (Sample of {len(df_rpcs)} total):
{df_rpcs.head(10).to_string()}

3. MAPPED DEXs / PROTOCOLS (Sample of {len(df_dexs)} total):
{df_dexs[['protocol_id', 'name', 'chain_id']].head(10).to_string()}

4. LIQUIDITY POOLS (Sample of {len(df_pools)} total):
{df_pools[['pool_id', 'dex_protocol_id', 'pool_name', 'tvl']].head(10).to_string()}

5. RESOLVED TOKENS (Sample of {len(df_tokens)} total):
{df_tokens[['token_id', 'symbol', 'chain_id', 'contract_address']].head(10).to_string()}

6. FLASH LOAN PROVIDERS (Sample of {len(df_flash)} total):
{df_flash[['provider_id', 'name', 'chain_id', 'fee_bps']].head(10).to_string()}

"""

with open(r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\tabular_dump.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("Tabular dump written to tabular_dump.txt")
