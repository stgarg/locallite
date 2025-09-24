#!/usr/bin/env python3
"""
AI Gateway - OpenAI-compatible API with NPU acceleration
Minimal implementation for Phase 1: Embeddings with NPU
"""
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Import our embedding engine
from embedding_engine import EmbeddingEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Models for OpenAI-compatible API
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
    uptime_seconds: float


# Global state
class AppState:
    def __init__(self):
        self.embedding_engine = None
        self.npu_available = False
        self.start_time = time.time()
        self.models_loaded = []


app_state = AppState()

# Security
security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple API key verification"""
    # For local use, we'll be permissive for now
    # In production, check against configured API keys
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic"""
    logger.info("Starting AI Gateway...")

    # Initialize NPU detection
    try:
        import onnxruntime as ort

        providers = ort.get_available_providers()
        app_state.npu_available = "QNNExecutionProvider" in providers
        logger.info(f"NPU Available: {app_state.npu_available}")
        logger.info(f"Available providers: {providers}")
    except Exception as e:
        logger.error(f"Failed to detect NPU: {e}")
        app_state.npu_available = False

    # Initialize embedding engine
    try:
        model_path = "C:/Learn/Code/fastembed/EmbeddingServer/models/bge-small-en-v1.5"
        app_state.embedding_engine = EmbeddingEngine(
            model_path, use_npu=app_state.npu_available
        )
        app_state.models_loaded = ["bge-small-en-v1.5"]
        logger.info("Embedding engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedding engine: {e}")
        app_state.embedding_engine = None

    logger.info("AI Gateway started successfully")

    yield

    logger.info("Shutting down AI Gateway...")
    # Cleanup logic here


# Initialize FastAPI app
app = FastAPI(
    title="AI Gateway",
    description="OpenAI-compatible API with NPU acceleration",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import psutil

    return HealthResponse(
        status="healthy",
        npu_available=app_state.npu_available,
        models_loaded=app_state.models_loaded,
        memory_usage={
            "used_gb": psutil.virtual_memory().used / (1024**3),
            "total_gb": psutil.virtual_memory().total / (1024**3),
            "percent": psutil.virtual_memory().percent,
        },
        uptime_seconds=time.time() - app_state.start_time,
    )


@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(authorized: bool = Depends(verify_token)):
    """List available models (OpenAI-compatible)"""
    models = [
        ModelInfo(id="bge-small-en-v1.5"),
        ModelInfo(id="e5-small-v2"),
    ]
    return ModelsResponse(data=models)


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest, authorized: bool = Depends(verify_token)
):
    """Generate embeddings (OpenAI-compatible)"""
    try:
        # Check if embedding engine is available
        if not app_state.embedding_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embedding engine not available",
            )

        # Normalize input to list
        texts = request.input if isinstance(request.input, list) else [request.input]

        if not texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Input cannot be empty"
            )

        # Intelligent NPU/CPU routing based on batch size
        # Use NPU for small batches (1-3 texts), CPU for larger batches
        use_npu = len(texts) <= 3 and app_state.npu_available

        # Generate embeddings using our engine
        embeddings_array, timing_info = app_state.embedding_engine.encode(
            texts, use_npu=use_npu
        )

        # Convert to OpenAI format
        embeddings = []
        for i, embedding in enumerate(embeddings_array):
            embeddings.append(EmbeddingData(embedding=embedding.tolist(), index=i))

        logger.info(
            f"Generated {len(embeddings)} embeddings using {timing_info['provider']} "
            f"in {timing_info['total_time']:.3f}s"
        )

        return EmbeddingResponse(
            data=embeddings,
            model=request.model,
            usage={
                "prompt_tokens": sum(len(text.split()) for text in texts),
                "total_tokens": sum(len(text.split()) for text in texts),
            },
        )

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}",
        )


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "AI Gateway",
        "version": "1.0.0",
        "status": "running",
        "npu_available": app_state.npu_available,
        "endpoints": ["/health", "/v1/models", "/v1/embeddings"],
    }


if __name__ == "__main__":
    # psutil is included in requirements.txt for health monitoring
    import psutil

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")
