import sqlite3

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def run_db_updates():
    print("--- PHANTOMX POST-ANALYSIS UPDATES ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Update UNCERTAIN status for chains with DeFi Active = Yes but 0 DEXs/Pools
    # First, find chains with 0 DEXs
    c.execute("""
        UPDATE chains 
        SET knowledge_status = 'UNCERTAIN', confidence = 'CONFLICTED'
        WHERE is_defi_active = 1 AND chain_id NOT IN (
            SELECT DISTINCT chain_id FROM protocols
        )
    """)
    print(f"Marked {c.rowcount} chains as UNCERTAIN/CONFLICTED due to missing DEXs.")
    
    # 2. Extract Data to JSON for the Knowledge Agent (Deliverable 1)
    import json
    import os
    
    base_dir = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
    output_json = os.path.join(base_dir, 'phantomx_parsed_data.json')
    
    export_data = {}
    
    c.execute("SELECT * FROM chains")
    chains_cols = [desc[0] for desc in c.description]
    export_data['chains'] = [dict(zip(chains_cols, row)) for row in c.fetchall()]
    
    c.execute("SELECT * FROM protocols")
    proto_cols = [desc[0] for desc in c.description]
    export_data['protocols'] = [dict(zip(proto_cols, row)) for row in c.fetchall()]
    
    c.execute("SELECT * FROM pools LIMIT 5000") # Limit to prevent massive JSON string in memory, though we should export all if possible
    pool_cols = [desc[0] for desc in c.description]
    export_data['pools'] = [dict(zip(pool_cols, row)) for row in c.fetchall()]
    
    c.execute("SELECT * FROM flash_loan_providers")
    fl_cols = [desc[0] for desc in c.description]
    export_data['flash_loan_providers'] = [dict(zip(fl_cols, row)) for row in c.fetchall()]
    
    c.execute("SELECT * FROM rpcs")
    rpc_cols = [desc[0] for desc in c.description]
    export_data['rpcs'] = [dict(zip(rpc_cols, row)) for row in c.fetchall()]
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4)
        
    print(f"Exported Machine-Readable JSON to {output_json}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    run_db_updates()
