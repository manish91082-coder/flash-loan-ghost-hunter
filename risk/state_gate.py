class StateConsistencyGate:
    def __init__(self, max_block_drift=1):
        """
        Ensures that quotes fetched from multiple DEXs/RPCs are within 
        an acceptable block drift of each other.
        """
        self.max_block_drift = max_block_drift

    def validate_quotes(self, quote_a_block, quote_b_block):
        """
        Validates if two quotes belong to compatible state snapshots.
        :param quote_a_block: Block number for Quote A
        :param quote_b_block: Block number for Quote B
        :return: (is_consistent, message)
        """
        drift = abs(quote_a_block - quote_b_block)
        if drift > self.max_block_drift:
            return False, f"State inconsistency detected. Block drift: {drift} (Max allowed: {self.max_block_drift})"
        return True, "State consistent."
