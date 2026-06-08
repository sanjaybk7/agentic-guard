"""Regression fixture: both crewai and agents imports in the same file.

Models a crewai project that has a local helper module named agents.py and
imports from it alongside crewai. The OpenAI Agents parser's matches_file fires
on any 'from agents import ...' (it cannot distinguish local modules from the
OpenAI Agents SDK). Without location-dedup, a single Agent(...) call would be
emitted twice — once as framework=crewai and once as framework=openai-agents.

The engine's _dedup_agents_by_location must collapse this to exactly 1 agent
and record 1 collision in result.agent_location_collisions.
"""

from crewai import Agent
from agents import SomeLocalHelper  # noqa: F401 — local agents.py, not OpenAI SDK

agent = Agent(
    role="Researcher",
    goal="Research topics in depth",
    backstory="Expert researcher with broad domain knowledge.",
)
