# arabic-fix roadmap

> Working doc. Updated by the arabic-content-architect rein as milestones ship.
> Owner: arabic-content-architect (project rein). Reviewer: human maintainer.

## North star

> Every AI agent worldwide can read, write, and render Arabic content and UI
> with the same fidelity as English — because the tools and instructions are
> already in their workflow, not because every maintainer re-solves it.

## Current state (as of 2026-07-07)

| Layer | Status | Gap to ship |
|---|---|---|
| Library `arabic_fix/` (v0.1.0) | Smoke-tested only | No pytest, no CI, no real corpus, no mypy enforcement |
| `agents/eval_cases.md` | 10 cases | Add 5 real-world cases; quality check on the 10 |
| `agents/system_prompt.md` | 75 lines, monolithic | Rewrite as 3 splice-in-able sections |
| `designs/tokens.json` | 15 tokens, mixed format | Convert to pure JSON, ≥50 tokens, 3 export formats |
| `designs/font-stack.md` | Solid | — |
| `designs/rtl-rules.md` | Solid | — |
| Linter | Missing | v0.5.0 build (scope-cut) |
| Distribution | Missing | PyPI at v0.4.0; adoption at v0.6.0 |

**Overall: ~25% done.** Library works at byte level (real reshape confirmed via `xxd`).

## Locked decisions (delegated by user)

- **Brand: `arabic-fix` for v0.x.** Renaming at v1.0 if needed.
- **Distribution model: reference implementation, not upstream.** Ship `examples/integrations/`. Don't make arabic-fix the bottleneck.
- **Test strategy: real corpus, not synthetic.** Quran for tashkeel, Al Jazeera for headlines, real app UIs for mixed-script.
- **Execution model: rein drives; human reviews.** Autonomous sessions, one-line summary each. Human-in-loop only for design forks.

## Milestones

### v0.2.0 — Lock the library
**Effort:** 2–3 days

**Deliverables:**
- `tests/test_shaper.py`, `tests/test_bidi.py`, `tests/test_fixer.py`, `tests/test_cli.py` — ≥80% coverage
- `tests/corpus/` — Quran samples, Al Jazeera headlines, real app UI strings, edge cases
- `.github/workflows/ci.yml` — Python 3.9 / 3.11 / 3.12 matrix
- `mypy --strict` clean on `arabic_fix/`
- Version bumped to 0.2.0 in `pyproject.toml`
- `arabic-fix.tar.gz` rebuilt

**Stop condition:** `pytest` exits 0 on 3 Python versions, mypy strict exits 0, all corpus cases pass.

### v0.3.0 — System prompt + eval
**Effort:** 1–2 days

**Deliverables:**
- `agents/system_prompt.md` rewritten as 3 splice-in-able sections:
  - **Read Arabic** (detect script, don't reshape user input)
  - **Write Arabic** (preserve tashkeel, isolate mixed-script runs)
  - **Design Arabic UI** (logical CSS, font fallback rules)
- Each section tagged with "when to splice this in"
- `agents/eval_cases.md` expanded from 10 → 15 cases (add: log file BiDi, Slack/Notion Arabic, RTL email subject, GitHub issue body, terminal output)
- Verification artifact: 3 real LLM runs on 3 cases; outputs saved to `agents/verification/`

**Stop condition:** ≥3 real LLM runs produce correct output for ≥3 eval cases without further prompting.

### v0.4.0 — Design tokens + first public release
**Effort:** 1–2 days

**Deliverables:**
- `designs/tokens.json` — pure JSON, ≥50 tokens across font / spacing-direction / typography / color / motion
- All spacing/direction tokens use logical properties only (no `left`/`right`)
- `examples/integrations/style-dictionary/` — exports to CSS variables, Tailwind config, Figma token JSON
- `examples/sample-arabic-page.html` — sample rendering with all token categories
- **README rewrite** — installation, usage, architecture diagram, links to eval cases + tokens + corpus. Anyone landing on the repo or PyPI page can grok it in 60 seconds.
- **First PyPI release** as `arabic-fix` v0.4.0. Library + tokens. `pip install arabic-fix` works globally.

**Why PyPI moved here:** the linter depends on the library, but the library is useful on its own. Don't gate public access on the linter shipping.

**Stop condition:** 50+ tokens, 3 export formats work, sample page renders correctly, README rewrite reviewed, `pip install arabic-fix` works in a clean venv.

### v0.5.0 — Linter (scope-cut)
**Effort:** 2–3 days

**Deliverables — scope cut from 5 detectors to 2 for v0.5.0:**
- ✅ Detect: **missing `dir` on Arabic HTML** (highest-signal rule — direct cite from real bugs)
- ✅ Detect: **RTL CSS mistakes** (`margin-left` instead of `margin-inline-start`, `letter-spacing` on Arabic)
- ⏸ Defer to v0.6.0+: font-family Arabic glyph coverage, mixed-BiDi isolation, Latin digits in Arabic-number context. These need a font DB or fontTools at runtime — too much weight for v0.5.0.
- `arabic-fix-lint` CLI as a subcommand of `arabic-fix` (not a separate package).
- **GitHub Action** that runs the linter on `.html` / `.css` / `.md` changes — generic, harness-agnostic.
- **No harness-specific hooks** in v0.5.0. Wait for a maintainer to ask.

**Why the cut:** the 5-detector scope was overambitious for the input data we have. Two high-confidence rules ship now; the others wait for evidence that they catch real bugs in the wild.

**Stop condition:** linter catches the 10 eval cases (true positive on the 2 supported rules), doesn't false-positive on Latin-only / empty / pass-through cases.

### v0.6.0 — Adoption (with measurement + fallback)
**Effort:** ongoing

**Deliverables:**
- Public landing page with live demo
- `examples/integrations/` — Cursor / Codex / OpenCode wiring examples
- 1 reference PR to a public harness
- **Measurement (added per mavis-doctor review):**
  - PyPI download count (weekly check via pypistats)
  - GitHub stars / forks / open issues
  - Eval-case pass-rate in CI (must stay ≥95%)
  - Harness integration count (count of `examples/integrations/` consumers)
  - Reported in `docs/adoption-metrics.md` updated monthly
- **Fallback (added per mavis-doctor review):** if 0/3 reference PRs land within 90 days, ship a separate repo `arabic-fix-integrations/` with reference wiring harnesses maintainers can copy from. Don't block adoption on other people's review cycles.
- **Audience targeting:**
  - Arabic-speaking devs → PyPI + GitHub discoverability + Arabic-language README section
  - Arabic-product PMs → landing page + before/after visuals
  - AI harness maintainers → `examples/integrations/` + minimal copy-paste path

**Stop condition:** ≥1 harness ships a reference integration OR `arabic-fix-integrations/` repo has ≥3 community-contributed examples.

## Risks I missed earlier (added)

- **Standards move.** UAX #9 was last revised 2025; will be revised again. Library + linter must track or rot. Pin a check: every 6 months, verify against current Unicode revision.
- **Browser divergence.** Chrome / Firefox / Safari handle BiDi differently. Library assumes terminal — what about mobile Safari? Note in `docs/before-after.md`.
- **Locale specificity.** Roadmap assumes Modern Standard Arabic. Egyptian / Gulf / Maghrebi have different number conventions and plural rules. Eval case 8 is MSA. Note in `agents/eval_cases.md` per-case which locale/dialect.
- **Single-maintainer (me) bottleneck.** Adoption at v0.6.0 needs issue response, PR review, blog posts. Before v0.6.0, identify a co-maintainer candidate.

## Rules of the road

1. **Foundation before surface.** v0.2.0 must complete before v0.3.0 starts. Each layer depends on the one below.
2. **Real Arabic, not synthetic.** No `"foo bar"`. Quran, Al Jazeera, real app UIs.
3. **Prove with bytes.** Any claim about reshape/BiDi must include `xxd` evidence in `docs/before-after.md`.
4. **Cite Unicode standards with revision year.** UAX #9 (last revised 2025), UAX #15 (NFC/NFKC), UAX #29 (text segmentation), UTS #39 (security), UTS #55 (normalization idempotence).
5. **Ship and tar after every meaningful change.** `arabic-fix.tar.gz` is the source of truth; never claim a milestone without rebuilding.
6. **One-line summary each phase.** Rein posts a one-line "what shipped" to the orchestrator at the end of each phase.
7. **Measurement before more scope.** v0.6.0 measurement runs before any v0.7.0 work — adoption data must drive scope.

## Anti-patterns to avoid

- ❌ Architecture astronauts. No "let's rewrite the CLI in Rust" detours.
- ❌ Synthetic eval cases. Every test must be real Arabic a real user would encounter.
- ❌ Documentation without proof. No "v0.X.0 done" without tar rebuilt + a verification artifact.
- ❌ Renaming mid-stream. `arabic-fix` is locked until v1.0.
- ❌ Single monolithic system prompt. Always 3 splice-in-able sections.
- ❌ Left/right CSS properties. Logical only — `margin-inline-start`, never `margin-left`.
- ❌ Scope-creep detectors before measurement. Linter grows only when real bugs demand it.

## Current next step

**v0.2.0, Phase A (now):** commit roadmap revision with the 6 mavis-doctor fixes baked in.
**v0.2.0, Phase B (next, after approval):** test infrastructure skeleton — `tests/`, `conftest.py`, pytest config in `pyproject.toml`.