import sqlite3
import pandas as pd
import os

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
conn = sqlite3.connect(db_path)

df_chains = pd.read_sql_query("SELECT chain_id, name, is_defi_active, tvl FROM chains WHERE knowledge_status='VERIFIED'", conn)
df_rpcs = pd.read_sql_query("SELECT rpc_id, chain_id, url, latency_ms FROM rpcs", conn)
df_dexs = pd.read_sql_query("SELECT protocol_id, name, chain_id FROM protocols", conn)
df_pools = pd.read_sql_query("SELECT pool_id, dex_protocol_id, pool_name, tvl FROM pools", conn)
df_tokens = pd.read_sql_query("SELECT token_id, symbol, chain_id, contract_address FROM tokens", conn)
df_flash = pd.read_sql_query("SELECT provider_id, name, chain_id, fee_bps FROM flash_loan_providers", conn)

with open(r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\detailed_tabular.txt', 'w', encoding='utf-8') as f:
    f.write("--- PHANTOMX OFFLINE DATABASE DUMP ---\n\n")
    
    f.write(f"1. VERIFIED CHAINS ({len(df_chains)} Total)\n")
    f.write(df_chains.to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
    
    f.write(f"2. ACTIVE RPCS ({len(df_rpcs)} Total)\n")
    f.write(df_rpcs.to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
    
    f.write(f"3. MAPPED DEXS/PROTOCOLS (First 200 of {len(df_dexs)} Total)\n")
    f.write(df_dexs.head(200).to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
    
    f.write(f"4. LIQUIDITY POOLS (First 200 of {len(df_pools)} Total)\n")
    f.write(df_pools.head(200).to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
    
    f.write(f"5. RESOLVED TOKENS ({len(df_tokens)} Total)\n")
    f.write(df_tokens.to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
    
    f.write(f"6. FLASH LOAN PROVIDERS ({len(df_flash)} Total)\n")
    f.write(df_flash.to_string(index=False))
    f.write("\n\n------------------------------------------------\n\n")
