"""Stage 1 — LangGraph: @tool-decorated extraction must still work (no regression).

The refactor must keep reusing the pre-registered decorated Tool object, which
carries the docstring-derived description. This fixture lets the test assert the
description survived (proving the registered object is reused, not re-synthesized
from the bare name).
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def read_email(message_id: str) -> str:
    """Fetch the body of an email by id."""
    return ""


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email on the user's behalf."""
    return ""


agent = create_react_agent(
    model="claude-opus-4-7",
    tools=[read_email, send_email],
    prompt="You are a helpful assistant.",
)
