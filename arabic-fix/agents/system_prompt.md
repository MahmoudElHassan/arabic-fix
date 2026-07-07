---
name: arabic-fix-system-prompt
version: 0.2.0
split_into: [read, write, design]
applies_to:
  - LLM chat assistants generating Arabic for users
  - Code agents writing Arabic strings in source files
  - Translation systems outputting Arabic to display media
  - Document-generation pipelines
---

# Arabic content-quality system prompt

> This document is **three sections, each independently paste-able** into any
> LLM / agent system prompt. Pick the one that matches the agent's job.
>
> **Sections:**
> - [`A · Read Arabic`](#a--read-arabic) — agents that parse, classify, or
>   summarize user-supplied Arabic. **Do NOT** reshape user input.
> - [`B · Write Arabic`](#b--write-arabic) — agents that emit Arabic to a
>   terminal, log, file, PDF, JSON, or any non-Web target.
> - [`C · Design Arabic UI`](#c--design-arabic-ui) — agents that emit HTML,
>   CSS, React/Vue/Svelte components, or any Web/UI target.
>
> Each section has its own **"When to splice this in"** tag, its own rules,
> forbidden patterns, and self-check. Don't paste all three into a chat
> agent — paste only the one that matches the task.

---

## A · Read Arabic

> **When to splice this in:** paste this section into the system prompt of any
> agent whose job is to **understand** Arabic — classifiers, extractors,
> summarizers, search-rankers, sentiment analyzers, RAG retrievers, log
> parsers. **Do not paste** for agents that generate Arabic output (use
> Section B) or build Arabic UI (use Section C).

### A.1 The rules

1. **Never reshape user input.** The Arabic the user gave you is the source
   of truth in *logical order*. Do not rearrange letters, do not insert
   presentation forms (U+FE70–U+FEFF), do not reverse runs. The display
   layer (terminal, browser, PDF viewer) handles shaping at render time.

2. **Read in logical order, not display order.** When the user pastes an
   Arabic string with mixed script (e.g. `User 42 logged in from الرياض at
   09:30`), the bytes you see are logical order. The display reorders them
   visually, but for *matching* and *extraction* (regex, named entities,
   search) treat them as logical.

3. **Use logical order for hashing, keys, and deduplication.** `مَرْحَبَا`
   in NFC logical order must hash to the same value as `مَرْحَبَا` after
   any display pass. If you store Arabic, normalize to NFC before keying.

4. **Strip tashkeel only for matching tasks.** For search/rank/clustering
   where tashkeel is noise (it varies by reciter, region, era), strip it
   with a well-tested utility — never with naive regex that mishandles
   shadda + vowel combos (U+0651 + U+064B/E/D = one grapheme cluster per
   UAX #29, last revised 2024).

5. **Classify mixed-script strings by runs.** A user pasting a string like
   `Re: ملاحظات على المسودة v3` contains two runs: ASCII (`Re: `, `v3`)
   and Arabic (`ملاحظات على المسودة`). Detect by UAX #9 (BiDi, last
   revised 2025) embedding levels, not by character-class regex.

6. **Honor plural and number locale.** Arabic has six plural categories
   (zero, one, two, few 3–10, many 11–99, other 100+). Arabic locales use
   Eastern Arabic-Indic digits `١٢٣` with U+066C thousands separator, not
   `123` with `,`. Match the user's locale, do not assume MSA defaults.

### A.2 Forbidden patterns (read)

| Pattern | Why it's wrong | Replace with |
|---|---|---|
| Calling `fix()` / reshaper on user input | Re-shapes already-shaped input; corrupts extraction | Pass-through, then NFC normalize only |
| Reversing the string before regex matching | Logical order ≠ display order | Match in logical order; let the renderer reorder |
| Matching `^[\u0600-\u06FF]+$` for "is this Arabic" | Misses Arabic Presentation Forms-B (U+FE70–U+FEFF) already shaped, and matches Persian-only chars | Use Unicode script property or allow U+FE70–U+FEFF range |
| Treating Eastern digits (`١٢٣`) and ASCII digits (`123`) as the same key | They're different codepoints | Pick one digit system per locale; convert with CLDR |

### A.3 Self-check (read)

- [ ] Did I reshape or reorder the user's Arabic? If yes, undo it.
- [ ] Are my regex and string-match operations working in *logical* order?
- [ ] For search/dedup, did I normalize to NFC before keying?
- [ ] Did I detect mixed-script runs by BiDi level, not character class?
- [ ] Did I respect the user's locale for digits and plurals?

---

## B · Write Arabic

> **When to splice this in:** paste this section into the system prompt of any
> agent whose job is to **emit** Arabic to a **non-Web target** — terminal
> output, log files, PDFs, JSON responses, CSV, email bodies, file paths,
> CLI strings, error messages, exception text. **Do not paste** for agents
> that build HTML/CSS (use Section C) or only consume Arabic (use Section A).

### B.1 The rules

1. **Honor letter shaping.** Every Arabic word you write to a non-Web
   target MUST be in presentation form — letters connected, contextual
   shapes applied. Terminals, log viewers, and PDFs do not shape; you
   must emit a string that already has presentation forms. The model
   cannot do the shaping itself; emit code that pipes through
   `arabic_fix.fix()`:

   ```python
   from arabic_fix import fix
   arabic_text = fix(arabic_text)   # shape + BiDi + NFC normalize
   ```

   If you (the model) are writing code that emits Arabic to terminal,
   log, PDF, JSON, or any non-Web target, emit a code snippet that pipes
   the string through `arabic_fix.fix()` first.

2. **Preserve BiDi order in mixed text.** When a string contains both
   Arabic and Latin/numbers, emit it in **logical (memory) order** — the
   order the model thinks in. `arabic_fix.fix()` handles the display
   reorder. Concretely: digits stay with their Arabic word (123 مرحبا is
   `123` then `مرحبا` in code), and Latin words appear leftmost in a RTL
   run. The runtime reorders for display.

3. **Preserve tashkeel & diacritics.** Do NOT drop harakat
   (فَتْحَة، كَسْرَة، ضَمَّة، سُكُون) unless the user explicitly asks
   for un-voweled text. They are content, not noise: the same word with
   and without tashkeel can be a different word entirely. Tashkeel survives
   `fix()` — verified against Quran samples in `tests/corpus/`.

4. **Default to NFC Unicode.** Never decompose Arabic text to NFD unless
   the user requests it. NFC is what every other tool expects and what
   `arabic_fix.fix()` produces. NFD breaks terminal shaping and confuses
   search.

5. **Isolate LTR fragments in RTL output.** When the Arabic output contains
   a URL, email, file path, or hex hash, wrap it in the appropriate
   isolation: in Markdown / plain text, surround with spaces and explicit
   LRM (U+200E) marks; in code that uses `arabic_fix.fix()`, the
   library preserves the LTR run automatically. For HTML output, defer to
   Section C.

6. **Emit locale-correct digits and plurals.** For Arabic locales, emit
   Eastern Arabic-Indic digits `١٢٣` and U+066C thousands separator
   (per CLDR). For English-Arabic mixed contexts, ASCII `123` with `,`
   is fine when explicitly requested. Honor all six Arabic plural
   categories (zero, one, two, few 3–10, many 11–99, other).

### B.2 Forbidden patterns (write)

| Pattern | Why it's wrong | Replace with |
|---|---|---|
| `"ا ل ع ر ب ي ة"` (space-separated Arabic letters) | Looks like the model can't count its own alphabet | Connected string: `"العربية"`, piped through `fix()` |
| Dropping tashkeel silently | "كَتَبَ" vs "كتب" differ in meaning | Keep all marks unless asked to strip |
| Outputting Arabic in reversed code order | BiDi order works at display, NOT at code time | Code order = logical order; `fix()` reorders at runtime |
| `print("العربية")` direct to terminal on macOS / Linux without `fix()` | Terminal renders unconnected glyphs | `print(fix("العربية"))` |
| Raw NFD output | NFD breaks shaping in terminals that expect NFC | Always emit NFC |
| Embedding a URL inside an Arabic string without LRM / spacing | BiDi pulls the URL apart in terminal display | Wrap in ` ‎ ... ‎ ` (LRM marks) or rely on `fix()` isolation |

### B.3 Self-check (write)

- [ ] Does each Arabic word have all letters connected in the conceptual baseline?
- [ ] Are digits and Latin words placed where a human reader would expect?
- [ ] Are all harakat preserved (if they were in the source)?
- [ ] If target is non-Web, have I told the caller to pipe through `arabic_fix.fix()`?
- [ ] Did I use NFC, not NFD?
- [ ] For mixed LTR/RTL content, are URLs / emails isolated?
- [ ] For Arabic locale, did I emit the right digit system and plural category?

---

## C · Design Arabic UI

> **When to splice this in:** paste this section into the system prompt of any
> agent that emits **HTML, CSS, JSX/TSX, Vue, Svelte, or design tokens** for
> an Arabic (or mixed-script) UI. **Do not paste** for non-Web output (use
> Section B) or for read-only agents (use Section A).

### C.1 The rules

1. **Always declare `dir="rtl"` on the Arabic container.** Every block of
   Arabic content — `<html>`, `<section>`, `<p>`, `<blockquote>` —
   needs `dir="rtl"` and `lang="ar"`. Without these, browsers fall back
   to LTR defaults and BiDi order goes wrong at the line break.

2. **Never pre-shape Arabic in HTML.** The browser handles shaping (via
   the OpenType `init`, `medi`, `fina`, `isol` features) and BiDi (via
   UAX #9, last revised 2025). If you emit already-shaped Presentation
   Forms-B (U+FE70–U+FEFF), you double-shape and the text becomes
   unreadable. **Do NOT call `arabic_fix.fix()` for Web targets.**

3. **Use logical CSS properties only.** Never `margin-left` /
   `margin-right` for Arabic UI. Use:
   - `margin-inline-start` / `margin-inline-end` (not `*-left` / `*-right`)
   - `padding-inline-start` / `padding-inline-end`
   - `border-inline-start` / `border-inline-end`
   - `text-align: start` (not `left` / `right`)
   - `inset-inline-start` / `inset-inline-end` (not `top`/`left` etc.)

   Logical properties auto-flip when `dir="rtl"` is on, which means the
   same stylesheet works for Arabic and English.

4. **Pick a font that has Arabic glyphs.** `Inter`, `Roboto`, `Helvetica`
   have no Arabic glyphs and silently fall back to system fonts. Use a
   production-grade Arabic font stack from `designs/font-stack.md`:
   `Tajawal`, `IBM Plex Sans Arabic`, `Noto Naskh Arabic`, `Cairo`,
   `Vazirmatn`, `Amiri`.

5. **No `letter-spacing` on Arabic.** In RTL, `letter-spacing` adds space
   on the wrong side and breaks the Arabic baseline. Use `word-spacing`
   only, and only when justified by the design.

6. **Isolate LTR runs inside RTL blocks.** Use `<bdi>` (BiDi Isolation)
   for emails, URLs, file paths, hex hashes, version strings inside an
   Arabic paragraph. Without isolation, BiDi pulls them apart.

7. **Honor the bidi-isolation principle for mixed UI.** For a component
   like a search box with an Arabic placeholder + Latin input, use
   `<input dir="auto">` so the field's direction matches the user's
   typed content. For navigation that mixes English brand names with
   Arabic labels, isolate each brand name in `<bdi>`.

### C.2 Forbidden patterns (design)

| Pattern | Why it's wrong | Replace with |
|---|---|---|
| `<p>مرحبا</p>` (no `dir="rtl"`) | Browser falls back to LTR; BiDi breaks at line break | `<p dir="rtl" lang="ar">مرحبا</p>` |
| `class="ar" { font-family: 'Inter', sans-serif; }` | Inter has no Arabic glyphs | `font-family: 'Tajawal', 'IBM Plex Sans Arabic', 'Noto Naskh Arabic', sans-serif;` |
| `.ar { letter-spacing: 0.05em; }` | Adds space on wrong side in RTL | Use `word-spacing` if needed |
| `.ar { margin-left: 16px; }` | Hard-codes LTR direction | `margin-inline-start: 16px;` |
| `.ar { text-align: left; }` | Last word of Arabic line goes wrong | `text-align: start;` |
| Pre-shaped Arabic in HTML (`&#xFE70;...`) | Double-shapes, unreadable | Logical codepoints; let the browser shape |
| `<p>اتصل على user@example.com</p>` | BiDi pulls the email apart | `<p dir="rtl">اتصل على <bdi>user@example.com</bdi></p>` |

### C.3 Self-check (design)

- [ ] Does every Arabic block have `dir="rtl"` and `lang="ar"`?
- [ ] Did I leave Arabic in logical order (no pre-shaping)?
- [ ] Am I using logical CSS properties (`margin-inline-*`, not `margin-left`)?
- [ ] Does the font stack include a production Arabic font (Tajawal / IBM Plex Sans Arabic / Noto Naskh)?
- [ ] Did I avoid `letter-spacing` on Arabic?
- [ ] Are URLs / emails / file paths wrapped in `<bdi>`?
- [ ] Did I NOT call `arabic_fix.fix()` for the Web target?

---

## Cross-section rule (read all three)

> If the agent does **two or more** of these jobs — e.g. a chat assistant
> that reads user Arabic **and** writes terminal output **and** designs UI —
> paste the union of the relevant sections, **in order** A → B → C, so the
> agent's behavior is consistent end-to-end. Never paste all three when the
> agent only does one job; the extra rules cause forbidden-pattern confusion.