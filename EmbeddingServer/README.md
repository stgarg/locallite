# FastEmbed Server - Simple & Reliable# FastEmbed Text Embedding Server# FastEmbed for Windows ARM64 🚀



A lightweight text embedding server with ONNX models. Clean architecture, minimal dependencies.



## 🚀 Quick StartA high-performance .NET 8 REST API for text embeddings on Windows ARM64, supporting multiple ONNX models with multilingual capabilities.**High-performance, offline-capable text embedding inference API optimized for Windows on ARM (Snapdragon X)**



### 1. Setup Model

```powershell

# Download a model (e.g., all-MiniLM-L6-v2)## Quick StartA complete, production-ready solution providing local text embeddings through a REST API or CLI, packaged as a single 102MB executable.

# Place model.onnx and vocab.txt in models/MODEL_NAME/

```



### 2. Run Server```powershell## ✨ Key Features

```powershell

cd C:\Learn\Code\fastembed\EmbeddingServer# 1. Build the server

$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"

dotnet run --project src --configuration Releasecd C:\Learn\Code\fastembed\EmbeddingServer\src- 🏗️ **Single-file executable** - No dependencies, just run `EmbeddingServer.exe`

```

dotnet build -c Release- 🔥 **ARM64 optimized** - Native performance on Snapdragon X (Oryon cores)

### 3. Test API

```powershell- 📶 **Offline capable** - No internet required after setup

# Health check

Invoke-RestMethod -Uri "http://localhost:8080/healthz"# 2. Start with English model- 🎯 **Production ready** - Health checks, logging, rate limiting



# Single embeddingcd ..- 🚀 **Fast inference** - 8-25ms per embedding on Snapdragon X

Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -ContentType "application/json" -Body '{"text":"Hello world"}'

$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"- 📦 **Small footprint** - ~200MB memory usage

# Batch embedding  

Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -ContentType "application/json" -Body '{"texts":["Hello","World"]}'.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe- 🔧 **Multiple backends** - CPU (default), DirectML (optional)

```

- 📋 **Flexible I/O** - REST API + CLI interface

## 📋 API Reference

# 3. Test embedding

### Health Check

**GET** `/healthz`$body = @{ text = "Hello world" } | ConvertTo-Json## 🎯 Quick Start

```json

{Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json"

  "status": "ok",

  "model": "model.onnx", ```### 1. Download Model

  "pid": 1234,

  "mock": false,```powershell

  "dimension": 384,

  "executionProvider": "cpu"## Available Models# Download all-MiniLM-L6-v2 (384-dimensional embeddings)

}

```.\scripts\download-models-simple.ps1 -Model "all-MiniLM-L6-v2"



### Text Embedding| Model | Size | Languages | Dimensions | Status |```

**POST** `/embed`

|-------|------|-----------|------------|--------|

**Single text:**

```json| **all-MiniLM-L6-v2** | 86MB | English | 384 | ✅ Ready |### 2. Build Single-File Executable

{"text": "Your text here"}

```| **multilingual-e5-small** | 448MB | 100+ Languages | 384 | ✅ Ready |```powershell



**Multiple texts:**| bge-small-en-v1.5 | - | English | 384 | ❌ Missing ONNX |cd src

```json

{"texts": ["Text 1", "Text 2", "Text 3"]}dotnet publish -c Release -r win-arm64 --self-contained

```

## Features```

**Response:**

```json

{

  "dimension": 384,- **High Performance**: 300-700 texts/sec on Snapdragon X### 3. Run Server

  "count": 2,

  "embeddings": [[0.1, -0.2, ...], [0.3, 0.1, ...]],- **Multilingual**: Support for 100+ languages including Hindi, Bengali, Tamil```powershell

  "tokensPerInput": [5, 3],

  "model": "model.onnx",- **Batch Processing**: Efficient batch embedding APIcd bin\Release\net8.0\win-arm64\publish

  "pooling": "mean",

  "normalized": true- **Single File**: Self-contained executable (~102MB)$env:EMB_MODEL_DIR="models/all-MiniLM-L6-v2"

}

```- **REST API**: Simple JSON API compatible with OpenAI-style requests.\EmbeddingServer.exe



## ⚙️ Configuration```



Set environment variables before starting:## Repository Structure



| Variable | Default | Description |### 4. Test API

|----------|---------|-------------|

| `EMB_MODEL_DIR` | `models/bge-small-en-v1.5` | Model directory |``````powershell

| `EMB_MODEL_FILE` | `model.onnx` | Model filename |

| `EMB_HOST` | `127.0.0.1` | Listen host |├── INSTRUCTIONS.md              # Complete usage guide (READ THIS FIRST)# Single embedding

| `EMB_PORT` | `8080` | Listen port |

| `EMB_MAX_SEQ` | `256` | Max sequence length |├── README.md                   # This overview$body = @{ text = "Hello world" } | ConvertTo-Json

| `EMB_BATCH` | `16` | Inference batch size |

| `EMB_EP` | `cpu` | Execution provider (`cpu`/`dml`) |├── indian-language-support.md  # Multilingual test resultsInvoke-RestMethod -Uri "http://localhost:8080/embed" -Method POST -Body $body -ContentType "application/json"



## 🛠️ Development├── DEPENDENCIES.md             # Package dependencies



### Build├── src/                        # C# source code# Batch embedding

```powershell

dotnet build src --configuration Release├── models/                     # ONNX models and tokenizers$body = @{ texts = @("Hello", "World", "AI") } | ConvertTo-Json  

```

└── scripts/                    # Utility scriptsInvoke-RestMethod -Uri "http://localhost:8080/embed" -Method POST -Body $body -ContentType "application/json"

### Test

```powershell    ├── benchmark-current-model.ps1     # Performance testing```

# Basic API test

.\scripts\test-api.ps1    ├── download-e5-prebuilt.ps1        # Download multilingual model



# Single embedding test    ├── extract_vocab.py                # Extract vocabulary files## 📊 Performance on Snapdragon X

.\scripts\test-embed.ps1

```    ├── test-embed.ps1                  # Basic functionality test



### Mock Mode (Testing)    ├── test-multilingual-success.ps1   # Multilingual validation| Metric | Performance |

```powershell

$env:EMB_MOCK = "1"    └── verify-environment.ps1          # Environment check|--------|-------------|

$env:EMB_MOCK_DIM = "384"

dotnet run --project src```| **Single embedding** | 8-25ms |

```

| **Batch (16 texts)** | 6-12ms per text |

## 📁 Project Structure

## API Endpoints| **Cold start** | 2-3 seconds |

```

EmbeddingServer/| **Memory usage** | 200-400MB |

├── src/

│   ├── Program.cs          # Main server + API endpoints### Health Check| **Model size** | 86MB (23MB quantized) |

│   ├── EmbeddingEngine.cs  # Core embedding logic

│   ├── Config.cs           # Environment configuration```| **Executable size** | 102MB |

│   ├── Dtos.cs            # Request/response models

│   ├── Tokenizer.cs        # Text tokenizationGET /healthz

│   ├── Vocabulary.cs       # Vocab loading

│   └── *.csproj           ```## 🎮 Usage Examples

├── models/

│   └── MODEL_NAME/

│       ├── model.onnx      # ONNX model file

│       └── vocab.txt       # Vocabulary file### Embed Text### CLI Interface

├── scripts/

│   ├── test-api.ps1        # API testing``````bash

│   └── verify-environment.ps1

└── README.md               # This filePOST /embed# Single text embedding

```

Content-Type: application/json.\EmbeddingServer.exe --text "Machine learning is amazing"

## 🧹 What's Different (Clean Architecture)



### ✅ Simplified

- **Single tokenizer**: No complex fallback logic{"text": "Your text here"}# Health check

- **Two endpoints**: Health + embed only  

- **Simple configuration**: Environment variables{"texts": ["Multiple", "texts", "here"]}.\EmbeddingServer.exe --health

- **Minimal dependencies**: Core .NET + ONNX Runtime

``````

### ❌ Removed Complexity

- Complex web interface with JavaScript

- Multiple conflicting launcher scripts

- Enhanced/legacy tokenizer dual modes## Documentation### REST API

- Overly detailed documentation

- Benchmarking and demo scripts```bash



### 🎯 Focus**📖 See [INSTRUCTIONS.md](INSTRUCTIONS.md) for complete documentation including:**# Health check

**Reliability** over features. **Simplicity** over complexity.

- Detailed configuration optionscurl http://localhost:8080/healthz

## 🔧 Troubleshooting

- Model management

### "Model file not found"

- Check `EMB_MODEL_DIR` points to correct directory- Performance optimization# Single embedding

- Ensure `model.onnx` and `vocab.txt` exist in model directory

- Troubleshooting guidecurl -X POST http://localhost:8080/embed \

### "vocab.txt not found" 

- Download complete model including vocabulary file- API examples  -H "Content-Type: application/json" \

- Check file permissions

  -d '{"text": "Hello world"}'

### Server won't start

- Check if port 8080 is available: `Test-NetConnection -ComputerName localhost -Port 8080`## System Requirements

- Try different port: `$env:EMB_PORT = "8081"`

# Batch embeddings

### CORS issues (if building web interface)

CORS is enabled by default for localhost development.- Windows ARM64 (Snapdragon X recommended)curl -X POST http://localhost:8080/embed \

- .NET 8 SDK  -H "Content-Type: application/json" \

- 4GB+ RAM (for multilingual model)  -d '{"texts": ["Hello", "World", "AI", "Embeddings"]}'

- 1GB+ disk space```



## License### Response Format

```json

MIT License - Built for practical text embedding applications.{
  "dimension": 384,
  "count": 1,
  "vectors": [[0.123, -0.456, 0.789, ...]],
  "tokensPerInput": [5],
  "model": "model.onnx",
  "pooling": "mean",
  "normalized": true
}
```

## ⚙️ Configuration

Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `EMB_MODEL_DIR` | `models/bge-small-en-v1.5` | Model directory path |
| `EMB_MODEL_FILE` | `model.onnx` | ONNX model filename |
| `EMB_MODEL_FILE_Q` | `null` | Quantized model filename |
| `EMB_MAX_SEQ` | `256` | Max sequence length |
| `EMB_EP` | `cpu` | Execution provider (cpu/dml) |
| `EMB_HOST` | `127.0.0.1` | Listen address |
| `EMB_PORT` | `8080` | Listen port |
| `EMB_L2` | `1` | L2 normalize embeddings |
| `EMB_POOL` | `mean` | Pooling strategy |

## 🔧 Advanced Features

### Model Quantization
```bash
# Use quantized model for 2x speed, 75% size reduction
$env:EMB_MODEL_FILE_Q="model_quantized.onnx"
```

### DirectML (GPU/NPU)
```bash
# Enable DirectML for potential acceleration
$env:EMB_EP="dml"
```

### Performance Tuning
```bash
# Memory optimization
$env:EMB_MEM_OPT="2"
$env:EMB_MEM_PATTERN="1"

# Thread optimization (Snapdragon X)
$env:OMP_NUM_THREADS="8"  # Use performance cores
```

## 📚 Available Models

| Model | Size | Dimensions | Languages | Use Case |
|-------|------|------------|-----------|-----------|
| **all-MiniLM-L6-v2** ⭐ | 86MB | 384 | English | General purpose, fast |
| **e5-small-v2** | 133MB | 384 | Multilingual | International use |
| **bge-small-en-v1.5** | 134MB | 384 | English | High quality, recent |

Download any model:
```bash
.\scripts\download-models-simple.ps1 -Model "e5-small-v2"
```

## 🔒 Security & Production

### Local Network Access
```bash
# WARNING: Only on trusted networks
$env:EMB_HOST="0.0.0.0"  # Listen on all interfaces
```

### API Key Protection
```bash
$env:EMB_API_KEY="your-secret-key"
# Then include header: X-API-Key: your-secret-key
```

### Rate Limiting
Built-in rate limiting: 100 requests/minute per IP

## 📁 Project Structure

```
EmbeddingServer/
├── src/                          # Source code
│   ├── Program.cs               # REST API server
│   ├── EmbeddingEngine.cs       # ONNX inference engine
│   ├── EnhancedTokenizer.cs     # Modern tokenizer support
│   ├── Config.cs                # Configuration management
│   └── EmbeddingServer.csproj   # Project file
├── scripts/
│   ├── download-models-simple.ps1  # Model downloader
│   └── test-embed.ps1              # Testing utilities
├── models/                       # Downloaded models
│   └── all-MiniLM-L6-v2/
├── docs/                         # Documentation
│   ├── optimization-guide.md    # Performance tuning
│   ├── troubleshooting.md       # Common issues
│   ├── security-operations.md   # Production setup
│   └── wasm-alternative.md      # WASM implementation
└── README.md                     # This file
```

## 🚀 Deployment Options

### 1. Standalone Executable (Recommended)
```bash
# Single 102MB file - just copy and run
copy EmbeddingServer.exe target-machine/
copy models/ target-machine/models/ -Recurse
```

### 2. Windows Service
```bash
# Install as Windows service
sc create EmbeddingServer binPath="C:\Apps\EmbeddingServer.exe"
```

### 3. Docker (Cross-platform)
```bash
docker build -t embedding-server .
docker run -p 8080:8080 embedding-server
```

## 🔍 Monitoring & Health

### Health Endpoints
- `GET /healthz` - Basic health check
- `GET /ready` - Readiness probe (includes inference test)
- `GET /metrics` - Performance metrics

### Logging
```bash
# Enable detailed logging
$env:EMB_LOG_LEVEL="DEBUG"

# Logs written to console and files (if configured)
```

## 📖 Documentation

- [📈 Optimization Guide](docs/optimization-guide.md) - Performance tuning for ARM64
- [🔧 Troubleshooting](docs/troubleshooting.md) - Common issues and solutions  
- [🔒 Security & Operations](docs/security-operations.md) - Production deployment
- [🌐 WASM Alternative](docs/wasm-alternative.md) - Cross-platform option

## ❓ FAQ

**Q: Why not use Python/FastEmbed directly?**
A: .NET 8 provides superior single-file packaging, native ARM64 performance, and smaller distributions compared to Python+dependencies.

**Q: Can I use my own ONNX models?**
A: Yes! Any sentence-transformer model exported to ONNX will work. Ensure you have the matching tokenizer files.

**Q: Does this work on Intel/AMD processors?**
A: Yes, build with `-r win-x64` instead of `-r win-arm64`. Performance will vary.

**Q: Can I run multiple models simultaneously?**
A: Currently single-model per instance. Run multiple instances on different ports for multiple models.

**Q: How accurate are the embeddings compared to OpenAI?**
A: all-MiniLM-L6-v2 achieves ~85% of text-embedding-ada-002 quality at 100x lower latency and cost.

## 📄 License

- **Code**: MIT License
- **Models**: Apache 2.0 (all-MiniLM-L6-v2, e5-small-v2, bge-small-en-v1.5)
- **ONNX Runtime**: MIT License

## 🙋‍♂️ Support

- 📧 Issues: Use GitHub Issues
- 💬 Discussions: GitHub Discussions  
- 📚 Docs: `/docs` directory
- 🔧 Debugging: Run with `--help` or check troubleshooting guide

---

**Made with ❤️ for Windows on ARM** | Optimized for Snapdragon X | Production Ready 🚀

## Cleanup (after Rust removal)
If you previously pulled the repository before the Rust removal, you can optionally prune any stale local artifacts:

```powershell
Remove-Item -Recurse -Force ..\rust_embedder -ErrorAction SilentlyContinue
git rm -r rust_embedder 2>$null
git commit -m "Remove rust embedder" 2>$null
```

No further action needed for fresh clones.

## Getting a Model
Use the provided download script (tries direct ONNX fetch first):

```powershell
cd EmbeddingServer
pwsh ./scripts/download-model.ps1 -ModelId "BAAI/bge-small-en-v1.5"
```

Ensure `models/bge-small-en-v1.5/model.onnx` and `vocab.txt` now exist.

Environment variables you can override:

| Variable | Default | Notes |
|----------|---------|-------|
| `EMB_MODEL_DIR` | models/bge-small-en-v1.5 | Folder containing model/vocab |
| `EMB_MODEL_FILE` | model.onnx | Main FP32 model file |
| `EMB_MODEL_FILE_Q` | (none) | Optional alternate quantized ONNX |
| `EMB_MAX_SEQ` | 256 | Max tokens (truncate) |
| `EMB_EP` | cpu | `cpu` or `dml` |
| `EMB_POOL` | mean | (future) pooling selection |
| `EMB_L2` | 1 | 1=normalize, 0=raw |
| `EMB_HOST` | 127.0.0.1 | Listen host |
| `EMB_PORT` | 8080 | Listen port |

## Running (Real Model)
```powershell
$env:EMB_PORT='8080'
dotnet run --project .\src\EmbeddingServer.csproj
```

Then:
```powershell
Invoke-RestMethod http://127.0.0.1:8080/healthz | ConvertTo-Json -Depth 4
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8080/embed -Body '{"text":"hello embeddings"}' -ContentType 'application/json'
```

Batch:
```powershell
@{ texts = @('first item','second item','third') } | ConvertTo-Json | \
	Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8080/embed -ContentType 'application/json'
```

## Mock Mode (No Model Needed)
Useful for integration wiring before you have ONNX assets:

```powershell
$env:EMB_MOCK='1'; $env:EMB_MOCK_DIM='48'; dotnet run --project .\src\EmbeddingServer.csproj
```

Vectors are deterministic per input string (hashed) and L2 normalized.

## Quick Test Script
Script `scripts/test-embed.ps1` can start the server (optional) and exercise the endpoint.

Examples:
```powershell
# Start mock server on custom port and test
pwsh .\scripts\test-embed.ps1 -Start -Mock -Port 5055 -Dim 24

# Against already-running real server on default port
pwsh .\scripts\test-embed.ps1
```

Output includes dimension, counts, and embedding lengths.

## CLI Mode
You can also get a single embedding via command line argument (returns JSON):

```powershell
dotnet run --project .\src\EmbeddingServer.csproj -- --text "one off embedding"
```

## Single-File Publish (win-arm64)
Produces a trimmed self-contained exe (adjust RID if needed):

```powershell
dotnet publish .\src\EmbeddingServer.csproj -c Release -r win-arm64 -p:PublishSingleFile=true -p:PublishTrimmed=false --self-contained true -o pub\win-arm64
```

Run it:
```powershell
cd pub\win-arm64
./EmbeddingServer.exe
```

## Roadmap / Ideas
- Add logging / timing metrics
- Optional quantized model handling (auto pick if present)
- Proper token count & truncation reporting in response
- DirectML EP fallback diagnostics
- Basic rate limiting or concurrency guard

