"""§11 (amended) — walrus inside a ternary expression does NOT resolve.

The walrus binding only happens when the ternary's selected branch
executes. PR #5 refuses to reason about evaluation-order conditionals.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(flag: bool):
    # W is the walrus binding inside the ternary's true branch.
    _ = (W := "from ternary true branch") if flag else None
    return Agent(
        name="walrus-in-ternary",
        instructions=W,
        tools=[lookup],
        model="gpt-4o",
    )
