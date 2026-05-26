"""§4 — closures walk outward through enclosing function scopes.

Inner function reads outer's PROMPT (closure capture). Per Python LEGB,
inner sees outer's binding because inner does not rebind PROMPT.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "literal in outer scope"

    def inner():
        return Agent(
            name="closure-outer",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
