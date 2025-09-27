import os
import pytest

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend
from runtime.model_registry import get_model

try:
    from transformers import AutoTokenizer  # type: ignore
    _TRANSFORMERS = True
except Exception:  # pragma: no cover
    _TRANSFORMERS = False


@pytest.mark.skipif(not _TRANSFORMERS, reason="transformers not installed")
def test_embedding_backend_reports_token_stats():
    spec = get_model("bge-small-en-v1.5")
    assert spec is not None, "Model spec missing"
    # Resolve model path similar to benchmark
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    model_dir = os.path.join(repo_root, spec.path)
    if not os.path.isdir(model_dir):
        pytest.skip("Model directory not present; skip tokenizer integration test")

    backend = OnnxEmbeddingBackend(spec.model_id, model_dir, spec.dimension)
    backend.load()
    texts = ["Hello world", "A longer sentence for tokenization testing."]
    backend.embed(texts)
    perf = backend.last_perf()
    assert perf is not None
    assert perf.get("total_tokens", 0) > 0
    assert perf.get("avg_tokens_per_text", 0) >= 1
    # Expect HF tokenizer yields >= whitespace heuristic tokens
    # whitespace baseline counts
    whitespace_counts = [len(t.split()) for t in texts]
    avg_ws = sum(whitespace_counts) / len(texts)
    assert perf.get("avg_tokens_per_text") >= avg_ws
