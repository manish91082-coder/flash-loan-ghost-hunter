import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle
import os

db_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_knowledge.db'
model_path = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_ai_brain.pkl'

def generate_training_data():
    print("--- PHANTOMX AI: DATA PREPARATION & SYNTHESIS ---")
    # We will generate a synthetic but highly realistic dataset based on our previous simulation logic
    # In a real environment, this would pull from months of historical execution logs.
    np.random.seed(42)
    n_samples = 10000
    
    # Features: TVL_A, TVL_B, APY_Variance, Gas_Cost
    # Target: Optimal Flash Loan Size (USD) that maximizes net profit
    
    tvl_a = np.random.uniform(10000, 10000000, n_samples)
    tvl_b = np.random.uniform(10000, 10000000, n_samples)
    apy_variance = np.random.uniform(0.1, 15.0, n_samples) # 0.1% to 15% difference
    gas_cost = np.random.uniform(10, 150, n_samples) # $10 to $150 gas
    
    # Mathematical optimization proxy (in reality, the model learns this from raw data)
    # The higher the TVL, the more liquidity can be absorbed without slippage killing the trade.
    # The higher the variance, the deeper the price dislocation.
    min_tvl = np.minimum(tvl_a, tvl_b)
    optimal_loan_size = min_tvl * (apy_variance / 100.0) * 0.5 
    
    # Add noise to simulate real-world MEV and slippage unpredictability
    noise = np.random.normal(0, optimal_loan_size * 0.05)
    optimal_loan_size = np.maximum(0, optimal_loan_size + noise)
    
    # Net profit calculation based on optimal loan size
    gross_profit = optimal_loan_size * (apy_variance / 100.0)
    net_profit = gross_profit - gas_cost - (optimal_loan_size * 0.0009) # 0.09% flash loan fee
    
    # Filter out unprofitable trades so the model learns from SUCCESS
    df = pd.DataFrame({
        'TVL_A': tvl_a,
        'TVL_B': tvl_b,
        'APY_Variance': apy_variance,
        'Gas_Cost': gas_cost,
        'Optimal_Loan_Size': optimal_loan_size,
        'Net_Profit': net_profit
    })
    
    profitable_df = df[df['Net_Profit'] > 0]
    print(f"Generated {len(profitable_df)} profitable training samples from {n_samples} total simulations.")
    return profitable_df

def train_model():
    print("--- PHANTOMX AI: NEURAL TRAINING SEQUENCE ---")
    df = generate_training_data()
    
    X = df[['TVL_A', 'TVL_B', 'APY_Variance', 'Gas_Cost']]
    y = df['Optimal_Loan_Size']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Regressor (Decision Agent)...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    
    print(f"Model Training Complete. RMSE: ${rmse:.2f} (Accuracy of Loan Sizing)")
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Model saved to {model_path}. System is now capable of Autonomous Self-Decision.")

if __name__ == '__main__':
    train_model()
