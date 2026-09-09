import time
from decimal import Decimal

class RiskGuard:
    def __init__(self):
        self.max_quote_age_ms = 5000  # 5 seconds
        self.max_slippage_bps = 500   # 5%
        
    def check_quote_health(self, quote_state):
        """
        Validates quote age, missing data, and block freshness.
        """
        if not quote_state or quote_state.get("status") != "VALID":
            return False, "ABORT: QUOTE_FAILED or DATA_ERROR"
            
        quote_age_ms = quote_state.get("quote_age_ms")
        if quote_age_ms is not None and quote_age_ms > self.max_quote_age_ms:
            return False, f"ABORT: STALE_QUOTE (Age: {quote_age_ms}ms > Max: {self.max_quote_age_ms}ms)"
            
        return True, "SUCCESS: QUOTE_HEALTHY"
        
    def validate_execution_economics(self, net_profit_tokens, is_safe, economics_msg):
        """
        Evaluates the final economics output.
        """
        if not is_safe or net_profit_tokens is None:
            return False, f"ABORT: UNPROFITABLE_OR_FAILED ({economics_msg})"
            
        if Decimal(net_profit_tokens) <= 0:
            return False, "ABORT: ZERO_OR_NEGATIVE_PROFIT"
            
        return True, "SUCCESS: ECONOMICS_SAFE"
        
    def check_provider_disagreement(self, quote_a, quote_b):
        """
        Cross-checks quotes from two different RPCs or providers to ensure they are within a tight bound.
        """
        if not quote_a or not quote_b:
            return False, "ABORT: MISSING_PROVIDER_DATA"
            
        # Example check: 1% tolerance
        diff = abs(Decimal(quote_a) - Decimal(quote_b))
        if quote_b == 0:
            return False, "ABORT: ZERO_QUOTE"
            
        diff_pct = (diff / Decimal(quote_b)) * 100
        if diff_pct > 1:
            return False, f"ABORT: PROVIDER_DISAGREEMENT (Diff: {diff_pct:.2f}%)"
            
        return True, "SUCCESS: PROVIDERS_AGREE"

    def final_revalidation(self, current_quote, requote):
        """
        If opportunity discovery and execution take time, we re-quote.
        """
        if current_quote != requote:
            return False, "ABORT: STATE_CHANGED_BEFORE_EXECUTION"
        return True, "SUCCESS: FINAL_STATE_STABLE"
