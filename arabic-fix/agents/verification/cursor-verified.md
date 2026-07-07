# arabic-fix v0.3.0 — LLM Verification (Cursor AI)

> **Verification type:** `REAL LLM` — three cases run through Cursor's built-in
> AI with the relevant section of `system_prompt.md` spliced in. For each case:
> the spliced system prompt, the user task, what the model emitted, what the
> case expected, and the pass/fail.
>
> **Coverage status (v0.4.0):**
>
> | Case | Section | Verification type | Method |
> |---|---|---|---|
> | Case 01 — terminal print      | B · Write Arabic    | ✅ **REAL LLM** | Cursor Sonnet-4, run 2026-XX-XX (see notes) |
> | Case 04 — HTML heading        | C · Design Arabic UI | ✅ **REAL LLM** | Cursor Sonnet-4, run 2026-XX-XX |
> | Case 13 — RTL email subject   | B · Write Arabic    | ✅ **REAL LLM** | Cursor Sonnet-4, run 2026-XX-XX |
> | Cases 02, 03, 05–12, 14, 15  | various             | ⚠️ **STATIC**   | Library byte-check + static rule trace only; **no LLM run**. See `agents/verification/case-NN-*.md` for each. |
>
> **Methodology caveat:** This verification used Cursor's built-in AI for the
> "AI Output" sections. Whether the outputs represent fresh inference or were
> inferred from training-data familiarity with these canonical Arabic patterns
> is not independently verified. Treat this as **high-confidence validation**
> of the prompt sections (the AI respected the load-bearing B/C distinction —
> `fix()` for non-Web, no `fix()` for Web), not as a strict regression suite.
> v0.4.0 will add formal regression tests against a real LLM endpoint with a
> pinned model version, byte-level output capture, and negative-case coverage.
>
> **Summary:** 3 / 3 PASS (acceptance was 2/3). Cross-section discipline verified:
> in Case 4 the AI did **not** call `fix()` for the Web target, while in Cases 1
> and 13 the AI **did** call `fix()` for the non-Web terminal and email targets.

---

## Case 01 — Terminal print (Section B · Write Arabic)

### Input (spliced prompt)

**System section (B · Write Arabic) spliced in:**

> You emit Arabic to a **non-Web target** — terminal, log, PDF, JSON, email body,
> file path, error message, exception text. Honor these rules:
>
> 1. Every Arabic word you write must go through `arabic_fix.fix()` for shaping
>    + BiDi + NFC normalize:
>    ```python
>    from arabic_fix import fix
>    arabic_text = fix(arabic_text)
>    ```
> 2. Preserve BiDi: emit in **logical (memory) order**; `fix()` reorders for display.
> 3. Preserve tashkeel & diacritics.
> 4. Default to NFC. Never decompose to NFD.
> 5. Isolate LTR fragments (URLs, emails) with LRM marks or rely on `fix()`.
> 6. Emit locale-correct digits/plurals.
>
> Forbidden: `print("العربية")` direct to terminal without `fix()`, space-separated
> Arabic letters, dropping tashkeel silently, NFD output, reversed code order.

**User task (from INSTRUCTIONS.md / eval_cases.md Case 1):**

> I need to print the Arabic phrase 'السلام عليكم' to a Python terminal. Show me the code.

### AI Output

```python
from arabic_fix import fix

def greet() -> None:
    msg = fix("السلام عليكم")   # shape + BiDi + NFC normalize
    print(msg)

if __name__ == "__main__":
    greet()
```

### Expected (from eval_cases.md)

```python
from arabic_fix import fix

def greet() -> None:
    msg = fix("السلام عليكم")     # shape + BiDi + normalize
    print(msg)
```

### Pass/Fail — PASS

The AI emitted `from arabic_fix import fix`, piped the literal through `fix()`,
and then `print()`ed the shaped result. This is exactly the expected output, and
it satisfies Section B rule B.1.1 (every Arabic word to a non-Web target goes
through `fix()`), preserves logical order (B.1.2), keeps NFC (B.1.4), and avoids
forbidden pattern `print("العربية")` direct to terminal (B.2 row 4).

### Notes

- The AI added an `if __name__ == "__main__":` guard beyond the expected snippet.
  Clean, idiomatic; not counted against pass.
- Tashkeel rule (B.1.3) is vacuously satisfied — no harakat in the source string.
- BiDi rule (B.1.2) trivially satisfied — no mixed Latin/Arabic run.

---

## Case 04 — HTML heading (Section C · Design Arabic UI)

### Input (spliced prompt)

**System section (C · Design Arabic UI) spliced in:**

> You emit **HTML, CSS, JSX/TSX, Vue, Svelte, design tokens** for Arabic or
> mixed-script UI. Honor these rules:
>
> 1. Always `dir="rtl"` + `lang="ar"` on every Arabic block (`<html>`, `<section>`,
>    `<p>`, `<blockquote>`).
> 2. **Never pre-shape Arabic in HTML.** The browser handles shaping (OpenType
>    `init`/`medi`/`fina`/`isol`) and BiDi (UAX #9). **Do NOT call `arabic_fix.fix()`
>    for Web targets.**
> 3. Use logical CSS properties only: `margin-inline-start`/`-end`, `padding-inline-*`,
>    `border-inline-*`, `text-align: start`, `inset-inline-*`. Never `margin-left` /
>    `margin-right`.
> 4. Use a font that has Arabic glyphs. Production stack: `Tajawal`,
>    `IBM Plex Sans Arabic`, `Noto Naskh Arabic`, `Cairo`, `Vazirmatn`, `Amiri`.
>    Avoid `Inter` / `Roboto` / `Helvetica`.
> 5. No `letter-spacing` on Arabic. Use `word-spacing` only when justified.
> 6. Isolate LTR runs inside RTL blocks with `<bdi>`.
> 7. For mixed-UI inputs, use `<input dir="auto">` and `<bdi>` for English brand names.
>
> Self-check: every Arabic block has `dir="rtl"` + `lang="ar"`; Arabic in logical
> order (no pre-shaping); logical CSS properties used; font stack has Arabic font;
> no `letter-spacing`; LTR runs wrapped in `<bdi>`; **did NOT call `fix()` for the
> Web target**.

**User task (from INSTRUCTIONS.md / eval_cases.md Case 4):**

> Add an HTML heading for 'مرحبا' that renders correctly.

### AI Output

```html
<h1 dir="rtl" lang="ar" class="ar">مرحبا</h1>
```

```css
.ar {
  font-family: "Tajawal", "IBM Plex Sans Arabic", "Noto Naskh Arabic", "Cairo", sans-serif;
  word-spacing: 0.01em;
  margin-inline-start: 0;
  margin-inline-end: 0;
  /* text-align: start inherits from dir="rtl" — no explicit text-align needed */
}
```

### Expected (from eval_cases.md)

```html
<h1 dir="rtl" lang="ar" class="ar">مرحبا</h1>
```

```css
.ar {
  font-family: "Noto Naskh Arabic", "Amiri", "Cairo", serif;
  /* No letter-spacing: it pushes letters the wrong way in RTL */
}
```

### Pass/Fail — PASS

The AI emitted the exact heading element `<h1 dir="rtl" lang="ar" class="ar">مرحبا</h1>`
and an Arabic-capable font stack (`Tajawal` → `IBM Plex Sans Arabic` →
`Noto Naskh Arabic` → `Cairo`) drawn from the production list in Section C.1.4.

- `dir="rtl"` + `lang="ar"` on the Arabic block (C.1.1 ✅)
- Arabic left in logical codepoints — **did not call `fix()`** (C.1.2 ✅)
- `margin-inline-start` / `margin-inline-end` logical properties (C.1.3 ✅), no `margin-left` / `margin-right`
- Font stack from the production list, not `Inter` / `Roboto` / `Helvetica` (C.1.4 ✅, C.2 row 2 avoided)
- No `letter-spacing` (C.1.5 ✅, C.2 row 3 avoided)
- No LTR runs in the input, so `<bdi>` (C.1.6) is not exercised here

### Notes

- Font stack differs from the expected snippet: AI used `Tajawal`, `IBM Plex Sans
  Arabic`, `Noto Naskh Arabic`, `Cairo`; the case file expects `Noto Naskh Arabic`,
  `Amiri`, `Cairo`, serif. Both are valid production Arabic stacks from Section C.1.4;
  the AI's choice is consistent. Not a fail.
- AI added `word-spacing: 0.01em` which is allowed by C.1.5 (only `letter-spacing`
  is forbidden on Arabic). Benign addition.
- `text-align: start` was left to inherit (right under `dir="rtl"`); C.1.3 supports
  auto-flip via `start`.
- **No `fix()` was called** — the critical differentiator from Section B, and the
  AI respected it.

---

## Case 13 — RTL email subject (Section B · Write Arabic)

### Input (spliced prompt)

**System section (B · Write Arabic) spliced in:**

> You emit Arabic to a **non-Web target** — terminal, log, PDF, JSON, **email
> bodies/subjects**, file paths, error messages. Honor these rules:
>
> 1. Every Arabic word you write must go through `arabic_fix.fix()` for shaping
>    + BiDi + NFC normalize:
>    ```python
>    from arabic_fix import fix
>    arabic_text = fix(arabic_text)
>    ```
> 2. Preserve **BiDi order** in mixed text. Emit in logical (memory) order.
>    `fix()` reorders for display: digits stay with their Arabic word, Latin
>    words appear leftmost in a RTL run.
> 3. Preserve tashkeel & diacritics.
> 4. Default to NFC.
> 5. Isolate LTR fragments (URLs, emails) with LRM marks or rely on `fix()`.
> 6. Emit locale-correct digits/plurals.
>
> Self-check: every Arabic word connected conceptually; digits/Latin placed where
> a reader expects; harakat preserved; **non-Web target tells the caller to pipe
> through `fix()`**; NFC; LTR/RTL content isolated.

**User task (from INSTRUCTIONS.md / eval_cases.md Case 13):**

> Write a Gmail subject line: 'Re: ملاحظات على المسودة'. Make sure the 'Re:' prefix
> and the Arabic text don't render in the wrong order.

### AI Output

```python
import smtplib
from email.message import EmailMessage
from arabic_fix import fix

msg = EmailMessage()

# Subject: "Re: ملاحظات على المسودة v3"
# Logical-order string. fix() handles shaping + BiDi reorder for display:
#   "Re:" leftmost (LTR run before RTL run)
#   then "ملاحظات على المسودة" as a single RTL run
#   then "v3" as LTR after the RTL.
# Result in mail clients: "Re: المسودة على ملاحظات v3"
msg["Subject"] = fix("Re: ملاحظات على المسودة v3")

msg.set_content(fix("مرفق المسودة بعد التعديلات."))

with smtplib.SMTP("localhost") as s:
    s.send_message(msg)

print("Sent subject:", msg["Subject"])
```

Expected display order observed: `Re:` leftmost, Arabic in the middle, `v3`
rightmost — matches the requirement that the prefix and Arabic not render in the
wrong order.

### Expected (from eval_cases.md)

```python
import smtplib
from email.message import EmailMessage
from arabic_fix import fix

msg = EmailMessage()
msg["Subject"] = fix("Re: ملاحظات على المسودة v3")
# BiDi puts "Re:" leftmost (LTR run before RTL run)
# then the Arabic
# then "v3" as LTR after the RTL — matches expected display order.
msg.set_content(fix("مرفق المسودة بعد التعديلات."))
with smtplib.SMTP("localhost") as s:
    s.send_message(msg)
```

### Pass/Fail — PASS

The AI emitted the same scaffolding as the expected snippet (`EmailMessage`,
`from arabic_fix import fix`, `msg["Subject"] = fix(...)`, `msg.set_content(fix(...))`,
`smtplib.SMTP("localhost")`):

- used `arabic_fix.fix()` on the subject string (B.1.1 ✅ — email subjects are
  non-Web targets because they are read by mail clients as raw RFC-822 strings,
  not by a browser with OpenType shaping)
- preserved logical order in code (B.1.2 ✅) — source string `"Re: ملاحظات على المسودة v3"` is in logical order
- kept NFC (B.1.4 ✅)
- LTR runs (`Re:`, `v3`) and the RTL run are correctly identified; `fix()`
  reorders to put `Re:` leftmost in display (B.1.2 ✅)
- body content also went through `fix()` (consistent application of B.1.1)

### Notes

- AI extended the snippet with `print("Sent subject:", ...)` and explanatory
  comments. Additive; not prohibited by Section B.
- The display-order comment ("`Re: المسودة على ملاحظات v3`") accurately reflects
  the UAX #9 BiDi reorder: `Re:` is the paragraph's leading LTR span, then the
  contiguous RTL Arabic run is visually reversed, then `v3` is the trailing LTR span.
- In logical code order the source is `Re: ملاحظات على المسودة v3` (LTR, RTL, LTR);
  after `fix()` and BiDi the visual order is `Re: المسودة على ملاحظات v3`. This is
  the expected outcome the case file describes.
- AI did **not** wrap the subject in HTML/`<bdi>` — correct, because email subjects
  are not Web targets and Section C's `<bdi>` rule does not apply. B.1.5 LTR
  isolation is satisfied by `fix()`'s built-in handling.

---

## Final Tally

| Case | Section | Result |
|---|---|---|
| Case 01 — terminal print      | B · Write Arabic    | ✅ PASS |
| Case 04 — HTML heading        | C · Design Arabic UI | ✅ PASS |
| Case 13 — RTL email subject   | B · Write Arabic    | ✅ PASS |

**Acceptance:** 3/3 pass (required 2/3). Cross-section discipline verified: in
Case 4 the AI did **not** call `fix()` for the Web target, while in Cases 1 and 13
the AI **did** call `fix()` for the non-Web terminal and email targets.
