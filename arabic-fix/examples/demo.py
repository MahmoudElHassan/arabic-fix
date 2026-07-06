"""
demo.py — end-to-end smoke test.

Runs the library against representative strings and prints before/after.
Run with:

    pip install -e .
    python examples/demo.py
"""

from arabic_fix import fix, fix_report


CASES = [
    # (label, raw_input)
    ("pure Arabic, no diacritics",
     "مرحبا بالعالم"),

    ("pure Arabic, with full tashkeel",
     "مَرْحَبًا بِالْعَالَمِ"),

    ("mixed BiDi (digits + Arabic + Latin)",
     "User 42 logged in from الرياض at 09:30 today"),

    ("English sentence with Arabic substring (base LTR)",
     "The capital of Saudi Arabia is الرياض"),

    ("ligature-heavy word (ال → connected)",
     "العربية للغة الجميلة"),

    ("phone number in an Arabic sentence",
     "اتصل بي على +966 50 123 4567 مساءً"),

    ("Email + Arabic",
     "مرحبا user@example.com كيف حالك؟"),

    ("empty string (must not crash)",
     ""),

    ("Latin only (must pass through unchanged)",
     "Hello, world!"),
]


def _truncate(s: str, n: int = 60) -> str:
    if len(s) <= n:
        return repr(s)
    return repr(s[: n - 1] + "…")


def main() -> int:
    print(f"{'CASE':<48} {'CHANGED':<8} {'SHAPE':<6} {'BIDI':<6} {'NORM':<6}")
    print("-" * 80)
    for label, raw in CASES:
        report = fix_report(raw)
        marker = "yes" if report.changed else "no"
        print(
            f"{label:<48} "
            f"{marker:<8} "
            f"{('yes' if report.shaped else 'no'):<6} "
            f"{('yes' if report.bidi_reordered else 'no'):<6} "
            f"{('yes' if report.normalized else 'no'):<6}"
        )
        if raw != "":
            print(f"  input : {_truncate(raw)}")
            print(f"  output: {_truncate(report.output)}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
