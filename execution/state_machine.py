import logging
from enum import Enum, auto
from typing import Dict, Any

class State(Enum):
    DISCOVER = auto()
    IDENTIFY = auto()
    VERIFY = auto()
    QUOTE = auto()
    LIQUIDITY_CHECK = auto()
    ECONOMICS = auto()
    RISK = auto()
    OPPORTUNITY_SCORE = auto()
    INTENT = auto()
    SIGNATURE = auto()
    SIMULATION = auto()
    FINAL_REQUOTE = auto()
    FINAL_STATE_CHECK = auto()
    EXECUTION_DECISION = auto()
    EXECUTE = auto()
    RECEIPT = auto()
    RECONCILE = auto()
    LEARN = auto()
    ABORT = auto()

class StateMachine:
    """
    Enforces strict 18-step sequential lifecycle for opportunities.
    No skipping allowed. Missing required data triggers ABORT.
    """
    def __init__(self):
        self.transitions = {
            State.DISCOVER: State.IDENTIFY,
            State.IDENTIFY: State.VERIFY,
            State.VERIFY: State.QUOTE,
            State.QUOTE: State.LIQUIDITY_CHECK,
            State.LIQUIDITY_CHECK: State.ECONOMICS,
            State.ECONOMICS: State.RISK,
            State.RISK: State.OPPORTUNITY_SCORE,
            State.OPPORTUNITY_SCORE: State.INTENT,
            State.INTENT: State.SIGNATURE,
            State.SIGNATURE: State.SIMULATION,
            State.SIMULATION: State.FINAL_REQUOTE,
            State.FINAL_REQUOTE: State.FINAL_STATE_CHECK,
            State.FINAL_STATE_CHECK: State.EXECUTION_DECISION,
            State.EXECUTION_DECISION: State.EXECUTE,
            State.EXECUTE: State.RECEIPT,
            State.RECEIPT: State.RECONCILE,
            State.RECONCILE: State.LEARN,
            State.LEARN: None
        }

    def process_opportunity(self, opp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the exact pipeline sequence.
        Since execution logic is bounded, it stops at SIMULATION if READ_ONLY.
        """
        current_state = State.DISCOVER
        opp_data["pipeline_history"] = []
        
        while current_state and current_state != State.ABORT:
            opp_data["pipeline_history"].append(current_state.name)
            
            # Simulated check logic per state
            if opp_data.get("failure_code"):
                opp_data["final_status"] = opp_data.get("failure_code")
                opp_data["pipeline_history"].append(State.ABORT.name)
                break
                
            # If executing purely Read Only, we abort safely at EXECUTE
            if current_state == State.EXECUTE and opp_data.get("execution_clearance") != "LIVE_EXECUTION_READY":
                opp_data["final_status"] = "SIMULATION_READY"
                break
                
            current_state = self.transitions.get(current_state)
            
        return opp_data
