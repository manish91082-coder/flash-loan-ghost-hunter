import time

class RiskEngine:
    def __init__(self, max_slippage_bips=50, quote_freshness_seconds=10):
        """
        :param max_slippage_bips: Maximum allowed slippage (e.g. 50 bips = 0.5%)
        :param quote_freshness_seconds: Quotes older than this are rejected.
        """
        self.max_slippage_bips = max_slippage_bips
        self.quote_freshness_seconds = quote_freshness_seconds

    def check_quote_freshness(self, timestamp):
        if time.time() - timestamp > self.quote_freshness_seconds:
            return False, "Quote is too stale for execution"
        return True, "Quote is fresh"
        
    def calculate_min_amount_out(self, expected_amount_out):
        """
        Calculates the minimum amount out to be enforced by the smart contract to protect against MEV/sandwiching.
        """
        slippage_multiplier = 10000 - self.max_slippage_bips
        min_amount_out = (expected_amount_out * slippage_multiplier) // 10000
        return min_amount_out

    def validate_execution_path(self, profit_wei, is_profitable):
        if not is_profitable or profit_wei <= 0:
            return False, "Opportunity is not profitable after net fee accounting"
            
        return True, "Execution path validated"

