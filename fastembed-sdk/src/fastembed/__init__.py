"""
FastEmbed SDK - High-performance embedding SDK with Snapdragon NPU acceleration

A drop-in replacement for OpenAI embeddings with automatic NPU optimization
for 2-10x faster inference and 90% cost savings on local hardware.
"""

from .client import FastEmbedClient, AsyncFastEmbedClient
from .models import EmbeddingResponse, EmbeddingRequest, Usage, SystemInfo
from .exceptions import FastEmbedError, FastEmbedConnectionError, FastEmbedTimeoutError

__version__ = "0.1.0"
__all__ = [
    "FastEmbedClient",
    "AsyncFastEmbedClient",
    "EmbeddingResponse",
    "EmbeddingRequest", 
    "Usage",
    "SystemInfo",
    "FastEmbedError",
    "FastEmbedConnectionError",
    "FastEmbedTimeoutError",
]