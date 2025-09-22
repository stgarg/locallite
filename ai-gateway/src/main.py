#!/usr/bin/env python3
"""
Production AI Gateway with NPU acceleration
Clean implementation with automatic performance optimization
"""
import os
import time
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# Core FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# System monitoring
import psutil

# Import our optimized embedding engine
from embedding_engine import OptimizedEmbeddingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === OpenAI-Compatible Data Models ===
class EmbeddingRequest(BaseModel):
    input: List[str] | str
    model: str = "bge-small-en-v1.5"
    encoding_format: str = "float"
    dimensions: Optional[int] = None

class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: Dict[str, int]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = int(time.time())
    owned_by: str = "local"

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

class HealthResponse(BaseModel):
    status: str
    npu_available: bool
    models_loaded: List[str]
    memory_usage: Dict[str, float]
    performance_stats: Dict[str, Any]
    uptime_seconds: float

# === Application State ===
class AppState:
    def __init__(self):
        self.embedding_engine: Optional[OptimizedEmbeddingEngine] = None
        self.start_time = time.time()
        self.request_count = 0
        self.total_texts_processed = 0
        self.npu_requests = 0
        self.cpu_requests = 0

app_state = AppState()

# === Security ===
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple API key verification - enhance for production"""
    # For local development, we're permissive
    # In production, implement proper API key validation
    return True

# === Application Lifecycle ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info("🚀 Starting AI Gateway...")
    
    try:
        # Initialize embedding engine
        model_path = "C:/Learn/Code/fastembed/EmbeddingServer/models/bge-small-en-v1.5"
        app_state.embedding_engine = OptimizedEmbeddingEngine(model_path)
        
        # Log system information
        model_info = app_state.embedding_engine.get_model_info()
        logger.info(f"✅ Model loaded: {model_info['model_config']['model_type']}")
        logger.info(f"✅ NPU available: {model_info['providers']['npu_available']}")
        logger.info(f"✅ Vocab size: {model_info['vocab_size']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize embedding engine: {e}")
        app_state.embedding_engine = None
    
    logger.info("✅ AI Gateway ready!")
    
    yield  # Server is running
    
    logger.info("🛑 Shutting down AI Gateway...")

# === FastAPI Application ===
app = FastAPI(
    title="AI Gateway",
    description="OpenAI-compatible API with automatic NPU/CPU optimization",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API Endpoints ===

@app.get("/")
async def root():
    """API information and status"""
    return {
        "name": "AI Gateway",
        "version": "2.0.0",
        "description": "OpenAI-compatible API with automatic NPU/CPU optimization",
        "status": "running",
        "features": [
            "NPU acceleration for small batches (1-3 texts)",
            "CPU optimization for large batches (4+ texts)",
            "Automatic provider selection",
            "OpenAI-compatible endpoints"
        ],
        "endpoints": {
            "health": "/health",
            "models": "/v1/models", 
            "embeddings": "/v1/embeddings",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check with performance metrics"""
    if not app_state.embedding_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding engine not available"
        )
    
    # Get system memory info
    memory = psutil.virtual_memory()
    
    # Calculate performance stats
    uptime = time.time() - app_state.start_time
    avg_texts_per_request = (app_state.total_texts_processed / app_state.request_count 
                           if app_state.request_count > 0 else 0)
    npu_usage_percentage = ((app_state.npu_requests / app_state.request_count * 100) 
                          if app_state.request_count > 0 else 0)
    
    # Get engine health
    engine_health = app_state.embedding_engine.health_check()
    model_info = app_state.embedding_engine.get_model_info()
    
    return HealthResponse(
        status="healthy",
        npu_available=model_info['providers']['npu_available'],
        models_loaded=["bge-small-en-v1.5"],
        memory_usage={
            "used_gb": memory.used / (1024**3),
            "total_gb": memory.total / (1024**3),
            "percent": memory.percent,
            "available_gb": memory.available / (1024**3)
        },
        performance_stats={
            "total_requests": app_state.request_count,
            "total_texts_processed": app_state.total_texts_processed,
            "npu_requests": app_state.npu_requests,
            "cpu_requests": app_state.cpu_requests,
            "npu_usage_percentage": round(npu_usage_percentage, 1),
            "avg_texts_per_request": round(avg_texts_per_request, 1),
            "requests_per_minute": round(app_state.request_count / (uptime / 60), 1) if uptime > 0 else 0
        },
        uptime_seconds=uptime
    )

@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(authorized: bool = Depends(verify_api_key)):
    """List available models (OpenAI-compatible)"""
    models = [
        ModelInfo(id="bge-small-en-v1.5"),
    ]
    return ModelsResponse(data=models)

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    authorized: bool = Depends(verify_api_key)
):
    """
    Generate embeddings with automatic NPU/CPU optimization
    
    Automatically selects:
    - NPU for 1-3 texts (up to 2.33x faster)
    - CPU for 4+ texts (more efficient for larger batches)
    """
    if not app_state.embedding_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding engine not available"
        )
    
    try:
        # Normalize input to list
        texts = request.input if isinstance(request.input, list) else [request.input]
        
        if not texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input cannot be empty"
            )
        
        if len(texts) > 100:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many texts in batch (max 100)"
            )
        
        # Generate embeddings (automatic provider selection)
        embeddings_array, performance_info = app_state.embedding_engine.encode(texts)
        
        # Update statistics
        app_state.request_count += 1
        app_state.total_texts_processed += len(texts)
        if performance_info['provider'] == 'NPU':
            app_state.npu_requests += 1
        else:
            app_state.cpu_requests += 1
        
        # Convert to OpenAI format
        embeddings_data = [
            EmbeddingData(embedding=embedding.tolist(), index=i)
            for i, embedding in enumerate(embeddings_array)
        ]
        
        # Log performance for monitoring
        logger.info(
            f"Generated {len(embeddings_data)} embeddings using {performance_info['provider']} "
            f"in {performance_info['total_time_ms']:.1f}ms "
            f"({performance_info['avg_time_per_text_ms']:.1f}ms/text)"
        )
        
        return EmbeddingResponse(
            data=embeddings_data,
            model=request.model,
            usage={
                "prompt_tokens": sum(len(text.split()) for text in texts),
                "total_tokens": sum(len(text.split()) for text in texts)
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate embeddings"
        )

# === Development Server ===
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )