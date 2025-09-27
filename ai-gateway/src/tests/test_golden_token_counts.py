import os
import pytest

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend
from runtime.model_registry import get_model

try:
    from transformers import AutoTokenizer  # type: ignore

    _TRANSFORMERS = True
except Exception:  # pragma: no cover
    _TRANSFORMERS = False

# Golden corpus (order matters) — chosen to exercise punctuation, unicode, short/long variance
GOLDEN_CORPUS = [
    "Hello world!",
    "Fast tokenization should be deterministic.",
    "Whitespace  tokenizer   vs.  HF fast tokenizer -- which wins?",
    "Unicode test: naïve café 😊",
    "Numbers and symbols: 12345, 67.89%; $ & ( ) [ ]",
    "Short",
    "The quick brown fox jumps over the lazy dog",
    "Edge-case---punctuation!!! with... ellipses?? and dashes—yes.",
]

# Captured with transformers==4.56.2 tokenizer from local model dir (2025-09-27)
GOLDEN_TOKENS_PER_TEXT = [5, 11, 18, 8, 20, 3, 11, 29]
GOLDEN_TOTAL = sum(GOLDEN_TOKENS_PER_TEXT)

# Allowed drift (absolute token count difference). We enforce exact for now for strong guardrail.
ALLOWED_TOTAL_DRIFT = 0
ALLOWED_PER_TEXT_DRIFT = 0


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

    backend = OnnxEmbeddingBackend(spec.model_id, model_dir, spec.dimension)
    backend.load()
    backend.embed(GOLDEN_CORPUS)
    perf = backend.last_perf() or {}

    observed_list = perf.get("tokens_per_text")
    assert isinstance(observed_list, list) and len(observed_list) == len(
        GOLDEN_TOKENS_PER_TEXT
    ), "tokens_per_text missing or length mismatch; update backend perf emission or golden corpus"

    # Per-text strict match (can relax later by allowing drift threshold)
    diffs = [abs(a - b) for a, b in zip(observed_list, GOLDEN_TOKENS_PER_TEXT)]
    max_diff = max(diffs)
    assert (
        max_diff <= ALLOWED_PER_TEXT_DRIFT
    ), f"Per-text token drift detected: observed={observed_list} expected={GOLDEN_TOKENS_PER_TEXT} diffs={diffs}"

    observed_total = perf.get("total_tokens")
    assert isinstance(observed_total, (int, float)), "total_tokens missing from perf"
    assert abs(observed_total - GOLDEN_TOTAL) <= ALLOWED_TOTAL_DRIFT, (
        f"Total token drift detected: observed={observed_total} expected={GOLDEN_TOTAL}. "
        f"If tokenizer or preprocessing intentionally changed, update GOLDEN_TOKENS_PER_TEXT."
    )

    # Distribution sanity
    assert perf.get("p50_tokens_per_text") <= perf.get("p95_tokens_per_text")
    # Extra safety: avg derived from totals
    avg = perf.get("avg_tokens_per_text")
    assert avg == pytest.approx(GOLDEN_TOTAL / len(GOLDEN_TOKENS_PER_TEXT), rel=1e-6)
