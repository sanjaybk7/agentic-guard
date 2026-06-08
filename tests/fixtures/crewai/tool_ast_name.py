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
