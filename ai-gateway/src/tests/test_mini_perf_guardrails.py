import json
import os
import time

import pytest

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend
from runtime.model_registry import get_model
from runtime.utils.digest import digest_vectors

# This mini test provides a fast CI guardrail without running the full benchmark harness.
# It verifies:
# 1. Basic embedding call succeeds (vectors returned, correct dimensionality)
# 2. Deterministic digest across two back-to-back runs for identical inputs
# 3. Token stats fields present
# 4. Cache provides at least one hit on second run (with small cache enabled)
# 5. No NaNs or zero-length vectors
#
# Skips if model assets are not present (CI environment without models).

MODEL_ID = "bge-small-en-v1.5"
TEXTS = ["mini perf guardrail one", "second short text"]
FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "embedding_digest_baseline.json"
)


@pytest.mark.skipif(
    not os.path.isdir(
        os.path.join(os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5")
    ),
    reason="Model assets not present",
)
def test_mini_perf_and_determinism():
    spec = get_model(MODEL_ID)
    assert spec is not None, "Model spec missing"
    model_path = os.path.join(
        os.path.dirname(__file__), "../../../../models/bge-small-en-v1.5"
    )

    backend = OnnxEmbeddingBackend(MODEL_ID, model_path, spec.dimension, cache_size=16)
    backend.load()

    first = backend.embed(TEXTS)
    second = backend.embed(TEXTS)

    # Structure / shape checks
    assert len(first.vectors) == len(TEXTS)
    dim = len(first.vectors[0])
    assert dim == spec.dimension or spec.dimension is None
    assert all(len(v) == dim for v in first.vectors)

    # Deterministic digest (head dims for speed) between first and second run
    d1 = digest_vectors(first.vectors, short=True, head_dims=16)
    d2 = digest_vectors(second.vectors, short=True, head_dims=16)
    assert d1 == d2, f"Embedding digest drift within same process: {d1} vs {d2}"

    # Baseline digest comparison (guardrail across commits)
    if os.path.isfile(FIXTURE_PATH):
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            baseline = json.load(f)
        if os.getenv("EMBEDDING_UPDATE_DIGEST") == "1":
            # Allow controlled update when intentional change occurs
            baseline["short_digest"] = d1
            with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
                json.dump(baseline, f, indent=2)
        else:
            expected_digest = baseline.get("short_digest")
            assert (
                d1 == expected_digest
            ), f"Digest mismatch vs baseline: {d1} != {expected_digest}. If intentional, rerun with EMBEDDING_UPDATE_DIGEST=1."
    else:  # pragma: no cover - first creation scenario
        # Write baseline if missing and update flag set
        if os.getenv("EMBEDDING_UPDATE_DIGEST") == "1":
            os.makedirs(os.path.dirname(FIXTURE_PATH), exist_ok=True)
            with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "model_id": MODEL_ID,
                        "texts": TEXTS,
                        "head_dims": 16,
                        "short_digest": d1,
                    },
                    f,
                    indent=2,
                )

    # Token stats presence
    perf = second.perf
    for field in [
        "total_tokens",
        "avg_tokens_per_text",
        "p50_tokens_per_text",
        "p95_tokens_per_text",
        "tokenize_time_ms",
    ]:
        assert field in perf, f"Missing perf field {field}"

    # Cache effectiveness (second call should have >=1 hit if cache enabled and identical inputs)
    assert (
        perf.get("cache_hits", 0) >= 1
    ), "Expected at least one cache hit on second run"
    # Minimum cache hit ratio threshold (two identical inputs among two) -> >=0.5 typical
    min_cache_ratio = float(os.getenv("MIN_CACHE_HIT_RATIO", "0.3"))
    if perf.get("cache_hit_ratio") is not None:
        assert (
            perf["cache_hit_ratio"] >= min_cache_ratio
        ), f"Cache hit ratio {perf['cache_hit_ratio']:.2f} below threshold {min_cache_ratio}"  # noqa: E501

    # Performance thresholds (very lenient defaults) configurable via env
    max_total_ms = float(os.getenv("PERF_MAX_TOTAL_MS", "1500"))
    if perf.get("total_time_ms") is not None:
        assert (
            perf["total_time_ms"] <= max_total_ms
        ), f"Total time {perf['total_time_ms']:.1f}ms exceeds budget {max_total_ms}ms"
    min_throughput = float(os.getenv("MIN_THROUGHPUT_TEXTS_PER_SEC", "1.0"))
    if perf.get("throughput_texts_per_sec") is not None:
        assert (
            perf["throughput_texts_per_sec"] >= min_throughput
        ), f"Throughput {perf['throughput_texts_per_sec']:.2f} below {min_throughput} texts/sec"

    # Basic sanity: no NaN values
    import math

    for vec in first.vectors:
        assert not any(math.isnan(x) for x in vec), "NaN detected in embedding"
