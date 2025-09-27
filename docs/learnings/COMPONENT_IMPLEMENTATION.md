# FastEmbed Component Implementation Design

## 🏗️ Core Component Implementation Specifications

This document provides detailed implementation designs for the key components identified in our main architecture. Each component includes specific algorithms, data structures, configuration options, and integration patterns.

---

## 1. 🚀 Model Warmup Manager

### 1.1 Detailed Implementation

```python
from typing import Dict, List, Optional, Tuple
import asyncio
import time
from dataclasses import dataclass
from collections import defaultdict, deque
import numpy as np

@dataclass
class UsagePattern:
    model_id: str
    hour_of_day: int
    day_of_week: int
    request_count: int
    avg_latency: float
    timestamp: float

@dataclass
class WarmupPrediction:
    model_id: str
    probability: float
    confidence: float
    time_window: str
    reasoning: str

class UsagePredictor:
    """
    Machine learning-based predictor for model usage patterns.
    Uses time-series analysis and pattern recognition.
    """
    
    def __init__(self, history_window_hours: int = 168):  # 1 week
        self.history_window = history_window_hours
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.daily_patterns: Dict[str, np.ndarray] = {}
        self.weekly_patterns: Dict[str, np.ndarray] = {}
        
    def record_usage(self, model_id: str, timestamp: float, latency: float):
        """Record model usage for pattern learning."""
        pattern = UsagePattern(
            model_id=model_id,
            hour_of_day=time.localtime(timestamp).tm_hour,
            day_of_week=time.localtime(timestamp).tm_wday,
            request_count=1,
            avg_latency=latency,
            timestamp=timestamp
        )
        self.usage_history[model_id].append(pattern)
        
    def _analyze_hourly_patterns(self, model_id: str) -> np.ndarray:
        """Analyze usage patterns by hour of day."""
        hourly_usage = np.zeros(24)
        history = self.usage_history[model_id]
        
        for pattern in history:
            hourly_usage[pattern.hour_of_day] += pattern.request_count
            
        # Normalize to probabilities
        total = hourly_usage.sum()
        return hourly_usage / total if total > 0 else hourly_usage
    
    def _analyze_weekly_patterns(self, model_id: str) -> np.ndarray:
        """Analyze usage patterns by day of week."""
        weekly_usage = np.zeros(7)
        history = self.usage_history[model_id]
        
        for pattern in history:
            weekly_usage[pattern.day_of_week] += pattern.request_count
            
        total = weekly_usage.sum()
        return weekly_usage / total if total > 0 else weekly_usage
    
    async def predict_next_hour(self) -> Dict[str, WarmupPrediction]:
        """Predict which models will be needed in the next hour."""
        predictions = {}
        current_time = time.time()
        current_hour = time.localtime(current_time).tm_hour
        current_day = time.localtime(current_time).tm_wday
        
        for model_id in self.usage_history.keys():
            # Analyze patterns
            hourly_pattern = self._analyze_hourly_patterns(model_id)
            weekly_pattern = self._analyze_weekly_patterns(model_id)
            
            # Calculate probability based on patterns
            hour_probability = hourly_pattern[current_hour]
            day_probability = weekly_pattern[current_day]
            
            # Combine probabilities with weights
            combined_probability = (hour_probability * 0.7 + day_probability * 0.3)
            
            # Calculate confidence based on data volume
            data_points = len(self.usage_history[model_id])
            confidence = min(data_points / 100.0, 1.0)  # Max confidence at 100+ data points
            
            # Generate reasoning
            reasoning = f"Hour:{hour_probability:.2f}, Day:{day_probability:.2f}, Data:{data_points}"
            
            predictions[model_id] = WarmupPrediction(
                model_id=model_id,
                probability=combined_probability,
                confidence=confidence,
                time_window="next_hour",
                reasoning=reasoning
            )
        
        return predictions

class AsyncModelLoader:
    """
    Handles asynchronous model loading with priority queuing and resource management.
    """
    
    def __init__(self, max_concurrent_loads: int = 2):
        self.max_concurrent_loads = max_concurrent_loads
        self.loading_semaphore = asyncio.Semaphore(max_concurrent_loads)
        self.loading_queue: asyncio.Queue = asyncio.Queue()
        self.loading_tasks: Dict[str, asyncio.Task] = {}
        self.loaded_models: Dict[str, object] = {}
        
    async def background_load(self, model_id: str, priority: int = 1):
        """Load model in background with priority."""
        if model_id in self.loaded_models:
            return  # Already loaded
            
        if model_id in self.loading_tasks:
            return  # Already loading
            
        # Add to priority queue
        await self.loading_queue.put((priority, model_id, time.time()))
        
        # Start loader if not running
        if not hasattr(self, '_loader_task') or self._loader_task.done():
            self._loader_task = asyncio.create_task(self._process_loading_queue())
    
    async def _process_loading_queue(self):
        """Process the model loading queue with priority ordering."""
        while True:
            try:
                # Get next item from queue (with timeout)
                priority, model_id, queued_time = await asyncio.wait_for(
                    self.loading_queue.get(), timeout=30.0
                )
                
                # Create loading task
                task = asyncio.create_task(self._load_model_with_semaphore(model_id))
                self.loading_tasks[model_id] = task
                
            except asyncio.TimeoutError:
                # No more items in queue, exit
                break
            except Exception as e:
                print(f"Error in loading queue: {e}")
                continue
    
    async def _load_model_with_semaphore(self, model_id: str):
        """Load model with semaphore control."""
        async with self.loading_semaphore:
            try:
                # Simulate model loading (replace with actual loading logic)
                print(f"Loading model {model_id}...")
                await asyncio.sleep(2)  # Simulate loading time
                
                # Store loaded model
                self.loaded_models[model_id] = f"loaded_model_{model_id}"
                print(f"Model {model_id} loaded successfully")
                
            except Exception as e:
                print(f"Failed to load model {model_id}: {e}")
            finally:
                # Remove from loading tasks
                if model_id in self.loading_tasks:
                    del self.loading_tasks[model_id]

class ModelWarmupManager:
    """
    Complete model warmup management with intelligent predictions and loading.
    """
    
    def __init__(self, warmup_interval: int = 300):  # 5 minutes
        self.warmup_interval = warmup_interval
        self.usage_predictor = UsagePredictor()
        self.model_loader = AsyncModelLoader()
        self.warmup_task: Optional[asyncio.Task] = None
        self.is_running = False
        
    async def start_warmup_loop(self):
        """Start the continuous warmup process."""
        self.is_running = True
        self.warmup_task = asyncio.create_task(self._warmup_loop())
        
    async def stop_warmup_loop(self):
        """Stop the warmup process."""
        self.is_running = False
        if self.warmup_task:
            self.warmup_task.cancel()
            
    async def _warmup_loop(self):
        """Main warmup loop that runs continuously."""
        while self.is_running:
            try:
                await self.warm_likely_models()
                await asyncio.sleep(self.warmup_interval)
            except Exception as e:
                print(f"Error in warmup loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
                
    async def warm_likely_models(self):
        """
        Intelligent model preloading based on usage predictions.
        """
        predictions = await self.usage_predictor.predict_next_hour()
        
        # Sort by probability * confidence
        sorted_predictions = sorted(
            predictions.values(),
            key=lambda p: p.probability * p.confidence,
            reverse=True
        )
        
        for prediction in sorted_predictions:
            if prediction.probability > 0.7 and prediction.confidence > 0.5:
                print(f"Warming up {prediction.model_id}: {prediction.reasoning}")
                await self.model_loader.background_load(prediction.model_id)
```

---

## 2. 📋 Request Queuing & Batching System

### 2.1 Advanced Queue Implementation

```python
from enum import Enum
from typing import List, Optional, Callable, Any
import heapq
import asyncio
from dataclasses import dataclass, field
import time

class RequestPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class UnifiedRequest:
    id: str
    model_id: str
    content: Any
    priority: RequestPriority
    timestamp: float
    max_wait_time: float = 30.0  # seconds
    batch_compatible: bool = True
    callback: Optional[Callable] = None
    metadata: dict = field(default_factory=dict)
    
    def __lt__(self, other):
        # For priority queue ordering
        return (self.priority.value, self.timestamp) < (other.priority.value, other.timestamp)

@dataclass
class RequestBatch:
    requests: List[UnifiedRequest]
    model_id: str
    created_at: float
    estimated_processing_time: float = 0.0
    
    def is_ready(self, max_batch_size: int = 8, max_wait_time: float = 2.0) -> bool:
        """Determine if batch is ready for processing."""
        current_time = time.time()
        
        # Ready if batch is full
        if len(self.requests) >= max_batch_size:
            return True
            
        # Ready if oldest request has waited too long
        if self.requests and (current_time - self.requests[0].timestamp) > max_wait_time:
            return True
            
        # Ready if any critical priority request
        if any(req.priority == RequestPriority.CRITICAL for req in self.requests):
            return True
            
        return False
    
    def add_request(self, request: UnifiedRequest) -> bool:
        """Add request to batch if compatible."""
        if request.model_id != self.model_id:
            return False
            
        if not request.batch_compatible:
            return False
            
        self.requests.append(request)
        return True

class BatchOptimizer:
    """
    Optimizes batch creation for maximum NPU efficiency.
    """
    
    def __init__(self):
        self.model_configs = {
            'gemma-3n-4b': {'optimal_batch_size': 8, 'max_batch_size': 16},
            'bge-small-en-v1.5': {'optimal_batch_size': 32, 'max_batch_size': 64},
            'granite-docling-258m': {'optimal_batch_size': 4, 'max_batch_size': 8}
        }
        
    def calculate_optimal_batch_size(self, model_id: str, current_load: float) -> int:
        """Calculate optimal batch size based on model and current system load."""
        config = self.model_configs.get(model_id, {'optimal_batch_size': 8, 'max_batch_size': 16})
        optimal = config['optimal_batch_size']
        max_size = config['max_batch_size']
        
        # Adjust based on system load
        if current_load > 0.8:  # High load
            return min(optimal // 2, max_size)
        elif current_load < 0.3:  # Low load  
            return min(optimal * 2, max_size)
        else:
            return optimal
    
    def group_compatible_requests(self, requests: List[UnifiedRequest]) -> List[List[UnifiedRequest]]:
        """Group requests that can be batched together."""
        groups = {}
        
        for request in requests:
            # Group by model and batch compatibility
            key = (request.model_id, request.batch_compatible)
            if key not in groups:
                groups[key] = []
            groups[key].append(request)
        
        return list(groups.values())

class IntelligentBatcher:
    """
    Advanced request batching with intelligent optimization.
    """
    
    def __init__(self, system_monitor):
        self.model_queues: Dict[str, asyncio.Queue] = {}
        self.active_batches: Dict[str, RequestBatch] = {}
        self.batch_optimizer = BatchOptimizer()
        self.system_monitor = system_monitor
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
    async def add_request(self, request: UnifiedRequest) -> str:
        """
        Add request to appropriate queue with intelligent batching.
        Returns: request_id for tracking
        """
        model_id = request.model_id
        
        # Ensure queue exists for model
        if model_id not in self.model_queues:
            self.model_queues[model_id] = asyncio.Queue()
            
        # Add to queue
        await self.model_queues[model_id].put(request)
        
        # Start processing task if not running
        if model_id not in self.processing_tasks or self.processing_tasks[model_id].done():
            self.processing_tasks[model_id] = asyncio.create_task(
                self._process_model_queue(model_id)
            )
            
        return request.id
    
    async def _process_model_queue(self, model_id: str):
        """Process requests for a specific model with batching."""
        queue = self.model_queues[model_id]
        
        while True:
            try:
                # Get current system load
                current_load = await self.system_monitor.get_npu_utilization()
                optimal_batch_size = self.batch_optimizer.calculate_optimal_batch_size(
                    model_id, current_load
                )
                
                # Create or get active batch
                if model_id not in self.active_batches:
                    self.active_batches[model_id] = RequestBatch(
                        requests=[],
                        model_id=model_id,
                        created_at=time.time()
                    )
                
                batch = self.active_batches[model_id]
                
                # Try to fill batch
                timeout = 2.0  # 2 second timeout for batching
                start_time = time.time()
                
                while len(batch.requests) < optimal_batch_size:
                    remaining_time = timeout - (time.time() - start_time)
                    if remaining_time <= 0:
                        break
                        
                    try:
                        request = await asyncio.wait_for(queue.get(), timeout=remaining_time)
                        batch.add_request(request)
                        
                        # Check if batch is ready early
                        if batch.is_ready(optimal_batch_size, timeout):
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if it has requests
                if batch.requests:
                    await self._process_batch(batch)
                    del self.active_batches[model_id]
                else:
                    # No requests, wait a bit
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"Error processing queue for {model_id}: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch: RequestBatch):
        """Process a batch of requests."""
        try:
            print(f"Processing batch of {len(batch.requests)} requests for {batch.model_id}")
            
            # Simulate batch processing
            await asyncio.sleep(0.5)  # Replace with actual model inference
            
            # Call callbacks for each request
            for request in batch.requests:
                if request.callback:
                    await request.callback(f"Response for {request.id}")
                    
        except Exception as e:
            print(f"Error processing batch: {e}")
```

---

## 3. 🛡️ Graceful Fallback System

### 3.1 Comprehensive Fallback Implementation

```python
from enum import Enum
from typing import Optional, List, Dict, Any
import asyncio
import time
from dataclasses import dataclass

class FallbackStrategy(Enum):
    SMALLER_MODEL = "smaller_model"
    CPU_FALLBACK = "cpu_fallback"
    QUEUE_WITH_ETA = "queue_with_eta"
    ALTERNATIVE_ENDPOINT = "alternative_endpoint"
    CACHED_RESPONSE = "cached_response"
    ERROR_RESPONSE = "error_response"

@dataclass
class FallbackAction:
    strategy: FallbackStrategy
    target_model: Optional[str] = None
    estimated_wait_time: Optional[float] = None
    degradation_factor: float = 1.0  # 0.0 = full degradation, 1.0 = no degradation
    explanation: str = ""

class ResourceExhaustionDetector:
    """
    Monitors system resources and detects exhaustion scenarios.
    """
    
    def __init__(self):
        self.npu_memory_threshold = 0.95  # 95% utilization
        self.cpu_threshold = 0.90  # 90% utilization
        self.queue_length_threshold = 50
        
    async def check_npu_exhaustion(self) -> bool:
        """Check if NPU is exhausted."""
        # Implement actual NPU monitoring
        # For now, simulate
        return False
        
    async def check_cpu_exhaustion(self) -> bool:
        """Check if CPU is exhausted."""
        # Implement actual CPU monitoring
        return False
        
    async def check_queue_saturation(self, model_id: str) -> bool:
        """Check if request queues are saturated."""
        # Implement queue length checking
        return False
        
    async def get_current_load_metrics(self) -> Dict[str, float]:
        """Get comprehensive load metrics."""
        return {
            'npu_utilization': 0.45,
            'npu_memory_usage': 0.67,
            'cpu_utilization': 0.32,
            'queue_lengths': {'gemma-3n-4b': 5, 'bge-small-en-v1.5': 2},
            'active_connections': 12
        }

class ModelCapabilityMapper:
    """
    Maps models to their capabilities and fallback alternatives.
    """
    
    def __init__(self):
        self.model_hierarchy = {
            'gemma-3n-4b': {
                'capabilities': ['text_generation', 'vision', 'audio', 'multimodal'],
                'smaller_variants': ['gemma-3n-2b'],
                'cpu_compatible': True,
                'quality_score': 0.95
            },
            'gemma-3n-2b': {
                'capabilities': ['text_generation', 'vision', 'multimodal'],
                'smaller_variants': [],
                'cpu_compatible': True,
                'quality_score': 0.85
            },
            'granite-docling-258m': {
                'capabilities': ['document_processing', 'text_extraction'],
                'smaller_variants': [],
                'cpu_compatible': True,
                'quality_score': 0.90
            },
            'bge-small-en-v1.5': {
                'capabilities': ['embeddings'],
                'smaller_variants': [],
                'cpu_compatible': True,
                'quality_score': 0.88
            }
        }
        
    def find_fallback_model(self, model_id: str, required_capabilities: List[str]) -> Optional[str]:
        """Find suitable fallback model with required capabilities."""
        if model_id not in self.model_hierarchy:
            return None
            
        # First try smaller variants
        smaller_variants = self.model_hierarchy[model_id].get('smaller_variants', [])
        for variant in smaller_variants:
            if self._has_capabilities(variant, required_capabilities):
                return variant
                
        # Then try other models with same capabilities
        for other_model, config in self.model_hierarchy.items():
            if other_model != model_id and self._has_capabilities(other_model, required_capabilities):
                return other_model
                
        return None
        
    def _has_capabilities(self, model_id: str, required_capabilities: List[str]) -> bool:
        """Check if model has required capabilities."""
        model_caps = self.model_hierarchy.get(model_id, {}).get('capabilities', [])
        return all(cap in model_caps for cap in required_capabilities)

class FallbackManager:
    """
    Advanced fallback management with multiple strategies.
    """
    
    def __init__(self):
        self.resource_detector = ResourceExhaustionDetector()
        self.capability_mapper = ModelCapabilityMapper()
        self.fallback_history: Dict[str, List[FallbackAction]] = {}
        
    async def handle_resource_exhaustion(self, request: UnifiedRequest) -> FallbackAction:
        """
        Handle resource exhaustion with intelligent fallback selection.
        """
        load_metrics = await self.resource_detector.get_current_load_metrics()
        
        # Strategy 1: Try smaller model variant
        smaller_model = self.capability_mapper.find_fallback_model(
            request.model_id, 
            request.metadata.get('required_capabilities', [])
        )
        
        if smaller_model:
            return FallbackAction(
                strategy=FallbackStrategy.SMALLER_MODEL,
                target_model=smaller_model,
                degradation_factor=0.85,
                explanation=f"Switched to {smaller_model} due to resource constraints"
            )
        
        # Strategy 2: CPU fallback if NPU is exhausted
        if load_metrics['npu_utilization'] > 0.9:
            cpu_compatible = self.capability_mapper.model_hierarchy.get(
                request.model_id, {}
            ).get('cpu_compatible', False)
            
            if cpu_compatible:
                return FallbackAction(
                    strategy=FallbackStrategy.CPU_FALLBACK,
                    target_model=request.model_id,
                    degradation_factor=0.6,  # Slower but functional
                    explanation="Fallback to CPU processing due to NPU saturation"
                )
        
        # Strategy 3: Queue with ETA
        queue_length = load_metrics['queue_lengths'].get(request.model_id, 0)
        if queue_length < 20:  # Reasonable queue
            eta = self._estimate_queue_wait_time(request.model_id, queue_length)
            return FallbackAction(
                strategy=FallbackStrategy.QUEUE_WITH_ETA,
                estimated_wait_time=eta,
                degradation_factor=1.0,
                explanation=f"Queued for processing, estimated wait: {eta:.1f}s"
            )
        
        # Strategy 4: Error response as last resort
        return FallbackAction(
            strategy=FallbackStrategy.ERROR_RESPONSE,
            degradation_factor=0.0,
            explanation="System temporarily overloaded, please try again later"
        )
    
    async def handle_model_failure(self, model_id: str, request: UnifiedRequest) -> FallbackAction:
        """
        Handle model failure with recovery strategies.
        """
        # Try to restart model first
        restart_success = await self._attempt_model_restart(model_id)
        if restart_success:
            return FallbackAction(
                strategy=FallbackStrategy.QUEUE_WITH_ETA,
                estimated_wait_time=10.0,
                degradation_factor=1.0,
                explanation="Model restarted, queuing request"
            )
        
        # Find backup model
        backup_model = self.capability_mapper.find_fallback_model(
            model_id,
            request.metadata.get('required_capabilities', [])
        )
        
        if backup_model:
            return FallbackAction(
                strategy=FallbackStrategy.SMALLER_MODEL,
                target_model=backup_model,
                degradation_factor=0.8,
                explanation=f"Using backup model {backup_model}"
            )
        
        return FallbackAction(
            strategy=FallbackStrategy.ERROR_RESPONSE,
            degradation_factor=0.0,
            explanation=f"Model {model_id} failed and no backup available"
        )
    
    def _estimate_queue_wait_time(self, model_id: str, queue_length: int) -> float:
        """Estimate wait time based on queue length and processing speed."""
        # Model-specific processing speeds (requests per second)
        processing_speeds = {
            'gemma-3n-4b': 1.2,
            'bge-small-en-v1.5': 8.0,
            'granite-docling-258m': 2.0
        }
        
        speed = processing_speeds.get(model_id, 1.0)
        return queue_length / speed
    
    async def _attempt_model_restart(self, model_id: str) -> bool:
        """Attempt to restart a failed model."""
        try:
            # Implement actual model restart logic
            print(f"Attempting to restart model {model_id}")
            await asyncio.sleep(2)  # Simulate restart time
            return True
        except Exception as e:
            print(f"Failed to restart model {model_id}: {e}")
            return False
```

---

## 4. 🔍 System Monitoring & Health Checks

### 4.1 Comprehensive Monitoring System

```python
import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class HealthMetrics:
    timestamp: float
    npu_utilization: float
    npu_memory_used: float
    npu_memory_total: float
    cpu_utilization: float
    ram_used: float
    ram_total: float
    active_models: List[str]
    request_queue_lengths: Dict[str, int]
    avg_response_times: Dict[str, float]
    error_rates: Dict[str, float]
    
    @property
    def npu_memory_percentage(self) -> float:
        return (self.npu_memory_used / self.npu_memory_total) * 100 if self.npu_memory_total > 0 else 0

class SystemMonitor:
    """
    Comprehensive system monitoring for NPU, CPU, memory, and application metrics.
    """
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.metrics_history: List[HealthMetrics] = []
        self.max_history_length = 1000
        self.monitoring_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self):
        """Start continuous system monitoring."""
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = await self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Trim history if too long
                if len(self.metrics_history) > self.max_history_length:
                    self.metrics_history = self.metrics_history[-self.max_history_length:]
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def collect_metrics(self) -> HealthMetrics:
        """Collect comprehensive system metrics."""
        current_time = time.time()
        
        # CPU and RAM metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # NPU metrics (simulated - replace with actual NPU monitoring)
        npu_util, npu_mem_used, npu_mem_total = await self._get_npu_metrics()
        
        # Application metrics (to be integrated with actual components)
        active_models = await self._get_active_models()
        queue_lengths = await self._get_queue_lengths()
        response_times = await self._get_response_times()
        error_rates = await self._get_error_rates()
        
        return HealthMetrics(
            timestamp=current_time,
            npu_utilization=npu_util,
            npu_memory_used=npu_mem_used,
            npu_memory_total=npu_mem_total,
            cpu_utilization=cpu_percent,
            ram_used=memory.used / (1024**3),  # GB
            ram_total=memory.total / (1024**3),  # GB
            active_models=active_models,
            request_queue_lengths=queue_lengths,
            avg_response_times=response_times,
            error_rates=error_rates
        )
    
    async def _get_npu_metrics(self) -> tuple[float, float, float]:
        """Get NPU utilization and memory metrics."""
        # Placeholder - implement actual NPU monitoring
        # For DirectML/NPU on Windows ARM64
        return 45.2, 6.8, 16.0  # utilization %, used GB, total GB
    
    async def _get_active_models(self) -> List[str]:
        """Get list of currently loaded models."""
        # Integrate with actual model manager
        return ['gemma-3n-4b', 'bge-small-en-v1.5']
    
    async def _get_queue_lengths(self) -> Dict[str, int]:
        """Get current request queue lengths."""
        # Integrate with actual queue manager
        return {'gemma-3n-4b': 3, 'bge-small-en-v1.5': 1}
    
    async def _get_response_times(self) -> Dict[str, float]:
        """Get average response times by model."""
        # Integrate with actual request tracking
        return {'gemma-3n-4b': 1.2, 'bge-small-en-v1.5': 0.3}
    
    async def _get_error_rates(self) -> Dict[str, float]:
        """Get error rates by model."""
        # Integrate with actual error tracking
        return {'gemma-3n-4b': 0.02, 'bge-small-en-v1.5': 0.01}
    
    async def _check_alerts(self, metrics: HealthMetrics):
        """Check for alert conditions."""
        alerts = []
        
        # NPU memory alert
        if metrics.npu_memory_percentage > 90:
            alerts.append(f"NPU memory high: {metrics.npu_memory_percentage:.1f}%")
        
        # CPU alert
        if metrics.cpu_utilization > 85:
            alerts.append(f"CPU utilization high: {metrics.cpu_utilization:.1f}%")
        
        # Queue length alerts
        for model, length in metrics.request_queue_lengths.items():
            if length > 20:
                alerts.append(f"Queue length high for {model}: {length}")
        
        # Error rate alerts
        for model, rate in metrics.error_rates.items():
            if rate > 0.05:  # 5% error rate
                alerts.append(f"Error rate high for {model}: {rate:.1%}")
        
        if alerts:
            await self._send_alerts(alerts)
    
    async def _send_alerts(self, alerts: List[str]):
        """Send alerts (implement actual alerting mechanism)."""
        for alert in alerts:
            print(f"ALERT: {alert}")
    
    def get_health_summary(self) -> Dict:
        """Get current health summary."""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        
        # Determine overall health status
        status = "healthy"
        if latest.npu_memory_percentage > 90 or latest.cpu_utilization > 85:
            status = "warning"
        if any(rate > 0.05 for rate in latest.error_rates.values()):
            status = "critical"
        
        return {
            "status": status,
            "timestamp": latest.timestamp,
            "npu": {
                "utilization": latest.npu_utilization,
                "memory_usage": latest.npu_memory_percentage,
                "memory_used_gb": latest.npu_memory_used,
                "memory_total_gb": latest.npu_memory_total
            },
            "cpu": {
                "utilization": latest.cpu_utilization
            },
            "memory": {
                "used_gb": latest.ram_used,
                "total_gb": latest.ram_total,
                "usage_percentage": (latest.ram_used / latest.ram_total) * 100
            },
            "models": {
                "active": latest.active_models,
                "queue_lengths": latest.request_queue_lengths,
                "avg_response_times": latest.avg_response_times,
                "error_rates": latest.error_rates
            }
        }
```

---

## 5. 🔧 Integration Pattern

### 5.1 Component Orchestration

```python
class FastEmbedOrchestrator:
    """
    Main orchestrator that coordinates all components.
    """
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.warmup_manager = ModelWarmupManager()
        self.intelligent_batcher = IntelligentBatcher(self.system_monitor)
        self.fallback_manager = FallbackManager()
        
    async def start_all_services(self):
        """Start all system components."""
        await self.system_monitor.start_monitoring()
        await self.warmup_manager.start_warmup_loop()
        print("FastEmbed services started successfully")
        
    async def stop_all_services(self):
        """Stop all system components."""
        await self.system_monitor.stop_monitoring()
        await self.warmup_manager.stop_warmup_loop()
        print("FastEmbed services stopped")
        
    async def process_request(self, request: UnifiedRequest) -> Any:
        """Process a request with full component integration."""
        try:
            # Check system health first
            health = self.system_monitor.get_health_summary()
            
            if health["status"] == "critical":
                # Apply fallback strategy
                fallback_action = await self.fallback_manager.handle_resource_exhaustion(request)
                return await self._execute_fallback(request, fallback_action)
            
            # Normal processing through intelligent batcher
            request_id = await self.intelligent_batcher.add_request(request)
            
            # Record usage for warmup predictions
            self.warmup_manager.usage_predictor.record_usage(
                request.model_id, 
                time.time(), 
                0.0  # Will be updated with actual latency
            )
            
            return request_id
            
        except Exception as e:
            # Handle failure
            fallback_action = await self.fallback_manager.handle_model_failure(
                request.model_id, request
            )
            return await self._execute_fallback(request, fallback_action)
    
    async def _execute_fallback(self, request: UnifiedRequest, action: FallbackAction) -> Any:
        """Execute a fallback action."""
        if action.strategy == FallbackStrategy.SMALLER_MODEL:
            # Modify request to use smaller model
            request.model_id = action.target_model
            return await self.process_request(request)
        
        elif action.strategy == FallbackStrategy.QUEUE_WITH_ETA:
            # Return ETA information
            return {
                "status": "queued",
                "estimated_wait_time": action.estimated_wait_time,
                "explanation": action.explanation
            }
        
        else:
            # Return error response
            return {
                "status": "error",
                "explanation": action.explanation,
                "degradation_factor": action.degradation_factor
            }

# Usage example
async def main():
    orchestrator = FastEmbedOrchestrator()
    await orchestrator.start_all_services()
    
    # Example request processing
    request = UnifiedRequest(
        id="req_123",
        model_id="gemma-3n-4b",
        content={"text": "Hello world"},
        priority=RequestPriority.NORMAL,
        timestamp=time.time()
    )
    
    result = await orchestrator.process_request(request)
    print(f"Request processed: {result}")
    
    await orchestrator.stop_all_services()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 Implementation Checklist

### ✅ Completed Design Components
- [x] Model Warmup Manager with ML-based predictions
- [x] Request Queuing & Batching with NPU optimization
- [x] Graceful Fallback System with multiple strategies
- [x] System Monitoring & Health Checks
- [x] Component Integration & Orchestration

### 🔄 Next Implementation Steps
1. **NPU Integration** - Replace simulated NPU metrics with DirectML
2. **Model Loading** - Implement actual ONNX model loading
3. **Request Processing** - Connect to real inference engines
4. **Persistence** - Add configuration and state persistence
5. **Testing** - Create comprehensive test suites

### 🎯 Configuration Examples

```yaml
# fastembed_config.yaml
system:
  warmup:
    enabled: true
    interval_seconds: 300
    prediction_threshold: 0.7
    confidence_threshold: 0.5
  
  batching:
    enabled: true
    max_wait_time: 2.0
    optimal_batch_sizes:
      "gemma-3n-4b": 8
      "bge-small-en-v1.5": 32
  
  fallback:
    enabled: true
    strategies: ["smaller_model", "cpu_fallback", "queue_with_eta"]
    max_queue_length: 20
  
  monitoring:
    enabled: true
    check_interval: 5.0
    alert_thresholds:
      npu_memory: 90
      cpu_utilization: 85
      error_rate: 0.05

models:
  "gemma-3n-4b":
    path: "./models/gemma-3n-4b"
    capabilities: ["text_generation", "vision", "audio"]
    cpu_compatible: true
    smaller_variants: ["gemma-3n-2b"]
```

This detailed component design provides the foundation for implementing robust, production-ready multimodal AI infrastructure that can handle real-world usage patterns and failure scenarios.