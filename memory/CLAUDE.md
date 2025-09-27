# CLAUDE.md (Project Memory Anchor)

This file centralizes the high-signal context Claude (and other AI assistants) should always ingest first. It points to canonical memory layers and gives reproducible entry points for development, performance baselining, and decision hygiene.

## 1. Project Identity
Name: LocalLite (local AI gateway + Python SDK path)  
Primary Goal: Learn-by-building a high-quality local OpenAI-compatible stack (embeddings + small chat) and distill into publishable technical posts.

## 2. Memory Layer Map
| Layer | Location | Purpose |
|-------|----------|---------|
| Purpose | `docs/PURPOSE.md` | North star & success signals |
| Principles | `docs/GUIDING_PRINCIPLES.md` | Non-negotiable behavioral guardrails |
| Open Questions | `docs/OPEN_QUESTIONS.md` | Time-boxed uncertainties w/ target decision dates |
| Tasks / Epics | `docs/TASKS.md` | Execution tracking (Epics → Features → Tasks) |
| Current Focus | `docs/CURRENT_FOCUS.md` | Weekly intent snapshot |
| Session Logs | `docs/sessions/` | Daily/Ad-hoc progress summaries |
| Decisions | `docs/DECISIONS/` | Immutable rationale artifacts |
| Benchmarks | `docs/BENCHMARKS.md` | Performance baselines & drift tracking |
| Deprecations | `DEPRECATIONS.md` | Traceability for removed code/paths |

## 3. Core Runtime Architecture (ai-gateway)
Layers:
1. API: `ai-gateway/src/model_router.py` → FastAPI endpoints (OpenAI-compatible)
2. Services: `ai-gateway/src/services/` (EmbeddingService, ChatService, ModelService, MetricsService)
3. Engines/Backends: `ai-gateway/src/embedding_engine.py` (soon → formal backend interfaces)
4. Registry: `ai-gateway/src/runtime/model_registry.py` (static specs → will unify with ModelService state)
5. Models: `models/` (download scripts under `scripts/`)
6. Tests: `ai-gateway/tests/`

Planned refinement: Introduce `runtime/backends/` with protocol-based pluggable backends (ONNX, fastembed, future HF/gguf).

## 4. Quickstart (Local Dev)
```bash
# Create env
python -m venv .venv && source .venv/bin/activate
pip install -r ai-gateway/requirements.txt

# Run API
ython ai-gateway/src/main.py  # (Serves on 127.0.0.1:8000)

# Smoke test
curl http://127.0.0.1:8000/health | jq

# Run tests (structural)
pytest ai-gateway/tests -q
```
Benchmark harness & deterministic tests:
- Harness: `ai-gateway/src/benchmarks/embedding_benchmark.py` (multi-batch, p50/p95, digest, JSON output)
- Inputs: `ai-gateway/src/benchmarks/benchmark_inputs.txt`
- Digest subset: `ai-gateway/src/benchmarks/digest_inputs.txt`
- Determinism test: `ai-gateway/tests/test_embedding_determinism.py`

## 5. Common Commands
| Intent | Command |
|--------|---------|
| Install deps | `pip install -r ai-gateway/requirements.txt` |
| Run server | `python ai-gateway/src/main.py` |
| Health check | `curl /health` |
| List models | `curl /v1/models` |
| Embed | `curl -X POST /v1/embeddings` |
| Chat | `curl -X POST /v1/chat/completions` |
| Tests | `pytest ai-gateway/tests -q` |

## 6. Decision Hygiene
Create decisions as `docs/DECISIONS/<ID>_<SLUG>.md` with template:
```
# Decision: <Title>
Date:
Status: Proposed|Accepted|Rejected
Context:
Options:
Decision:
Rationale:
Consequences (Positive / Negative):
Review Date:
```
Upcoming: TOKENIZER_CHOICE (by 2025-10-03), LLM_BACKEND_STRATEGY, DOC_PIPELINE_STORAGE.

## 7. Performance Baseline Protocol (Embeddings)
1. Run harness:
```bash
python ai-gateway/src/benchmarks/embedding_benchmark.py \
	--model bge-small-en-v1.5 --backend onnx-custom \
	--batch-sizes 1,2,4,8 --runs 5 --discard-warmup 1 \
	--out benchmarks/results/$(date +%Y%m%d)_bge.json
```
2. Capture metrics (p50, p95, mean, stdev, throughput) + digest.
3. Update `docs/BENCHMARKS.md` table rows.
4. If digest change intentional, add DECISION entry first.

## 8. Deterministic Embedding Digest (Planned)
- Quantize: round float32 vectors to 6 decimals → bytes → SHA256.
- Store canonical digest for a fixed sample set in `docs/BENCHMARKS.md`.
- Add `tests/test_embedding_determinism.py` to ensure no drift.

## 9. Tokenization Strategy (Risk Area)
Current: heuristic lowercase `.split()` → token counting drift risk.  
Spike: Compare HF tokenizer (e.g. `tokenizers` BERT style) vs heuristic on 5-string sample set; record overhead & accuracy; produce decision doc.

## 10. Provider Routing
Current rule-of-thumb (embedding_engine): batch ≤3 → CPU-ARM64 label; else Azure (if available) else CPU. Clarify that "Azure" here is a provider fallback, not real NPU yet. Future: replace with actual QNN provider detection.

## 11. Deprecation Practice
When archiving directories (e.g., `EmbeddingServer/`, `DocumentProcessor/`), move under `archive/` + add pointer line in `DEPRECATIONS.md` with date + rationale + replacement path.

## 12. Style & Conventions
- Logging: INFO for lifecycle / performance summary; DEBUG for per-request internals.
- Tests: File naming `test_*.py`; deterministic tests separate from perf tests.
- Avoid random fallbacks for model outputs—fail loud (remove random embedding fallback soon).
- License metadata required in every `ModelSpec`.

## 13. Roadmap (Near-Term Extract)
Phase 0 Remaining:
- Registry ↔ API wiring + enriched model listing
- Baseline benchmarks + digest
- Tokenizer decision
- Archive legacy servers
- Backend interface formalization

## 14. Glossary
| Term | Meaning |
|------|---------|
| Model Registry | Static + dynamic model metadata authoritative source |
| Backend | Specific implementation (ONNX, fastembed, etc.) behind a protocol |
| Digest | Stable hash of normalized embedding vector(s) |
| Memory Docs | Persistent scaffolding enabling fast mental reload |
| Drift | Change in embedding output or latency beyond tolerance |

## 15. Assistant Usage Tips
When asking an AI assistant for code changes:
- Reference file paths explicitly.
- State whether change affects public endpoint or internal API.
- Provide expected contract (inputs / outputs / error modes) if new component.

## 16. Open Risks (Active)
- Token drift (mitigate via tokenizer decision + test)
- Lack of performance baseline (do before refactor)
- Registry not source of truth yet
- Random fallback embeddings hide failures

Updated: 2025-09-27
