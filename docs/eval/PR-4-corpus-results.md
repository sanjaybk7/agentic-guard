# PR #4 — corpus scan results

Real-world A/B re-scan of the 9-repo corpus from PR #1/PR #2 validation,
after PR #4's src-layout symbol-table normalization landed. The corpus
and methodology are documented in `/tmp/ag_eval/SUMMARY.md` (corpus
list with shallow-clone URLs) and the design doc's §4.7.

## Methodology

The same `run_eval.py` harness used for PR #1 and PR #2 baselines:

```python
from agentic_guard.engine import Scanner
result = Scanner().scan(repo_path)  # default include_tests=False
```

Each repo was scanned once with PR #4 applied. Per-repo IG002 counts
compared against the PR #2 baseline captured in
`/tmp/ag_eval/results_pr2.json`. No repo was re-cloned between PR #2
and PR #4 — same SHAs, same file trees, only the analyzer changed.

## Per-repo IG002 deltas

| Repo | PR #1 baseline | PR #2 | PR #4 | Δ vs PR #2 | Note |
|---|---:|---:|---:|---:|---|
| openai-agents-python | 7 | 13 | **7** | **−6** | typed agents in `customer_service/main.py` now resolve `RECOMMENDED_PROMPT_PREFIX` cross-module |
| langgraph | 0 | 0 | 0 | 0 | unchanged |
| crewAI | 0 | 0 | 0 | 0 | unchanged |
| GenAI_Agents | 2 | 2 | 2 | 0 | unchanged |
| langchain-academy | 0 | 0 | 0 | 0 | unchanged |
| open_deep_research | 0 | 0 | 0 | 0 | unchanged |
| agents-towards-production | 3 | 3 | 3 | 0 | unchanged |
| openai-cookbook | 13 | 13 | 13 | 0 | unchanged — residuals are `load_prompt(...)` runtime file-load calls, correctly classified as findings, not FPs (see PR-5 corpus doc) |
| langchain (sparse) | 0 | 0 | 0 | 0 | unchanged |
| **TOTAL** | **25** | **31** | **25** | **−6** | |

## §4.8 acceptance criteria check

**Criterion 1:** *The openai-agents-python IG002 delta is approximately
−6 (±2 to accommodate minor measurement variance from re-cloning the
corpus on a different day).*

→ **Met.** Delta is exactly −6 (no measurement variance because the
corpus wasn't re-cloned).

**Criterion 2:** *Other repos' IG002 counts must not change.*

→ **Met.** All 8 non-SDK repos unchanged. The blast-radius scoping
hypothesis (`Agent[T]` and `RECOMMENDED_PROMPT_PREFIX` are
OpenAI-Agents-SDK-specific patterns) is confirmed for the third time
across PR #1, PR #2, and PR #4 scans.

## What the residual ~25 IG002 are

Per-finding inspection was completed during the PR #5 corpus A/B. The
full per-finding table is in `docs/eval/PR-5-corpus-results.md`. Summary:

- **True positives (parameter interpolation):** `{repo}` in
  `examples/hosted_mcp/simple.py:14`, `{directory_path}` in
  `examples/mcp/git_example/main.py:12`, `{step}` in
  `examples/memory/hitl_session_scenario.py:80` — real dynamic-prompt
  risk; IG002 correct.
- **True positives (`dedent(...)`):** `BENEFITS_PROMPT`,
  `ORCHESTRATOR_PROMPT`, `MEMORY_PROMPT` in
  `examples/sandbox/healthcare_support/support_agents.py` — `dedent()`
  is a function call; the prompt value is not statically knowable.
- **Ambiguous:** `examples/mcp/prompt_server/main.py:63` — `instructions`
  from an MCP call result; TP or FP depends on MCP server trust posture.
- **1 confirmed function-local-literal FP:** `examples/memory/file_hitl_example.py:50`
  — `instructions` bound to an implicit-concat string literal in function
  scope. Resolved by PR #5.
- **`openai-cookbook` (13):** `load_prompt(...)` runtime file-load calls —
  correctly classified as findings; prompts are not statically knowable.
- **`agents-towards-production` (3):** `ChatPromptTemplate` /
  `MessagesPlaceholder` LangGraph template objects — not string literals.
- **`GenAI_Agents` (2):** `self.X` class-attribute patterns — out of scope
  per design decision §3.

> **[Corrected]** An earlier revision of this document estimated
> "~16 function-local-literal-binding false positives" here. That estimate
> was category-level and unverified; it was not backed by per-finding
> inspection. The per-finding inspection above found the real count to be
> **1**. See `docs/eval/PR-5-corpus-results.md` for the full reconciliation.

## Cumulative deltas across PR #1, PR #2, PR #4

| Stage | Total IG002 | Δ from prior | Note |
|---|---:|---:|---|
| v0.1 baseline | 25 | — | pre-Fix-1 |
| Fix 1 (PR #1, cross-module resolution) | 25 | 0 | resolver added, but flat-layout target + corpus mismatch |
| PR #2 (`Agent[T]` recognition) | 31 | **+6** | unmasked 6 typed agents that PR #1 couldn't resolve due to src-layout indexing |
| PR #4 (src-layout normalization) | 25 | **−6** | the 6 unmasked agents now resolve through PR #1's cross-module resolver |

The net delta from v0.1 to post-PR-#4 is zero IG002 *count* but a
materially different *composition*: pre-Fix-1 the 25 included a number
of cross-module-import FPs that the analyzer simply couldn't see
past; post-PR-#4 the 25 excludes those (resolved) and includes the
typed-agent findings (now visible). The qualitative improvement
doesn't show up in totals because PR #2 surfaced as many findings as
PR #4 will eventually resolve. **The honest framing for v0.2 release
notes:** "PR #2 + PR #4 together restore the analyzer's view of the
OpenAI Agents SDK ecosystem (previously invisible due to typed-call
syntax) and resolve cross-module prompts within it (previously
unresolved due to src-layout indexing). The headline IG002 count is
unchanged because the two effects exactly cancel on this corpus —
that's why per-rule, per-repo, and per-finding labels matter more
than totals."

## Artifacts

- `/tmp/ag_eval/results_pr4.json` — full per-repo JSON output
- `/tmp/ag_eval/results_pr2.json` — PR #2 baseline for the diff above
- `/tmp/ag_eval/results_v01.json` — v0.1 baseline
- `/tmp/ag_eval/results_v02.json` — Fix 1 only

The PR #4 doc estimated a ~16 IG002 reduction once PR #5 landed, based on a
category-level count of "function-local-literal-binding FPs" across four
repos. **That estimate was wrong.** Per-finding inspection during the PR #5
corpus A/B (see `docs/eval/PR-5-corpus-results.md`) found that most of those
findings were not function-local string literals: `openai-cookbook`'s 13 are
`load_prompt(...)` calls, `agents-towards-production`'s 3 are LangGraph
template objects, `GenAI_Agents`'s 2 are `self.X` class-attribute patterns
(§3 carve-out), and `openai-agents-python`'s `dedent(...)` findings are
function calls per Python's AST. Only 1 confirmed function-local-literal FP
existed in the corpus; PR #5 resolved it. The actual reduction is −1
(drift-adjusted).
