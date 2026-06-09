"""§5.2 — from_tools(chat_history=...) with no system_prompt= → dynamic=False, location=None.

This fixture encodes the v1 known gap: from_tools agents pass system context via
chat_history=, not system_prompt=. The parser cannot resolve the system text without
local-variable tracking. v1 emits system_prompt_is_dynamic=False and location=None.
The test asserts this documented behavior, locking the gap so it is visible.
"""

from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage

chat_history = [ChatMessage.from_str("You are a helpful assistant for developers.", role="system")]


async def search(query: str) -> str:
    """Search for information."""
    return "results"


agent = ReActAgent.from_tools(
    tools=[search],
    chat_history=chat_history,
    verbose=True,
)
