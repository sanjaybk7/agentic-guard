"""§26 — function-local binding shadows imported name.

``from prompts import PROMPT`` brings in a dynamic value (per the
sibling module's ``_build()`` call). The in-function ``PROMPT =
"literal"`` shadows the import. Per LEGB (and §4.2): function-local
wins → resolves → IG002 silent.

If the analyzer skips the function-local check and falls through to
the cross-module resolver, it would see the dynamic import binding
and IG002 would fire. This fixture catches that bug-mode.
"""

from agents import Agent, function_tool
from prompts import PROMPT  # noqa: F401  (intentionally shadowed below)


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT = "function-local literal"
    return Agent(
        name="shadow-import",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
