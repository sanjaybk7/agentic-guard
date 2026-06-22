"""LG-3 — LangGraph: ``bind_tools`` arguments that are NOT statically resolvable.

Both forms below must be left unextracted (no agent emitted) rather than guessed:
  - ``imported_tools`` comes from another module — resolving it would require
    cross-module list tracing, which is out of scope for LG-3.
  - ``a + b`` is a runtime concatenation, not a literal list.

A wrong attribution here would create a false-positive finding against an agent
whose real toolbox we cannot see, so the conservative choice is to skip.
"""

from langchain_openai import ChatOpenAI
from mytools import search_tools, write_tools
from somewhere.else_ import imported_tools

llm = ChatOpenAI(model="gpt-4o")

# Cross-module imported var — not a same-file literal.
runnable_a = llm.bind_tools(imported_tools)

# Runtime concatenation of two name lists — not a literal.
runnable_b = llm.bind_tools(search_tools + write_tools)
