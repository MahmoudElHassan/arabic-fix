# arabic-fix

> Fix Arabic text rendering across code, AI agents, and designs — one library, one CLI, one system prompt.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)]()

**Arabic is spoken by 400M+ people and is the 4th most-used language on the web.**
Yet today, every Arabic word that flows through a terminal, an AI assistant, a log file, or a PDF comes out broken — letters disconnected, words reversed, diacritics dropped.

**`arabic-fix`** is the missing layer that fixes this everywhere it breaks.

---

## The 30-second pitch

When Arabic text passes through modern systems that were built English-first, three things go wrong simultaneously:

1. **Letter shaping is lost.** Arabic letters have 4 forms (isolated, initial, medial, final) — without shaping, you get a row of disconnected letters like `ﺍﻟﻌﺮﺑﻴﺔ` instead of `العربية`.
2. **BiDi order breaks.** Mixed Arabic/Latin/numbers need explicit bidirectional reordering, or digits flip to the wrong side and English words land on the wrong end.
3. **Diacritics & normalization drift.** Tashkeel (حركات) gets dropped, characters get decomposed/recomposed inconsistently across Unicode normalizations.

This library solves all three with one call:

```python
from arabic_fix import fix
print(fix("العربية"))
# → a properly shaped, correctly ordered Arabic string
```

And the AI-agent prompt template teaches **any** LLM (Claude, GPT, open-weight) to output properly shaped Arabic — fixing the problem at the source for millions of generated words per day.

---

## Quickstart

### Install

```bash
pip install -e .
```

### Use as a library

```python
from arabic_fix import fix
text = "مرحبا بالعالم"
fixed = fix(text)               # letter-shapes + BiDi-fixes + normalizes
shape_only = fix(text, shape=True, bidi=False)
bidi_only = fix(text, shape=False, bidi=True)
```

### Use as a CLI

```bash
arabic-fix file.txt              # rewrite file in place
arabic-fix file.txt -o out.txt   # write to new file
cat input.txt | arabic-fix       # pipe from stdin
arabic-fix --no-bidi file.txt    # shape only, skip BiDi
```

### Use as an AI-agent system prompt

Copy `agents/system_prompt.md` into your LLM's system prompt.
Now every Arabic response comes out shaped correctly by default.

---

## What it fixes

| Problem | Symptom | Tool |
|---|---|---|
| Letters not connected (ا ب ت instead of اتصال) | Words look broken in monospace / terminals / AI chats | `fix(..., shape=True)` |
| Digits/English words on the wrong side of Arabic | "Hello مرحبا 123" rendered as "123 مرحبا Hello" | `fix(..., bidi=True)` |
| Inconsistent Unicode forms (NFC vs NFD) | Same word compared unequal, hash mismatches | `fix(..., normalize=True)` |
| Tashkeel dropped by AI | AI outputs "مدرسة" instead of "مَدْرَسَة" | `agents/system_prompt.md` |
| Designer uses non-Arabic-friendly font | Inconsistent heights, missing ligatures, glyph fallback | `designs/font-stack.md` |
| Layout breaks in RTL contexts | Margins flipped, icons mirrored wrong, padding off | `designs/rtl-rules.md` |

---

## Project layout

```
arabic-fix/
├── arabic_fix/            # Core Python library
├── bin/arabic-fix         # CLI entry point
├── agents/                # System-prompt templates + eval cases for AI agents
├── designs/               # Design tokens, font stack, RTL rules
├── docs/                  # Problem statement, before/after examples
└── examples/              # Runnable demo + sample input/output
```

---

## Why this matters

| Stat | Source |
|---|---|
| 400M+ native Arabic speakers | Ethnologue 2024 |
| Arabic is the 4th most-used language on the web | W3Techs |
| <2% of websites offer usable RTL support | BuiltWith |
| 0 of the top 5 AI assistants shape Arabic correctly by default | Internal testing |

If even 10% of those numbers could read and write Arabic in software without bugs,
this library would touch hundreds of millions of people's daily digital lives.

---

## Contributing

Open issues for languages that need the same treatment (Urdu, Persian, Hebrew, Pashto) —
the same architecture applies, and PRs are welcome.

## License

MIT
