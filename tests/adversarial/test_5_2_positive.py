import unittest
from execution.state_machine import StateMachine
from execution.agent import ExecutionAgent
from agents.risk import RiskAgent

class TestPositiveControls(unittest.TestCase):
    def setUp(self):
        self.state_machine = StateMachine()
        self.risk = RiskAgent()
        self.executor = ExecutionAgent()

    def test_golden_path_execution(self):
        """
        Proves the engine CAN reach RECONCILED state when fed perfect data.
        """
        # 1. Provide perfect quote
        opp_data = {
            "opportunity_id": "GOLDEN-TEST",
            "chain_id": 1,
            "strategy": "Spatial",
            "token_in": "0xWETH",
            "amount_in": 10**18,
            "quote_out": int(1.1 * 10**18),
            "estimated_gas": 150000,
            "net_pnl": int(0.08 * 10**18),
            "quote_status": "VALID",
            "quote_age_ms": 100,
            "execution_clearance": "LIVE_EXECUTION_READY",
            "is_safe": True
        }
        
        # 2. Pass risk
        risk_res = self.risk.evaluate_opportunity(opp_data)
        self.assertEqual(risk_res["status"], "RISK_PASSED")
        
        # 3. Pipeline execution
        opp_data["final_status"] = "RECONCILED" # Simulated successful callback
        res = self.state_machine.process_opportunity(opp_data)
        
        self.assertEqual(res["final_status"], "RECONCILED")
        self.assertIn("RECONCILE", res["pipeline_history"])
        self.assertNotIn("ABORT", res["pipeline_history"])

if __name__ == '__main__':
    unittest.main()
