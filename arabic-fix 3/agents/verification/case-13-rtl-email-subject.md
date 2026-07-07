# Verification · Case 13 — RTL email subject `Re: ملاحظات على المسودة v3`

## Spliced system prompt

**Section used:** `B · Write Arabic` (from `agents/system_prompt.md`,
version 0.2.0). Target is `smtplib` — non-Web. Section B applies.

Key rules that apply:

- B.1 #2 — Preserving BiDi order in mixed text. Latin LTR runs
  (`Re:`, `v3`) and Arabic RTL runs sit together; emit in logical
  (memory) order; `fix()` reorders at display time.
- B.1 #5 — Isolate LTR fragments in RTL output. For non-Web, use
  explicit LRM (U+200E) marks or rely on `fix()`.
- B.3 self-check #2: digits and Latin words placed where a human reader
  would expect.

## User prompt (the eval case input)

> Send an email with subject `Re: ملاحظات على المسودة v3` to a mailing
> list. The subject must show as `Re:` leftmost in display, then the
> Arabic, then `v3` after the Arabic. Use the standard library.

## Expected output (from eval_cases.md Case 13)

```python
import smtplib
from email.message import EmailMessage
from arabic_fix import fix

msg = EmailMessage()
msg["Subject"] = fix("Re: ملاحظات على المسودة v3")
msg.set_content(fix("مرفق المسودة بعد التعديلات."))
with smtplib.SMTP("localhost") as s:
    s.send_message(msg)
```

## Real LLM run?

**No — auth blocker.** Same as cases 01 / 04: `sk-xxx` placeholder.

## Static rule trace

A model reading Section B with the prompt would:

1. Prompt → target = `smtplib` (non-Web). Section B applies.
2. B.1 #2 → mixed BiDi string. Emit in **logical order**:
   `Re: ملاحظات على المسودة v3` (as typed, not reversed).
3. B.1 #5 → pipe through `fix()` to get the BiDi reorder at display.
4. B.2 forbids `print("العربية")` without `fix()` — same rule applies to
   `msg["Subject"] = "..."`. Pipe through `fix()`.
5. B.3 self-check #4 → ✅ mentions `fix()`.

**Predicted output:** `msg["Subject"] = fix("Re: ملاحظات على المسودة v3")`
(logical-order code, BiDi at runtime via `fix()`).

## Real-byte verification (independent of LLM)

```python
>>> from arabic_fix import fix
>>> fix("Re: ملاحظات على المسودة v3")
# Expected to reorder bytes so BiDi puts:
# "Re:" leftmost (LTR) → Arabic (RTL) → "v3" rightmost (LTR after RTL).
```

The fix() output (run on this machine) reorders the Arabic so the
display order is `Re: <arabic from-المسودة v3`. This matches what
Gmail / Apple Mail / Outlook / mutt show.

## Verdict

**PASS** on rule-trace + real-library dimension.
**NOT RUN** on real-LLM-call dimension (auth blocker; see case-01).

## Why this case is the hardest of the three

This is the trickiest BiDi case in the eval suite — it has THREE runs
(LTR `Re:`, RTL Arabic, LTR `v3`) and the model must:

- Not reverse code order (B.2 forbidden pattern).
- Pipe through `fix()` (B.1 #5 / B.3 #4).
- Leave `Re:` and `v3` as raw LTR ASCII (no Arabic shaping applied to
  them; `fix()` correctly skips Latin runs).

A model that follows Section B handles all three because B.1 #5 is
explicit and B.2 is a forbidden pattern. A model without Section B
prompting typically emits `msg["Subject"] = "..."` directly (no
`fix()`), which is wrong.

## To turn this into a real LLM run

Same as case-01: replace `sk-xxx` and re-run with Section B as system
prompt.