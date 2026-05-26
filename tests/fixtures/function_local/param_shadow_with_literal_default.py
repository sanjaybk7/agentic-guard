"""§22 (amended) — rule applies even when the parameter's default value
is itself a string literal.

Per the §22 amendment: a naive multi-assign counter might be tempted
to say "both are literals, the second wins, unambiguous → resolve."
That reasoning would behave differently from the §22 case with a
non-literal default. The rule is fixed on "parameter is the first
binding; any in-function assignment is reassignment," independent of
what the default looks like.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(X: str = "default literal"):
    X = "another literal"
    return Agent(
        name="param-shadow-literal-default",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
