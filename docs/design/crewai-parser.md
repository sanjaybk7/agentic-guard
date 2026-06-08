# Design: CrewAI Parser

**Status:** Draft — awaiting review before implementation  
**Branch:** `crewai-parser`  
**Date:** 2026-06-07

---

## 1. Scope & Recall Ceiling

### What this parser targets

The `CrewAIParser` will extract `ir.Agent` objects from Python source files that construct CrewAI `Agent(...)` objects directly in code — either through the `@CrewBase` / `@agent` decorator pattern or through plain class/function factory methods that call `Agent(...)`.

### Survey basis

8 repos from the eval corpus CrewAI set were inspected. Results:

| # | Repo | @CrewBase+@agent | tools= literal | Prompt location | Runtime-indirect |
|---|------|-----------------|----------------|-----------------|-----------------|
| C1 | tonykipkemboi/resume-optimization-crew | YES | YES (2/5 agents) | YAML | NO |
| C2 | NanGePlus/CrewAIFlowsFullStack | YES | YES | YAML | NO |
| C3 | yuriwa/crewai-sheets-ui | NO (factory fn) | NO (Sheets) | Sheets runtime | YES — fully |
| C4 | strnad/CrewAI-Studio | NO (custom class) | NO (DB) | DB runtime | YES — fully |
| C5 | bhancockio/crewai-updated-tutorial-hierarchical | NO (plain class) | YES (attr refs) | Inline literals | NO |
| C6 | alejandro-ao/crewai-instagram-example | YES | YES (1/4 agents) | YAML | NO |
| C7 | liangdabiao/crewai_stock_analysis_system | MIXED | MIXED | MIXED | PARTIAL |
| C8 | google-gemini/crewai-quickstart | YES | NO tools kwarg | YAML | NO |

### Recall ceiling

- **Detectable (5/8 = 62.5%):** Repos C1, C2, C5, C6, C8 — `Agent(...)` is in source, tools list is a literal or attribute reference.
- **Partially detectable (1/8 = 12.5%):** Repo C7 — some agents detectable, some tools are conditional/runtime lists.
- **Undetectable (2/8 = 25%):** Repos C3, C4 — agents and tools are fully runtime-indirect (Google Sheets, DB). No AST analysis can recover these.

The practical recall ceiling for `agent_count` on this corpus is **~62–75%**, with precision near 100% (we only emit what we can verify statically).

---

## 2. Detection Anchor

### File-level matching (`matches_file`)

A file matches if it imports from `crewai`:

```python
# All of these trigger a match:
from crewai import Agent
from crewai import Agent, Task, Crew
import crewai
from crewai.agents import Agent
```

Implementation: `collect_imports` returns a set; check for membership of `"crewai"` or any string starting with `"crewai."`.

### Agent-call detection (`visit_Call`)

Trigger on any `ast.Call` node where `call_base_name(node.func) == "Agent"` and the file-level import set contains a crewai import.

This covers three surface forms observed in the corpus:

1. **Direct call** (C5-style plain factory):
   ```python
   return Agent(role="Researcher", goal="...", tools=[...])
   ```

2. **`@agent`-decorated method** (C1/C2/C6/C8-style `@CrewBase`):
   ```python
   @agent
   def researcher(self) -> Agent:
       return Agent(config=self.agents_config['researcher'], tools=[...])
   ```
   The `@agent` decorator is registration metadata; the `Agent(...)` call is the AST node we detect.

3. **Attribute-qualified call** (unlikely but possible):
   ```python
   return crewai.Agent(role="...", tools=[...])
   ```
   `call_base_name` already strips attribute access, so `"Agent"` is returned for `crewai.Agent(...)`.

No new `visit_*` handlers are needed beyond `visit_Call`. The `@agent` decorator does not need to be detected; `Agent(...)` call detection is sufficient.

---

## 3. Tool Extraction

### Input forms in the corpus

All detected tools appear as a `tools=[...]` keyword argument to `Agent(...)`. Three element forms are observed:

| Form | AST type | Example | Seen in |
|------|----------|---------|---------|
| Class instantiation | `ast.Call` | `SerperDevTool()` | C1, C2, C6 |
| Attribute reference | `ast.Attribute` | `SearchTools.search_internet` | C5, C6 |
| Name reference | `ast.Name` | `search_tool` | (variable alias) |

The existing LangGraph `_extract_tool_names` handles `ast.Name` and `ast.Attribute` but **not** `ast.Call`. A new helper (or an extended version) must handle the `ast.Call` case by calling `call_base_name(elt.func)` to recover the class name (e.g., `"SerperDevTool"`).

### Extraction algorithm

```
for elt in tools_list.elts:
    if isinstance(elt, ast.Name):
        yield elt.id
    elif isinstance(elt, ast.Attribute):
        yield elt.attr
    elif isinstance(elt, ast.Call):
        yield call_base_name(elt.func)   # "SerperDevTool()" → "SerperDevTool"
    # else: skip (runtime-indirect, starred unpack, etc.)
```

Emit each recovered name as an `ir.Tool` with classification from `taxonomy.yaml`. If the name is not in the taxonomy, classify as `NEUTRAL` (same behavior as existing parsers).

### Config-only agents (`config=self.agents_config[...]`)

Repos C1, C2, C6, C8 pass `config=self.agents_config['key']` to Agent. When `tools=` is also present, extract it as above. When `tools=` is absent (C8-style), emit the agent with an empty tool list — the agent still counts toward `agent_count`.

### Taxonomy gaps

The following CrewAI built-in tool class names appear in the corpus but have **no taxonomy entries**:

| Class name | Observed in | Expected classification |
|------------|------------|------------------------|
| `SerperDevTool` | C1, C2, C6 | SOURCE (web search, privilege=0, trust_of_output=untrusted) |
| `ScrapeWebsiteTool` | C1, C2 | SOURCE (web scrape, privilege=0, trust_of_output=untrusted) |

These will be classified `NEUTRAL` until taxonomy entries are added. Adding them is out of scope for this parser PR — they belong in a separate taxonomy PR. This is an open question for the reviewer (see §8).

---

## 4. System Prompt / IG002 Mapping

### CrewAI's prompt model

CrewAI agents do not have a `system_prompt=` constructor argument. The agent's behavioral framing comes from three fields:

- `role`: a short string (e.g., `"Senior Financial Analyst"`)
- `goal`: a sentence describing the agent's objective
- `backstory`: a paragraph giving the agent context and persona

When the `@CrewBase` / YAML pattern is used, all three come from `config=self.agents_config['key']` which reads `config/agents.yaml`. This YAML is loaded at runtime but is always a static file — no f-string, no `.format()`, no concatenation possible inside the YAML loader.

**Result: `system_prompt_is_dynamic = False` for all YAML-backed agents.**

### Inline literal case (C5-style)

When role/goal/backstory are passed as inline string literals, they are also always static:

```python
Agent(role="Researcher", goal="Find market data", backstory="You are...")
```

**Result: `system_prompt_is_dynamic = False`.**

### Hypothetical dynamic case

If a repo were to pass an f-string or concatenated string:

```python
Agent(role=f"Analyst for {company}", goal=..., backstory=...)
```

`classify_prompt_expr` applied to the `role`, `goal`, or `backstory` keyword arguments would return `True`. Set `system_prompt_is_dynamic = True` and populate `system_prompt_taint_sources` accordingly.

### Implementation

Inspect `role`, `goal`, `backstory` kwargs on the `Agent(...)` call node. Run each through `classify_prompt_expr`. Set `system_prompt_is_dynamic = True` if any returns `True`. Record `system_prompt_location` as the file+line of the `Agent(...)` call.

For YAML-backed agents where all three come from `config=...`, set `system_prompt_is_dynamic = False` without inspecting the YAML file (static by construction).

---

## 5. Emit Tool-less Agents

Agents with no `tools=` kwarg (C8: `google-gemini/crewai-quickstart`) and agents where tools are runtime-indirect but the `Agent(...)` call is still in source (partial C7 case) should still be emitted as `ir.Agent` objects.

- `tools: list[Tool]` → empty list `[]`
- `system_prompt_is_dynamic` → evaluated from role/goal/backstory as above
- Agent still increments `result.agents_seen`

This matters for corpus `agent_count` accuracy: currently 0 for all crewai repos because no parser runs. After this parser, config-only and tool-less agents will be counted.

---

## 6. IR Changes

**None required.**

The existing `ir.Agent` dataclass fields cover all data this parser will produce:

| Field | Source in CrewAI |
|-------|-----------------|
| `name` | Method name (for `@agent` methods) or synthetic `"agent_N"` |
| `location` | File + line of the `Agent(...)` call node |
| `framework` | `"crewai"` |
| `tools` | Extracted from `tools=[...]` kwarg |
| `system_prompt_location` | File + line of `Agent(...)` call |
| `system_prompt_is_dynamic` | From role/goal/backstory classification |
| `system_prompt_taint_sources` | From `classify_prompt_expr` |
| `interrupts_before` | `[]` (not applicable in v1) |
| `interrupts_after` | `[]` (not applicable in v1) |

The `framework` field will use the string `"crewai"` (matches the corpus tag).

### Agent name heuristic

For `@agent`-decorated methods, the method name is a good proxy for the agent's logical name:

```python
@agent
def researcher(self) -> Agent:   # name = "researcher"
    return Agent(...)
```

For plain factory functions or class methods without `@agent`, use the containing function/method name if available, otherwise `"agent_N"` with N as a counter.

---

## 7. Gates

**`human_input_mode` is out of scope for v1.**

CrewAI's `Agent` has a `human_input` boolean (`human_input=True`) that pauses the agent for human confirmation before tool execution. This would be the natural IG001 gate for CrewAI agents.

Reasons to defer:

1. None of the 8 surveyed repos set `human_input=True` — it is uncommon in open-source examples.
2. The IG001 rule's gate interface (`interrupts_before`, `interrupts_after`) is designed for LangGraph's `interrupt_before`/`interrupt_after` checkpointing semantics, which differ from CrewAI's `human_input` flag semantics.
3. Adding gate suppression requires deciding how to surface `human_input` in `ir.Agent` — a cross-cutting change better addressed after the parser baseline is established.

**v1 behavior:** IG001 fires whenever a CrewAI agent has ≥1 SOURCE tool and ≥1 SINK tool, regardless of `human_input`. This is conservative (may over-fire on repos that use `human_input=True`). The count is expected to be small given corpus observation.

---

## 8. Open Questions

The following require explicit decisions before or during implementation:

**Q1 — Taxonomy additions for CrewAI built-in tools**  
`SerperDevTool` and `ScrapeWebsiteTool` appear in 3/8 repos. Until taxonomy entries exist, IG001 cannot fire on CrewAI agents using only these tools (they're classified NEUTRAL). Should taxonomy additions be bundled into this parser PR or handled as a separate follow-on?

**Q2 — YAML file inspection**  
Should the parser open and parse `config/agents.yaml` to extract the agent name (key), role, goal, backstory for richer IR? This would improve agent name accuracy and enable IG002 detection on hypothetical dynamic YAML (not observed in corpus). Cost: additional file I/O and YAML parsing complexity. Recommendation: skip for v1 (static YAML is never dynamic; names are inferable from method names).

**Q3 — `config=` argument handling for tool extraction**  
When `Agent(config=self.agents_config['researcher'], tools=[SearchTool()])` is called, `tools=` is separately provided and extractable. When only `config=` is provided with no `tools=`, should the parser look up the YAML key for a `tools:` list? Recommendation: no — YAML tool lists in CrewAI are rarely populated and would require resolving tool names from YAML strings, which is a different classification surface.

**Q4 — `agent_N` naming for non-decorated agents**  
For plain factory methods (C5-style), the containing method name is used as the agent name. Is this sufficient, or should the parser attempt to extract the `role=` string value as the canonical name? `role=` is always a string literal in the non-YAML case, so this is cheap. Recommendation: use `role=` string value when present, fall back to method name.

**Q5 — Scope of `matches_file`**  
Should `matches_file` also match files that contain `from crewai.agents.agent import Agent` or other deep import paths? The current proposal (any import containing `"crewai"`) covers this. Confirm this is the intended behavior before implementation.
