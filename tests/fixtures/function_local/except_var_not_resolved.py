"""§24 + §17 — exception-handler ``as e`` syntax must not crash the
analyzer, and bindings in try/except bodies still follow §17 (don't
resolve).

Rewritten per fixture-matrix review: the original fixture passed
``instructions=e`` (exception object), which was tautologically not a
string-literal candidate — the assertion would pass regardless of any
§24 logic. This version makes the test substantive:

* The except body binds a normal PROMPT literal and constructs the
  Agent with it. Per §17 (try/except body bindings don't resolve),
  PROMPT must not resolve → IG002 fires.
* The exception variable ``e`` is bound by ``as e`` and is referenced
  in the log call, so the binding-extractor genuinely walks past
  ``ast.ExceptHandler.name``. §24 says ``e`` is bound to the exception
  object (never a string) and must not be tracked as a literal — that
  invariant is implicitly verified: if ``e`` were somehow tracked as
  a literal, downstream resolution would behave incorrectly.
* The §24 crash-protection invariant: if the analyzer's function-
  scope walker chokes on ``ast.ExceptHandler``, scan() raises and the
  test errors before the assertion runs.
"""

import logging

from agents import Agent, function_tool

log = logging.getLogger(__name__)


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        log.warning("recovered from %r", e)  # e is genuinely referenced
        PROMPT = "literal in except body"
        return Agent(
            name="except-var",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
    return None
