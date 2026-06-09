"""§3.1 Negative — receiver class NOT in {ReActAgent, OpenAIAgent, FunctionCallingAgent} → NOT detected.

This is the critical precision guard. Without the receiver-check predicate, any
SomeClass.from_tools(...) call in a llama_index-importing file would fire as a false
positive. The parser must verify BOTH func.attr == "from_tools" AND the receiver
class is in the agent receiver set.
"""

from llama_index.core.tools import FunctionTool  # noqa: F401 — triggers llama_index file match

ToolBuilder = None  # dummy class; NOT in {ReActAgent, OpenAIAgent, FunctionCallingAgent}
result = ToolBuilder.from_tools(tools=["tool1", "tool2"])
