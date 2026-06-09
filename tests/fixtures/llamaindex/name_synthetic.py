"""§6 — from_tools(...) with no name= kwarg → synthetic name agent_N."""

from llama_index.core.agent import ReActAgent


async def search(query: str) -> str:
    """Search for information."""
    return "results"


# from_tools agents have no name= kwarg — parser must synthesise agent_1.
agent = ReActAgent.from_tools(tools=[search], verbose=True)
