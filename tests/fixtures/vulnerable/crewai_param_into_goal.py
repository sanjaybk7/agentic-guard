"""Vulnerable (TP preservation): caller-supplied function parameter
interpolated into a LangGraph agent's ``prompt`` f-string.

Mirrors F10/F17 (liangdabiao/crewai_stock_analysis_system): a caller-
controlled string (``company``/``ticker``) flows from an outer entry
point through a builder function and into the system prompt. CrewAI's
``goal=`` field carries the same semantic in the real codebase; here we
use LangGraph's ``prompt=`` because the registered parsers cover
LangGraph and OpenAI Agents (CrewAI's role/goal aren't captured by the
v0.2 parsers).

Must still fire IG002 after the fixes — function parameters are not
allowlisted, do not resolve to module constants, and the JoinedStr
slot's name is a locally-bound parameter that the LEGB walk reports
as unresolved.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def lookup(key: str) -> str:
    """Look up a value."""
    return ""


def create_agent(company: str, ticker: str):
    return create_react_agent(
        model="claude-opus-4-7",
        tools=[lookup],
        prompt=f"You are an analyst. Research {company} ({ticker}) trends.",
    )
