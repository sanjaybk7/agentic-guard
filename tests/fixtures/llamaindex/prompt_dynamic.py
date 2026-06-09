"""§5.1 — FunctionAgent(system_prompt=f"...{x}...") → system_prompt_is_dynamic=True, taint captured."""

from llama_index.core.agent.workflow import FunctionAgent

company = "Acme Corp"


async def search(query: str) -> str:
    """Search for information."""
    return "results"


agent = FunctionAgent(
    name="Researcher",
    description="Research assistant",
    system_prompt=f"You are a research assistant for {company}. Answer questions accurately.",
    tools=[search],
)
