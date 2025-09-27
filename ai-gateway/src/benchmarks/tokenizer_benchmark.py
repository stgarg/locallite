"""Tokenizer benchmark & comparison.

Compares current heuristic token counting (split on whitespace) with a Hugging Face
fast tokenizer for a target model (default: BERT-like tokenizer from 'bert-base-uncased'
if model-specific tokenizer files are not available in the exported model directory).

Metrics per mode:
- total_texts
- total_chars
- total_tokens
- mean_tokens_per_text
- mean_ms_per_text (tokenization latency)
- throughput_texts_per_sec

Outputs JSON to stdout (and optional --out path) so it can be versioned like embedding benchmarks.

Usage:
    python tokenizer_benchmark.py \
        --inputs ai-gateway/src/benchmarks/benchmark_inputs.txt \
        --model-path models/bge-small-en-v1.5 \
        --hf-tokenizer BAAI/bge-small-en-v1.5 \
        --runs 3 --discard-warmup 1 \
        --out ai-gateway/benchmarks/results/$(date +%Y%m%d)_tokenizers.json

If HF tokenizer cannot be loaded, script will mark that mode as unavailable.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

try:  # Optional heavy imports guarded
    from transformers import AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover
    AutoTokenizer = None  # type: ignore


def load_hf_tokenizer(model_id: str) -> Optional[Callable[[str], List[int]]]:
    if AutoTokenizer is None:
        return None
    try:
        tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=False)
        fast = tok if hasattr(tok, "_tokenizer") else None  # ensure fast tokenizer
        if fast is None:
            return None
        def encode(s: str) -> List[int]:  # noqa: D401
            return fast.encode(s, add_special_tokens=True)
        return encode
    except Exception:
        return None


def heuristic_tokenize(s: str) -> List[str]:
    return s.split()


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] * (c - k) + s[c] * (k - f)


def time_mode(name: str, texts: List[str], tokenize_fn: Callable[[str], List]) -> Dict[str, object]:
    start_all = time.perf_counter()
    token_counts: List[int] = []
    per_text_times: List[float] = []
    for t in texts:
        t0 = time.perf_counter()
        tokens = tokenize_fn(t)
        per_text_times.append((time.perf_counter() - t0) * 1000)
        token_counts.append(len(tokens))
    total_time = time.perf_counter() - start_all
    total_tokens = sum(token_counts)
    return {
        "mode": name,
        "total_texts": len(texts),
        "total_chars": sum(len(t) for t in texts),
        "total_tokens": total_tokens,
        "mean_tokens_per_text": statistics.mean(token_counts) if token_counts else 0.0,
        "mean_ms_per_text": statistics.mean(per_text_times) if per_text_times else 0.0,
        "p50_ms_per_text": percentile(per_text_times, 50),
        "p95_ms_per_text": percentile(per_text_times, 95),
        "throughput_texts_per_sec": len(texts) / total_time if total_time else 0.0,
    }


def run(runs: int, discard: int, texts: List[str], hf_model: Optional[str]) -> Dict[str, object]:
    results: List[Dict[str, object]] = []

    # Heuristic mode aggregated timing (single run, per-text internal timing)
    results.append(time_mode("heuristic_whitespace", texts, heuristic_tokenize))

    # HF tokenizer (if available)
    if hf_model:
        encode = load_hf_tokenizer(hf_model)
        if encode:
            results.append(time_mode("hf_fast", texts, encode))
        else:
            results.append({"mode": "hf_fast", "available": False})

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runs": runs,
        "discard_warmup": discard,
        "inputs": len(texts),
        "hf_model": hf_model,
        "modes": results,
    }


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Tokenizer benchmark comparison")
    parser.add_argument("--inputs", required=True, help="Path to benchmark_inputs.txt")
    parser.add_argument("--hf-tokenizer", help="HF model id for tokenizer (e.g. BAAI/bge-small-en-v1.5)")
    parser.add_argument("--runs", type=int, default=1, help="Reserved for future multi-run aggregation")
    parser.add_argument("--discard-warmup", type=int, default=0, help="Reserved warmup discard")
    parser.add_argument("--out", help="Write JSON artifact path")
    args = parser.parse_args()

    path = Path(args.inputs)
    if not path.exists():
        raise SystemExit(f"Inputs file not found: {path}")
    texts = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    artifact = run(args.runs, args.discard_warmup, texts, args.hf_tokenizer)
    print(json.dumps(artifact, indent=2))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
