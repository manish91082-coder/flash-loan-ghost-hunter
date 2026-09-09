import time
import logging
from typing import Dict, Any, Optional

class RPCHealthMonitor:
    """
    Monitors RPC provider health, rate limits, and latency.
    """
    def __init__(self):
        self.providers: Dict[str, Dict[str, Any]] = {}
        
    def register_provider(self, url: str):
        if url not in self.providers:
            self.providers[url] = {
                "requests": 0,
                "successes": 0,
                "timeouts": 0,
                "429s": 0,
                "401s": 0,
                "403s": 0,
                "reverts": 0,
                "latency_ms": 0.0,
                "latest_successful_block": None,
                "banned_until": 0
            }
            
    def record_attempt(self, url: str):
        self.register_provider(url)
        self.providers[url]["requests"] += 1
        
    def record_success(self, url: str, latency: float, block: Optional[int] = None):
        self.providers[url]["successes"] += 1
        self.providers[url]["latency_ms"] = latency
        if block:
            self.providers[url]["latest_successful_block"] = block
            
    def record_failure(self, url: str, error_type: str, retry_after: int = 5):
        self.register_provider(url)
        if error_type in ["429", "timeout", "500", "502", "503"]:
            self.providers[url][f"{error_type}s" if error_type != "timeout" else "timeouts"] += 1
            self.providers[url]["banned_until"] = time.time() + retry_after
        elif error_type in ["401", "403"]:
            self.providers[url][f"{error_type}s"] += 1
            self.providers[url]["banned_until"] = time.time() + 3600  # Ban for 1 hour
        elif error_type == "revert":
            self.providers[url]["reverts"] += 1
            
    def is_provider_healthy(self, url: str) -> bool:
        if url not in self.providers:
            return True
        return time.time() > self.providers[url]["banned_until"]

def calculate_quote_age_ms(quote_block_timestamp: int, current_block_timestamp: int) -> int:
    """
    Calculates quote age explicitly based on block timestamps (in seconds), 
    converted to ms.
    """
    return max(0, (current_block_timestamp - quote_block_timestamp) * 1000)
