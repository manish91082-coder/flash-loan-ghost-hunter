import os
import sys
import unittest
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from economics.profit_calculator import ProfitCalculator
from risk.risk_guard import RiskGuard
from execution.pipeline import ExecutionPipeline

class DummyFlashProvider:
    def calculate_premium(self, amt):
        return amt * 5 // 10000

class TestNegativeControls(unittest.TestCase):
    def setUp(self):
        self.risk_guard = RiskGuard()
        self.profit_calc = ProfitCalculator(DummyFlashProvider())
        self.pipeline = ExecutionPipeline(self.risk_guard, self.profit_calc)
        self.base_opp = {
            "chain_id": 8453,
            "strategy": "Spatial",
            "quote_status": "VALID",
            "liquidity_sufficient": True,
            "net_profit": 10000,
            "is_safe": True,
            "simulation_passed": True,
            "final_requote_match": True
        }

    def test_rpc_zero_response(self):
        """Test that missing quote data results in NULL PnL and proper abortion"""
        # final_amount = None (quote failed)
        net_profit_tokens, is_safe, msg = self.profit_calc.calculate_net_profit(1000, None, 150000)
        self.assertIsNone(net_profit_tokens)
        self.assertFalse(is_safe)
        self.assertIn("QUOTE_FAILED", msg)

    def test_stale_quote_abort(self):
        """Test that quotes exceeding max age trigger Risk Guard abortion"""
        quote_state = {"status": "VALID", "quote_age_ms": 6000}
        passed, msg = self.risk_guard.check_quote_health(quote_state)
        self.assertFalse(passed)
        self.assertIn("STALE_QUOTE", msg)

    def test_provider_disagreement(self):
        """Test that differing quotes from RPCs trigger abortion"""
        # 1.5% difference
        quote_a = 10150
        quote_b = 10000
        passed, msg = self.risk_guard.check_provider_disagreement(quote_a, quote_b)
        self.assertFalse(passed)
        self.assertIn("PROVIDER_DISAGREEMENT", msg)

    def test_simulation_revert(self):
        """Test pipeline correctly aborts if simulation fails"""
        opp = dict(self.base_opp)
        opp["simulation_passed"] = False
        res = self.pipeline.run_pipeline(opp)
        self.assertEqual(res["final_status"], "SIMULATION_FAILED")
        
    def test_pipeline_zero_loss_aborted(self):
        """Test pipeline correctly aborts if economics fail"""
        opp = dict(self.base_opp)
        opp["net_profit"] = -500
        opp["is_safe"] = False
        res = self.pipeline.run_pipeline(opp)
        self.assertEqual(res["final_status"], "RISK_REJECTED")

if __name__ == "__main__":
    unittest.main()
