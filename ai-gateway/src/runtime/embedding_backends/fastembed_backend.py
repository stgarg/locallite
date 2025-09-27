"""Adapter for external fastembed library (if installed).

This backend is optional; it gracefully degrades if fastembed is missing.
"""

from __future__ import annotations

from typing import List

try:
    import fastembed as fe  # type: ignore
except Exception:  # pragma: no cover - optional import
    fe = None  # type: ignore


class FastEmbedBackend:
    provider_type = "fastembed"

    def __init__(self, model_id: str):
        self.id = model_id
        self.dimension = 0
        self._model = None

    def load(self) -> None:
        if fe is None:
            raise RuntimeError("fastembed library not installed")
        self._model = fe.TextEmbedding(model_name=self.id)
        # Try a dummy embed to discover dimension
        vec = next(self._model.embed("dimension probe"))
        self.dimension = len(vec)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not self._model:
            raise RuntimeError("Backend not loaded")
        # fastembed yields generator
        return [vec for vec in self._model.embed(texts)]

    def tokenize_count(self, text: str) -> int:
        # Library does not expose tokenizer; fallback heuristic
        return len(text.split())

    def supports_batching(self) -> bool:
        return True


__all__ = ["FastEmbedBackend"]
