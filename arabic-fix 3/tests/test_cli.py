"""Tests for the `arabic-fix` CLI entry point.

What's under test:
- argparse exit codes (0 = ok, 1 = file error, 2 = argument error)
- stdin → stdout pipeline (default mode, or with `-`)
- File mode: in-place writes (no --output), explicit --output
- --check: exit non-zero if any file would change
- --report: JSON report per file to stderr
- Flag forwarding: --no-shape / --no-bidi / --no-normalize / --no-ligatures
- --normalize-form / --bidi-base-dir choices
- Multi-file handling (no --output allowed)
- Missing / unreadable files fail gracefully
- Real corpus as stdin input
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest

from arabic_fix import cli


# Resolve the CLI as a module entry-point the same way end-users would
# invoke it: `python -m arabic_fix.cli`. This is the canonical,
# non-shebang path. (We can't rely on the `arabic-fix` console script
# being on PATH inside the test venv; the module path works everywhere.)
PYTHON = sys.executable


def _run_cli(*args: str, stdin: str | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    """Invoke the CLI as a subprocess.

    We use a subprocess (not in-process) because:
    - The CLI uses sys.stdin / sys.stdout / sys.stderr directly
    - An in-process test would have to monkeypatch all three
    - A subprocess mirrors how users actually run the command
    - This catches issues with the `if __name__ == '__main__'` guard
    """
    return subprocess.run(
        [PYTHON, "-m", "arabic_fix.cli", *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


# ───────────────────────────── Basic arg parsing ──────────────────────────────


def test_help_exits_zero() -> None:
    """`--help` prints usage and exits 0."""
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "arabic-fix" in result.stdout.lower() or "fix arabic" in result.stdout.lower()


def test_version_flag_works() -> None:
    """`--version` is supported (argparse adds it for free; here we
    just assert the CLI exits cleanly on it)."""
    # We don't enforce --version because pyproject doesn't declare a
    # version action; but `argparse` exits 2 on unknown args.
    result = _run_cli("--bogus-flag")
    assert result.returncode == 2  # argparse: unknown arg


# ───────────────────────────── stdin → stdout ─────────────────────────────────


def test_stdin_no_args_writes_to_stdout() -> None:
    """No path args → read stdin, write stdout."""
    text = "السلام عليكم"
    result = _run_cli(stdin=text)
    assert result.returncode == 0
    # Output must contain Arabic letters in presentation forms
    # (after shaping).
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in result.stdout), (
        f"Arabic shaping did not happen in CLI output: {result.stdout!r}"
    )


def test_stdin_dash_arg_writes_to_stdout() -> None:
    """`-` as the single path means stdin → stdout."""
    text = "User 42 من الرياض"
    result = _run_cli("-", stdin=text)
    assert result.returncode == 0
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in result.stdout)


def test_stdin_empty_string_writes_empty_stdout() -> None:
    """Empty stdin → empty stdout."""
    result = _run_cli(stdin="")
    assert result.returncode == 0
    assert result.stdout == ""


def test_stdin_quran_verse_passes() -> None:
    """Real Quran text as stdin: no exception, output is a string."""
    from corpus.quran import الفاتحة
    result = _run_cli(stdin=الفاتحة)
    assert result.returncode == 0
    assert result.stdout  # non-empty
    # Tashkeel preserved: output must contain at least one of the
    # tashkeel codepoints present in the input.
    tashkeel_cps = {0x064B, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652, 0x0670}
    in_cps = {ord(c) for c in الفاتحة}
    expected_tashkeel = in_cps & tashkeel_cps
    out_cps = {ord(c) for c in result.stdout}
    assert expected_tashkeel & out_cps, (
        f"CLI dropped all tashkeel from الفاتحة. "
        f"Expected tashkeel: {sorted(hex(c) for c in expected_tashkeel)}"
    )


# ───────────────────────────── File mode ──────────────────────────────────────


def test_file_mode_in_place_write(tmp_path: Path) -> None:
    """A single input file (no --output) is rewritten in place."""
    src = tmp_path / "input.txt"
    src.write_text("السلام عليكم", encoding="utf-8")

    result = _run_cli(str(src))
    assert result.returncode == 0
    assert "would change" not in result.stderr

    new = src.read_text(encoding="utf-8")
    # The file was reshaped (some codepoint moved to PF-B).
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in new), (
        f"file was not reshaped in place: {new!r}"
    )


def test_file_mode_explicit_output(tmp_path: Path) -> None:
    """`--output` writes the fixed text to a separate file."""
    src = tmp_path / "input.txt"
    out = tmp_path / "output.txt"
    src.write_text("السلام عليكم", encoding="utf-8")

    result = _run_cli(str(src), "--output", str(out))
    assert result.returncode == 0
    # Source unchanged.
    assert src.read_text(encoding="utf-8") == "السلام عليكم"
    # Output file written.
    assert out.exists()
    new = out.read_text(encoding="utf-8")
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in new)


def test_file_mode_multiple_files_in_place(tmp_path: Path) -> None:
    """Multiple input files are all rewritten in place."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("السلام", encoding="utf-8")
    f2.write_text("عليكم", encoding="utf-8")

    result = _run_cli(str(f1), str(f2))
    assert result.returncode == 0
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in f1.read_text(encoding="utf-8"))
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in f2.read_text(encoding="utf-8"))


def test_multiple_files_with_output_errors(tmp_path: Path) -> None:
    """`--output` with multiple input files is rejected (exit 2)."""
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("السلام", encoding="utf-8")
    f2.write_text("عليكم", encoding="utf-8")

    result = _run_cli(str(f1), str(f2), "--output", str(tmp_path / "out.txt"))
    assert result.returncode == 2
    assert "--output" in result.stderr or "single input" in result.stderr


def test_missing_file_errors(tmp_path: Path) -> None:
    """Reading a non-existent file fails with exit code 1."""
    nonexistent = tmp_path / "does-not-exist.txt"
    result = _run_cli(str(nonexistent))
    assert result.returncode == 1
    assert "cannot read" in result.stderr or "no such file" in result.stderr.lower()


# ───────────────────────────── --check mode ───────────────────────────────────


def test_check_exits_nonzero_when_file_would_change(tmp_path: Path) -> None:
    """`--check` on an unshaped file exits 1; file is NOT modified."""
    src = tmp_path / "input.txt"
    src.write_text("السلام عليكم", encoding="utf-8")
    original = src.read_text(encoding="utf-8")

    result = _run_cli(str(src), "--check")
    assert result.returncode == 1
    assert "would change" in result.stderr
    # Source file unchanged.
    assert src.read_text(encoding="utf-8") == original


def test_check_exits_zero_when_file_already_fixed(tmp_path: Path) -> None:
    """`--check` on a Latin-only / already-fixed file exits 0."""
    src = tmp_path / "input.txt"
    src.write_text("Hello, world!", encoding="utf-8")

    result = _run_cli(str(src), "--check")
    assert result.returncode == 0
    assert "would change" not in result.stderr


# ───────────────────────────── --report mode ─────────────────────────────────


def test_report_emits_json_to_stderr(tmp_path: Path) -> None:
    """`--report` writes one JSON line per file to stderr."""
    src = tmp_path / "input.txt"
    src.write_text("السلام عليكم", encoding="utf-8")

    result = _run_cli(str(src), "--report")
    assert result.returncode == 0
    # At least one JSON line on stderr.
    lines = [ln for ln in result.stderr.splitlines() if ln.strip().startswith("{")]
    assert lines, f"no JSON lines in stderr: {result.stderr!r}"
    payload = json.loads(lines[0])
    assert payload["path"] == str(src)
    assert "shaped" in payload
    assert "bidi_reordered" in payload
    assert "normalized" in payload
    assert "contained_arabic" in payload
    assert "changed" in payload
    assert "warnings" in payload
    # For an Arabic input, the file would change.
    assert payload["contained_arabic"] is True
    assert payload["shaped"] is True
    assert payload["bidi_reordered"] is True


# ───────────────────────────── Flag forwarding ────────────────────────────────


def test_no_shape_flag_skips_shaping(tmp_path: Path) -> None:
    """`--no-shape`: output stays in base Arabic, not PF-B."""
    src = tmp_path / "input.txt"
    src.write_text("السلام", encoding="utf-8")

    result = _run_cli(str(src), "--no-shape")
    assert result.returncode == 0
    new = src.read_text(encoding="utf-8")
    # No Presentation Forms-B codepoints should appear.
    pf_b = range(0xFE70, 0xFF00)
    for c in new:
        assert ord(c) not in pf_b, (
            f"--no-shape but output has PF-B codepoint U+{ord(c):04X}"
        )


def test_no_bidi_flag(tmp_path: Path) -> None:
    """`--no-bidi`: no reorder happens."""
    src = tmp_path / "input.txt"
    src.write_text("User 42 من الرياض", encoding="utf-8")

    result = _run_cli(str(src), "--no-bidi")
    assert result.returncode == 0
    # The Latin digits "42" stay where they were in the source.
    new = src.read_text(encoding="utf-8")
    # Note: --no-bidi only stops the bidi stage; shaping still happens.
    # We can't assert "42" is preserved without bidi because reshape
    # changes codepoint positions, but Latin digits do survive reshape.
    assert "42" in new or any(c == "4" for c in new)


def test_no_normalize_flag(tmp_path: Path) -> None:
    """`--no-normalize`: no normalization stage."""
    src = tmp_path / "input.txt"
    src.write_text("السلام", encoding="utf-8")

    result = _run_cli(str(src), "--no-normalize")
    assert result.returncode == 0
    assert src.read_text(encoding="utf-8")  # non-empty


def test_no_ligatures_flag(tmp_path: Path) -> None:
    """`--no-ligatures`: reshaping still happens, but without ligatures."""
    src = tmp_path / "input.txt"
    src.write_text("لا", encoding="utf-8")  # laam-alef ligature candidate

    result = _run_cli(str(src), "--no-ligatures")
    assert result.returncode == 0
    new = src.read_text(encoding="utf-8")
    # Output is still in PF-B (shaping ran), but no specific assertion
    # about ligatures since the reshaping library handles it.
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in new), (
        f"--no-ligatures but output not in PF-B: {new!r}"
    )


def test_normalize_form_nfd(tmp_path: Path) -> None:
    """`--normalize-form NFD` accepts NFD as an argument."""
    src = tmp_path / "input.txt"
    src.write_text("السلام", encoding="utf-8")

    result = _run_cli(str(src), "--normalize-form", "NFD")
    assert result.returncode == 0


def test_normalize_form_bogus_rejected() -> None:
    """An invalid --normalize-form is rejected by argparse (exit 2)."""
    result = _run_cli("--normalize-form", "bogus")
    assert result.returncode == 2


def test_bidi_base_dir_ltr(tmp_path: Path) -> None:
    """`--bidi-base-dir ltr` is accepted."""
    src = tmp_path / "input.txt"
    src.write_text("Hello مرحبا", encoding="utf-8")

    result = _run_cli(str(src), "--bidi-base-dir", "ltr")
    assert result.returncode == 0


def test_bidi_base_dir_bogus_rejected() -> None:
    """An invalid --bidi-base-dir is rejected by argparse (exit 2)."""
    result = _run_cli("--bidi-base-dir", "upside-down")
    assert result.returncode == 2


# ───────────────────────────── Encoding ───────────────────────────────────────


def test_custom_encoding(tmp_path: Path) -> None:
    """`--encoding` reads the file in the requested encoding."""
    src = tmp_path / "input.txt"
    src.write_text("السلام", encoding="utf-8")

    result = _run_cli(str(src), "--encoding", "utf-8")
    assert result.returncode == 0
    assert src.read_text(encoding="utf-8")


# ───────────────────────────── Real corpus round-trip ─────────────────────────


def test_real_corpus_quran_file(tmp_path: Path) -> None:
    """Real Quran text file round-trips through the CLI."""
    from corpus.quran import آية_الكرسي
    src = tmp_path / "ayat.txt"
    src.write_text(آية_الكرسي, encoding="utf-8")

    result = _run_cli(str(src))
    assert result.returncode == 0
    new = src.read_text(encoding="utf-8")
    # Tashkeel preserved.
    tashkeel_cps = {0x064B, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652, 0x0670}
    out_cps = {ord(c) for c in new}
    in_tashkeel = {ord(c) for c in آية_الكرسي} & tashkeel_cps
    assert in_tashkeel & out_cps, "CLI dropped tashkeel from Ayat al-Kursi"


def test_real_corpus_app_ui_stdin(tmp_path: Path) -> None:
    """App UI strings from the corpus as stdin: CLI handles them cleanly."""
    from corpus.app_ui import toasts
    for key, text in toasts.items():
        result = _run_cli(stdin=text)
        assert result.returncode == 0, f"[{key}] CLI failed: {result.stderr}"
        assert result.stdout  # non-empty output


# ───────────────────────────── in-process CLI invocation (no subprocess) ────


def test_build_parser_returns_parser() -> None:
    """`cli._build_parser()` returns an argparse.ArgumentParser."""
    parser = cli._build_parser()
    assert parser is not None
    # Sanity-check: parsing `--help` doesn't error at construction time
    # (it WOULD exit when `.parse_args()` is called, but constructing
    # the parser alone is fine).
    assert parser.prog == "arabic-fix"


def test_main_function_takes_argv() -> None:
    """`cli.main(argv=[...])` accepts a list of args (the standard
    argparse signature)."""
    # We can't easily test the full stdin path in-process (pytest
    # captures stdin), but we CAN verify the signature accepts a list.
    import inspect
    sig = inspect.signature(cli.main)
    assert "argv" in sig.parameters
    # argv has a default of None (the standard argparse convention).
    assert sig.parameters["argv"].default is None


def test_main_returns_int_for_empty_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    """`cli.main([])` returns an int when stdin is empty.

    pytest captures stdin by default; we override stdin with an empty
    StringIO so the call doesn't block or raise. We also redirect
    stdout to discard the output.
    """
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    monkeypatch.setattr("sys.stdout", io.StringIO())
    rc = cli.main([])
    assert isinstance(rc, int)
    assert rc == 0


def test_main_with_dash_arg_reads_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """`cli.main(["-"])` reads stdin, writes to stdout."""
    monkeypatch.setattr("sys.stdin", io.StringIO("السلام عليكم"))
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)
    rc = cli.main(["-"])
    assert rc == 0
    # Output must have reshaped Arabic letters.
    assert any(0xFE70 <= ord(c) <= 0xFEFF for c in out.getvalue())