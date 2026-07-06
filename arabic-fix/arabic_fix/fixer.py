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
from typing import Optional

from .shaper import shape
from .bidi import reorder
from .normalize import normalize, contains_arabic


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


def fix(text: str, **opts) -> str:
    """One-call fix: shape, BiDi-reorder, normalize.

    Returns the fixed string. For diagnostics, use `fix_report()`.

    Examples
    --------
    >>> fix("العربية")
    '\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\\u0629'  # shaped + BiDi-fixed
    >>> fix("Hello مرحبا 123")
    ...  # digits 123 end up on the left in display order
    """
    options = FixOptions(**opts) if opts else FixOptions()
    return _apply(text, options).output


def fix_report(text: str, **opts) -> FixReport:
    """Same as `fix()` but returns a `FixReport` describing what happened."""
    options = FixOptions(**opts) if opts else FixOptions()
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
