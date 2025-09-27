# Decision: Adopt Hugging Face Fast Tokenizer for Embeddings

Date: 2025-09-27
Status: Proposed (auto-generated draft)
Owners: Runtime / Benchmarking

## Context
Current embedding engine uses a simplistic whitespace split to:
- Estimate token counts for provider routing heuristics.
- Generate hash digest subset (not strongly impacted by token boundaries).

Benchmark baselines (2025-09-27) show embedding latency ~300 ms / text (per-text mean) on aarch64 WSL2.
Tokenizer spike (`20250927_tokenizers.json`) compared heuristic vs HF fast tokenizer (BAAI/bge-small-en-v1.5) on 32 representative inputs.

## Data
| Mode | Mean ms / text | p50 ms / text | p95 ms / text | Mean tokens / text | Tokens Delta vs Heuristic |
|------|----------------|---------------|---------------|--------------------|---------------------------|
| heuristic_whitespace | 0.00072 | 0.00060 | 0.00143 | 7.41  | baseline |
| hf_fast               | 0.31212 | 0.04154 | 0.09046 | 13.91 | +87.8% tokens |

Observations:
- Heuristic undercounts tokens (~47% of true subword count) → inaccurate length-based routing / future pricing metrics.
- HF tokenizer latency p95 <0.1 ms per text (0.03% of embedding latency) → negligible overhead.
- Mean ms inflated by infrequent longer texts; distribution tails still tiny.

## Decision
Adopt Hugging Face fast tokenizer (AutoTokenizer fast path) for embedding preprocessing & token count statistics. Remove heuristic token counting from critical path while retaining a fallback (with warning) if tokenizer initialization fails.

## Rationale
1. Accuracy: Correct token counts required for batching logic, context window enforcement, and future cost modeling.
2. Negligible Cost: <0.1 ms p95 overhead vs ~300 ms embedding encode → <0.05% runtime impact.
3. Consistency: Aligns token counts with future rerank/chat components using HF tokenizers.
4. Risk Mitigation: Keep fallback only for catastrophic tokenizer load failures to avoid total outage.

## Implementation Plan
1. Add tokenizer initialization to `OptimizedEmbeddingEngine` (attempt to load from model directory; fallback to HF model id if absent).
2. Replace `_tokenize` whitespace split with fast tokenizer encode (batched if available) producing input_ids, attention_mask.
3. Cache vocab / tokenization objects to avoid re-instantiation.
4. Update provider routing to use accurate token counts (optionally incorporate total_tokens * batch_size threshold).
5. Extend benchmark harness to record tokenization latency separately (already partially recorded) and include tokens-per-second metrics.
6. Add regression test: token count monotonicity (more chars ⇒ >= tokens) using sample corpus.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Larger dependency surface (transformers) | Already in dev; can make runtime optional with clear error if missing. |
| Tokenizer model mismatch (exported vs HF hub revision) | Prefer local tokenizer files if present; log revision hash. |
| Non-English text edge cases (CJK, etc.) | Add future corpus expansion test; HF handles subword segmentation robustly. |

## Success Criteria
- p95 tokenization latency <1 ms per text across corpus (current: <0.1 ms).
- Correct token counts (HF vs internal) match exactly; heuristic removed from metrics.
- No >1% regression in end-to-end embedding throughput due to tokenizer change.

## Follow-Up Metrics
- Add `tokens_per_sec` and `avg_tokens_per_text` to embedding benchmark JSON.
- Track any drift in mean embedding latency after integration.

## Decision Review
If future hardware acceleration drastically reduces encode latency below ~5 ms per text, re-evaluate tokenizer overhead proportion (unlikely). Otherwise decision stands.

---
(Generated draft; finalize via PR review and flip Status to Accepted.)
