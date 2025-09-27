# 🚀 AI Gateway - OpenAI-Compatible API with NPU Acceleration

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-1.16+-orange.svg)](https://onnxruntime.ai/)
[![NPU Support](https://img.shields.io/badge/NPU-QNN%20Provider-purple.svg)](https://onnxruntime.ai/docs/execution-providers/)

A production-ready OpenAI-compatible API gateway that provides high-performance AI inference with automatic NPU acceleration support.

## 🌟 Features

### 🔥 **Core Capabilities**
- **OpenAI-Compatible API** - Drop-in replacement for OpenAI endpoints
- **NPU Acceleration** - Automatic NPU/CPU selection for optimal performance
- **Real ONNX Inference** - Production-ready model inference with proper tokenization
- **Multi-Modal Support** - Both embeddings and chat completions

### ⚡ **Performance Highlights**
- **Sub-100ms Embeddings** with NPU acceleration (91ms average)
- **Sub-second Chat Completions** with Phi-3 Mini (280-640ms)
- **Automatic Provider Selection** - NPU for small batches, CPU for larger ones
- **Memory Efficient** - ~12GB usage for both models

### 🧠 **Supported Models**
- **BGE-small-en-v1.5** - Text embeddings (384 dimensions, NPU optimized)
- **Phi-3-Mini-4K** - Chat completions (4K context, ONNX inference)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Windows ARM64 (for NPU support) or x64
- 16GB+ RAM recommended
- ONNX Runtime with providers

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd fastembed/ai-gateway
pip install -r requirements.txt
```

> 💡 **Developer Tip:** To run the test suite locally, install the extra tooling:
> ```bash
> pip install -r requirements-dev.txt
> python -m pytest
> ```

2. **Download Models**
```bash
# Embedding model (BGE-small-en-v1.5)
python -c "from embedding_engine import OptimizedEmbeddingEngine; OptimizedEmbeddingEngine.download_model()"

# Chat model (Phi-3-Mini) - Download from Hugging Face
# Place in: ../models/phi-3-mini-4k/onnx/model.onnx
```

3. **Start Server**
```bash
python src/main.py
```

The server will start on `http://localhost:8000` with automatic NPU detection.

## 📖 API Usage

### 🔍 **Text Embeddings**

Generate embeddings with automatic NPU acceleration:

```python
import requests

response = requests.post("http://localhost:8000/v1/embeddings", 
    json={
        "input": "Hello world",
        "model": "bge-small-en-v1.5"
    }
)

embeddings = response.json()["data"][0]["embedding"]  # 384-dimensional vector
```

**Batch Processing:**
```python
response = requests.post("http://localhost:8000/v1/embeddings", 
    json={
        "input": ["Hello world", "How are you?", "Machine learning"],
        "model": "bge-small-en-v1.5"
    }
)
```

### 💬 **Chat Completions**

Generate chat responses with Phi-3 Mini:

```python
import requests

response = requests.post("http://localhost:8000/v1/chat/completions",
    json={
        "model": "phi-3-mini-4k",
        "messages": [
            {"role": "user", "content": "What is machine learning?"}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
)

answer = response.json()["choices"][0]["message"]["content"]
```

**Multi-turn Conversations:**
```python
response = requests.post("http://localhost:8000/v1/chat/completions",
    json={
        "model": "phi-3-mini-4k", 
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain Python in simple terms."},
            {"role": "assistant", "content": "Python is a programming language..."},
            {"role": "user", "content": "What can I build with it?"}
        ]
    }
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Model paths (optional, defaults provided)
export EMBEDDING_MODEL_PATH="/path/to/bge-small-en-v1.5"
export CHAT_MODEL_PATH="/path/to/phi-3-mini-4k"

# Server configuration
export HOST="0.0.0.0"          # Default: 127.0.0.1
export PORT="8000"             # Default: 8000
export LOG_LEVEL="INFO"        # Default: INFO
```

### Hardware Configuration

**NPU Support:**
- Windows ARM64 with Snapdragon X Elite
- QNNExecutionProvider automatically detected
- Optimal for embedding inference (1-3 texts)

**CPU Fallback:**
- Works on any system
- Automatic fallback when NPU unavailable
- Better for larger batches (4+ texts)

## 📊 Performance Benchmarks

### Embeddings Performance
| Provider | Batch Size | Avg Time | Throughput |
|----------|------------|----------|------------|
| NPU      | 1 text     | 91ms     | ~11/sec    |
| NPU      | 2 texts    | 151ms    | ~13/sec    |
| CPU      | 4+ texts   | ~200ms   | ~20/sec    |

### Chat Performance
| Complexity | Response Time | Model Provider |
|------------|---------------|----------------|
| Simple     | 280ms        | CPU            |
| Complex    | 640ms        | CPU            |
| Multi-turn | 366ms        | CPU            |

### Current Internal Benchmarks (2025-09-27)
Source artifacts: `ai-gateway/benchmarks/results/20250927_bge.json` (baseline) and `20250927_bge_tokenized.json` (post HF tokenizer + batching). Methodology: warmups discarded, multiple repeats aggregated (mean, p50, p95), deterministic digest for drift.

| Scenario | Batch | Mean Total (ms) | Mean / Text (ms) | Throughput (texts/sec) | Avg Tokens / Text | Tokens / Sec | Tokenizer |
|----------|-------|-----------------|------------------|------------------------|-------------------|--------------|-----------|
| Baseline (pre-HF) | 4 | 1217.8 | 304.5 | 3.28 | 15.2 | 49.9 | whitespace |
| Post HF + Batched | 4 | 829.3 | 207.3 | 4.83 | 15.2 | 73.4 | hf-fast |
| Baseline (pre-HF) | 8 | 2498.9 | 312.4 | 3.20 | 15.2 | 97.2 | whitespace |
| Post HF + Batched | 8 | 1434.4 | 179.3 | 5.58 | 15.2 | 135.0 | hf-fast |

Highlights:
- ~32% per‑text latency reduction at batch 4 (304.5 → 207.3 ms)
- ~74% throughput gain at batch 8 (3.20 → 5.58 texts/sec)
- Accurate token counts enable future routing & pricing logic.

See `docs/BENCHMARKS.md` for full methodology and guardrails.

## 🛠️ Development

### Project Structure
```
ai-gateway/
├── src/
│   ├── main.py              # FastAPI application
│   ├── simple_router.py     # Chat model router
│   └── embedding_engine.py  # Embedding engine with NPU support
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Dev & test tooling
├── README.md               # This file
└── tests/                  # Unit & regression tests (determinism, tokenizer)
```

### Adding New Models

1. **Create Model Class**
```python
class NewModel:
    async def load(self) -> bool:
        # Load your ONNX model
        
    async def process(self, request: UnifiedRequest) -> UnifiedResponse:
        # Process requests
```

2. **Register in Router**
```python
# In simple_router.py
self.new_model = NewModel()
await self.new_model.load()
```

### Benchmarking & Regression Guardrails

Run embedding benchmark (writes JSON artifact under `benchmarks/results/`):
```bash
python -m src.benchmarks.embedding_benchmark --model bge-small-en-v1.5 --batches 4 8 --repeat 3
```
Key artifact fields:
- latency_ms: per batch latencies + aggregate stats (mean, p50, p95)
- tokenize_time_ms, total_tokens, avg_tokens_per_text, tokens_per_sec
- digest: deterministic SHA256 over normalized embedding slice (drift detection)

Tokenizer micro-benchmark:
```bash
python tokenizer_benchmark.py --repeat 5 --corpus data/corpus_small.txt
```

Proposed (manual for now) guardrails:
- Digest must remain identical unless a deliberate tokenizer/model change is documented.
- Throughput regression >10% vs last committed artifact triggers investigation.
- Avg tokens per text shift > ±1 on corpus requires review (signals tokenization change).

### Testing

```bash
# Health check
curl http://localhost:8000/health

# List models  
curl http://localhost:8000/v1/models

# Test embeddings
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"test","model":"bge-small-en-v1.5"}'

# Test chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"phi-3-mini-4k","messages":[{"role":"user","content":"Hi"}]}'
```

## 🔍 Monitoring

### Health Endpoints

- **`GET /health`** - System health, memory usage, uptime
- **`GET /v1/models`** - Available models and status
- **`GET /`** - API information and endpoints

### Logging

The server provides detailed logging for:
- Request/response times
- Provider selection (NPU/CPU)
- Model loading status
- Error handling and fallbacks

## 🚧 Roadmap

### Immediate Improvements
- [x] **Accurate Embedding Tokenization & Batching** (HF fast tokenizer + single-run ONNX)
- [ ] **Embedding Cache Layer** (LRU + hit ratio & p50 impact metrics)
- [ ] **Reduced-Run CI Benchmark** (regression thresholds: digest, throughput, tokens)
- [ ] **Chat Multi-Token Generation** (incremental decoding)
- [ ] **Streaming Support** (SSE / chunked responses)

### Future Features
- [ ] **Provider Routing Heuristics** (token-aware dynamic batch sizing)
- [ ] **Quantization Experiments** (int8 / mixed precision post‑baseline)
- [ ] **Memory & p99 Tracking** (extended benchmark artifact fields)
- [ ] **Hot-Load Custom Models** (plugin registry & reload)
- [ ] **Distributed / Multi-NPU Scaling**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft ONNX Runtime** for excellent NPU support
- **Hugging Face** for model hosting and tokenizers
- **FastAPI** for the robust API framework
- **BGE Team** for the excellent embedding model
- **Microsoft Phi-3** team for the chat model

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: See `/docs` folder for detailed guides

---

**Built with ❤️ for the AI community**