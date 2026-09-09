import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

np.random.seed(42)

scaler = StandardScaler()
# Using SGDRegressor with StandardScaler
model = SGDRegressor(loss='squared_error', penalty='l2', alpha=1e-3, learning_rate='invscaling', eta0=0.01, random_state=42)

print("\n--- Testing Online Scaler + SGDRegressor ---")
for i in range(50):
    X_sub = np.random.uniform(50000, 10000000, (10000, 5)).astype(np.float32)
    y_sub = (X_sub[:, 0] * 0.01 / 100000.0).astype(np.float32)
    
    # Update scaler incrementally
    scaler.partial_fit(X_sub)
    X_scaled = scaler.transform(X_sub)
    
    model.partial_fit(X_scaled, y_sub)
    
    pred = model.predict(X_scaled[:2000])
    mse = mean_squared_error(y_sub[:2000], pred)
    r2 = r2_score(y_sub[:2000], pred)
    if (i+1) % 10 == 0 or i == 0:
        print(f"Subchunk #{i+1}: MSE={mse:.6f}, R2={r2:.6f}, max_coef={np.max(np.abs(model.coef_)):.4f}")
