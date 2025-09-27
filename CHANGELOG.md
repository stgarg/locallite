# Changelog
All notable changes to this project will be documented here.

## [Unreleased]
### Added
- `memory/CLAUDE.md` central assistant/context anchor.
- Model registry integration into `/v1/models` plus extended `/v1/models/registry` endpoint.
- Benchmark harness upgrade: multi-batch, p50/p95, digest, JSON output.
- Deterministic embedding digest utilities (`runtime/utils/digest.py`).
- Determinism test `test_embedding_determinism.py` (skips if model assets absent).
- Rich benchmark input corpus + digest subset files.
- API playground files (`examples/api_playground.http` / `.py`).
- ONNX export helper script `scripts/export_bge_model.py`.
- Tokenizer benchmark harness (`tokenizer_benchmark.py`) and initial artifact.
- HF tokenizer integration (batched) into embedding engine with token stats (avg_tokens_per_text, total_tokens, tokenize_time_ms).
- Extended embedding benchmark artifact fields: tokenize_time_ms, avg_tokens_per_text, total_tokens, tokens_per_sec, tokenizer.
- Regression test `test_tokenizer_integration.py` validating token stats exposure.

### Benchmarks
- First embedding baseline captured for `bge-small-en-v1.5` (2025-09-27) on aarch64 WSL2; see `docs/BENCHMARKS.md` and artifact `ai-gateway/benchmarks/results/20250927_bge.json`.
- Tokenizer spike results added; decision draft `docs/DECISIONS/TOKENIZER_DECISION.md`.
- Post-tokenizer + batched inference metrics captured (`20250927_bge_tokenized.json`) showing ~32% per-text latency reduction (batch4) and ~74% throughput gain (batch8) vs baseline.

### Changed
- Dynamic model path resolution (removed hardcoded absolute paths).
- Removed random embedding fallback; errors now surface clearly.
- Updated `.gitignore` to retain tests & core docs; added scratch + benchmark result patterns.
- Expanded `BENCHMARKS.md` with methodology & table scaffold.
- Updated `CLAUDE.md` to reflect benchmark workflow.

### Fixed
- Embedding and chat initialization failures due to invalid path defaults.

### Pending / Next
- Introduce embedding caching layer + cache impact metrics.
- Provider routing heuristics leveraging accurate token counts.
- CI reduced-run benchmark + automated regression thresholds (throughput, digest, tokens).
- Chat multi-token generation + streaming (TTFT & tokens/sec metrics).
- Quantization experiments after cache & routing stability.
- Memory usage & p99 latency reporting in benchmark artifacts.

---
This changelog follows Keep a Changelog style (unreleased consolidated until first tagged release).
