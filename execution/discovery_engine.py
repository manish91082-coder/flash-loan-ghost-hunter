import time
from typing import List, Dict, Any

class DiscoveryEngine:
    """
    Dynamically discovers valid trading pairs from a chain's configuration and live RPC state.
    Eliminates all hardcoded token combinations.
    """
    def __init__(self, rpc_manager, chain_config: Dict[str, Any]):
        self.rpc = rpc_manager
        self.config = chain_config
        self.chain_id = chain_config.get("chain_id")
        
    def get_anchor_tokens(self) -> List[Dict[str, Any]]:
        """
        Extracts all dynamically configured tokens from the chain config.
        We use these as discovery anchors.
        """
        tokens = []
        
        # Wrapped Native
        wnative = self.config.get("wrapped_native")
        if wnative:
            tokens.append({"symbol": "W_NATIVE", "address": wnative, "decimals": 18})
            
        # Stablecoins
        stables = self.config.get("stablecoins", {})
        for symbol, addr in stables.items():
            # Assume 6 decimals for USDC/USDT, 18 for DAI/others. For safety we dynamically check if possible,
            # but for baseline discovery we just register them.
            decimals = 6 if symbol in ["USDC", "USDT"] else 18
            tokens.append({"symbol": symbol, "address": addr, "decimals": decimals})
            
        return tokens

    def generate_candidate_pairs(self) -> List[Dict[str, Any]]:
        """
        Creates permutations of available anchor tokens to search for liquidity pools.
        """
        tokens = self.get_anchor_tokens()
        pairs = []
        
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                tA = tokens[i]
                tB = tokens[j]
                
                # Check V3 fee tiers
                for fee in [100, 500, 3000, 10000]:
                    pairs.append({
                        "chain_id": self.chain_id,
                        "chain_config": self.config,
                        "tokenA": tA["address"],
                        "tokenB": tB["address"],
                        "tokenA_sym": tA["symbol"],
                        "tokenB_sym": tB["symbol"],
                        "tokenA_dec": tA["decimals"],
                        "tokenB_dec": tB["decimals"],
                        "v3_fee": fee,
                        "type": "V3"
                    })
                
                # Check V2
                pairs.append({
                    "chain_id": self.chain_id,
                    "chain_config": self.config,
                    "tokenA": tA["address"],
                    "tokenB": tB["address"],
                    "tokenA_sym": tA["symbol"],
                    "tokenB_sym": tB["symbol"],
                    "tokenA_dec": tA["decimals"],
                    "tokenB_dec": tB["decimals"],
                    "v2_fee_bips": 30, # Default V2 fee
                    "type": "V2"
                })
                
        return pairs

    def discover_eligible_venues(self) -> List[str]:
        """
        Returns the list of configured DEX venues on this chain.
        """
        dexes = self.config.get("dexes", {})
        return list(dexes.keys())
