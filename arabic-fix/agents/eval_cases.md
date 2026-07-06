# Eval cases for Arabic-handling AI agents

> Use this file with your LLM eval pipeline. Each case has:
> - **input**: what the agent sees
> - **expected_code_or_output**: what the agent should emit
> - **why**: what's broken if it doesn't

Run your agent through these after every system-prompt tweak.

---

## Case 1 — Shaping survives in code

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

**input**: "Translate `I wrote the book` to Arabic, preserving diacritics."

**bad**: `"كتبت الكتاب"` (harakat dropped)

**good**: `"كَتَبْتُ الْكِتَابَ"`

**why**: The diacritics disambiguate; dropping them is content loss.

---

## Case 4 — HTML output (different rules!)

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

**input**: "Pick a font for an Arabic blog."

**bad**: `font-family: 'Inter', sans-serif;` (Inter has NO Arabic glyphs)
**good**: `font-family: 'Tajawal', 'Noto Naskh Arabic', sans-serif;`

---

## Case 8 — Plural form (Arabic has 6)

**input**: "Generate `you have N messages` for N=1, 2, 5."

**good**:
- N=1 → `لديك رسالة واحدة`
- N=2 → `لديك رسالتان`
- N=5 → `لديك 5 رسائل`

**why**: Arabic has singular, dual (2), and plural (3-10, 11-99, 100+).
English-style plurals are wrong.

---

## Case 9 — Right number format

**input**: "Format 1234567 as a localized number for Arabic users."

**good**: `١٬٢٣٤٬٥٦٧` (Eastern Arabic-Indic digits + Arabic thousands separator)

**why**: Many Arabic locales use `١٢٣` not `123` and U+066C as separator.

---

## Case 10 — Email / URL stays LTR inside RTL

**input**: "Render `Contact: user@example.com — مرحبا` as an HTML footer."

**expected**:
```html
<p dir="rtl">
  Contact: <bdi>user@example.com</bdi> — مرحبا
</p>
```

**why**: `<bdi>` isolates the email so BiDi doesn't break the `@`.
