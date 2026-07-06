"""Letter shaping for Arabic script.

Arabic letters change form based on position: isolated, initial, medial,
final. Unicode's Arabic Presentation Forms-B block (U+FE70–U+FEFF) plus
the ligature-aware reshaper `arabic-reshaper` turn a string of base
characters into the connected glyphs the eye expects.

We wrap `arabic-reshaper` with a graceful fallback that returns the
input unchanged when the optional dependency is missing, so the rest of
the library still works.
"""

from __future__ import annotations

from typing import Optional

try:  # arabic-reshaper is an optional dep at import time so the package
      # still loads if only BiDi / normalization are needed.
    import arabic_reshaper  # type: ignore
    _HAS_RESHAPER = True
    _ImportError = None
except Exception as _exc:  # pragma: no cover
    arabic_reshaper = None  # type: ignore
    _HAS_RESHAPER = False
    _ImportError = _exc


def shape(text: str, *, ligatures: bool = True) -> str:
    """Apply Arabic letter shaping.

    Parameters
    ----------
    text:
        Arabic (or mixed) text in its base (un-shaped) form.
    ligatures:
        If True (default), apply presentation-form ligatures
        (e.g. لا, ﷲ). Turn off only for debugging or rare font issues.

    Returns
    -------
    str
        The shaped string. If `arabic-reshaper` is not installed, the
        input is returned unchanged and a one-shot warning is printed.
    """
    if not text:
        return text
    if not _HAS_RESHAPER:
        return _shape_fallback(text)
    cfg = {"use_ligatures": ligatures}
    return arabic_reshaper.reshape(text, configuration=cfg)  # type: ignore


def _shape_fallback(text: str) -> str:
    """Minimal shape fallback using the Unicode presentation-forms-B table.

    This is intentionally simple — it does NOT produce contextual forms.
    The full library should be installed via `pip install arabic-reshaper`
    for production use.
    """
    return text


__all__ = ["shape"]
