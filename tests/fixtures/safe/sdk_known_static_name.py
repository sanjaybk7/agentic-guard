"""Safe: f-string interpolation of an SDK-allowlisted static constant.

Fix 3 pattern: ``RECOMMENDED_PROMPT_PREFIX`` is a fixed module-level
``str`` in the OpenAI Agents SDK (`agents.extensions.handoff_prompt`).
The SDK ships as an installed package, so cross-module resolution can't
reach its source — the curated ``KNOWN_STATIC_NAMES`` allowlist covers
exactly this gap, gated by the name being imported in this file. Must
NOT fire IG002.
"""

from agents import Agent, function_tool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


@function_tool
def lookup(key: str) -> str:
    return ""


faq_agent = Agent(
    name="faq-agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are an FAQ agent.""",
    tools=[lookup],
    model="gpt-4o",
)
