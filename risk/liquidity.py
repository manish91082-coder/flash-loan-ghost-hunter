class LiquidityModel:
    def __init__(self, max_utilization_bips=1000): # max 10% pool utilization
        self.max_utilization_bips = max_utilization_bips

    def get_executable_size(self, reserve_in, reserve_out, requested_flash_loan):
        """
        Determines if the pool can absorb the flash loan without exceeding the utilization limit.
        """
        max_allowed_in = (reserve_in * self.max_utilization_bips) // 10000
        
        executable_size = min(requested_flash_loan, max_allowed_in)
        
        is_safe = executable_size >= requested_flash_loan
        
        return executable_size, is_safe
