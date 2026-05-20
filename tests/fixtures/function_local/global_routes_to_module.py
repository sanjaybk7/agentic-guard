"""§23 — ``global X`` declaration routes lookup to module scope; if module
scope has a single literal, the reference resolves.

Inside ``make_agent``, ``global PROMPT`` declares that PROMPT refers to
the module-scope binding. No in-function assignment, so module-scope's
PROMPT stays singly-bound and resolves via Fix 1's ModuleContext.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


PROMPT = "module-level literal"


def make_agent():
    global PROMPT
    return Agent(
        name="global-routes-to-module",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
