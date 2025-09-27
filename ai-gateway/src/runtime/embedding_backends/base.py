"""Base interfaces for embedding backends and related result containers.

This layer formalizes the contract between higher-level orchestration (routers,
benchmark harness, caching) and concrete embedding providers (ONNX, fastembed,
external APIs). Keeping it lightweight (dataclasses + Protocol) allows gradual
adoption without large refactors while enabling test doubles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Sequence


@dataclass
class EmbeddingResult:
    """Result of an embedding batch.

    Attributes:
        vectors: 2D list (batch, dim) of float embeddings (L2 normalized recommended).
        perf:   Performance / diagnostic metrics (timings, tokens, provider, cache stats).
    """

    vectors: List[List[float]]
    perf: Dict[str, Any]


@dataclass
class TokenBatch:
    """Tokenization output (optional, backend may ignore)."""

    input_ids: Any
    attention_mask: Any
    total_tokens: int
    avg_tokens_per_text: float


class EmbeddingBackend(Protocol):
    """Protocol every embedding backend must satisfy."""

    id: str
    provider_type: str
    dimension: int

    # Lifecycle
    def load(self) -> None: ...  # noqa: D401

    # Core embedding call returning vectors + perf metadata
    def embed(self, texts: Sequence[str]) -> EmbeddingResult: ...  # noqa: D401

    # Optional helpers
    def supports_batching(self) -> bool: ...  # noqa: D401
    def tokenize_count(self, text: str) -> int: ...  # noqa: D401
    def last_perf(self) -> Dict[str, Any] | None: ...  # noqa: D401

__all__ = [
    "EmbeddingBackend",
    "EmbeddingResult",
    "TokenBatch",
]
