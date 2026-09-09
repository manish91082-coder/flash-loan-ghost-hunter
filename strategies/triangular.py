from typing import Dict, Any, List
from strategies.base_strategy import BaseStrategy

class TriangularArbitrage(BaseStrategy):
    """
    TRIANGULAR ARBITRAGE
    A -> B -> C -> A on the same venue.
    """
    def discover_opportunities(self, discovery_engine) -> List[Dict[str, Any]]:
        candidates = []
        dexes = discovery_engine.config.get("dexes", {})
        
        # We need at least 3 anchor tokens
        tokens = discovery_engine.get_anchor_tokens()
        if len(tokens) < 3:
            return candidates
            
        for venue_name, venue_config in dexes.items():
            # For simplicity in Phase 2, we just test A -> B -> C -> A
            # where A = tokens[0], B = tokens[1], C = tokens[2]
            tokenA = tokens[0]
            tokenB = tokens[1]
            tokenC = tokens[2]
            
            amount_in = 1 * (10 ** tokenA["decimals"])
            
            candidates.append({
                "strategy": "Triangular",
                "chain_id": discovery_engine.chain_id,
                "chain_config": discovery_engine.config,
                "venue": venue_name,
                "venue_config": venue_config,
                "tokenA": tokenA["address"],
                "tokenB": tokenB["address"],
                "tokenC": tokenC["address"],
                "tokenA_dec": tokenA["decimals"],
                "amount_in": amount_in,
                "type": 'v3' if 'v3' in venue_name.lower() else 'v2'
            })
            
        return candidates
        
    def extract_market_state(self, candidate: Dict[str, Any], rpc_manager) -> Dict[str, Any]:
        from quote_engine.adapters import QuoteAdapterFactory
        
        venue_type = candidate["type"]
        adapter = QuoteAdapterFactory.get_adapter(venue_type, rpc_manager)
        venue_config = candidate["venue_config"]
        
        target = venue_config.get("quoter") if venue_type == 'v3' else venue_config.get("router")
        if not target:
            return {"status": "QUOTE_FAILED", "failure_code": "MISSING_DEX_CONFIG"}
            
        amount_in = candidate["amount_in"]
        
        # Leg 1: A -> B
        if venue_type == 'v3':
            state_1 = adapter.fetch_market_state(target, candidate["tokenA"], candidate["tokenB"], amount_in, 500)
            leg1_out = adapter.calculate_out_given_in(state_1, amount_in)
        else:
            state_1 = adapter.fetch_market_state(target, candidate["tokenA"], candidate["tokenB"], amount_in)
            leg1_out = adapter.calculate_out_given_in(state_1, amount_in, 30)
            
        if not leg1_out or leg1_out <= 0:
            return {"status": "QUOTE_FAILED", "failure_code": "LEG_1_FAILED"}
            
        # Leg 2: B -> C
        if venue_type == 'v3':
            state_2 = adapter.fetch_market_state(target, candidate["tokenB"], candidate["tokenC"], leg1_out, 500, block_identifier=state_1.get("block_number", "latest"))
            leg2_out = adapter.calculate_out_given_in(state_2, leg1_out)
        else:
            state_2 = adapter.fetch_market_state(target, candidate["tokenB"], candidate["tokenC"], leg1_out, block_identifier=state_1.get("block_number", "latest"))
            leg2_out = adapter.calculate_out_given_in(state_2, leg1_out, 30)
            
        if not leg2_out or leg2_out <= 0:
            return {"status": "QUOTE_FAILED", "failure_code": "LEG_2_FAILED"}
            
        # Leg 3: C -> A
        if venue_type == 'v3':
            state_3 = adapter.fetch_market_state(target, candidate["tokenC"], candidate["tokenA"], leg2_out, 500, block_identifier=state_1.get("block_number", "latest"))
            leg3_out = adapter.calculate_out_given_in(state_3, leg2_out)
        else:
            state_3 = adapter.fetch_market_state(target, candidate["tokenC"], candidate["tokenA"], leg2_out, block_identifier=state_1.get("block_number", "latest"))
            leg3_out = adapter.calculate_out_given_in(state_3, leg2_out, 30)
            
        if not leg3_out or leg3_out <= 0:
            return {"status": "QUOTE_FAILED", "failure_code": "LEG_3_FAILED"}
            
        gross_profit = leg3_out - amount_in
        
        candidate.update({
            "status": "VALID",
            "leg1_out": leg1_out,
            "leg2_out": leg2_out,
            "quote_out": leg3_out,
            "gross_profit": gross_profit,
            "estimated_gas": state_1.get("gasEstimate", 150000) * 3,
            "target": target
        })
        
        return candidate
        
    def evaluate_economics(self, state: Dict[str, Any], profit_calc) -> Dict[str, Any]:
        from economics.flash_loan import get_best_provider
        
        chain_id = state.get("chain_id")
        chain_config = state.get("chain_config", {})
        amount_in = state["amount_in"]
        quote_out = state["quote_out"]
        tokenA = state["tokenA"]
        
        provider_addr = get_best_provider(chain_id, tokenA, amount_in)
        if not provider_addr:
            state["is_safe"] = False
            state["failure_code"] = "NO_PROVIDER_AVAILABLE"
            return state
            
        provider_info = chain_config.get("flash_providers", {}).get(provider_addr, {"fee_bps": 5})
        flash_fee = (amount_in * provider_info.get("fee_bps", 5)) // 10000
        gross_profit = quote_out - amount_in - flash_fee
        
        if gross_profit <= 0:
            state["is_safe"] = False
            state["net_profit"] = gross_profit
            state["failure_code"] = "UNPROFITABLE_GROSS"
            return state
            
        state["provider_addr"] = provider_addr
        state["provider_info"] = provider_info
        state["is_safe"] = True
        state["net_profit"] = gross_profit
        return state
        
    def build_intent(self, state: Dict[str, Any], intent_builder) -> Dict[str, Any]:
        import os
        import time
        from execution.intent import PathEncoder
        import datetime
        
        # We must package 3 hops into PathEncoder.
        # But wait, our current PathEncoder and intent schema might only support Swap1 and Swap2 natively!
        # The executor contract currently splits intent into `pathA` and `pathB`.
        # For a 3-hop triangular on the same router, `pathA` can encode A->B->C->A. 
        # Then `pathB` can just be empty, and `swap2Type = 0` with zero amount.
        # Let's verify PathEncoder can encode a multi-hop path.
        
        # For V2, a path is just a list of addresses: [A, B, C, A]
        # For V3, a path is packed bytes: A + fee1 + B + fee2 + C + fee3 + A
        
        tokenA = state["tokenA"]
        tokenB = state["tokenB"]
        tokenC = state["tokenC"]
        
        if state["type"] == "v3":
            pathA = PathEncoder.build_v3_path_triangular(
                tokenA, 500, tokenB, 500, tokenC, 500, tokenA
            )
            swap1Type = 1
        else:
            pathA = PathEncoder.build_v2_path([tokenA, tokenB, tokenC, tokenA])
            swap1Type = 0
            
        min_amount_out_final = state["quote_out"] * 995 // 1000
        
        intent_dict = {
            "executionId": os.urandom(32), 
            "providerType": state["provider_info"].get("type", 1),
            "providerAddress": state["provider_addr"],
            "tokenBorrow": tokenA,
            "amountBorrow": state["amount_in"],
            "swap1Type": swap1Type,
            "routerA": state["target"],
            "pathA": pathA,
            "minAmountOut1": 0, # Not applicable for full multi-hop single-router
            "swap2Type": 0, # Null swap 2
            "routerB": "0x0000000000000000000000000000000000000000",
            "pathB": b"",
            "minAmountOutFinal": min_amount_out_final,
            "minimumOnChainSurplus": 0,
            "maximumGasLimit": 1000000,
            "deadline": int(time.time()) + 300
        }
        
        calldata = intent_builder.build_calldata(intent_dict)
        
        opp_id = f"OPP-{state['chain_id']}-TRI-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "opp_id": opp_id,
            "chain_id": state["chain_id"],
            "strategy": "Triangular",
            "quote_status": "VALID",
            "liquidity_sufficient": True,
            "net_profit": state["net_profit"],
            "is_safe": state["is_safe"],
            "calldata": calldata,
            "intent_dict": intent_dict,
            "borrow_token": tokenA,
            "borrow_amount": state["amount_in"],
            "provider_addr": state["provider_addr"]
        }

