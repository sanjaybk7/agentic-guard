"""§16 — assignment inside an ``if`` branch does NOT resolve.

The value is conditional on the branch taken; static analysis cannot
know which path executed. Conservative-on-doubt: do not resolve.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


cond = True


def make_agent():
    if cond:
        PROMPT = "if-branch literal"
    return Agent(
        name="if-branch",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
