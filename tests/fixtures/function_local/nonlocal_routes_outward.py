"""§23 — ``nonlocal X`` declaration + assignment in inner demotes outer's X.

Per §5.3 of the design doc: when inner declares ``nonlocal X`` and
then assigns ``X = "literal"``, that assignment writes to the outer
function's X. We do not register it as a local binding in inner's
scope, and we mark the outer scope's X as "potentially-modified-by-inner"
→ demote to dynamic (same logic as multi-assign).

Outer's PROMPT (bound once initially, then rebound via inner's
nonlocal write) is effectively multi-assigned → drops from exports
→ IG002 fires when inner constructs the Agent with PROMPT.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "outer initial literal"

    def inner():
        nonlocal PROMPT
        PROMPT = "inner overrides outer"
        return Agent(
            name="nonlocal-routes-outward",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
