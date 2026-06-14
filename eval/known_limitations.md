# Known Limitations — Analyzer v0.2

This file records false-positive patterns and known gaps identified during the evaluation.
The analyzer is **frozen** at v0.2 for the duration of the precision/recall evaluation.
Items here are candidates for post-eval rule refinements; they must NOT be fixed during
the evaluation so that the v0.2 precision measurement remains valid.

---

## KL-001 — BOTH-classified tools produce IG001 FP via single-tool co-membership

**Identified:** 2026-06-10, first IG001 labeling pass  
**Triggered by:** Finding #1 (`tonykipkemboi/crewai-gmail-automation`, `organizer` agent,
`GmailOrganizeTool`)  
**Label assigned:** FP

### Description

A tool classified as `BOTH` (source and sink) in `taxonomy.yaml` satisfies both
`Tool.is_source = True` and `Tool.is_sink = True` (`ir.py:75–80`). When an agent holds a
single `BOTH`-classified tool, the IG001 rule (`confused_deputy.py:31–33`) finds a
non-empty `sources` list and a non-empty `sinks` list — both populated by the same tool
— and fires.

This can produce a false positive when the tool's source-side behavior (what it returns
to the LLM) is a non-content status string rather than externally-authored data. Example:

```python
# GmailOrganizeTool._run() return value:
return f"Email organized: Starred={should_star}, Labels={labels}"
```

The return value is constructed entirely from the agent's own inputs. No externally-
authored text flows back to the LLM through this tool's output, so criterion (a) of the
labeling methodology is not met — yet the rule fires because the taxonomy classification
alone (BOTH → is_source) is treated as sufficient for co-membership.

### Impact

Any agent holding exactly one `BOTH`-classified tool with no other sources or sinks will
produce a spurious IG001 finding. In the v0.2 corpus scan, one such finding was produced.

### Candidate refinement (post-eval)

A `BOTH` tool should not satisfy co-membership with *itself* as both source and sink,
unless there is explicit evidence that its source-side output carries externally-
influenceable content. Possible approaches:

1. **Require a distinct source and sink:** IG001 fires only if `source_tool != sink_tool`
   (object identity or name check), even when a single tool is classified `BOTH`.
2. **Content-output check:** For `BOTH`-classified tools, inspect the return value (or
   docstring/description) for evidence that the tool returns externally-authored content
   vs. a status string. This requires heuristics.
3. **Taxonomy refinement:** For tools whose source-side behavior is exclusively
   write-confirmation (returns a status string, not content), use `SINK` rather than
   `BOTH`. Reserve `BOTH` for tools that both return external content AND take a
   privileged action (e.g., a DB tool that reads rows and can write rows).

**Do not implement during evaluation.** Log and fix post-v0.2.

---

## KL-002 — Callable instructions composing static strings from literal args flagged IG002

**Identified:** 2026-06-13, IG002 labeling pass (Batch 1)  
**Triggered by:** F01–F05 (`study8677/OpenCMO`, `build_prompt()`)  
**Label assigned:** FP (5 findings; 5/8 callable-stratum sample findings)

### Description

A helper callable that accepts only literal string keyword arguments and returns `str`
by concatenating module-level constants is flagged IG002 as having a dynamic system
prompt. The engine detects that the system prompt is the return value of a function call
and marks `system_prompt_is_dynamic=True`, but cannot determine that the callable's
return value is statically composed.

Example pattern (`OpenCMO/prompt_contracts.py`):

```python
def build_prompt(*, base_instructions: str, task_contract: str | None = None, ...) -> str:
    sections = [base_instructions, TRUTH_CONTRACT, ANTI_SLOP_GUARDRAILS, ...]
    return "\n\n".join(sections).strip() + "\n"

agent = Agent(instructions=build_prompt(base_instructions="You are..."))
```

The call site uses only literal string arguments; `build_prompt` returns only `str`.
The engine has no way to resolve this as static without analyzing the function body.

### Impact

5 of 8 callable-stratum sample findings are this pattern (the other 3 are
demo-data-conditional; see KL-note on F06–F08).

### Candidate refinement (post-eval)

For callables whose return type is `str`, whose function body composes only module-level
constants and literal string arguments, and whose call site provides only literal
arguments — treat the return value as a static string. Requires interprocedural analysis.

**Do not implement during evaluation.** Analyzer frozen at v0.2.

---

## KL-003 — `dedent(f"literal")` or `dedent("""literal""")` flagged as dynamic

**Identified:** 2026-06-13, IG002 labeling pass (Batch 2 / Batch 3)  
**Triggered by:** F15, F18 (`alexfazio/viral-clips-crew`), F39 (`alejandro-ao/crewai-crash-course`)  
**Label assigned:** FP (3 findings)

### Description

The taint extraction step identifies interpolated variable names from the call expression.
When the engine processes `role=dedent((f"""literal text"""))`, it sees `dedent` in the
call expression and treats it as a taint variable name (an interpolated identifier).

However, `dedent` is `textwrap.dedent` — a stdlib callable, not a data variable. The
f-string (or plain string) passed to `dedent` contains zero `{var}` interpolations.
There is no dynamic content whatsoever; the engine's taint extraction is incorrectly
treating the callable name as an interpolated variable.

F39 is even clearer: it uses a plain triple-quoted string (`dedent("""literal"""`), not
even an f-string — no syntactic ambiguity.

### Impact

3 findings in the sample (2 f-string stratum, 1 variable stratum). Likely a small
fraction of the population given how specific this pattern is.

### Candidate refinement (post-eval)

Filter recognized stdlib callable names (`dedent`, `strip`, `join`, etc.) from taint
extraction. Alternatively, only extract taint names from `{...}` interpolation positions,
not from outer call expressions.

**Do not implement during evaluation.** Analyzer frozen at v0.2.

---

## KL-004 — Module-level / cross-module / imported constant prompts flagged IG002

**Identified:** 2026-06-13, IG002 labeling pass (Batch 2 / Batch 3)  
**Triggered by:** F09, F11, F12, F13, F19, F20, F24, F25, F27, F30, F34, F38, F40, F41  
**Label assigned:** FP (13 findings directly; 18 total in "unresolved static" class when
combined with KL-002)

### Description

PR#5 extended literal-binding resolution for function-local variable assignments:
`x = "literal"; Agent(instructions=x)` → resolved as static. But several common
patterns remain unresolved:

1. **Cross-module import:** `from .prompts import SYSTEM_PROMPT` → engine cannot
   follow the import and see that `SYSTEM_PROMPT` is a module-level string literal.
   Examples: `RECOMMENDED_PROMPT_PREFIX` (OpenAI Agents SDK), `CODE_VALIDATION_PROMPT`
   (circuitron), `researcher_prompt` (langgraph-swarm research example).

2. **Dict subscript of literal dict:** `optimizations["quick_responses"]["instructions"]`
   where `optimizations` is a dict literal defined in the same scope.

3. **`.format()` with literal-only args:** `planner_prompt.format(llms_txt=LLMS_TXT,
   num_urls=NUM_URLS)` where both args are module-level literal constants.

4. **Ternary over literals:** `CODE_GENERATION_PROMPT if flag else CODE_GENERATION_PROMPT_NO_FOOTPRINT`
   where both branches are imported module constants.

5. **Loop variable over literal list:** `for role in ["Urban Planner", "Artist", ...]`
   where the list is a literal.

6. **Literal at call site (constructor param):** `ProductionAgent(instructions="literal")`;
   the engine sees `instructions` as a parameter variable rather than tracing back to
   the literal at the call site.

7. **Enum-ternary in f-string:** `{...if level==Enum.A else...}` where both branch
   values are string literals and all call sites pass hardcoded enum members.

### Impact

Largest IG002 FP class. 13 of 38 FPs are directly this pattern; 18 if KL-002
(unresolvable callable static composition) is included in the "unresolved static"
umbrella.

### Candidate refinement (post-eval)

Extend the PR#5 literal-binding resolution pass:
- (a) Follow `from mod import X` to the module's source and resolve module-level
  assignments.
- (b) Resolve `dict_literal["key"]` subscripts when the dict is a literal.
- (c) Resolve `.format(k=literal, ...)` calls when all named arguments are literals.
- (d) Resolve ternary `A if cond else B` as static when both `A` and `B` are literals
  (regardless of `cond`).
- (e) Resolve loop variable taints from literal list iterables.
- (f) Trace function parameter literals from known call sites (limited to single-file
  scope).

**Do not implement during evaluation.** Analyzer frozen at v0.2.
