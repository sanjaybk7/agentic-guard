"""§4 + §21 — inner function rebinds the name: no closure, multi-assign in inner.

Inner has its own PROMPT (assigned twice). Outer's PROMPT is shadowed by
inner's local. Inner's PROMPT is multi-assigned (per §21) so it doesn't
resolve. IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "outer literal"

    def inner():
        PROMPT = "inner first"
        PROMPT = "inner second"
        return Agent(
            name="closure-inner-rebinds",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
