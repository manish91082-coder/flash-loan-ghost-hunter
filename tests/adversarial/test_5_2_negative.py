import unittest
from execution.state_machine import StateMachine
from agents.risk import RiskAgent
from economics.precise_math import PreciseMath

class TestNegativeControls(unittest.TestCase):
    def setUp(self):
        self.state_machine = StateMachine()
        self.risk_agent = RiskAgent()

    def test_stale_quote_rejection(self):
        data = {"quote_status": "VALID", "quote_age_ms": 10000, "net_pnl": 500}
        res = self.risk_agent.evaluate_opportunity(data)
        self.assertEqual(res["status"], "RISK_REJECTED")
        self.assertEqual(res["reason"], "STALE_QUOTE")

    def test_float_math_rejection(self):
        data = {"quote_status": "VALID", "quote_age_ms": 100, "net_pnl": 500.5}
        res = self.risk_agent.evaluate_opportunity(data)
        self.assertEqual(res["status"], "RISK_REJECTED")
        self.assertEqual(res["reason"], "FLOAT_DETECTED")

    def test_unprofitable_rejection(self):
        data = {"quote_status": "VALID", "quote_age_ms": 100, "net_pnl": -10}
        res = self.risk_agent.evaluate_opportunity(data)
        self.assertEqual(res["status"], "RISK_REJECTED")
        self.assertEqual(res["reason"], "UNPROFITABLE")
        
    def test_pipeline_abort_on_missing_data(self):
        opp_data = {"failure_code": "DATA_ERROR"}
        res = self.state_machine.process_opportunity(opp_data)
        self.assertEqual(res["final_status"], "DATA_ERROR")
        self.assertIn("ABORT", res["pipeline_history"])

if __name__ == '__main__':
    unittest.main()
