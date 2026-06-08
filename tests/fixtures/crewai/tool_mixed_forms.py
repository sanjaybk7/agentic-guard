"""§3 Tool extraction — mixed list with all three AST element forms.

A single tools=[...] list may contain ast.Call, ast.Attribute, and ast.Name
elements simultaneously. All three must be extracted; others (e.g., starred
unpacks) are skipped without error.
"""

from crewai import Agent
from crewai_tools import SerperDevTool
from my_tools import SearchTools  # noqa: F401

lookup_tool = None  # ast.Name

agent = Agent(
    role="Researcher",
    goal="Research topics comprehensively",
    backstory="Expert researcher.",
    tools=[SerperDevTool(), SearchTools.fetch, lookup_tool],
)
