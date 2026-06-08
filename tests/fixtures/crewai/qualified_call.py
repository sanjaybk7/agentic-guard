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
