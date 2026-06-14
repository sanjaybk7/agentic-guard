"""Safe: ternary ``A if cond else B`` between two module-level string
constants.

IfExp pattern: with Fix 2, when both ``body`` and ``orelse`` recursively
classify as static, the ternary is static regardless of the test
condition. Must NOT fire IG002.
"""

from agents import Agent, function_tool

PROMPT_STRICT = "You are strict."
PROMPT_LENIENT = "You are lenient."


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(strict: bool) -> Agent:
    return Agent(
        name="ifexp-agent",
        instructions=PROMPT_STRICT if strict else PROMPT_LENIENT,
        tools=[lookup],
        model="gpt-4o",
    )
