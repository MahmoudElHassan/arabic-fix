"""Pytest configuration for arabic-fix tests.

We don't rely on `pip install -e .` being run before tests — the
project's src layout puts `arabic_fix/` at the repo root, so we add
the repo root to `sys.path` here. This lets `pytest` work directly
from a fresh clone + `pip install -r requirements-dev.txt`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root = parent of this conftest.py's directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))