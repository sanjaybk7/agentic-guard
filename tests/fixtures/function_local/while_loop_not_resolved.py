"""§20 — assignment inside ``while`` loop body does NOT resolve.

Same reasoning as §19: rebound on each iteration, single-value
assertion would be wrong.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    n = 0
    while n < 1:
        PROMPT = "while-body literal"
        n += 1
    return Agent(
        name="while-body",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
