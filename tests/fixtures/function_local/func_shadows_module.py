"""§25 — function-local binding shadows module-scope dynamic binding.

Module-scope PROMPT is the result of a function call (non-literal) and
does NOT resolve via Fix 1's ModuleContext. The function-local PROMPT
is a literal. Per LEGB (and §25 / §4.1), function-local wins; the
in-function Agent reference to PROMPT resolves to the function-local
literal → IG002 silent.

If the analyzer walks module scope first and finds the dynamic value
(ignoring the function-local shadow), IG002 would fire — this fixture
catches that bug-mode.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def _build() -> str:
    return "dynamic from module"


PROMPT = _build()  # module-scope: dynamic, will not resolve via Fix 1


def make_agent():
    PROMPT = "function-local literal"
    return Agent(
        name="shadow-module",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
