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
import os
import time
import logging
import uuid
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Import our embedding engine and chat router
from embedding_engine import OptimizedEmbeddingEngine
from simple_router import ModelRouter, RequestType, UnifiedRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI-compatible API Models
class EmbeddingRequest(BaseModel):
    """Request model for embedding generation."""
    input: Union[List[str], str] = Field(..., description="Text(s) to embed")
    model: str = Field(default="bge-small-en-v1.5", description="Model to use for embedding")
    encoding_format: str = Field(default="float", description="Encoding format")
    dimensions: Optional[int] = Field(None, description="Number of dimensions (optional)")

class EmbeddingData(BaseModel):
    """Individual embedding data."""
    object: str = "embedding"
    embedding: List[float] = Field(..., description="The embedding vector")
    index: int = Field(..., description="Index of the embedding in the batch")

class EmbeddingResponse(BaseModel):
    """Response model for embedding generation."""
    object: str = "list"
    data: List[EmbeddingData] = Field(..., description="List of embeddings")
    model: str = Field(..., description="Model used")
    usage: Dict[str, int] = Field(..., description="Token usage information")

class ModelInfo(BaseModel):
    """Information about an available model."""
    id: str = Field(..., description="Model identifier")
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()), description="Creation timestamp")
    owned_by: str = "local"

class ModelsResponse(BaseModel):
    """Response model for listing available models."""
    object: str = "list"
    data: List[ModelInfo] = Field(..., description="List of available models")

# Chat completion models
class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    """Request model for chat completion."""
    model: str = Field(..., description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    max_tokens: Optional[int] = Field(150, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    stream: Optional[bool] = Field(False, description="Stream response")

class ChatChoice(BaseModel):
    """Individual chat completion choice."""
    index: int = Field(..., description="Choice index")
    message: ChatMessage = Field(..., description="Generated message")
    finish_reason: str = Field(..., description="Reason for completion")

class ChatUsage(BaseModel):
    """Token usage information for chat completion."""
    prompt_tokens: int = Field(..., description="Tokens in prompt")
    completion_tokens: int = Field(..., description="Tokens in completion")
    total_tokens: int = Field(..., description="Total tokens used")

class ChatCompletionResponse(BaseModel):
    """Response model for chat completion."""
    id: str = Field(..., description="Completion ID")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()), description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[ChatChoice] = Field(..., description="Generated choices")
    usage: ChatUsage = Field(..., description="Token usage")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    npu_available: bool = Field(..., description="NPU availability")
    models_loaded: List[str] = Field(..., description="Currently loaded models")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")
    uptime_seconds: float = Field(..., description="Service uptime")

# Global application state
class AppState:
    """Global application state container."""
    
    def __init__(self) -> None:
        self.embedding_engine: Optional[OptimizedEmbeddingEngine] = None
        self.model_router: Optional[ModelRouter] = None
        self.npu_available: bool = False
        self.start_time: float = time.time()
        self.models_loaded: List[str] = []

app_state = AppState()

# Security
security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """
    Simple API key verification.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        True if authorized (currently permissive for local use)
        
    Note:
        In production, this should check against configured API keys
    """
    # For local use, we'll be permissive for now
    # In production, check against configured API keys
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown logic.
    
    Initializes:
    - NPU detection and provider setup
    - Embedding engine with automatic provider selection
    - Chat model router with Phi-3 Mini
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Starting AI Gateway...")
    
    # Initialize NPU detection
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        app_state.npu_available = 'QNNExecutionProvider' in providers
        logger.info(f"NPU Available: {app_state.npu_available}")
        logger.info(f"Available providers: {providers}")
    except Exception as e:
        logger.error(f"Failed to detect NPU: {e}")
        app_state.npu_available = False
    
    # Initialize embedding engine
    try:
        model_path = "C:/Learn/Code/fastembed/EmbeddingServer/models/bge-small-en-v1.5"
        app_state.embedding_engine = OptimizedEmbeddingEngine(model_path)
        app_state.models_loaded.append("bge-small-en-v1.5")
        logger.info("Embedding engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embedding engine: {e}")
        app_state.embedding_engine = None
    
    # Initialize chat model router
    try:
        app_state.model_router = ModelRouter()
        if await app_state.model_router.initialize():
            app_state.models_loaded.append("phi-3-mini-4k")
            logger.info("Chat model router initialized successfully")
        else:
            logger.warning("Chat model router failed to initialize")
    except Exception as e:
        logger.error(f"Failed to initialize chat model router: {e}")
        app_state.model_router = None
    
    logger.info("AI Gateway started successfully")
    
    yield
    
    logger.info("Shutting down AI Gateway...")
    # Cleanup logic here

# Initialize FastAPI app
app = FastAPI(
    title="AI Gateway",
    description="OpenAI-compatible API with NPU acceleration",
    version="1.0.0",
    lifespan=lifespan
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
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Returns:
        HealthResponse containing:
        - Service status
        - NPU availability  
        - Loaded models list
        - Memory usage statistics
        - Service uptime
    """
    import psutil
    
    return HealthResponse(
        status="healthy",
        npu_available=app_state.npu_available,
        models_loaded=app_state.models_loaded,
        memory_usage={
            "used_gb": psutil.virtual_memory().used / (1024**3),
            "total_gb": psutil.virtual_memory().total / (1024**3),
            "percent": psutil.virtual_memory().percent
        },
        uptime_seconds=time.time() - app_state.start_time
    )

@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(authorized: bool = Depends(verify_token)) -> ModelsResponse:
    """
    List available models (OpenAI-compatible).
    
    Args:
        authorized: Token verification result
        
    Returns:
        ModelsResponse containing available models:
        - bge-small-en-v1.5 (embeddings with NPU support)
        - e5-small-v2 (embeddings, placeholder)  
        - phi-3-mini-4k (chat completions with ONNX)
    """
    models = [
        ModelInfo(id="bge-small-en-v1.5"),
        ModelInfo(id="e5-small-v2"),
        ModelInfo(id="phi-3-mini-4k"),  # Add chat model
    ]
    return ModelsResponse(data=models)

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    authorized: bool = Depends(verify_token)
):
    """Generate embeddings (OpenAI-compatible)"""
    try:
        # Check if embedding engine is available
        if not app_state.embedding_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embedding engine not available"
            )
        
        # Normalize input to list
        texts = request.input if isinstance(request.input, list) else [request.input]
        
        if not texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input cannot be empty"
            )
        
        # Intelligent NPU/CPU routing based on batch size
        # OptimizedEmbeddingEngine handles NPU/CPU selection automatically
        
        # Generate embeddings using our engine
        embeddings_array, timing_info = app_state.embedding_engine.encode(texts)
        
        # Convert to OpenAI format
        embeddings = []
        for i, embedding in enumerate(embeddings_array):
            embeddings.append(EmbeddingData(
                embedding=embedding.tolist(),
                index=i
            ))
        
        logger.info(f"Generated {len(embeddings)} embeddings using {timing_info['provider']} "
                   f"in {timing_info['total_time_ms']:.1f}ms")
        
        return EmbeddingResponse(
            data=embeddings,
            model=request.model,
            usage={
                "prompt_tokens": sum(len(text.split()) for text in texts),
                "total_tokens": sum(len(text.split()) for text in texts)
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorized: bool = Depends(verify_token)
):
    """Generate chat completions (OpenAI-compatible)"""
    try:
        # Check if model router is available
        if not app_state.model_router:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat model not available"
            )
        
        # Create unified request
        import uuid
        unified_request = UnifiedRequest(
            id=f"chatcmpl-{str(uuid.uuid4())[:8]}",
            request_type=RequestType.CHAT_COMPLETION,
            model_id=request.model,
            content={
                "messages": [msg.model_dump() for msg in request.messages],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
        )
        
        # Process request through model router
        start_time = time.time()
        response = await app_state.model_router.process_request(unified_request)
        processing_time = time.time() - start_time
        
        # Convert to OpenAI format
        choices = []
        for choice_data in response.content["choices"]:
            choices.append(ChatChoice(
                index=choice_data["index"],
                message=ChatMessage(
                    role=choice_data["message"]["role"],
                    content=choice_data["message"]["content"]
                ),
                finish_reason=choice_data["finish_reason"]
            ))
        
        usage_data = response.content.get("usage", {})
        usage = ChatUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        logger.info(f"Chat completion generated in {processing_time:.3f}s using {request.model}")
        
        return ChatCompletionResponse(
            id=response.id,
            created=int(time.time()),
            model=request.model,
            choices=choices,
            usage=usage
        )
        
    except Exception as e:
        logger.error(f"Error creating chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat completion"
        )

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "AI Gateway",
        "version": "1.0.0",
        "status": "running",
        "npu_available": app_state.npu_available,
        "endpoints": [
            "/health",
            "/v1/models",
            "/v1/embeddings",
            "/v1/chat/completions"
        ]
    }

if __name__ == "__main__":
    # Add psutil for health monitoring
    try:
        import psutil
    except ImportError:
        os.system("pip install psutil")
        import psutil
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )