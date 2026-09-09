import sqlite3
import os

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def upgrade_schema():
    print("--- PHANTOMX DB SCHEMA UPGRADE V2 (EXECUTION READY) ---")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Function to add column safely
    def add_col(table, col, def_type):
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {def_type}")
            print(f"Added {col} to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col} already exists in {table}")
            else:
                print(f"Error adding {col} to {table}: {e}")

    # 1. Protocols (DEXs)
    add_col('protocols', 'router_address', 'TEXT')
    add_col('protocols', 'factory_address', 'TEXT')
    add_col('protocols', 'confidence', 'TEXT')
    add_col('protocols', 'observed_at', 'TEXT')

    # 2. Pools
    add_col('pools', 'pool_address', 'TEXT')
    add_col('pools', 'token_a_address', 'TEXT')
    add_col('pools', 'token_b_address', 'TEXT')
    add_col('pools', 'fee_tier', 'TEXT')
    add_col('pools', 'confidence', 'TEXT')
    add_col('pools', 'observed_at', 'TEXT')

    # 3. Tokens (already has contract_address, add decimals and others)
    add_col('tokens', 'decimals', 'INTEGER')
    add_col('tokens', 'confidence', 'TEXT')
    add_col('tokens', 'observed_at', 'TEXT')

    # 4. Flash Loan Providers
    add_col('flash_loan_providers', 'contract_address', 'TEXT')
    add_col('flash_loan_providers', 'supported_assets', 'TEXT')
    add_col('flash_loan_providers', 'confidence', 'TEXT')
    add_col('flash_loan_providers', 'observed_at', 'TEXT')
    
    # 5. Chains
    add_col('chains', 'confidence', 'TEXT')
    add_col('chains', 'observed_at', 'TEXT')

    conn.commit()
    conn.close()
    print("Schema Upgrade Complete.")

if __name__ == '__main__':
    upgrade_schema()
