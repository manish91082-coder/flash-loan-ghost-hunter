import math

class UniV2MarketModel:
    def __init__(self, fee_bips=30):
        """
        :param fee_bips: Fee in basis points (e.g., 30 = 0.3%)
        """
        self.fee_bips = fee_bips
        self.fee_multiplier = 10000 - fee_bips

    def get_amount_out(self, amount_in, reserve_in, reserve_out):
        """
        Calculates exact amount out for a UniV2 swap.
        """
        if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
            return 0
            
        amount_in_with_fee = amount_in * self.fee_multiplier
        numerator = amount_in_with_fee * reserve_out
        denominator = (reserve_in * 10000) + amount_in_with_fee
        
        return numerator // denominator

    def get_optimal_arbitrage_input(self, reserve1_in, reserve1_out, reserve2_in, reserve2_out):
        """
        Calculates the optimal input amount for a spatial arbitrage between two UniV2 pools.
        Assumes token path: TokenA -> TokenB (Pool 1) -> TokenA (Pool 2)
        :param reserve1_in: Reserve of Token A in Pool 1
        :param reserve1_out: Reserve of Token B in Pool 1
        :param reserve2_in: Reserve of Token B in Pool 2
        :param reserve2_out: Reserve of Token A in Pool 2
        :return: Optimal input amount of Token A
        """
        if reserve1_in <= 0 or reserve1_out <= 0 or reserve2_in <= 0 or reserve2_out <= 0:
            return 0

        # Based on x*y=k arbitrage mathematics (assuming 0.3% fee for both for simplicity)
        fee = self.fee_multiplier / 10000.0
        
        # We need to maximize: out2 - in1
        # out1 = (in1 * fee * r1_out) / (r1_in + in1 * fee)
        # out2 = (out1 * fee * r2_out) / (r2_in + out1 * fee)
        # We find the root of the derivative wrt in1.
        
        r1_in = float(reserve1_in)
        r1_out = float(reserve1_out)
        r2_in = float(reserve2_in)
        r2_out = float(reserve2_out)

        # To avoid complex floating point edge cases, we use the standard UniV2 optimal arb formula:
        # a = fee^2 * r1_out * r2_out
        # b = fee * r1_out * r2_in
        # c = r1_in * r2_in
        # optimal_in = (sqrt(a * c) - c) / (fee * b + fee * c)   (Approximate, needs exact derivation)

        # Exact derivation:
        # Let a = fee * r1_out, b = r1_in
        # Let c = fee * r2_out, d = r2_in
        # f(x) = (a * c * x) / (b * d + (a * d + b * c) * x)
        # We want to maximize f(x) - x
        # d/dx (f(x) - x) = 0 => a*b*c*d / (b*d + (a*d+b*c)*x)^2 = 1
        # => x = (sqrt(a*b*c*d) - b*d) / (a*d + b*c)
        
        a = fee * r1_out
        b = r1_in
        c = fee * r2_out
        d = r2_in
        
        numerator = math.sqrt(a * b * c * d) - (b * d)
        denominator = (a * d) + (b * c)
        
        if denominator == 0:
            return 0
            
        optimal_in = numerator / denominator
        
        if optimal_in <= 0:
            return 0
            
        return int(optimal_in)
