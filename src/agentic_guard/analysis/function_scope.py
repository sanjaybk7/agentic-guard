"""Function-local literal binding for PR #5.

Implements the 26 locked decisions from
``docs/design/PR-3-function-local-scoping.md`` plus the §4a cross-function
pollution prevention rule.

Architecture summary:

* ``FunctionScope`` is a per-function record of single-binding literals,
  with a ``parent`` pointer for LEGB walking and ``nonlocal_names`` /
  ``global_names`` sets for §23 declaration routing.
* ``build_function_scope_tree(tree, module_ctx)`` does a single pre-pass
  over the module, building a FunctionScope per ``ast.FunctionDef`` /
  ``ast.AsyncFunctionDef`` (recursively for nested functions), populating
  bindings from the function body's top-level statements only, and
  applying §23 demotions (nonlocal-write demotes parent; global-write
  demotes ``ModuleContext.string_constants``). The tree is keyed by
  ``id(ast_node)`` so the visitor can look up the scope when entering a
  FunctionDef.
* ``ModuleContext`` (in ``parsers/base.py``) gains the function-scope
  map and a ``function_stack`` updated by visitor push/pop. Its
  ``name_resolves_to_static`` walks the stack innermost-first per §4
  closure semantics, honoring §23 nonlocal/global routing.

Design rules implemented (all 26 locked decisions are honored — the
docstrings on each helper name the §):

* §1/§15 (plain), §2 (async), §3 (methods) — function-scope pre-pass
  runs on every FunctionDef and AsyncFunctionDef encountered.
* §1.7 (class bodies) — class body statements are not extracted.
* §1.6 (comprehensions) and §1.5 (lambdas) — we never recurse into
  these for binding extraction; outer-scope LEGB walks still work via
  ``name_resolves_to_static``.
* §1.4 (closures), §25 (shadow module), §26 (shadow import) — LEGB walk
  in ``ModuleContext.name_resolves_to_static``.
* §4a (cross-function pollution) — each ``_build_scope`` call creates a
  fresh FunctionScope instance; the visitor push/pop is bracketed by
  try/finally in the parser. Sibling functions never share state.
* §9 (annotated, Final), §13 (chained), §12 (tuple unpacking all-or-
  nothing), §14 (starred unpacking) — handled in ``_extract_assign_targets``.
* §11 (walrus statement-level only) — ``_walk_for_statement_level_walrus``.
* §16 (if), §17 (try), §18 (with), §19 (for), §20 (while) — control-flow
  statements are not traversed by the binding extractor; bindings inside
  them are deliberately not picked up.
* §21 (reassignment) — multi-assign counter drops the binding.
* §22 (parameter shadowing) — parameter names pre-populate the
  assign-count map with 1; any in-function assignment becomes the second
  binding and triggers the drop.
* §23 (nonlocal/global) — declaration sets routed; subsequent assignment
  demotes the target scope's binding.
* §24 (exception variables) — ``ast.ExceptHandler.name`` is not
  collected as a binding; ``except as e`` only contributes to the
  except-body branch which is itself skipped per §17.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_guard.analysis.symbol_table import Symbol, SymbolKind

if TYPE_CHECKING:
    # Avoid the circular: ModuleContext lives in parsers/base.py which
    # imports from this module. At runtime we accept any duck-typed
    # object with the demote_module_binding() callable used below.
    from agentic_guard.parsers.base import ModuleContext


@dataclass
class FunctionScope:
    """Per-function record of single-binding literals + LEGB chain.

    ``parent`` points at the enclosing function's scope (None for
    top-level functions). The LEGB walk in
    ``ModuleContext.name_resolves_to_static`` follows ``parent`` chains
    and then falls through to module scope and the cross-module
    resolver.

    ``locally_bound`` is the Python-shadowing tripwire. Any name that
    receives an assignment anywhere in this function's top-level body
    (even one that gets dropped from ``bindings`` by the multi-assign
    rule) is in ``locally_bound``. The LEGB walk uses this to honor
    Python's "a name assigned in a function scope is local to that
    scope" rule — once a name is locally bound, the walk does not
    fall through to an enclosing scope's binding (per §4 closure
    semantics combined with §21 multi-assign drop).

    Parameters are also in ``locally_bound`` (they are local to the
    function even if we cannot resolve their values).

    Names in ``nonlocal_names`` and ``global_names`` are deliberately
    NOT added to ``locally_bound`` — those declarations route lookups
    outward by definition.
    """

    name: str
    bindings: dict[str, Symbol] = field(default_factory=dict)
    locally_bound: set[str] = field(default_factory=set)
    nonlocal_names: set[str] = field(default_factory=set)
    global_names: set[str] = field(default_factory=set)
    parent: FunctionScope | None = None


def build_function_scope_tree(
    tree: ast.Module,
    module_ctx: ModuleContext,
) -> dict[int, FunctionScope]:
    """Build FunctionScope for every function in ``tree``, applying §23 demotions.

    Returns a dict mapping ``id(FunctionDef_or_AsyncFunctionDef_node)`` →
    ``FunctionScope``. The visitor uses this map to push the right scope
    when it enters a function body.

    Demotion side effects (§23):

    * ``nonlocal X`` + write inside an inner function → ``parent.bindings.pop(X)``
    * ``global X`` + write inside any function → ``module_ctx.string_constants.pop(X)``

    Demotions are applied during this pre-pass so they're visible to all
    subsequent resolution queries, including ones from sibling functions
    that read before the writing function in source order (see
    ``global_routes_to_module`` fixture).
    """
    scope_map: dict[int, FunctionScope] = {}
    for stmt in tree.body:
        _walk_top_level(stmt, parent=None, scope_map=scope_map, module_ctx=module_ctx)
    return scope_map


def _walk_top_level(
    node: ast.AST,
    parent: FunctionScope | None,
    scope_map: dict[int, FunctionScope],
    module_ctx: ModuleContext,
) -> None:
    """Recurse into module/function/class bodies looking for FunctionDefs.

    Class bodies are walked (so methods inside classes get their own
    scope per §3), but the class's own name space is not extracted.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        _build_scope(node, parent=parent, scope_map=scope_map, module_ctx=module_ctx)
    elif isinstance(node, ast.ClassDef):
        # §1.7: class body is not a function-scope; we don't extract
        # class-level bindings. But methods inside are functions, and
        # they get their own scope with parent=None (they don't close
        # over class-scope names — that's not how Python works).
        for child in node.body:
            _walk_top_level(child, parent=None, scope_map=scope_map, module_ctx=module_ctx)


def _build_scope(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    parent: FunctionScope | None,
    scope_map: dict[int, FunctionScope],
    module_ctx: ModuleContext,
) -> FunctionScope:
    """Construct and populate the FunctionScope for one function."""
    scope = FunctionScope(name=node.name, parent=parent)
    scope_map[id(node)] = scope

    # §22: parameters count as initial bindings (assign-count = 1). They
    # are NOT added to ``scope.bindings`` — we can't know what value the
    # caller passed. The assign-count entry exists solely to make any
    # in-function assignment to the same name be the *second* binding,
    # triggering the multi-assign drop. Parameters ARE added to
    # ``locally_bound`` since they're function-local in Python.
    args = node.args
    assign_count: dict[str, int] = {}
    for arg in args.posonlyargs + args.args + args.kwonlyargs:
        assign_count[arg.arg] = 1
        scope.locally_bound.add(arg.arg)
    if args.vararg is not None:
        assign_count[args.vararg.arg] = 1
        scope.locally_bound.add(args.vararg.arg)
    if args.kwarg is not None:
        assign_count[args.kwarg.arg] = 1
        scope.locally_bound.add(args.kwarg.arg)

    # First pass: collect nonlocal/global declarations. These must take
    # effect before any assignment in the body is processed.
    for stmt in node.body:
        if isinstance(stmt, ast.Nonlocal):
            scope.nonlocal_names.update(stmt.names)
        elif isinstance(stmt, ast.Global):
            scope.global_names.update(stmt.names)

    # Second pass: process bindings + recurse into nested function defs.
    for stmt in node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Recurse to build the nested function's own scope. Nested
            # FunctionDef does not become a binding in the enclosing
            # function (per §1.4 closures — the inner function name is
            # implicitly available but resolution doesn't treat it as a
            # literal).
            _build_scope(stmt, parent=scope, scope_map=scope_map, module_ctx=module_ctx)
        elif isinstance(stmt, ast.ClassDef):
            # §1.7: class body opaque to function-scope extraction.
            # Methods inside still get their own scope (parent=None per
            # _walk_top_level's handling).
            for child in stmt.body:
                _walk_top_level(child, parent=None, scope_map=scope_map, module_ctx=module_ctx)
        elif isinstance(stmt, ast.Assign):
            _process_assign(stmt, scope, assign_count, module_ctx)
        elif isinstance(stmt, ast.AnnAssign):
            _process_ann_assign(stmt, scope, assign_count, module_ctx)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.NamedExpr):
            # §11 amended: walrus binds only at statement level (an
            # ``ast.Expr`` wrapping ``ast.NamedExpr``). Walrus inside
            # boolean short-circuits, ternaries, or comprehension filters
            # never reach this branch and so does not resolve.
            _process_walrus(stmt.value, scope, assign_count, module_ctx)
        # Every other top-level statement type — ast.If, ast.Try,
        # ast.With, ast.For, ast.While, ast.Expr (non-walrus), ast.Return,
        # etc. — is skipped per §§16-20 and §24 (and §17 in-function
        # try/except is intentionally not the optional-import exception
        # Fix 1 makes at module scope).

    return scope


def _process_assign(
    stmt: ast.Assign,
    scope: FunctionScope,
    assign_count: dict[str, int],
    module_ctx: ModuleContext,
) -> None:
    """Handle ``ast.Assign`` per §§8 / §12 / §13 / §14 / §23."""
    for name, sym in _extract_assign_targets(stmt):
        _record_binding(name, sym, scope, assign_count, module_ctx)


def _process_ann_assign(
    stmt: ast.AnnAssign,
    scope: FunctionScope,
    assign_count: dict[str, int],
    module_ctx: ModuleContext,
) -> None:
    """Handle ``ast.AnnAssign`` per §9 amended (Final[str] and bare Final).

    The annotation field is parsed but ignored for binding extraction;
    only ``target`` and ``value`` matter.
    """
    if not isinstance(stmt.target, ast.Name) or stmt.value is None:
        return
    sym = _value_to_symbol(stmt.value)
    _record_binding(stmt.target.id, sym, scope, assign_count, module_ctx)


def _process_walrus(
    walrus: ast.NamedExpr,
    scope: FunctionScope,
    assign_count: dict[str, int],
    module_ctx: ModuleContext,
) -> None:
    """Handle ``ast.NamedExpr`` at statement level per §11 amended."""
    if not isinstance(walrus.target, ast.Name):
        return
    sym = _value_to_symbol(walrus.value)
    _record_binding(walrus.target.id, sym, scope, assign_count, module_ctx)


def _record_binding(
    name: str,
    sym: Symbol | None,
    scope: FunctionScope,
    assign_count: dict[str, int],
    module_ctx: ModuleContext,
) -> None:
    """Apply §23 routing (nonlocal/global write demotes outer) or §21
    multi-assign drop, then insert into ``scope.bindings`` if the
    binding survives."""
    # §23: nonlocal write demotes parent's binding; not registered locally
    # and explicitly not added to locally_bound (the routing IS outward).
    if name in scope.nonlocal_names:
        if scope.parent is not None:
            scope.parent.bindings.pop(name, None)
        return
    # §23: global write demotes module-scope binding; not registered locally.
    if name in scope.global_names:
        module_ctx.string_constants.pop(name, None)
        return
    # Local binding: this name is in scope.locally_bound regardless of
    # whether the multi-assign rule lets us track its value. Python
    # treats any assignment as making the name local-to-this-scope; our
    # LEGB walk uses ``locally_bound`` to enforce that shadowing
    # (preventing fall-through to an enclosing scope's binding even
    # when our analyzer dropped the local one).
    scope.locally_bound.add(name)
    assign_count[name] = assign_count.get(name, 0) + 1
    if assign_count[name] > 1 or sym is None:
        scope.bindings.pop(name, None)
        return
    scope.bindings[name] = sym


def _extract_assign_targets(stmt: ast.Assign) -> list[tuple[str, Symbol | None]]:
    """Return (name, Symbol|None) per target of a (possibly chained) Assign.

    Handles:
    * Plain ``X = "..."`` — single Name target.
    * Chained ``X = Y = "..."`` (§13) — multiple targets, same value.
    * Tuple unpacking ``X, Y = "a", "b"`` (§12 all-or-nothing) —
      delegated to ``_unpack_tuple_targets``.

    Attribute and subscript targets (``self.x``, ``arr[0]``) are not
    registered as local bindings (§3 self.x carve-out).
    """
    results: list[tuple[str, Symbol | None]] = []
    value = stmt.value
    rhs_symbol = _value_to_symbol(value)
    for target in stmt.targets:
        if isinstance(target, ast.Name):
            results.append((target.id, rhs_symbol))
        elif isinstance(target, ast.Tuple):
            results.extend(_unpack_tuple_targets(target, value))
        # Other target shapes (Attribute, Subscript, Starred-bare): no entry.
    return results


def _unpack_tuple_targets(
    target_tuple: ast.Tuple,
    value: ast.expr,
) -> list[tuple[str, Symbol | None]]:
    """Implement §12 all-or-nothing tuple unpacking + §14 starred carve-out.

    * Any ``ast.Starred`` in the target list → entire unpacking yields
      (name, None) for each simple-name target; the starred name is not
      registered (§14).
    * Targets that are not all simple Names → skip entirely (nested
      unpacking, §12).
    * RHS that's not a Tuple/List of matching length → unpacking can't
      be resolved; all targets yield (name, None) so multi-assign rules
      apply correctly.
    * RHS is a Tuple/List with at least one non-literal element →
      §12 amended all-or-nothing: all targets yield (name, None).
    * RHS is a Tuple/List of all literals matching length → resolve
      each target to its position.
    """
    if any(isinstance(t, ast.Starred) for t in target_tuple.elts):
        return [(t.id, None) for t in target_tuple.elts if isinstance(t, ast.Name)]
    if not all(isinstance(t, ast.Name) for t in target_tuple.elts):
        return []
    target_names = [t.id for t in target_tuple.elts if isinstance(t, ast.Name)]
    if not isinstance(value, (ast.Tuple, ast.List)):
        return [(n, None) for n in target_names]
    if len(value.elts) != len(target_names):
        return [(n, None) for n in target_names]
    value_symbols = [_value_to_symbol(v) for v in value.elts]
    if any(s is None for s in value_symbols):
        return [(n, None) for n in target_names]
    return list(zip(target_names, value_symbols, strict=True))


def _value_to_symbol(value: ast.expr) -> Symbol | None:
    """Map an RHS expression to a Symbol if and only if it's a literal.

    Mirrors ``analysis.symbol_table._value_to_symbol`` for module-scope
    bindings. A plain ``ast.Constant`` string or a constant-only
    ``ast.JoinedStr`` (multi-string-literal, no FormattedValue children)
    qualifies.
    """
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return Symbol(kind=SymbolKind.STR_LITERAL, value=value.value)
    if isinstance(value, ast.JoinedStr) and all(
        isinstance(v, ast.Constant) for v in value.values
    ):
        return Symbol(kind=SymbolKind.STR_LITERAL, value=None)
    return None
