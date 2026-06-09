"""§6 — FunctionAgent(name="BrowserAgent") → agent.name == "BrowserAgent"."""

from llama_index.core.agent.workflow import FunctionAgent


async def navigate(url: str) -> str:
    """Navigate to a URL."""
    return f"at {url}"


agent = FunctionAgent(
    name="BrowserAgent",
    description="Browses the web",
    tools=[navigate],
)
