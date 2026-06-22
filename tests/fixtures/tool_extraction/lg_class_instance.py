"""Stage 1 — LangGraph: class-instance tools in tools=[...].

Before the refactor, ast.Call elements (class instantiations) in the tools list
were not handled at all by the LangGraph parser. After the refactor the callee
base name is recovered via call_base_name.

ScrapeWebsiteTool is a taxonomy-recognized SOURCE; PythonREPLTool is not in the
taxonomy and resolves NEUTRAL — both must still appear in the extracted list.
"""

from langchain_community.tools import ScrapeWebsiteTool
from langchain_experimental.tools import PythonREPLTool
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model="claude-opus-4-7",
    tools=[ScrapeWebsiteTool(), PythonREPLTool()],
    prompt="You are a research assistant.",
)
