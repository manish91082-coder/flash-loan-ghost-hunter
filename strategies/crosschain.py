from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy

class CrossChainArbitrage(BaseStrategy):
    """
    Cross-Chain Arbitrage strategy. Compares prices of the same asset across chains.
    """
    def __init__(self, profit_calc=None, global_config=None):
        self.profit_calc = profit_calc
        self.global_config = global_config or {}
        
    def discover_opportunities(self, discovery_engine) -> List[Dict[str, Any]]:
        # Cross-chain looks at anchor tokens and marks them for cross-chain pricing
        tokens = discovery_engine.get_anchor_tokens()
        candidates = []
        for token in tokens:
            candidates.append({
                "strategy": "CrossChain",
                "chain_id": discovery_engine.chain_id,
                "chain_config": discovery_engine.config,
                "token": token["address"],
                "symbol": token["symbol"],
                "decimals": token["decimals"]
            })
        return candidates
        
    def extract_market_state(self, candidate: Dict[str, Any], rpc_manager) -> Dict[str, Any]:
        # Step 1: Check if messaging layer / bridge is configured
        bridges = candidate["chain_config"].get("bridges", {})
        if not bridges:
            return {"status": "FAILED", "failure_code": "NO_BRIDGES_CONFIGURED"}
            
        layer_zero = bridges.get("layer_zero")
        if not layer_zero:
            return {"status": "FAILED", "failure_code": "LAYER_ZERO_NOT_CONFIGURED"}
            
        # Step 2: Check cross-chain spot price (requires multi-rpc)
        # We look for a target chain in the global config that also has this token
        target_chain_config = None
        target_chain_id = None
        for cid, c_cfg in self.global_config.items():
            if str(cid) == str(candidate["chain_id"]):
                continue
            if candidate["symbol"] in c_cfg.get("stablecoins", {}):
                target_chain_config = c_cfg
                target_chain_id = cid
                break
                
        if not target_chain_config:
            return {"status": "FAILED", "failure_code": "NO_TARGET_CHAIN_FOR_TOKEN"}
            
        # Step 3: Verify local bridge infrastructure
        try:
            # We attempt to read the LayerZero endpoint version on the local chain
            version = rpc_manager.get_layerzero_version(layer_zero)
        except Exception as e:
            return {"status": "FAILED", "failure_code": "BRIDGE_RPC_REVERTED"}
            
        # To truly verify multi-chain state, we need an RPC for the target chain.
        # Since we only have the single-chain rpc_manager here natively, we safely fail closed.
        return {"status": "FAILED", "failure_code": "MULTI_CHAIN_RPC_UNAVAILABLE"}
            
    def evaluate_economics(self, state: Dict[str, Any], profit_calc) -> Dict[str, Any]:
        return {"is_safe": False}
        
    def build_intent(self, state: Dict[str, Any], intent_builder) -> Dict[str, Any]:
        return {}
