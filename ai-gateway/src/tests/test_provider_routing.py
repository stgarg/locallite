import os

import pytest

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend
from runtime.model_registry import get_model

MODEL_ID = "bge-small-en-v1.5"
SMALL_BATCH = ["one short text"]
LARGE_BATCH = ["t1", "t2", "t3", "t4"]  # batch size = 4 triggers large path


@pytest.mark.skipif(
    not os.path.isdir(
        os.path.join(os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5")
    ),
    reason="Model assets not present",
)
def test_provider_routing_batch_size_heuristic():
    """Validate provider selection heuristic remains stable.

    Rules (current engine):
      - batch <= 3 => CPU-ARM64
      - batch >= 4 => Azure if available else CPU-ARM64
    We assert the small batch uses CPU-ARM64 and that large batch either switches
    provider or (if Azure not available) remains CPU-ARM64 without causing errors.
    """
    spec = get_model(MODEL_ID)
    assert spec is not None
    model_path = os.path.join(
        os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5"
    )
    backend = OnnxEmbeddingBackend(MODEL_ID, model_path, spec.dimension, cache_size=0)
    backend.load()

    small = backend.embed(SMALL_BATCH)
    assert (
        small.perf.get("provider") == "CPU-ARM64"
    ), f"Expected CPU-ARM64 for small batch, got {small.perf.get('provider')}"

    large = backend.embed(LARGE_BATCH)
    large_provider = large.perf.get("provider")
    assert large_provider in {
        "CPU-ARM64",
        "Azure",
    }, f"Unexpected provider {large_provider}"
    # If Azure available, ensure change occurred
    if large_provider == "Azure":
        assert large_provider != small.perf.get(
            "provider"
        ), "Provider should differ for larger batch when Azure available"
