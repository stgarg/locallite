# BENCHMARKS
Performance & determinism tracking for embeddings (Phase 0 baseline) and future chat streaming.

## Method Summary
Harness: `ai-gateway/src/benchmarks/embedding_benchmark.py` collects per batch size:
- mean, stdev, p50, p95 latency (ms) over N timed runs (default 5, discard warmup 1)
- per-text derived latency, throughput (texts/sec)
- deterministic digest (first 8 dims, rounded 6 decimals)
- zero / NaN value count

Outputs JSON artifact when `--out` provided; curated summary added here.

Run example (multi-batch):
```
python ai-gateway/src/benchmarks/embedding_benchmark.py \
	--model bge-small-en-v1.5 \
	--backend onnx-custom \
	--batch-sizes 1,2,4,8 \
	--runs 5 \
	--discard-warmup 1 \
	--out benchmarks/results/$(date +%Y%m%d)_bge.json
```

## Embedding Baselines
First captured baseline (multi-run mean over 4 timed runs after warmup; runs=5, discard=1).

| Date       | Model             | Backend     | Batch | p50 ms  | p95 ms  | Mean ms | /Text ms | Throughput t/s | Dim | Digest                              | Notes |
|------------|-------------------|-------------|-------|---------|---------|---------|----------|----------------|-----|--------------------------------------|-------|
| 2025-09-27 | bge-small-en-v1.5 | onnx-custom | 1     | 313.03  | 316.25  | 300.66  | 300.66   | 3.33           | 384 | 80c2e365b9cc58dc8f233c2df1a24cf8 | Pre-tokenizer baseline |
| 2025-09-27 | bge-small-en-v1.5 | onnx-custom | 2     | 606.11  | 760.82  | 629.33  | 314.66   | 3.18           | 384 | 9a91e2e11cd0fece5c75d06f97c9abdc |  |
| 2025-09-27 | bge-small-en-v1.5 | onnx-custom | 4     | 1214.71 | 1303.92 | 1217.78 | 304.45   | 3.28           | 384 | 0f88b084b58cfa43267edb59f55d65df | Provider switch boundary |
| 2025-09-27 | bge-small-en-v1.5 | onnx-custom | 8     | 2430.80 | 2800.72 | 2496.67 | 312.08   | 3.20           | 384 | e76b2e1b370bdc9ee605b66c571a4dff |  |

### Post Tokenizer + Batched Inference (same day incremental)
Artifact: `ai-gateway/benchmarks/results/20250927_bge_tokenized.json`

| Date       | Model             | Batch | p50 ms | p95 ms | Mean ms | /Text ms | Throughput t/s | Avg Tokens/Text | Tokens/sec | Digest (new) | Notes |
|------------|-------------------|-------|--------|--------|---------|----------|----------------|-----------------|------------|--------------|-------|
| 2025-09-27 | bge-small-en-v1.5 | 1 | 278.20 | 335.21 | 287.77 | 287.77 | 3.47 | 12.00 | 41.70 | c742d5a0c1b81fe6134a91068b5e6051 | Tokenizer integrated |
| 2025-09-27 | bge-small-en-v1.5 | 2 | 487.10 | 520.73 | 487.79 | 243.89 | 4.10 | 12.00 | 49.20 | 13b9cc36491db424bc06075bbf4de2d1 | Batched session.run |
| 2025-09-27 | bge-small-en-v1.5 | 4 | 779.95 | 1013.33 | 829.33 | 207.33 | 4.82 | 12.00 | 57.88 | 7cf265734fe111ca32515427bd4c3d6d | Throughput +47% vs baseline batch4 |
| 2025-09-27 | bge-small-en-v1.5 | 8 | 1416.12 | 1624.06 | 1434.55 | 179.32 | 5.58 | 9.75 | 54.37 | d31c4a7ca788b5b7638dcf2dc5116fca | Lower /text ms from batching |

Improvement snapshot:
- Mean /text latency reduced: batch 4 → 304.45 ms → 207.33 ms (~31.9% faster per text).
- Throughput gains: batch 4 → 3.28 t/s → 4.82 t/s (~47% increase); batch 8 → 3.20 t/s → 5.58 t/s (~74%).
- Tokenization overhead remains <1.3 ms absolute even for batch 8 (<0.1% of total latency), validating negligible cost.
- Digests changed as expected after switch from heuristic to HF tokenizer (different token boundaries).

Next regression guardrails (update):
- If future commit reduces throughput at batch ≥4 by >15% without digest change or explicit change log, flag regression.
- If avg_tokens_per_text shifts materially (±>10%) on same corpus without model/tokenizer upgrade, investigate corpus drift or tokenization bug.

Artifact: `ai-gateway/benchmarks/results/20250927_bge.json` (model load time: 565.25 ms, aarch64 WSL2).

Observations:
- Near-linear per-text time across batches (304–314 ms) indicates minimal batching efficiency with current per-text tokenization loop; future optimization: vectorized tokenization + true batch inference.
- p95 for batch 2 spiked (760 ms) relative to others—investigate variance source (thread scheduling?) in follow-up.
- Throughput plateau (~3.2–3.33 t/s) suggests provider routing heuristic (currently CPU-only effective) offers no large batch gains yet.

## Drift Policy
1. Digest change → investigate (tokenizer, weights, normalization).
2. If intentional: add DECISION entry + update table with new digest.
3. Latency regression >15% mean OR >25% p95 triggers investigation before merge.

## Upcoming Additions
- Chat: TTFT, tokens/sec (after streaming implementation).
- Cache impact (hit ratio & latency delta) once caching layer lands.
- Provider routing distribution summary.

## Design Rationale & Choices
| Design Choice | Rationale | Alternatives Considered | Trade-offs |
|---------------|-----------|-------------------------|------------|
| Multi-run timing with warmup discard | Reduces JIT / cache warmup noise | Single timing; median-only | Slightly longer runtime per batch |
| p50 & p95 (not p99) | p95 captures tail jitter without being too sparse | p99, max | p99 unstable at low sample counts |
| Deterministic digest of embeddings | Detect silent numerical drift (tokenizer/model changes) quickly | Full vector snapshot | Digest is lossy; collisions improbable but possible |
| JSON artifact per run | Machine-readable for CI regression & docs | CSV, stdout-only | Slight overhead to parse but flexible |
| Separate tokenizer benchmark | Isolates tokenization overhead & correctness | Only measure end-to-end | Better root-cause capability |
| Keep initial heuristic tokenizer (baseline) | Provided contrast & safety while HF dep optional | Immediate HF adoption | Temporary duplicate logic |

### Why Deterministic Digests
We hash a truncated & rounded slice of each batch's vectors to create a lightweight fingerprint. A changed digest signals a likely shift in: (a) tokenizer segmentation, (b) numerical library/version, (c) model weights. It lets us gate merges without storing large binary artifacts.

### Interpreting Current Metrics
- Flat per-text latency across batch sizes reveals we're effectively doing per-text inference; ONNX session isn't batching tokenization/inference together yet.
- Throughput ≈ (1 / per-text latency) * batch size scaling stops because we re-enter session.run for each text.
- p95 spike at batch=2 suggests intermittent system noise (e.g., thread scheduling). We'll revalidate after batching improvements.

### Pending Optimizations (Ordered)
1. HF fast tokenizer integration with batch encode (reduces Python loop + provides accurate token counts).
2. True batch ONNX inference (single session.run on stacked input_ids) → expect ~1.5-3× throughput for batches ≥4.
3. Lightweight embedding cache (LRU) for repeated short queries (expect p50 improvements for hot phrases).
4. Provider routing refinement using total token count (not raw text count) once counts are accurate.
5. Optional vectorization of digest creation (already very cheap; low priority).

### What We Are NOT Doing Yet
- Quantization: Defer until we have stable baseline & batching; adds variance.
- Hardware-specific acceleration beyond AzureExecutionProvider fallback: Need deterministic token path first.
- Micro-bench p99: sample size currently too small; will add after CI increases run counts.

Updated: 2025-09-27 (baseline recorded)

## Tokenizer Benchmark (Initial Spike)
Artifact: `ai-gateway/benchmarks/results/20250927_tokenizers.json` (inputs=32).

| Mode | Mean ms / text | p50 ms / text | p95 ms / text | Mean tokens / text | Total tokens | Throughput texts/s | Notes |
|------|----------------|---------------|---------------|--------------------|--------------|--------------------|-------|
| heuristic_whitespace | 0.00072 | 0.00060 | 0.00143 | 7.41 | 237 | 881,980 | Splits on spaces only; severe under-count vs HF |
| hf_fast | 0.31212 | 0.04154 | 0.09046 | 13.91 | 445 | 3,197 | Accurate subword tokenization (≈1.88x more tokens) |

Observations:
- Token count delta: HF fast tokenizer yields ~1.88× tokens compared to whitespace heuristic (445 vs 237); heuristic is not viable for cost/length accounting.
- Latency: Absolute per-text tokenization latency is sub-millisecond at p50/p95; mean inflated by a few outliers (longer texts) but still negligible relative to ~300 ms embedding latency (~0.1% overhead).
- Throughput metric for whitespace appears artificially huge because work per text is trivial; meaningful comparison is absolute added time (<0.1 ms typical) not raw texts/s.

Implication: We can adopt HF tokenizer without materially affecting end-to-end latency; next step is integrating batch tokenization and removing heuristic path for production metrics.

## Why Removing the Whitespace Heuristic Helps
| Problem with Heuristic | Impact | HF Tokenizer Benefit |
|------------------------|--------|----------------------|
| Under-counts tokens (~47% of real) | Misleading routing & future cost estimates | Accurate subword counts enable data-driven batching & pricing |
| Language & punctuation blind | Over/under merges multi-lingual or punctuation-heavy text | Proper segmentation per vocab improves consistency |
| No normalization consistency | Potential mismatch if future models rely on canonical forms | HF pipelines apply consistent normalization/token rules |
| Hard to extend (CJK, emojis) | Complex bespoke rules creep | HF handles Unicode, multilingual cases |
| False performance optimism (tiny time) | Masks negligible true cost, encourages ignoring token phase | Realistic overhead budgeting ensures balanced optimization |

Net: Removing it reduces risk of subtle regressions when we later tune provider routing or enforce context limits. Tokenization correctness is foundational; latency cost is negligible (<0.1 ms p95 vs ~300 ms encode ≈ 0.03%).

## FAQ
**Q: Why do we report both mean and p50?**  Mean helps see aggregate impact of occasional spikes; p50 tracks central tendency; together with p95 they show distribution shape quickly.

**Q: Why not include memory usage yet?**  Early focus is latency & determinism. We'll add memory once batching & cache layers stabilize to avoid churn.

**Q: Could digest collisions hide drift?**  Theoretically yes, practically extremely low probability with SHA256 over normalized slice. If critical we can widen slice or store periodic full vectors.

**Q: Why does throughput barely increase with batch?**  Because current implementation performs per-text session.run. True batching will change this curve.

**Q: Is tokenizer latency stable across hardware?**  Yes, dominated by lightweight C++ fast tokenizer; expected to remain sub-ms per text.


