"""Deterministic embedding digest utilities.

Policy:
- Round float values to 6 decimals for stability across minor numeric noise.
- Serialize as UTF-8 joined strings (faster + human-inspectable) OR raw bytes if needed later.
- Hash with SHA256; expose short (32 hex chars) and full variants.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Iterable, List, Sequence

Precision = 6  # decimal places


def _round_vector(vec: Sequence[float]) -> List[float]:
    return [round(x, Precision) for x in vec]


def digest_vectors(vectors: Iterable[Sequence[float]], short: bool = True, head_dims: int | None = None) -> str:
    """Return deterministic hash of sequence of embedding vectors.

    Args:
        vectors: sequence of numeric sequences.
        short: if True, return first 32 hex chars.
        head_dims: if provided, only include first N dims of each vector (used for quick signature).
    """
    parts: List[str] = []
    for vec in vectors:
        if head_dims is not None:
            slice_vec = vec[:head_dims]
        else:
            slice_vec = vec
        rounded = _round_vector(slice_vec)
        parts.append(",".join(f"{v:.{Precision}f}" for v in rounded))
    joined = "|".join(parts).encode("utf-8")
    h = sha256(joined).hexdigest()
    return h[:32] if short else h


def compare_digest(vectors_a: Iterable[Sequence[float]], vectors_b: Iterable[Sequence[float]], tolerance: float = 1e-6) -> bool:
    """Element-wise compare two embedding sets within tolerance.

    Returns True if shapes match and each absolute difference <= tolerance.
    """
    list_a = [list(v) for v in vectors_a]
    list_b = [list(v) for v in vectors_b]
    if len(list_a) != len(list_b):
        return False
    for va, vb in zip(list_a, list_b):
        if len(va) != len(vb):
            return False
        for x, y in zip(va, vb):
            if abs(x - y) > tolerance:
                return False
    return True

__all__ = ["digest_vectors", "compare_digest"]
