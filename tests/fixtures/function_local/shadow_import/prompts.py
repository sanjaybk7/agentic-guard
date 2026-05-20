"""Sibling module for §26 fixture: defines PROMPT dynamically so the
in-function literal in ``agent.py`` is meaningfully shadowing it.

If PROMPT here were a literal, the analyzer could resolve via Fix 1's
cross-module resolver without ever consulting function-local scope —
and the fixture would not actually test §26's shadowing rule. The
dynamic-from-import value ensures function-local resolution is the
only way for IG002 to stay silent.
"""


def _build() -> str:
    return "dynamic from sibling module"


PROMPT = _build()
