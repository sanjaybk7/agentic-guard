"""§4a — cross-function pollution prevention (the keystone test).

Two sibling functions in the same file:

* ``function_a`` binds PROMPT to a literal locally. Its Agent's PROMPT
  must resolve via ``function_a``'s scope → IG002 silent.
* ``function_b`` does NOT bind PROMPT locally and PROMPT is not in
  module scope either. Its Agent's PROMPT must NOT silently resolve
  to ``function_a``'s value (the failure mode this fixture guards
  against) → IG002 fires on ``function_b``.

Implementation correctness requirement from §4a:
  * Each FunctionScope is a fresh instance per function visit.
  * Push/pop discipline must be bracketed by try/finally so a parser
    exception cannot leave a polluted stack.
  * On exit from a function, the popped scope is discarded.

If the analyzer reuses a mutable scope dict across sibling functions
without resetting between visits, ``function_b``'s lookup of PROMPT
would find ``function_a``'s value and IG002 would silently disappear
from ``function_b``. The test asserts the precise finding-count split
(1 from function_b, 0 from function_a) so either-direction breakage
is caught.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def function_a():
    PROMPT = "from function_a only"
    return Agent(
        name="sibling-a",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )


def function_b():
    # function_b does NOT bind PROMPT. The reference below should be
    # unresolved; IG002 must fire on this Agent specifically.
    return Agent(
        name="sibling-b",
        instructions=PROMPT,  # noqa: F821 (intentionally unresolved)
        tools=[lookup],
        model="gpt-4o",
    )
