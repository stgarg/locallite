"""
Shared Metrics Service
Usage analytics and performance monitoring shared across endpoints
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Literal

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request"""

    endpoint_type: Literal["human", "agent"]
    operation: str  # embeddings, chat, batch
    response_size_bytes: int
    latency_ms: float
    timestamp: float
    success: bool
    model_used: str
    provider_used: str
    tokens_processed: int


@dataclass
class ServiceMetrics:
    """Aggregated service metrics"""

    start_time: float = field(default_factory=time.time)
    human_requests: int = 0
    agent_requests: int = 0
    total_requests: int = 0

    # Performance tracking
    total_latency_ms: float = 0
    total_response_bytes: int = 0
    total_tokens_processed: int = 0

    # Provider usage
    npu_requests: int = 0
    cpu_requests: int = 0

    # Error tracking
    failed_requests: int = 0

    # Bandwidth savings calculation
    agent_bandwidth_saved_bytes: int = 0  # Estimated savings vs human endpoints


class MetricsService:
    """
    Performance monitoring & analytics service

    Tracks usage patterns that distinguish between human and agent traffic
    Calculates bandwidth savings and performance improvements
    """

    def __init__(self):
        self.metrics = ServiceMetrics()
        self._lock = threading.Lock()

    async def track_request(
        self,
        endpoint_type: Literal["human", "agent"],
        operation: str,
        response_size_bytes: int,
        latency_ms: float,
        success: bool = True,
        model_used: str = "unknown",
        provider_used: str = "unknown",
        tokens_processed: int = 0,
    ):
        """
        Track a single request with comprehensive metrics

        Args:
            endpoint_type: Whether request came from human or agent endpoint
            operation: Type of operation (embeddings, chat, batch)
            response_size_bytes: Size of the response payload
            latency_ms: Request processing time in milliseconds
            success: Whether the request succeeded
            model_used: Model that processed the request
            provider_used: Compute provider (NPU, CPU)
            tokens_processed: Number of tokens processed
        """
        with self._lock:
            # Basic request counting
            self.metrics.total_requests += 1
            if endpoint_type == "human":
                self.metrics.human_requests += 1
            else:
                self.metrics.agent_requests += 1

            # Performance tracking
            self.metrics.total_latency_ms += latency_ms
            self.metrics.total_response_bytes += response_size_bytes
            self.metrics.total_tokens_processed += tokens_processed

            # Provider tracking
            if provider_used.lower() == "npu":
                self.metrics.npu_requests += 1
            else:
                self.metrics.cpu_requests += 1

            # Error tracking
            if not success:
                self.metrics.failed_requests += 1

            # Calculate bandwidth savings for agent requests
            if endpoint_type == "agent" and success:
                # Estimate bandwidth savings vs equivalent human endpoint
                # Agent endpoints typically save 50-60% bandwidth
                estimated_human_size = response_size_bytes * 2.2  # Rough multiplier
                savings = estimated_human_size - response_size_bytes
                self.metrics.agent_bandwidth_saved_bytes += max(0, int(savings))

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics including human vs agent usage stats

        Returns:
            Dictionary with detailed metrics and calculated insights
        """
        with self._lock:
            uptime_seconds = time.time() - self.metrics.start_time

            # Calculate rates and percentages
            total_requests = self.metrics.total_requests
            if total_requests == 0:
                return {
                    "status": "no_data",
                    "uptime_seconds": uptime_seconds,
                    "message": "No requests processed yet",
                }

            avg_latency_ms = self.metrics.total_latency_ms / total_requests
            avg_response_size_bytes = self.metrics.total_response_bytes / total_requests
            requests_per_minute = (
                (total_requests / uptime_seconds) * 60 if uptime_seconds > 0 else 0
            )

            # Human vs Agent breakdown
            agent_adoption_pct = (self.metrics.agent_requests / total_requests) * 100
            human_adoption_pct = (self.metrics.human_requests / total_requests) * 100

            # Provider usage
            npu_usage_pct = (self.metrics.npu_requests / total_requests) * 100

            # Error rates
            error_rate_pct = (self.metrics.failed_requests / total_requests) * 100
            success_rate_pct = 100 - error_rate_pct

            # Bandwidth calculations
            bandwidth_saved_mb = self.metrics.agent_bandwidth_saved_bytes / (
                1024 * 1024
            )
            total_bandwidth_mb = self.metrics.total_response_bytes / (1024 * 1024)

            return {
                "overview": {
                    "uptime_seconds": uptime_seconds,
                    "total_requests": total_requests,
                    "requests_per_minute": round(requests_per_minute, 2),
                    "success_rate_pct": round(success_rate_pct, 2),
                    "avg_latency_ms": round(avg_latency_ms, 2),
                },
                "audience_breakdown": {
                    "human_requests": self.metrics.human_requests,
                    "agent_requests": self.metrics.agent_requests,
                    "human_adoption_pct": round(human_adoption_pct, 1),
                    "agent_adoption_pct": round(agent_adoption_pct, 1),
                },
                "performance": {
                    "npu_requests": self.metrics.npu_requests,
                    "cpu_requests": self.metrics.cpu_requests,
                    "npu_usage_pct": round(npu_usage_pct, 1),
                    "total_tokens_processed": self.metrics.total_tokens_processed,
                    "avg_response_size_bytes": int(avg_response_size_bytes),
                },
                "bandwidth_optimization": {
                    "agent_bandwidth_saved_mb": round(bandwidth_saved_mb, 2),
                    "total_bandwidth_mb": round(total_bandwidth_mb, 2),
                    "bandwidth_savings_pct": round(
                        (bandwidth_saved_mb / max(total_bandwidth_mb, 0.001)) * 100, 1
                    ),
                },
                "errors": {
                    "failed_requests": self.metrics.failed_requests,
                    "error_rate_pct": round(error_rate_pct, 2),
                },
            }

    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get condensed summary statistics"""
        analytics = await self.get_analytics()

        if analytics.get("status") == "no_data":
            return analytics

        return {
            "total_requests": analytics["overview"]["total_requests"],
            "human_requests": analytics["audience_breakdown"]["human_requests"],
            "agent_requests": analytics["audience_breakdown"]["agent_requests"],
            "agent_adoption_pct": analytics["audience_breakdown"]["agent_adoption_pct"],
            "bandwidth_saved_mb": analytics["bandwidth_optimization"][
                "agent_bandwidth_saved_mb"
            ],
            "npu_usage_pct": analytics["performance"]["npu_usage_pct"],
            "success_rate_pct": analytics["overview"]["success_rate_pct"],
            "avg_latency_ms": analytics["overview"]["avg_latency_ms"],
        }

    def reset_metrics(self):
        """Reset all metrics (useful for testing or periodic resets)"""
        with self._lock:
            self.metrics = ServiceMetrics()
            logger.info("📊 Metrics reset")

    def health_check(self) -> Dict[str, Any]:
        """Health check for metrics service"""
        try:
            uptime = time.time() - self.metrics.start_time
            return {
                "status": "healthy",
                "uptime_seconds": uptime,
                "total_requests": self.metrics.total_requests,
                "tracking_active": True,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
