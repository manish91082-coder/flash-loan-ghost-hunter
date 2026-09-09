class FinalityEngine:
    def __init__(self, rpc_fallback_manager, max_acceptable_drift_blocks=2):
        self.rpc = rpc_fallback_manager
        self.max_drift = max_acceptable_drift_blocks

    def pre_broadcast_revalidation(self, original_quote_block):
        """
        Immediately before execution, checks if the chain has drifted significantly
        or if a reorg invalidated the original quote snapshot.
        """
        current_block = self.rpc.w3.eth.block_number
        
        drift = current_block - original_quote_block
        
        if drift < 0:
            return False, f"Reorg detected. Original quote block {original_quote_block} is ahead of current block {current_block}."
            
        if drift > self.max_drift:
            return False, f"State stale. Drift {drift} exceeds max {self.max_drift} blocks."
            
        return True, "State valid for execution."
