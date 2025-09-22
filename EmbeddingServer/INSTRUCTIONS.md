# EmbeddingServer - Complete Usage Instructions

This document provides comprehensive instructions for building, configuring, and running the FastEmbed text embedding server on Windows ARM64.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Available Models](#available-models)
4. [Building the Server](#building-the-server)
5. [Configuration](#configuration)
6. [Running the Server](#running-the-server)
7. [Global CLI Access Setup](#global-cli-access-setup)
8. [Performance Testing](#performance-testing)
9. [Troubleshooting](#troubleshooting)

## 📚 Developer Documentation

**For API usage, code examples, and integration guides, see:**
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete developer reference with interactive examples

This document focuses on setup, deployment, and operations.

## Project Overview

The EmbeddingServer is a standalone .NET 8 executable that provides a REST API for text embedding using ONNX models. It's optimized for Windows ARM64 (Snapdragon X) processors and supports multiple embedding models with different language capabilities.

## Prerequisites

- .NET 8 SDK
- Windows ARM64 environment (Snapdragon X recommended)
- PowerShell 5.1 or later
- Sufficient disk space for models (up to 500MB per model)

## Available Models

### 1. all-MiniLM-L6-v2
- **File Size**: 86.22 MB
- **Languages**: English-focused
- **Embedding Dimension**: 384
- **Use Case**: English text, fast inference
- **Required Files**: `model.onnx`, `tokenizer.json`, `vocab.txt`

### 2. bge-small-en-v1.5
- **File Size**: 127 MB
- **Languages**: English-focused  
- **Embedding Dimension**: 384
- **Use Case**: English text, optimized for retrieval tasks
- **Required Files**: `model.onnx`, `tokenizer.json`, `vocab.txt`
- **Status**: ✅ **Complete and working**

### 3. multilingual-e5-small
- **File Size**: 448.48 MB
- **Languages**: 100+ languages including Hindi, Bengali, Tamil, Telugu, Gujarati, Marathi
- **Embedding Dimension**: 384
- **Use Case**: Multilingual applications, cross-language search
- **Required Files**: `model.onnx`, `tokenizer.json`, `vocab.txt`, `config.json`

## Building the Server

### Debug Build
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer\src
dotnet build -c Debug
```
**Output**: `bin\Debug\net8.0\win-arm64\EmbeddingServer.exe`

### Release Build (Recommended)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer\src
dotnet build -c Release
```
**Output**: `bin\Release\net8.0\win-arm64\EmbeddingServer.exe`

### Single-File Publish (Production)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer\src
dotnet publish -c Release
```
**Output**: Self-contained executable (~102MB)

## Configuration

The server uses environment variables for configuration. All variables are optional with sensible defaults.

### Environment Variables

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `EMB_MODEL_DIR` | `models/bge-small-en-v1.5` | Path to model directory | `models/multilingual-e5-small` |
| `EMB_MODEL_FILE` | `model.onnx` | ONNX model filename | `model.onnx` |
| `EMB_MODEL_FILE_Q` | `null` | Quantized model file (optional) | `model_q8.onnx` |
| `EMB_MAX_SEQ` | `256` | Maximum sequence length | `512` |
| `EMB_EP` | `cpu` | Execution provider | `cpu` or `dml` |
| `EMB_POOL` | `mean` | Pooling strategy | `mean` or `cls` |
| `EMB_L2` | `1` | L2 normalization (1=on, 0=off) | `1` |
| `EMB_BATCH` | `16` | Inference batch size | `32` |
| `EMB_HOST` | `127.0.0.1` | Listen host | `0.0.0.0` |
| `EMB_PORT` | `8080` | Listen port | `8080` |
| `EMB_MOCK` | `0` | Mock mode for testing | `1` |

## Running the Server

### Quick Start (Working Model)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe
```

**Note**: The default model `bge-small-en-v1.5` is missing the `model.onnx` file and cannot be used. Use `all-MiniLM-L6-v2` for English text or `multilingual-e5-small` for multilingual support.

### Running with Specific Models

#### 1. All-MiniLM-L6-v2 (English)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe
```

#### 2. Multilingual E5-Small (100+ Languages)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe
```

#### 3. Background Process
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"
Start-Process -FilePath ".\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -WorkingDirectory "." -WindowStyle Hidden
```

### Command Line Options

#### Test Mode (Single Text)
```powershell
.\EmbeddingServer.exe --text "Hello world"
```
**Output**: JSON with embedding vector

#### Health Check
```powershell
.\EmbeddingServer.exe --health
```
**Output**: "healthy"

**For complete API reference and code examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

## Quick API Test

Once your server is running, test it quickly:

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8080/healthz" -Method Get

# Single embedding  
$body = @{ text = "Hello world" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json"
```

**For comprehensive API documentation, interactive examples, and multi-language code samples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

## 🌍 Global CLI Access Setup

## 🌍 Global CLI Access Setup

For convenience, you can make `EmbeddingServer.exe` available globally from any directory:

```powershell
# Run the setup script (adds to PATH permanently)
.\scripts\setup-global-access.ps1
```

After setup, you can use these commands from anywhere:
```powershell
EmbeddingServer.exe --help      # Show help
EmbeddingServer.exe --health    # Check health  
EmbeddingServer.exe --text "hi" # Get embedding
EmbeddingServer.exe             # Start server
```

**Note**: You may need to restart your terminal after running the setup script.

**For detailed CLI documentation and advanced usage, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md#cli-reference)**

## 🌐 Interactive Web API Testing

For a user-friendly way to test the API without command line tools, use the provided HTML test interface:

### Quick Start Web Interface
```powershell
# 1. Start EmbeddingServer (in one terminal)
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe

# 2. Start web interface (in another terminal)
.\scripts\launch-web-test.ps1 -OpenBrowser
```

This will:
- ✅ Start a local HTTP server on port 3000
- 🌐 Open your browser to the API test interface
- 🧪 Provide interactive forms for all API endpoints
- 📊 Include performance testing and similarity analysis
- 🌍 Support multilingual testing examples

### Web Interface Features
- **🏥 Health Check**: Real-time server status monitoring
- **📝 Single Text Embedding**: Interactive text input with examples
- **📚 Batch Processing**: Multi-text embedding with similarity analysis
- **⚠️ Error Testing**: Validate error handling behavior
- **⚡ Performance Testing**: Automated benchmarking with statistics
- **🧠 Semantic Similarity**: Visual similarity comparison tools

**URL**: `http://localhost:3000` (or your configured port)

**Note**: The web interface requires your EmbeddingServer to be running on port 8080 (default).

## Simple Benchmarking Guide

### Quick Performance Test (Any Model)

**1. Start Server with Model**
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/YOUR_MODEL_NAME"
Start-Process -FilePath ".\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -WorkingDirectory "." -WindowStyle Hidden
Start-Sleep 5  # Wait for startup
```

**2. Run Standard Benchmark**
```powershell
.\scripts\benchmark-current-model.ps1 -Iterations 10
```

**3. Quick Manual Test**
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8080/healthz" -Method Get

# Single text test
$body = @{ text = "This is a test sentence for performance measurement." } | ConvertTo-Json
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json" }

# Batch test (10 texts)
$body = @{ texts = @(1..10 | ForEach-Object { "Test sentence number $_" }) } | ConvertTo-Json
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json" }
```

### Model Performance Comparison

#### Standard Test Results (Snapdragon X)

| Model | Single Text | Batch (10) | Throughput | Memory | Notes |
|-------|-------------|------------|------------|---------|--------|
| **all-MiniLM-L6-v2** | ~80ms | ~15ms/text | **650 texts/sec** | 1.2GB | ✅ **HIGHEST THROUGHPUT** |
| **bge-small-en-v1.5** | **~9ms** | ~5ms/text | 288 texts/sec | 1.5GB | ✅ **LOWEST LATENCY** |
| **multilingual-e5-small** | ~120ms | ~25ms/text | 400 texts/sec | 2.1GB | 100+ languages |

**Test Conditions**: Snapdragon X (X1E-78-100), 16GB RAM, medium-length sentences (8-12 words)

### Performance Analysis: Latency vs Throughput

**🚀 For Real-Time Applications (Low Latency):**
- **BGE-small-en-v1.5**: 9ms per text → Best for interactive apps, real-time search
- Use when: Chat applications, instant search, live recommendations

**⚡ For Batch Processing (High Throughput):**
- **all-MiniLM-L6-v2**: 650 texts/sec → Best for bulk processing, data pipelines  
- Use when: Document indexing, batch analysis, ETL processes

**🌐 For Multilingual Support:**
- **multilingual-e5-small**: 400 texts/sec, 100+ languages → Best for global applications
- Use when: International apps, cross-language search, diverse content

### Adding New Model Performance Data

When testing a new model, follow this procedure:

**1. Benchmark the Model**
```powershell
# Replace with your model name
$env:EMB_MODEL_DIR = "models/your-new-model"
.\scripts\benchmark-current-model.ps1 -Iterations 15
```

**2. Record Key Metrics**
- Single text latency (average)
- Batch processing per-text time  
- Peak throughput (texts/sec)
- Memory usage (Task Manager)
- Model file size

**3. Update the Performance Table Above**
Add your results to the comparison table following the same format.

### Benchmark Script Details

The `benchmark-current-model.ps1` script provides:
- **Text Length Testing**: Very short to very long texts
- **Batch Size Testing**: 1, 5, 10, 25, 50 texts per request
- **Statistical Analysis**: Min, max, average times
- **Throughput Calculation**: Texts/sec and words/sec
- **Warmup Runs**: Excludes cold-start from measurements

**Example Output:**
```
Single Text Performance by Length:
Content Type    Words   Latency     Texts/Sec   Words/Sec
Short           3       82.4ms      12.1        36
Medium          12      89.1ms      11.2        134
Long            27      95.8ms      10.4        281

Best batch size: 25 texts - 487 texts/sec
```

## Performance Testing

### Current Model Benchmark
The repository includes a comprehensive performance testing script:

```powershell
# Start server first with desired model
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"
Start-Process -FilePath ".\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -WorkingDirectory "." -WindowStyle Hidden

# Wait for startup
Start-Sleep 5

# Run comprehensive benchmark
.\scripts\benchmark-current-model.ps1 -Iterations 20
```

This script tests:
- Different text lengths (very short to very long)
- Various batch sizes (1, 5, 10, 25, 50)
- Warmup runs and statistical analysis
- Throughput and latency metrics

### Available Utility Scripts

| Script | Purpose | Usage |
|--------|---------|--------|
| `benchmark-current-model.ps1` | Performance testing | `.\scripts\benchmark-current-model.ps1 -Iterations 20` |
| `download-bge-model.ps1` | Download BGE model | `.\scripts\download-bge-model.ps1` |
| `download-e5-prebuilt.ps1` | Download multilingual model | `.\scripts\download-e5-prebuilt.ps1` |
| `extract_vocab.py` | Extract vocab from tokenizer.json | `python .\scripts\extract_vocab.py` |
| `setup-global-access.ps1` | Enable global CLI access | `.\scripts\setup-global-access.ps1` |
| `test-embed.ps1` | Basic functionality test | `.\scripts\test-embed.ps1` |
| `test-multilingual-success.ps1` | Multilingual validation | `.\scripts\test-multilingual-success.ps1` |
| `verify-environment.ps1` | Environment check | `.\scripts\verify-environment.ps1` |

### Expected Performance (Snapdragon X)
- **Single Text Latency**: 50-200ms
- **Batch Throughput**: 300-700 texts/sec
- **Optimal Batch Size**: 25-50 texts
- **Memory Usage**: ~2GB for multilingual model

## Troubleshooting

### Common Issues

#### 1. "Model file not found"
**Cause**: Incorrect `EMB_MODEL_DIR` or missing model files
**Solution**: 
```powershell
# Verify model directory exists
Get-ChildItem "models/multilingual-e5-small"

# Set correct environment variable
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"
```

#### 2. "Server not responding"
**Cause**: Server not started or port conflict
**Solution**:
```powershell
# Check if server is running
Get-Process -Name "EmbeddingServer" -ErrorAction SilentlyContinue

# Kill existing process
Stop-Process -Name "EmbeddingServer" -Force -ErrorAction SilentlyContinue

# Start fresh
Start-Process -FilePath ".\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -WorkingDirectory "."
```

#### 3. "Build failed"
**Cause**: Missing .NET 8 SDK or wrong directory
**Solution**:
```powershell
# Verify .NET version
dotnet --version

# Build from correct directory
cd C:\Learn\Code\fastembed\EmbeddingServer\src
dotnet build -c Release
```

#### 4. "500 Internal Server Error"
**Cause**: Model loading issues or missing vocabulary files
**Solution**:
```powershell
# Check server logs by running in foreground
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe

# Verify all required model files exist
Get-ChildItem "models/multilingual-e5-small" | Format-Table Name, Length
```

### Diagnostic Commands

#### Check Server Status
```powershell
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/healthz" -Method Get
    Write-Host "Server Status: $($health.status)" -ForegroundColor Green
    Write-Host "Model: $($health.model), Dimension: $($health.dimension)" -ForegroundColor Green
} catch {
    Write-Host "Server not responding: $($_.Exception.Message)" -ForegroundColor Red
}
```

#### Process Management
```powershell
# Find server process
Get-Process -Name "EmbeddingServer" -ErrorAction SilentlyContinue

# Stop server
Stop-Process -Name "EmbeddingServer" -Force -ErrorAction SilentlyContinue

# Verify port is free
Test-NetConnection -ComputerName localhost -Port 8080 -InformationLevel Quiet
```

### Performance Optimization

#### For Maximum Speed
```powershell
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"  # Smaller model
$env:EMB_BATCH = "32"                           # Larger batch size
$env:EMB_MAX_SEQ = "128"                       # Shorter sequences
```

#### For Maximum Quality
```powershell
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"  # Larger model
$env:EMB_MAX_SEQ = "512"                             # Longer sequences
$env:EMB_BATCH = "16"                                # Conservative batch
```

#### For Development/Testing
```powershell
$env:EMB_MOCK = "1"                            # Mock mode (no model loading)
$env:EMB_HOST = "0.0.0.0"                     # Allow external connections
```

## Model Management

### Adding New Models
1. Create directory: `models/your-model-name/`
2. Place required files: `model.onnx`, `vocab.txt` (minimum)
3. Optional files: `tokenizer.json`, `config.json`
4. Set environment: `$env:EMB_MODEL_DIR = "models/your-model-name"`

### Model File Requirements
- **Required**: `model.onnx` (ONNX format embedding model)
- **Required**: `vocab.txt` OR `tokenizer.json` (vocabulary/tokenizer)
- **Optional**: `config.json` (model configuration)
- **Optional**: Quantized versions for faster inference

---

## Quick Reference Card

### Essential Commands

#### Start Server (English Model)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe
```

#### Start Server (Multilingual Model)
```powershell
cd C:\Learn\Code\fastembed\EmbeddingServer
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe
```

#### Test Health
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/healthz" -Method Get
```

#### Single Text Embedding
```powershell
$body = @{ text = "Your text here" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json"
```

#### Batch Text Embedding
```powershell
$body = @{ texts = @("Text 1", "Text 2", "Text 3") } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json"
```

#### Performance Test
```powershell
.\scripts\benchmark-current-model.ps1 -Iterations 10
```

#### CLI Mode (No Server)
```powershell
$env:EMB_MODEL_DIR = "models/all-MiniLM-L6-v2"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe --text "Hello world"
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe --health
.\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe --help
```

#### Stop Server
```powershell
Stop-Process -Name "EmbeddingServer" -Force
```

### Model Quick Switch
```powershell
# Stop current server
Stop-Process -Name "EmbeddingServer" -Force

# Start with different model
$env:EMB_MODEL_DIR = "models/multilingual-e5-small"  # or "models/all-MiniLM-L6-v2"
Start-Process -FilePath ".\src\bin\Release\net8.0\win-arm64\EmbeddingServer.exe" -WorkingDirectory "." -WindowStyle Hidden
```

### Benchmarking Quick Commands
```powershell
# Quick single test
$body = @{ text = "Performance test sentence" } | ConvertTo-Json
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8080/embed" -Method Post -Body $body -ContentType "application/json" }

# Comprehensive benchmark
.\scripts\benchmark-current-model.ps1 -Iterations 15
```

---

## Maintenance Guidelines

### Current Repository Structure Overview
The repository maintains a clean documentation structure:
- **INSTRUCTIONS.md** (this file): Setup, deployment, and operations
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**: Complete developer API reference
- **README.md**: Project overview and quick start
- **DEPENDENCIES.md**: Dependency information
- **indian-language-support.md**: Multilingual capabilities
- **8 Essential Scripts**: benchmark-current-model.ps1, download-bge-model.ps1, download-e5-prebuilt.ps1, extract_vocab.py, setup-global-access.ps1, test-embed.ps1, test-multilingual-success.ps1, verify-environment.ps1

### Three-Model Configuration
1. **all-MiniLM-L6-v2** (86MB): English-focused, high throughput (650 texts/sec)
2. **bge-small-en-v1.5** (127MB): English-focused, low latency (9ms per text)
3. **multilingual-e5-small** (448MB): 100+ languages, balanced performance (400 texts/sec)

### 📋 IMPORTANT: Keep Documentation Updated

**When making ANY changes to this repository, you MUST update the relevant documentation:**

1. **Code Changes**: Update API examples in API_DOCUMENTATION.md or configuration in INSTRUCTIONS.md
2. **New Models**: Add model specifications to the "Available Models" section
3. **New Scripts**: Document usage in appropriate sections
4. **Bug Fixes**: Update troubleshooting sections in both files
5. **Performance Changes**: Update expected performance metrics
6. **API Changes**: Update API_DOCUMENTATION.md with new endpoints or parameters

### Regular Maintenance Tasks

1. **Monthly Model Updates**
   - Check for new model versions on Hugging Face
   - Test new models with existing benchmarking framework
   - Update performance documentation if models change

2. **Quarterly Dependency Review**
   - Update ONNX Runtime to latest stable version
   - Verify compatibility with .NET updates
   - Run full test suite after updates

3. **Documentation Consistency**
   - Keep INSTRUCTIONS.md focused on setup and operations
   - Keep API_DOCUMENTATION.md focused on developer integration
   - Update benchmarks when hardware or models change
   - Maintain script documentation table accuracy

4. **Performance Monitoring**
   - Run benchmarks after system updates
   - Monitor for performance regressions
   - Document optimal configurations

### File Organization Rules
- Keep only essential files (current: 12 files total)
- Remove temporary/test files after use
- Maintain clear separation between docs and scripts
- Use consistent naming conventions

### Quality Assurance
- Test all three models before major releases
- Verify CLI functionality with --help, --text, --health
- Ensure global PATH integration works
- Validate multilingual capabilities regularly

### Update Process:
```powershell
# After making changes, always update:
# 1. Edit INSTRUCTIONS.md for setup/config changes
# 2. Edit API_DOCUMENTATION.md for API/integration changes  
# 3. Test documented procedures
# 4. Update version date below
```

**🚨 Rule: No code changes without corresponding documentation updates!**

**For API usage, code examples, and integration help, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

---

**Last Updated**: September 2025  
**Platform**: Windows ARM64 (.NET 8)  
**Version**: EmbeddingServer v1.0  
**Repository Status**: ✅ Clean - No temporary files