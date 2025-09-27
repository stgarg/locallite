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

from services import ChatService, EmbeddingService, MetricsService, ModelService
from runtime.model_registry import MODEL_REGISTRY, list_models as registry_list_models

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


class RegistryModelInfo(BaseModel):
    id: str
    task: str
    backend: str
    dimension: Optional[int] = None
    license: Optional[str] = None
    revision: Optional[str] = None
    notes: Optional[str] = None
    capabilities: Dict[str, Any] = {}


class RegistryModelsResponse(BaseModel):
    object: str = "list"
    data: List[RegistryModelInfo]


class HealthResponse(BaseModel):
    status: str
    npu_available: bool
    models_loaded: List[str]
    memory_usage: Dict[str, float]
    uptime_seconds: float
    performance_stats: Dict[str, Any] = Field(default_factory=dict)


# Chat completion models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of." \
    " the message (system, user, assistant)")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="gemma-3n-4b", description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=512, ge=1)
    stream: bool = Field(default=False)


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


# Global state
class AppState:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chat_service = ChatService()
        self.model_service = ModelService()
        self.metrics_service = MetricsService()
        self.npu_available = False
        self.start_time = time.time()
        self.models_loaded: List[str] = []




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

    # Initialize model services
    await app_state.model_service.initialize()

    # Initialize embedding service
    # Resolve embedding model path: prefer env, else use archived EmbeddingServer asset if present.
    embedding_model_path = os.getenv("EMBEDDING_MODEL_PATH")
    if not embedding_model_path:
        # Try co-located archived path first
        candidate = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "EmbeddingServer", "models", "bge-small-en-v1.5"))
        if os.path.exists(os.path.join(candidate, "model.onnx")):
            embedding_model_path = candidate
        else:
            # Final fallback: models/ path under repo root
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            alt = os.path.join(repo_root, "models", "bge-small-en-v1.5")
            embedding_model_path = alt
    logger.info(f"Using embedding model path: {embedding_model_path}")
    try:
        embedding_loaded = await app_state.embedding_service.initialize(embedding_model_path)
        if embedding_loaded:
            app_state.models_loaded.append("bge-small-en-v1.5")
            logger.info("Embedding service initialized successfully")
        else:
            logger.error("Failed to initialize embedding service")
    except Exception as exc:
        logger.error(f"Failed to initialize embedding service: {exc}")

    # Load Gemma chat model via model service
    chat_model_path = os.getenv("CHAT_MODEL_PATH")
    if not chat_model_path:
        # Prefer repo models/gemma-3n if exists
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        candidate = os.path.join(repo_root, "models", "gemma-3n")
        if os.path.isdir(candidate):
            chat_model_path = candidate
        else:
            # Fallback to archived EmbeddingServer path pattern if someone kept older layout
            alt = os.path.join(repo_root, "EmbeddingServer", "models", "gemma-3n")
            chat_model_path = alt
    logger.info(f"Using chat model path: {chat_model_path}")
    try:
        chat_loaded = await app_state.model_service.load_model(
            model_id="gemma-3n-4b",
            model_path=chat_model_path,
            model_type="chat",
        )
        if chat_loaded:
            await app_state.chat_service.initialize(app_state.model_service)
            app_state.models_loaded.append("gemma-3n-4b")
            logger.info("Gemma chat model initialized successfully")
        else:
            logger.error("Failed to load Gemma chat model")
    except Exception as exc:
        logger.error(f"Failed to initialize Gemma chat model: {exc}")

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

    embedding_stats = (
        app_state.embedding_service.health_check()
        if app_state.embedding_service
        else {"status": "unavailable"}
    )

    chat_models = app_state.model_service.list_models_by_type("chat")
    if chat_models:
        model_id = chat_models[0]
        model = app_state.model_service.get_model(model_id)
        chat_stats = {
            "status": "loaded",
            "models": chat_models,
            "health": model.health_check() if hasattr(model, "health_check") else {},
        }
    else:
        chat_stats = {"status": "unavailable"}

    models_loaded = []
    if getattr(app_state.embedding_service, "_is_initialized", False):
        models_loaded.append("bge-small-en-v1.5")
    models_loaded.extend(app_state.model_service.get_available_models())
    app_state.models_loaded = list(dict.fromkeys(models_loaded))

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
        performance_stats={
            "embedding": embedding_stats,
            "chat": chat_stats,
            "uptime_seconds": time.time() - app_state.start_time,
        },
    )


@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(authorized: bool = Depends(verify_token)):
    """List available models (OpenAI-compatible minimal view).

    Maintains backward compatibility (only id/object fields) while sourcing
    model ids from both the static registry and dynamically loaded models.
    """
    models: Dict[str, ModelInfo] = {}

    # Static registry seeds
    for spec in MODEL_REGISTRY.values():
        models.setdefault(spec.model_id, ModelInfo(id=spec.model_id))

    # Dynamically loaded models (may include ones not in static registry yet)
    for model_id in app_state.model_service.get_available_models():
        models.setdefault(model_id, ModelInfo(id=model_id))

    # Only include models actually initialized / loadable for embeddings/chat if required
    # (For now we expose all known ids; future: filter by health)
    return ModelsResponse(data=list(models.values()))


@app.get("/v1/models/registry", response_model=RegistryModelsResponse)
async def list_registry_models(authorized: bool = Depends(verify_token)):
    """Extended model metadata (internal/non-OpenAI extension).

    Exposes backend, dimension, license, capabilities for tooling & UI.
    """
    extended: List[RegistryModelInfo] = []
    for spec in registry_list_models():
        extended.append(
            RegistryModelInfo(
                id=spec.model_id,
                task=spec.task,
                backend=spec.backend,
                dimension=spec.dimension,
                license=spec.license,
                revision=spec.revision,
                notes=spec.notes,
                capabilities=spec.capabilities,
            )
        )
    return RegistryModelsResponse(data=extended)


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest, authorized: bool = Depends(verify_token)
):
    """Generate embeddings (OpenAI-compatible)"""
    try:
        # Check if embedding service is available
        if not getattr(app_state.embedding_service, "_is_initialized", False):
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

        try:
            result = await app_state.embedding_service.process_embeddings(texts, model=request.model)
        except FileNotFoundError as fnf:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Embedding model assets missing: {fnf}")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Embedding processing failed: {exc}")

        embeddings: List[EmbeddingData] = []
        for idx, embedding in enumerate(result.embeddings):
            if embedding is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.errors[idx] or "Failed to generate embedding",
                )
            embeddings.append(EmbeddingData(embedding=embedding, index=idx))

        logger.info(
            "Generated %s embeddings using %s in %.3fs",
            len(embeddings),
            result.provider_used,
            result.processing_time_ms / 1000,
        )

        return EmbeddingResponse(
            data=embeddings,
            model=request.model,
            usage={
                "prompt_tokens": result.tokens,
                "total_tokens": result.tokens,
            },
        )

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}",
        )


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest, authorized: bool = Depends(verify_token)
):
    """Generate chat completion (OpenAI-compatible)"""
    try:
        # Check if chat service is available
        if not getattr(app_state.chat_service, "_is_initialized", False):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat model not available",
            )

        # Validate messages
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Messages cannot be empty"
            )

        # Convert Pydantic models to dicts for processing
        messages_dict = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        chat_result = await app_state.chat_service.process_chat(
            messages=messages_dict,
            model=request.model,
            stream=request.stream,
            max_tokens=request.max_tokens or 512,
            temperature=request.temperature,
            top_p=1.0,
            stop=None,
        )

        completion_id = chat_result.request_id
        choice = ChatCompletionChoice(
            index=0,
            message=ChatMessage(role="assistant", content=chat_result.content),
            finish_reason=chat_result.finish_reason,
        )

        usage = ChatCompletionUsage(
            prompt_tokens=chat_result.input_tokens,
            completion_tokens=chat_result.output_tokens,
            total_tokens=chat_result.total_tokens,
        )

        logger.info(
            "Generated chat completion in %.3fs (model=%s, tokens=%s)",
            chat_result.processing_time_ms / 1000,
            chat_result.model_used,
            chat_result.total_tokens,
        )

        return ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=chat_result.model_used,
            choices=[choice],
            usage=usage,
        )

    except Exception as e:
        logger.error(f"Error generating chat completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chat completion: {str(e)}",
        )


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "AI Gateway",
        "version": "1.0.0",
        "status": "running",
        "npu_available": app_state.npu_available,
        "endpoints": ["/health", "/v1/models", "/v1/embeddings", "/v1/chat/completions"],
    }


if __name__ == "__main__":
    # psutil is included in requirements.txt for health monitoring
    import psutil

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_level="info")
