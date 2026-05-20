"""§2 — ``async def`` body behaves identically to plain ``def``.

PEP 492's async keyword changes nothing about name binding. The same
code path that handles ``ast.FunctionDef`` must accept
``ast.AsyncFunctionDef``.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


async def make_agent():
    PROMPT = "You are a helpful assistant."
    return Agent(
        name="func-local-async",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
