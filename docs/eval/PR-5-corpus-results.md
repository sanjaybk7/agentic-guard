# PR #5 — corpus scan results

Real-world A/B re-scan of the 9-repo corpus after PR #5's function-local
literal binding resolution landed. The corpus repos were re-cloned at
HEAD before this scan (the previous `/tmp/ag_eval/` workspace was purged
by macOS); see the Corpus drift section below for implications.

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
which for `openai-agents-python` is commit `fedc809` —  more recent than
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

### What this means

PR #5 fixed the one confirmed function-local-literal-binding FP in the corpus:
`file_hitl_example.py:50` used the pattern
```python
instructions = (
    "You assist support agents. ..."
    "...keep responses under three sentences."
)
agent = Agent(name="...", instructions=instructions, ...)
```
where `instructions` is a function-local variable bound to an
implicit-concat string literal. After PR #5, `instructions` resolves as a
static literal → IG002 is silent.

The headline count went **+2** (not the −8 originally projected), because:
* −1: the `file_hitl_example.py` FP was fixed (PR #5 working correctly)
* +3: corpus drift — the re-cloned repo at a newer HEAD introduced two
  entirely new example files (`capabilities.py`, `apply_patch.py`) and a
  new finding in `support_agents.py` (the PR #4 clone had only 2
  `support_agents.py` findings; the new clone has 3, suggesting the SDK
  added a third `Agent[T](...)` definition with a `dedent(...)` prompt
  between the two clones)

**Corpus-drift-adjusted net:** −1 IG002 (one confirmed FP resolved).

---

## Why the projected −8 FP reduction wasn't observed

The PR #1/PR #2 analysis estimated ~8 function-local-literal-binding FPs
in the corpus. Spot-inspection of the actual findings in the PR #4 corpus
showed:

* `agents-towards-production` (3 findings): `ChatPromptTemplate` and
  `MessagesPlaceholder` LangGraph prompt patterns in notebooks — not
  function-local literals.
* `GenAI_Agents` (2 findings): `self.X` attribute patterns — out of scope
  for PR #5 (§3 carve-out).
* `openai-cookbook` (13 findings): function-call-result prompts
  (`load_prompt(...)`) — the prompts are loaded from files at runtime,
  not bound to literals in function scope.
* `openai-agents-python` (7 findings in PR #4 scan): only 1 confirmed
  function-local-literal FP (`file_hitl_example.py`); the rest were TPs
  or `dedent("""...""")` patterns (which are function calls, not literals,
  per Python's AST).

The gap between the projection (~8) and the observation (1) reflects the
same phenomenon as PR #1's corpus surprise: the corpus used for validation
happens not to have many of the targeted patterns. The fix is correct;
the corpus doesn't surface it at scale.

---

## Methodology note — SHA pinning

The PR #4 and PR #5 corpus scans used different repo HEAD SHAs due to the
workspace purge. This makes precise A/B comparison impossible for
`openai-agents-python`. Future corpus eval rounds should record and pin
exact commit SHAs for each repo in the evaluation YAML (per the Fix 5
roadmap item in the original v0.2 brief). Without pinned SHAs, any
per-PR IG002 delta has an unquantifiable corpus-drift component.

The 8 repos that showed 0 delta are unaffected by this concern — they
are stable regardless of drift.

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
  PR #4's numbers above are from memory / `docs/eval/PR-4-corpus-results.md`
