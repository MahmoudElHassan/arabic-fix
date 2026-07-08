"""The high-level `fix()` API — one call, all three fixes.

Pipeline order matters: shape FIRST, then BiDi-reorder, then normalize.
Skipping any step produces subtly-broken output in a different way:

    normalize → shape  : marks get reshaped into presentation forms too
                          late to fix; cached glyph tables may stay wrong.
    shape → normalize → bidi : normalization AFTER shape may decompose
                               presentation forms back to base chars.
    bidi first         : without shaping, BiDi reorders disconnected
                         glyphs and you can't fix it later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .shaper import shape
from .bidi import reorder
from .normalize import normalize, contains_arabic, NormForm
from .bidi import _RTL_LTR_TO_BIDI  # for normalizing base_dir at the API edge


@dataclass
class FixOptions:
    """Tune which fixes get applied and how."""
    shape: bool = True
    bidi: bool = True
    normalize_text: bool = True
    normalize_form: str = "NFC"        # 'NFC' | 'NFD' | 'NFKC' | 'NFKD'
    bidi_base_dir: str = "rtl"         # 'rtl' | 'ltr'
    bidi_upper_is_rtl: bool = False
    ligatures: bool = True             # reshape-config: presentation-form ligatures

    def __post_init__(self) -> None:
        """Validate and normalize fields at construction.

        Without this guard, `FixOptions(normalize_form="bogus")` silently
        succeeds, only failing later inside `unicodedata.normalize()` (or
        inside `python-bidi`) with a cryptic error that doesn't point at
        the actual `FixOptions` field. Direct construction (e.g. from a
        config file, or from library-internal code) needs the same
        validation as the `fix(**opts)` path.

        Also normalizes `bidi_base_dir`:
        - "rtl" / "ltr" (any case) → lowercased
        - "R" / "L" (python-bidi single-char codes) → expanded to "rtl"/"ltr"
        - anything else → ValueError

        Fix from v0.4.0 code review (P1.5, Cursor AI).
        """
        # --- normalize_form: accept any case, validate against the four
        # NF forms. Match the case-insensitive behavior of normalize.py.
        if not isinstance(self.normalize_form, str):
            raise TypeError(
                f"normalize_form must be str, got "
                f"{type(self.normalize_form).__name__}"
            )
        n = self.normalize_form.upper()
        if n not in {"NFC", "NFD", "NFKC", "NFKD"}:
            raise ValueError(
                f"normalize_form must be one of NFC/NFD/NFKC/NFKD, "
                f"got {self.normalize_form!r}"
            )
        self.normalize_form = n

        # --- bidi_base_dir: accept 'rtl'/'ltr' (any case) or single-char
        # codes 'R'/'L' (python-bidi compatibility). Reject everything else.
        if not isinstance(self.bidi_base_dir, str):
            raise TypeError(
                f"bidi_base_dir must be str, got "
                f"{type(self.bidi_base_dir).__name__}"
            )
        b = self.bidi_base_dir
        if b in {"R", "L"}:
            self.bidi_base_dir = "rtl" if b == "R" else "ltr"
        elif b.lower() in {"rtl", "ltr"}:
            self.bidi_base_dir = b.lower()
        else:
            raise ValueError(
                f"bidi_base_dir must be 'rtl' or 'ltr' (or 'R'/'L'), "
                f"got {b!r}"
            )


@dataclass
class FixReport:
    """Returned by `fix_report()` so callers can see what changed."""
    input: str
    output: str
    shaped: bool
    bidi_reordered: bool
    normalized: bool
    contained_arabic: bool
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.input != self.output


def _coerce_options(opts: dict[str, Any]) -> FixOptions:
    """Build FixOptions from arbitrary user kwargs, rejecting unknown keys.

    We do this rather than `FixOptions(**opts)` so a typo'd option name
    fails loudly with a helpful message instead of silently producing
    a dataclass missing that field.
    """
    known = {f for f in FixOptions.__dataclass_fields__}
    unknown = set(opts) - known
    if unknown:
        raise TypeError(
            f"unknown fix() option(s): {sorted(unknown)}; "
            f"valid options: {sorted(known)}"
        )
    # Normalize bidi_base_dir to its long form ('rtl'/'ltr') if the
    # caller passed the single-char bidi code ('R'/'L').
    if "bidi_base_dir" in opts:
        b = opts["bidi_base_dir"]
        if isinstance(b, str) and b in {"R", "L"}:
            opts["bidi_base_dir"] = "rtl" if b == "R" else "ltr"
    # Narrow normalize_form if it was passed as a valid literal.
    if "normalize_form" in opts:
        f = opts["normalize_form"]
        if f not in {"NFC", "NFD", "NFKC", "NFKD"}:
            raise ValueError(
                f"normalize_form must be one of NFC/NFD/NFKC/NFKD, got {f!r}"
            )
        opts["normalize_form"] = f
    return FixOptions(**opts)


def fix(text: str, **opts: Any) -> str:
    """One-call fix: shape, BiDi-reorder, normalize.

    Returns the fixed string. For diagnostics, use `fix_report()`.

    Examples
    --------
    >>> fix("العربية")
    '\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\\u0629'  # shaped + BiDi-fixed
    >>> fix("Hello مرحبا 123")
    ...  # digits 123 end up on the left in display order
    """
    options = _coerce_options(opts) if opts else FixOptions()
    return _apply(text, options).output


def fix_report(text: str, **opts: Any) -> FixReport:
    """Same as `fix()` but returns a `FixReport` describing what happened."""
    options = _coerce_options(opts) if opts else FixOptions()
    return _apply(text, options)


def _apply(text: str, options: FixOptions) -> FixReport:
    if not text:
        return FixReport(
            input=text,
            output=text,
            shaped=False,
            bidi_reordered=False,
            normalized=False,
            contained_arabic=False,
        )

    warnings: list[str] = []
    had_arabic = contains_arabic(text)
    out = text
    shaped_now = False
    bidi_now = False
    normalized_now = False

    if options.normalize_text:
        new = normalize(out, form=options.normalize_form)
        if new != out:
            normalized_now = True
            out = new

    if options.shape and had_arabic:
        try:
            new = shape(out, ligatures=options.ligatures)
            if new != out:
                shaped_now = True
                out = new
        except Exception as exc:  # pragma: no cover
            warnings.append(f"shaper failed: {exc}")

    if options.bidi and had_arabic:
        try:
            new = reorder(
                out,
                base_dir=options.bidi_base_dir,
                upper_is_rtl=options.bidi_upper_is_rtl,
            )
            if new != out:
                bidi_now = True
                out = new
        except Exception as exc:  # pragma: no cover
            warnings.append(f"bidi reorder failed: {exc}")

    return FixReport(
        input=text,
        output=out,
        shaped=shaped_now,
        bidi_reordered=bidi_now,
        normalized=normalized_now,
        contained_arabic=had_arabic,
        warnings=warnings,
    )


__all__ = ["fix", "fix_report", "FixOptions", "FixReport"]
