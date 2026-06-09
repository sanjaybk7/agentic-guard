"""Tests for the LlamaIndex parser — fixture matrix for docs/design/llamaindex-parser.md.

Red half of TDD: LlamaIndexParser exists as a non-functional stub. Every test that
expects agents or tool extraction will fail at the assertion level (stub returns
[], []). Negative tests (no detection) pass vacuously on the red half and for the
right reason on the green half.

Each test cites the design-doc section (§) it enforces in its failure message.
"""

from __future__ import annotations

from pathlib import Path

from agentic_guard.engine import Scanner
from agentic_guard.parsers.llamaindex import LlamaIndexParser
from agentic_guard.taxonomy import Taxonomy

FIXTURES = Path(__file__).parent / "fixtures" / "llamaindex"


def _parser() -> LlamaIndexParser:
    return LlamaIndexParser(taxonomy=Taxonomy.load())


def _scanner() -> Scanner:
    taxonomy = Taxonomy.load()
    return Scanner(parsers=[LlamaIndexParser(taxonomy=taxonomy)])


# ---------------------------------------------------------------------------
# §3.1 Detection — classmethod form
# ---------------------------------------------------------------------------


def test_react_agent_from_tools_detected() -> None:
    """§3.1 — ReActAgent.from_tools(...) in a llama_index file → one agent detected."""
    _, agents = _parser().parse_file(FIXTURES / "react_agent_from_tools.py")
    assert len(agents) == 1, (
        "§3.1 ReActAgent.from_tools(...) not detected — parser must fire when "
        "receiver class is in {ReActAgent, OpenAIAgent, FunctionCallingAgent} "
        f"and file imports llama_index; got {len(agents)} agents"
    )


def test_openai_agent_from_tools_detected() -> None:
    """§3.1 — OpenAIAgent.from_tools(...) → one agent detected."""
    _, agents = _parser().parse_file(FIXTURES / "openai_agent_from_tools.py")
    assert len(agents) == 1, (
        "§3.1 OpenAIAgent.from_tools(...) not detected — OpenAIAgent must be in "
        f"the receiver set; got {len(agents)} agents"
    )


def test_function_calling_agent_from_tools_detected() -> None:
    """§3.1/§8.2 — FunctionCallingAgent.from_tools(...) → one agent detected."""
    _, agents = _parser().parse_file(FIXTURES / "function_calling_agent_from_tools.py")
    assert len(agents) == 1, (
        "§3.1/§8.2 FunctionCallingAgent.from_tools(...) not detected — "
        "FunctionCallingAgent is documented-but-unseen; must be in the receiver set "
        f"at zero marginal cost; got {len(agents)} agents"
    )


def test_wrong_receiver_not_detected() -> None:
    """§3.1 Negative — ToolBuilder.from_tools(...) NOT in receiver set → NOT detected.

    This is the critical precision guard. Without the receiver-check predicate
    (func.attr == 'from_tools' AND func.value.id in _FROM_TOOLS_CLASSES), any
    X.from_tools() call in a llama_index-importing file would fire as a false positive.
    """
    _, agents = _parser().parse_file(FIXTURES / "wrong_receiver_from_tools.py")
    assert len(agents) == 0, (
        f"§3.1 precision: ToolBuilder.from_tools() must not be detected — "
        "receiver-check requires class to be in {ReActAgent, OpenAIAgent, FunctionCallingAgent}; "
        f"got {len(agents)} agents"
    )


def test_no_llama_import_not_detected() -> None:
    """§2/§3.1 Negative — from_tools(...) without llama_index import → NOT detected."""
    _, agents = _parser().parse_file(FIXTURES / "no_llama_import.py")
    assert len(agents) == 0, (
        "§2 precision: from_tools call with no llama_index import must not be detected — "
        f"file match requires import from llama_index or llama_index.*; got {len(agents)} agents"
    )


# ---------------------------------------------------------------------------
# §3.2 Detection — constructor form
# ---------------------------------------------------------------------------


def test_function_agent_constructor_detected() -> None:
    """§3.2 — FunctionAgent(name=..., tools=[...]) → detected, name from name= kwarg."""
    _, agents = _parser().parse_file(FIXTURES / "function_agent_constructor.py")
    assert len(agents) == 1, (
        "§3.2 FunctionAgent(...) constructor not detected — callee-name match on "
        f"'FunctionAgent' must fire; got {len(agents)} agents"
    )
    assert agents[0].name == "BrowserAgent", (
        f"§6 expected name 'BrowserAgent' from name= kwarg, got {agents[0].name!r}"
    )


def test_agent_workflow_not_double_counted() -> None:
    """§3.3 — Two FunctionAgent + AgentWorkflow → exactly 2 agents, NOT 3.

    AgentWorkflow is an orchestrator referencing already-detected FunctionAgent
    instances. Counting it as a third agent would double-count.

    Two-part check so the count alone can't pass for the wrong reason:
    (a) count == 2 — necessary but not sufficient.
    (b) names == {"BrowserAgent", "WriterAgent"} — proves the right two were
        detected, not one FunctionAgent + the AgentWorkflow orchestrator.
    """
    _, agents = _parser().parse_file(FIXTURES / "agent_workflow_exclusion.py")
    # (a) count
    assert len(agents) == 2, (
        f"§3.3 expected exactly 2 agents (two FunctionAgent constructors); "
        f"got {len(agents)} — AgentWorkflow must be excluded as a detection anchor"
    )
    # (b) correct identities — rules out FunctionAgent + AgentWorkflow passing as 2
    names = {a.name for a in agents}
    assert names == {"BrowserAgent", "WriterAgent"}, (
        f"§3.3 expected agent names {{'BrowserAgent', 'WriterAgent'}}; "
        f"got {names} — AgentWorkflow or a missed FunctionAgent in the detected set"
    )


# ---------------------------------------------------------------------------
# §4 Tool extraction
# ---------------------------------------------------------------------------


def test_tools_keyword_form() -> None:
    """§4.1 — from_tools(tools=[a, b]) keyword form → both tools extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tools_keyword.py")
    assert len(agents) == 1, "§4.1 agent not detected in tools_keyword fixture"
    names = {t.name for t in agents[0].tools}
    assert names == {"search_web", "read_email"}, (
        f"§4.1 keyword-form tool extraction failed: expected {{'search_web', 'read_email'}}, got {names}"
    )


def test_tools_positional_name_no_extraction() -> None:
    """§4.1/§4.3 — from_tools(tools_var, ...) positional ast.Name → agent emitted, tools=[].

    Two-part check so neither part can pass vacuously in the red phase:
    (a) agent must be detected — the from_tools call is statically visible.
    (b) tools must be [] — ast.Name is not a literal list; no tracking attempted.
    """
    _, agents = _parser().parse_file(FIXTURES / "tools_positional_name.py")
    # (a) detection
    assert len(agents) == 1, (
        "§4.1 agent not detected in tools_positional_name fixture — "
        "from_tools call is statically visible; parser must still emit the agent"
    )
    # (b) no extraction
    assert agents[0].tools == [], (
        f"§4.3 expected tools=[] for positional ast.Name arg (no tracking); "
        f"got {agents[0].tools}"
    )


def test_tools_positional_list_extracted() -> None:
    """§4.1 — from_tools([a, b], ...) positional ast.List → both tools extracted."""
    _, agents = _parser().parse_file(FIXTURES / "tools_positional_list.py")
    assert len(agents) == 1, "§4.1 agent not detected in tools_positional_list fixture"
    names = {t.name for t in agents[0].tools}
    assert names == {"search_web", "read_email"}, (
        f"§4.1 positional-list extraction failed: expected {{'search_web', 'read_email'}}, got {names}"
    )


def test_tools_element_forms() -> None:
    """§4.2 — [bare_fn, SearchTools.fetch, FunctionTool.from_defaults(fn)] → all three extracted.

    ast.Name → "bare_fn"
    ast.Attribute → "fetch" (SearchTools.fetch)
    ast.Call → "from_defaults" (call_base_name on FunctionTool.from_defaults(fn))
    """
    _, agents = _parser().parse_file(FIXTURES / "tools_element_forms.py")
    assert len(agents) == 1, "§4.2 agent not detected in tools_element_forms fixture"
    names = {t.name for t in agents[0].tools}
    assert names == {"bare_fn", "fetch", "from_defaults"}, (
        f"§4.2 element-form extraction failed: "
        f"expected {{'bare_fn', 'fetch', 'from_defaults'}}, got {names}"
    )


# ---------------------------------------------------------------------------
# §5 System prompt / IG002
# ---------------------------------------------------------------------------


def test_prompt_static() -> None:
    """§5.1 — FunctionAgent(system_prompt="literal") → system_prompt_is_dynamic=False."""
    _, agents = _parser().parse_file(FIXTURES / "prompt_static.py")
    assert len(agents) == 1, "§5.1 agent not detected in prompt_static fixture"
    assert agents[0].system_prompt_is_dynamic is False, (
        "§5.1 literal system_prompt must not be classified dynamic; "
        f"got system_prompt_is_dynamic={agents[0].system_prompt_is_dynamic}"
    )


def test_prompt_dynamic_fstring() -> None:
    """§5.1 — FunctionAgent(system_prompt=f"...{company}...") → dynamic=True, taint captured."""
    _, agents = _parser().parse_file(FIXTURES / "prompt_dynamic.py")
    assert len(agents) == 1, "§5.1 agent not detected in prompt_dynamic fixture"
    assert agents[0].system_prompt_is_dynamic is True, (
        "§5.1 f-string in system_prompt must set system_prompt_is_dynamic=True; "
        f"got {agents[0].system_prompt_is_dynamic}"
    )
    assert "company" in agents[0].system_prompt_taint_sources, (
        f"§5.1 taint source 'company' not captured; got {agents[0].system_prompt_taint_sources}"
    )


def test_prompt_chat_history_v1_gap() -> None:
    """§5.2 — from_tools(chat_history=...) with no system_prompt= → dynamic=False, location=None.

    Asserts the documented v1 behavior for the chat_history= gap. The parser cannot
    resolve the system text without local-variable tracking; it must emit the agent
    with system_prompt_is_dynamic=False and system_prompt_location=None rather than
    failing or hallucinating a dynamic classification.
    """
    _, agents = _parser().parse_file(FIXTURES / "prompt_chat_history.py")
    assert len(agents) == 1, "§5.2 agent not detected in prompt_chat_history fixture"
    assert agents[0].system_prompt_is_dynamic is False, (
        "§5.2 v1 gap: chat_history= without system_prompt= must emit dynamic=False "
        f"(local-variable tracking deferred); got {agents[0].system_prompt_is_dynamic}"
    )
    assert agents[0].system_prompt_location is None, (
        "§5.2 v1 gap: chat_history= without system_prompt= must emit location=None; "
        f"got {agents[0].system_prompt_location}"
    )


# ---------------------------------------------------------------------------
# §6 Name resolution
# ---------------------------------------------------------------------------


def test_name_from_kwarg() -> None:
    """§6 — FunctionAgent(name="BrowserAgent") → agent.name == "BrowserAgent"."""
    _, agents = _parser().parse_file(FIXTURES / "name_from_kwarg.py")
    assert len(agents) == 1, "§6 agent not detected in name_from_kwarg fixture"
    assert agents[0].name == "BrowserAgent", (
        f"§6 expected name 'BrowserAgent' from name= kwarg, got {agents[0].name!r}"
    )


def test_name_synthetic() -> None:
    """§6 — from_tools(...) with no name= kwarg → synthetic 'agent_1'."""
    _, agents = _parser().parse_file(FIXTURES / "name_synthetic.py")
    assert len(agents) == 1, "§6 agent not detected in name_synthetic fixture"
    assert agents[0].name == "agent_1", (
        f"§6 expected synthetic name 'agent_1' for from_tools agent with no name=, "
        f"got {agents[0].name!r}"
    )


# ---------------------------------------------------------------------------
# §7 IG001 precision guards
# ---------------------------------------------------------------------------


def test_sources_only_no_ig001() -> None:
    """§7 IG001 precision — source-only tools → (a) detected with tools, (b) IG001 NOT fire.

    Two-part check so the test cannot pass vacuously in the red phase:
    (a) parser must detect the agent and extract its source tools.
    (b) IG001 must not fire — no sink means no confused-deputy risk.
    Tool names (search_web, read_email) match existing taxonomy SOURCE patterns.
    """
    _, agents = _parser().parse_file(FIXTURES / "sources_only_llamaindex.py")
    # (a) detection with non-empty tool list
    assert len(agents) >= 1, (
        "§7 agent not detected in sources_only_llamaindex fixture — "
        "IG001 silence is meaningless without a detected agent"
    )
    tool_names = {t.name for t in agents[0].tools}
    assert tool_names, (
        "§7 expected non-empty source tool list, got empty — "
        "tool extraction must work before rule behavior can be verified"
    )
    assert "search_web" in tool_names or "read_email" in tool_names, (
        f"§7 expected taxonomy-recognized SOURCE tool in list, got {tool_names}"
    )
    # (b) IG001 must not fire
    result = _scanner().scan(FIXTURES / "sources_only_llamaindex.py")
    ig001 = [f for f in result.findings if f.rule_id == "IG001"]
    assert not ig001, (
        f"§7 IG001 fired on a sources-only agent — requires both SOURCE and SINK: {ig001}"
    )


def test_sinks_only_no_ig001() -> None:
    """§7 IG001 precision — sink-only tools → (a) detected with tools, (b) IG001 NOT fire.

    Two-part check so the test cannot pass vacuously in the red phase:
    (a) parser must detect the agent and extract its sink tools.
    (b) IG001 must not fire — no source means no attacker-controlled input.
    Tool names (send_email, write_file) match existing taxonomy SINK patterns.
    """
    _, agents = _parser().parse_file(FIXTURES / "sinks_only_llamaindex.py")
    # (a) detection with non-empty tool list
    assert len(agents) >= 1, (
        "§7 agent not detected in sinks_only_llamaindex fixture — "
        "IG001 silence is meaningless without a detected agent"
    )
    tool_names = {t.name for t in agents[0].tools}
    assert tool_names, (
        "§7 expected non-empty sink tool list, got empty — "
        "tool extraction must work before rule behavior can be verified"
    )
    assert "send_email" in tool_names or "write_file" in tool_names, (
        f"§7 expected taxonomy-recognized SINK tool in list, got {tool_names}"
    )
    # (b) IG001 must not fire
    result = _scanner().scan(FIXTURES / "sinks_only_llamaindex.py")
    ig001 = [f for f in result.findings if f.rule_id == "IG001"]
    assert not ig001, (
        f"§7 IG001 fired on a sinks-only agent — no source tool means no confused-deputy risk: {ig001}"
    )
