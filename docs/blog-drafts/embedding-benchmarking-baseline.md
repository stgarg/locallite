# Building a Reproducible Embedding Benchmark Baseline (Draft)

Date: 2025-09-27
Status: Draft
Audience: Engineers & practitioners optimizing local / edge embedding inference.

---
## 1. Why Start With Measurement (Not Optimization)
Optimizing without a trustworthy baseline makes every future change anecdotal. We anchored on:
- Deterministic fingerprints (digest) to catch silent drift.
- Multi-batch latency distributions (p50 & p95) instead of single best/worst anecdotes.
- Explicit environment capture (Python, platform, arch) per artifact.

> Principle: "If it isn't measured, it didn't improve; if it can't drift, it isn't fragile." 

## 2. What We Measure Today
| Layer | Metric | Reason |
|-------|--------|--------|
| Load | model_load_time_ms | Cold start / deployment impact |
| Inference | mean_ms, p50_ms, p95_ms | Central + tail latency health |
| Inference | per_text_mean_ms | Efficiency vs batch growth |
| Throughput | texts/sec | Capacity planning, saturation checks |
| Quality proxy | digest | Drift detection (tokenizer, weights, normalization) |
| Integrity | zero_or_nan_count | Quick anomaly flag |

## 3. Early Findings (BGE Small, aarch64 WSL2)
- Flat per-text latency at increasing batch sizes → we're effectively single-text inside a loop.
- p95 outlier at batch=2 hints at scheduling noise; not a systematic degradation.
- Throughput plateau (~3.2–3.3 texts/sec) confirms batching isn't real yet.

## 4. Tokenization: Accuracy Over Illusory Speed
The whitespace heuristic “looks” free (microseconds) but under-counted tokens by ~47%. That distorts:
- Provider routing heuristics (batch size vs token volume).
- Future context-length enforcement.
- Pricing / cost estimation if applied.

HF fast tokenizer adds <0.1 ms p95 per text—0.03% of ~300 ms embedding time. We trade a negligible constant for correctness & future-proofing.

## 5. Deterministic Digests (Lightweight Drift Alarms)
Instead of storing full embeddings (space & privacy concerns), we:
1. Normalize vectors.
2. Take first N dims (currently 8) & round to fixed decimals.
3. Hash with SHA256 → 128-bit hex slice.

If digest flips: investigate changed dependencies, tokenizer, runtime libs, or model weights before accepting a performance win/loss claim.

## 6. Roadmap of Incremental Wins
| Order | Change | Expected Impact | Risk |
|-------|--------|-----------------|------|
| 1 | HF tokenizer (batched) | Stable token counts, tiny overhead | Low |
| 2 | True batch ONNX session.run | 1.5–3× throughput for batch ≥4 | Medium (shape handling) |
| 3 | LRU embedding cache | p50 improvement on hot queries | Low |
| 4 | Token-aware provider routing | Better NPU/CPU split decisions | Medium (tuning) |
| 5 | Memory & p99 tracking | Capacity transparency | Low |
| 6 | Quantization experiments | Potential >30% latency lift | Medium (accuracy drift) |

## 7. Interpreting Latency Stats Quickly
- mean ≈ p50 → distribution tight (good); large gap means stragglers.
- p95 / p50 ratio > 1.2 repeatedly → emergent jitter source (thread contention, GC, IO).
- Flat throughput with rising batch size → no true batching or overhead dominated.

## 8. FAQ Extracts
**Why no p99 yet?** Sample size (5 runs minus warmup) renders p99 meaningless; we'll increase runs in CI first.
**Why digest instead of cosine similarity vs golden set?** Avoid storing & maintaining a golden vector matrix; digest is constant size + privacy-neutral.
**Why not optimize tokenizer further?** It's already negligible; premature micro-optimization invites complexity.

## 9. Next Blog in Series (Planned)
"Turning a Loop into a Batch: Achieving Real Throughput Gains in ONNX Embeddings" — showing before/after throughput curves & updated digest verification flow.

## 10. Takeaways
1. Baseline first; optimize second.
2. Accuracy (token counts) enables *intelligent* performance work.
3. Lightweight drift detection prevents celebrating regressions.
4. The biggest near-term win is true batching, not micro-tweaking current loops.

---
Feedback welcome before we promote this draft. Planned appendices: raw artifact JSON samples, CLI cheat sheet, and CI integration snippet.
