"""§3 — method body is a function scope; local literal binding resolves.

A method is just a function with ``self`` as first argument; its body
participates in function-scope resolution like any other function body.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class AgentFactory:
    def make(self):
        PROMPT = "You are a helpful assistant."
        return Agent(
            name="method-local",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
