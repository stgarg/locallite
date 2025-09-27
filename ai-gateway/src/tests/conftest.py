"""Pytest configuration to ensure source modules are importable.
Adds the parent src directory (containing `runtime`, `services`, etc.) to sys.path
so tests can `import runtime...` without installing the package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent.parent  # .../ai-gateway/src
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
