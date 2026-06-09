# LlamaIndex Fixture Inventory

Red-half counts: **18 tests — 16 FAIL, 2 PASS, 0 ERRORS**

Passing tests are pure negatives (`test_wrong_receiver_not_detected`,
`test_no_llama_import_not_detected`). Both pass vacuously on the red half (stub
returns 0 agents; assertions require 0). On the green half they pass for the right
reason (receiver-check and file-match logic). No test passes for the wrong reason.

---

## Fixture files

### `react_agent_from_tools.py`

```python
"""§3.1 — ReActAgent.from_tools(...) in a llama_index-importing file → one agent detected."""

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


def my_tool() -> str:
    """A simple tool."""
    return "result"


tool = FunctionTool.from_defaults(my_tool)
agent = ReActAgent.from_tools(tools=[tool], verbose=True)
```

---

### `openai_agent_from_tools.py`

```python
"""§3.1 — OpenAIAgent.from_tools(...) in a llama_index-importing file → one agent detected."""

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool


def get_weather(location: str) -> float:
    """Get current weather for a location."""
    return 72.0


tool = FunctionTool.from_defaults(get_weather, name="get_weather")
agent = OpenAIAgent.from_tools(tools=[tool], verbose=True)
```

---

### `function_calling_agent_from_tools.py`

```python
"""§3.1/§8.2 — FunctionCallingAgent.from_tools(...) → one agent detected."""

from llama_index.core.agent import FunctionCallingAgent
from llama_index.core.tools import FunctionTool


def search(query: str) -> str:
    """Search for information."""
    return "results"


tool = FunctionTool.from_defaults(search)
agent = FunctionCallingAgent.from_tools(tools=[tool], verbose=True)
```

---

### `wrong_receiver_from_tools.py`

```python
"""§3.1 Negative — receiver NOT in {ReActAgent, OpenAIAgent, FunctionCallingAgent} → NOT detected."""

from llama_index.core.tools import FunctionTool  # noqa: F401 — triggers llama_index file match

ToolBuilder = None  # dummy class; NOT in {ReActAgent, OpenAIAgent, FunctionCallingAgent}
result = ToolBuilder.from_tools(tools=["tool1", "tool2"])
```

---

### `no_llama_import.py`

```python
"""§2/§3.1 Negative — from_tools(...) without any llama_index import → NOT detected."""

# No llama_index import anywhere in this file.
ReActAgent = None  # dummy; no llama_index import so file must not match
agent = ReActAgent.from_tools(tools=["tool1"], verbose=True)
```

---

### `function_agent_constructor.py`

```python
"""§3.2 — FunctionAgent(name=..., tools=[...]) constructor → detected, name from name= kwarg."""

from llama_index.core.agent.workflow import FunctionAgent


async def navigate_to(url: str) -> str:
    """Navigate to a URL."""
    return f"Navigated to {url}"


agent = FunctionAgent(
    name="BrowserAgent",
    description="Browses the web and retrieves information",
    system_prompt="You are a web browsing agent. Navigate to URLs and retrieve content.",
    tools=[navigate_to],
)
```

---

### `agent_workflow_exclusion.py`

```python
"""§3.3 — Two FunctionAgent + AgentWorkflow → exactly 2 agents detected, NOT 3."""

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent


async def search(query: str) -> str:
    """Search the web."""
    return "results"


async def write_report(content: str) -> str:
    """Write a report."""
    return "written"


browser_agent = FunctionAgent(name="BrowserAgent", description="Browses the web", tools=[search])
writer_agent = FunctionAgent(name="WriterAgent", description="Writes reports", tools=[write_report])

# AgentWorkflow wraps already-detected agents — must NOT be counted as agent #3.
workflow = AgentWorkflow(agents=[browser_agent, writer_agent], root_agent=browser_agent.name)
```

---

### `tools_keyword.py`

```python
"""§4.1 — from_tools(tools=[a, b]) keyword form → both tools extracted."""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    return "results"


async def read_email() -> str:
    return "emails"


agent = ReActAgent.from_tools(tools=[search_web, read_email], verbose=True)
```

---

### `tools_positional_name.py`

```python
"""§4.1/§4.3 — from_tools(tools_var, ...) positional ast.Name → agent emitted, tools=[]."""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    return "results"


async def read_email() -> str:
    return "emails"


tools_list = [search_web, read_email]

# Positional arg is an ast.Name — not a literal list at the call site.
agent = ReActAgent.from_tools(tools_list, verbose=True)
```

---

### `tools_positional_list.py`

```python
"""§4.1 — from_tools([a, b], ...) positional literal ast.List → both tools extracted."""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    return "results"


async def read_email() -> str:
    return "emails"


# Literal list passed as positional arg — args[0] is an ast.List.
agent = ReActAgent.from_tools([search_web, read_email], verbose=True)
```

---

### `tools_element_forms.py`

```python
"""§4.2 — [bare_fn, SearchTools.fetch, FunctionTool.from_defaults(fn)] → all three extracted.

  ast.Name      → "bare_fn"
  ast.Attribute → "fetch"          (SearchTools.fetch)
  ast.Call      → "from_defaults"  (call_base_name on FunctionTool.from_defaults(fn))
"""

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from my_tools import SearchTools


def bare_fn() -> str:
    return "result"


def fn() -> str:
    return "result"


agent = ReActAgent.from_tools(
    tools=[bare_fn, SearchTools.fetch, FunctionTool.from_defaults(fn)],
    verbose=True,
)
```

---

### `prompt_static.py`

```python
"""§5.1 — FunctionAgent(system_prompt="literal string") → system_prompt_is_dynamic=False."""

from llama_index.core.agent.workflow import FunctionAgent


async def search(query: str) -> str:
    return "results"


agent = FunctionAgent(
    name="Researcher",
    system_prompt="You are a research assistant. Answer questions thoroughly and accurately.",
    tools=[search],
)
```

---

### `prompt_dynamic.py`

```python
"""§5.1 — FunctionAgent(system_prompt=f"...{x}...") → dynamic=True, taint captured."""

from llama_index.core.agent.workflow import FunctionAgent

company = "Acme Corp"


async def search(query: str) -> str:
    return "results"


agent = FunctionAgent(
    name="Researcher",
    system_prompt=f"You are a research assistant for {company}. Answer questions accurately.",
    tools=[search],
)
```

---

### `prompt_chat_history.py`

```python
"""§5.2 — from_tools(chat_history=...) no system_prompt= → dynamic=False, location=None (v1 gap)."""

from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage

chat_history = [ChatMessage.from_str("You are a helpful assistant for developers.", role="system")]


async def search(query: str) -> str:
    return "results"


agent = ReActAgent.from_tools(tools=[search], chat_history=chat_history, verbose=True)
```

---

### `name_from_kwarg.py`

```python
"""§6 — FunctionAgent(name="BrowserAgent") → agent.name == "BrowserAgent"."""

from llama_index.core.agent.workflow import FunctionAgent


async def navigate(url: str) -> str:
    return f"at {url}"


agent = FunctionAgent(name="BrowserAgent", description="Browses the web", tools=[navigate])
```

---

### `name_synthetic.py`

```python
"""§6 — from_tools(...) with no name= kwarg → synthetic name agent_1."""

from llama_index.core.agent import ReActAgent


async def search(query: str) -> str:
    return "results"


# from_tools agents have no name= kwarg — parser must synthesise agent_1.
agent = ReActAgent.from_tools(tools=[search], verbose=True)
```

---

### `sources_only_llamaindex.py`

```python
"""§7 IG001 precision — source-only tools → (a) detected with tools, (b) IG001 NOT fire."""

from llama_index.core.agent import ReActAgent

search_web = None  # ast.Name; "search_web" matches taxonomy SOURCE pattern
read_email = None  # ast.Name; "read_email" matches taxonomy SOURCE pattern

agent = ReActAgent.from_tools(tools=[search_web, read_email], verbose=True)
```

---

### `sinks_only_llamaindex.py`

```python
"""§7 IG001 precision — sink-only tools → (a) detected with tools, (b) IG001 NOT fire."""

from llama_index.core.agent import ReActAgent

send_email = None  # ast.Name; "send_email" matches taxonomy SINK pattern
write_file = None  # ast.Name; "write_file" matches taxonomy SINK pattern

agent = ReActAgent.from_tools(tools=[send_email, write_file], verbose=True)
```

---

## Test file (`tests/test_llamaindex_parser.py`)

18 tests. Red-half behavior per test:

| # | Test | Red-half | Reason |
|---|------|----------|--------|
| 1 | `test_react_agent_from_tools_detected` | FAIL | stub → 0 agents |
| 2 | `test_openai_agent_from_tools_detected` | FAIL | stub → 0 agents |
| 3 | `test_function_calling_agent_from_tools_detected` | FAIL | stub → 0 agents |
| 4 | `test_wrong_receiver_not_detected` | **PASS** | vacuous: 0 == 0 |
| 5 | `test_no_llama_import_not_detected` | **PASS** | vacuous: 0 == 0 |
| 6 | `test_function_agent_constructor_detected` | FAIL | stub → 0 agents |
| 7 | `test_agent_workflow_not_double_counted` | FAIL | stub → 0, expected 2 |
| 8 | `test_tools_keyword_form` | FAIL | stub → 0 agents |
| 9 | `test_tools_positional_name_no_extraction` | FAIL | part (a): 0 agents |
| 10 | `test_tools_positional_list_extracted` | FAIL | stub → 0 agents |
| 11 | `test_tools_element_forms` | FAIL | stub → 0 agents |
| 12 | `test_prompt_static` | FAIL | stub → 0 agents |
| 13 | `test_prompt_dynamic_fstring` | FAIL | stub → 0 agents |
| 14 | `test_prompt_chat_history_v1_gap` | FAIL | stub → 0 agents |
| 15 | `test_name_from_kwarg` | FAIL | stub → 0 agents |
| 16 | `test_name_synthetic` | FAIL | stub → 0 agents |
| 17 | `test_sources_only_no_ig001` | FAIL | part (a): 0 agents |
| 18 | `test_sinks_only_no_ig001` | FAIL | part (a): 0 agents |
