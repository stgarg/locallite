import os
import pytest

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend

MODEL_ID = "bge-small-en-v1.5"

@pytest.mark.skipif(
    not os.path.isdir(os.path.join(os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5")),
    reason="Model assets not present"
)
def test_cache_hit_ratio_improves():
    model_path = os.path.join(os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5")
    be = OnnxEmbeddingBackend(MODEL_ID, model_path, cache_size=8)
    be.load()
    texts = ["hello world", "machine learning", "hello world"]  # repeat triggers cache
    first = be.embed(texts[:2])
    assert first.perf["cache_hits"] == 0
    second = be.embed(texts)
    assert second.perf["cache_hits"] >= 1
    assert len(second.vectors) == 3
