import time
import os
import json
import traceback

from economics.flash_loan import load_chain_config
from quote_engine.rpc_fetcher import RPCFallbackManager
from execution.discovery_engine import DiscoveryEngine
from execution.pipeline import ExecutionPipeline
from risk.risk_guard import RiskGuard
from economics.profit_calculator import ProfitCalculator
from execution.intent import ExecutionIntentBuilder

# Import all strategies
from strategies.spatial import SpatialArbitrage
from strategies.triangular import TriangularArbitrage
from strategies.statistical import StatisticalArbitrage
from strategies.yield_strat import YieldArbitrage
from strategies.crosschain import CrossChainArbitrage
from strategies.mev import SandwichMEV

class AutonomousLifecycleDaemon:
    def __init__(self, private_key=None, verifying_contract=None):
        self.private_key = private_key or os.getenv("PHANTOMX_PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("CRITICAL: No private key provided in environment. Failing closed.")
            
        self.chain_config = load_chain_config()
        self.verifying_contract = verifying_contract or os.getenv("PHANTOMX_EXECUTOR_CONTRACT")
        if not self.verifying_contract:
            raise ValueError("CRITICAL: No Executor Contract address provided in environment.")
            
        # We need a dummy provider to init the base pipeline objects; real providers injected per-opportunity
        class DummyBaseProvider:
            def calculate_premium(self, amt): return 0
            
        self.risk_guard = RiskGuard()
        self.base_profit_calc = ProfitCalculator(DummyBaseProvider())
        self.pipeline = ExecutionPipeline(self.risk_guard, self.base_profit_calc)
        
        # Initialize 6 Strategies
        self.strategies = {
            "Spatial": SpatialArbitrage(None, None, self.base_profit_calc),
            "Triangular": TriangularArbitrage(),
            "Statistical": StatisticalArbitrage(),
            "Yield": YieldArbitrage(),
            "CrossChain": CrossChainArbitrage(global_config=self.chain_config),
            "Sandwich": SandwichMEV()
        }

    def start_daemon(self, iterations=1):
        """
        Runs the continuous 8-chain x 6-strategy saturation loop.
        """
        print("[DAEMON] Initializing Universal Discovery & Execution Daemon")
        
        count = 0
        while count < iterations:
            count += 1
            print(f"\n--- [DAEMON] Global Iteration {count} ---")
            
            for chain_id_str, config in self.chain_config.items():
                if not isinstance(config, dict) or "chain_id" not in config:
                    continue
                chain_id = int(chain_id_str)
                self._scan_chain(chain_id, config)
                
            print(f"--- [DAEMON] Global Iteration {count} Complete. Resting for next block ---")
            if count < iterations:
                time.sleep(1)

    def _scan_chain(self, chain_id, config):
        print(f"\n[SCAN] Executing Discovery on Chain: {config.get('name')} ({chain_id})")
        
        try:
            rpc_manager = RPCFallbackManager(config.get("rpc_urls", []), chain_id)
            discovery_engine = DiscoveryEngine(rpc_manager, config)
            
            for strat_name, strategy in self.strategies.items():
                print(f"  -> Applying Strategy: {strat_name}")
                self._execute_strategy(chain_id, config, rpc_manager, discovery_engine, strat_name, strategy)
                
        except Exception as e:
            print(f"[SCAN ERROR] Failed on {config.get('name')}: {e}")

    def _execute_strategy(self, chain_id, config, rpc_manager, discovery_engine, strat_name, strategy):
        try:
            # 1. Discover Candidates
            candidates = strategy.discover_opportunities(discovery_engine)
            if not candidates:
                print(f"    [Strategy:{strat_name}] NO_QUALIFIED_OPPORTUNITY (No Candidates)")
                return
                
            for candidate in candidates:
                # 2. Extract Market State
                state = strategy.extract_market_state(candidate, rpc_manager)
                if state.get("status") != "VALID":
                    print(f"    [Strategy:{strat_name}] MARKET_EXTRACTION_FAILED: {state.get('failure_code')}")
                    continue
                    
                # 3. Evaluate Economics
                econ_state = strategy.evaluate_economics(state, self.base_profit_calc)
                if not econ_state.get("is_safe"):
                    print(f"    [Strategy:{strat_name}] NO_QUALIFIED_OPPORTUNITY (Unprofitable)")
                    continue
                    
                # 4. Build Intent
                intent_builder = ExecutionIntentBuilder(self.private_key, self.verifying_contract, chain_id)
                final_opp = strategy.build_intent(econ_state, intent_builder)
                if not final_opp:
                    print(f"    [Strategy:{strat_name}] INTENT_BUILD_FAILED")
                    continue
                    
                # 5. Hand over to General Pipeline
                print(f"    [Strategy:{strat_name}] OPPORTUNITY VERIFIED! Passing to Pipeline...")
                final_opp["rpc_manager"] = rpc_manager
                final_opp["signer"] = intent_builder.account
                final_opp["verifying_contract"] = self.verifying_contract
                final_opp["execution_mode"] = os.getenv("EXECUTION_MODE", "READ_ONLY")
                
                self.pipeline.run_pipeline(final_opp)
                
                # We execute at most one valid opportunity per strategy per cycle to manage RPC load
                break
                
        except Exception as e:
            print(f"    [Strategy:{strat_name}] ERROR: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    daemon = AutonomousLifecycleDaemon()
    print("Daemon initialized and ready for fully dynamic execution.")
