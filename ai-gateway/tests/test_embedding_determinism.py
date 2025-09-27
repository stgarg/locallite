"""Deterministic embedding test.

Skips gracefully if embedding model assets are unavailable.
"""
from __future__ import annotations

import os
import pytest
import sys
from pathlib import Path

# Add src path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from runtime.embedding_backends.onnx_backend import OnnxEmbeddingBackend  # noqa: E402
from runtime.utils.digest import digest_vectors, compare_digest  # noqa: E402

SAMPLE_TEXTS = [
    "A quick brown fox jumps over the lazy dog.",
    "Deterministic outputs enable confident refactors.",
]


@pytest.mark.skipif(
    not any(
        Path(p).exists()
        for p in [
            Path(__file__).resolve().parents[2] / 'EmbeddingServer' / 'models' / 'bge-small-en-v1.5' / 'model.onnx',
            Path(__file__).resolve().parents[2] / 'models' / 'bge-small-en-v1.5' / 'model.onnx',
        ]
    ),
    reason="Embedding model assets not present",
)
def test_embedding_digest_stable():
    # Resolve model path heuristic (mirrors runtime logic)
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / 'models' / 'bge-small-en-v1.5',
        repo_root / 'EmbeddingServer' / 'models' / 'bge-small-en-v1.5',
    ]
    model_path = None
    for c in candidates:
        if (c / 'model.onnx').exists():
            model_path = c
            break
    assert model_path, "Model path not found despite skip guard"

    backend = OnnxEmbeddingBackend('bge-small-en-v1.5', str(model_path))
    backend.load()

    emb1 = backend.embed(SAMPLE_TEXTS)
    emb2 = backend.embed(SAMPLE_TEXTS)

    assert compare_digest(emb1, emb2, tolerance=1e-6), "Embeddings differ beyond tolerance"
    d1 = digest_vectors(emb1, head_dims=8)
    d2 = digest_vectors(emb2, head_dims=8)
    assert d1 == d2, "Digest mismatch indicates nondeterminism"
