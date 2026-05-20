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
    """§5 — lambdas can contain no bindings; analyzer must not crash on them.

    The Agent in this fixture references a module-level literal (handled
    by Fix 1). The lambda is structural noise — if the analyzer's
    function-scope walker crashes on lambda descent, this test catches it.
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


def test_global_routes_to_module_literal_resolves() -> None:
    """§23 — ``global X`` declaration routes lookup to module scope's literal."""
    assert "IG002" not in _rule_ids(FIXTURES / "global_routes_to_module.py"), (
        "§23 global declaration must route to module-scope literal via Fix 1"
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
