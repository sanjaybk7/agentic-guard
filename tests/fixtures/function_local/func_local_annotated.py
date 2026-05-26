"""§9 — annotated assignment ``X: str = "..."`` resolves like plain assignment."""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT: str = "You are a helpful assistant."
    return Agent(
        name="func-local-annotated",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
