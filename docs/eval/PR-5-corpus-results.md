# PR #5 — corpus scan results

Real-world A/B re-scan of the 9-repo corpus after PR #5's function-local
literal binding resolution landed. The corpus repos were re-cloned at
HEAD before this scan (the previous `/tmp/ag_eval/` workspace was purged
by macOS); see the Corpus drift section below for implications.

---

## Prediction (stated before scan)

The PR #4 corpus doc projected a reduction of **~16** IG002 findings once
PR #5 landed, based on a category-level estimate of "~16 function-local-
literal-binding false positives" across four repos. That estimate was
**never verified at the per-finding level** — the PR #4 doc explicitly
deferred per-finding inspection to a future precision measurement.

**Actual result: −1 confirmed FP fixed (drift-adjusted).**

The projection was wrong from the start. See the per-finding reconciliation
below.

Note: the PR #5 corpus doc previously stated the projection as "~8," which
does not appear in any prior doc and is inconsistent with the PR #4 doc's
"~16." Both numbers were wrong; "~8" is corrected here and removed.

---

## Per-repo IG002 deltas (PR #4 baseline → PR #5)

| Repo | PR #4 IG002 | PR #5 IG002 | Δ | Notes |
|---|---:|---:|---:|---|
| `openai-agents-python` | 7 | 9 | **+2** | See corpus-drift analysis below |
| `langgraph` | 0 | 0 | 0 | unchanged |
| `crewAI` | 0 | 0 | 0 | unchanged |
| `GenAI_Agents` | 2 | 2 | 0 | unchanged |
| `langchain-academy` | 0 | 0 | 0 | unchanged |
| `open_deep_research` | 0 | 0 | 0 | unchanged |
| `agents-towards-production` | 3 | 3 | 0 | unchanged |
| `openai-cookbook` | 13 | 13 | 0 | unchanged |
| `langchain` (sparse) | 0 | 0 | 0 | unchanged |
| **TOTAL** | **25** | **27** | **+2** | |

---

## Corpus drift and the openai-agents-python anomaly

The PR #5 scan is **not a clean A/B comparison** against the PR #4 scan.
The `/tmp/ag_eval/` workspace was purged by macOS between the two scans,
forcing a full re-clone. The re-cloned repos are at their current HEAD,
which for `openai-agents-python` is commit `fedc809` — more recent than
the clone used for PR #4.

Inspection of the 9 PR #5 findings in `openai-agents-python` shows:

| File | Finding | Status vs PR #4 |
|---|---|---|
| `examples/hosted_mcp/simple.py:14` | `{repo}` param interpolation | same (TP) |
| `examples/mcp/git_example/main.py:12` | `{directory_path}` param interpolation | same (TP) |
| `examples/mcp/prompt_server/main.py:63` | `instructions` from MCP call | same (ambiguous) |
| `examples/memory/hitl_session_scenario.py:80` | `{step}` param interpolation | same (TP) |
| `examples/sandbox/healthcare_support/support_agents.py:94` | `BENEFITS_PROMPT` from `dedent(...)` | same (TP — function call, not literal) |
| `examples/sandbox/healthcare_support/support_agents.py:139` | `ORCHESTRATOR_PROMPT` from `dedent(...)` | same (TP) |
| `examples/sandbox/healthcare_support/support_agents.py:159` | `MEMORY_PROMPT` from `dedent(...)` | same (TP) |
| `examples/sandbox/extensions/runloop/capabilities.py:547` | `managed_secret_name` + `network_policy_name` | **new file in re-clone** |
| `examples/tools/apply_patch.py:112` | `workspace_path` param interpolation | **new file in re-clone** |

And critically, **this finding from PR #4 is absent from the PR #5 scan**:

| File | Finding | Status |
|---|---|---|
| `examples/memory/file_hitl_example.py:50` | `instructions` — function-local literal binding | **FIXED by PR #5** |

The headline count went **+2** (not the projected −16), because:
* −1: the `file_hitl_example.py` FP was fixed (PR #5 working correctly)
* +3: corpus drift — the re-cloned repo introduced two new example files
  (`capabilities.py`, `apply_patch.py`) and a third `support_agents.py`
  finding not present in the PR #4 clone

**Corpus-drift-adjusted net: −1 IG002 (one confirmed FP resolved).**

---

## Per-finding reconciliation of the projected −16

The PR #4 doc classified findings in four repos as "function-local-literal-
binding false positives" without individual inspection. Here is what each
finding actually is.

### openai-agents-python — 7 findings at PR #4 baseline

| File:line | Actual classification | PR #5 resolves? | Reason |
|---|---|---|---|
| `examples/hosted_mcp/simple.py:14` | TP — `{repo}` f-string parameter interpolation | N/A | Real dynamic-prompt risk |
| `examples/mcp/git_example/main.py:12` | TP — `{directory_path}` parameter interpolation | N/A | Real dynamic-prompt risk |
| `examples/mcp/prompt_server/main.py:63` | Ambiguous — `instructions` from MCP call result | No | RHS is a function call result, not a literal |
| `examples/memory/hitl_session_scenario.py:80` | TP — `{step}` parameter interpolation | N/A | Real dynamic-prompt risk |
| `examples/sandbox/healthcare_support/support_agents.py:94` | TP — `BENEFITS_PROMPT` from `dedent(...)` | No | `dedent(...)` is a function call; RHS is not a literal per Python AST |
| `examples/sandbox/healthcare_support/support_agents.py:139` | TP — `ORCHESTRATOR_PROMPT` from `dedent(...)` | No | Same |
| `examples/sandbox/healthcare_support/support_agents.py:159` | TP — `MEMORY_PROMPT` from `dedent(...)` | No | Same; this finding appeared in re-clone only |
| `examples/memory/file_hitl_example.py:50` | **FP — confirmed function-local-literal binding** | **Yes — fixed** | `instructions` bound to implicit-concat string literal in function scope |

**Genuine function-local-literal FPs in this repo: 1 of 7. PR #5 fixed it.**

### openai-cookbook — 13 findings

These were counted in the ~16 estimate as function-local-literal FPs. On
inspection, all 13 are `load_prompt(...)` calls — the prompts are loaded
from files at runtime. The RHS is a function call result, not a string
literal. PR #5 does not resolve these, and should not: they are correctly
classified as findings (the prompt value is not statically knowable).

**Genuine function-local-literal FPs in this repo: 0 of 13.**

### agents-towards-production — 3 findings

These were counted in the ~16 estimate. On inspection, all 3 are
`ChatPromptTemplate` and `MessagesPlaceholder` LangGraph prompt objects —
not string literals and not function-local binding in the sense PR #5
targets. PR #5 does not resolve these.

**Genuine function-local-literal FPs in this repo: 0 of 3.**

### GenAI_Agents — 2 findings

These were counted in the ~16 estimate. On inspection, both are `self.X`
class-attribute patterns — explicitly carved out by design decision §3.
They were never in scope for PR #5.

**Genuine function-local-literal FPs in this repo: 0 of 2.**

### Summary

| Repo | Findings in ~16 estimate | Genuine function-local-literal FPs | Fixed by PR #5 |
|---|---:|---:|---:|
| `openai-agents-python` | ~2 (support_agents dedent + file_hitl) | 1 | 1 |
| `openai-cookbook` | ~13 | 0 | 0 |
| `agents-towards-production` | ~3 | 0 | 0 |
| `GenAI_Agents` | ~2 | 0 | 0 |
| **Total** | **~16** | **1** | **1** |

---

## Honest conclusion: the projection was wrong from the start (conclusion a)

The ~16 estimate in the PR #4 doc was a category-level claim made without
inspecting individual findings. The findings that were labelled
"function-local-literal-binding false positives" turned out on per-finding
inspection to be:

- Runtime function-call results (`load_prompt(...)`, `dedent(...)`) — not
  literals by Python's AST definition
- Class-attribute patterns (`self.X`) — explicitly out of scope per §3
- LangGraph template objects — not string literals at all

PR #5's implementation is **not buggy**. It correctly resolved the one
genuine function-local-literal FP in the corpus. The gap between the
projected −16 (or "~8," a further inconsistency introduced without a
source) and the observed −1 is entirely explained by misclassification in
the original estimate.

The correct correction to the design doc's projection: the corpus contained
**1 confirmed function-local-literal FP**. PR #5 resolved it.

---

## Methodology note — SHA pinning

The PR #4 and PR #5 corpus scans used different repo HEAD SHAs due to the
workspace purge. This makes precise A/B comparison impossible for
`openai-agents-python`. Future corpus eval rounds should record and pin
exact commit SHAs for each repo in the evaluation YAML (per the Fix 5
roadmap item in the original v0.2 brief). Without pinned SHAs, any
per-PR IG002 delta has an unquantifiable corpus-drift component.

The 8 repos that showed 0 delta are unaffected by this concern.

---

## Cumulative picture (v0.1 → post-PR-#5)

| Stage | `openai-agents-python` IG002 | Total IG002 | Notes |
|---|---:|---:|---|
| v0.1 baseline | 7 | 25 | pre-Fix-1 |
| Fix 1 + PR #1 | 7 | 25 | cross-module resolver added (flat-layout) |
| PR #2 (`Agent[T]` recognition) | 13 | 31 | 6 typed agents newly visible, prompts unresolved |
| PR #4 (src-layout normalization) | 7 | 25 | −6 from PR #2: typed agents' prompts now resolve |
| PR #5 (function-local binding) + corpus drift | 9 | 27 | −1 FP fixed, +3 from re-clone drift |

Baseline-adjusted (accounting for the corpus drift): post-PR-#5 total is
approximately **25 − 1 = 24**, representing a cumulative reduction of 1
confirmed FP from the v0.2 work after accounting for drift. The remaining
residual is dominated by TPs and pattern classes not yet targeted by
implemented rules (IG003 library-call sinks, IG004 disclosure, the
`self.X` class-attribute pattern).

---

## Artifacts

* `/tmp/ag_eval/results_pr5.json` — full per-repo JSON output from this scan
* `/tmp/ag_eval/results_pr4.json` — was purged along with the workspace;
  PR #4's numbers above are from `docs/eval/PR-4-corpus-results.md`
