# CrewAI Parser — Fixture Inventory

Generated artifact: concatenates every CrewAI fixture file and the test file
for design-doc review. Mirrors the PR-4/PR-5 inventory pattern.
Committed on `crewai-parser` branch.

Red-half result (stub parser, no implementation):
- **17 tests collected, 16 FAIL (assertion), 1 PASS, 0 ERRORS**
- Passing test: `test_no_crewai_import_not_detected` — true negative, correct for the right reason
  (stub returns [] = expected 0 agents in a non-crewai file).
- Tests 10, 16, 17 carry two-part assertions (detection + rule behavior) so they cannot
  pass vacuously; all three fail at part (a) on the red half.

---

## tests/fixtures/crewai/direct_agent.py

```python
"""§2 Detection — direct Agent(role=..., tools=[]) in a crewai-importing file.

Baseline positive: a bare module-level Agent(...) call after importing from crewai.
Parser must detect one agent named "Researcher" (from role=) with no tools.
"""

from crewai import Agent

agent = Agent(
    role="Researcher",
    goal="Research topics thoroughly",
    backstory="You are an expert researcher with broad domain knowledge.",
)
```

---

## tests/fixtures/crewai/qualified_call.py

```python
"""§2 Detection — crewai.Agent(...) attribute-qualified form.

call_base_name strips attribute access so "crewai.Agent(...)" yields base "Agent".
Parser must detect one agent even when the class is accessed as a module attribute.
"""

import crewai

agent = crewai.Agent(
    role="Analyst",
    goal="Analyze market data",
    backstory="You are a seasoned market analyst.",
)
```

---

## tests/fixtures/crewai/agent_decorated_method.py

```python
"""§2/§6 Detection — @agent-decorated method returning Agent(...).

The @agent decorator is registration metadata only; the Agent(...) call node
is the detection anchor. Agent name comes from the method name ("researcher"),
not from role= (which is YAML-backed via config=).
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
        )
```

---

## tests/fixtures/crewai/no_crewai_import.py

```python
"""§2 Negative — Agent(...) in a file that does NOT import crewai.

"Agent" is a common name. The parser must require a crewai import to avoid
false-positives in non-CrewAI code that happens to define or use an Agent class.
"""


class Agent:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


agent = Agent(
    role="Researcher",
    goal="Do research",
    backstory="Expert",
)
```

---

## tests/fixtures/crewai/tool_ast_call.py

```python
"""§3 Tool extraction — ast.Call form: tools=[SerperDevTool()].

Class instantiations are the dominant tool form in @CrewBase repos.
call_base_name(elt.func) recovers the class name "SerperDevTool" from the Call node.
SerperDevTool is not in taxonomy yet (no taxonomy PR in this branch), so it resolves NEUTRAL.
"""

from crewai import Agent
from crewai_tools import SerperDevTool

agent = Agent(
    role="Researcher",
    goal="Research market trends",
    backstory="Expert market researcher.",
    tools=[SerperDevTool()],
)
```

---

## tests/fixtures/crewai/tool_ast_attribute.py

```python
"""§3 Tool extraction — ast.Attribute form: tools=[SearchTools.search_internet].

Attribute references (class.method) are common in plain-factory CrewAI repos.
elt.attr yields the tool name "search_internet".
"search_internet" contains "search" but the taxonomy pattern is "search_web" —
no substring match — so this resolves NEUTRAL (tests name extraction, not classification).
"""

from crewai import Agent
from my_tools import SearchTools  # noqa: F401 — import present for parser context

agent = Agent(
    role="Researcher",
    goal="Research topics",
    backstory="Expert researcher.",
    tools=[SearchTools.search_internet],
)
```

---

## tests/fixtures/crewai/tool_ast_name.py

```python
"""§3 Tool extraction — ast.Name form: tools=[search_tool].

Variable references (plain names) pass through as-is.
elt.id yields the tool name "search_tool".
"""

from crewai import Agent

search_tool = None  # runtime value; name extracted statically from AST

agent = Agent(
    role="Researcher",
    goal="Research topics",
    backstory="Expert researcher.",
    tools=[search_tool],
)
```

---

## tests/fixtures/crewai/tool_mixed_forms.py

```python
"""§3 Tool extraction — mixed list with all three AST element forms.

A single tools=[...] list may contain ast.Call, ast.Attribute, and ast.Name
elements simultaneously. All three must be extracted; others (e.g., starred
unpacks) are skipped without error.
"""

from crewai import Agent
from crewai_tools import SerperDevTool
from my_tools import SearchTools  # noqa: F401

lookup_tool = None  # ast.Name

agent = Agent(
    role="Researcher",
    goal="Research topics comprehensively",
    backstory="Expert researcher.",
    tools=[SerperDevTool(), SearchTools.fetch, lookup_tool],
)
```

---

## tests/fixtures/crewai/toolless_agent.py

```python
"""§5 Emit tool-less — no tools= kwarg; agent still emitted with tools=[].

Config-only and no-tools agents (e.g., google-gemini/crewai-quickstart) must
increment agent_count even when tools cannot be extracted. tools=[] is correct;
the parser must not skip the agent simply because it has no tool list.
"""

from crewai import Agent

agent = Agent(
    role="Writer",
    goal="Write clear and concise reports",
    backstory="You are a skilled technical writer.",
)
```

---

## tests/fixtures/crewai/runtime_indirect_tools.py

```python
"""§3/§5 Runtime-indirect tools — Agent(config=runtime_dict) with no tools= kwarg.

Models C3/C4 style: the Agent(...) call is statically visible but tools come
from a runtime value (dict, DB, etc.). The parser must still emit the agent
(the call exists in source) with tools=[] and must NOT hallucinate tool names
by inspecting the config variable.
"""

from crewai import Agent


def make_agent(config: dict) -> Agent:
    return Agent(config=config)
```

---

## tests/fixtures/crewai/prompt_inline_static.py

```python
"""§4 IG002 — inline literal role/goal/backstory → system_prompt_is_dynamic=False.

All three fields are string literals. classify_prompt_expr returns False for each.
This is the C5-style non-YAML-backed case. IG002 must NOT fire.
"""

from crewai import Agent

agent = Agent(
    role="Analyst",
    goal="Analyze market data carefully and produce structured reports.",
    backstory="You are a seasoned analyst with ten years of experience in financial markets.",
)
```

---

## tests/fixtures/crewai/prompt_yaml_backed.py

```python
"""§4 IG002 — config=self.agents_config['x'] (YAML-backed) → system_prompt_is_dynamic=False.

All role/goal/backstory come from a YAML file loaded at runtime. The YAML loader
cannot produce f-strings or concatenation, so the result is always static.
Parser must set system_prompt_is_dynamic=False WITHOUT opening or parsing any YAML file.
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def analyst(self) -> Agent:
        return Agent(config=self.agents_config["analyst"])
```

---

## tests/fixtures/crewai/prompt_dynamic_fstring.py

```python
"""§4 IG002 — f-string role/goal → system_prompt_is_dynamic=True, taint source captured.

Evidenced in liangdabiao/crewai_stock_analysis_system/src/crews/data_collection_crew.py
(goal=f"收集{company}的市场趋势..."). Not hypothetical — real pattern in the corpus.
classify_prompt_expr detects the JoinedStr node and extracts "company" as a taint source.
IG002 must fire on this agent.
"""

from crewai import Agent


def make_agent(company: str) -> Agent:
    return Agent(
        role=f"Analyst for {company}",
        goal=f"Analyze {company}'s financial position and market standing.",
        backstory="You are an expert financial analyst.",
    )
```

---

## tests/fixtures/crewai/name_from_role.py

```python
"""§6 Name resolution — role="Researcher" literal → agent name "Researcher".

When role= is an inline string literal and there is no @agent decorator,
the role string is the best proxy for the agent's logical identity.
Parser must set agent.name = "Researcher".
"""

from crewai import Agent

agent = Agent(
    role="Researcher",
    goal="Research topics in depth",
    backstory="Expert researcher with broad domain knowledge.",
)
```

---

## tests/fixtures/crewai/name_from_method.py

```python
"""§6 Name resolution — @agent method name fallback when role= is absent (YAML-backed).

When Agent(config=...) provides no inline role= literal, the enclosing @agent
method name ("researcher") is the fallback. Parser must set agent.name = "researcher".
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"])
```

---

## tests/fixtures/crewai/sources_only_crewai.py

```python
"""§7 IG001 precision — CrewAI agent with only SOURCE tools; IG001 must NOT fire.

Tool names use existing taxonomy patterns (search_web, read_email) so the rule
engine can classify them without waiting for the CrewAI taxonomy PR. This test
verifies that the source+sink-pair requirement from IG001 is enforced on
crewai-emitted agents, preventing the DeepGit-class false positive (agent present,
tools present, but no confused-deputy risk because no sink exists).
"""

from crewai import Agent

search_web = None  # ast.Name; "search_web" matches taxonomy SOURCE pattern
read_email = None  # ast.Name; "read_email" matches taxonomy SOURCE pattern

agent = Agent(
    role="Researcher",
    goal="Search the web and read emails to gather information.",
    backstory="Expert information gatherer.",
    tools=[search_web, read_email],
)
```

---

## tests/fixtures/crewai/sinks_only_crewai.py

```python
"""§7 IG001 precision — CrewAI agent with only SINK tools; IG001 must NOT fire.

Tool names use existing taxonomy patterns (send_email, write_file) so the rule
engine can classify them without waiting for the CrewAI taxonomy PR. No source
tool means no attacker-controlled input can flow into the sink — IG001 requires
both a SOURCE and a SINK to fire.
"""

from crewai import Agent

send_email = None  # ast.Name; "send_email" matches taxonomy SINK pattern
write_file = None  # ast.Name; "write_file" matches taxonomy SINK pattern

agent = Agent(
    role="Communicator",
    goal="Send emails and write files on behalf of users.",
    backstory="Expert communication assistant.",
    tools=[send_email, write_file],
)
```

---

## tests/test_crewai_parser.py

```python
"""Tests for the CrewAI parser — fixture matrix for docs/design/crewai-parser.md.

Red half of TDD: CrewAIParser exists as a non-functional stub. Every test that
expects agents or tool extraction will fail at the assertion level (stub returns
[], []). Negative tests (no detection, IG001 not-fire precision guards) pass
vacuously on the red half and for the right reason on the green half.

Each test cites the design-doc section (§) it enforces in its failure message.
"""

from __future__ import annotations

from pathlib import Path

from agentic_guard.engine import Scanner
from agentic_guard.parsers.crewai import CrewAIParser
from agentic_guard.taxonomy import Taxonomy

FIXTURES = Path(__file__).parent / "fixtures" / "crewai"


def _parser() -> CrewAIParser:
    return CrewAIParser(taxonomy=Taxonomy.load())


def _scanner() -> Scanner:
    taxonomy = Taxonomy.load()
    return Scanner(parsers=[CrewAIParser(taxonomy=taxonomy)])


# ---------------------------------------------------------------------------
# §2 Detection
# ---------------------------------------------------------------------------


def test_direct_agent_detected() -> None:
    """§2 — direct Agent(role=...) in a crewai-importing file → one agent detected."""
    _, agents = _parser().parse_file(FIXTURES / "direct_agent.py")
    assert len(agents) == 1, (
        "§2 direct Agent(...) call not detected — CrewAIParser must trigger on "
        "Agent(...) when file imports from crewai"
    )


def test_qualified_call_detected() -> None:
    """§2 — crewai.Agent(...) attribute-qualified form → one agent detected."""
    _, agents = _parser().parse_file(FIXTURES / "qualified_call.py")
    assert len(agents) == 1, (
        "§2 crewai.Agent(...) qualified call not detected — call_base_name must "
        "strip attribute access and return 'Agent'"
    )


def test_agent_decorated_method_name() -> None:
    """§2/§6 — @agent-decorated method returning Agent(...) → detected, name from method."""
    _, agents = _parser().parse_file(FIXTURES / "agent_decorated_method.py")
    assert len(agents) == 1, (
        "§2 @agent-decorated method not detected — Agent(...) call inside method body "
        "must be the detection anchor, not the decorator"
    )
    assert agents[0].name == "researcher", (
        f"§6 expected name 'researcher' from method name, got {agents[0].name!r}"
    )


def test_no_crewai_import_not_detected() -> None:
    """§2 Negative — Agent(...) without crewai import → must NOT be detected."""
    _, agents = _parser().parse_file(FIXTURES / "no_crewai_import.py")
    assert len(agents) == 0, (
        "§2 precision: Agent(...) with no crewai import must not be detected — "
        f"'Agent' is too common a name; got {len(agents)} agents"
    )


# ---------------------------------------------------------------------------
# §3 Tool extraction
# ---------------------------------------------------------------------------


def test_tool_ast_call() -> None:
    """§3 — tools=[SerperDevTool()] (ast.Call) → tool name 'SerperDevTool' extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tool_ast_call.py")
    assert len(agents) == 1, "§3 agent not detected in tool_ast_call fixture"
    names = {t.name for t in agents[0].tools}
    assert "SerperDevTool" in names, (
        f"§3 ast.Call tool extraction failed: expected 'SerperDevTool', got {names}"
    )


def test_tool_ast_attribute() -> None:
    """§3 — tools=[SearchTools.search_internet] (ast.Attribute) → 'search_internet' extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tool_ast_attribute.py")
    assert len(agents) == 1, "§3 agent not detected in tool_ast_attribute fixture"
    names = {t.name for t in agents[0].tools}
    assert "search_internet" in names, (
        f"§3 ast.Attribute tool extraction failed: expected 'search_internet', got {names}"
    )


def test_tool_ast_name() -> None:
    """§3 — tools=[search_tool] (ast.Name) → 'search_tool' extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tool_ast_name.py")
    assert len(agents) == 1, "§3 agent not detected in tool_ast_name fixture"
    names = {t.name for t in agents[0].tools}
    assert "search_tool" in names, (
        f"§3 ast.Name tool extraction failed: expected 'search_tool', got {names}"
    )


def test_tool_mixed_forms() -> None:
    """§3 — mixed tools=[SerperDevTool(), SearchTools.fetch, lookup_tool] → all three extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tool_mixed_forms.py")
    assert len(agents) == 1, "§3 agent not detected in tool_mixed_forms fixture"
    names = {t.name for t in agents[0].tools}
    assert names == {"SerperDevTool", "fetch", "lookup_tool"}, (
        f"§3 mixed tool extraction failed: expected {{'SerperDevTool', 'fetch', 'lookup_tool'}}, got {names}"
    )


def test_toolless_agent_emitted() -> None:
    """§5 — no tools= kwarg → agent still emitted with tools=[]."""
    _, agents = _parser().parse_file(FIXTURES / "toolless_agent.py")
    assert len(agents) == 1, (
        "§5 tool-less agent not emitted — parser must emit agents even when "
        "no tools= kwarg is present"
    )
    assert agents[0].tools == [], (
        f"§5 expected tools=[], got {agents[0].tools}"
    )


def test_runtime_indirect_tools_no_hallucination() -> None:
    """§3/§5 — Agent(config=runtime_dict) no tools= → (a) emitted, (b) tools=[].

    Two-part check so the test cannot pass vacuously:
    (a) agent must be detected — the Agent(...) call is statically visible.
    (b) tool list must be empty — parser must not hallucinate names from the
        runtime config value.
    Both parts must hold; failing either is a bug.
    """
    _, agents = _parser().parse_file(FIXTURES / "runtime_indirect_tools.py")
    # (a) detection
    assert len(agents) == 1, (
        "§5 runtime-indirect agent not emitted — Agent(...) call is statically "
        "visible so parser must still emit it"
    )
    # (b) no hallucination
    assert agents[0].tools == [], (
        f"§3 parser hallucinated tool names from runtime config: {agents[0].tools}"
    )


# ---------------------------------------------------------------------------
# §4 IG002 — system prompt dynamic analysis
# ---------------------------------------------------------------------------


def test_prompt_inline_static() -> None:
    """§4 — inline literal role/goal/backstory → system_prompt_is_dynamic=False."""
    _, agents = _parser().parse_file(FIXTURES / "prompt_inline_static.py")
    assert len(agents) == 1, "§4 agent not detected in prompt_inline_static fixture"
    assert agents[0].system_prompt_is_dynamic is False, (
        "§4 inline literal strings must not be classified dynamic; "
        f"got system_prompt_is_dynamic={agents[0].system_prompt_is_dynamic}"
    )


def test_prompt_yaml_backed() -> None:
    """§4 — config=self.agents_config['x'] (YAML-backed) → system_prompt_is_dynamic=False, no YAML I/O."""
    _, agents = _parser().parse_file(FIXTURES / "prompt_yaml_backed.py")
    assert len(agents) == 1, "§4 agent not detected in prompt_yaml_backed fixture"
    assert agents[0].system_prompt_is_dynamic is False, (
        "§4 YAML-backed config must always be static (YAML cannot contain f-strings); "
        f"got system_prompt_is_dynamic={agents[0].system_prompt_is_dynamic}"
    )


def test_prompt_dynamic_fstring() -> None:
    """§4 — f-string role=f"Analyst for {company}" → system_prompt_is_dynamic=True, taint captured."""
    _, agents = _parser().parse_file(FIXTURES / "prompt_dynamic_fstring.py")
    assert len(agents) == 1, "§4 agent not detected in prompt_dynamic_fstring fixture"
    assert agents[0].system_prompt_is_dynamic is True, (
        "§4 f-string in role/goal/backstory must set system_prompt_is_dynamic=True; "
        f"got {agents[0].system_prompt_is_dynamic}"
    )
    assert "company" in agents[0].system_prompt_taint_sources, (
        f"§4 taint source 'company' not captured; got {agents[0].system_prompt_taint_sources}"
    )


# ---------------------------------------------------------------------------
# §6 Name resolution
# ---------------------------------------------------------------------------


def test_name_from_role() -> None:
    """§6 — role="Researcher" literal → agent.name == "Researcher"."""
    _, agents = _parser().parse_file(FIXTURES / "name_from_role.py")
    assert len(agents) == 1, "§6 agent not detected in name_from_role fixture"
    assert agents[0].name == "Researcher", (
        f"§6 expected name 'Researcher' from role= literal, got {agents[0].name!r}"
    )


def test_name_from_method_fallback() -> None:
    """§6 — @agent def researcher with YAML config (no role literal) → name 'researcher'."""
    _, agents = _parser().parse_file(FIXTURES / "name_from_method.py")
    assert len(agents) == 1, "§6 agent not detected in name_from_method fixture"
    assert agents[0].name == "researcher", (
        f"§6 expected method-name fallback 'researcher', got {agents[0].name!r}"
    )


# ---------------------------------------------------------------------------
# §7 Gates / IG001 precision
# ---------------------------------------------------------------------------


def test_sources_only_crewai_no_ig001() -> None:
    """§7 IG001 precision — agent with only source tools → (a) detected, (b) IG001 NOT fire.

    Two-part check so the test cannot pass vacuously on the red half:
    (a) parser must detect the agent and extract its source tools — if this fails,
        the "IG001 silent" assertion proves nothing.
    (b) IG001 must not fire — no sink means no confused-deputy risk.
    Tool names (search_web, read_email) are existing taxonomy SOURCE patterns so
    the rule engine can evaluate them without the CrewAI taxonomy PR.
    """
    _, agents = _parser().parse_file(FIXTURES / "sources_only_crewai.py")
    # (a) detection with non-empty tool list
    assert len(agents) >= 1, (
        "§7 agent not detected in sources_only_crewai fixture — "
        "IG001 silence is meaningless without a detected agent"
    )
    tool_names = {t.name for t in agents[0].tools}
    assert tool_names, (
        f"§7 expected non-empty source tool list, got empty — "
        "tool extraction must work before rule behavior can be verified"
    )
    assert "search_web" in tool_names or "read_email" in tool_names, (
        f"§7 expected taxonomy-recognized SOURCE tool in list, got {tool_names}"
    )
    # (b) IG001 must not fire
    result = _scanner().scan(FIXTURES / "sources_only_crewai.py")
    ig001 = [f for f in result.findings if f.rule_id == "IG001"]
    assert not ig001, (
        f"§7 IG001 fired on a sources-only agent — requires both SOURCE and SINK: {ig001}"
    )


def test_sinks_only_crewai_no_ig001() -> None:
    """§7 IG001 precision — agent with only sink tools → (a) detected, (b) IG001 NOT fire.

    Two-part check so the test cannot pass vacuously on the red half:
    (a) parser must detect the agent and extract its sink tools — if this fails,
        the "IG001 silent" assertion proves nothing.
    (b) IG001 must not fire — no source means no attacker-controlled input.
    Tool names (send_email, write_file) are existing taxonomy SINK patterns so
    the rule engine can evaluate them without the CrewAI taxonomy PR.
    """
    _, agents = _parser().parse_file(FIXTURES / "sinks_only_crewai.py")
    # (a) detection with non-empty tool list
    assert len(agents) >= 1, (
        "§7 agent not detected in sinks_only_crewai fixture — "
        "IG001 silence is meaningless without a detected agent"
    )
    tool_names = {t.name for t in agents[0].tools}
    assert tool_names, (
        f"§7 expected non-empty sink tool list, got empty — "
        "tool extraction must work before rule behavior can be verified"
    )
    assert "send_email" in tool_names or "write_file" in tool_names, (
        f"§7 expected taxonomy-recognized SINK tool in list, got {tool_names}"
    )
    # (b) IG001 must not fire
    result = _scanner().scan(FIXTURES / "sinks_only_crewai.py")
    ig001 = [f for f in result.findings if f.rule_id == "IG001"]
    assert not ig001, (
        f"§7 IG001 fired on a sinks-only agent — no source tool means no confused-deputy risk: {ig001}"
    )
```
