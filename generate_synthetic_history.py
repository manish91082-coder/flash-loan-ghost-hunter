import sqlite3
import json
import random

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'

def create_synthetic_history():
    print("=== SYNTHESIZING HISTORICAL ARBITRAGE DATA ===")
    
    # Connect to the local SQLite DB to fetch current pools
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT pool_id, pool_name, tvl, base_apy FROM pools WHERE tvl > 10000 LIMIT 100")
    pools = c.fetchall()
    
    # We will generate 10,000 synthetic rows that represent 'past' states
    # This helps the AI learn what conditions were historically profitable
    
    synthetic_data = []
    
    for i in range(10000):
        # Pick two random pools to represent Pool A and Pool B for arbitrage
        pool_a = random.choice(pools)
        pool_b = random.choice(pools)
        
        # We need overlapping pairs. If they don't overlap in name, skip.
        # But for synthetic training, we just want to teach it the MATH of arbitrage.
        
        # Synthetic TVLs (varying historical amounts)
        tvl_a_hist = pool_a[2] * random.uniform(0.5, 1.5)
        tvl_b_hist = pool_b[2] * random.uniform(0.5, 1.5)
        
        # Synthetic APYs
        apy_a_hist = pool_a[3] * random.uniform(0.8, 1.2) if pool_a[3] else 2.0
        apy_b_hist = pool_b[3] * random.uniform(0.8, 1.2) if pool_b[3] else 2.0
        
        apy_variance = abs(apy_a_hist - apy_b_hist)
        
        # Base Gas Cost on Ethereum fluctuates between $10 and $150
        gas_cost_usd = random.uniform(10, 150)
        
        # True Optimal Flash Loan Size Formula (Simplified for synthetic generation)
        # In reality, this depends on the constant product formula dx = (y*dx) / (x+dx)
        # Here we teach it that higher variance and higher TVL = bigger loan size.
        
        if apy_variance > 1.0 and min(tvl_a_hist, tvl_b_hist) > 50000:
            # A profitable scenario
            base_loan_size = min(tvl_a_hist, tvl_b_hist) * (apy_variance / 100.0)
            optimal_loan_size = base_loan_size - gas_cost_usd - (base_loan_size * 0.0009) # 0.09% flash loan fee
            if optimal_loan_size < 0:
                optimal_loan_size = 0
        else:
            # Unprofitable scenario
            optimal_loan_size = 0
            
        synthetic_data.append({
            "timestamp": f"2025-0{random.randint(1,9)}-15T10:00:00Z",
            "pool_a_id": pool_a[0],
            "pool_b_id": pool_b[0],
            "tvl_a": round(tvl_a_hist, 2),
            "tvl_b": round(tvl_b_hist, 2),
            "apy_variance": round(apy_variance, 4),
            "gas_cost": round(gas_cost_usd, 2),
            "historical_optimal_loan": round(optimal_loan_size, 2)
        })
        
    with open("synthetic_arbitrage_history.json", "w") as f:
        json.dump(synthetic_data, f, indent=4)
        
    print(f"Generated {len(synthetic_data)} synthetic historical arbitrage events.")
    print("Saved to synthetic_arbitrage_history.json")

if __name__ == '__main__':
    create_synthetic_history()
