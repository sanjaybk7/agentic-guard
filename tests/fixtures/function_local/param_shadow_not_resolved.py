"""§22 — function parameter establishes the first binding; in-function
assignment to the same name is the second binding → multi-assign drop.

The parameter ``X`` is bound at function entry; ``X = "literal"``
inside the body is reassignment. Per the multi-assign-drops-the-name
policy, X does not resolve.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(X: str = "default"):
    X = "in-function literal"
    return Agent(
        name="param-shadow",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
