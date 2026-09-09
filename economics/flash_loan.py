import json
import os
from typing import Optional

def load_chain_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'chains.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"chains": {}}

def get_best_provider(chain_id: int, borrow_asset: str, amount: int) -> Optional[str]:
    """
    Returns the best flash loan provider address for the given chain based on basic logic:
    1. Aave V3 (0.05% fee)
    2. Uniswap V3 (variable fee 0.05% or 0.30%)
    3. Balancer (0% fee but limited asset coverage)
    Fallback to None if no provider works.
    """
    config_data = load_chain_config()
    # The JSON config is a flat dict where keys are chain IDs
    chain_config = config_data.get(str(chain_id))
    
    if not chain_config:
        return None
        
    providers = chain_config.get('flash_loan_providers', {})
    
    # Logic: Balancer 0 fee if available (ideal case)
    if 'balancer' in providers and providers['balancer']:
        # Assuming Balancer has liquidity
        return providers['balancer']
        
    # Fallback to Aave V3
    if 'aave_v3' in providers and providers['aave_v3']:
        return providers['aave_v3']
        
    # Fallback to UniV3 if flash loan is supported via callback
    if 'uniswap_v3' in providers and providers['uniswap_v3']:
        return providers['uniswap_v3']
        
    return None
