"""Shared request/response types for model routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ModelType(str, Enum):
    """High level categories of models managed by the gateway."""

    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    MULTIMODAL = "multimodal"


class RequestType(str, Enum):
    """Supported inference request types."""

    CHAT_COMPLETION = "chat_completion"
    EMBEDDING = "embedding"
    DOCUMENT = "document"


@dataclass
class UnifiedRequest:
    """Standardised request payload handed to loaded models."""

    id: str
    request_type: RequestType
    model_id: str
    content: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None


@dataclass
class UnifiedResponse:
    """Standardised response returned from loaded models."""

    id: str
    request_type: RequestType
    model_id: str
    content: Dict[str, Any]
    usage: Dict[str, Any] = field(default_factory=dict)
    provider_used: str = "unknown"
    tokens_used: int = 0
    processing_time: float = 0.0

"""Module public API."""
__all__ = [
    "ModelType",
    "RequestType",
    "UnifiedRequest",
    "UnifiedResponse",
]
