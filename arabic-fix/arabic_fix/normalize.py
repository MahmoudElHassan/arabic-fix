"""Unicode normalization helpers.

NFC vs NFD drift is a common source of "same text, different bytes" bugs
across macOS / Windows / Linux systems handling Arabic — especially with
tashkeel (combining marks for fatḥa, kasra, ḍamma).

Default to NFC (composed) for interchange: smaller byte size, more
predictable hashing, fully compatible with the rest of the library.
"""

from __future__ import annotations

import unicodedata
from typing import Literal


def normalize(text: str, form: str = "NFC") -> str:
    """Return text in the requested Unicode normalization form.

    Parameters
    ----------
    text:
        Any string.
    form:
        One of 'NFC' (default), 'NFD', 'NFKC', 'NFKD'.

    Returns
    -------
    str
        Normalized string. Empty input returns empty.
    """
    if not text:
        return text
    form = form.upper()
    if form not in {"NFC", "NFD", "NFKC", "NFKD"}:
        raise ValueError(f"unknown normalization form: {form!r}")
    # unicodedata.normalize wants a Literal[...] for the form arg;
    # we've validated it above, so the cast is safe.
    return unicodedata.normalize(form, text)  # type: ignore[arg-type]


NormForm = Literal["NFC", "NFD", "NFKC", "NFKD"]


def contains_arabic(text: str) -> bool:
    """Return True if `text` contains any Arabic-block codepoint."""
    for ch in text:
        cp = ord(ch)
        # Arabic block U+0600–U+06FF
        # Arabic Supplement U+0750–U+077F
        # Arabic Extended-A U+08A0–U+08FF
        # Arabic Presentation Forms-A U+FB50–U+FDFF
        # Arabic Presentation Forms-B U+FE70–U+FEFF
        if (
            0x0600 <= cp <= 0x06FF
            or 0x0750 <= cp <= 0x077F
            or 0x08A0 <= cp <= 0x08FF
            or 0xFB50 <= cp <= 0xFDFF
            or 0xFE70 <= cp <= 0xFEFF
        ):
            return True
    return False


def has_tashkeel(text: str) -> bool:
    """Return True if text contains any Arabic combining mark (tashkeel)."""
    tashkeel_ranges = (
        (0x064B, 0x065F),   # tanween, harakat, hamza-here
        (0x0670, 0x0670),   # alef khanjariya (superscript alef)
        (0x06D6, 0x06DC),   # Quranic marks
        (0x06DF, 0x06E4),
        (0x06E7, 0x06E8),
        (0x06EA, 0x06ED),
    )
    for ch in text:
        cp = ord(ch)
        for lo, hi in tashkeel_ranges:
            if lo <= cp <= hi:
                return True
    return False


__all__ = ["normalize", "contains_arabic", "has_tashkeel"]
