# GUIDING PRINCIPLES

1. Measure Before Optimizing – Always capture a baseline (latency, memory) before refactors.
2. Replaceable Backends – No embedding/chat backend is permanent; abstractions first, allegiance later.
3. Thin Public Surface – Keep APIs minimal; enrich via docs/examples instead of premature feature flags.
4. Deterministic Repro – Same inputs → same outputs (tokenization, normalization, model versions pinned).
5. Document Before Deleting – Any removal of capability has a note in DEPRECATIONS.md or DECISIONS/.
6. Dogfood the SDK – Internal scripts prefer the public client path.
7. Prefer Clarity Over Cleverness – Readability beats micro-optimizations (unless profiler disagrees).
8. Small, Safe Iterations – Merge vertical slices; avoid giant refactor branches.
9. Performance Predictability – Stable p95 latency > record p50.
10. License Awareness – Every model/spec includes license metadata; no opaque additions.

Updated: 2025-09-27
