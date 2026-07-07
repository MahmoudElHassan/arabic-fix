# arabic-fix

> Fix Arabic text rendering across code, AI agents, and designs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-169%20passing-brightgreen)]()

**One library, one CLI, one system prompt.** Letter-shaping, BiDi reordering,
Unicode normalization, and a 3-section prompt template for any LLM. Arabic
flows through terminals, AI agents, log files, and PDFs the way it should.

```bash
pip install arabic-fix
```

```python
from arabic_fix import fix
print(fix("User 42 من الرياض at 09:30"))
# → a properly shaped, correctly ordered, NFC-normalized string
```

```bash
# CLI
cat arabic.txt | arabic-fix
arabic-fix --check file.txt          # CI mode: exit non-zero if changes needed
```

```text
# AI agent: paste one of the 3 sections from agents/system_prompt.md
#   A · Read Arabic    — for agents that parse / summarize / classify
#   B · Write Arabic   — for agents that emit to terminal / log / email
#   C · Design Arabic  — for HTML / CSS / Tailwind / design tokens
```

## Why

- **Letter shaping** — `ا ب ت` (isolated forms) become `اتصال` (connected) via
  Unicode Presentation Forms-B.
- **BiDi order** — `User 42 من الرياض` ends up with `42` on the visual left
  and Arabic letters in their connected form, per UAX #9.
- **Tashkeel preserved** — diacritics survive; `مَرْحَبًا` round-trips intact.
- **Logical CSS only** — `margin-inline-start`, never `margin-left`.
- **Real Arabic fonts** — Tajawal, IBM Plex Sans Arabic, Noto Naskh Arabic
  in priority order; never Inter or Roboto.

## What's in the box

| Path | What it is |
|---|---|
| `arabic_fix/` | Python library: `fix()`, `shape()`, `reorder()`, `normalize()` |
| `agents/system_prompt.md` | 3 splice-in-able sections for any LLM |
| `agents/eval_cases.md` | 15 cases to verify the system prompt works |
| `designs/tokens.json` | 73 design tokens (W3C DTCG), CSS / Tailwind / Figma exports |
| `examples/sample-arabic-page.html` | 5 Arabic surfaces using the tokens |
| `docs/roadmap.md` | v0.2 → v0.6 milestones |

## Verify

```bash
pytest -q                          # 169 tests
mypy arabic_fix                    # strict, clean
python designs/validate_tokens.py  # 73 token schema check
```

## License

MIT — see [LICENSE](LICENSE). The brand `arabic-fix` is locked until v1.0.
