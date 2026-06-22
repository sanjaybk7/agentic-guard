"""Stage 1 — LangGraph: plain undecorated functions in tools=[...].

Before the direct-extraction refactor the parser only resolved names that were
@tool-decorated in the same file, so these plain functions were dropped and the
agent came back with tools=[]. After the refactor their names are extracted and
classified by the taxonomy directly.

read_email / send_email are taxonomy-recognized SOURCE / SINK names so the test
can assert classification flowed through, not just that a name string survived.
"""

from langgraph.prebuilt import create_react_agent


def read_email(message_id: str) -> str:  # NO @tool decorator
    """Fetch the body of an email by id."""
    return ""


def send_email(to: str, subject: str, body: str) -> str:  # NO @tool decorator
    """Send an email on the user's behalf."""
    return ""


agent = create_react_agent(
    model="claude-opus-4-7",
    tools=[read_email, send_email],
    prompt="You are a helpful assistant.",
)
