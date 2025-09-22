# FastEmbed NPU - Python SDK Design

## SDK Architecture

### Core Components
1. **Client Class** - Main interface (OpenAI-compatible)
2. **Auto-batching** - Intelligent request grouping
3. **Connection Pool** - Efficient HTTP connections  
4. **Error Handling** - Graceful fallbacks and retries
5. **Async Support** - Non-blocking operations

### Key Features
- **Drop-in OpenAI replacement** 
- **Automatic NPU optimization**
- **Offline-first design**
- **Cost tracking** (vs cloud APIs)
- **Performance monitoring**

## API Design

### Basic Usage (OpenAI Compatible)
```python
from fastembed_npu import EmbeddingClient

# Initialize client
client = EmbeddingClient(
    base_url="http://localhost:8000",
    api_key="optional-for-local"
)

# Generate embeddings (auto-optimized)
response = client.embeddings.create(
    input=["Hello world", "Another text"],
    model="bge-small-en-v1.5"
)

embeddings = [data.embedding for data in response.data]
```

### Advanced Features
```python
# Async usage
import asyncio
async def main():
    async with EmbeddingClient() as client:
        embeddings = await client.embeddings.acreate(
            input=large_text_list
        )

# Batch optimization
client = EmbeddingClient(auto_batch=True, batch_size="auto")
embeddings = client.embed_batch(texts, batch_timeout=100)  # ms

# Performance monitoring
stats = client.get_performance_stats()
print(f"NPU usage: {stats.npu_percentage}%")
print(f"Avg latency: {stats.avg_latency_ms}ms")

# Cost comparison
cost_analysis = client.compare_costs(
    alternatives=["openai", "cohere", "voyage"]
)
```

### Benchmark Integration
```python
# Built-in benchmarking
from fastembed_npu.benchmark import compare_providers

results = compare_providers(
    providers=["fastembed_npu", "openai", "sentence_transformers"],
    test_texts=load_benchmark_texts(),
    metrics=["latency", "cost", "quality"]
)

results.save_report("benchmark_report.html")
```

## Implementation Structure
```
fastembed_npu/
├── __init__.py
├── client.py           # Main client class
├── embeddings.py       # Embedding operations
├── async_client.py     # Async support
├── batching.py         # Auto-batching logic
├── benchmark/
│   ├── __init__.py
│   ├── providers.py    # Competitor integrations
│   ├── metrics.py      # Performance measurement
│   └── reports.py      # Benchmark reporting
├── utils/
│   ├── performance.py  # Performance tracking
│   ├── costs.py        # Cost calculations
│   └── compatibility.py # OpenAI compatibility
└── tests/
    ├── test_client.py
    ├── test_benchmarks.py
    └── integration/
```

## Target Benchmarks

### Performance Targets
- **Latency**: <100ms for single text (vs 200-500ms cloud)
- **Throughput**: >50 texts/sec (vs 10-20 cloud)
- **Cost**: $0 (vs $0.02-0.10 per 1K tokens)
- **Setup**: <5 minutes (vs instant cloud)

### Quality Targets  
- **Accuracy**: Match OpenAI text-embedding-3-small
- **Consistency**: <1% variance across runs
- **Languages**: Good performance on top 10 languages

### Developer Experience
- **API Compatibility**: 100% OpenAI compatible
- **Documentation**: Complete with examples
- **Error Handling**: Clear error messages
- **Monitoring**: Built-in performance dashboard