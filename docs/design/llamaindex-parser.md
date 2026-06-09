# LlamaIndex Parser Design

Branch: `llamaindex-parser`  
Status: design — no fixtures or implementation yet

---

## §1 Scope and motivation

LlamaIndex agents appear in the zero-agent remainder of the corpus as a detectable
pattern. Pre-implementation investigation (6 repos; 4 agent-defining) showed that
the dominant construction forms are static and co-located — tools are passed as
a literal list at the constructor in 3 of 4 agent-defining repos. This makes
LlamaIndex a **constructor-co-located parser** (same class as CrewAI), not a
runtime-indirect one (like AutoGen/StateGraph).

The parser is expected to be smaller than the CrewAI parser.

---

## §2 File match

A file matches if it imports from `llama_index`:

```python
collect_imports(tree)  # returns set of dotted module paths
# match: imp == "llama_index" or imp.startswith("llama_index.")
```

Examples that match:
- `from llama_index.core.agent import ReActAgent`
- `from llama_index.core.agent.workflow import FunctionAgent`
- `from llama_index.agent.openai import OpenAIAgent`
- `import llama_index`

---

## §3 Detection anchors

LlamaIndex has two distinct construction forms. Both must be supported. A third
form (AgentWorkflow) is a deliberate exclusion.

### §3.1 Classmethod form — `X.from_tools(...)`

```python
agent = ReActAgent.from_tools(tools=[...], llm=..., verbose=True)
agent = OpenAIAgent.from_tools(tools=[tool], llm=..., ...)
```

**Receiver classes** (the set `_FROM_TOOLS_CLASSES`):
- `ReActAgent` — `llama_index.core.agent`
- `OpenAIAgent` — `llama_index.agent.openai`
- `FunctionCallingAgent` — `llama_index.core.agent` (less common; included for completeness)

**Critical correctness point — why matching on method name alone is wrong:**

`call_base_name(node)` for `ReActAgent.from_tools(...)` returns `"from_tools"` (the
`ast.Attribute.attr` value). Any library could expose a `from_tools` factory. Matching
on `"from_tools"` alone would fire on unrelated code and produce false positives at
corpus scale.

The correct predicate is:

```python
def _is_from_tools_agent_call(node: ast.Call) -> bool:
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "from_tools"
        and isinstance(func.value, ast.Name)
        and func.value.id in _FROM_TOOLS_CLASSES
    )
```

Both conditions (`attr == "from_tools"` AND `func.value.id` in the receiver set) must
hold in the same predicate.

### §3.2 Constructor form — `FunctionAgent(...)`

```python
browser_agent = FunctionAgent(
    name="BrowserAgent",
    system_prompt="You are a web browsing agent ...",
    tools=[navigate_to, click_element, search_text],
    ...
)
```

`call_base_name(node)` returns `"FunctionAgent"`. This is a straightforward callee-name
match, identical to CrewAI's `"Agent"` match.

**Constructor classes** (the set `_CONSTRUCTOR_CLASSES`):
- `FunctionAgent` — `llama_index.core.agent.workflow`

### §3.3 AgentWorkflow — deliberate exclusion

```python
agent_workflow = AgentWorkflow(agents=[browser_agent, analysis_agent], ...)
```

`AgentWorkflow` is an orchestrator that references already-detected `FunctionAgent`
instances by variable name. Detecting it as its own agent would double-count agents
the parser already found via their `FunctionAgent(...)` constructors.

**Do not anchor on `AgentWorkflow`.** If handoff-graph analysis is added later, it
is a separate feature that reads already-detected agents rather than emitting new ones.

---

## §4 Tool extraction

### §4.1 Finding the tool list — positional AND keyword

CrewAI only passed tools as a keyword arg (`tools=[...]`). LlamaIndex `from_tools`
uses **both** forms in real code:

```python
# keyword form (AstraBert, NetEase-Media)
agent = ReActAgent.from_tools(tools=[router_tool, web_search_tool], ...)

# positional form (Andrew-Tsegaye)
agent = ReActAgent.from_tools(tools_var, llm=..., verbose=True)
```

The extractor must check both:

```python
def _find_tools_arg(node: ast.Call) -> ast.expr | None:
    # Priority 1: tools= keyword arg
    for kw in node.keywords:
        if kw.arg == "tools":
            return kw.value
    # Priority 2: first positional arg (from_tools convention)
    if node.args:
        return node.args[0]
    return None
```

This applies to both classmethod and constructor forms (FunctionAgent also uses
`tools=` keyword; the positional path is a no-op for it in practice).

### §4.2 Tool list element forms

Same three cases as the CrewAI extractor — observed in the corpus:

| Form | Example | Extraction |
|------|---------|-----------|
| `ast.Name` | `tools=[navigate_to, web_search_tool]` | `elt.id` |
| `ast.Attribute` | `tools=[SearchTools.fetch]` | `elt.attr` |
| `ast.Call` | `tools=[FunctionTool.from_defaults(fn)]` | `call_base_name(elt)` |

All three forms are represented in the surveyed corpus. The `ast.Name` form dominates
(bare function references, variable-bound `FunctionTool`/`QueryEngineTool` results).

### §4.3 Tool list not a literal — no-tool emission

If `_find_tools_arg` returns a node that is not `ast.List | ast.Tuple | ast.Set`,
the agent is still emitted with `tools=[]`. Do not attempt further tracking. This is
the same discipline as CrewAI's runtime-indirect handling.

---

## §5 System prompt / IG002

LlamaIndex agents pass system context via two distinct kwargs depending on API
version:

### §5.1 `system_prompt=` (FunctionAgent, preferred path)

```python
FunctionAgent(
    system_prompt="You are a web browsing agent ...",
    ...
)
```

Classify via `classify_prompt_expr(kw.value, module=module_ctx)`. Follows the same
static/dynamic logic as CrewAI's `role`/`goal`/`backstory` fields.

### §5.2 `chat_history=` with a system ChatMessage (from_tools, secondary path)

```python
chat_history = [ChatMessage.from_str("You are a useful assistant...", role="system")]
agent = ReActAgent.from_tools(tools=[...], chat_history=chat_history, ...)
```

The system content is not at the constructor call site — it is in the `chat_history`
variable assembled above. Static resolution would require tracing the `chat_history`
binding to its assignment and then inspecting the first `ChatMessage` element. This
is non-trivial for a first-pass parser.

**Decision**: defer `chat_history=` system-prompt analysis to a follow-on PR. In v1:
- If `system_prompt=` kwarg is present, classify it.
- If only `chat_history=` is present (no `system_prompt=`), emit `system_prompt_is_dynamic=False` and `system_prompt_location=None` — document this as a known gap, not a bug.

**Open question (§8.1)**: Is the `chat_history=` IG002 gap worth closing in v1 or
deferred? The corpus shows it in `from_tools` agents only; `FunctionAgent` (newer API)
uses `system_prompt=` directly.

---

## §6 Name resolution

Priority order (first match wins):

1. **`name=` kwarg literal string** — `FunctionAgent(name="BrowserAgent", ...)` → `"BrowserAgent"`
2. **Synthetic** — `agent_N` (counter-incremented per file)

There is no `role=` equivalent in LlamaIndex. No method-name or config-key fallback
is needed: `FunctionAgent` always passes an explicit `name=`; `from_tools` agents have
no name kwarg at all in the observed corpus.

---

## §7 IR fit

No IR changes needed. `ir.Agent` fields map as follows:

| `ir.Agent` field | LlamaIndex source |
|-----------------|------------------|
| `name` | `name=` kwarg literal, else `agent_N` |
| `framework` | `"llama-index"` |
| `location` | `(file, node.lineno, node.col_offset)` |
| `tools` | extracted from `tools=` kwarg or `node.args[0]` |
| `system_prompt_location` | location of `system_prompt=` kwarg value |
| `system_prompt_is_dynamic` | from `classify_prompt_expr` on `system_prompt=` value |
| `system_prompt_taint_sources` | taint names from `classify_prompt_expr` |
| `interrupts_before` | `[]` (no equivalent in LlamaIndex) |
| `interrupts_after` | `[]` |

---

## §8 Open questions

### §8.1 `chat_history=` system-prompt path (v1 gap)

`from_tools` agents pass system context via `chat_history=[ChatMessage.from_str("...", role="system")]`.
Resolving this statically requires local-variable tracking (the variable is assembled
before the call, not inline). v1 defers this — `system_prompt_is_dynamic=False` is
emitted with a gap note. The corpus showed 2 instances (both AstraBert docker/scripts
variants of the same file; the system text is a literal, so missing it loses an IG002
signal but never produces a false positive).

Defer to a follow-on PR once corpus scan confirms whether the gap is material.

### §8.2 `FunctionCallingAgent` prevalence

`FunctionCallingAgent` is listed in `_FROM_TOOLS_CLASSES` based on LlamaIndex
documentation; it was not observed in the 4 surveyed repos. Its AST form is identical
to `ReActAgent.from_tools` — add it to the receiver set at zero marginal cost and
confirm or remove after the corpus scan.

### §8.3 Recall ceiling confidence

≈75% tool detection on 4 agent-defining repos surveyed. Small denominator — treat as
a provisional lower bound. The true figure comes from the corpus scan (≥25 repos),
not this survey. The design doc reports it here to avoid citing it as a hard fact.

---

## §9 Corpus evidence — quoted construction sites

All detection decisions above are grounded in real code observed during the
pre-design investigation.

**NetEase-Media/grps_trtllm** `client/llamaindex_ai_agent.py:35–40`:
```python
tool = FunctionTool.from_defaults(get_weather, name="get_weather", description="...")
agent = OpenAIAgent.from_tools(tools=[tool], verbose=True, max_function_calls=1,
                               allow_parallel_tool_calls=False, llm=llm)
```

**Andrew-Tsegaye/Advanced-AI-Code-Generation-Agent** `main.py:29–41`:
```python
tools = [
    QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="api_documentation", ...)),
    code_reader,
]
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, context=context)
```
← positional arg; tools= keyword missing at call site

**lesteroliver911/llamaindex-agentworkflow-browse-agent** `main.py:75–97`:
```python
browser_agent = FunctionAgent(
    name="BrowserAgent",
    system_prompt=("You are a web browsing agent that can navigate websites ..."),
    llm=llm,
    tools=[navigate_to, click_element, search_text, take_screenshot],
    can_handoff_to=["AnalysisAgent"],
)
analysis_agent = FunctionAgent(
    name="AnalysisAgent",
    system_prompt=("You analyze web content and screenshots ..."),
    llm=llm,
    tools=[search_text, take_screenshot],
    can_handoff_to=["BrowserAgent"],
)
agent_workflow = AgentWorkflow(agents=[browser_agent, analysis_agent], ...)  # excluded
```

**AstraBert/llamaindex-docs-agent** `scripts/main.py:75–84`:
```python
web_search_tool = FunctionTool.from_defaults(fn=tavily_search)
chat_history = [ChatMessage.from_str("You are a useful assistant...", role="system")]
agent = ReActAgent.from_tools(tools=[router_tool, web_search_tool],
                              chat_history=chat_history, verbose=True)
```
← system prompt via chat_history, not system_prompt=; v1 gap (§8.1)
