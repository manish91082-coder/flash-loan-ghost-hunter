from decimal import Decimal, getcontext
import logging

getcontext().prec = 78

class PreciseMath:
    """
    Enforces strict precision mathematics.
    Forbids floating-point math across all financial calculations.
    """
    @staticmethod
    def calculate_net_profit(borrow_amount_wei: int, amount_out_wei: int, flash_fee_wei: int, gas_cost_wei: int) -> int:
        if any(isinstance(x, float) for x in [borrow_amount_wei, amount_out_wei, flash_fee_wei, gas_cost_wei]):
            raise ValueError("[PreciseMath] Floating point passed to economic engine.")
            
        gross_profit = amount_out_wei - borrow_amount_wei
        total_costs = flash_fee_wei + gas_cost_wei
        net = gross_profit - total_costs
        return net
        
    @staticmethod
    def calculate_flash_fee(borrow_amount_wei: int, fee_bips: int = 5) -> int:
        # Default 0.05% for Aave V3 = 5 bips
        return (borrow_amount_wei * fee_bips) // 10000
