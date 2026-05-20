"""§14 — starred unpacking is out of scope; entire unpacking skipped.

Consistent with §12 (no partial resolution): a star in the target list
means neither the non-starred nor the starred name resolves.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    X, *REST = "a", "b", "c"
    return Agent(
        name="starred-unpack",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
