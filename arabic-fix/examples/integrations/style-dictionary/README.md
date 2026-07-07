# arabic-fix — Style Dictionary integration

> Reference integration that converts `arabic-fix/designs/tokens.json`
> (73 W3C DTCG tokens) into **three downstream formats** that designers
> and engineers can drop into real projects.

## What you get

| Output | Format | Used by |
|---|---|---|
| `dist/css/variables.css` | CSS custom properties, light mode | Plain CSS / CSS Modules / PostCSS |
| `dist/css/variables-dark.css` | CSS custom properties, dark-mode filter | Theme switching via `[data-theme="dark"]` |
| `dist/css/all.css` | All tokens, no theme filter | Drop-in defaults |
| `dist/tailwind/tokens.js` | CommonJS flat token module | Tailwind projects (spread into `theme.extend`) |
| `dist/figma/tokens.json` | W3C DTCG JSON | Tokens Studio / Figma Variables |

## Quick start

```bash
cd examples/integrations/style-dictionary
npm install
npm run build       # writes to dist/
npm run verify      # smoke-tests the exports
```

After `npm run build`, link the artifacts into your project:

```bash
# Plain CSS
cp dist/css/variables.css path/to/your/styles/

# Tailwind — see "Use with Tailwind" below
cat dist/tailwind/tokens.js > path/to/your/project/

# Figma — paste dist/figma/tokens.json into Tokens Studio plugin
```

## Use with Tailwind

Style Dictionary 4 has no built-in Tailwind format, so we emit a flat
CommonJS module (`dist/tailwind/tokens.js`) that you spread into your
own `tailwind.config.js`. Example:

```js
// your-tailwind.config.js
const arabicFixTokens = require('arabic-fix-style-dictionary/tailwind/tokens.js');

module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        'arabic-display': arabicFixTokens.FontFamilyArabicDisplay,
        'arabic-body':    arabicFixTokens.FontFamilyArabicBody,
        'arabic-mono':    arabicFixTokens.FontFamilyArabicMono,
        // ...etc
      },
      fontSize: {
        'body-sm': arabicFixTokens.FontSizeBodySm, // "14px"
        // ...etc
      },
      spacing: {
        'inline-start-xs': arabicFixTokens.SpacingDirectionInlineStartXs, // "4px"
        // ...etc
      },
    },
  },
  plugins: [],
};
```

Use the tokens in markup:

```html
<h1 class="font-arabic-display text-display-xl text-start"
    dir="rtl" lang="ar">مرحبا بالعالم</h1>
```

## How it works

`sd.config.cjs` declares three Style Dictionary platforms. Each one reads
the same source — `../../../designs/tokens.json` — and writes to its own
output format. Style Dictionary 4 understands the W3C DTCG shape
(`$value` / `$type` / `$description`) natively, so no custom parser is
needed.

```js
// sd.config.cjs (excerpt)
module.exports = {
  source: ["../../../designs/tokens.json"],
  platforms: {
    css:     { /* → dist/css/*.css */ },
    tailwind: { /* → dist/tailwind/tailwind.config.js */ },
    figma:   { /* → dist/figma/tokens.json */ },
  },
};
```

## Why three platforms?

| Platform | Why |
|---|---|
| **CSS** | Every web project understands CSS variables. Zero dependencies — paste and go. |
| **Tailwind** | Many Arabic-UI projects already use Tailwind; this lets them keep their utility-class workflow without rewriting the token set. |
| **Figma** | Designers and engineers stay in sync when both pull from the same JSON. Tokens Studio reads W3C DTCG directly. |

## Direction rules (Arabic-specific)

These tokens are **RTL-aware by construction**:

- `spacing-direction.*` uses CSS logical-property names
  (`margin-inline-start`, not `margin-left`). The browser resolves them
  correctly per `dir="rtl"` / `dir="ltr"`.
- `motion.transform-translate.inline-rtl` exists for the rare case you
  really need physical translation.

If you're using these in a Tailwind config, set `dir="rtl"` on the
container and Tailwind's `rtl:` / `ltr:` variants will work as expected.

## Banned: `letter-spacing > 0` on Arabic

`typography.letter-spacing.arabic = 0` and carries a `banned: true`
marker in `$extensions`. Setting it > 0 on Arabic text is a content
bug — see `designs/tokens.README.md` §"Letter-spacing BANNED".

The export does not enforce this; the future `arabic-fix-lint` (v0.5.0)
will refuse to ship a stylesheet that breaks the rule.

## Versioning

The package version (`package.json`) tracks the arabic-fix version
that owns this integration. When `designs/tokens.json` changes, bump
the version here and re-publish.

## Tests

```bash
npm run verify
```

This is a smoke test, not exhaustive. It checks file existence, file
size, and that a known token (`letter-spacing.arabic = 0`) propagated
to `all.css`. Add project-specific checks in your own CI.