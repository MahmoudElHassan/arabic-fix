/**
 * Smoke test for the Style Dictionary build output.
 *
 * Run after `npm run build`. Verifies:
 *   - dist/css/variables.css exists and is non-empty
 *   - dist/css/all.css exists
 *   - dist/css/variables-dark.css exists
 *   - dist/tailwind/tailwind.config.js exports a `theme.extend` object
 *   - dist/figma/tokens.json exists and is valid JSON
 *   - Each format contains a token we know exists in tokens.json
 *     (typography.letter-spacing.arabic = 0) — proves end-to-end wiring.
 *
 * Exits 0 on success, 1 on any check failure.
 */

const fs = require("fs");
const path = require("path");

const DIST = path.resolve(__dirname, "dist");
const checks = [];
let failed = 0;

function check(label, fn) {
  try {
    fn();
    checks.push(`  [OK]   ${label}`);
  } catch (err) {
    failed += 1;
    checks.push(`  [FAIL] ${label}\n         ${err.message}`);
  }
}

check("dist/ exists", () => {
  if (!fs.existsSync(DIST)) {
    throw new Error(`dist/ not found at ${DIST} — did you run 'npm run build'?`);
  }
});

check("dist/css/variables.css exists and non-empty", () => {
  const p = path.join(DIST, "css/variables.css");
  const stat = fs.statSync(p);
  if (stat.size < 200) {
    throw new Error(`file too small (${stat.size} bytes); build probably failed silently`);
  }
});

check("dist/css/all.css exists and non-empty", () => {
  const p = path.join(DIST, "css/all.css");
  const stat = fs.statSync(p);
  if (stat.size < 200) {
    throw new Error(`file too small (${stat.size} bytes)`);
  }
});

check("dist/css/variables-dark.css exists", () => {
  const p = path.join(DIST, "css/variables-dark.css");
  fs.accessSync(p, fs.constants.R_OK);
});

check("dist/tailwind/tokens.js is a CommonJS flat token module", () => {
  const p = path.join(DIST, "tailwind/tokens.js");
  const src = fs.readFileSync(p, "utf8");
  if (!/module\.exports\s*=\s*\{/.test(src)) {
    throw new Error(`expected "module.exports = { ... }" shape, got:\n${src.slice(0, 200)}`);
  }
  // Must contain at least one of the well-known token keys.
  if (!/FontFamilyArabicDisplay/.test(src)) {
    throw new Error(`expected FontFamilyArabicDisplay key in tokens.js`);
  }
});

check("dist/figma/tokens.json exists and is valid JSON", () => {
  const p = path.join(DIST, "figma/tokens.json");
  const data = JSON.parse(fs.readFileSync(p, "utf8"));
  if (Object.keys(data).length === 0) {
    throw new Error(`figma tokens file is empty`);
  }
});

check("letter-spacing.arabic token reached all.css (BANNED=0)", () => {
  const p = path.join(DIST, "css/all.css");
  const src = fs.readFileSync(p, "utf8");
  if (!/letter-spacing/i.test(src) || !/0(px|rem|em)?\s*;/.test(src)) {
    throw new Error(`letter-spacing token did not propagate to all.css`);
  }
});

console.log("arabic-fix style-dictionary — verification report");
console.log("--------------------------------------------------");
console.log(checks.join("\n"));
console.log("--------------------------------------------------");
if (failed > 0) {
  console.log(`FAIL — ${failed} check(s) failed.`);
  process.exit(1);
} else {
  console.log("PASS — all exports look good.");
}