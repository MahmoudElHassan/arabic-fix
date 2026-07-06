"""Tests for arabic_fix.shaper.

These tests protect the shaper against the most common failure modes:
- empty / whitespace / Latin-only inputs must pass through safely
- Arabic input must be transformed into Presentation Forms-B (U+FE70–U+FEFF)
- diacritics (tashkeel) must survive (the bug caught while writing this test)
- ligatures off must still reshape, just without the connected forms
- the shaper must be deterministic

The byte-level Presentation Forms-B assertion is the exact check that proved
the integration fix in commit a635d8a — promoted here to a regression test
so future reshaper upgrades can't silently regress to base Arabic.
"""

from __future__ import annotations

import pytest

from arabic_fix.shaper import shape


# ───────────────────────────── Pass-through cases ─────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "",  # empty
        " ",  # whitespace only
        "   ",  # multiple whitespace
        "\n\t",  # mixed whitespace
        "Hello, world!",  # pure Latin
        "12345",  # digits only
        "user@example.com",  # email-ish Latin
    ],
    ids=[
        "empty-string",
        "single-space",
        "multi-space",
        "mixed-whitespace",
        "pure-latin",
        "digits-only",
        "email-latin",
    ],
)
def test_pass_through_returns_unchanged(text: str) -> None:
    """Empty / whitespace / Latin-only inputs are returned byte-for-byte."""
    assert shape(text) == text
    assert shape(text, ligatures=False) == text


# ──────────────────────────── Presentation Forms-B ────────────────────────────


# Codepoint ranges that matter for the byte-level check.
ARABIC_BASE_BLOCK = range(0x0600, 0x0700)  # base Arabic letters + diacritics
ARABIC_PRESENTATION_FORMS_A = range(0xFB50, 0xFDFF)  # ligatures, old
ARABIC_PRESENTATION_FORMS_B = range(0xFE70, 0xFEFF)  # contextual forms


def _codepoints(text: str) -> list[int]:
    return [ord(c) for c in text]


def test_default_mode_produces_presentation_forms_b() -> None:
    """`السلام عليكم` reshapes into Presentation Forms-B (U+FE70–U+FEFF).

    This is the byte-level assertion that proved the integration fix in
    commit a635d8a. If this test ever fails, somebody upgraded
    arabic-reshaper in a way that no longer emits presentation forms.
    """
    text = "السلام عليكم"
    out = shape(text)
    cps = _codepoints(out)

    # Every letter-shaped codepoint must be in Presentation Forms-B.
    # The space U+0020 is fine; we just check that Arabic letters moved.
    arabic_out_cps = [cp for cp in cps if cp in ARABIC_BASE_BLOCK
                      or cp in ARABIC_PRESENTATION_FORMS_A
                      or cp in ARABIC_PRESENTATION_FORMS_B]
    assert arabic_out_cps, "expected Arabic codepoints in output"
    for cp in arabic_out_cps:
        assert cp in ARABIC_PRESENTATION_FORMS_B, (
            f"Arabic codepoint U+{cp:04X} is not in Presentation Forms-B "
            f"(U+FE70–U+FEFF); reshaper is no longer emitting "
            f"presentation forms"
        )


def test_input_is_base_arabic_output_is_presentation_forms_b() -> None:
    """The input codepoints are base Arabic (U+0600–U+06FF); the output codepoints are PF-B.

    This is the inverse-direction assertion: same string, but we check
    that input-vs-output blocks differ. Catches the silent failure mode
    where the shaper is wired up but doesn't actually transform.
    """
    text = "السلام عليكم"
    in_blocks = {0x0600 <= cp < 0x0700 for cp in _codepoints(text)}
    out_blocks = {0xFE70 <= cp < 0xFF00 for cp in _codepoints(shape(text))}
    assert True in in_blocks, "sanity: input is base Arabic"
    assert True in out_blocks, "shaper emitted PF-B codepoints"
    assert in_blocks != {True} or out_blocks != in_blocks, (
        "shaper did not move codepoints out of base Arabic block"
    )


# ───────────────────────────── Tashkeel preservation ──────────────────────────


# Tashkeel codepoints (Arabic Supplement block, U+064B–U+065F + U+0670).
TASKEEL_RANGE = set(range(0x064B, 0x0670)) | {0x0670}


@pytest.mark.parametrize(
    "text,expected_tashkeel_cps",
    [
        # One fatha on meem — fatha (U+064E) must survive.
        ("مَ", [0x064E]),
        # Sukun on ra — sukun (U+0652) must survive.
        ("رْ", [0x0652]),
        # Fathatan on alef — fathatan (U+064B) must survive.
        ("اً", [0x064B]),
        # Real-world: مرحبا with full tashkeel (matches eval case 3).
        ("مَرْحَبًا", [0x064E, 0x0652, 0x064E, 0x064B]),
    ],
    ids=["fatha", "sukun", "fathatan", "full-tashkeel"],
)
def test_tashkeel_preserved_default_mode(
    text: str, expected_tashkeel_cps: list[int]
) -> None:
    """Tashkeel (diacritics) survives default reshape.

    Background: arabic-reshaper 3.0.0 defaults to `delete_harakat=True`
    — we override that. If this test fails, somebody reverted the
    override in arabic_fix/shaper.py.
    """
    out = shape(text)
    out_cps = set(_codepoints(out))
    for cp in expected_tashkeel_cps:
        assert cp in out_cps, (
            f"tashkeel codepoint U+{cp:04X} was stripped from {text!r}; "
            f"output codepoints: {[hex(c) for c in _codepoints(out)]}"
        )


def test_tashkeel_preserved_ligatures_off() -> None:
    """Tashkeel also survives when ligatures=False."""
    text = "مَرْحَبًا"
    out = shape(text, ligatures=False)
    out_cps = set(_codepoints(out))
    for cp in [0x064E, 0x0652, 0x064B]:
        assert cp in out_cps, (
            f"tashkeel U+{cp:04X} stripped with ligatures=False"
        )


# ───────────────────────────── Ligatures control ──────────────────────────────


def test_ligatures_off_still_reshapes() -> None:
    """`ligatures=False` disables ligatures but still reshapes.

    Compare codepoint-by-codepoint: `ligatures=False` produces
    different (more isolated) forms than default, but still in PF-B.
    """
    text = "السلام"
    default_out = shape(text, ligatures=True)
    no_lig_out = shape(text, ligatures=False)

    default_cps = _codepoints(default_out)
    no_lig_cps = _codepoints(no_lig_out)

    # Both must be in Presentation Forms-B.
    for cp in default_cps:
        if cp in ARABIC_BASE_BLOCK or cp in ARABIC_PRESENTATION_FORMS_B:
            assert cp in ARABIC_PRESENTATION_FORMS_B
    for cp in no_lig_cps:
        if cp in ARABIC_BASE_BLOCK or cp in ARABIC_PRESENTATION_FORMS_B:
            assert cp in ARABIC_PRESENTATION_FORMS_B

    # The two outputs must differ somewhere — otherwise the flag is a no-op.
    assert default_out != no_lig_out, (
        "ligatures=False produced the same output as ligatures=True; "
        "the flag is being ignored"
    )


# ───────────────────────────── Determinism ───────────────────────────────────


def test_deterministic_across_repeated_calls() -> None:
    """Same input → same output across 100 calls.

    Catches non-determinism in the reshaper (e.g., random font selection,
    time-dependent config). Cheap to test, expensive to debug if broken.
    """
    text = "السلام عليكم مَرْحَبًا بالعالم"
    first = shape(text)
    for _ in range(100):
        assert shape(text) == first


# ───────────────────────────── Mixed-script preservation ─────────────────────


def test_latin_substring_survives_reshape() -> None:
    """Latin letters inside Arabic text are passed through untouched.

    This is the shape-only check; BiDi reorder is fixer.py's job.
    """
    text = "User 42 مرحبا"
    out = shape(text)
    assert "User 42" in out, (
        f"Latin substring lost during reshape: {out!r}"
    )


# ───────────────────────────── Codepoint invariants ──────────────────────────


@pytest.mark.parametrize(
    "text",
    ["السلام", "مَرْحَبًا", "العربية", "مكتوب"],
    ids=["bare-letters", "with-tashkeel", "with-alef-lam", "kataba-style"],
)
def test_output_keeps_most_letters(text: str) -> None:
    """Reshape doesn't catastrophically lose letters.

    Note: this is NOT a 1:1 invariant — ligatures like `ال` collapse two
    base letters into one Presentation Form-B glyph. So we check that
    the output retains *at least half* of the input letters as PF-B
    codepoints. That catches the failure mode where the shaper silently
    drops letters entirely, without false-failing on ligature collapse.
    """
    letter_count_in = sum(1 for c in text if 0x0620 <= ord(c) <= 0x064A)
    out = shape(text)
    letter_count_out = sum(
        1
        for c in out
        if 0xFE70 <= ord(c) <= 0xFEFF or 0xFB50 <= ord(c) <= 0xFDFF
    )
    assert letter_count_out >= max(1, letter_count_in // 2), (
        f"reshape lost too many letters: in={letter_count_in} "
        f"out={letter_count_out} for {text!r}"
    )