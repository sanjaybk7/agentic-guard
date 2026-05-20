"""§12 — tuple unpacking from a function call RHS does NOT resolve.

``X, Y = build_pair()`` — we cannot statically determine the RHS
contents. Skip the entire unpacking.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def build_pair() -> tuple[str, str]:
    return "a", "b"


def make_agent():
    X, _Y = build_pair()
    return Agent(
        name="tuple-unpack-call-rhs",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
