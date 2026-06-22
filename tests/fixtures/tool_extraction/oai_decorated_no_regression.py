"""Stage 1 — OpenAI Agents: @function_tool extraction must still work (no regression).

The refactor must keep reusing the pre-registered decorated Tool object, which
carries the docstring-derived description. This fixture lets the test assert the
description survived.
"""

from agents import Agent, function_tool


@function_tool
def read_email(message_id: str) -> str:
    """Fetch the body of an email by id."""
    return ""


@function_tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email on the user's behalf."""
    return ""


agent = Agent(
    name="inbox-agent",
    instructions="You are a helpful assistant.",
    tools=[read_email, send_email],
    model="gpt-4o",
)
