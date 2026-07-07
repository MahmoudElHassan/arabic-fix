# arabic-fix — agent memory

> Project-scoped notes for AI agents working on this repo. Owned by
> `arabic-content-architect` rein. Append, don't rewrite.

## State

- **Current milestone:** v0.3.0 — system prompt rewrite + eval expansion +
  verification (delivered 2026-07-07).
- **Commits:** `ad651b3` (verification+tar), `4f62dc4` (eval), `98f6ecd`
  (prompts), on top of `47de8f7` (v0.2.0).
- **Tests:** 159 passing (`pytest -q`); mypy strict clean.
- **Tarball:** `arabic-fix.tar.gz` rebuilt, 64 KB, 63 files.

## v0.3.0 layout

```
agents/
  system_prompt.md         # 3 sections: A Read, B Write, C Design
                           # version 0.2.0, split_into: [read, write, design]
                           # each section standalone paste-able
  eval_cases.md            # 15 cases (10 original + 5 new for v0.3.0)
  verification/
    case-01-terminal-print.md
    case-04-html-heading.md
    case-13-rtl-email-subject.md
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

## Conventions for this repo

- Cite Unicode standards with revision year (UAX #9 = 2025, UAX #29 =
  2024). See agent memory for full list.
- Real Arabic in every test case. Never `"foo bar"`.
- Library verified via byte-level proof (`xxd`); cited in
  `docs/before-after.md`.
- Tarball rebuilt and committed alongside every meaningful change.
- System prompt is **always 3 splice-in-able sections** (A/B/C). Single
  monolithic prompts are forbidden.