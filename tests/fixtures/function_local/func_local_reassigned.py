"""§21 / §10 — reassignment within function disqualifies the name.

Multi-binding-drops-the-name policy: PROMPT is bound twice in the same
function scope, so PR #5's pre-pass drops it from the export set.
Resolution falls through to dynamic; IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT = "first binding"
    PROMPT = "second binding"
    return Agent(
        name="func-local-reassigned",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
