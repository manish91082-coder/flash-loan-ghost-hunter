import os
import sys
import time
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.governance import GovernanceAgent
from agents.discovery import DiscoveryAgent
from agents.knowledge import KnowledgeAgent
from agents.market import MarketAgent
from agents.risk import RiskAgent
from execution.agent import ExecutionAgent
from execution.state_machine import StateMachine

from economics.flash_loan import load_chain_config
from economics.precise_math import PreciseMath
from utils.rpc_health import RPCHealthMonitor
from quote_engine.rpc_fetcher import RPCFallbackManager
from quote_engine.adapters import QuoteAdapterFactory

from strategies.spatial import SpatialArbitrage
from strategies.triangular import TriangularArbitrage
from strategies.statistical import StatisticalArbitrage
from strategies.yield_strat import YieldArbitrage
from strategies.crosschain import CrossChainArbitrage
from strategies.mev import MEVSandwich

def run_mission():
    print("=== STARTING PFLC-5.2 MISSION ===")
    config_data = load_chain_config()
    
    gov = GovernanceAgent({})
    knowledge = KnowledgeAgent()
    market = MarketAgent(None) # Updated per chain
    risk = RiskAgent()
    executor = ExecutionAgent()
    state_machine = StateMachine()
    profit_calc = PreciseMath()
    
    for chain_id_str, config in config_data.items():
        chain_id = int(chain_id_str)
        if not gov.verify_mission_parameters("Spatial", chain_id):
            continue
            
        print(f"[Runner] Initializing Chain {chain_id}")
        rpc = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
        market.rpc_manager = rpc
        discovery = DiscoveryAgent(rpc, config)
        
        adapters = {
            "uniswap_v3": QuoteAdapterFactory.get_adapter('v3', rpc),
            "sushiswap_v2": QuoteAdapterFactory.get_adapter('v2', rpc), # dummy
            "aerodrome_v2": QuoteAdapterFactory.get_adapter('v2', rpc), # dummy
            "velodrome_v2": QuoteAdapterFactory.get_adapter('v2', rpc), # dummy
            "quickswap_v2": QuoteAdapterFactory.get_adapter('v2', rpc), # dummy
            "traderjoe_v2": QuoteAdapterFactory.get_adapter('v2', rpc), # dummy
            "spookyswap_v2": QuoteAdapterFactory.get_adapter('v2', rpc) # dummy
        }
        
        strategies = [
            SpatialArbitrage(discovery, market, profit_calc),
            TriangularArbitrage(discovery, market, profit_calc),
            StatisticalArbitrage(discovery, market, profit_calc),
            YieldArbitrage(discovery, market, profit_calc),
            CrossChainArbitrage(discovery, market, profit_calc),
            MEVSandwich(discovery, market, profit_calc)
        ]
        
        for strategy in strategies:
            strat_name = strategy.__class__.__name__
            candidates = strategy.discover_opportunities(config)
            
            for i, candidate in enumerate(candidates):
                opp_id = f"OPP-{chain_id}-{strat_name.upper()[:4]}-{int(time.time())}-{i}"
                candidate["opportunity_id"] = opp_id
                candidate["chain_id"] = chain_id
                candidate["execution_clearance"] = gov.check_execution_permission()
                
                # 1. State Extraction
                market_state = strategy.extract_market_state(candidate, adapters)
                candidate.update(market_state)
                
                if candidate.get("quote_status") == "VALID":
                    # 2. Economics
                    candidate = strategy.evaluate_economics(candidate)
                    
                # 3. Risk Eval
                risk_eval = risk.evaluate_opportunity(candidate)
                if risk_eval["status"] != "RISK_PASSED":
                    candidate["failure_code"] = risk_eval["reason"]
                    
                # 4. Pipeline execution
                final_state = state_machine.process_opportunity(candidate)
                
                # 5. Log Evidence
                knowledge.record_evidence(opp_id, final_state, ["LIVE_CHAIN"])

    knowledge.dump_evidence("PFLC_5.2_Evidence_Manifest.json")
    print("Mission Complete. Manifest written.")

if __name__ == "__main__":
    run_mission()
