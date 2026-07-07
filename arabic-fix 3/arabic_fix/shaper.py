"""Letter shaping for Arabic script.

Arabic letters change form based on position: isolated, initial, medial,
final. Unicode's Arabic Presentation Forms-B block (U+FE70–U+FEFF) plus
the ligature-aware reshaper `arabic-reshaper` turn a string of base
characters into the connected glyphs the eye expects.

We wrap `arabic-reshaper` with a graceful fallback that returns the
input unchanged when the optional dependency is missing, so the rest of
the library still works.

Note: `arabic-reshaper` 3.0.0's `default_config` has
`delete_harakat=True`. We override that to **preserve tashkeel**
(matches `agents/eval_cases.md` Case 3 — "Tashkeel preservation").
Stripping diacritics silently is a content-loss bug.
"""

from __future__ import annotations

from typing import Optional

try:  # arabic-reshaper is an optional dep at import time so the package
      # still loads if only BiDi / normalization are needed.
    import arabic_reshaper  # type: ignore[import-untyped]
    from arabic_reshaper.reshaper_config import (  # type: ignore[import-untyped]
        default_config as _default_config,
    )
    _HAS_RESHAPER = True
    _ImportError: Exception | None = None
except Exception as _exc:  # pragma: no cover
    # mypy sees these names as Any (module is untyped), so plain `= None`
    # works without an explicit ignore.
    arabic_reshaper = None
    _default_config = None
    _HAS_RESHAPER = False
    _ImportError = _exc


def _build_reshaper(ligatures: bool) -> "object":
    """Build an ArabicReshaper with tashkeel preservation + caller-controlled ligatures.

    We always build our own rather than using `arabic_reshaper.reshape()`
    so we can override `delete_harakat`. The library default strips
    diacritics silently — we don't want that.

    Returns the reshaper object typed as `object` because arabic_reshaper
    ships no py.typed marker; we only call `.reshape(text)` on it.
    """
    from arabic_reshaper import ArabicReshaper  # noqa: F401  (only used at runtime)

    # `default_config` is dict[str, Any] at runtime; mypy sees it as
    # `Literal[...]` which doesn't accept dict(). Cast through Any.
    cfg = dict(_default_config)
    cfg["delete_harakat"] = False
    cfg["support_ligatures"] = ligatures
    return ArabicReshaper(configuration=cfg)


# Cache one reshaper per (ligatures True / False). Identity cache —
# reuse the same instance across calls so the library isn't rebuilt
# every shape() invocation.
_RESHAPERS: dict[bool, "object"] = {}


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
        The shaped string. Tashkeel (diacritics) is preserved. If
        `arabic-reshaper` is not installed, the input is returned
        unchanged.
    """
    if not text:
        return text
    if not _HAS_RESHAPER:
        return text  # graceful fallback: input passes through

    reshaper = _RESHAPERS.get(ligatures)
    if reshaper is None:
        reshaper = _build_reshaper(ligatures)
        _RESHAPERS[ligatures] = reshaper
    # `reshaper.reshape` is typed by arabic-reshaper as Any -> Any.
    # We promise the caller a str; assert at runtime via cast.
    out: str = reshaper.reshape(text)  # type: ignore[attr-defined]
    return out


__all__ = ["shape"]
