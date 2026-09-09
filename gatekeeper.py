import sqlite3
import os

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
db_path = os.path.join(base, 'phantomx_knowledge.db')

def enforce_gates():
    if not os.path.exists(db_path):
        print("FAIL: DB does not exist.")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check Phase 1: Chains
    cursor.execute("SELECT count(*) FROM chains WHERE knowledge_status='VERIFIED'")
    verified_chains = cursor.fetchone()[0]
    if verified_chains == 0:
        print("GATE FAILED: Phase 1 (Chains). 0 VERIFIED chains found.")
        return False
    print(f"GATE PASSED: Phase 1 (Chains). Found {verified_chains} verified chains.")
    
    # Check Phase 2: RPCs
    cursor.execute("SELECT count(*) FROM rpcs WHERE is_active=1")
    active_rpcs = cursor.fetchone()[0]
    if active_rpcs == 0:
        print("GATE FAILED: Phase 2 (RPCs). 0 ACTIVE RPCs found.")
        return False
    print(f"GATE PASSED: Phase 2 (RPCs). Found {active_rpcs} active RPCs.")
    
    # Check Phase 3: DEXs (Protocols)
    try:
        cursor.execute("SELECT count(*) FROM protocols")
        protocols = cursor.fetchone()[0]
        if protocols == 0:
            print("GATE FAILED: Phase 3 (DEXs). 0 MAPPED DEXs found.")
            return False
        print(f"GATE PASSED: Phase 3 (DEXs). Found {protocols} mapped protocols.")
    except Exception as e:
        print(f"GATE FAILED: Phase 3 (DEXs) exception: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("--- PHANTOMX GATEKEEPER ---")
    if enforce_gates():
        print("SYSTEM STATUS: GREEN. Ready for next phase.")
    else:
        print("SYSTEM STATUS: RED. Execution blocked due to lack of evidence.")
