"""Vulnerable (FN regression test): a closure-returning callable whose
inner closure interpolates external runtime state into the system prompt.

History: PR #12 introduced a broad "all-Names-resolve → static" rule for
generic Calls (KL-002). That rule had no visibility into what the called
function returned and silenced *any* function-call-with-literal-args,
including closure-returning ones whose closures capture external data
at invocation time. This was a false negative: in deployments that pass
real user input to the closure, IG002 would miss the dynamic prompt.

KL-002 was narrowed (kl002-narrow) to an explicit
``STATIC_COMPOSER_FUNCTIONS`` allowlist. ``make_prompt`` is NOT in the
allowlist; the generic-Call branch now stays dynamic; IG002 MUST fire on
this fixture. If IG002 ever stops firing here, the broad rule has been
reintroduced.

This fixture is the permanent regression test for that bug.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def lookup(key: str) -> str:
    """Look up a value."""
    return ""


def make_prompt(base: str):
    """Returns a closure that captures external runtime state."""

    def closure(state, config):
        # External content interpolated into the system prompt at call time
        user_input = state["user_input"]
        return base + "\n\nUser said: " + user_input

    return closure


agent = create_react_agent(
    model="claude-opus-4-7",
    tools=[lookup],
    prompt=make_prompt("You are an assistant."),
)
