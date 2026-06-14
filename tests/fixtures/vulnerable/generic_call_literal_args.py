"""Vulnerable (corrected behavior): a generic non-allowlisted function
called with only literal arguments.

The pre-KL-002-narrow rule silenced this — wrongly, because the engine
has no visibility into what an arbitrary callable returns. The correct
default for any non-allowlisted callable is Dynamic: callers can extend
``STATIC_COMPOSER_FUNCTIONS`` to opt specific verified-static composers
in, but the default must stay conservative.

``fetch_or_compose`` is illustrative — it could read a file, query a DB,
or compose a literal; the engine can't tell. The conservative answer is
to assume it might be dynamic. IG002 MUST fire on this fixture.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def lookup(key: str) -> str:
    """Look up a value."""
    return ""


def fetch_or_compose(name: str) -> str:
    """Engine can't see the body — could read a file, hit an API, or compose a literal."""
    return f"You are {name}."


agent = create_react_agent(
    model="claude-opus-4-7",
    tools=[lookup],
    prompt=fetch_or_compose("an assistant"),
)
