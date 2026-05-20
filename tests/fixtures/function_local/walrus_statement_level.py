"""§11 — walrus operator at statement level (``ast.Expr`` wrapping
``ast.NamedExpr``) resolves.

Per the §11 amendment, walrus bindings resolve only when they appear at
statement level — not inside boolean short-circuits, ternary
expressions, or comprehension filters.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    (PROMPT := "literal via statement-level walrus")
    return Agent(
        name="walrus-statement-level",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
