"""§24 — exception variable ``except Exception as e`` is bound to the
exception object, never a string. Out of scope for PR #5.

We do not want to resolve ``e`` to a literal. The fixture also confirms
the analyzer doesn't crash on ``ast.ExceptHandler.name`` patterns.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        return Agent(
            name="except-var",
            instructions=e,  # type: ignore[arg-type]
            tools=[lookup],
            model="gpt-4o",
        )
    return None
