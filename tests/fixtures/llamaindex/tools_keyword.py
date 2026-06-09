"""§4.1 — from_tools(tools=[a, b]) keyword form → both tools extracted."""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    """Search the web for information."""
    return "results"


async def read_email() -> str:
    """Read emails from the inbox."""
    return "emails"


agent = ReActAgent.from_tools(tools=[search_web, read_email], verbose=True)
