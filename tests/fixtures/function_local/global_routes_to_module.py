"""§23 — ``global X`` declaration writes through to module scope;
in-function assignment via ``global`` demotes module-scope's binding
to dynamic (parallel to ``nonlocal_routes_outward.py``).

Rewritten per fixture-matrix review: the original fixture only
exercised the global-read case, which was indistinguishable from
Fix 1's normal module-scope resolution — §23's global branch was
under-tested.

Two functions in the same fixture:

* ``make_agent_routed`` declares ``global PROMPT`` and reads it. By
  itself, this is a no-op (Python would resolve module-scope PROMPT
  with or without the global declaration).
* ``make_agent_writes`` declares ``global PROMPT`` AND assigns
  ``PROMPT = "..."``. Per §23's implementation sketch (§5.3 in the
  design doc): the assignment writes to module scope; module-scope's
  PROMPT becomes effectively multi-assigned (the module-scope
  initializer plus this write); the binding is demoted to dynamic.

Both agents reference PROMPT. Both must fire IG002 because the
module-scope PROMPT no longer resolves once ``make_agent_writes`` has
demoted it. If §23's demotion logic isn't implemented, ``make_agent_routed``
silently resolves via Fix 1's module-scope path — and this fixture
catches that gap.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


PROMPT = "module-level literal"


def make_agent_routed():
    """Reads module-scope PROMPT via the ``global`` declaration."""
    global PROMPT
    return Agent(
        name="global-routed",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )


def make_agent_writes():
    """Writes module-scope PROMPT via the ``global`` declaration.

    This write demotes module-scope PROMPT to dynamic. The Agent
    constructed here, and also the one constructed by
    ``make_agent_routed``, lose their resolution.
    """
    global PROMPT
    PROMPT = "rebinding via global declaration"
    return Agent(
        name="global-writes",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
