"""§7 — class bodies are out of scope for PR #5; class-attribute
resolution does NOT happen.

``Config.PROMPT`` is class-attribute access. Resolving it would require
class-body scoping (deferred per §7) plus a separate attribute-lookup
rule. For PR #5, ``ast.Attribute`` on a class name returns unresolved
→ IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class Config:
    PROMPT = "class-level literal"


def make_agent():
    return Agent(
        name="class-body-attr",
        instructions=Config.PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
