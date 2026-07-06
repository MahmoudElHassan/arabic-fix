"""Skeleton — real shaper tests land in Phase C.

This file exists so Phase B can verify pytest discovers the project
and runs at all. Delete the smoke test once Phase C ships.
"""

from __future__ import annotations


def test_pytest_works() -> None:
    """Sanity check: pytest is wired and the conftest sys.path setup works."""
    import arabic_fix  # noqa: F401  (import just verifies the package is on path)

    assert True