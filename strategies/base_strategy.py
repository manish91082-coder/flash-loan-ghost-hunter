from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseStrategy(ABC):
    """
    Abstract base for all strategies. Ensures each strategy implements 
    its own unique discovery, market extraction, and validation logic.
    """
    
    @abstractmethod
    def discover_opportunities(self, discovery_engine) -> List[Dict[str, Any]]:
        """
        Scan and discover strategy-specific candidates using the dynamic discovery engine.
        """
        pass
        
    @abstractmethod
    def extract_market_state(self, candidate: Dict[str, Any], rpc_manager) -> Dict[str, Any]:
        """
        Extract market state specific to this strategy 
        (e.g., dual-venue quotes for Spatial, three-legged quotes for Triangular).
        """
        pass
        
    @abstractmethod
    def evaluate_economics(self, state: Dict[str, Any], profit_calc) -> Dict[str, Any]:
        """
        Calculate precise economics strictly based on the extracted state.
        """
        pass

    @abstractmethod
    def build_intent(self, state: Dict[str, Any], intent_builder) -> Dict[str, Any]:
        """
        Build the verifiable EIP-712 execution intent mapping directly to the opportunity state.
        """
        pass
