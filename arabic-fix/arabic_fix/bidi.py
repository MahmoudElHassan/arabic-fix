"""Bidirectional (BiDi) reordering for mixed-direction text.

Arabic is RTL. Numbers and Latin words embedded inside Arabic need
explicit reordering or they land on the wrong side of the line.
`python-bidi` does this correctly; we wrap it here so callers can pass a
single string and get a display-ready one back.

For HTML/CSS contexts (which is most web output), use the system's own
BiDi engine via `direction: rtl` + `unicode-bidi: isolate` on the
container — DO NOT pre-shape Arabic inside HTML, the browser does that
better. This module is for terminals, log files, PDFs, AI chat where
no rendering engine helps.
"""

from __future__ import annotations

from typing import Optional

try:
    from bidi.algorithm import get_display  # type: ignore
    _HAS_BIDI = True
    _ImportError = None
except Exception as _exc:  # pragma: no cover
    get_display = None  # type: ignore
    _HAS_BIDI = False
    _ImportError = _exc


# python-bidi v0.6+ uses single-char codes for base_dir
_RTL_LTR_TO_BIDI = {"rtl": "R", "ltr": "L"}


def reorder(
    text: str,
    *,
    base_dir: str = "rtl",
    upper_is_rtl: bool = False,
) -> str:
    """Apply BiDi reordering for display.

    Parameters
    ----------
    text:
        Input. May already be letter-shaped, but most callers pass
        unshaped text here — shaping is a separate step.
    base_dir:
        'rtl' (default) or 'ltr'. Set 'ltr' if the dominant run is
        English with an Arabic substring. Internally translated to
        python-bidi's 'R' / 'L' codes.
    upper_is_rtl:
        Treat runs of uppercase Latin as RTL. Almost never what you
        want; default False.

    Returns
    -------
    str
        Display-ordered string. If `python-bidi` is missing, the input
        is returned unchanged.
    """
    if not text:
        return text
    if not _HAS_BIDI:
        return text
    bidi_dir = _RTL_LTR_TO_BIDI.get(base_dir.lower(), base_dir)
    return get_display(  # type: ignore
        text,
        base_dir=bidi_dir,
        upper_is_rtl=upper_is_rtl,
    )


__all__ = ["reorder"]
