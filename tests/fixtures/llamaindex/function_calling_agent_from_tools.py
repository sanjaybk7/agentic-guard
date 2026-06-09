"""§3.1/§8.2 — FunctionCallingAgent.from_tools(...) → one agent detected.

Tests the §8.2 "documented-but-unseen" class: included in the receiver set at zero
marginal cost; this fixture verifies it works when encountered.
"""

from llama_index.core.agent import FunctionCallingAgent
from llama_index.core.tools import FunctionTool


def search(query: str) -> str:
    """Search for information."""
    return "results"


tool = FunctionTool.from_defaults(search)
agent = FunctionCallingAgent.from_tools(tools=[tool], verbose=True)
