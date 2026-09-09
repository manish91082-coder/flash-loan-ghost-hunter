import os
import time
import datetime
from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy
from execution.intent import PathEncoder

class SpatialArbitrage(BaseStrategy):
    """
    SPATIAL ARBITRAGE
    Same asset traded across two distinct venues dynamically.
    """
    def __init__(self, discovery_agent, market_agent, profit_calc):
        self.profit_calc = profit_calc

    def discover_opportunities(self, discovery_engine) -> List[Dict[str, Any]]:
        candidates = []
        dexes = discovery_engine.config.get("dexes", {})
        venues = list(dexes.keys())
        if len(venues) < 2:
            return candidates
            
        base_pairs = discovery_engine.generate_candidate_pairs()
        
        # We need a combination of Venue A -> Venue B.
        # For simplicity, let's just use the first two configured venues for Spatial
        # In a fully saturated environment we'd test all combinations of len 2.
        venue_A = venues[0]
        venue_B = venues[1]
        
        for pair in base_pairs:
            # We only generate spatial for base token pairs (A->B then B->A)
            # Default trade size: 1 unit of Token A (e.g. 1 WETH or 1 USDC) to ensure quotes don't revert
            amount_in = 1 * (10 ** pair["tokenA_dec"])
            
            candidates.append({
                "strategy": "Spatial",
                "chain_id": pair.get("chain_id"),
                "chain_config": pair.get("chain_config"),
                "venue_A": venue_A,
                "venue_B": venue_B,
                "dexes_config": dexes,
                "token_in": pair["tokenA"],
                "token_out": pair["tokenB"],
                "token_in_sym": pair["tokenA_sym"],
                "token_out_sym": pair["tokenB_sym"],
                "amount_in": amount_in,
                "v3_fee": pair.get("v3_fee", 500),
                "v2_fee_bips": pair.get("v2_fee_bips", 30),
                "type": pair["type"] # The primary venue's expected pair type
            })
            
        return candidates

    def extract_market_state(self, candidate: Dict[str, Any], rpc_manager) -> Dict[str, Any]:
        """
        Fetches quotes from Venue A and Venue B dynamically.
        """
        from quote_engine.adapters import QuoteAdapterFactory
        
        venue_A = candidate["venue_A"]
        venue_B = candidate["venue_B"]
        dexes = candidate["dexes_config"]
        
        # Deduce adapter type from venue name loosely
        type_A = 'v3' if 'v3' in venue_A.lower() else 'v2'
        type_B = 'v3' if 'v3' in venue_B.lower() else 'v2'
        
        adapter_A = QuoteAdapterFactory.get_adapter(type_A, rpc_manager)
        adapter_B = QuoteAdapterFactory.get_adapter(type_B, rpc_manager)
        
        config_A = dexes.get(venue_A, {})
        config_B = dexes.get(venue_B, {})
        
        # Target contracts
        target_A = config_A.get("quoter") if type_A == 'v3' else config_A.get("router") # Ideally we use a quoter or factory/pair
        target_B = config_B.get("quoter") if type_B == 'v3' else config_B.get("router")
        
        if not target_A or not target_B:
            return {"status": "QUOTE_FAILED", "failure_code": "MISSING_DEX_CONFIG"}
            
        # Leg 1: TokenIn -> TokenOut on Venue A
        amount_in = candidate["amount_in"]
        
        if type_A == 'v3':
            fee = candidate.get("v3_fee", 500)
            state_A = adapter_A.fetch_market_state(target_A, candidate["token_in"], candidate["token_out"], amount_in, fee)
            leg1_out = adapter_A.calculate_out_given_in(state_A, amount_in)
        else:
            state_A = adapter_A.fetch_market_state(target_A, candidate["token_in"], candidate["token_out"], amount_in)
            fee_bips = candidate.get("v2_fee_bips", 30)
            leg1_out = adapter_A.calculate_out_given_in(state_A, amount_in, fee_bips)
            
        if not leg1_out or leg1_out <= 0:
            return {"status": "QUOTE_FAILED", "failure_code": "LEG_1_FAILED"}
            
        # Leg 2: TokenOut -> TokenIn on Venue B
        if type_B == 'v3':
            fee = candidate.get("v3_fee", 500)
            state_B = adapter_B.fetch_market_state(target_B, candidate["token_out"], candidate["token_in"], leg1_out, fee, block_identifier=state_A.get("block_number", "latest"))
            leg2_out = adapter_B.calculate_out_given_in(state_B, leg1_out)
        else:
            state_B = adapter_B.fetch_market_state(target_B, candidate["token_out"], candidate["token_in"], leg1_out, block_identifier=state_A.get("block_number", "latest"))
            fee_bips = candidate.get("v2_fee_bips", 30)
            leg2_out = adapter_B.calculate_out_given_in(state_B, leg1_out, fee_bips)

        if not leg2_out or leg2_out <= 0:
            return {"status": "QUOTE_FAILED", "failure_code": "LEG_2_FAILED"}
            
        gross_profit = leg2_out - amount_in
        
        candidate.update({
            "status": "VALID",
            "leg1_out": leg1_out,
            "quote_out": leg2_out,
            "gross_profit": gross_profit,
            "estimated_gas": state_A.get("gasEstimate", 150000) + state_B.get("gasEstimate", 150000),
            "state_A": state_A,
            "state_B": state_B,
            "target_A": target_A,
            "target_B": target_B,
            "type_A": type_A,
            "type_B": type_B
        })
        
        return candidate

    def evaluate_economics(self, state: Dict[str, Any], profit_calc) -> Dict[str, Any]:
        """
        Dynamically fetch the best flash loan provider and calculate absolute integer math profitability.
        """
        from economics.flash_loan import get_best_provider
        
        chain_id = state.get("chain_id")
        chain_config = state.get("chain_config", {})
        amount_in = state["amount_in"]
        quote_out = state["quote_out"]
        gas_estimate = state.get("estimated_gas", 300000)
        token_in = state["token_in"]
        
        provider_addr = get_best_provider(chain_id, token_in, amount_in)
        if not provider_addr:
            state["is_safe"] = False
            state["failure_code"] = "NO_PROVIDER_AVAILABLE"
            return state
            
        provider_info = chain_config.get("flash_providers", {}).get(provider_addr, {"fee_bps": 5})
        
        # Calculate flash loan fee
        flash_fee_bps = provider_info.get("fee_bps", 5)
        flash_fee = (amount_in * flash_fee_bps) // 10000
        
        # Calculate gross profit
        gross_profit = quote_out - amount_in - flash_fee
        
        # Gas cost estimate 
        # Since we don't have w3 and actual calldata here yet, we use a basic estimate
        # 1 ETH = 10^18 wei. If we trade USDC (10^6), we need price conversion.
        # But for Phase 2 stubbing, we will just use gross_profit > 0 and calculate it properly inside intent builder
        
        if gross_profit <= 0:
            state["is_safe"] = False
            state["net_profit"] = gross_profit
            state["failure_code"] = "UNPROFITABLE_GROSS"
            return state
            
        # Passing gas/eth checks down to pipeline or treating gross > threshold
        min_profit_usd = chain_config.get("min_profit_usd", 1.0)
        min_profit_tokens = int(min_profit_usd * (10 ** state.get("token_in_dec", 6))) # Rough estimation
        
        if gross_profit < min_profit_tokens:
            state["is_safe"] = False
            state["net_profit"] = gross_profit
            state["failure_code"] = "PROFIT_BELOW_THRESHOLD"
            return state
            
        state["provider_addr"] = provider_addr
        state["provider_info"] = provider_info
        state["is_safe"] = True
        state["net_profit"] = gross_profit
        return state

    def build_intent(self, state: Dict[str, Any], intent_builder) -> Dict[str, Any]:
        """
        Build EIP-712 payload dynamically across any valid spatial venues.
        """
        import os
        import time
        from execution.intent import PathEncoder
        
        token_in = state["token_in"]
        token_out = state["token_out"]
        
        # Path encoding based on venue type
        if state["type_A"] == "v3":
            pathA = PathEncoder.build_v3_path_single(token_in, state.get("v3_fee", 500), token_out)
            swap1Type = 1
        else:
            pathA = PathEncoder.build_v2_path([token_in, token_out])
            swap1Type = 0
            
        if state["type_B"] == "v3":
            pathB = PathEncoder.build_v3_path_single(token_out, state.get("v3_fee", 500), token_in)
            swap2Type = 1
        else:
            pathB = PathEncoder.build_v2_path([token_out, token_in])
            swap2Type = 0
            
        # Slippage - hardcoded 0.5% for now
        min_amount_out1 = state["leg1_out"] * 995 // 1000
        min_amount_out_final = state["quote_out"] * 995 // 1000
        
        intent_dict = {
            "executionId": os.urandom(32), 
            "providerType": state["provider_info"].get("type", 1),
            "providerAddress": state["provider_addr"],
            "tokenBorrow": token_in,
            "amountBorrow": state["amount_in"],
            "swap1Type": swap1Type,
            "routerA": state["target_A"],
            "pathA": pathA,
            "minAmountOut1": min_amount_out1,
            "swap2Type": swap2Type,
            "routerB": state["target_B"],
            "pathB": pathB,
            "minAmountOutFinal": min_amount_out_final,
            "minimumOnChainSurplus": 0,
            "maximumGasLimit": 1000000,
            "deadline": int(time.time()) + 300
        }
        
        calldata = intent_builder.build_calldata(intent_dict)
        
        # Build standard opportunity dictionary for pipeline
        import datetime
        opp_id = f"OPP-{state['chain_id']}-SPAT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "opp_id": opp_id,
            "chain_id": state["chain_id"],
            "strategy": "Spatial",
            "quote_status": "VALID",
            "liquidity_sufficient": True,
            "net_profit": state["net_profit"],
            "is_safe": state["is_safe"],
            "calldata": calldata,
            "intent_dict": intent_dict,
            "borrow_token": token_in,
            "borrow_amount": state["amount_in"],
            "provider_addr": state["provider_addr"]
        }
