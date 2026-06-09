"""§3.1 — OpenAIAgent.from_tools(...) in a llama_index-importing file → one agent detected."""

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool


def get_weather(location: str) -> float:
    """Get current weather for a location."""
    return 72.0


tool = FunctionTool.from_defaults(get_weather, name="get_weather")
agent = OpenAIAgent.from_tools(tools=[tool], verbose=True)
