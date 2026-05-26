"""§17 — assignment inside ``try``/``except`` body does NOT resolve.

Unlike Fix 1's top-level module-scope exception (optional-dependency
pattern), function-scope try/except almost always wraps a runtime
operation, not an optional binding. No exception here: conditional
binding, fall through to dynamic.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    try:
        PROMPT = "try-branch literal"
    except Exception:
        PROMPT = "except-branch literal"
    return Agent(
        name="try-branch",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
