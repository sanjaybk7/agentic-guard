"""§1 / §15 — plain ``def`` body in scope; single literal binding resolves.

Baseline positive case: function defines PROMPT once, then constructs an
Agent using it. PR #5's function-local resolution must recognize PROMPT as
a static literal and silence IG002.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT = "You are a helpful assistant. Be concise."
    return Agent(
        name="func-local-basic",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
