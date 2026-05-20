"""§16 — assignment inside an ``if`` branch does NOT resolve.

The value is conditional on the branch taken; static analysis cannot
know which path executed. Conservative-on-doubt: do not resolve.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it. The
conditionality is genuinely opaque, mirroring real conditional bindings
in production code.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(cond: bool):
    if cond:
        PROMPT = "if-branch literal"
    return Agent(
        name="if-branch",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
