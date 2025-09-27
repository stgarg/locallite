# DEPRECATIONS
Tracks components removed or frozen. Do not delete entries; append with dates.

| Component | Original Location | Status | Date | Rationale | Replacement |
|-----------|-------------------|--------|------|-----------|-------------|
| Legacy main_old.py | ai-gateway/src/main_old.py | Archived | 2025-09-27 | Duplicate entrypoint; consolidation | main.py |
| C# EmbeddingServer | EmbeddingServer/ | Pending Archive | 2025-09-27 | Shift to single Python runtime; reduce cognitive load | Python runtime + future modular backends |
| backup/ experimental scripts | ai-gateway/backup/ | Pending Review | 2025-09-27 | Redundant logic & old experiments | Curated examples or removal |

Notes:
- Full archival of EmbeddingServer will involve moving directory under /archive with README marker.
- backup/ will be triaged; only keep scripts that add unique instructional value.
