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
