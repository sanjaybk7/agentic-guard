"""§4.2 — [bare_fn, SearchTools.fetch, FunctionTool.from_defaults(fn)] → all three extracted.

The three ast element forms:
  - ast.Name  → bare_fn          extracted as "bare_fn"
  - ast.Attribute → SearchTools.fetch  extracted as "fetch"
  - ast.Call  → FunctionTool.from_defaults(fn)  extracted via call_base_name → "from_defaults"
"""

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from my_tools import (
    SearchTools,
)


def bare_fn() -> str:
    """A bare function passed directly as a tool."""
    return "result"


def fn() -> str:
    """Inner function wrapped by FunctionTool."""
    return "result"


agent = ReActAgent.from_tools(
    tools=[bare_fn, SearchTools.fetch, FunctionTool.from_defaults(fn)],
    verbose=True,
)
