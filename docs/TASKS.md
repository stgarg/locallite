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
| F4 | E2 | Embedding backend abstraction | In Progress | ONNX + FastEmbed stubs present, full routing later |
| F5 | E3 | Benchmark script (embeddings) | Done | Harness + drift digest + baseline captured |
| F6 | E3 | HF tokenizer integration plan | In Progress | Baseline set; spike script next |
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
| T12| F3 | Decision doc: tokenizer adoption | Todo | After spike metrics |

| T14| F2 | Wire registry into /v1/models + add /v1/models/registry | Done |
| T15| F3 | Add CLAUDE.md + memory folder aggregator | Done |

## BUGS
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| B1 | Simple tokenizer may miscount tokens | Open | Pending HF tokenizer decision |
| B2 | Provider naming ambiguity (Azure vs real NPU) | Open | Clarify in model info |

## EXPERIMENTS
| ID | Hypothesis | Status | Next Step |
|----|------------|--------|----------|
| X1 | HF tokenizer adds <5ms overhead small batch | Planned | Implement spike |
| X2 | Caching first 100 embeddings yields measurable latency reduction | Planned | Add simple LRU |

Updated: 2025-09-27 (post-baseline)
