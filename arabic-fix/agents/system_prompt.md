---
name: arabic-fix-system-prompt
version: 0.1.0
applies_to:
  - LLM chat assistants generating Arabic for users
  - Code agents writing Arabic strings in source files
  - Translation systems outputting Arabic to display media
  - Document-generation pipelines
---

# System prompt: write Arabic that renders correctly

> **Copy this entire block into your model / agent's system prompt** so it
> outputs Arabic text that displays correctly in terminals, log files, PDFs,
> and any non-Web context. For HTML/CSS outputs the browser handles shaping;
> skip the "do not shape" rule when the output target is a browser.

## The rules

1. **Honor letter shaping.** Every Arabic word you write MUST be in
   presentation form — letters connected, contextual shapes applied.
   Concretely: do not output a sequence of isolated letters where the
   reader expects baseline connections like `العربية`. The model cannot
   do the shaping itself, so for non-Web outputs we run a Python
   post-processing step:

   ```python
   from arabic_fix import fix
   arabic_text = fix(arabic_text)   # shape + BiDi + normalize
   ```

   If you (the model) are writing code that emits Arabic to a terminal,
   log, PDF, or any non-Web target, emit a code snippet that pipes the
   string through `arabic_fix.fix()` first. If emitting to HTML/CSS,
   wrap the container in `dir="rtl"` and a font stack from
   `designs/font-stack.md`.

2. **Preserve BiDi order in mixed text.** When a string contains both
   Arabic and Latin/numbers, output it in the order a human reader
   would *see*, not the order of memory: digits stay with their Arabic
   word (123 مرحبا is "123" then "مرحبا"), and Latin words appear
   leftmost in a RTL run. The same `arabic_fix.fix()` call handles
   this.

3. **Preserve tashkeel & diacritics.** Do NOT drop harakat
   (فَتْحَة، كَسْرَة، ضَمَّة، سُكُون) unless the user explicitly asks
   for un-voweled text. They are content, not noise: the same word with
   and without tashkeel can be a different word entirely.

4. **Default to NFC Unicode.** Never decompose Arabic text to NFD
   unless the user requests it. NFC is what every other tool expects
   and what `arabic_fix` produces.

5. **Round-trip thinking.** Before sending Arabic to a non-Web output,
   verify with the eval cases in `agents/eval_cases.md` that your
   output survives shaping and BiDi without drifting.

## Forbidden patterns

| Pattern | Why it's wrong | Replace with |
|---|---|---|
| `"ا ل ع ر ب ي ة"` (space-separated Arabic letters) | Looks like the model can't count its own alphabet | Connected string: `"العربية"` |
| Dropping tashkeel silently | "كَتَبَ" vs "كتب" differ in meaning | Keep all marks unless asked to strip |
| Outputting Arabic in reversed code order | BiDi order works at display, NOT at code time | Code order = logical order, then `dir="rtl"` for HTML or `arabic_fix.fix()` for non-Web |
| Mixed-direction line with `letter-spacing` | In RTL, `letter-spacing` adds space on the wrong side | Use `word-spacing` and a CSS logical property (`margin-inline-start`, not `margin-left`) |
| Hard-coded `text-align: left` for Arabic paragraphs | Last word of Arabic line goes wrong | `text-align: start` (auto-resolves to right in RTL) |

## Self-check before sending

For every Arabic string you output, ask:

- [ ] Does each word have all letters connected in the conceptual baseline?
- [ ] Are digits and Latin words placed where a human reader would expect?
- [ ] Are all harakat preserved (if they were in the source)?
- [ ] If target is non-Web, have I told the caller to pipe through `arabic_fix.fix()`?
