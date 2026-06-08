"""Tests for the CrewAI parser and cross-parser dedup — fixture matrix for docs/design/crewai-parser.md.

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
        "§7 expected non-empty source tool list, got empty — "
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
        "§7 expected non-empty sink tool list, got empty — "
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


# ---------------------------------------------------------------------------
# Cross-parser dedup — location collision regression
# ---------------------------------------------------------------------------


def test_no_double_emission_on_both_import() -> None:
    """Regression: Agent(...) in a file importing both crewai and a local agents module.

    OpenAIAgentsParser.matches_file fires on any 'from agents import ...' including
    local modules named agents.py. Without location-dedup, a single Agent(...) call
    would be emitted twice (framework=openai-agents AND framework=crewai).

    The engine's _dedup_agents_by_location must:
    (a) collapse both emissions to exactly 1 agent (agents_seen == 1)
    (b) record the collision (agent_location_collisions == 1)

    Uses the full default Scanner (all parsers) so both parsers actually run.
    """
    result = Scanner().scan(FIXTURES / "both_import_collision.py")
    assert result.agents_seen == 1, (
        f"Double-emission: expected 1 agent after location-dedup, got {result.agents_seen}. "
        "Engine must dedup agents sharing the same (file, line, col) across parsers."
    )
    assert result.agent_location_collisions == 1, (
        f"Expected 1 collision recorded, got {result.agent_location_collisions}. "
        "Dedup must increment agent_location_collisions for each dropped agent."
    )
