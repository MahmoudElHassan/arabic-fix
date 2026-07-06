# The global problem: Arabic text in modern systems

> 400M+ native speakers. 4th-most-used web language. <2% of the world's
> software was originally designed to display it. This is what's broken
> and why.

## TL;DR

Every Arabic string that flows through modern Western-built software
loses 0–3 of its 3 essential rendering properties:

1. **Letter shape** (isolated / initial / medial / final)
2. **Bidirectional order** (where to place digits & Latin inside)
3. **Tashkeel** (the vowel marks that disambiguate meaning)

When all three are lost, the same word can become three different
visual artifacts depending on where you render it. That's why Arabic
"just feels broken" in software, and why most AI assistants don't
even notice.

## Where it breaks

### Terminals, log files, chat UIs, CLIs

The most broken class of surfaces:

- macOS `Terminal.app` — no shaping
- iTerm2 — no shaping (without a font override)
- VSCode terminal — no shaping
- Jupyter notebooks — no shaping
- Slack/Discord — partially shaping, dropping when message is code-block
- Every shell command's stdout — every `--help` output — no shaping

Result: a developer types `print("مرحبا")` and the user sees:

```
ﻡﺮﺣﺒﺍ
```

This is the #1 reason Arabic developers feel their tools don't speak
their language.

### AI assistants

Even when an LLM is prompted in Arabic, the output is un-shaped because:

1. Tokenizers split on whitespace — but Arabic shaping is per-letter
2. Training data (mostly scraped web) is already un-shaped
3. There is no post-processing hook by default

This library provides one: a system prompt template
(`agents/system_prompt.md`) that teaches the assistant to call
`arabic_fix.fix()` on every output, plus eval cases
(`agents/eval_cases.md`) to verify.

### PDFs

`fpdf2`, `reportlab`, and many other PDF libraries render without
shaping unless you embed a proper Arabic font and pass the text
through a shaper.

### Web (HTML / CSS) — actually the one place that mostly works

The browser renders shaping automatically IF:

- The font supports Arabic (`Inter` alone is not enough)
- `dir="rtl"` is set on the document or container
- The CSS uses logical properties (`inline-start`, not `left`)
- Icons that imply direction are mirrored

This is covered in `designs/rtl-rules.md` + `designs/font-stack.md`.

### Databases

Same word in NFC vs NFD = different bytes = different hashes =
deduplication broken. `arabic_fix.normalize` defaults to NFC, which
matches the format every other tool uses.

## Why this has been broken for 30+ years

1. **English bias at design time.** Unicode's Arabic block (U+0600–06FF)
   was added in 1989, AFTER most software architectures that use it
   today were frozen.

2. **Shaping is per-font, not per-character.** A "perfect" Arabic
   rendering requires not just the codepoints but a font file with the
   OpenType GSUB shaping tables. Most fonts ship English-only.

3. **Right-to-left feels alien to LTR-trained engineers.** Cognitive
   friction leads to bugs that aren't caught until Arabic users file
   them.

4. **No one owns the round-trip.** A well-shaped string in the
   database may be re-encoded by a logging library, then post-processed
   by another pipeline, ending up un-shaped at the user's eye. Nobody
   inspects the chain.

5. **AI training pays the original sin forward.** Models learn from
   un-shaped scraped Arabic. They reproduce un-shaped output. They
   teach more agents to reproduce un-shaped output. The loop is
   self-reinforcing.

## What arabic-fix changes

| Touch point | What's fixed |
|---|---|
| Python code | `from arabic_fix import fix; fix(text)` — one call, three fixes |
| Command line | `arabic-fix file.txt` — rewrites any UTF-8 file |
| CI | `arabic-fix --check file.txt` — fails the build if Arabic isn't already correct |
| AI agents | Drop `agents/system_prompt.md` into the system prompt |
| Design | Inherit tokens from `designs/tokens.json`, follow `designs/rtl-rules.md` |
| Fonts | Use the stack in `designs/font-stack.md` |
| Eval | Run `agents/eval_cases.md` against your agent on every system-prompt change |

## A 30-day adoption plan

If you ship a product that touches Arabic users:

- **Day 1**: Replace fonts in your CSS with a stack from `font-stack.md`.
- **Day 1**: Add `dir="rtl"` to your Arabic-locale document root.
- **Day 7**: Add `arabic_fix.fix()` to every Python path that emits
  Arabic to a non-Web target.
- **Day 7**: Drop `system_prompt.md` into your AI assistant config.
- **Day 14**: Audit your design tokens — replace `left`/`right` with
  logical properties.
- **Day 21**: Add `--check` to your CI for any text file containing
  Arabic.
- **Day 30**: Run the full `eval_cases.md` against your AI agent and
  ship the fixes.

That's it. Most teams unlock 80% of the value in week 1.
