"""arabic-fix: shape, BiDi-fix, and normalize Arabic text.

A unified API for the three things that go wrong when Arabic text flows
through systems built English-first: lost letter shaping, broken BiDi
order, and inconsistent Unicode normalization.
"""

from __future__ import annotations

from .fixer import fix, fix_report, FixOptions, FixReport

__all__ = ["fix", "fix_report", "FixOptions", "FixReport"]
__version__ = "0.1.0"
