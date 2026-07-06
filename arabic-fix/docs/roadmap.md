# arabic-fix roadmap

> Working doc. Updated by the arabic-content-architect rein as milestones ship.
> Owner: arabic-content-architect (project rein). Reviewer: human maintainer.

## North star

> Every AI agent worldwide can read, write, and render Arabic content and UI
> with the same fidelity as English — because the tools and instructions are
> already in their workflow, not because every maintainer re-solves it.

## Current state (as of 2026-07-06)

| Layer | Status | Gap to ship |
|---|---|---|
| Library `arabic_fix/` (v0.1.0) | Smoke-tested only | No pytest, no CI, no real corpus, no mypy enforcement |
| `agents/eval_cases.md` | 10 cases | Add 5 real-world cases; quality check on the 10 |
| `agents/system_prompt.md` | 75 lines, monolithic | Rewrite as 3 splice-in-able sections |
| `designs/tokens.json` | 15 tokens, mixed format | Convert to pure JSON, ≥50 tokens, 3 export formats |
| `designs/font-stack.md` | Solid | — |
| `designs/rtl-rules.md` | Solid | — |
| Linter | Missing | New build |
| Distribution | Missing | PyPI + 3 harness examples |

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

### v0.4.0 — Design tokens
**Effort:** 1–2 days

**Deliverables:**
- `designs/tokens.json` — pure JSON, ≥50 tokens across font / spacing-direction / typography / color / motion
- All spacing/direction tokens use logical properties only (no `left`/`right`)
- `examples/integrations/style-dictionary/` — exports to CSS variables, Tailwind config, Figma token JSON
- `examples/sample-arabic-page.html` — sample rendering with all token categories

**Stop condition:** 50+ tokens, 3 export formats work, sample page renders correctly.

### v0.5.0 — Linter
**Effort:** 2–3 days

**Deliverables:**
- `arabic-fix-lint` CLI — detects: missing `dir` on Arabic HTML, mixed BiDi without isolation, RTL CSS mistakes, font-family without Arabic coverage, Latin digits in Arabic-number context
- `.github/hooks/pre-commit` and a GitHub Action that runs the linter on `.md` / `.html` / `.css` changes
- PyPI release of `arabic-fix` with both `arabic-fix` and `arabic-fix-lint` commands

**Stop condition:** linter catches the 10 eval cases (true positive), doesn't false-positive on Latin-only / empty / pass-through cases.

### v0.6.0 — Adoption
**Effort:** ongoing

**Deliverables:**
- Public landing page with live demo
- `examples/integrations/` — Cursor / Codex / OpenCode wiring examples
- 1 reference PR to a public harness
- README rewrite with the full story

## Rules of the road

1. **Foundation before surface.** v0.2.0 must complete before v0.3.0 starts. Each layer depends on the one below.
2. **Real Arabic, not synthetic.** No `"foo bar"`. Quran, Al Jazeera, real app UIs.
3. **Prove with bytes.** Any claim about reshape/BiDi must include `xxd` evidence in `docs/before-after.md`.
4. **Cite Unicode standards with revision year.** UAX #9 (last revised 2025), UAX #15 (NFC/NFKC), UAX #29 (text segmentation), UTS #39 (security), UTS #55 (normalization idempotence).
5. **Ship and tar after every meaningful change.** `arabic-fix.tar.gz` is the source of truth; never claim a milestone without rebuilding.
6. **One-line summary each session.** Rein posts a one-line "what shipped" to the orchestrator at the end of each session.

## Anti-patterns to avoid

- ❌ Architecture astronauts. No "let's rewrite the CLI in Rust" detours.
- ❌ Synthetic eval cases. Every test must be real Arabic a real user would encounter.
- ❌ Documentation without proof. No "v0.X.0 done" without tar rebuilt + a verification artifact.
- ❌ Renaming mid-stream. `arabic-fix` is locked until v1.0.
- ❌ Single monolithic system prompt. Always 3 splice-in-able sections.
- ❌ Left/right CSS properties. Logical only — `margin-inline-start`, never `margin-left`.

## Current next step

**v0.2.0 first deliverable:** `tests/test_shaper.py` covering the shaper's 4 cases (no ligatures / ligatures / empty string / Latin-only) + the Presentation Forms-B byte-level assertion that proved the fix in commit `a635d8a`.