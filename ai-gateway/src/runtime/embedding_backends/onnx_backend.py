"""ONNX-based embedding backend wrapping existing OptimizedEmbeddingEngine."""
from __future__ import annotations

from typing import List

from embedding_engine import OptimizedEmbeddingEngine


class OnnxEmbeddingBackend:
    provider_type = "onnx-custom"

    def __init__(self, model_id: str, model_path: str, dimension: int | None = None):
        self.id = model_id
        self.model_path = model_path
        self.dimension = dimension or 384
        self._engine: OptimizedEmbeddingEngine | None = None

    def load(self) -> None:
        if not self._engine:
            self._engine = OptimizedEmbeddingEngine(self.model_path, model_id=self.id)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not self._engine:
            raise RuntimeError("Backend not loaded")
        embeddings, _perf = self._engine.encode(texts)
        return [vec.tolist() for vec in embeddings]

    def last_perf(self):
        if not self._engine:
            return None
        return self._engine.last_performance()

    def tokenize_count(self, text: str) -> int:
        # Approximate using simple split if detailed tokenizer not exposed
        return len(text.split())

    def supports_batching(self) -> bool:
        return True


__all__ = ["OnnxEmbeddingBackend"]
