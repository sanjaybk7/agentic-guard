"""§3 — ``self.x = "..."`` is attribute assignment, not local binding.

Resolving instance attributes would require flow analysis across methods,
inheritance, and class hierarchies — out of scope for PR #5. The
``instructions=self.prompt`` reference is an ``ast.Attribute`` that does
NOT resolve via function-local scope.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class AgentHolder:
    def __init__(self):
        self.prompt = "instance attribute literal"
        self.agent = Agent(
            name="self-attribute",
            instructions=self.prompt,
            tools=[lookup],
            model="gpt-4o",
        )
