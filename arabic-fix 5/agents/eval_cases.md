# Eval cases for Arabic-handling AI agents

> Use this file with your LLM eval pipeline. Each case has:
> - **input**: what the agent sees
> - **expected_code_or_output**: what the agent should emit
> - **why**: what's broken if it doesn't

Run your agent through these after every system-prompt tweak.

---

## Case 1 — Shaping survives in code

**locale**: MSA (Modern Standard Arabic). Output target: macOS Terminal.app, no Arabic font fallback set.

**input**: "Write a Python `greet()` function that prints `السلام عليكم` to
the terminal. Run on macOS, Python 3.12."

**expected_code_or_output**:
```python
from arabic_fix import fix

def greet() -> None:
    msg = fix("السلام عليكم")     # shape + BiDi + normalize
    print(msg)
```

**why**: Terminals don't auto-shape Arabic. Without `fix()`, the user
sees unconnected glyphs.

---

## Case 2 — Mixed BiDi string for a log file

**locale**: MSA. Mixed ASCII-Arabic digits — Arabic digit policy depends on user locale.

**input**: "Append `User 42 logged in from الرياض at 09:30` to a log file."

**expected_code_or_output**:
```python
import logging
from arabic_fix import fix

logger = logging.getLogger(__name__)
line = fix("User 42 logged in from الرياض at 09:30")
logger.info(line)
```

**why**: BiDi reordering matters for log grep'ability AND human
readability.

---

## Case 3 — Tashkeel preservation

**locale**: MSA (formal translation). Tashkeel applies across all Arabic dialects.

**input**: "Translate `I wrote the book` to Arabic, preserving diacritics."

**bad**: `"كتبت الكتاب"` (harakat dropped)

**good**: `"كَتَبْتُ الْكِتَابَ"`

**why**: The diacritics disambiguate; dropping them is content loss.

---

## Case 4 — HTML output (different rules!)

**locale**: MSA. Browser handles shaping regardless of dialect.

**input**: "Add the heading `مرحبا` to an HTML page."

**expected_code_or_output**:
```html
<h1 dir="rtl" lang="ar" class="ar">مرحبا</h1>
```

```css
.ar {
  font-family: "Noto Naskh Arabic", "Amiri", "Cairo", serif;
  /* No letter-spacing: it pushes letters the wrong way in RTL */
}
```

**why**: Browser handles shaping. Don't pre-shape. Use logical
properties and a proper font stack.

---

## Case 5 — Don't reverse the code order

**locale**: MSA. Code-side BiDi logic is dialect-agnostic.

**input**: "Write a JS string concatenation: `'<welcome>' + 'مرحبا' +
'<end>'`, using template literals."

**bad**:
```js
const html = `<end> مرحبا <welcome>` // code-level reversal is wrong
```

**good**:
```js
const html = `<welcome> ${fix("مرحبا")} <end>`
// logical order in code; display order = BiDi of the runtime string
```

**why**: Code-side reversal lies to your maintainers. Let BiDi do it.

---

## Case 6 — Don't add `letter-spacing` for Arabic

**locale**: MSA. CSS rendering applies to all Arabic locales.

**input**: "Style an Arabic paragraph."

**bad**:
```css
.ar { letter-spacing: 0.05em; }
```

**good**:
```css
.ar {
  word-spacing: 0.05em;
  /* letter-spacing breaks Arab baseline in unpredictable ways */
}
```

---

## Case 7 — Use a font that has Arabic

**locale**: MSA. Font choice should cover the user's full locale glyph range.

**input**: "Pick a font for an Arabic blog."

**bad**: `font-family: 'Inter', sans-serif;` (Inter has NO Arabic glyphs)
**good**: `font-family: 'Tajawal', 'Noto Naskh Arabic', sans-serif;`

---

## Case 8 — Plural form (Arabic has 6)

**locale**: MSA. CLDR categories: zero/one/two/few (3-10)/many (11-99)/other (100+). Egyptian dialect collapses to 3 categories (1, 2, 3+); Maghrebi varies further. Ask if dialectal.

**input**: "Generate `you have N messages` for N=0, 1, 2, 5, 25, 150."

**good** (MSA, all six CLDR plural categories):
- N=0 → `ليس لديك رسائل` (zero)
- N=1 → `لديك رسالة واحدة` (one)
- N=2 → `لديك رسالتان` (two)
- N=5 → `لديك 5 رسائل` (few: 3–10)
- N=25 → `لديك 25 رسالة` (many: 11–99)
- N=150 → `لديك 150 رسالة` (other: 100+)

**why**: Arabic has six plural categories per CLDR: `zero`, `one`, `two`,
`few` (3–10), `many` (11–99), `other` (100+). English-style plurals are
wrong. Colloquial dialects collapse categories — Egyptian uses 3 (1, 2, 3+),
Maghrebi varies further. The MSA forms shown above are the default; ask
the user before assuming dialectal.

---

## Case 9 — Right number format

**locale**: ar-SA (Saudi Arabia) uses Eastern Arabic-Indic digits `١٢٣` + U+066C separator. Tunisia/Morocco/Algeria use ASCII digits `123`. Levant varies. Match the user's locale explicitly.

**input**: "Format 1234567 as a localized number for Arabic users."

**good**: `١٬٢٣٤٬٥٦٧` (Eastern Arabic-Indic digits + Arabic thousands separator)

**why**: Many Arabic locales use `١٢٣` not `123` and U+066C as separator.

---

## Case 10 — Email / URL stays LTR inside RTL

**locale**: MSA. Email/URL rendering is locale-independent.

**input**: "Render `Contact: user@example.com — مرحبا` as an HTML footer."

**expected**:
```html
<p dir="rtl">
  Contact: <bdi>user@example.com</bdi> — مرحبا
</p>
```

**why**: `<bdi>` isolates the email so BiDi doesn't break the `@`.

---

## Case 11 — Log file BiDi (Python `logging`, mixed-script, grep'able)

**locale**: MSA. Log line Arabic text uses logical codepoints; `grep` matches logical order.

**input**: "Write a Python module that logs `User 42 logged in from الرياض
at 09:30` to a rotating file handler. Ops team greps for both
`user_id=42` and `الرياض`."

**expected_code_or_output**:
```python
import logging
from logging.handlers import RotatingFileHandler
from arabic_fix import fix

logger = logging.getLogger(__name__)
handler = RotatingFileHandler("app.log", maxBytes=10_000_000, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def on_login(user_id: int, city: str, at: str) -> None:
    line = fix(f"User {user_id} logged in from {city} at {at}")
    logger.info(line)
```

**why**: Log files are non-Web targets — terminal and `grep` see raw
bytes. Without `fix()` the city name ships as unconnected glyphs and
`grep "الرياض"` fails. BiDi reorder keeps `user_id=42` next to the
verb in display order while `grep` matches in logical order.

---

## Case 12 — Slack / Notion message (emoji + tashkeel + RTL marks)

**locale**: MSA. Tashkeel content is dialect-independent (Quranic-style tashkeel shown).

**input**: "Post a Slack message: `📢 تَذكِير: اِجتِماع الفَريق غَدًا السّاعَة 10:00 ص`. The message must render correctly with tashkeel intact."

**expected_code_or_output**:
```python
from arabic_fix import fix

msg = fix("📢 تَذكِير: اِجتِماع الفَريق غَدًا السّاعَة 10:00 ص")
# Slack's web client reshapes on display, but clipboard paste from a
# terminal, Notion API write, and chat.postMessage from a backend
# don't auto-shape — pre-shape defensively when the source is a Python
# pipeline:
print(msg)  # or chat.postMessage(channel=..., text=msg)
```

**why**: Tashkeel (حركات) is content — `تَذكِير` ≠ `تذكير` ≠ `تذكّر`.
Slack's web client reshapes on display, but clipboard paste from a
terminal, Notion API write, and `chat.postMessage` from a backend
*don't* auto-shape. Pre-shape via `fix()` to make the message robust
across all paths. Emoji is an LTR run inside the RTL paragraph —
preserved by `fix()`.

---

## Case 13 — RTL email subject (`Re: ملاحظات على المسودة`)

**locale**: MSA. Subject rendering is locale-independent.

**input**: "Send an email with subject `Re: ملاحظات على المسودة v3` to a
mailing list. The subject must show as `Re:` leftmost in display, then
the Arabic, then `v3` after the Arabic."

**expected_code_or_output**:
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

**why**: Email clients vary wildly in BiDi handling. Pre-shaping via
`fix()` is the only way to get consistent behavior across Gmail web,
Apple Mail, Outlook, and `mutt`. The `Re:` prefix is LTR, the Arabic
is RTL, the `v3` version tag is LTR — `fix()` reorders to match what
human readers expect.

---

## Case 14 — GitHub issue body (code fences, markdown lists, RTL)

**locale**: MSA. GitHub renderer handles dialect-agnostic shaping.

**input**: "Open a GitHub issue titled `خطأ في تسجيل الدخول` with body:

```
## الخطوات
1. افتح `/login`
2. أدخل البريد `user@example.com`
3. اضغط دخول

```python
# expected output
print(fix('مرحبا'))
```

> الخطأ: 'invalid credentials'
"

The issue must render with the steps in RTL and the code block LTR."

**expected_code_or_output**:
```markdown
## الخطوات
1. افتح `/login`
2. أدخل البريد `user@example.com`
3. اضغط دخول

```python
# expected output
print(fix('مرحبا'))
```

> الخطأ: 'invalid credentials'
```

(emit **logical-order** Arabic in the body; GitHub's browser renderer
shapes it. Do NOT call `fix()` for Web targets.)

**why**: GitHub is Web — DO NOT call `fix()` on the issue body. Emit
Arabic in logical order. The browser viewing GitHub handles shaping
and BiDi. Code fences are always LTR. Email inside the prose stays
isolated by GitHub's renderer.

---

## Case 15 — Terminal output without `fix()` (the classic broken case)

**locale**: MSA. Output target: macOS Terminal.app with default font (Geeza Pro on macOS). **Note:** Terminal.app with Geeza Pro *does* apply OpenType shaping and renders connected Arabic; the unconnected-glyph failure mode occurs on Linux terminals (xterm, GNOME Terminal) without an Arabic font fallback. Test on the specific target.

**input**: "Run this Python script and explain what the user sees:

```python
print('السلام عليكم')
```

User is on macOS, Python 3.12, default Terminal.app."

**expected_code_or_output**:

**Diagnosis:** the user sees the letters in isolation forms, no
connections, baseline broken — `ﺍﻟﺴﻼﻡ ﻋﻠﻴﻜﻢ` rendered with
every codepoint in its isolated form. This is because Terminal.app
renders Arabic from the byte stream without applying OpenType shaping
features (`init`, `medi`, `fina`, `isol`).

**Fix:**
```python
from arabic_fix import fix
print(fix('السلام عليكم'))
```

After `fix()`, the codepoints land in U+FE70–U+FEFF (Presentation
Forms-B) with correct contextual forms (initial, medial, final,
isolated), and Terminal.app renders connected Arabic.

**why**: This is the single most common bug in Arabic tooling —
Python 3 strings carry codepoints in logical order and the *font*
has the glyphs, but the *terminal emulator* does not apply OpenType
shaping. The `fix()` step pre-shapes so the terminal's naive
renderer can display connected Arabic. Verify with
`python -c "import sys; sys.stdout.write(fix('السلام'))"` and inspect
the output with `xxd` to confirm Presentation Forms-B codepoints.
