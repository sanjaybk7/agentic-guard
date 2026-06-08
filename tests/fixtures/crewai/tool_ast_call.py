"""§3 Tool extraction — ast.Call form: tools=[SerperDevTool()].

Class instantiations are the dominant tool form in @CrewBase repos.
call_base_name(elt.func) recovers the class name "SerperDevTool" from the Call node.
SerperDevTool is not in taxonomy yet (no taxonomy PR in this branch), so it resolves NEUTRAL.
"""

from crewai import Agent
from crewai_tools import SerperDevTool

agent = Agent(
    role="Researcher",
    goal="Research market trends",
    backstory="Expert market researcher.",
    tools=[SerperDevTool()],
)
