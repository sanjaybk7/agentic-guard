"""§5 — lambdas: language semantics prohibit statements inside, so no
bindings can live there. This fixture exists only to confirm the analyzer
doesn't crash when a lambda is in scope alongside the function-local
resolution code path.

The Agent here uses a module-level constant (already handled by Fix 1);
the lambda is irrelevant noise. If the analyzer crashes on lambda
descent, this fixture catches it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


# A lambda exists in module scope; PR #5 must not crash when it walks past.
PROMPT = "module-level literal"
_filter = lambda x: x > 0  # noqa: E731


def make_agent():
    # Also a lambda inside the function body.
    _local_filter = lambda x: x * 2  # noqa: E731
    return Agent(
        name="lambda-structural",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
