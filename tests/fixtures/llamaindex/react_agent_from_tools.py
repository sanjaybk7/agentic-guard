"""§3.1 — ReActAgent.from_tools(...) in a llama_index-importing file → one agent detected."""

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


def my_tool() -> str:
    """A simple tool."""
    return "result"


tool = FunctionTool.from_defaults(my_tool)
agent = ReActAgent.from_tools(tools=[tool], verbose=True)
