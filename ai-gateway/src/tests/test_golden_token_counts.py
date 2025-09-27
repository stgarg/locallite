import json
import os

import pytest

try:
    from transformers import AutoTokenizer  # type: ignore

    _TRANSFORMERS = True
except Exception:  # pragma: no cover
    _TRANSFORMERS = False

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend
from runtime.model_registry import get_model

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "golden_token_counts.json"
)
ALLOWED_TOTAL_DRIFT = int(os.getenv("TOKEN_TOTAL_DRIFT", "0"))
ALLOWED_PER_TEXT_DRIFT = int(os.getenv("TOKEN_PER_TEXT_DRIFT", "0"))


@pytest.mark.skipif(not _TRANSFORMERS, reason="transformers not installed")
def test_golden_token_counts_stable():
    spec = get_model("bge-small-en-v1.5")
    assert spec is not None
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    model_dir = os.path.join(repo_root, spec.path)
    if not os.path.isdir(
        model_dir
    ):  # pragma: no cover - environment without model assets
        pytest.skip("Model directory not present; skipping golden token test")

    assert os.path.isfile(FIXTURE_PATH), "Missing golden_token_counts.json fixture"
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        fixture = json.load(f)

    corpus = fixture["corpus"]
    expected_tokens = fixture["tokens_per_text"]
    backend = OnnxEmbeddingBackend(spec.model_id, model_dir, spec.dimension)
    backend.load()
    backend.embed(corpus)
    perf = backend.last_perf() or {}
    observed_list = perf.get("tokens_per_text")
    assert isinstance(observed_list, list) and len(observed_list) == len(
        expected_tokens
    ), "tokens_per_text missing or length mismatch; update backend perf emission or golden corpus"

    # Update path if intentional change signaled
    if os.getenv("TOKEN_UPDATE_GOLDEN") == "1":
        fixture["tokens_per_text"] = observed_list
        with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
            json.dump(fixture, f, indent=2)
        pytest.skip("Golden token counts updated (TOKEN_UPDATE_GOLDEN=1)")

    diffs = [abs(a - b) for a, b in zip(observed_list, expected_tokens)]
    max_diff = max(diffs)
    assert (
        max_diff <= ALLOWED_PER_TEXT_DRIFT
    ), f"Per-text token drift detected: observed={observed_list} expected={expected_tokens} diffs={diffs}"

    observed_total = perf.get("total_tokens")
    expected_total = sum(expected_tokens)
    assert isinstance(observed_total, (int, float)), "total_tokens missing from perf"
    assert abs(observed_total - expected_total) <= ALLOWED_TOTAL_DRIFT, (
        f"Total token drift detected: observed={observed_total} expected={expected_total}. "
        f"If intentional, set TOKEN_UPDATE_GOLDEN=1 and re-run tests."
    )

    # Distribution sanity
    assert perf.get("p50_tokens_per_text") <= perf.get("p95_tokens_per_text")
    # Extra safety: avg derived from totals
    avg = perf.get("avg_tokens_per_text")
    assert avg == pytest.approx(expected_total / len(expected_tokens), rel=1e-6)
