# PR #5 — fixture inventory

Generated artifact: concatenates every function-local fixture file and
the test file into one document for review. Regenerable from disk;
committed on the `fix-3-function-local-binding` branch as a permanent
reference for fixture-matrix sign-off (mirrors PR #4's
`PR-4-fixture-inventory.md` pattern).

---

## tests/test_function_local_binding.py

```python
"""Tests for PR #5 — function-local literal binding.

Decisions per the locked design doc at
``docs/design/PR-3-function-local-scoping.md`` (branch name preserved
for git history; PR is numbered #5 in the v0.2 sequence).

Red half of TDD: on the current branch (decisions locked but no
behavioral commits yet) the positive tests fail because function-local
resolution doesn't exist; the negative tests pass for the wrong reason
(no function-local resolution = no resolution at all = IG002 fires).
After implementation, positives pass for the right reason and negatives
continue to pass for the right reason — each negative case has at
least one disqualifying property that survives even when function-
local resolution works in general.

Each test references the design-doc § that governs its decision.
"""

from __future__ import annotations

from pathlib import Path

from agentic_guard.engine import Scanner

FIXTURES = Path(__file__).parent / "fixtures" / "function_local"


def _rule_ids(target: Path) -> set[str]:
    return {f.rule_id for f in Scanner(include_tests=True).scan(target).findings}


def _findings(target: Path) -> list:
    return list(Scanner(include_tests=True).scan(target).findings)


# -------- §1 / §15 / §21 — Plain function bodies + reassignment ----------


def test_func_local_basic_resolves() -> None:
    """§1 — plain ``def`` body in scope; single literal binding resolves."""
    assert "IG002" not in _rule_ids(FIXTURES / "func_local_basic.py"), (
        "§1/§15 plain function-local literal resolution regressed"
    )


def test_func_local_reassigned_does_not_resolve() -> None:
    """§21 — reassignment within function disqualifies the name (multi-assign drop)."""
    assert "IG002" in _rule_ids(FIXTURES / "func_local_reassigned.py"), (
        "§21 multi-binding-drops-the-name policy; expected IG002 to fire"
    )


# -------- §2 — Async function bodies -------------------------------------


def test_func_local_async_resolves() -> None:
    """§2 — ``async def`` behaves identically to plain ``def``."""
    assert "IG002" not in _rule_ids(FIXTURES / "func_local_async.py"), (
        "§2 async function-local literal resolution regressed"
    )


# -------- §3 — Methods inside classes ------------------------------------


def test_method_local_resolves() -> None:
    """§3 — method body is in-scope; local literal in ``def`` method resolves."""
    assert "IG002" not in _rule_ids(FIXTURES / "method_local.py"), (
        "§3 method-body function-local resolution regressed"
    )


def test_self_attribute_does_not_resolve() -> None:
    """§3 — ``self.x = "..."`` is attribute assignment, not local binding."""
    assert "IG002" in _rule_ids(FIXTURES / "self_attribute_not_resolved.py"), (
        "§3 self.x attribute resolution must remain out-of-scope; IG002 expected"
    )


# -------- §4 — Closures --------------------------------------------------


def test_closure_outer_binding_resolves() -> None:
    """§4 — closure walks outward through enclosing function scopes."""
    assert "IG002" not in _rule_ids(FIXTURES / "closure_outer_binding.py"), (
        "§4 closure-walk-outward to outer function's literal regressed"
    )


def test_closure_inner_rebinds_does_not_resolve() -> None:
    """§4 + §21 — inner shadows outer; inner is multi-assigned → no resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "closure_inner_rebinds.py"), (
        "§4 shadowing + §21 multi-assign should leave IG002 firing"
    )


# -------- §5 — Lambdas (structural) --------------------------------------


def test_lambda_presence_does_not_crash_analyzer() -> None:
    """§5 — lambdas cannot contain statements, so no bindings inside them.

    Two distinct guarantees this fixture exercises, separately:

    1. The analyzer does NOT crash during ``scan()`` when lambdas are
       present in module or function scope. A crash here surfaces as
       a test error (raised exception) before any assertion runs;
       this guarantee is verified by the absence of such an exception,
       not by the assertion below.
    2. The Agent's reference to a module-level literal is unaffected
       by lambda presence — Fix 1's module-scope resolution still
       works around lambda nodes. The assertion below verifies this.

    Each guarantee catches a different bug-mode; the no-crash one is
    structural (surfaces as test error), the resolution one is
    behavioral (surfaces as assertion failure).
    """
    rule_ids = _rule_ids(FIXTURES / "lambda_structural.py")
    assert "IG002" not in rule_ids, (
        "§5 lambda presence should not affect Fix 1's module-scope resolution"
    )


# -------- §6 — Comprehensions --------------------------------------------


def test_comp_uses_outer_resolves() -> None:
    """§6 — comprehension reads outer-scope binding via LEGB; resolves."""
    assert "IG002" not in _rule_ids(FIXTURES / "comp_uses_outer.py"), (
        "§6 comprehension reading outer-scope literal regressed"
    )


def test_comp_iter_var_does_not_resolve() -> None:
    """§6 — comprehension iteration variable is comp-local; not extracted."""
    assert "IG002" in _rule_ids(FIXTURES / "comp_iter_var_not_resolved.py"), (
        "§6 comp-local iteration variable must not resolve; IG002 expected"
    )


# -------- §7 — Class bodies (out of scope) -------------------------------


def test_class_body_attribute_does_not_resolve() -> None:
    """§7 — class bodies out of scope; ``Config.PROMPT`` does not resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "class_body_attr_not_resolved.py"), (
        "§7 class-attribute lookup must remain out-of-scope; IG002 expected"
    )


# -------- §9 — Annotated + Final ------------------------------------------


def test_func_local_annotated_resolves() -> None:
    """§9 — ``X: str = "..."`` resolves like plain assignment."""
    assert "IG002" not in _rule_ids(FIXTURES / "func_local_annotated.py"), (
        "§9 annotated assignment resolution regressed"
    )


def test_func_local_final_resolves() -> None:
    """§9 (amended) — ``Final[str]`` and bare ``Final`` both resolve.

    Fixture has two functions, one per Final variant; neither should
    fire IG002.
    """
    assert "IG002" not in _rule_ids(FIXTURES / "func_local_final.py"), (
        "§9 amended Final[str] / bare Final resolution regressed"
    )


# -------- §11 — Walrus ---------------------------------------------------


def test_walrus_statement_level_resolves() -> None:
    """§11 — walrus at statement level resolves."""
    assert "IG002" not in _rule_ids(FIXTURES / "walrus_statement_level.py"), (
        "§11 statement-level walrus resolution regressed"
    )


def test_walrus_in_boolean_expr_does_not_resolve() -> None:
    """§11 (amended) — walrus inside boolean short-circuit doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "walrus_in_boolean_expr.py"), (
        "§11 amended: walrus inside boolean expression must not resolve"
    )


def test_walrus_in_ternary_does_not_resolve() -> None:
    """§11 (amended) — walrus inside ternary doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "walrus_in_ternary.py"), (
        "§11 amended: walrus inside ternary must not resolve"
    )


# -------- §12 — Tuple unpacking ------------------------------------------


def test_tuple_unpack_all_literals_resolves() -> None:
    """§12 — tuple unpacking with all-literal RHS resolves."""
    assert "IG002" not in _rule_ids(FIXTURES / "tuple_unpack_all_literals.py"), (
        "§12 all-literal tuple unpacking resolution regressed"
    )


def test_tuple_unpack_mixed_does_not_resolve() -> None:
    """§12 (amended) — all-or-nothing: mixed RHS skips entire unpacking."""
    assert "IG002" in _rule_ids(FIXTURES / "tuple_unpack_mixed.py"), (
        "§12 amended: mixed-RHS tuple unpacking must not partially resolve"
    )


def test_tuple_unpack_call_rhs_does_not_resolve() -> None:
    """§12 — tuple unpacking from a function call RHS doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "tuple_unpack_call_rhs.py"), (
        "§12 function-call-RHS tuple unpacking must not resolve"
    )


# -------- §13 — Chained assignment ---------------------------------------


def test_chained_assignment_resolves_both() -> None:
    """§13 — ``X = Y = "..."`` resolves both targets."""
    assert "IG002" not in _rule_ids(FIXTURES / "chained_assignment.py"), (
        "§13 chained assignment resolution regressed (both X and Y must resolve)"
    )


# -------- §14 — Starred unpacking (negative) -----------------------------


def test_starred_unpack_does_not_resolve() -> None:
    """§14 — starred unpacking entire-skip rule."""
    assert "IG002" in _rule_ids(FIXTURES / "starred_unpack_not_resolved.py"), (
        "§14 starred unpacking must skip entire unpacking; IG002 expected"
    )


# -------- §16 — if branches (negative) -----------------------------------


def test_if_branch_does_not_resolve() -> None:
    """§16 — assignment inside ``if`` branch doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "if_branch_not_resolved.py"), (
        "§16 conditional binding inside if branch must not resolve"
    )


def test_if_all_branches_same_literal_does_not_resolve_deferred() -> None:
    """§16 (deferred enhancement documented) — even symmetric all-branches case."""
    assert (
        "IG002"
        in _rule_ids(FIXTURES / "if_all_branches_same_literal_still_not_resolved.py")
    ), (
        "§16 deferred enhancement: all-branches-same-literal must still not resolve "
        "in PR #5"
    )


# -------- §17 — try/except (negative) ------------------------------------


def test_try_branch_does_not_resolve() -> None:
    """§17 — assignment inside ``try``/``except`` body doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "try_branch_not_resolved.py"), (
        "§17 try/except function-scope binding must not resolve"
    )


# -------- §18 — with block (negative) ------------------------------------


def test_with_block_does_not_resolve() -> None:
    """§18 (amended) — assignment inside ``with`` block doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "with_block_not_resolved.py"), (
        "§18 amended: with-block binding must not resolve"
    )


# -------- §19 — for loop (negative) --------------------------------------


def test_for_loop_does_not_resolve() -> None:
    """§19 — assignment inside ``for`` loop body doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "for_loop_not_resolved.py"), (
        "§19 for-loop-body binding must not resolve"
    )


# -------- §20 — while loop (negative) ------------------------------------


def test_while_loop_does_not_resolve() -> None:
    """§20 — assignment inside ``while`` loop body doesn't resolve."""
    assert "IG002" in _rule_ids(FIXTURES / "while_loop_not_resolved.py"), (
        "§20 while-loop-body binding must not resolve"
    )


# -------- §22 — Parameter shadowing (negative) ---------------------------


def test_param_shadow_does_not_resolve() -> None:
    """§22 — parameter is first binding; in-function assignment is reassignment."""
    assert "IG002" in _rule_ids(FIXTURES / "param_shadow_not_resolved.py"), (
        "§22 parameter+in-function-assign must demote to dynamic"
    )


def test_param_shadow_with_literal_default_does_not_resolve() -> None:
    """§22 (amended) — rule applies even when parameter default is a literal."""
    assert (
        "IG002"
        in _rule_ids(FIXTURES / "param_shadow_with_literal_default.py")
    ), (
        "§22 amended: rule applies regardless of whether parameter default is a literal"
    )


# -------- §23 — nonlocal / global ----------------------------------------


def test_nonlocal_demotes_outer_binding() -> None:
    """§23 — ``nonlocal X`` + assignment in inner demotes outer's X to dynamic."""
    assert "IG002" in _rule_ids(FIXTURES / "nonlocal_routes_outward.py"), (
        "§23 nonlocal+write must demote outer's binding to dynamic"
    )


def test_global_with_in_function_write_demotes_module_scope() -> None:
    """§23 — ``global X`` + in-function write demotes module-scope X to dynamic.

    Rewritten per fixture-matrix review: the previous test only
    exercised the global-read case (indistinguishable from Fix 1's
    normal module-scope resolution), under-testing §23.

    Fixture has two functions sharing the same module-scope PROMPT:
    one reads via ``global``, one writes via ``global``. The write
    demotes module-scope PROMPT to dynamic (parallel to
    ``nonlocal_routes_outward``'s outer-scope demotion). Both agents
    must fire IG002 because PROMPT no longer resolves.
    """
    findings = _findings(FIXTURES / "global_routes_to_module.py")
    ig002 = [f for f in findings if f.rule_id == "IG002"]
    routed = [f for f in ig002 if "global-routed" in f.message]
    writes = [f for f in ig002 if "global-writes" in f.message]
    assert len(routed) == 1, (
        f"§23 global-routed agent must fire IG002 (module-scope PROMPT "
        f"demoted by sibling's write); got {len(routed)} findings"
    )
    assert len(writes) == 1, (
        f"§23 global-writes agent must fire IG002 (write demotes the "
        f"binding it then reads); got {len(writes)} findings"
    )


# -------- §24 — Exception variable (negative) ----------------------------


def test_except_var_does_not_resolve() -> None:
    """§24 — exception variable bound to exception object, not a string."""
    assert "IG002" in _rule_ids(FIXTURES / "except_var_not_resolved.py"), (
        "§24 except-handler-bound name must remain out-of-scope"
    )


# -------- §25 — Shadow module-level --------------------------------------


def test_func_local_shadows_module_dynamic() -> None:
    """§25 — function-local literal shadows module-scope dynamic binding.

    Module-scope PROMPT is a function-call result (dynamic). Function-
    local PROMPT is a literal. Per LEGB, function-local wins → resolves.
    If analyzer ignores function-local and walks module-first, IG002
    would fire (caught by this assertion).
    """
    assert "IG002" not in _rule_ids(FIXTURES / "func_shadows_module.py"), (
        "§25 function-local must shadow module-scope dynamic; IG002 should be silent"
    )


# -------- §26 — Shadow imported (sub-package) ----------------------------


def test_func_local_shadows_imported_dynamic() -> None:
    """§26 — function-local literal shadows imported (dynamic) binding.

    The sub-package ``shadow_import/`` contains a sibling ``prompts.py``
    that defines PROMPT dynamically. ``agent.py`` imports PROMPT and
    shadows it with a function-local literal. Per LEGB, function-local
    wins → resolves → IG002 silent.

    Bug-mode this catches: analyzer falls through to cross-module
    resolver (which sees the dynamic import) and reports IG002
    incorrectly.
    """
    assert "IG002" not in _rule_ids(FIXTURES / "shadow_import"), (
        "§26 function-local must shadow imported binding; IG002 should be silent"
    )


# -------- §4a — Cross-function pollution prevention (keystone) -----------


def test_sibling_functions_isolated() -> None:
    """§4a — sibling functions in the same file must not share scope.

    ``function_a`` binds PROMPT to a literal; its Agent must resolve.
    ``function_b`` does NOT bind PROMPT and must NOT see ``function_a``'s
    binding via stale scope state; its Agent's PROMPT must remain
    unresolved (IG002 fires on ``function_b`` only).

    The two assertions check the precise finding-count split — if
    function_a's PROMPT leaks into function_b's scope, IG002 silently
    disappears from function_b and this test catches it.
    """
    findings = _findings(FIXTURES / "sibling_functions_isolated.py")
    ig002 = [f for f in findings if f.rule_id == "IG002"]

    # IG002 messages name the agent (via the `name=...` kwarg captured
    # into ``agent.name`` in the IR), so we bucket findings by message
    # content rather than line-number ranges (which are fragile to edits).
    a_findings = [f for f in ig002 if "sibling-a" in f.message]
    b_findings = [f for f in ig002 if "sibling-b" in f.message]

    assert len(a_findings) == 0, (
        f"§4a function_a's Agent must resolve PROMPT to its own literal; "
        f"unexpected IG002 findings on sibling-a: "
        f"{[f.message for f in a_findings]}"
    )
    assert len(b_findings) == 1, (
        f"§4a function_b's Agent must NOT see function_a's PROMPT; "
        f"expected exactly one IG002 finding on sibling-b, got {len(b_findings)}"
    )
```

---

## Fixture directory tree (tests/fixtures/function_local/)

```
.
chained_assignment.py
class_body_attr_not_resolved.py
closure_inner_rebinds.py
closure_outer_binding.py
comp_iter_var_not_resolved.py
comp_uses_outer.py
except_var_not_resolved.py
for_loop_not_resolved.py
func_local_annotated.py
func_local_async.py
func_local_basic.py
func_local_final.py
func_local_reassigned.py
func_shadows_module.py
global_routes_to_module.py
if_all_branches_same_literal_still_not_resolved.py
if_branch_not_resolved.py
lambda_structural.py
method_local.py
nonlocal_routes_outward.py
param_shadow_not_resolved.py
param_shadow_with_literal_default.py
self_attribute_not_resolved.py
shadow_import
    agent.py
    prompts.py
sibling_functions_isolated.py
starred_unpack_not_resolved.py
try_branch_not_resolved.py
tuple_unpack_all_literals.py
tuple_unpack_call_rhs.py
tuple_unpack_mixed.py
walrus_in_boolean_expr.py
walrus_in_ternary.py
walrus_statement_level.py
while_loop_not_resolved.py
with_block_not_resolved.py
```

---

## Every fixture .py file

### `tests/fixtures/function_local/chained_assignment.py`

```python
"""§13 — chained assignment ``X = Y = "..."`` resolves both targets to
the same literal.

Two agents, one per chained target, both must resolve.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent_x():
    X = Y = "shared literal"
    return Agent(
        name="chained-x",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )


def make_agent_y():
    X = Y = "shared literal"
    return Agent(
        name="chained-y",
        instructions=Y,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/class_body_attr_not_resolved.py`

```python
"""§7 — class bodies are out of scope for PR #5; class-attribute
resolution does NOT happen.

``Config.PROMPT`` is class-attribute access. Resolving it would require
class-body scoping (deferred per §7) plus a separate attribute-lookup
rule. For PR #5, ``ast.Attribute`` on a class name returns unresolved
→ IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class Config:
    PROMPT = "class-level literal"


def make_agent():
    return Agent(
        name="class-body-attr",
        instructions=Config.PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/closure_inner_rebinds.py`

```python
"""§4 + §21 — inner function rebinds the name: no closure, multi-assign in inner.

Inner has its own PROMPT (assigned twice). Outer's PROMPT is shadowed by
inner's local. Inner's PROMPT is multi-assigned (per §21) so it doesn't
resolve. IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "outer literal"

    def inner():
        PROMPT = "inner first"
        PROMPT = "inner second"
        return Agent(
            name="closure-inner-rebinds",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
```

### `tests/fixtures/function_local/closure_outer_binding.py`

```python
"""§4 — closures walk outward through enclosing function scopes.

Inner function reads outer's PROMPT (closure capture). Per Python LEGB,
inner sees outer's binding because inner does not rebind PROMPT.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "literal in outer scope"

    def inner():
        return Agent(
            name="closure-outer",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
```

### `tests/fixtures/function_local/comp_iter_var_not_resolved.py`

```python
"""§6 — comprehension iteration variable is comp-local and rebound per
iteration; does NOT resolve via function-local scope.

``p`` is bound to a different literal on each iteration. Even though
every value is a literal, ``p`` itself is comp-local and PR #5 does not
extract bindings from comprehensions. Conservative default: IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agents():
    return [
        Agent(
            name=f"comp-iter-var-{i}",
            instructions=p,
            tools=[lookup],
            model="gpt-4o",
        )
        for i, p in enumerate(["alpha", "beta", "gamma"])
    ]
```

### `tests/fixtures/function_local/comp_uses_outer.py`

```python
"""§6 — comprehension body references outer-scope binding; resolves.

PROMPT is function-local; the comprehension reads it from the enclosing
function scope (Python's LEGB rule naturally walks outward from
comprehension scope to function scope).
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agents():
    PROMPT = "shared system prompt"
    return [
        Agent(
            name=f"comp-uses-outer-{i}",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
        for i in range(3)
    ]
```

### `tests/fixtures/function_local/except_var_not_resolved.py`

```python
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
```

### `tests/fixtures/function_local/for_loop_not_resolved.py`

```python
"""§19 — assignment inside ``for`` loop body does NOT resolve.

Rebound on each iteration. Even when the RHS is a literal, the name's
lifetime spans multiple iterations and the analyzer shouldn't assert a
single value.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    for _i in range(1):
        PROMPT = "for-body literal"
    return Agent(
        name="for-body",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/func_local_annotated.py`

```python
"""§9 — annotated assignment ``X: str = "..."`` resolves like plain assignment."""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT: str = "You are a helpful assistant."
    return Agent(
        name="func-local-annotated",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/func_local_async.py`

```python
"""§2 — ``async def`` body behaves identically to plain ``def``.

PEP 492's async keyword changes nothing about name binding. The same
code path that handles ``ast.FunctionDef`` must accept
``ast.AsyncFunctionDef``.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


async def make_agent():
    PROMPT = "You are a helpful assistant."
    return Agent(
        name="func-local-async",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/func_local_basic.py`

```python
"""§1 / §15 — plain ``def`` body in scope; single literal binding resolves.

Baseline positive case: function defines PROMPT once, then constructs an
Agent using it. PR #5's function-local resolution must recognize PROMPT as
a static literal and silence IG002.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT = "You are a helpful assistant. Be concise."
    return Agent(
        name="func-local-basic",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/func_local_final.py`

```python
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
```

### `tests/fixtures/function_local/func_local_reassigned.py`

```python
"""§21 / §10 — reassignment within function disqualifies the name.

Multi-binding-drops-the-name policy: PROMPT is bound twice in the same
function scope, so PR #5's pre-pass drops it from the export set.
Resolution falls through to dynamic; IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    PROMPT = "first binding"
    PROMPT = "second binding"
    return Agent(
        name="func-local-reassigned",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/func_shadows_module.py`

```python
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
```

### `tests/fixtures/function_local/global_routes_to_module.py`

```python
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
```

### `tests/fixtures/function_local/if_all_branches_same_literal_still_not_resolved.py`

```python
"""§16 (deferred enhancement) — even when every branch binds the name to
the *same* literal, PR #5 does NOT resolve.

The "all branches assign literals" enhancement was considered and
explicitly deferred in §16. A branch-equivalence walker plus a
"set of possible literal values" representation would close this case,
but adds rule complexity not justified by corpus prevalence. This
fixture documents the deferred decision: any conditional binding,
including this symmetric case, falls through to dynamic.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(cond: bool):
    if cond:
        PROMPT = "both-branches identical literal"
    else:
        PROMPT = "both-branches identical literal"
    return Agent(
        name="if-all-branches-same",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/if_branch_not_resolved.py`

```python
"""§16 — assignment inside an ``if`` branch does NOT resolve.

The value is conditional on the branch taken; static analysis cannot
know which path executed. Conservative-on-doubt: do not resolve.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it. The
conditionality is genuinely opaque, mirroring real conditional bindings
in production code.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(cond: bool):
    if cond:
        PROMPT = "if-branch literal"
    return Agent(
        name="if-branch",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/lambda_structural.py`

```python
"""§5 — lambdas: language semantics prohibit statements inside, so no
bindings can live there. This fixture exists only to confirm the analyzer
doesn't crash when a lambda is in scope alongside the function-local
resolution code path.

The Agent here uses a module-level constant (already handled by Fix 1);
the lambda is irrelevant noise. If the analyzer crashes on lambda
descent, this fixture catches it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


# A lambda exists in module scope; PR #5 must not crash when it walks past.
PROMPT = "module-level literal"
_filter = lambda x: x > 0  # noqa: E731


def make_agent():
    # Also a lambda inside the function body.
    _local_filter = lambda x: x * 2  # noqa: E731
    return Agent(
        name="lambda-structural",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/method_local.py`

```python
"""§3 — method body is a function scope; local literal binding resolves.

A method is just a function with ``self`` as first argument; its body
participates in function-scope resolution like any other function body.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class AgentFactory:
    def make(self):
        PROMPT = "You are a helpful assistant."
        return Agent(
            name="method-local",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
```

### `tests/fixtures/function_local/nonlocal_routes_outward.py`

```python
"""§23 — ``nonlocal X`` declaration + assignment in inner demotes outer's X.

Per §5.3 of the design doc: when inner declares ``nonlocal X`` and
then assigns ``X = "literal"``, that assignment writes to the outer
function's X. We do not register it as a local binding in inner's
scope, and we mark the outer scope's X as "potentially-modified-by-inner"
→ demote to dynamic (same logic as multi-assign).

Outer's PROMPT (bound once initially, then rebound via inner's
nonlocal write) is effectively multi-assigned → drops from exports
→ IG002 fires when inner constructs the Agent with PROMPT.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def outer():
    PROMPT = "outer initial literal"

    def inner():
        nonlocal PROMPT
        PROMPT = "inner overrides outer"
        return Agent(
            name="nonlocal-routes-outward",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )

    return inner
```

### `tests/fixtures/function_local/param_shadow_not_resolved.py`

```python
"""§22 — function parameter establishes the first binding; in-function
assignment to the same name is the second binding → multi-assign drop.

The parameter ``X`` is bound at function entry; ``X = "literal"``
inside the body is reassignment. Per the multi-assign-drops-the-name
policy, X does not resolve.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(X: str = "default"):
    X = "in-function literal"
    return Agent(
        name="param-shadow",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/param_shadow_with_literal_default.py`

```python
"""§22 (amended) — rule applies even when the parameter's default value
is itself a string literal.

Per the §22 amendment: a naive multi-assign counter might be tempted
to say "both are literals, the second wins, unambiguous → resolve."
That reasoning would behave differently from the §22 case with a
non-literal default. The rule is fixed on "parameter is the first
binding; any in-function assignment is reassignment," independent of
what the default looks like.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(X: str = "default literal"):
    X = "another literal"
    return Agent(
        name="param-shadow-literal-default",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/self_attribute_not_resolved.py`

```python
"""§3 — ``self.x = "..."`` is attribute assignment, not local binding.

Resolving instance attributes would require flow analysis across methods,
inheritance, and class hierarchies — out of scope for PR #5. The
``instructions=self.prompt`` reference is an ``ast.Attribute`` that does
NOT resolve via function-local scope.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


class AgentHolder:
    def __init__(self):
        self.prompt = "instance attribute literal"
        self.agent = Agent(
            name="self-attribute",
            instructions=self.prompt,
            tools=[lookup],
            model="gpt-4o",
        )
```

### `tests/fixtures/function_local/shadow_import/agent.py`

```python
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
```

### `tests/fixtures/function_local/shadow_import/prompts.py`

```python
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
```

### `tests/fixtures/function_local/sibling_functions_isolated.py`

```python
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
```

### `tests/fixtures/function_local/starred_unpack_not_resolved.py`

```python
"""§14 — starred unpacking is out of scope; entire unpacking skipped.

Consistent with §12 (no partial resolution): a star in the target list
means neither the non-starred nor the starred name resolves.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    X, *REST = "a", "b", "c"
    return Agent(
        name="starred-unpack",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/try_branch_not_resolved.py`

```python
"""§17 — assignment inside ``try``/``except`` body does NOT resolve.

Unlike Fix 1's top-level module-scope exception (optional-dependency
pattern), function-scope try/except almost always wraps a runtime
operation, not an optional binding. No exception here: conditional
binding, fall through to dynamic.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    try:
        PROMPT = "try-branch literal"
    except Exception:
        PROMPT = "except-branch literal"
    return Agent(
        name="try-branch",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/tuple_unpack_all_literals.py`

```python
"""§12 — tuple unpacking with all-literal RHS resolves.

Both targets are simple names; the RHS is a Tuple of literals of equal
length. Position-wise matching gives each target a static value.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    SYS, FALLBACK = "primary literal", "secondary literal"
    return Agent(
        name="tuple-unpack-all-literals",
        instructions=SYS,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/tuple_unpack_call_rhs.py`

```python
"""§12 — tuple unpacking from a function call RHS does NOT resolve.

``X, Y = build_pair()`` — we cannot statically determine the RHS
contents. Skip the entire unpacking.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def build_pair() -> tuple[str, str]:
    return "a", "b"


def make_agent():
    X, _Y = build_pair()
    return Agent(
        name="tuple-unpack-call-rhs",
        instructions=X,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/tuple_unpack_mixed.py`

```python
"""§12 (amended) — tuple unpacking with mixed RHS skips entire unpacking.

All-or-nothing: ``SYS, OTHER = "lit", build()`` — even though SYS's
position is a literal, the whole tuple is rejected. SYS does not
resolve; IG002 fires.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def build_other() -> str:
    return "dynamic value"


def make_agent():
    SYS, OTHER = "primary literal", build_other()
    return Agent(
        name="tuple-unpack-mixed",
        instructions=SYS,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/walrus_in_boolean_expr.py`

```python
"""§11 (amended) — walrus inside boolean short-circuit does NOT resolve.

``if cond and (PROMPT := "...")`` — the walrus may or may not execute
depending on ``cond``'s value. The "single deterministic binding"
guarantee that justifies resolution is broken; refuse rather than
reason about evaluation order.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(cond: bool):
    if cond and (PROMPT := "from boolean-and walrus"):
        return Agent(
            name="walrus-in-boolean",
            instructions=PROMPT,
            tools=[lookup],
            model="gpt-4o",
        )
    return None
```

### `tests/fixtures/function_local/walrus_in_ternary.py`

```python
"""§11 (amended) — walrus inside a ternary expression does NOT resolve.

The walrus binding only happens when the ternary's selected branch
executes. PR #5 refuses to reason about evaluation-order conditionals.

The condition is a function parameter (per fixture-matrix review) so
no static analyzer — present or future — can constant-fold it.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent(flag: bool):
    # W is the walrus binding inside the ternary's true branch.
    _ = (W := "from ternary true branch") if flag else None
    return Agent(
        name="walrus-in-ternary",
        instructions=W,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/walrus_statement_level.py`

```python
"""§11 — walrus operator at statement level (``ast.Expr`` wrapping
``ast.NamedExpr``) resolves.

Per the §11 amendment, walrus bindings resolve only when they appear at
statement level — not inside boolean short-circuits, ternary
expressions, or comprehension filters.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    (PROMPT := "literal via statement-level walrus")
    return Agent(
        name="walrus-statement-level",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/while_loop_not_resolved.py`

```python
"""§20 — assignment inside ``while`` loop body does NOT resolve.

Same reasoning as §19: rebound on each iteration, single-value
assertion would be wrong.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    n = 0
    while n < 1:
        PROMPT = "while-body literal"
        n += 1
    return Agent(
        name="while-body",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

### `tests/fixtures/function_local/with_block_not_resolved.py`

```python
"""§18 (amended) — assignment inside ``with`` block does NOT resolve.

Original spec proposal was conditional resolution; the amendment
simplifies to "do not resolve" for consistency with §16/§17. The
``with open(...) as f: prompt = "lit"`` pattern is rare in real agent
code; the implementation cost of distinguishing this case from §16/§17
isn't worth the marginal corpus benefit.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    with open("/dev/null") as f:
        PROMPT = "with-block literal"
    return Agent(
        name="with-block",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
```

