import sqlite3
import os
import json
import urllib.request
import datetime

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')

def fetch_json_secure(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'PhantomX/1.1'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except:
        return None

def run_audit():
    if not os.path.exists(db_path):
        return "ERROR: Database missing."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    report = []
    report.append("--- PHANTOMX MATHEMATICAL SATURATION AUDIT ---")
    
    # 1. Chains
    cursor.execute("SELECT count(*) FROM chains WHERE knowledge_status='VERIFIED'")
    verified_chains = cursor.fetchone()[0]
    # Llama claims ~300 chains
    chain_sat = min(100.0, (verified_chains / 300.0) * 100)
    report.append(f"[Chains] Verified: {verified_chains} | Saturation: {chain_sat:.2f}%")
    
    # 2. Protocols / DEXs
    cursor.execute("SELECT count(*) FROM protocols")
    mapped_dexs = cursor.fetchone()[0]
    # Llama has ~4000 protocols, ~1500 DEXs
    dex_sat = min(100.0, (mapped_dexs / 1500.0) * 100)
    report.append(f"[DEXs] Mapped: {mapped_dexs} | Saturation: {dex_sat:.2f}%")
    
    # 3. Pools
    cursor.execute("SELECT count(*) FROM pools")
    mapped_pools = cursor.fetchone()[0]
    # Llama yields has ~10000 pools
    pool_sat = min(100.0, (mapped_pools / 10000.0) * 100)
    report.append(f"[Pools] Mapped: {mapped_pools} | Saturation: {pool_sat:.2f}%")
    
    # 4. Token Identity
    cursor.execute("SELECT count(*) FROM token_resolution_queue WHERE status='PENDING_RESOLUTION'")
    pending_tokens = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM tokens WHERE contract_address != 'UNKNOWN'")
    resolved_tokens = cursor.fetchone()[0]
    total_tokens = pending_tokens + resolved_tokens
    token_sat = 0.0 if total_tokens == 0 else (resolved_tokens / total_tokens) * 100
    report.append(f"[Tokens] Pending: {pending_tokens} | Resolved: {resolved_tokens} | Saturation: {token_sat:.2f}%")
    
    # 5. Flash Loan Providers
    cursor.execute("SELECT count(*) FROM flash_loan_providers")
    try:
        flash_providers = cursor.fetchone()[0]
    except:
        flash_providers = 0
    # At least ~5 major flash providers across top 20 chains = ~100 mappings
    flash_sat = min(100.0, (flash_providers / 100.0) * 100)
    report.append(f"[Flash Loans] Mapped: {flash_providers} | Saturation: {flash_sat:.2f}%")
    
    # Global Saturation
    global_sat = (chain_sat + dex_sat + pool_sat + token_sat + flash_sat) / 5
    report.append("----------------------------------------------")
    report.append(f"GLOBAL SATURATION SCORE: {global_sat:.2f}%")
    
    if global_sat >= 99.0:
        report.append("STATUS: SATURATED. READY FOR LIVE DEPLOYMENT.")
    else:
        report.append("STATUS: INTELLIGENCE GAPS DETECTED. CONTINUE HUNTING.")
        
    conn.close()
    
    full_report = "\\n".join(report)
    print(full_report)
    
    with open(os.path.join(base, 'saturation_report.md'), 'w', encoding='utf-8') as f:
        f.write("```text\\n" + full_report + "\\n```")

if __name__ == "__main__":
    run_audit()
