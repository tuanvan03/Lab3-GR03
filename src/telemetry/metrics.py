import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(usage) # Mock cost calculation
        }
        self.session_metrics.append(metric)
        print(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        input_cost = (usage.get("prompt_tokens", 0) / 1000000) * 0.241
        output_cost = (usage.get("completion_tokens", 0) / 1000000) * 2.5
        return input_cost + output_cost

# Global tracker instance
tracker = PerformanceTracker()
