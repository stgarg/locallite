# Memory Folder

This `memory/` directory centralizes high-signal meta knowledge for the project and provides a stable ingestion point for AI coding assistants.

Primary anchor: `CLAUDE.md` (quickstart, architecture, decisions pipeline, performance protocol).

Source-of-truth documents remain in `docs/` to avoid breaking existing links. This folder *indexes* rather than duplicates.

## Contents
- `CLAUDE.md` – Canonical assistant bootstrap context.
- (Future) `INDEX.md` – Curated, periodically refreshed synopsis once CURATION_PASS begins.

## Why Not Move Existing Docs?
We keep authoritative docs in `docs/` to preserve historical paths and avoid churn. Assistants and humans can start here, then follow links into `docs/`.

## Next Enhancements
- Generate `INDEX.md` after first curation pass.
- Add automation script to verify all decision target dates are fresh (future `tools/`).
