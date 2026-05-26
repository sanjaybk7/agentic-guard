"""§12 (amended) — tuple unpacking with mixed RHS skips entire unpacking.

All-or-nothing: ``SYS, OTHER = "lit", build()`` — even though SYS's
position is a literal, the whole tuple is rejected. SYS does not
resolve; IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def build_other() -> str:
    return "dynamic value"


def make_agent():
    SYS, OTHER = "primary literal", build_other()
    return Agent(
        name="tuple-unpack-mixed",
        instructions=SYS,
        tools=[lookup],
        model="gpt-4o",
    )
