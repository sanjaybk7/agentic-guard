"""§5.1 — FunctionAgent(system_prompt=f"...{x}...") → system_prompt_is_dynamic=True, taint captured.

company is a function parameter — not resolvable as a static constant — so classify_prompt_expr
returns (True, ["company"]).
"""

from llama_index.core.agent.workflow import FunctionAgent


async def search(query: str) -> str:
    """Search for information."""
    return "results"


def make_agent(company: str) -> FunctionAgent:
    return FunctionAgent(
        name="Researcher",
        description="Research assistant",
        system_prompt=f"You are a research assistant for {company}. Answer questions accurately.",
        tools=[search],
    )
