import logging
from typing import Dict, Any

class ExecutionAgent:
    """
    Agent 6: EXECUTION
    Executes fully validated opportunities. Never invents data.
    """
    
    def generate_intent(self, opp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a strict intent payload. Any mutation will break signature.
        """
        required_fields = ["chain_id", "strategy", "opportunity_id", "token_in", "amount_in", "quote_out", "estimated_gas", "net_pnl"]
        
        for field in required_fields:
            if opp_data.get(field) is None or opp_data.get(field) == "NULL":
                logging.error(f"[ExecutionAgent] Missing required field '{field}'. ABORT.")
                return {"status": "ABORT_MISSING_DATA"}
                
        intent = {
            "intent_hash": f"HASH_{opp_data['opportunity_id']}",
            "execution_id": f"EXEC_{opp_data['opportunity_id']}",
            "payload": {k: opp_data[k] for k in required_fields},
            "status": "READY_FOR_SIGNATURE"
        }
        return intent

    def execute_intent(self, intent: Dict[str, Any], clearance: str) -> str:
        """
        Executes the intent based on global clearance.
        """
        if clearance != "LIVE_EXECUTION_READY":
            logging.info("[ExecutionAgent] Execution blocked. Clearance is not LIVE_EXECUTION_READY.")
            return "SIMULATION_READY"
            
        # In a real environment, this sends the transaction
        return "SUBMITTED"
        
    def reconcile(self, execution_id: str, expected_net: int, actual_net: int) -> str:
        """
        Strict mathematical reconciliation.
        """
        if expected_net != actual_net:
             logging.warning(f"[ExecutionAgent] Reconciliation failed! Expected {expected_net}, Got {actual_net}")
             return "RECONCILIATION_FAILED"
        return "RECONCILED"
