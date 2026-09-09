import pytest
import sqlite3
import pandas as pd
import numpy as np
import pickle
import os

from ai_model_trainer import db_path, model_path

# ==========================================
# UNIT TESTS: MATHEMATICAL & AI ENGINE
# ==========================================

def test_ai_model_loading_and_prediction():
    # Test if model is generated and can predict
    assert os.path.exists(model_path), "AI Model not found!"
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        
    # Dummy data: tvl_a, tvl_b, apy_variance, gas_cost
    dummy_input = pd.DataFrame([[500000, 400000, 5.0, 50]], columns=['tvl_a', 'tvl_b', 'apy_variance', 'gas_cost'])
    prediction = model.predict(dummy_input)
    
    assert prediction[0] > 0, "AI failed to predict a valid optimal loan size."
    assert prediction[0] < 500000, "AI predicted an unrealistically large loan size."

def test_database_schema_integrity():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check execution_logs
    c.execute("PRAGMA table_info(execution_logs)")
    cols = [row[1] for row in c.fetchall()]
    assert 'decision' in cols
    assert 'outcome' in cols
    
    # Check pools identity layer
    c.execute("PRAGMA table_info(pools)")
    cols = [row[1] for row in c.fetchall()]
    assert 'pool_address' in cols
    assert 'fee_tier' in cols
    
    conn.close()

# ==========================================
# INTEGRATION TESTS: LOGIC PIPELINES
# ==========================================

def test_profit_calculation_logic():
    # Simple spatial arbitrage mathematical test (mocked AMM logic)
    # If DEX A and DEX B have exactly same reserves, profit should be negative (due to fees)
    from global_hunting_orchestrator import calculate_opportunity
    
    pool_a = {'tvlUsd': 100000, 'apy': 5.0}
    pool_b = {'tvlUsd': 100000, 'apy': 5.0}
    profit, status = calculate_opportunity(pool_a, pool_b)
    
    assert status == "NO_OPPORTUNITY", "Engine falsely identified a 0-variance pair as profitable."
    
    # High variance should be profitable
    pool_c = {'tvlUsd': 100000, 'apy': 25.0}
    profit, status = calculate_opportunity(pool_a, pool_c)
    assert status == "PROFITABLE", "Engine failed to identify a massive 20% variance arbitrage."
    assert profit > 0, "Profit must be positive for a profitable status."

# Run via: pytest test_suite.py -v
