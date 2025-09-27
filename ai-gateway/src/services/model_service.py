"""
Shared Model Service
Core model loading and management logic
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"


@dataclass
class ModelInfo:
    """Information about a loaded model"""

    model_id: str
    model_type: str
    status: ModelStatus
    load_time: Optional[float]
    memory_usage: Optional[int]
    provider: Optional[str]
    capabilities: List[str]
    metadata: Dict[str, Any]


class ModelService:
    """
    Core model service for loading and managing models

    Handles:
    - Model loading and unloading
    - Memory management
    - Model metadata and capabilities
    - Health monitoring of loaded models
    """

    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.model_info: Dict[str, ModelInfo] = {}
        self._initialization_lock = asyncio.Lock()
        self.default_models: Dict[str, str] = {}

    async def initialize(self) -> bool:
        """Initialize the model service"""
        try:
            logger.info("✅ ModelService initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize ModelService: {e}")
            return False

    async def load_model(self, model_id: str, model_path: str, model_type: str) -> bool:
        """
        Load a model into memory

        Args:
            model_id: Unique identifier for the model
            model_path: Path to model files
            model_type: Type of model (embeddings, chat, etc.)
        """
        async with self._initialization_lock:
            try:
                if model_id in self.loaded_models:
                    logger.info(f"Model {model_id} already loaded")
                    return True

                # Create model info entry
                self.model_info[model_id] = ModelInfo(
                    model_id=model_id,
                    model_type=model_type,
                    status=ModelStatus.LOADING,
                    load_time=None,
                    memory_usage=None,
                    provider=None,
                    capabilities=[],
                    metadata={"path": model_path},
                )

                logger.info(f"Loading {model_type} model: {model_id}")

                # Load based on model type
                if model_type == "embeddings":
                    model_instance = await self._load_embedding_model(
                        model_id, model_path
                    )
                elif model_type == "chat":
                    model_instance = await self._load_chat_model(model_id, model_path)
                else:
                    raise ValueError(f"Unknown model type: {model_type}")

                if model_instance:
                    self.loaded_models[model_id] = model_instance
                    self.model_info[model_id].status = ModelStatus.LOADED
                    provider = getattr(model_instance, "providers", None)
                    if provider:
                        if isinstance(provider, list):
                            provider_desc = ",".join(provider)
                        else:
                            provider_desc = str(provider)
                        self.model_info[model_id].provider = provider_desc
                    self.default_models.setdefault(model_type, model_id)
                    logger.info(f"✅ Successfully loaded {model_id}")
                    return True
                else:
                    self.model_info[model_id].status = ModelStatus.ERROR
                    return False

            except Exception as e:
                logger.error(f"❌ Failed to load model {model_id}: {e}")
                if model_id in self.model_info:
                    self.model_info[model_id].status = ModelStatus.ERROR
                    self.model_info[model_id].metadata["error"] = str(e)
                return False

    async def _load_embedding_model(self, model_id: str, model_path: str):
        """Load an embedding model"""
        from embedding_engine import OptimizedEmbeddingEngine

        return OptimizedEmbeddingEngine(model_path)

    async def _load_chat_model(self, model_id: str, model_path: str):
        """Load a chat model"""
        from chat.gemma_model import GemmaChatModel

        chat_model = GemmaChatModel(model_id=model_id, model_path=model_path)
        success = await chat_model.load()
        return chat_model if success else None

    async def unload_model(self, model_id: str) -> bool:
        """Unload a model from memory"""
        try:
            if model_id in self.loaded_models:
                model = self.loaded_models[model_id]

                # Call model's unload method if available
                if hasattr(model, "unload"):
                    await model.unload()

                del self.loaded_models[model_id]

                if model_id in self.model_info:
                    self.model_info[model_id].status = ModelStatus.UNLOADED

                logger.info(f"✅ Unloaded model: {model_id}")
                return True
            else:
                logger.warning(f"Model {model_id} not found for unloading")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to unload model {model_id}: {e}")
            return False

    def get_model(self, model_id: str) -> Optional[Any]:
        """Get a loaded model instance"""
        return self.loaded_models.get(model_id)

    def is_model_loaded(self, model_id: str) -> bool:
        """Check if a model is loaded"""
        return model_id in self.loaded_models

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a model"""
        return self.model_info.get(model_id)

    def get_available_models(self) -> List[str]:
        """Get list of loaded model IDs"""
        return list(self.loaded_models.keys())

    def get_default_model_id(self, model_type: str) -> Optional[str]:
        """Return the default model id for a given type if available."""
        return self.default_models.get(model_type)

    def list_models_by_type(self, model_type: str) -> List[str]:
        """Return all models matching the supplied type."""
        return [
            model_id
            for model_id, info in self.model_info.items()
            if info.model_type == model_type
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get overall service status"""
        return {
            "models": {
                model_id: {
                    "status": info.status.value,
                    "type": info.model_type,
                    "load_time": info.load_time,
                    "provider": info.provider,
                    "capabilities": info.capabilities,
                }
                for model_id, info in self.model_info.items()
            },
            "loaded_count": len(self.loaded_models),
            "total_count": len(self.model_info),
        }

    def health_check(self) -> Dict[str, Any]:
        """Health check for the model service"""
        try:
            healthy_models = sum(
                1
                for info in self.model_info.values()
                if info.status == ModelStatus.LOADED
            )

            return {
                "status": "healthy" if healthy_models > 0 else "degraded",
                "models_loaded": healthy_models,
                "models_total": len(self.model_info),
                "models": self.get_status()["models"],
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
