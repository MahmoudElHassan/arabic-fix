# arabic-fix — agent memory

> Project-scoped notes for AI agents working on this repo. Owned by
> `arabic-content-architect` rein. Append, don't rewrite.

## State

- **Current milestone:** v0.4.0 — design tokens + first public PyPI release
  (delivered 2026-07-08).
- **Commits:** `6cdf519` (G1+G2+G3 stop-condition), `b917a94` (P0 quick wins
  from Cursor review), `76445d3` / `91108c8` (Phase A tokens + tarball),
  on top of `51733bf` (v0.3.1 hotfix).
- **Tests:** 169 passing (`pytest -q`); mypy strict clean.
- **PyPI:** v0.4.0 published at https://pypi.org/project/arabic-fix/.
- **Tarball:** `arabic-fix.tar.gz` rebuilt, 116 KB, 62 files (legacy —
  PyPI is now the source of truth; revisit in v0.5.0 per Cursor review).

## v0.3.0 layout

```
agents/
  system_prompt.md         # 3 sections: A Read, B Write, C Design
                           # version 0.3.1, split_into: [read, write, design]
                           # each section standalone paste-able
  eval_cases.md            # 15 cases (10 original + 5 new for v0.3.0)
  verification/
    case-01-terminal-print.md
    case-04-html-heading.md
    case-13-rtl-email-subject.md
    cursor-verified.md     # 3/3 cases via Cursor AI; dates still placeholder
```

## v0.3.0 verification limitation

Real LLM runs were NOT executed in this milestone because
`~/.mavis/config.yaml` carries `provider.minimax.options.apiKey: sk-xxx`
(literal placeholder, returns `401 auth failed`). The verification
artifacts document this and use a static rule trace + real-byte library
check instead. **To unlock real LLM runs:** human maintainer installs a
real minimax API key in config.yaml, then re-runs the bash commands
documented in each verification file.

## Next milestone

**v0.4.0 — Design tokens + first public release** (per `docs/roadmap.md`):
- `designs/tokens.json` → pure JSON, ≥50 tokens across font / spacing /
  typography / color / motion; logical properties only.
- `examples/integrations/style-dictionary/` (CSS / Tailwind / Figma
  exports).
- README rewrite (60-second-onboarding).
- First PyPI release as `arabic-fix` v0.4.0.

## Architecture review (2026-07-08, pre-Cursor)

Empirical checks run before handing the project to Cursor for review.
Findings saved here so future agents don't re-litigate them.

### Pipeline order (normalize → shape → bidi) — confirmed correct
- For NFC-clean input, `n + s + b == s + b` (normalize is a noop).
- For NFD input (e.g. macOS-exported strings), normalize is the guard
  against representation drift before shaping.
- Don't reorder without explicit reason. The order is in `fixer._apply()`.

### `fix()` is NOT idempotent — load-bearing property
- `fix(fix(x)) != fix(x)` — verified empirically.
- Implication: `--check` mode in CLI does catch double-fix, because the
  second pass still produces different bytes than the first. So the
  v0.4.0 review concern ("--check silently says fine on already-broken
  input") is LESS severe than intuition suggested.
- Document this behavior if it ever matters to callers; right now it's
  a load-bearing property, not a bug.

### P1.5 — FixOptions does NOT validate at construction
- `FixOptions(normalize_form="bogus")` does NOT raise.
- Validation only happens in `_coerce_options()` at `fix()` call time.
- Direct FixOptions construction (e.g. from a config file or library
  internal call) lets bad values through, which then either get caught
  later by `unicodedata.normalize()` (cryptic error) or by `python-bidi`
  (cryptic error) — neither points at the actual FixOptions field.
- **Fix:** add `__post_init__` to FixOptions that validates
  `normalize_form in {NFC,NFD,NFKC,NFKD}` and `bidi_base_dir in {rtl,ltr}`.
- **Status (2026-07-08):** FIXED in v0.4.0 prep commit. `__post_init__`
  added to `FixOptions` with case-insensitive form validation and
  bidi_base_dir normalization. Verified by Cursor AI review.

## Conventions for this repo

- Cite Unicode standards with revision year (UAX #9 = 2025, UAX #29 =
  2024). See agent memory for full list.
- Real Arabic in every test case. Never `"foo bar"`.
- Library verified via byte-level proof (`xxd`); cited in
  `docs/before-after.md`.
- Tarball rebuilt and committed alongside every meaningful change.
- System prompt is **always 3 splice-in-able sections** (A/B/C). Single
  monolithic prompts are forbidden.