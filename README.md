# Fa## 🚀 Quick Start

> **⚠️ Important**: Models are not included in the repository. See [MODEL_SETUP.md](MODEL_SETUP.md) for download instructions.

```bash
# 1. Clone the repository
git clone https://github.com/stgarg/locallite.git
cd locallite

# 2. Download models (REQUIRED - see MODEL_SETUP.md)
cd EmbeddingServer/scripts
.\download-bge-model.ps1

# 3. Set up the AI Gateway (FastEmbed Server)
cd ../../ai-gateway/src
python main.py

# 4. Try the Python SDK
cd ../../fastembed-sdk
pip install -e .
python azure_demo.py
```erformance Local Embeddings with NPU Acceleration

A comprehensive local embedding solution optimized for Windows ARM64 (Snapdragon X Elite) with automatic NPU acceleration, delivering 5-10x faster inference and 90% cost savings compared to cloud APIs.

## � Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/fastembed.git
cd fastembed

# 2. Set up the AI Gateway (FastEmbed Server)
cd ai-gateway/src
python main.py

# 3. Try the Python SDK
cd ../../fastembed-sdk
pip install -e .
python azure_demo.py
```

## 📁 Repository Structure

```
fastembed/
├── ai-gateway/                # FastAPI server with NPU optimization
│   ├── src/                   # Python server implementation
│   ├── main.py               # Server entry point
│   └── embedding_engine.py   # NPU-accelerated inference
├── fastembed-sdk/            # Python SDK (OpenAI-compatible)
│   ├── src/fastembed/        # SDK source code
│   ├── examples/             # Usage examples
│   ├── azure_demo.py         # Azure OpenAI comparison demo
│   └── secure_benchmark.py   # Comprehensive benchmarking
├── EmbeddingServer/          # .NET C# implementation (legacy)
└── docs/                     # Documentation
```

## ✨ Key Features

### 🔥 **Performance**
- **5-10x faster** than cloud APIs (local NPU acceleration)
- **Automatic optimization**: NPU for small batches, CPU for large batches  
- **Sub-200ms latency** for single text embedding
- **90+ tokens/second** sustained throughput

### 💰 **Cost Savings**
- **100% FREE** after hardware purchase
- **90% cost reduction** vs OpenAI/Azure at scale
- No per-token charges or API limits
- Perfect for high-volume applications

### 🔒 **Privacy & Security**
- **100% local processing** - data never leaves your device
- No network calls for inference
- GDPR/compliance friendly
- Perfect for sensitive documents

### 🔌 **Developer Experience**  
- **Drop-in OpenAI replacement** - change only the base URL
- Comprehensive Python SDK with async support
- Detailed examples and benchmarking tools
- Fair comparisons with cloud providers

## 📊 Performance Comparison

| Provider | Latency | Cost (1M tokens) | Quality | Privacy |
|----------|---------|------------------|---------|---------|
| **FastEmbed** | ~120ms | **$0** | Good (384D) | **100% Local** |
| Azure OpenAI | ~730ms | ~$200-400 | Premium (1536D) | Cloud |
| OpenAI API | ~500ms | ~$200-400 | Premium (1536D) | Cloud |

> **Note**: Different model architectures - FastEmbed uses BGE-small-en-v1.5 (efficient), cloud APIs use larger models (premium quality)

## 🎯 Use Cases

### ✅ **Perfect for FastEmbed:**
- High-volume document processing
- Cost-sensitive applications  
- Privacy-critical data
- Prototyping and development
- Real-time embedding generation
- On-device AI applications

### ✅ **Consider Cloud APIs for:**
- Maximum embedding quality needed
- Low-volume processing
- Enterprise support requirements
- Multi-modal embeddings

## � Components

### 1. AI Gateway (FastAPI Server)
High-performance embedding server with automatic NPU optimization.

**Features:**
- OpenAI-compatible API endpoints
- Automatic hardware optimization (NPU/CPU)
- Health monitoring and metrics
- Request batching and optimization

**Quick Start:**
```bash
cd ai-gateway/src
python main.py
# Server runs on http://127.0.0.1:8000
```

### 2. Python SDK
OpenAI-compatible Python client with automatic NPU optimization.

**Features:**
- Drop-in OpenAI replacement
- Sync and async clients
- Comprehensive error handling
- Built-in benchmarking tools

**Example:**
```python
import fastembed

# Same API as OpenAI!
client = fastembed.FastEmbedClient()
response = client.embeddings.create(
    input="Your text here",
    model="bge-small-en-v1.5"
)
```

### 3. Benchmarking & Demos
Comprehensive comparison tools and real-world examples.

**Available Demos:**
- `azure_demo.py` - Compare FastEmbed vs Azure OpenAI
- `model_comparison_guide.py` - Detailed model analysis
- `examples/` - Basic usage patterns

## 📚 Documentation

- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[NPU Learnings](NPU_LEARNINGS.md)** - Hardware optimization insights
- **[SDK Design](SDK_DESIGN.md)** - Python SDK architecture

## 🧪 Examples & Tutorials

### Basic Usage
```python
# examples/basic_usage.py
import fastembed

client = fastembed.FastEmbedClient()

# Single embedding
response = client.embeddings.create(input="Hello world")
embedding = response.data[0].embedding  # 384 dimensions

# Batch embeddings (auto-optimized)
texts = ["Text 1", "Text 2", "Text 3"]
response = client.embeddings.create(input=texts)
embeddings = [item.embedding for item in response.data]
```

### Azure OpenAI Comparison
```python
# azure_demo.py - See live performance comparison
python azure_demo.py
```

### Secure Benchmarking
```python
# secure_benchmark.py - Compare against your cloud providers
python secure_benchmark.py
```

## ⚙️ Setup & Installation

### Prerequisites
- **Windows ARM64** (Snapdragon X Elite recommended)
- **Python 3.8+**
- **16GB+ RAM** (for optimal performance)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/stgarg/locallite.git
cd locallite

# 2. Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Download and setup models (REQUIRED)
# See MODEL_SETUP.md for detailed instructions
cd EmbeddingServer/scripts
.\download-bge-model.ps1   # Downloads BGE-small-en-v1.5

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install SDK in development mode
cd ../../fastembed-sdk
pip install -e .

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your API credentials for benchmarking
```

### Configuration
```bash
# .env file for secure benchmarking
FASTEMBED_BASE_URL=http://127.0.0.1:8000
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
# ... see .env.example for full configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BGE Model**: [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- **ONNX Runtime**: Microsoft's high-performance inference engine
- **Snapdragon X Elite**: Qualcomm's NPU-enabled processor
- **FastAPI**: Modern, fast web framework for building APIs

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/fastembed/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/fastembed/discussions)
- **Documentation**: [docs/](docs/)

---

**⭐ Star this repo if FastEmbed helps you save costs and improve performance!**
**Use Case**: Semantic search, RAG, document similarity
```powershell
# Start embedding server
cd EmbeddingServer
$env:EMB_MODEL_DIR="models/all-MiniLM-L6-v2"
.\EmbeddingServer.exe

# Use REST API
curl -X POST http://localhost:8080/embed -H "Content-Type: application/json" -d '{"texts":["Hello world","How are you?"]}'
```

### Scenario 2: Document Conversion + Embeddings
**Use Case**: Build searchable knowledge base from mixed documents
```bash
# 1. Convert documents to markdown (future)
doc-processor convert --input ./docs --output ./markdown --embed --index-path ./search.db

# 2. Use existing embedding server for search
curl -X POST http://localhost:8080/embed -d '{"text":"search query"}'
```

### Scenario 3: Standalone Document Processing
**Use Case**: Simple format conversion without embeddings
```powershell
# Current workaround using provided script
.\scripts\convert-to-markdown.ps1 -InputFile "document.pdf" -Engine auto
```

## 🛠️ Development Status

### Completed ✅
- **FastEmbed Server**: Full implementation with ARM64 optimization
- **ONNX Integration**: Text embedding with multiple model support
- **Performance Benchmarking**: Comprehensive testing suite
- **Documentation**: Complete server documentation
- **Architecture Design**: Document processing system specification

### In Progress 🔄
- **Document Processing Implementation**: CLI tool based on provided architecture
- **Integration Testing**: FastEmbed + document processing workflows

### Planned 📋
- **VS Code Extension**: Direct integration with editor workflows
- **Docker Support**: Containerized deployment options
- **Model Quantization**: Further performance optimization
- **Cloud Deployment**: Azure/AWS deployment guides

## 🔧 Development Setup

### Prerequisites
- **Windows on ARM64** (Snapdragon X optimized)
- **.NET 8 SDK**
- **Python 3.8+** (for future document processing)
- **PowerShell 7+**

### Quick Setup
```powershell
# Clone and setup
git clone <repository>
cd fastembed

# Setup embedding server
cd EmbeddingServer
dotnet restore
.\scripts\download-models-simple.ps1
dotnet run --project .\src\EmbeddingServer.csproj

# Test the setup
.\scripts\test-embed.ps1
```

## 📊 Performance Benchmarks

**FastEmbed Server on Snapdragon X ARM64**:
- **Single embedding**: 12.7ms average
- **Batch of 16**: 2.8ms per text
- **Peak throughput**: 360.9 texts/second
- **Memory usage**: ~200MB with model loaded
- **Cold start**: ~500ms for first request

## 🤝 Contributing

1. **FastEmbed Server**: Production ready, accepting optimization PRs
2. **Document Processing**: Architecture complete, implementation needed
3. **Documentation**: Continuously updated, feedback welcome

## 📄 License

- **Code**: MIT License
- **Models**: Apache 2.0 (sentence-transformers models)
- **Documentation**: MIT License

---

**Status**: FastEmbed server is production-ready. Document processing system is fully designed and ready for implementation.

Last updated: September 21, 2025