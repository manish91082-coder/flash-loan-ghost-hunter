from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy
from quote_engine.adapters import QuoteAdapterFactory

class StatisticalArbitrage(BaseStrategy):
    """
    Mean-reversion strategy. Relies on spot price deviating from TWAP.
    """
    def __init__(self, profit_calc=None):
        self.profit_calc = profit_calc
        
    def discover_opportunities(self, discovery_engine) -> List[Dict[str, Any]]:
        # Statistical arbitrage requires pools with concentrated liquidity (V3)
        pairs = discovery_engine.generate_candidate_pairs()
        candidates = []
        for pair in pairs:
            if pair["type"] == "V3":
                candidates.append({
                    "strategy": "Statistical",
                    "chain_id": pair["chain_id"],
                    "chain_config": pair["chain_config"],
                    "tokenA": pair["tokenA"],
                    "tokenB": pair["tokenB"],
                    "decimals": pair["tokenA_dec"],
                    "fee": pair["v3_fee"]
                })
        return candidates
        
    def extract_market_state(self, candidate: Dict[str, Any], rpc_manager) -> Dict[str, Any]:
        # Step 1: Extract Spot Price
        chain_config = candidate["chain_config"]
        dexes = chain_config.get("dexes", {})
        
        v3_router = None
        v3_quoter = None
        for dex_name, dex_cfg in dexes.items():
            if "v3" in dex_name.lower() or "uniswap_v3" in dex_name:
                v3_quoter = dex_cfg.get("quoter")
                v3_router = dex_cfg.get("router")
                break
                
        if not v3_quoter:
            return {"status": "FAILED", "failure_code": "NO_V3_DEX_CONFIGURED"}
            
        adapter = QuoteAdapterFactory.get_adapter("v3", rpc_manager)
        amount_in = 1 * (10 ** candidate["decimals"])
        
        try:
            market_state = adapter.fetch_market_state(v3_quoter, candidate["tokenA"], candidate["tokenB"], amount_in, candidate["fee"])
            spot_out = adapter.calculate_out_given_in(market_state, amount_in)
            if spot_out is None:
                return {"status": "FAILED", "failure_code": "SPOT_QUOTE_REVERTED"}
        except Exception:
            return {"status": "FAILED", "failure_code": "SPOT_QUOTE_REVERTED"}
            
        # Step 2: Attempt to get TWAP (Time-Series Data)
        v3_factory = None
        for dex_name, dex_cfg in dexes.items():
            if "v3" in dex_name.lower() or "uniswap_v3" in dex_name:
                v3_factory = dex_cfg.get("factory")
                break
                
        if not v3_factory:
            return {"status": "FAILED", "failure_code": "NO_V3_FACTORY_CONFIGURED"}
            
        try:
            # We attempt to read the TWAP from the Uniswap V3 Pool
            twap_data = rpc_manager.get_univ3_twap(v3_factory, candidate["tokenA"], candidate["tokenB"], candidate["fee"], seconds_ago=300)
            
            # (If it successfully returns, we would calculate the time-weighted average price
            # using tick cumulatives. But since we just need ground-level verification of capability,
            # reaching this point means TWAP is available and oracle is initialized.)
        except Exception as e:
            error_str = str(e).upper()
            if "OLD" in error_str:
                return {"status": "FAILED", "failure_code": "TWAP_OBSERVATION_OLD_CARDINALITY_TOO_LOW"}
            elif "POOL_DOES_NOT_EXIST" in error_str:
                return {"status": "FAILED", "failure_code": "V3_POOL_NOT_DEPLOYED"}
            else:
                return {"status": "FAILED", "failure_code": "TWAP_RPC_REVERTED"}
        
        return {
            "status": "VALID",
            "spot_price": spot_out,
            "twap_available": True,
            "amount_in": amount_in
        }
        
    def evaluate_economics(self, state: Dict[str, Any], profit_calc) -> Dict[str, Any]:
        return {"is_safe": False}
        
    def build_intent(self, state: Dict[str, Any], intent_builder) -> Dict[str, Any]:
        return {}
