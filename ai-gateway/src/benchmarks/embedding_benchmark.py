"""Embedding benchmark harness.

Measures latency distribution, throughput, and deterministic digest for drift detection.
Intended for internal regression monitoring (not end-user marketing output).
"""

from __future__ import annotations

import argparse
import importlib.util as _importlib_util
import json
import os
import pathlib
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List

# Ensure the parent 'src' directory is on sys.path when executed directly via a relative path
_THIS_FILE = pathlib.Path(__file__).resolve()
_SRC_DIR = _THIS_FILE.parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Pre-flight dependency check (gives clearer error than deep stack trace)
_REQUIRED = ["numpy", "onnxruntime"]
_missing = [m for m in _REQUIRED if _importlib_util.find_spec(m) is None]
if _missing:
    sys.stderr.write(
        "\n[benchmark] Missing required packages: "
        + ", ".join(_missing)
        + "\nInstall them (inside the active venv) with:\n    pip install -r ai-gateway/requirements.txt\n\n"
    )
    raise SystemExit(2)

from runtime.embedding_backends.base import (  # type: ignore  # noqa: E402
    EmbeddingResult,
)
from runtime.embedding_backends.onnx_backend import (  # type: ignore  # noqa: E402
    OnnxEmbeddingBackend,
)
from runtime.model_registry import get_model  # type: ignore  # noqa: E402
from runtime.utils.digest import digest_vectors  # type: ignore  # noqa: E402

try:  # pragma: no cover - optional dep
    from runtime.embedding_backends.fastembed_backend import (
        FastEmbedBackend,  # type: ignore
    )
except Exception:  # pragma: no cover
    FastEmbedBackend = None  # type: ignore


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    d0 = s[f] * (c - k)
    d1 = s[c] * (k - f)
    return d0 + d1


def run_timed(fn, repeat: int, discard: int = 0) -> Dict[str, float]:
    raw: List[float] = []
    for i in range(repeat):
        start = time.perf_counter()
        fn()
        raw.append((time.perf_counter() - start) * 1000)
    used = raw[discard:] if discard else raw
    return {
        "runs": repeat - discard,
        "mean_ms": statistics.mean(used) if used else 0.0,
        "stdev_ms": statistics.pstdev(used) if len(used) > 1 else 0.0,
        "p50_ms": percentile(used, 50),
        "p95_ms": percentile(used, 95),
        "samples": used,
    }


def resolve_model_path(spec_path: str | None) -> str:
    """Resolve a model path from a registry entry or user override.

    Resolution strategy:
    1. If spec_path exists as given (absolute or relative), use it.
    2. If spec_path starts with "models/" (registry style), prepend repo root once.
    3. Otherwise try repo_root / "models" / spec_path.
    """
    if not spec_path:
        raise SystemExit("Model spec has no path; update registry or pass --model-path")

    # Direct hit (absolute or relative from CWD)
    if os.path.isdir(spec_path):
        return spec_path

    repo_root = Path(__file__).resolve().parents[3]

    # Avoid double models/models
    if spec_path.startswith("models/"):
        candidate = repo_root / spec_path
    else:
        candidate = repo_root / "models" / spec_path
    return str(candidate)


def run(
    model_id: str,
    backend: str,
    inputs: List[str],
    batch_sizes: List[int],
    runs: int,
    discard_warmup: int,
    digest_inputs: List[str],
    out: Path | None,
    model_path_override: str | None = None,
):
    spec = get_model(model_id)
    if not spec:
        raise SystemExit(f"Model not found: {model_id}")
    if backend == "onnx-custom":
        resolved_path = model_path_override or resolve_model_path(spec.path)
        if not os.path.isdir(resolved_path):
            raise SystemExit(
                f"Model directory not found: {resolved_path}\n"
                "Create it and place model.onnx (and optional config.json, vocab.txt) there, or pass --model-path to override.\n"
                f"Hint: expected file: {resolved_path}/model.onnx\n"
            )
        be = OnnxEmbeddingBackend(
            model_id, resolved_path, spec.dimension, cache_size=256
        )
    elif backend == "fastembed":  # pragma: no cover
        if FastEmbedBackend is None:
            raise SystemExit("fastembed library not installed")
        be = FastEmbedBackend(model_id)
    else:  # pragma: no cover
        raise SystemExit(f"Unsupported backend: {backend}")

    load_start = time.perf_counter()
    be.load()
    load_ms = (time.perf_counter() - load_start) * 1000

    results: List[Dict[str, object]] = []
    for batch in batch_sizes:
        subset = inputs[:batch]
        if not subset:
            continue
        # Warmup single run (populate tokenizer caches etc.)
        warm = be.embed(subset)  # warmup
        timings = run_timed(
            lambda: be.embed(subset), repeat=runs, discard=discard_warmup
        )
        result: EmbeddingResult = be.embed(subset)
        vectors = result.vectors
        perf = result.perf or {}
        digest = digest_vectors(vectors, short=True, head_dims=8)
        zero_or_nan = sum(
            1 for v in vectors for x in v if (x == 0.0 or (x != x))
        )  # NaN check via x!=x
        results.append(
            {
                "batch_size": batch,
                "runs": timings["runs"],
                "mean_ms": timings["mean_ms"],
                "stdev_ms": timings["stdev_ms"],
                "p50_ms": timings["p50_ms"],
                "p95_ms": timings["p95_ms"],
                "per_text_mean_ms": timings["mean_ms"] / batch if batch else 0.0,
                "throughput_texts_per_sec": (
                    (batch / (timings["mean_ms"] / 1000)) if timings["mean_ms"] else 0.0
                ),
                "dimension": len(vectors[0]) if vectors else 0,
                "digest": digest,
                "zero_or_nan_count": zero_or_nan,
                "tokenize_time_ms": perf.get("tokenize_time_ms"),
                "avg_tokens_per_text": perf.get("avg_tokens_per_text"),
                "total_tokens": perf.get("total_tokens"),
                "tokens_per_sec": (
                    ((perf.get("total_tokens") or 0) / (timings["mean_ms"] / 1000))
                    if timings["mean_ms"]
                    else 0.0
                ),
                "tokenizer": perf.get("tokenizer"),
                "tokenizer_version": perf.get("tokenizer_version"),
                "cache_hit_ratio": perf.get("cache_hit_ratio"),
                "cache_hits": perf.get("cache_hits"),
                "cache_misses": perf.get("cache_misses"),
                # Token distribution percentiles if available
                "p50_tokens_per_text": perf.get("p50_tokens_per_text"),
                "p95_tokens_per_text": perf.get("p95_tokens_per_text"),
            }
        )

    artifact = {
        "model": model_id,
        "backend": backend,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "model_load_time_ms": load_ms,
        "scenarios": results,
        "tokenizer_version": results[0].get("tokenizer_version") if results else None,
    }

    print(json.dumps(artifact, indent=2))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embedding benchmark harness")
    parser.add_argument("--model", default="bge-small-en-v1.5")
    parser.add_argument("--backend", default="onnx-custom")
    parser.add_argument(
        "--inputs", default=str(Path(__file__).with_name("benchmark_inputs.txt"))
    )
    parser.add_argument(
        "--batch-sizes", default="1,2,4,8", help="Comma list of batch sizes"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Timed runs per batch size (excluding warmup)",
    )
    parser.add_argument(
        "--discard-warmup", type=int, default=1, help="Discard first N timed runs"
    )
    parser.add_argument(
        "--digest-inputs", default=str(Path(__file__).with_name("digest_inputs.txt"))
    )
    parser.add_argument("--out", type=str, help="Write JSON artifact to path")
    parser.add_argument(
        "--model-path",
        type=str,
        help="Override model directory (containing model.onnx)",
    )
    args = parser.parse_args()

    inputs_path = Path(args.inputs)
    if not inputs_path.exists():
        raise SystemExit(f"Inputs file not found: {inputs_path}")
    lines = [
        l.strip()
        for l in inputs_path.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    if not lines:
        raise SystemExit("No inputs found in benchmark file")

    digest_path = Path(args.digest_inputs)
    if digest_path.exists():
        digest_inputs = [
            l.strip()
            for l in digest_path.read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
    else:
        digest_inputs = lines[:5]

    out_path = Path(args.out) if args.out else None
    batch_sizes = [int(x) for x in args.batch_sizes.split(",") if x]
    run(
        args.model,
        args.backend,
        lines,
        batch_sizes,
        args.runs,
        args.discard_warmup,
        digest_inputs,
        out_path,
        model_path_override=args.model_path,
    )
