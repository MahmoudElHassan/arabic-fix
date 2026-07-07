#!/usr/bin/env python3
"""Validate designs/tokens.json against designs/tokens.schema.json.

Exits 0 on pass, 1 on schema violation, 2 on missing files / parse errors.
Token count is printed per category and overall.

Usage:  python3 validate_tokens.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "tokens.schema.json"
TOKENS_PATH = ROOT / "tokens.json"

EXPECTED_CATEGORIES = ("font", "spacing-direction", "typography", "color", "motion")
MIN_TOKENS_TOTAL = 50
MIN_TOKENS_PER_CATEGORY = 10


def count_leaf_tokens(obj: dict) -> int:
    """Count leaf tokens (nodes with $value + $type)."""
    n = 0
    for v in obj.values():
        if isinstance(v, dict):
            if "$value" in v and "$type" in v:
                n += 1
            else:
                n += count_leaf_tokens(v)
    return n


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"Error: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 2
    if not TOKENS_PATH.exists():
        print(f"Error: tokens.json not found at {TOKENS_PATH}", file=sys.stderr)
        return 2

    try:
        schema = json.loads(SCHEMA_PATH.read_text())
        data = json.loads(TOKENS_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        return 2

    # Validate
    to_validate = {
        k: v
        for k, v in data.items()
        if k != "$schema" and not k.startswith("_")
    }
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(to_validate))
    if errors:
        print(f"SCHEMA VALIDATION FAILED — {len(errors)} error(s):", file=sys.stderr)
        for e in errors[:10]:
            print(f"  - {list(e.absolute_path)}: {e.message}", file=sys.stderr)
        return 1

    # Count per category
    per_category: dict[str, int] = {}
    missing = [c for c in EXPECTED_CATEGORIES if c not in data]
    if missing:
        print(
            f"Error: missing top-level categories: {missing}",
            file=sys.stderr,
        )
        return 1
    for cat in EXPECTED_CATEGORIES:
        per_category[cat] = count_leaf_tokens(data[cat])

    total = sum(per_category.values())

    # BANNED token check
    letter_spacing = data.get("typography", {}).get("letter-spacing", {}).get("arabic", {})
    if letter_spacing.get("$value") != 0:
        print(
            "Error: typography.letter-spacing.arabic must be 0 (BANNED on Arabic).",
            file=sys.stderr,
        )
        return 1

    # Print report
    print("arabic-fix design tokens — validation report")
    print("-" * 50)
    for cat in EXPECTED_CATEGORIES:
        n = per_category[cat]
        flag = "OK" if n >= MIN_TOKENS_PER_CATEGORY else "FAIL"
        print(f"  [{flag}] {cat}: {n} token(s)")
    print("-" * 50)
    print(f"  TOTAL: {total} tokens (minimum {MIN_TOKENS_TOTAL})")
    print(f"  BANNED letter-spacing.arabic: {letter_spacing['$value']} "
          f"(must be 0) — OK")
    print("-" * 50)

    if total < MIN_TOKENS_TOTAL:
        print(f"FAIL: total below minimum ({total} < {MIN_TOKENS_TOTAL}).",
              file=sys.stderr)
        return 1
    below_min = [c for c, n in per_category.items() if n < MIN_TOKENS_PER_CATEGORY]
    if below_min:
        print(f"FAIL: categories below minimum: {below_min}", file=sys.stderr)
        return 1

    print("PASS — schema valid, all thresholds met.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
