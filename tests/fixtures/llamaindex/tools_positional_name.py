"""§4.1/§4.3 — from_tools(tools_var, ...) positional ast.Name → agent emitted, tools=[].

The tool list is assembled in a variable and passed as the first positional arg.
_find_tools_arg finds node.args[0] = ast.Name('tools_list'), which is not an
ast.List/Tuple/Set, so no tool names are extracted. The agent must still be emitted.
"""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    """Search the web."""
    return "results"


async def read_email() -> str:
    """Read emails."""
    return "emails"


tools_list = [search_web, read_email]

# Positional arg is an ast.Name — not a literal list at the call site.
agent = ReActAgent.from_tools(tools_list, verbose=True)
