import json
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

def train_new_model():
    print("=== TRAINING NEW AI BRAIN ON SYNTHETIC HISTORY ===")
    
    with open("synthetic_arbitrage_history.json", "r") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # Features: TVL of Pool A, TVL of Pool B, APY Variance, Gas Cost
    X = df[['tvl_a', 'tvl_b', 'apy_variance', 'gas_cost']]
    # Target: The historically optimal loan size that maximized profit
    y = df['historical_optimal_loan']
    
    print(f"Training on {len(df)} historical data points...")
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print("Model Training Complete. Score:", model.score(X,y))
    
    # Save the updated brain
    with open(r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter\phantomx_ai_brain.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    print("New AI Brain Saved to phantomx_ai_brain.pkl")

if __name__ == '__main__':
    train_new_model()
