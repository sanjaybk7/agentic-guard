"""LG-3 — LangGraph: tools declared via ``model.bind_tools([...])``.

This is the tool-calling LCEL idiom used in hand-built StateGraphs, where there
is no ``create_react_agent`` call at all — the bound model drives the agent loop
inside a graph node. Before LG-3 the scanner saw no agent here (no factory call),
so the read_email -> send_email confused-deputy pair was invisible. After LG-3
the inline ``bind_tools([...])`` list is treated as the agent's toolbox.

read_email / send_email are taxonomy-recognized SOURCE / SINK names so the test
asserts classification flowed through, not just that the name strings survived.
"""

from langchain_openai import ChatOpenAI


def read_email(message_id: str) -> str:  # NO @tool decorator
    """Fetch the body of an email by id."""
    return ""


def send_email(to: str, subject: str, body: str) -> str:  # NO @tool decorator
    """Send an email on the user's behalf."""
    return ""


llm = ChatOpenAI(model="gpt-4o")
assistant_runnable = llm.bind_tools([read_email, send_email])
