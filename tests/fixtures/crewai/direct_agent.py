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
