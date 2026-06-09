"""§3.3 — Two FunctionAgent + AgentWorkflow → exactly 2 agents detected, NOT 3.

AgentWorkflow is an orchestrator that references already-detected FunctionAgent
instances by variable name. The parser must not count it as a third agent.
"""

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent


async def search(query: str) -> str:
    """Search the web."""
    return "results"


async def write_report(content: str) -> str:
    """Write a report."""
    return "written"


browser_agent = FunctionAgent(
    name="BrowserAgent",
    description="Browses the web",
    tools=[search],
)

writer_agent = FunctionAgent(
    name="WriterAgent",
    description="Writes reports",
    tools=[write_report],
)

# AgentWorkflow wraps already-detected agents — must NOT be counted as agent #3.
workflow = AgentWorkflow(
    agents=[browser_agent, writer_agent],
    root_agent=browser_agent.name,
)
