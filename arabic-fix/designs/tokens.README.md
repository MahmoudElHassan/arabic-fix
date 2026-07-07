# arabic-fix design tokens (v0.4.0)

> Pure-JSON design tokens for Arabic UI. Logical CSS properties only,
> RTL-aware by default, real Arabic fonts, BANNED letter-spacing on
> Arabic runs.

## Files

| File | Purpose |
|---|---|
| `tokens.json` | **73 tokens** across 5 categories. W3C DTCG format (`$value`/`$type`/`$description`). |
| `tokens.schema.json` | JSON Schema (Draft 2020-12). Validates `tokens.json` shape. |
| `validate_tokens.py` | Validates tokens.json, counts per category, checks BANNED token. |

## Categories

```
font               15  Arabic font stacks + weights + sizes + line-height + kashida
spacing-direction  15  Logical CSS properties only (inline-*, block-*) — never left/right
typography         12  BANNED letter-spacing (0), word-spacing, paragraph-indent, bidi-isolation
color              20  10 tokens × {light, dark} mode
motion             11  Durations, easings, RTL-aware transforms, z-index scale
TOTAL              73
```

Every category exceeds the v0.4.0 minimum of 10 tokens per category and
50 tokens overall.

## Format

Tokens follow the [W3C Design Tokens Community Group format](https://design-tokens.github.io/community-group/format/)
which is supported by Style Dictionary 3+, Figma Tokens (Tokens Studio),
and most modern design-system tooling. Every leaf token has:

```json
{
  "$value":       <value>,
  "$type":        <fontFamily | fontWeight | dimension | fontSize | lineHeight
                   | duration | cubicBezier | color | string | number | boolean>,
  "$description": "Human-readable meaning / usage.",
  "$extensions":  { /* optional custom metadata */ }
}
```

`$extensions` is used for:

- `mode: "light" | "dark"` — color tokens (each color token has a
  `light` and `dark` sibling under the same group).
- `rtl: "auto-flip" | "ltr-only" | "rtl-only" | "mirror"` — directional
  tokens. `auto-flip` means the token uses CSS logical-property naming
  so the browser resolves it correctly per `dir`.
- `banned: true` — flag for downstream linters to error on non-zero
  use. Used on `typography.letter-spacing.arabic`.
- `category: "font|spacing-direction|typography|color|motion"` —
  bookkeeping for tooling that needs to filter by category.

## Direction rules (why we never write `left` / `right`)

CSS logical properties auto-flip when `dir="rtl"`:

| Physical (forbidden for Arabic UI) | Logical (use this) |
|---|---|
| `margin-left` | `margin-inline-start` |
| `margin-right` | `margin-inline-end` |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left` | `inset-inline-start` |
| `right` | `inset-inline-end` |
| `text-align: left` | `text-align: start` |
| `text-align: right` | `text-align: end` |
| `float: left` | `float: inline-start` |
| `float: right` | `float: inline-end` |

Use physical properties only when you mean **physical** — e.g. a
calendar icon, a phone-pointer. The `transform-translate.inline-rtl`
motion token exists for that case.

## Letter-spacing BANNED

`typography.letter-spacing.arabic = 0` and carries
`$extensions.banned = true`. **Setting it > 0 on Arabic text is a bug**:

1. It adds space on the wrong side in RTL runs.
2. It breaks the Arabic baseline.
3. It interacts poorly with OpenType contextual ligatures
   (lam-alef, Allah).

Use `typography.word-spacing.arabic` instead.

The downstream `arabic-fix-lint` (planned v0.5.0) will refuse to ship
a stylesheet that sets letter-spacing > 0 on a selector matching
Arabic text.

## Real Arabic fonts

The `font.family.arabic.*` stacks ship production Arabic fonts in this
order (first listed = first to load):

- `family.arabic.display` — Tajawal, IBM Plex Sans Arabic, Noto Naskh
  Arabic, system-ui, sans-serif
- `family.arabic.body` — IBM Plex Sans Arabic, Tajawal, Noto Naskh
  Arabic, system-ui, sans-serif
- `family.arabic.mono` — Vazirmatn Mono, Fira Code Arabic, monospace
- `family.arabic.naskh` — Amiri, Noto Naskh Arabic, Scheherazade New,
  serif (Quran, long-form editorial)
- `family.mixed` — IBM Plex Sans Arabic, Tajawal, Inter, system-ui,
  sans-serif (bilingual UI strings)

All five carry Arabic glyphs; none falls back silently to a font with
no Arabic.

## Bidi-isolation principle

For mixed-script UI (Arabic paragraph with a `@mention`, email, file
path, version tag), use CSS `unicode-bidi: isolate` (token
`typography.bidi-isolation`). UTS #39 §6.2 (Security Mechanisms)
recommends isolation for visually-ambiguous spans. The token records
this default; per-instance overrides go in the component CSS.

## Validating locally

```bash
pip install jsonschema
python3 designs/validate_tokens.py
```

Expected output:
```
arabic-fix design tokens — validation report
--------------------------------------------------
  [OK] font: 15 token(s)
  [OK] spacing-direction: 15 token(s)
  [OK] typography: 12 token(s)
  [OK] color: 20 token(s)
  [OK] motion: 11 token(s)
--------------------------------------------------
  TOTAL: 73 tokens (minimum 50)
  BANNED letter-spacing.arabic: 0 (must be 0) — OK
--------------------------------------------------
PASS — schema valid, all thresholds met.
```

Exit code 0 = pass; 1 = schema violation; 2 = missing file / parse
error.

## Using in a build pipeline

**Style Dictionary 3+** (npm) reads `tokens.json` directly:

```bash
npm i -D style-dictionary
npx style-dictionary build --config sd.config.cjs
```

A minimal `sd.config.cjs`:

```js
module.exports = {
  source: ["designs/tokens.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "build/",
      files: [{ destination: "tokens.css", format: "css/variables" }]
    },
    tailwind: {
      transformGroup: "js",
      buildPath: "build/",
      files: [{ destination: "tailwind-tokens.js", format: "javascript/es6" }]
    }
  }
};
```

The Phase B deliverables of v0.4.0 ship reference Style Dictionary,
Tailwind, and Figma export configs in `examples/integrations/`.

## Citations

- **UAX #9** — Unicode Bidirectional Algorithm (last revised 2025).
  Source for bidi-isolation rules, dual-direction runs.
- **UAX #15** — Unicode Normalization Forms. NFC default for all
  emitted strings.
- **UAX #29** — Unicode Text Segmentation (last revised 2024).
  Source for kashida handling, tashkeel grapheme clusters.
- **UTS #39** — Unicode Security Mechanisms. Source for bidi-isolation
  as a security control against spoofing.