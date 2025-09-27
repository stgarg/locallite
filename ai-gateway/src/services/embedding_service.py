"""
Shared Embedding Service
Core embedding processing logic shared by both human and agent endpoints
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from embedding_engine import OptimizedEmbeddingEngine

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result from embedding processing"""

    embeddings: List[Optional[List[float]]]  # None for failures
    tokens: int
    model_used: str
    provider_used: str
    processing_time_ms: float
    errors: List[Optional[str]]  # Error messages, None for successful embeddings
    performance_info: Dict[str, Any]


class EmbeddingService:
    """
    Core embedding service shared by both human and agent endpoints

    Handles:
    - NPU/CPU routing logic
    - Batch optimization
    - Error handling with detailed feedback
    - Performance monitoring
    """

    def __init__(self):
        self.engine: Optional[OptimizedEmbeddingEngine] = None
        self.model_path: Optional[str] = None
        self._is_initialized = False

    async def initialize(self, model_path: str) -> bool:
        """Initialize the embedding engine"""
        try:
            self.model_path = model_path
            self.engine = OptimizedEmbeddingEngine(model_path)
            self._is_initialized = True
            logger.info(f"✅ EmbeddingService initialized with model at {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize EmbeddingService: {e}")
            self._is_initialized = False
            return False

    async def process_embeddings(
        self, texts: List[str], model: str = "bge-small-en-v1.5"
    ) -> EmbeddingResult:
        """
        Core embedding logic - shared by both human and agent endpoints

        Args:
            texts: List of texts to embed
            model: Model identifier

        Returns:
            EmbeddingResult with embeddings, errors, and metadata
        """
        if not self._is_initialized or not self.engine:
            raise RuntimeError("EmbeddingService not initialized")

        start_time = time.time()
        embeddings = []
        errors = []
        total_tokens = 0

        try:
            # Validate inputs
            if not texts:
                raise ValueError("Input texts cannot be empty")

            if len(texts) > 100:  # Reasonable batch limit
                raise ValueError(f"Batch size {len(texts)} exceeds maximum of 100")

            # Process embeddings with automatic provider routing
            embeddings_array, performance_info = self.engine.encode(texts)

            # Convert numpy arrays to lists and handle any failures
            for i, embedding in enumerate(embeddings_array):
                try:
                    if embedding is not None:
                        embeddings.append(embedding.tolist())
                        errors.append(None)
                        # Rough token estimation
                        total_tokens += len(texts[i].split())
                    else:
                        embeddings.append(None)
                        errors.append(f"Failed to generate embedding for text {i}")
                except Exception as e:
                    embeddings.append(None)
                    errors.append(f"Error processing text {i}: {str(e)}")

            processing_time_ms = (time.time() - start_time) * 1000

            # Log performance metrics
            success_count = sum(1 for emb in embeddings if emb is not None)
            logger.info(
                f"Processed {success_count}/{len(texts)} embeddings using "
                f"{performance_info.get('provider', 'unknown')} in {processing_time_ms:.1f}ms"
            )

            return EmbeddingResult(
                embeddings=embeddings,
                tokens=total_tokens,
                model_used=model,
                provider_used=performance_info.get("provider", "unknown"),
                processing_time_ms=processing_time_ms,
                errors=errors,
                performance_info=performance_info,
            )

        except Exception as e:
            # Handle catastrophic failures: do NOT fabricate embeddings; surface error cleanly
            processing_time_ms = (time.time() - start_time) * 1000
            logger.exception(f"Critical error in embedding processing: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities"""
        if not self.engine:
            return {"status": "not_initialized"}

        return self.engine.get_model_info()

    def health_check(self) -> Dict[str, Any]:
        """Health check for the embedding service"""
        if not self._is_initialized or not self.engine:
            return {"status": "unhealthy", "error": "Service not initialized"}

        try:
            # Quick health check with engine
            health_info = self.engine.health_check()
            return {
                "status": "healthy",
                "model_path": self.model_path,
                "engine_health": health_info,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
