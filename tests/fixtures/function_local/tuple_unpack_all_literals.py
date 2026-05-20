"""§12 — tuple unpacking with all-literal RHS resolves.

Both targets are simple names; the RHS is a Tuple of literals of equal
length. Position-wise matching gives each target a static value.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    SYS, FALLBACK = "primary literal", "secondary literal"
    return Agent(
        name="tuple-unpack-all-literals",
        instructions=SYS,
        tools=[lookup],
        model="gpt-4o",
    )
