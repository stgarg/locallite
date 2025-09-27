#!/usr/bin/env python3
"""
AI Gateway - OpenAI-compatible API with NPU acceleration

A production-ready API gateway that provides OpenAI-compatible endpoints for:
- Text embeddings with NPU acceleration (bge-small-en-v1.5)  
- Chat completions with Phi-3 Mini ONNX inference

Features:
- Automatic NPU/CPU provider selection for optimal performance
- Real ONNX model inference with proper tokenization
- OpenAI-compatible API format for drop-in replacement
- Comprehensive error handling and monitoring

Author: AI Gateway Team
Version: 1.0.0
Date: September 2025
"""

# Import the actual model router FastAPI app
from model_router import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")