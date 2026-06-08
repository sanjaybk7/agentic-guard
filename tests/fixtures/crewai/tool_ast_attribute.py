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
