"""Stage 1 — direct tool-extraction refactor for LangGraph + OpenAI Agents parsers.

Red-half discipline: each "must now be extracted" test fails before the refactor
(the old pre-register-then-lookup path returned tools=[] for plain functions and
silently skipped ast.Call class instances) and passes after. The no-regression
tests confirm @tool / @function_tool extraction — including the docstring-derived
description carried by the reused registered object — still works.

Scope: inline forms only (plain undecorated functions, class instantiations).
Variable-passed lists and bind_tools are Stage 2 and intentionally not covered.
"""

from __future__ import annotations

from pathlib import Path

from agentic_guard.ir import ToolClassification
from agentic_guard.parsers import LangGraphParser, OpenAIAgentsParser

FIXTURES = Path(__file__).parent / "fixtures" / "tool_extraction"


# ---------------------------------------------------------------------------
# LangGraph
# ---------------------------------------------------------------------------


def test_langgraph_plain_function_extracted() -> None:
    """Plain undecorated functions in tools=[...] must now be extracted + classified."""
    _, agents = LangGraphParser().parse_file(FIXTURES / "lg_plain_function.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"read_email", "send_email"}, (
        f"plain functions not extracted from tools=[...]; got {set(by_name)}"
    )
    # Classification must flow through the taxonomy on the bare name.
    assert by_name["read_email"].classification == ToolClassification.SOURCE
    assert by_name["send_email"].is_sink


def test_langgraph_class_instance_extracted() -> None:
    """Class-instance (ast.Call) tools in tools=[...] must now be extracted."""
    _, agents = LangGraphParser().parse_file(FIXTURES / "lg_class_instance.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"ScrapeWebsiteTool", "PythonREPLTool"}, (
        f"class-instance tools not extracted; got {set(by_name)}"
    )
    # Taxonomy-recognized class name classifies; unknown one stays NEUTRAL.
    assert by_name["ScrapeWebsiteTool"].classification == ToolClassification.SOURCE
    assert by_name["PythonREPLTool"].classification == ToolClassification.NEUTRAL


def test_langgraph_decorated_no_regression() -> None:
    """@tool-decorated extraction (incl. docstring description) must still work."""
    _, agents = LangGraphParser().parse_file(FIXTURES / "lg_decorated_no_regression.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"read_email", "send_email"}
    assert by_name["read_email"].classification == ToolClassification.SOURCE
    assert by_name["send_email"].is_sink
    # Reused registered object retains the docstring-derived description.
    assert by_name["read_email"].description == "Fetch the body of an email by id."


# ---------------------------------------------------------------------------
# OpenAI Agents
# ---------------------------------------------------------------------------


def test_openai_plain_function_extracted() -> None:
    """Plain undecorated functions in tools=[...] must now be extracted + classified."""
    _, agents = OpenAIAgentsParser().parse_file(FIXTURES / "oai_plain_function.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"read_email", "send_email"}, (
        f"plain functions not extracted from tools=[...]; got {set(by_name)}"
    )
    assert by_name["read_email"].classification == ToolClassification.SOURCE
    assert by_name["send_email"].is_sink


def test_openai_class_instance_extracted() -> None:
    """Hosted tool class instances (ast.Call) in tools=[...] must now be extracted."""
    _, agents = OpenAIAgentsParser().parse_file(FIXTURES / "oai_class_instance.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"WebSearchTool", "FileSearchTool"}, (
        f"class-instance tools not extracted; got {set(by_name)}"
    )
    assert by_name["WebSearchTool"].classification == ToolClassification.SOURCE
    assert by_name["FileSearchTool"].classification == ToolClassification.NEUTRAL


def test_openai_decorated_no_regression() -> None:
    """@function_tool-decorated extraction (incl. docstring description) must still work."""
    _, agents = OpenAIAgentsParser().parse_file(FIXTURES / "oai_decorated_no_regression.py")
    assert len(agents) == 1, "agent not detected"
    by_name = {t.name: t for t in agents[0].tools}
    assert set(by_name) == {"read_email", "send_email"}
    assert by_name["read_email"].classification == ToolClassification.SOURCE
    assert by_name["send_email"].is_sink
    assert by_name["read_email"].description == "Fetch the body of an email by id."
