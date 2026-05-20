"""§6 — comprehension body references outer-scope binding; resolves.

PROMPT is function-local; the comprehension reads it from the enclosing
function scope (Python's LEGB rule naturally walks outward from
comprehension scope to function scope).
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agents():
    PROMPT = "shared system prompt"
    return [
        Agent(
            name=f"comp-uses-outer-{i}",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
        for i in range(3)
    ]
