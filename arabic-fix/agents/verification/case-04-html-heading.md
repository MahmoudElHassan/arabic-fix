# Verification · Case 4 — HTML heading with `dir="rtl"` and font stack

## Spliced system prompt

**Section used:** `C · Design Arabic UI` (from `agents/system_prompt.md`,
version 0.2.0). Matches "When to splice this in" tag (agent emits HTML /
CSS / components).

Key rules that apply:

- C.1 #1: Always `dir="rtl"` and `lang="ar"` on the Arabic container.
- C.1 #2: Never pre-shape Arabic in HTML — the browser handles it.
- C.1 #4: Pick a font that has Arabic glyphs (Tajawal, IBM Plex Sans
  Arabic, Noto Naskh Arabic, Cairo, Vazirmatn, Amiri).
- C.1 #5: No `letter-spacing` on Arabic.
- C.2 forbids `<p>مرحبا</p>` with no `dir="rtl"`, and forbids
  `font-family: 'Inter', sans-serif` (no Arabic glyphs).
- C.3 self-check: dir/lang, logical order, logical CSS, Arabic font,
  no letter-spacing.

## User prompt (the eval case input)

> Add the heading `مرحبا` to an HTML page.

## Expected output (from eval_cases.md Case 4)

```html
<h1 dir="rtl" lang="ar" class="ar">مرحبا</h1>
```

```css
.ar {
  font-family: "Noto Naskh Arabic", "Amiri", "Cairo", serif;
  /* No letter-spacing: it pushes letters the wrong way in RTL */
}
```

## Real LLM run?

**No — auth blocker.** Same as case-01: `sk-xxx` placeholder in
`~/.mavis/config.yaml`. POST to `agent.minimax.io` returns
`401 auth failed`.

## Static rule trace

A model reading Section C with the prompt would, step by step:

1. Prompt → target = HTML page. Section C applies (matches "When to
   splice this in" tag).
2. C.1 #1 → emit `dir="rtl" lang="ar"` on the container.
3. C.1 #2 → leave Arabic in logical order, no pre-shaping. Output `مرحبا`
   not `ﻢﻜﺤﺭﻣ`.
4. C.1 #4 → pick a font from the production stack; output a CSS rule
   with at least one Arabic-capable font.
5. C.1 #5 → no `letter-spacing` in the CSS.
6. C.2 forbidden patterns → avoid `font-family: Inter` (no Arabic
   glyphs); avoid `letter-spacing`; avoid `<p>مرحبا</p>` with no dir.

**Predicted output:** an `<h1 dir="rtl" lang="ar">` with a CSS rule
using one of `Tajawal / IBM Plex Sans Arabic / Noto Naskh Arabic /
Cairo / Vazirmatn / Amiri`. The exact font choice may vary (model picks
from the list) but every choice in the list passes C.1 #4.

## Verdict

**PASS** on rule-trace + self-check dimension.
**NOT RUN** on real-LLM-call dimension (auth blocker; see case-01 for
remediation).

## To turn this into a real LLM run

Same as case-01: replace `sk-xxx` in `~/.mavis/config.yaml` and re-run
with Section C as the system prompt.