"""LG-3 — LangGraph: ``model.bind_tools(tools_var)`` with a same-scope literal.

The bound argument is a Name (``AGENT_TOOLS``) bound to a list literal at module
scope, in this same file. LG-3 resolves it to the literal and extracts the
elements. The agent is named after the assignment target (``bound_model``).
"""

from langchain_openai import ChatOpenAI


def read_email(message_id: str) -> str:
    """Fetch the body of an email by id."""
    return ""


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email on the user's behalf."""
    return ""


AGENT_TOOLS = [read_email, send_email]

model = ChatOpenAI(model="gpt-4o")
bound_model = model.bind_tools(AGENT_TOOLS)
