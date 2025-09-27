"""Base abstractions for chat models."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.router_types import UnifiedRequest, UnifiedResponse


@dataclass
class ChatGeneration:
    """Convenience container for chat outputs prior to response wrapping."""

    text: str
    tokens: int
    prompt_tokens: int
    finish_reason: str = "stop"
    provider_used: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None


class BaseChatModel(abc.ABC):
    """Abstract base class that all chat models must implement."""

    def __init__(self, model_id: str, model_path: str):
        self.model_id = model_id
        self.model_path = model_path
        self.is_loaded: bool = False

    @abc.abstractmethod
    async def load(self) -> bool:
        """Load model weights/tokenizer into memory."""

    async def unload(self) -> None:
        """Free resources associated with the model."""

    @abc.abstractmethod
    async def generate(self, request: UnifiedRequest) -> ChatGeneration:
        """Generate a chat response for the given request."""

    async def process(self, request: UnifiedRequest) -> UnifiedResponse:
        """Standardised wrapper that returns a unified response object."""
        generation = await self.generate(request)
        content = {
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": generation.text},
                    "finish_reason": generation.finish_reason,
                }
            ]
        }
        usage = {
            "prompt_tokens": generation.prompt_tokens,
            "completion_tokens": generation.tokens,
            "total_tokens": generation.prompt_tokens + generation.tokens,
        }
        metadata = generation.metadata or {}
        if metadata:
            content["metadata"] = metadata

        return UnifiedResponse(
            id=request.id,
            request_type=request.request_type,
            model_id=request.model_id,
            content=content,
            usage=usage,
            provider_used=generation.provider_used,
            tokens_used=generation.tokens,
        )

    def health_check(self) -> Dict[str, Any]:
        """Return implementation-specific health information."""
        return {
            "model_id": self.model_id,
            "loaded": self.is_loaded,
        }
