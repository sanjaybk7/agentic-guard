"""§11 (amended) — walrus inside boolean short-circuit does NOT resolve.

``if cond and (PROMPT := "...")`` — the walrus may or may not execute
depending on ``cond``'s value. The "single deterministic binding"
guarantee that justifies resolution is broken; refuse rather than
reason about evaluation order.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(cond: bool):
    if cond and (PROMPT := "from boolean-and walrus"):
        return Agent(
            name="walrus-in-boolean",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
    return None
