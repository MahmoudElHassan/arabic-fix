# Verification · Case 1 — terminal `print(fix('السلام عليكم'))`

## Spliced system prompt

**Section used:** `B · Write Arabic` (from `agents/system_prompt.md`,
version 0.2.0). Standalone paste-able; matches the "When to splice this
in" tag (agent that emits Arabic to a non-Web target — terminal).

The full Section B text is 80 lines. Key rules that apply to this case:

- B.1 — Honor letter shaping. Non-Web targets do not auto-shape; pipe
  through `arabic_fix.fix()`.
- B.1 example block shows exactly the `from arabic_fix import fix; msg =
  fix("السلام عليكم"); print(msg)` shape.
- B.3 self-check #4: "If target is non-Web, have I told the caller to pipe
  through `arabic_fix.fix()`?"

## User prompt (the eval case input)

> Write a Python `greet()` function that prints `السلام عليكم` to the
> terminal. Run on macOS, Python 3.12.

## Expected output (from eval_cases.md Case 1)

```python
from arabic_fix import fix

def greet() -> None:
    msg = fix("السلام عليكم")     # shape + BiDi + normalize
    print(msg)
```

## Real LLM run?

**No — auth blocker.** `~/.mavis/config.yaml` has
`provider.minimax.options.apiKey: sk-xxx` (literal placeholder). The
`llm-call` script POSTs to
`https://agent.minimax.io/mavis/api/v1/llm/v1/chat/completions` with
`Authorization: Bearer sk-xxx` and gets back
`{"code":401,"message":"auth failed"}`. No LLM endpoint is reachable
from this Mavis instance without a real token being installed in
config.yaml by the human maintainer.

## Static rule trace (what a model following Section B would emit)

A model that reads Section B and the prompt would, step by step:

1. Read the prompt → target = terminal (macOS, Python 3.12). Section B
   applies (B.1 first sentence: "Every Arabic word you write to a
   non-Web target MUST be in presentation form").
2. Hit B.1 example block → exact code shape `from arabic_fix import fix;
   print(fix("..."))`.
3. Pass B.3 self-check #4 → ✅ mentions `fix()`.
4. Emit the expected code shape above.

**Predicted output:** matches the expected output (model follows the
example block verbatim because it's the canonical pattern).

## Real-byte verification (independent of LLM)

Ran the exact code shape from the expected output through the actual
library on this machine:

```
$ python3 -c "from arabic_fix import fix; print(repr(fix('السلام عليكم')))"
'ﻢﻜﻴﻠﻋ ﻡﻼﺴﻟﺍ'
```

Codepoints: `0xFEE2, 0xFEDC, 0xFEF4, 0xFEE0, 0xFECB, 0x20, 0xFEE1,
0xFEFC, 0xFEB4, 0xFEDF, 0xFE8D`. Every Arabic codepoint is in
U+FE70–U+FEFF (Presentation Forms-B). One space (0x20) is between the
two words, as expected. **Library works.**

## Verdict

**PASS** on the rule-trace + real-library dimension.
**NOT RUN** on real-LLM-call dimension (auth blocker above).

## To turn this into a real LLM run

1. Replace `sk-xxx` in `~/.mavis/config.yaml` line 72 with a real
   `minimax` API key (request from human maintainer / Mavis provider).
2. Re-run:
   ```bash
   python3 .mavis/.builtin-skills/llm-call/scripts/llm_call.py \
     --model minimax/MiniMax-M3 \
     --system "$(cat /tmp/section_b.md)" \
     --max-tokens 500 --temperature 0.2 \
     --prompt "Write a Python greet() function that prints 'السلام عليكم' to the terminal. Run on macOS, Python 3.12. Output ONLY the Python code, no prose."
   ```
3. Diff the output against `expected_code_or_output` above. If the model
   emits the `from arabic_fix import fix; print(fix(...))` shape, this
   case flips to **PASS (real LLM)**.