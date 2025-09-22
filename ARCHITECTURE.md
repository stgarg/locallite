# AI Gateway Architecture - ARM64 + NPU Acceleration

## Executive Summary

Design for a local, OpenAI-compatible AI gateway running entirely on Snapdragon X ARM64 laptop (16GB RAM) with NPU acceleration. The system orchestrates multiple ONNX models, provides unified storage, and supports embeddings, chat completions, and document processing.

## System Requirements

### Hardware Platform
- **CPU**: Snapdragon X126100 ARM64 (12 cores)
- **NPU**: Qualcomm Hexagon NPU (detected: Snapdragon X126100)
- **Memory**: 16GB RAM (conservative allocation strategy)
- **Storage**: SSD for model cache and vector database
- **OS**: Windows 11 ARM64

### Performance Targets
- **Embedding Generation**: 5-10x speedup with NPU vs CPU
- **Memory Usage**: <12GB peak (4GB reserved for OS/browser)
- **Response Time**: <2s for embeddings, <10s for chat completion
- **Concurrent Users**: 2-5 local users

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ /v1/embeddings  │ │/v1/chat/compl.  │ │   /v1/route     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Model Manager                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ BGE Embeddings  │ │  Phi-3.5 Mini   │ │  Model Swapper  ││
│  │   (NPU Accel)   │ │   (CPU/NPU)     │ │ (Memory Mgmt)   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 ONNX Runtime + QNN Provider                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │QNNExecutionProv.│ │ CPUExecutionProv│ │ Fallback Logic  ││
│  │  (NPU Accel)    │ │   (Baseline)    │ │  (Auto-switch)  ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    LanceDB Storage                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Embeddings    │ │    Metadata     │ │  Document Store ││
│  │ (Quantized F16) │ │  (SQL Queries)  │ │  (Chunked Text) ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│               Document Processing Pipeline                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  PDF Extractor  │ │ Image OCR (Easy)│ │ Video Transcr.  ││
│  │   (PyMuPDF)     │ │     OCR         │ │   (Whisper)     ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Framework
- **API Gateway**: FastAPI with OpenAI-compatible endpoints
- **Model Runtime**: ONNX Runtime with QNN Provider for NPU acceleration
- **Vector Database**: LanceDB for unified storage (vectors + metadata)
- **Document Processing**: PyMuPDF, EasyOCR, Whisper for multi-format support

### Model Selection
- **Embeddings**: BGE-small-en-v1.5 (384 dim) or e5-small-v2 (384 dim)
- **Chat LLM**: Phi-3.5-mini-instruct (3.8B params, quantized)
- **Fallback LLM**: Llama-3.2-1B-Instruct (1B params)
- **Vision**: Phi-3.5-vision (when memory allows)

### Memory Allocation Strategy
```
Total RAM: 16GB
├── OS + Browser: 4GB
├── FastAPI + Utils: 1GB
├── Model Active: 6GB (swappable)
├── LanceDB + Cache: 3GB
└── Processing Buffer: 2GB
```

## Implementation Phases

### Phase 1: Core Gateway (MVP)
**Goal**: Basic OpenAI-compatible API with NPU-accelerated embeddings

**Components**:
1. FastAPI server with CORS and authentication
2. BGE embedding model converted to ONNX with QNN optimization
3. LanceDB setup for vector storage
4. Basic model swapping (CPU ↔ NPU)

**Endpoints**:
- `POST /v1/embeddings` - Generate embeddings with NPU acceleration
- `GET /v1/models` - List available models
- `GET /health` - System health check

**Success Criteria**:
- ✅ NPU acceleration working (5-10x speedup)
- ✅ OpenAI-compatible response format
- ✅ Memory usage <8GB
- ✅ Response time <2s for embeddings

### Phase 2: Chat Completions
**Goal**: Add LLM chat capabilities with function calling

**Components**:
1. Phi-3.5-mini integration with ONNX Runtime
2. Function calling system for RAG queries
3. Context management and model swapping
4. LanceDB semantic search integration

**Endpoints**:
- `POST /v1/chat/completions` - Chat with function calling
- `POST /v1/route` - Unified endpoint (embeddings + chat)

**Success Criteria**:
- ✅ OpenAI-compatible chat completions
- ✅ Function calling for RAG
- ✅ Automatic model swapping based on memory
- ✅ Context preservation across requests

### Phase 3: Document Processing
**Goal**: Multi-format document ingestion and processing

**Components**:
1. PDF text extraction with PyMuPDF
2. Image OCR with EasyOCR
3. HTML content extraction
4. Document chunking with metadata
5. Batch processing pipeline

**Endpoints**:
- `POST /v1/documents` - Upload and process documents
- `GET /v1/documents/{id}` - Retrieve document metadata
- `DELETE /v1/documents/{id}` - Remove document and vectors

**Success Criteria**:
- ✅ Support PDF, DOCX, images (PNG/JPG), HTML
- ✅ Intelligent chunking with overlap
- ✅ Metadata extraction and storage
- ✅ Batch processing with progress tracking

### Phase 4: Advanced Features
**Goal**: Production-ready features and optimization

**Components**:
1. Video transcription with Whisper
2. Model quantization optimization
3. Caching and performance tuning
4. Admin dashboard
5. Configuration management

**Success Criteria**:
- ✅ Video content support (MP4, AVI)
- ✅ Advanced caching strategies
- ✅ Performance monitoring
- ✅ Configuration hot-reload

## NPU Acceleration Strategy

### Verified Working Components
- ✅ **Hardware**: Snapdragon X126100 Hexagon NPU detected
- ✅ **Software**: ONNX Runtime QNN Provider installed and functional
- ✅ **Integration**: Direct ONNX Runtime approach (no QAIRT SDK needed)

### Model Conversion Pipeline
1. **Source Models**: Hugging Face BGE/e5 models (PyTorch)
2. **Conversion**: PyTorch → ONNX → QNN-optimized
3. **Quantization**: FP32 → INT8 for NPU efficiency
4. **Validation**: Accuracy testing CPU vs NPU output
5. **Benchmarking**: Performance comparison and optimization

### Fallback Strategy
- **Primary**: QNN Provider (NPU acceleration)
- **Fallback**: CPU Provider (guaranteed compatibility)
- **Auto-detection**: Runtime switching based on model compatibility
- **Graceful degradation**: Maintain functionality if NPU fails

## Storage Architecture

### LanceDB Schema
```sql
-- Unified table for vectors and metadata
CREATE TABLE embeddings (
    id VARCHAR PRIMARY KEY,
    vector VECTOR(384),  -- BGE embedding dimension
    content TEXT,
    document_id VARCHAR,
    chunk_index INTEGER,
    metadata JSON,
    created_at TIMESTAMP,
    embedding_model VARCHAR,
    INDEX (document_id),
    INDEX (created_at)
);

-- Document metadata table
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    filename VARCHAR,
    content_type VARCHAR,
    file_size INTEGER,
    page_count INTEGER,
    processed_at TIMESTAMP,
    processing_status VARCHAR,
    metadata JSON
);
```

### Performance Optimizations
- **Vector Quantization**: F32 → F16 for 50% memory reduction
- **Chunking Strategy**: 512 tokens with 50-token overlap
- **Indexing**: HNSW for fast similarity search
- **Caching**: In-memory cache for frequent queries

## API Specification

### OpenAI Compatibility

```python
# Embeddings endpoint
POST /v1/embeddings
{
    "input": ["text to embed", "another text"],
    "model": "bge-small-en-v1.5",
    "encoding_format": "float"
}

# Chat completions endpoint  
POST /v1/chat/completions
{
    "model": "phi-3.5-mini",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ],
    "functions": [...],  # Optional function calling
    "stream": false
}

# Unified routing endpoint
POST /v1/route
{
    "task": "embed_and_search",
    "input": "query text",
    "options": {
        "top_k": 5,
        "include_metadata": true
    }
}
```

### Custom Endpoints

```python
# Document upload
POST /v1/documents
Content-Type: multipart/form-data
{
    "file": <binary>,
    "metadata": {"source": "manual_upload"}
}

# Batch embeddings
POST /v1/embeddings/batch
{
    "inputs": [...],  # Large list of texts
    "callback_url": "http://localhost/webhook"  # Optional webhook
}

# System status
GET /health
{
    "status": "healthy",
    "npu_available": true,
    "models_loaded": ["bge-small", "phi-3.5-mini"],
    "memory_usage": {"used_gb": 8.2, "total_gb": 16},
    "vector_count": 125000
}
```

## Security and Authentication

### Security Model
- **Local Only**: No external network access by default
- **API Keys**: Simple bearer token authentication
- **CORS**: Configurable cross-origin policy
- **Rate Limiting**: Per-IP request limiting
- **Input Validation**: Strict schema validation

### Configuration
```yaml
# config.yaml
server:
  host: "localhost"
  port: 8000
  cors_origins: ["http://localhost:3000"]

auth:
  enabled: true
  api_keys: ["sk-local-key-123"]

models:
  embeddings:
    default: "bge-small-en-v1.5"
    npu_enabled: true
  chat:
    default: "phi-3.5-mini"
    max_context: 4096

storage:
  lancedb_path: "./data/vectors"
  cache_size_mb: 1024

processing:
  max_file_size_mb: 50
  chunk_size: 512
  chunk_overlap: 50
```

## Deployment and Operations

### File Structure
```
ai-gateway/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── chat.py
│   │   └── documents.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   ├── embeddings.py
│   │   └── chat.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── lancedb_client.py
│   │   └── schemas.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   ├── chunking.py
│   │   └── extractors/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── auth.py
│   │   └── monitoring.py
│   └── main.py
├── models/
│   ├── onnx/
│   │   ├── bge-small-en-v1.5.onnx
│   │   └── phi-3.5-mini.onnx
│   └── cache/
├── data/
│   ├── vectors/  # LanceDB storage
│   └── uploads/  # Temporary file storage
├── config.yaml
├── requirements.txt
├── Dockerfile
└── README.md
```

### Monitoring
- **Health Checks**: Endpoint availability and response times
- **Resource Monitoring**: CPU, RAM, NPU utilization
- **Model Performance**: Inference latency and throughput
- **Error Tracking**: Failed requests and model errors
- **Vector Database**: Storage size and query performance

### Performance Targets
- **Embedding Generation**: <2s for batch of 10 texts
- **Chat Completion**: <10s for 2K token response
- **Document Processing**: <30s for 10-page PDF
- **Memory Usage**: <12GB peak under normal load
- **Startup Time**: <60s including model loading

## Next Steps

1. **Start Phase 1 Implementation**: Begin with FastAPI gateway and NPU-accelerated embeddings
2. **Model Conversion**: Convert BGE model to ONNX with QNN optimization
3. **Performance Validation**: Benchmark NPU vs CPU performance gains
4. **Storage Setup**: Configure LanceDB with optimized schema
5. **Iterative Development**: Build and test each phase incrementally

This architecture provides a solid foundation for a local, high-performance AI gateway optimized for ARM64 + NPU acceleration while maintaining OpenAI compatibility.