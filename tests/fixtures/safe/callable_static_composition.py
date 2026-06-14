"""Safe: helper callable whose return is a static composition of module
constants and literal arguments.

KL-002 pattern: ``instructions=build_prompt(base_instructions="literal")``
where ``build_prompt`` is allowlisted in ``STATIC_COMPOSER_FUNCTIONS`` —
it takes only string-typed arguments, returns ``str`` by composing them
with module-level string constants, and contains no closure or runtime
data. Must NOT fire IG002.

A broader rule that silenced any Call whose argument Names all resolve
was replaced with this explicit allowlist after the rule produced false
negatives on closure-returning callables (see
``vulnerable/closure_captures_external.py``).
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
