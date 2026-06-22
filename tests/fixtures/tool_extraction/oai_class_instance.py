"""Stage 1 — OpenAI Agents: hosted tool class instances in tools=[...].

Before the refactor, ast.Call elements (hosted tool instantiations) were not
handled by the OpenAI Agents parser. After the refactor the callee base name is
recovered. WebSearchTool is a taxonomy-recognized SOURCE; FileSearchTool is not
in the taxonomy and resolves NEUTRAL — both must appear in the extracted list.
"""

from agents import Agent, FileSearchTool, WebSearchTool

agent = Agent(
    name="research-agent",
    instructions="You are a research assistant.",
    tools=[WebSearchTool(), FileSearchTool(vector_store_ids=["vs_1"])],
    model="gpt-4o",
)
