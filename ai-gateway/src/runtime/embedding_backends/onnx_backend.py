"""ONNX-based embedding backend wrapping existing OptimizedEmbeddingEngine.

Adds an optional in-process LRU cache for repeated short texts to reduce
latency & tokenization overhead (useful in retrieval-heavy workflows).
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List, Sequence, Tuple

from embedding_engine import OptimizedEmbeddingEngine
from runtime.embedding_backends.base import EmbeddingResult


class OnnxEmbeddingBackend:
    provider_type = "onnx-custom"

    def __init__(
        self,
        model_id: str,
        model_path: str,
        dimension: int | None = None,
        cache_size: int | None = 0,
    ):
        self.id = model_id
        self.model_path = model_path
        self.dimension = dimension or 384
        self._engine: OptimizedEmbeddingEngine | None = None
        self._cache_size = cache_size or 0
        self._cache: "OrderedDict[str, List[float]]" = OrderedDict()
        self._last_perf: Dict[str, any] | None = None

    def load(self) -> None:
        if not self._engine:
            self._engine = OptimizedEmbeddingEngine(self.model_path, model_id=self.id)

    def _cache_get(self, key: str) -> List[float] | None:
        if self._cache_size <= 0:
            return None
        vec = self._cache.get(key)
        if vec is not None:
            # mark as recently used
            self._cache.move_to_end(key)
        return vec

    def _cache_put(self, key: str, vec: List[float]):
        if self._cache_size <= 0:
            return
        self._cache[key] = vec
        self._cache.move_to_end(key)
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

    def embed(self, texts: Sequence[str]) -> EmbeddingResult:
        if not self._engine:
            raise RuntimeError("Backend not loaded")
        texts_list = list(texts)
        cache_hits: List[Tuple[int, List[float]]] = []
        misses: List[Tuple[int, str]] = []
        for idx, t in enumerate(texts_list):
            c = self._cache_get(t)
            if c is not None:
                cache_hits.append((idx, c))
            else:
                misses.append((idx, t))

        miss_vectors: Dict[int, List[float]] = {}
        encode_time_ms = 0.0
        if misses:
            miss_texts = [m[1] for m in misses]
            start = time.perf_counter()
            embs, perf = self._engine.encode(miss_texts)
            encode_time_ms = (time.perf_counter() - start) * 1000
            for i, (orig_index, _t) in enumerate(misses):
                vec_list = embs[i].tolist()
                miss_vectors[orig_index] = vec_list
                self._cache_put(_t, vec_list)
        else:
            perf = self._engine.last_performance() or {}

        ordered: List[List[float]] = []
        for i in range(len(texts_list)):
            # prefer miss vector then hit
            if i in miss_vectors:
                ordered.append(miss_vectors[i])
            else:
                # must exist as hit
                vec = [v for idx, v in cache_hits if idx == i][0]
                ordered.append(vec)

        total = len(texts_list) or 1
        hit_count = len(cache_hits)
        perf_out = {
            **(perf or {}),
            "cache_enabled": self._cache_size > 0,
            "cache_size": self._cache_size,
            "cache_hits": hit_count,
            "cache_misses": len(misses),
            "cache_hit_ratio": hit_count / total if total else 0.0,
        }
        self._last_perf = perf_out
        return EmbeddingResult(vectors=ordered, perf=perf_out)

    def last_perf(self):  # alias for benchmark harness compatibility
        return self._last_perf or (self._engine.last_performance() if self._engine else None)

    def tokenize_count(self, text: str) -> int:
        return len(text.split())  # heuristic; engine exposes batch token stats only

    def supports_batching(self) -> bool:
        return True


__all__ = ["OnnxEmbeddingBackend"]
