
### Unicode standards revision years (2026-07-07)
Type: reference
Always cite Unicode standards with their **revision year**, not just the name:
- **UAX #9 — Unicode Bidirectional Algorithm**, last revised **2025** (was 2014 / 2018 / 2020 / 2024 in earlier revisions). bidi-js and python-bidi 0.6.11 ship the 2014 revision; needs explicit upgrade for current behavior.
- **UAX #15 — Unicode Normalization Forms** (NFC / NFD / NFKC / NFKD). Stable, but cite `UAX #15`.
- **UAX #29 — Unicode Text Segmentation** (grapheme clusters, tashkeel grouping). Last revised **2024**.
- **UTS #39 — Unicode Security Mechanisms** (BiDi spoofing, confusables).
- **UTS #55 — Unicode Normalization Idempotence**.

Tashkeel clusters: shadda (U+0651) + vowel (U+064B/E/D) = one grapheme cluster per UAX #29 — naive regex stripping breaks these. python-bidi and arabic_reshaper libraries predate current revisions; verify against current UAX before relying on them in production.

### LLM-call skill auth blocker in Mavis instances (2026-07-07)
Type: gotcha
`~/.mavis/config.yaml` has `provider.minimax.options.apiKey: sk-xxx` as a literal placeholder in this Mavis instance. Any `mavis mcp call` style LLM invocation (or `llm-call/scripts/llm_call.py` with `--model minimax/MiniMax-M3`) POSTs to `https://agent.minimax.io/mavis/api/v1/llm/v1/chat/completions` with `Authorization: Bearer sk-xxx` and returns `401 auth failed`. No env var override exists; script reads apiKey from config.yaml only. Workarounds: (1) ask human maintainer to install a real minimax API key, (2) fall back to static rule trace + library byte-check for verification. Do NOT silently swap providers — surface the blocker honestly in the verification artifact.
