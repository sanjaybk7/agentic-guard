"""§4.1 — from_tools([a, b], ...) positional literal ast.List → both tools extracted.

The first positional arg IS a literal list (not a variable name). _find_tools_arg
returns node.args[0] = ast.List([...]), which IS extractable. Confirms args[0] is
read when it contains a literal list.
"""

from llama_index.core.agent import ReActAgent


async def search_web(query: str) -> str:
    """Search the web for information."""
    return "results"


async def read_email() -> str:
    """Read emails from the inbox."""
    return "emails"


# Literal list passed as positional arg — args[0] is an ast.List.
agent = ReActAgent.from_tools([search_web, read_email], verbose=True)
