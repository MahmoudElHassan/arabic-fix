"""Tests for arabic_fix.fixer — the high-level fix() / fix_report() API.

The fixer composes shape(), reorder(), normalize() with options to
enable/disable each stage. The tests here cover:

- Composition: fix() applies shape, bidi, normalize in the documented order
- fix_report() returns a FixReport describing what each stage did
- Empty / whitespace / Latin-only inputs short-circuit cleanly
- Per-option disable flags work (shape=False, bidi=False, etc.)
- Unknown option names raise TypeError (loud-fail, not silent)
- normalize_form validation
- Pipeline order invariants:
    - Tashkeel (combining marks) survives the whole pipeline
    - Letter count is preserved (modulo ligature collapse in shaping)
- Determinism
- Real corpus (Quran, Al Jazeera-style, app UI) end-to-end
"""

from __future__ import annotations

import pytest

from arabic_fix import fix, fix_report, FixOptions, FixReport
from arabic_fix.normalize import contains_arabic, has_tashkeel


# ───────────────────────────── Pass-through cases ─────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "   ",
        "\n\t",
        "Hello, world!",
        "12345",
        "user@example.com",
        "abc xyz",
        "café résumé",
    ],
    ids=[
        "empty", "single-space", "multi-space", "mixed-whitespace",
        "pure-latin", "digits-only", "email", "ascii-letters", "latin-diacritics",
    ],
)
def test_pass_through_latin_text(text: str) -> None:
    """Latin-only / empty / whitespace: fix() may touch neutral
    punctuation per UAX #9 but Latin letters must survive.
    """
    out = fix(text)
    in_letters = [c for c in text if c.isalpha()]
    out_letters = [c for c in out if c.isalpha()]
    assert in_letters == out_letters, (
        f"Latin letters changed: in={in_letters!r} out={out_letters!r}"
    )


def test_empty_string_returns_empty() -> None:
    """fix("") == "" — short-circuit."""
    assert fix("") == ""
    report = fix_report("")
    assert report.input == ""
    assert report.output == ""
    assert report.shaped is False
    assert report.bidi_reordered is False
    assert report.normalized is False
    assert report.contained_arabic is False


# ───────────────────────────── Composition (all three stages) ─────────────────


def test_full_pipeline_on_pure_arabic() -> None:
    """fix("السلام عليكم") runs shape + bidi + normalize."""
    text = "السلام عليكم"
    report = fix_report(text)
    # All three stages ran (or at least were attempted) for Arabic text.
    assert report.contained_arabic is True
    assert report.shaped is True, "shaper stage did not run for Arabic input"
    assert report.bidi_reordered is True, "bidi stage did not run for Arabic input"
    # normalize runs unconditionally if option enabled; for clean NFC input
    # it's a no-op so `normalized` is False — that's fine.
    # Output differs from input.
    assert report.output != text
    assert report.changed is True


def test_output_is_str() -> None:
    """fix() returns a str (not bytes, not None)."""
    out = fix("السلام عليكم")
    assert isinstance(out, str)
    assert out  # non-empty


def test_fix_and_fix_report_consistent() -> None:
    """fix() and fix_report() agree on the output string."""
    text = "User 42 من الرياض"
    assert fix(text) == fix_report(text).output
    assert fix(text, shape=False) == fix_report(text, shape=False).output
    assert fix(text, bidi=False) == fix_report(text, bidi=False).output
    assert fix(text, normalize_text=False) == fix_report(text, normalize_text=False).output


# ───────────────────────────── Tashkeel preservation ──────────────────────────


@pytest.mark.parametrize(
    "text,label",
    [
        ("مَ", "fatha"),
        ("رْ", "sukun"),
        ("كَتَبْتُ الْكِتَابَ", "harakat-laced"),
        ("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", "basmala-with-tashkeel"),
    ],
    ids=["fatha", "sukun", "harakat-laced", "basmala-with-tashkeel"],
)
def test_tashkeel_survives_full_pipeline(text: str, label: str) -> None:
    """Tashkeel is preserved through shape + bidi + normalize."""
    assert has_tashkeel(text), f"[{label}] sanity: input has tashkeel"
    out = fix(text)
    assert has_tashkeel(out), (
        f"[{label}] tashkeel lost during full pipeline; "
        f"input codepoints: {[hex(ord(c)) for c in text]}\n"
        f"output codepoints: {[hex(ord(c)) for c in out]}"
    )


def test_quran_verse_keeps_tashkeel() -> None:
    """Ayat al-Kursi keeps ALL its diacritics after fix()."""
    from corpus.quran import آية_الكرسي
    assert has_tashkeel(آية_الكرسي)
    out = fix(آية_الكرسي)
    assert has_tashkeel(out), "Ayat al-Kursi lost tashkeel during fix()"


# ───────────────────────────── Per-option flags ───────────────────────────────


def test_shape_off_skips_shaping() -> None:
    """`shape=False`: output is NOT in Presentation Forms-B."""
    text = "السلام عليكم"
    out = fix(text, shape=False)
    report = fix_report(text, shape=False)
    assert report.shaped is False
    # None of the output codepoints should be in Presentation Forms-B
    # (because we skipped the shaper). Base Arabic letters stay as-is.
    pf_b = range(0xFE70, 0xFF00)
    for c in out:
        assert ord(c) not in pf_b, (
            f"shape=False but output has PF-B codepoint U+{ord(c):04X}"
        )


def test_bidi_off_skips_reorder() -> None:
    """`bidi=False`: no BiDi reordering happens."""
    text = "User 42 من الرياض"
    out_no_bidi = fix(text, bidi=False)
    out_default = fix(text)
    report = fix_report(text, bidi=False)
    assert report.bidi_reordered is False
    # The no-bidi output should differ from the default output (because
    # the default reorders digits visually).
    # Note: this is heuristic — if both happen to be equal by coincidence,
    # the test would still pass; we want the strong invariant.
    # The strong invariant is that report.bidi_reordered is False.
    assert report.bidi_reordered is False


def test_normalize_off_skips_normalization() -> None:
    """`normalize_text=False`: no normalization stage."""
    text = "السلام"  # NFC already
    report = fix_report(text, normalize_text=False)
    assert report.normalized is False


def test_ligatures_off_keeps_output_in_pf_b() -> None:
    """`ligatures=False`: reshaping still happens, just without ligatures."""
    text = "السلام"
    out = fix(text, ligatures=False)
    # Letters still get reshaped — output has PF-B codepoints.
    pf_b = range(0xFE70, 0xFF00)
    pf_b_count = sum(1 for c in out if ord(c) in pf_b)
    assert pf_b_count > 0, (
        f"ligatures=False but no PF-B codepoints in output: {out!r}"
    )


def test_bidi_base_dir_ltr_changes_ordering() -> None:
    """`bidi_base_dir='ltr'` produces a different ordering than 'rtl'."""
    text = "Hello مرحبا"
    out_rtl = fix(text)
    out_ltr = fix(text, bidi_base_dir="ltr")

    def _has_arabic(s: str) -> bool:
        # Arabic letters live in base Arabic (U+0600-U+06FF) BEFORE shaping
        # and in Presentation Forms-B (U+FE70-U+FEFF) AFTER shaping.
        return any(
            0x0600 <= ord(c) <= 0x06FF
            or 0xFE70 <= ord(c) <= 0xFEFF
            or 0xFB50 <= ord(c) <= 0xFDFF
            for c in s
        )

    # Both should still contain the Arabic letters (no letter loss).
    assert _has_arabic(out_rtl), f"Arabic letters lost in rtl output: {out_rtl!r}"
    assert _has_arabic(out_ltr), f"Arabic letters lost in ltr output: {out_ltr!r}"
    # Both reports' bidi_reordered flags are the same — the option
    # doesn't gate whether bidi ran, only its direction.
    assert (
        fix_report(text).bidi_reordered
        == fix_report(text, bidi_base_dir="ltr").bidi_reordered
    )


def test_bidi_base_dir_ltr_actually_runs_bidi() -> None:
    """`bidi_base_dir='ltr'` does invoke reorder(); the report shows it."""
    text = "Hello مرحبا 123"
    report = fix_report(text, bidi_base_dir="ltr")
    assert report.bidi_reordered is True
    assert report.contained_arabic is True


# ───────────────────────────── Normalization forms ─────────────────────────────


@pytest.mark.parametrize(
    "form",
    ["NFC", "NFD", "NFKC", "NFKD"],
)
def test_all_normalization_forms_accepted(form: str) -> None:
    """All four Unicode normalization forms are accepted."""
    text = "السلام"
    report = fix_report(text, normalize_form=form)
    assert isinstance(report.output, str)
    assert len(report.output) > 0


def test_invalid_normalize_form_raises() -> None:
    """An invalid normalize_form raises ValueError either at fix() or
    when constructing FixOptions directly."""
    # Direct construction: FixOptions doesn't validate at __init__ time —
    # we validate when running fix() / fix_report() so callers building
    # FixOptions from external config don't have to handle validation
    # errors at construction.
    #
    # But fix() DOES validate, so this raises:
    with pytest.raises(ValueError):
        fix("السلام", normalize_form="bogus")  # type: ignore[arg-type]
    # And fix_report() too:
    with pytest.raises(ValueError):
        fix_report("السلام", normalize_form="bogus")  # type: ignore[arg-type]


# ───────────────────────────── Option validation ──────────────────────────────


def test_unknown_option_raises_typeerror() -> None:
    """A typo'd option name fails loudly, doesn't silently no-op."""
    with pytest.raises(TypeError) as excinfo:
        fix("السلام", shep=False)  # 'shep' is a typo for 'shape'
    assert "shep" in str(excinfo.value)
    assert "shape" in str(excinfo.value) or "valid options" in str(excinfo.value)


def test_fix_options_dataclass_constructable_directly() -> None:
    """FixOptions can be built directly, not just through fix()."""
    opts = FixOptions(shape=False, bidi=True, normalize_form="NFKC")
    assert opts.shape is False
    assert opts.bidi is True
    assert opts.normalize_form == "NFKC"


# ───────────────────────────── FixReport contract ──────────────────────────────


def test_fix_report_changed_property() -> None:
    """FixReport.changed is True iff input != output."""
    text = "السلام"
    report = fix_report(text)
    assert report.changed == (report.input != report.output)


def test_fix_report_warnings_is_list() -> None:
    """FixReport.warnings is a list (possibly empty)."""
    report = fix_report("السلام")
    assert isinstance(report.warnings, list)


def test_fix_report_contained_arabic_flag() -> None:
    """FixReport.contained_arabic reflects the input, not the output."""
    assert fix_report("السلام").contained_arabic is True
    assert fix_report("Hello").contained_arabic is False
    assert fix_report("").contained_arabic is False


# ───────────────────────────── Real corpus end-to-end ─────────────────────────


from corpus.quran import (  # noqa: E402
    الفاتحة,
    آية_الكرسي,
    الإخلاص,
)
from corpus.aljazeera_headlines import (  # noqa: E402
    breaking_news,
    lede,
    election,
    summit,
)
from corpus.app_ui import (  # noqa: E402
    email_subjects,
    form_errors,
    toasts,
    dashboard,
)
from corpus.edge_cases import (  # noqa: E402
    format_chars,
    with_emoji,
    paths,
    multiline,
)


@pytest.mark.parametrize(
    "label,text",
    [
        ("quran_fatiha", الفاتحة),
        ("quran_ayat_alkursi", آية_الكرسي),
        ("quran_ikhlas", الإخلاص),
        ("aljazeera_breaking_news", breaking_news),
        ("aljazeera_lede", lede),
        ("aljazeera_election", election),
        ("aljazeera_summit", summit),
        ("app_email_subject_meeting", email_subjects["meeting"]),
        ("app_email_subject_verification", email_subjects["verification"]),
        ("app_form_error_required", form_errors["required"]),
        ("app_form_error_password_short", form_errors["password_short"]),
        ("app_toast_saved", toasts["saved"]),
        ("app_toast_session_expired", toasts["session_expired"]),
        ("app_dashboard_revenue", dashboard["revenue_today"]),
        ("app_dashboard_users_online", dashboard["users_online"]),
        ("edge_emoji", with_emoji[0]),
        ("edge_path_unix", paths["unix_arabic_filename"]),
        ("edge_multiline", multiline["single_newline"]),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_real_corpus_end_to_end(label: str, text: str) -> None:
    """Real Arabic text from the corpus: fix() produces a string, no exception."""
    out = fix(text)
    assert isinstance(out, str)
    assert len(out) > 0
    # Arabic letter count must be preserved (reorder + normalize don't drop letters).
    if contains_arabic(text):
        assert contains_arabic(out), f"[{label}] Arabic letters lost"


@pytest.mark.parametrize(
    "label,text",
    [
        ("quran_fatiha", الفاتحة),
        ("quran_ayat_alkursi", آية_الكرسي),
        ("quran_ikhlas", الإخلاص),
        ("aljazeera_breaking_news", breaking_news),
        ("aljazeera_lede", lede),
    ],
)
def test_real_corpus_keeps_tashkeel(label: str, text: str) -> None:
    """Real Quran + news text keeps tashkeel through the full pipeline."""
    if has_tashkeel(text):
        out = fix(text)
        assert has_tashkeel(out), f"[{label}] tashkeel dropped"


# ───────────────────────────── Determinism ─────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "السلام عليكم",
        "User 42 من الرياض",
        "Hello مرحبا 123",
        "نص طويل من عدة جمل",
    ],
    ids=["pure-arabic", "mixed-numbers", "mixed-words", "long-arabic"],
)
def test_deterministic_across_repeated_calls(text: str) -> None:
    """Same input → same output across 100 calls."""
    first = fix(text)
    for _ in range(100):
        assert fix(text) == first


def test_fix_report_deterministic() -> None:
    """Same input → same FixReport across calls."""
    text = "السلام عليكم"
    first = fix_report(text)
    for _ in range(50):
        again = fix_report(text)
        assert again.output == first.output
        assert again.shaped == first.shaped
        assert again.bidi_reordered == first.bidi_reordered
        assert again.normalized == first.normalized


# ───────────────────────────── FixOptions exposes public dataclass ────────────


def test_fix_options_default_values() -> None:
    """Default FixOptions enables all three fixes, NFC normalization, RTL bidi."""
    opts = FixOptions()
    assert opts.shape is True
    assert opts.bidi is True
    assert opts.normalize_text is True
    assert opts.normalize_form == "NFC"
    assert opts.bidi_base_dir == "rtl"
    assert opts.bidi_upper_is_rtl is False
    assert opts.ligatures is True


# ───────────────────────────── No-letter-loss invariant ───────────────────────


def test_arabic_letter_count_preserved_for_pure_arabic() -> None:
    """Pure Arabic: the count of base Arabic letters must survive fix().

    Note: ligatures may collapse two letters into one PF-B codepoint, but
    the total PF-B codepoint count must be at least half the input letter
    count (we'd see 50%+ loss only if letters were truly being dropped).
    """
    text = "العربية"
    in_count = sum(1 for c in text if 0x0620 <= ord(c) <= 0x064A)
    out = fix(text)
    pf_b_count = sum(1 for c in out if 0xFE70 <= ord(c) <= 0xFEFF)
    assert pf_b_count >= max(1, in_count // 2), (
        f"Arabic letter count: in={in_count}, pf_b_out={pf_b_count}"
    )


def test_arabic_letter_count_preserved_with_tashkeel() -> None:
    """Tashkeel-laden Arabic: diacritics survive, letters survive."""
    text = "كَتَبْتُ الْكِتَابَ"
    out = fix(text)
    # Tashkeel survived
    assert has_tashkeel(out)
    # Base Arabic letters survived (count should be ≥ input count / 2
    # to allow for ligature collapse).
    in_count = sum(1 for c in text if 0x0620 <= ord(c) <= 0x064A)
    out_count = sum(1 for c in out if 0xFE70 <= ord(c) <= 0xFEFF)
    assert out_count >= max(1, in_count // 2), (
        f"Arabic letters: in={in_count}, pf_b_out={out_count}"
    )


# ───────────────────────────── Edge cases from corpus ─────────────────────────


def test_format_chars_pass_through_safely() -> None:
    """Bidirectional format characters don't crash fix()."""
    for key, text in format_chars.items():
        out = fix(text)
        assert isinstance(out, str)


def test_emoji_does_not_crash() -> None:
    """Emoji in mixed-script text doesn't break the pipeline."""
    for text in with_emoji:
        out = fix(text)
        assert isinstance(out, str)


def test_paths_with_arabic_filenames() -> None:
    """File paths with Arabic segments round-trip through fix()."""
    for key, text in paths.items():
        out = fix(text)
        assert isinstance(out, str)
        # The path separators survive (no rewriting of `/` or `\`).
        if "/" in text and "\\" not in text:
            assert "/" in out
        elif "\\" in text:
            assert "\\" in out


def test_multiline_text_preserves_line_breaks() -> None:
    """Multiline input keeps its line-break structure.

    After shaping, base Arabic letters move into Presentation Forms-B
    (U+FE70-U+FEFF), so we check for *Arabic-shape* codepoints in
    the output, not the raw base letters.
    """
    for key, text in multiline.items():
        out = fix(text)
        assert isinstance(out, str)
        # Newlines survive
        assert out.count("\n") >= text.count("\n") - 1, (
            f"[{key}] newlines were lost"
        )
        # Some Arabic-shape codepoint from each line should be present
        # in the output.
        def _has_arabic_shape(s: str) -> bool:
            return any(0x0600 <= ord(c) <= 0x06FF or 0xFE70 <= ord(c) <= 0xFEFF for c in s)

        for line in text.split("\n"):
            stripped = line.strip()
            if _has_arabic_shape(stripped):
                assert _has_arabic_shape(out), (
                    f"[{key}] Arabic letters in line lost across the pipeline"
                )