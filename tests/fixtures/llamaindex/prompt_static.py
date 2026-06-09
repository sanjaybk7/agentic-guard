"""§5.1 — FunctionAgent(system_prompt="literal string") → system_prompt_is_dynamic=False."""

from llama_index.core.agent.workflow import FunctionAgent


async def search(query: str) -> str:
    """Search for information."""
    return "results"


agent = FunctionAgent(
    name="Researcher",
    description="Research assistant",
    system_prompt="You are a research assistant. Answer questions thoroughly and accurately.",
    tools=[search],
)
