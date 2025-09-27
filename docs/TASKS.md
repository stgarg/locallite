# TASKS (Local Tracking)
Structure mirrors a simple project management hierarchy without external tooling.

## EPICS
- E1: Phase 0 Cleanup & Memory Foundations
- E2: Runtime Modularization & Model Registry
- E3: Benchmark & Deterministic Embedding Harness
- E4: Retrieval + Document Pipeline MVP
- E5: SDK Feature Alignment (Streaming, Errors, Health)

## FEATURES (Mapped to Epics)
| ID | Epic | Title | Status | Notes |
|----|------|-------|--------|-------|
| F1 | E1 | Archive legacy C# + old entrypoints | Todo | Move to /archive + deprecations doc |
| F2 | E1 | Memory file scaffolding | In Progress | Core files created |
| F3 | E2 | Model registry skeleton | Done | dataclass + in-memory specs |
| F4 | E2 | Embedding backend abstraction | In Progress | Formal ABC + backend registry + engine slimming pending |
| F5 | E3 | Benchmark script (embeddings) | Done | Harness + drift digest + baseline captured |
| F6 | E3 | HF tokenizer integration | Done | Fast tokenizer + batched ONNX inference + perf stats |
| F7 | E4 | Ingestion pipeline design doc | Todo | Document before code |
| F8 | E4 | Minimal FAISS+SQLite index | Todo | After registry stable |
| F9 | E5 | SDK health + models sync | Todo | Endpoint contract test |
| F10| E5 | Chat streaming support | Todo | SSE or WebSocket |

## TASKS (Actionable, <= 0.5 day)
| ID | Feature | Description | Status |
|----|---------|-------------|--------|
| T1 | F1 | Move EmbeddingServer/ to archive | Todo |
| T2 | F1 | Move ai-gateway/src/main_old.py to archive | Done |
| T3 | F1 | Create DEPRECATIONS.md | In Progress |
| T4 | F2 | Create model_registry.py stub | Done |
| T5 | F2 | Wrap existing engine as OnnxEmbeddingBackend | Done |
| T6 | F2 | FastEmbedBackend adapter stub | Done |
| T7 | F3 | Write benchmark_inputs.txt | Done |
| T8 | F3 | Implement benchmark script | Done | Multi-batch + percentiles + digest |
| T9 | F3 | Add test: deterministic embedding hash | Done |
| T10| F3 | Capture baseline timings to BENCHMARKS.md | Done | 2025-09-27 baseline recorded |
| T11| F3 | Tokenizer benchmark spike script | Done | Artifact 20250927_tokenizers.json |
| T12| F3 | Decision doc: tokenizer adoption | Done | DECISIONS/TOKENIZER_DECISION.md |
| T13| F3 | Extend benchmark artifacts (token stats) | Done | tokenize_time_ms, tokens_per_sec added |
| T16| F4 | EmbeddingBackend ABC + refactor engine | In Progress | Abstraction + ONNX backend migrated; engine slimming next |
| T17| F6 | Golden corpus token count test | Done | Strict guardrail (0 drift) added tests/test_golden_token_counts.py |
| T18| F6 | Tokenizer version + model revision emission | In Progress | tokenizer_version emitted; revision pending |
| T19| F4 | LRU embedding cache layer | In Progress | Implemented in OnnxEmbeddingBackend (cache_size param) |
| T20| F4 | Provider routing heuristics | In Progress | Added test_provider_routing.py asserting batch-size heuristic |
| T21| F6 | Mini CI benchmark (reduced-run) | In Progress | Added tests/test_mini_perf_guardrails.py (digest baseline, perf thresholds, cache ratio); provider routing check pending |
| T22| F5 | Chat tokenizer unification | Planned | Reuse HF tokenizer provider |
| T23| F3 | Add p50/p95 tokenize_time metrics | In Progress | Per-text token percentiles added (p50/p95); tokenize_time aggregation pending |
| T24| F? | DSPy evaluation write-up | Deferred | See DSPy note |

| T14| F2 | Wire registry into /v1/models + add /v1/models/registry | Done |
| T15| F3 | Add CLAUDE.md + memory folder aggregator | Done |

## BUGS
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| B1 | Simple tokenizer may miscount tokens | Closed | Replaced by HF fast tokenizer |
| B2 | Provider naming ambiguity (Azure vs real NPU) | Open | Clarify in model info |

## EXPERIMENTS
| ID | Hypothesis | Status | Next Step |
|----|------------|--------|----------|
| X1 | HF tokenizer adds <5ms overhead small batch | Done | Overhead acceptable; throughput improved |
| X2 | Caching first 100 embeddings yields measurable latency reduction | Planned | Add simple LRU |
| X3 | Provider routing using token stats improves p50 | Planned | After cache + guardrails |
| X4 | DSPy pipelines add net value vs lightweight orchestrator | Deferred | Revisit post-core perf |

### DSPy (Deferred Evaluation)
DSPy (Stanford) is a declarative framework for self-improving LLM pipelines (modules for retrieval, generation, optimization). Native embedding now is deferred to avoid premature complexity.
Pros: built-in prompt optimization, modular composition, potential automated improvement loops.
Cons: added dependency & cognitive load, overlaps with planned internal routing/caching abstractions, tuning cycles increase latency.
Decision: Defer native support; external users can layer DSPy atop the stable OpenAI-compatible API once backend abstraction + caching + guardrails are complete.
Tracked: F24/T24 (Deferred) — revisit after embedding cache + CI guardrails ship.

Updated: 2025-09-27 (post-tokenizer integration & task expansion)
