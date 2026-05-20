"""§6 — comprehension iteration variable is comp-local and rebound per
iteration; does NOT resolve via function-local scope.

``p`` is bound to a different literal on each iteration. Even though
every value is a literal, ``p`` itself is comp-local and PR #5 does not
extract bindings from comprehensions. Conservative default: IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agents():
    return [
        Agent(
            name=f"comp-iter-var-{i}",
            instructions=p,
            tools=[lookup],
            model="gpt-4o",
        )
        for i, p in enumerate(["alpha", "beta", "gamma"])
    ]
