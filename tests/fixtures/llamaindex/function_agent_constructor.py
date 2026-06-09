"""§3.2 — FunctionAgent(name=..., tools=[...]) constructor → detected, name from name= kwarg."""

from llama_index.core.agent.workflow import FunctionAgent


async def navigate_to(url: str) -> str:
    """Navigate to a URL."""
    return f"Navigated to {url}"


agent = FunctionAgent(
    name="BrowserAgent",
    description="Browses the web and retrieves information",
    system_prompt="You are a web browsing agent. Navigate to URLs and retrieve content.",
    tools=[navigate_to],
)
