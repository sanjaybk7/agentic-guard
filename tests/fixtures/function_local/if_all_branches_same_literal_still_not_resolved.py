"""§16 (deferred enhancement) — even when every branch binds the name to
the *same* literal, PR #5 does NOT resolve.

The "all branches assign literals" enhancement was considered and
explicitly deferred in §16. A branch-equivalence walker plus a
"set of possible literal values" representation would close this case,
but adds rule complexity not justified by corpus prevalence. This
fixture documents the deferred decision: any conditional binding,
including this symmetric case, falls through to dynamic.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


cond = True


def make_agent():
    if cond:
        PROMPT = "both-branches identical literal"
    else:
        PROMPT = "both-branches identical literal"
    return Agent(
        name="if-all-branches-same",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
