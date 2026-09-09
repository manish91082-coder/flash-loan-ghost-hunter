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
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def resolve_tokens():
    print("Starting Phase 6: Global Token Identity Resolution...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch pending tokens
    cursor.execute("SELECT queue_id, token_symbol, chain_id FROM token_resolution_queue WHERE status='PENDING_RESOLUTION'")
    pending = cursor.fetchall()
    
    if not pending:
        print("No tokens pending resolution.")
        return
        
    print(f"Found {len(pending)} tokens in resolution queue.")
    
    # ZERO-COST GLOBAL TOKEN LISTS (Aggregated)
    # 1inch Token List (Mainly Ethereum, but massive)
    # Sushiswap / Uniswap defaults
    # For zero cost and massive coverage, we pull static token lists.
    
    # 1. 1inch Extended List
    oneinch_url = "https://tokens.1inch.eth.link"
    print(f"Fetching global token dictionary from {oneinch_url}...")
    oneinch_data = fetch_json_secure(oneinch_url)
    
    # Map Symbol (lowercase) -> { chain_id: contract_address }
    token_dict = {}
    
    if oneinch_data and 'tokens' in oneinch_data:
        for t in oneinch_data['tokens']:
            sym = str(t.get('symbol')).lower()
            cid = t.get('chainId')
            addr = t.get('address')
            if sym not in token_dict:
                token_dict[sym] = {}
            token_dict[sym][cid] = addr
    
    # 2. Uniswap Default List
    uni_url = "https://gateway.ipfs.io/ipns/tokens.uniswap.org"
    uni_data = fetch_json_secure(uni_url)
    if uni_data and 'tokens' in uni_data:
        for t in uni_data['tokens']:
            sym = str(t.get('symbol')).lower()
            cid = t.get('chainId')
            addr = t.get('address')
            if sym not in token_dict:
                token_dict[sym] = {}
            if cid not in token_dict[sym]:
                token_dict[sym][cid] = addr
                
    # Evaluate pending queue
    resolved_count = 0
    failed_count = 0
    
    for queue_id, symbol, cid in pending:
        sym_lower = symbol.lower()
        
        # Check dictionary
        contract_addr = None
        if sym_lower in token_dict:
            if cid in token_dict[sym_lower]:
                contract_addr = token_dict[sym_lower][cid]
            # Fallback: if we only have ETH mainnet address but need an L2 address, 
            # true cross-chain resolution requires a bridging map. 
            # For now, if we match the EXACT chain, we resolve it.
        
        if contract_addr:
            tok_id = f"{symbol}-{cid}"
            cursor.execute('''
                INSERT OR IGNORE INTO tokens (token_id, symbol, chain_id, contract_address, knowledge_status, last_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tok_id, symbol, cid, contract_addr, 'VERIFIED', now))
            
            cursor.execute('''
                UPDATE token_resolution_queue SET status='RESOLVED' WHERE queue_id=?
            ''', (queue_id,))
            resolved_count += 1
        else:
            # Leave as PENDING or mark UNRESOLVED
            failed_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"Phase 6 Complete. Resolved: {resolved_count} | Unresolved: {failed_count}")
    
    with open(os.path.join(base, 'execution_report.md'), 'a', encoding='utf-8') as f:
        f.write(f"\\n## Report 19: Phase 6 Token Resolution\\n")
        f.write(f"**Task:** Resolved token identities using zero-cost global lists.\\n")
        f.write(f"**Result:** Resolved {resolved_count} tokens. {failed_count} remaining pending.\\n")

if __name__ == "__main__":
    resolve_tokens()
