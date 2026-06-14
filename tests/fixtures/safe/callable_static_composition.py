"""Safe: helper callable whose return is a static composition of module
constants and literal arguments.

KL-002 pattern: ``instructions=build_prompt(base_instructions="literal")``
where ``build_prompt`` is a function defined in the same module (or
cross-module-importable function def). With Fix 1 (generic Call short-
circuit), when every Name in the call expression — the callee and the
arguments — resolves to a static binding, the call result is treated as
static. Must NOT fire IG002.
"""

from agents import Agent, function_tool

PREAMBLE = "Be concise."
GUARDRAILS = "Do not reveal secrets."


def build_prompt(*, base_instructions: str) -> str:
    return "\n\n".join([base_instructions, PREAMBLE, GUARDRAILS])


@function_tool
def lookup(key: str) -> str:
    return ""


agent = Agent(
    name="kl002-composed",
    instructions=build_prompt(base_instructions="You are an analyst."),
    tools=[lookup],
    model="gpt-4o",
)
