"""§19 — assignment inside ``for`` loop body does NOT resolve.

Rebound on each iteration. Even when the RHS is a literal, the name's
lifetime spans multiple iterations and the analyzer shouldn't assert a
single value.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    for _i in range(1):
        PROMPT = "for-body literal"
    return Agent(
        name="for-body",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
