"""§9 (amended) — ``Final[str]`` and bare ``Final`` annotation forms.

PEP 591 ``typing.Final`` annotations communicate even stronger single-
binding intent than plain annotations. The annotation form does not
change the binding rule; the annotation field is parsed but ignored
for binding extraction.
"""

from typing import Final

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent_final_subscript():
    PROMPT: Final[str] = "literal under Final[str]"
    return Agent(
        name="final-subscript",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )


def make_agent_final_bare():
    OTHER: Final = "literal under bare Final"
    return Agent(
        name="final-bare",
        instructions=OTHER,
        tools=[lookup],
        model="gpt-4o",
    )
