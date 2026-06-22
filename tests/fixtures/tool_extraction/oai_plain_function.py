"""Stage 1 — OpenAI Agents: plain undecorated functions in tools=[...].

Mirror of lg_plain_function.py for the OpenAI Agents parser: before the refactor
these functions were dropped (not in _tools_by_name); after, they are extracted
and classified by name.
"""

from agents import Agent


def read_email(message_id: str) -> str:  # NO @function_tool decorator
    """Fetch the body of an email by id."""
    return ""


def send_email(to: str, subject: str, body: str) -> str:  # NO @function_tool decorator
    """Send an email on the user's behalf."""
    return ""


agent = Agent(
    name="inbox-agent",
    instructions="You are a helpful assistant.",
    tools=[read_email, send_email],
    model="gpt-4o",
)
