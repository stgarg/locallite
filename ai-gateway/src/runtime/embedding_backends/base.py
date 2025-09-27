"""Base protocol for embedding backends."""
from __future__ import annotations

from typing import List, Protocol


class EmbeddingBackend(Protocol):
    id: str
    provider_type: str
    dimension: int

    def load(self) -> None: ...  # noqa: D401
    def embed(self, texts: List[str]) -> List[List[float]]: ...  # noqa: D401
    def tokenize_count(self, text: str) -> int: ...  # noqa: D401
    def supports_batching(self) -> bool: ...  # noqa: D401


__all__ = ["EmbeddingBackend"]
