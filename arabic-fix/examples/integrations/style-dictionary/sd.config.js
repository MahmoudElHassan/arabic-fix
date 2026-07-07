/**
 * Style Dictionary 4 config for arabic-fix design tokens.
 *
 * Source: ../../../designs/tokens.json (73 tokens, 5 categories, W3C DTCG)
 *
 * Outputs three downstream formats:
 *   - dist/css/variables.css           — CSS custom properties (light + dark)
 *   - dist/tailwind/tailwind.config.js — Tailwind v3 config (theme.extend)
 *   - dist/figma/tokens.json           — copy of W3C DTCG JSON for Figma import
 *
 * Run:  npm install && npm run build
 *
 * Why three platforms?
 *   - CSS variables → drop-in for plain stylesheets, no framework needed.
 *   - Tailwind config → for projects already on Tailwind; consumers do
 *     `import config from 'arabic-fix-tailwind-config'` and merge into
 *     their tailwind.config.js.
 *   - Figma JSON → paste into Tokens Studio / Figma Variables to keep
 *     design source-of-truth synced with code.
 *
 * Style Dictionary 4 supports W3C DTCG natively (the `$value`/`$type`/
 * `$description` shape used in tokens.json). No pre-processing needed.
 */

const path = require("path");

// `path.resolve` strips trailing slashes on darwin/linux, but
// Style Dictionary 4 hard-requires a trailing slash on `buildPath`.
// Build a helper that always appends one.
const buildPath = (...parts) =>
  path.resolve(__dirname, ...parts) + path.sep;

module.exports = {
  // Source: the W3C DTCG token file in the parent repo.
  source: [path.resolve(__dirname, "../../../designs/tokens.json")],

  // The DTCG format is supported natively by Style Dictionary 4 — no
  // custom parser needed. We just declare the platforms we export to.
  platforms: {
    // ─────────────────────────────────────────────────────────────────
    // Platform 1: CSS custom properties
    // ─────────────────────────────────────────────────────────────────
    css: {
      transformGroup: "css",
      buildPath: buildPath("dist/css"),
      files: [
        {
          destination: "variables.css",
          format: "css/variables",
          options: {
            outputReferences: false,
            selector: ":root[data-theme='light']",
          },
        },
        {
          destination: "variables-dark.css",
          format: "css/variables",
          filter: (token) => {
            // Only emit dark-mode tokens in this file.
            const ext = token.$extensions || {};
            return ext.mode === "dark";
          },
          options: {
            outputReferences: false,
            selector: ":root[data-theme='dark']",
          },
        },
        {
          destination: "all.css",
          format: "css/variables",
          options: {
            outputReferences: false,
            selector: ":root",
          },
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────
    // Platform 2: Tailwind-friendly token module
    // ─────────────────────────────────────────────────────────────────
    // Style Dictionary 4 has no built-in Tailwind format. We emit a
    // flat JS object (`tokens.js`) that consumers spread into their own
    // `tailwind.config.js` under `theme.extend`. The example merge is
    // documented in `README.md` §"Use with Tailwind".
    tailwind: {
      transformGroup: "js",
      buildPath: buildPath("dist/tailwind"),
      files: [
        {
          destination: "tokens.js",
          format: "javascript/module-flat",
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────
    // Platform 3: Figma / Tokens Studio
    // ─────────────────────────────────────────────────────────────────
    figma: {
      transformGroup: "js",
      buildPath: buildPath("dist/figma"),
      files: [
        {
          // Tokens Studio / Figma Variables reads the W3C DTCG shape
          // directly. Just copy the source as-is so designers can
          // import the exact same JSON developers use.
          destination: "tokens.json",
          format: "json/flat",
        },
      ],
    },
  },
};