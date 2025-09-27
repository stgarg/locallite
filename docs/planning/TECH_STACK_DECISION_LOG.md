# Tech Stack Decision Log
Date: 2025-09-27
Status: Accepted (Phase 0)
Owner: Core Maintainers
Revisit Window: 6–8 weeks or upon major new hardware target (e.g. Linux NPU stack maturity, GPU addition), or if latency targets unmet by >25%.

---
## 1. Context & Goals
We are formalizing the baseline stack for LocalLite (FastEmbed evolution) before executing Phase 0 cleanup. Core mission: Local, private, low-latency AI gateway (embeddings, chat/LLM, document enrichment & retrieval) with an SDK and OpenAI-compatible API surface.

Key non‑functional goals:
- Developer velocity (fast iteration, easy contributions)
- Deterministic + portable inference
- Hardware acceleration (CPU, NPU now; GPU optional later)
- Simplicity of deployment (local dev, future Docker)
- Extensibility for multi-modal and document pipeline

## 2. Candidate Stack Components Considered
| Layer | Option(s) | Notes |
|-------|-----------|-------|
| Inference Runtime | ONNX Runtime, PyTorch (direct), ExecuTorch, ggml, custom Rust ORT bindings | Need broad model coverage + NPU/DirectML/QNN; ONNX Runtime already in use. |
| Embedding Models API | Custom engine (`embedding_engine.py`), `fastembed` library, sentence-transformers, Hugging Face pipeline wrappers | Need balance of performance + reproducibility; `fastembed` good for some models; custom logic needed for provider routing + telemetry. |
| Language / Orchestration | Python, C#, Rust (Axum/Tonic), Go | Python already primary; C# legacy; Rust good for future perf-critical plug-ins. |
| Chat / LLM Execution | ONNX Runtime (Phi-3 etc.), vLLM (future for GPU), MLC / llama.cpp integration | Start ONNX for uniformity; design adapter interface to swap. |
| Document Processing | Python ecosystem (pypdf, pymupdf, docling, unstructured, rapidocr) | Python has strongest coverage; unify behind adapters. |
| Vector Index | FAISS (CPU), sqlite + faiss, LanceDB, Chroma, Qdrant (remote) | Start lightweight: FAISS + SQLite metadata; keep abstraction. |
| Tokenization | HuggingFace tokenizers (fast), custom fallback | Replace simplistic split-tokenizer ASAP for accuracy and correct token accounting. |
| Metrics / Observability | Prometheus + structured JSON logs | Simplicity + ecosystem tooling. |
| Packaging | Pip + requirements files, optional Docker; later: model bundle manifests | Keep lean first; add bundle spec Phase 5+. |

## 3. Evaluation Criteria & Scores (1–5, higher is better)
| Criterion | Python + ONNX | C# + ONNX | Rust + ORT Bindings | Mixed (Python orchestrates, Rust cores) |
|-----------|---------------|-----------|--------------------|----------------------------------------|
| Dev Velocity | 5 | 3 | 2 | 4 |
| Existing Code Leverage | 5 | 2 | 1 | 4 |
| Ecosystem for Docs/OCR/Parsing | 5 | 2 | 2 | 5 |
| NPU / Provider Support Today | 4 (QNN / DirectML via ORT) | 4 | 4 | 4 |
| Community Contributor Familiarity | 5 | 3 | 2 | 4 |
| Performance Headroom (Future) | 4 | 4 | 5 | 5 |
| Complexity Overhead | 3 | 3 | 4 | 2 |
| Deployment Simplicity | 4 | 3 | 3 | 3 |
| Extensibility (Plugins) | 4 | 4 | 5 | 5 |
| Total | 39 | 30 | 28 | 40 |

Mixed approach (Python orchestration + optional Rust perf modules) slightly edges pure Python long-term, but pure Python is optimal for immediate Phase 0–2.

## 4. Decision (Baseline Stack)
Adopt a Python-first architecture using ONNX Runtime for embeddings & initial chat models.

- Keep ONNX Runtime as the universal inference substrate (provides CPU + NPU portability and model interchange format).
- Maintain custom `embedding_engine` abstraction but refactor into: tokenizer adapter, provider selector, runtime session manager.
- Integrate HuggingFace `tokenizers` for correctness (deterministic embeddings, proper token accounting). Fallback lightweight tokenizer retained for bootstrapping.
- Use `fastembed` selectively for any models where it materially improves performance or reduces maintenance (wrap behind a uniform interface so we can swap).
- Deprecate C# server (archive) — remove from active path to reduce cognitive load.
- Postpone Rust until specific hotspots (e.g., high-throughput embedding batching or vector post-processing) become bottlenecks and are proven by profiling.
- Design plugin boundary so later Rust or C++ acceleration (quantization kernels, re-rankers) can slot in without API changes.

## 5. Near-Term Architecture Shape
```
ai-gateway/
  src/
    config/            # Pydantic settings (Phase 1)
    runtime/
      embedding_runtime.py   # provider selection + sessions
      tokenization.py        # HF tokenizer wrapper + fallback
      model_registry.py      # metadata + lazy loaders
    services/
      embedding_service.py
      chat_service.py
      document_service.py (placeholder)
    api/
      routes_embeddings.py
      routes_chat.py
      routes_documents.py (future)
    indexing/ (Phase 3)
      store_faiss.py
      store_sqlite.py
```

## 6. Why Not C# Now?
- Increases dual-language maintenance burden.
- Python already hosts planned document/OCR libraries.
- No immediate perf gap justifying rewrite; profiling first.

## 7. Why Not Rust First?
- Upfront build friction + slower contributor ramp.
- Most early latency anchored in model runtime (ORT) and tokenization, not Python overhead.
- We can surgically introduce Rust crates later behind FFI if Python CPU time for orchestration >20% of request budget.

## 8. Future Rust / Native Acceleration Entry Points
| Candidate | Trigger Threshold | Notes |
|-----------|------------------|-------|
| High-throughput batching queue | >5K embeddings/sec target | Tokio/Axum microservice or Rust lib via pyo3 |
| Reranker / cross-encoder | Latency-critical pipelines | Could run with candle/onnx in Rust |
| Vector post-processing (PQ, ANN) | Need >10M vectors local | Use `hnsw` / `tantivy` or bind FAISS wrappers |

## 9. Revisit Triggers
- Need GPU-first optimization (vLLM integration) → maybe expand beyond pure ONNX
- Large user demand for single static self-contained binary → consider Rust packaging
- Python GIL contention observed in profiling with concurrency > 256 RPS → evaluate Rust task runtime

## 10. Immediate Phase 0 Action Items
| Item | Action | Owner | Status |
|------|--------|-------|--------|
| Archive Legacy C# | Move `EmbeddingServer/` → `archive/EmbeddingServer/` + add note in root README | Maintainer | Pending |
| Archive Old Entrypoints | Move `ai-gateway/src/main_old.py` and `backup/` duplicates → `archive/legacy/` | Maintainer | Pending |
| Create Deprecations Doc | `DEPRECATIONS.md` with rationale + migration notes | Maintainer | Pending |
| Introduce Decision Log | (This file) | Done | ✅ |
| Plan Config Module | Draft `config/settings.py` with env schema | Maintainer | Pending |
| Tokenizer Plan | Select HF tokenizer package + dependency pin | Maintainer | Pending |
| Model Registry Skeleton | Define metadata structure (id, path, dims, modality) | Maintainer | Pending |

## 11. Next (Phase 1 Preview)
- Implement `config/settings.py` (Pydantic BaseSettings) → unify env access.
- Create `runtime/model_registry.py` with static registry + lazy loader.
- Refactor `embedding_engine.py` into `runtime/embedding_runtime.py` + `runtime/tokenization.py`.
- Add unit tests for new components before deleting old engine (safety net).

## 12. Communication Plan
- Root README: Add "Tech Stack: Python + ONNX Runtime" + note about archived C#.
- Changelog entry referencing this decision log.
- PR template addition: "Does this change affect tech stack assumptions?".

## 13. Open Questions (Track, Don’t Block)
| Question | Resolution Path |
|----------|-----------------|
| Add GPU (CUDA) early? | Wait until clear model requiring GPU (e.g., larger Llama) |
| Add quantization pipeline? | Evaluate ORT + onnxruntime-tools vs llama.cpp integration |
| Use `fastembed` for all embeddings? | Benchmark vs custom path; choose per-model. |
| Multi-process vs async for concurrency? | Benchmark under uvicorn workers after Phase 1 refactor. |

## 14. Summary Statement
We standardize on Python + ONNX Runtime for rapid evolution of the local AI gateway, deferring Rust/C# until profiling data justifies native optimization. Architecture will modularize runtime, model registry, tokenization, and services now to keep future polyglot acceleration paths open.

---
Decision Accepted. Begin executing Phase 0 cleanup tasks.
