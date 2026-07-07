"""Pytest configuration for arabic-fix tests.

Responsibilities:
- Add the repo root to sys.path so `import arabic_fix` works without
  `pip install -e .`. Tests should work straight from a fresh clone.
- Add `tests/` to sys.path so test files can do
  `from corpus.quran import ...` to pull real Arabic text fixtures.
- Register custom markers (`arabic_corpus`, `slow`) so the
  `--strict-markers` flag in pyproject.toml doesn't complain.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root = parent of this conftest.py's directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# tests/ on sys.path so `from corpus.quran import ...` works. The
# `corpus` directory is a regular subpackage of `tests`.
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


# ───────────────────────────── Pytest fixtures ────────────────────────────────


def pytest_configure(config: object) -> None:
    """Register custom markers.

    Centralized here so tests can use `pytest.mark.arabic_corpus` and
    `--strict-markers` (set in pyproject.toml) doesn't complain.
    """
    config.addinivalue_line(  # type: ignore[attr-defined]
        "markers",
        "arabic_corpus: mark a test as pulling from the real Arabic corpus "
        "(quran, Al Jazeera-style headlines, app UI strings, edge cases)",
    )
    config.addinivalue_line(  # type: ignore[attr-defined]
        "markers",
        "slow: mark a test as slow (>1s); CI may skip on a tight schedule",
    )