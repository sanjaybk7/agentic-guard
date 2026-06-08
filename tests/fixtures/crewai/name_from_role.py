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
