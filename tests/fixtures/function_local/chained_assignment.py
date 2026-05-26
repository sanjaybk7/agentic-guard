"""§13 — chained assignment ``X = Y = "..."`` resolves both targets to
the same literal.

Two agents, one per chained target, both must resolve.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent_x():
    X = Y = "shared literal"
    return Agent(
        name="chained-x",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )


def make_agent_y():
    X = Y = "shared literal"
    return Agent(
        name="chained-y",
        instructions=Y,
        tools=[lookup],
        model="gpt-4o",
    )
