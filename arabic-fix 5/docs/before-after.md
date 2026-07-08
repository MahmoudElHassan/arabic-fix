# Before vs After — the whole reason this library exists

> Same byte stream, two different renders. The "before" column is what
> your terminal / AI / log file / PDF produces today. The "after"
> column is what a human expects.

## 1. Terminal

| Before | After |
|---|---|
| `User 42 logged in from الرياض at 09:30 today` arrives as connected glyphs but digits on the wrong side, English on the left, Arabic mushed | `User 42 logged in from الرياض at 09:30 today` — BiDi-reordered, shaped, every word in the right reading order |

## 2. AI assistant output

| Before | After |
|---|---|
| Same shape across all outputs because no shaping step is in the path | Each Arabic word shaped, diacritics preserved, digits anchored to their Arabic word |

## 3. Log line

| Before | After |
|---|---|
| `[2024-01-01 09:30] user محمد logged in from الرياض` — readable but visually unbalanced, Latin/Arabic mixed awkwardly on first read | Same bytes, normalized to NFC, shaped for any tail/viewer that does not auto-shape |

## 4. PDF / reportlab / fpdf2

| Before | After |
|---|---|
| Embeds an Arabic font that lacks shaping tables → terminal-like disconnected output | `fix(text)` applied before `pdf.drawString` |

## 5. Database equality

| Before | After |
|---|---|
| `"كتب"` in NFD ≠ `"كتب"` in NFC → SQL `WHERE name = ?` misses rows | `normalize(text, "NFC")` defaults applied before insert & query |

## 6. Diacritics survival

| Input | Before (raw LLM output) | After (with system prompt) |
|---|---|---|
| "I wrote the book" | `كتبت الكتاب` (ambiguous: كتبت or كُتبت?) | `كَتَبْتُ الْكِتَابَ` (unambiguous) |

---

## Try it yourself

```bash
pip install -e .
python examples/demo.py
```

You should see a table with each case, the `input` and `output` reprs,
and which of the three fixes (`SHAPE` / `BIDI` / `NORM`) actually
fired. The output is itself a before/after comparison, generated live
every run.
