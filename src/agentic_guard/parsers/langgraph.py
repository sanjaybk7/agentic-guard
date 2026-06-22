"""LangGraph (and adjacent LangChain) agent parser.

Recognizes:
  - Functions decorated with `@tool` from langchain_core.tools / langchain.tools
  - `create_react_agent(...)` calls (and similar agent factories) from langgraph.prebuilt
  - Tools listed in `tools=[...]` by direct extraction (mirrors CrewAI/LlamaIndex):
    ast.Name (plain function or variable), ast.Attribute, and ast.Call
    (class instantiations like `TavilySearch()`). A pre-registered `@tool`
    function is reused for its metadata; everything else is classified by name.
  - `<model>.bind_tools([...])` calls (LG-3): the tool-calling LCEL idiom that is
    the alternative to `create_react_agent`. In a hand-built StateGraph there is
    no agent-factory call — the bound model IS the agent loop — so each in-scope
    `bind_tools` call is treated as introducing an agent whose toolbox is the
    bound list. SCOPE: the bound list must be statically resolvable in THIS file
    — an inline list/tuple/set literal, or a Name bound to such a literal at
    module scope or in the enclosing function. Cross-module/imported tool vars,
    `a + b` concatenations, and runtime-built lists are left unextracted (a known
    miss, never a guessed attribution). Method *definitions* (`def bind_tools` in
    fake/stub chat models) are not calls and never match.
  - System prompts / instructions passed via `prompt=` or `state_modifier=` args
  - Human-approval gates via `interrupt_before=[...]` / `interrupt_after=[...]`

This is best-effort static parsing; we don't run the code, so we infer based on
syntactic patterns. False positives and negatives are managed via the taxonomy
and rule severity scoring.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path

from agentic_guard.ir import (
    Agent,
    SourceLocation,
    Tool,
    ToolClassification,
)
from agentic_guard.parsers.base import (
    FrameworkParser,
    ModuleContext,
    call_base_name,
    classify_prompt_expr,
    collect_imports,
    collect_module_context,
    decorator_base_name,
)

_TOOL_DECORATOR_NAMES = {"tool", "Tool"}
_AGENT_FACTORY_NAMES = {
    "create_react_agent",
    "create_tool_calling_agent",
    "create_openai_functions_agent",
    "create_agent",
}
_BIND_TOOLS_METHOD = "bind_tools"
_RELEVANT_IMPORT_PREFIXES = (
    "langgraph",
    "langchain",
    "langchain_core",
    "langchain_community",
)


class LangGraphParser(FrameworkParser):
    """Parse a Python source file into LangGraph IR."""

    framework = "langgraph"

    def matches_file(self, source: str, tree: ast.Module) -> bool:
        imports = collect_imports(tree)
        return any(any(imp.startswith(prefix) for prefix in _RELEVANT_IMPORT_PREFIXES) for imp in imports)

    def extract(self, path: Path, source: str, tree: ast.Module) -> tuple[list[Tool], list[Agent]]:
        cross_module = self.build_cross_module(path, tree)
        module_ctx = collect_module_context(tree, cross_module=cross_module)
        visitor = _Visitor(path=path, taxonomy=self.taxonomy, module_ctx=module_ctx)
        visitor.collect_module_lists(tree)
        visitor.visit(tree)
        return visitor.tools, visitor.agents


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: Path, taxonomy: object, module_ctx: ModuleContext) -> None:
        from agentic_guard.taxonomy import Taxonomy

        assert isinstance(taxonomy, Taxonomy)
        self.path = path
        self.taxonomy = taxonomy
        self.module_ctx = module_ctx
        self.tools: list[Tool] = []
        self.agents: list[Agent] = []
        self._tools_by_name: dict[str, Tool] = {}
        # LG-3 bind_tools support: module-scope list literals (name -> node),
        # plus stacks tracking the enclosing FunctionDef and the assignment
        # target currently being built (for naming bind_tools agents).
        self._module_lists: dict[str, ast.expr] = {}
        self._func_stack: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        self._assign_target_stack: list[str | None] = []

    def collect_module_lists(self, tree: ast.Module) -> None:
        """Record module-level ``NAME = [literal list]`` assignments.

        Only single-Name targets bound to a List/Tuple/Set literal at module
        scope are recorded; these are the ``bind_tools(tools_var)`` resolution
        targets. Anything else (concat, comprehension, function call) is left
        out so it resolves to "unknown" and the bind_tools site is skipped.
        """
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign) and isinstance(
                stmt.value, (ast.List, ast.Tuple, ast.Set)
            ):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        self._module_lists[target.id] = stmt.value

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._maybe_register_tool(node)
        self._enter_function_scope(node)
        self._func_stack.append(node)
        try:
            self.generic_visit(node)
        finally:
            self._func_stack.pop()
            self._exit_function_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._maybe_register_tool(node)
        self._enter_function_scope(node)
        self._func_stack.append(node)
        try:
            self.generic_visit(node)
        finally:
            self._func_stack.pop()
            self._exit_function_scope(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track a single-Name assignment target so a ``bind_tools`` call inside
        the value (e.g. ``runnable = prompt | llm.bind_tools([...])``) can name
        its agent after the variable it is assigned to."""
        target: str | None = None
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        self._assign_target_stack.append(target)
        try:
            self.generic_visit(node)
        finally:
            self._assign_target_stack.pop()

    # §4a: try/finally bracketing guarantees the scope stack unwinds
    # cleanly even if generic_visit raises mid-function, so a sibling
    # function visited next cannot inherit a polluted stack.
    def _enter_function_scope(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        scope = self.module_ctx.function_scopes.get(id(node))
        if scope is not None:
            self.module_ctx.function_stack.append(scope)

    def _exit_function_scope(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        if id(node) in self.module_ctx.function_scopes and self.module_ctx.function_stack:
            self.module_ctx.function_stack.pop()

    def _maybe_register_tool(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        decorator = self._find_tool_decorator(node)
        if decorator is None:
            return

        tool_name = self._tool_name_override(decorator) or node.name
        description = ast.get_docstring(node)
        entry = self.taxonomy.classify(tool_name, description)

        loc = SourceLocation(
            file=self.path,
            line=node.lineno,
            column=node.col_offset,
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
        )

        if entry is None:
            tool = Tool(
                name=tool_name,
                location=loc,
                classification=ToolClassification.NEUTRAL,
                description=description,
                raw_decorator=self._decorator_repr(decorator),
            )
        else:
            tool = Tool(
                name=tool_name,
                location=loc,
                classification=entry.classification,
                privilege=entry.privilege,
                trust_of_output=entry.trust_of_output,
                reversible=entry.reversible,
                description=description,
                raw_decorator=self._decorator_repr(decorator),
                matched_pattern=entry.pattern,
            )
        self.tools.append(tool)
        self._tools_by_name[tool_name] = tool

    def _find_tool_decorator(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.expr | None:
        for dec in node.decorator_list:
            name = decorator_base_name(dec)
            if name in _TOOL_DECORATOR_NAMES:
                return dec
        return None

    def _tool_name_override(self, decorator: ast.expr) -> str | None:
        if isinstance(decorator, ast.Call):
            for kw in decorator.keywords:
                if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                    if isinstance(kw.value.value, str):
                        return kw.value.value
            for arg in decorator.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    return arg.value
        return None

    def _decorator_repr(self, decorator: ast.expr) -> str:
        try:
            return ast.unparse(decorator)
        except Exception:
            return decorator_base_name(decorator) or "tool"

    def visit_Call(self, node: ast.Call) -> None:
        func_name = call_base_name(node)
        if func_name in _AGENT_FACTORY_NAMES:
            self._register_agent(node, func_name)
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == _BIND_TOOLS_METHOD
        ):
            self._register_bind_tools_agent(node)
        self.generic_visit(node)

    def _register_agent(self, node: ast.Call, factory_name: str) -> None:
        loc = SourceLocation(
            file=self.path,
            line=node.lineno,
            column=node.col_offset,
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
        )

        agent_tools = self._extract_tools(node)

        prompt_loc, prompt_dynamic, prompt_taint = self._analyze_prompt(node)
        interrupts_before = self._extract_string_list(node, "interrupt_before")
        interrupts_after = self._extract_string_list(node, "interrupt_after")

        agent = Agent(
            name=factory_name,
            location=loc,
            framework="langgraph",
            tools=agent_tools,
            system_prompt_location=prompt_loc,
            system_prompt_is_dynamic=prompt_dynamic,
            system_prompt_taint_sources=prompt_taint,
            interrupts_before=interrupts_before,
            interrupts_after=interrupts_after,
        )
        self.agents.append(agent)

    def _register_bind_tools_agent(self, node: ast.Call) -> None:
        """Register an agent for a ``<model>.bind_tools([...])`` call.

        The bound tool list must be statically resolvable in this file (inline
        literal, or a Name bound to a same-scope literal list). If it is not, we
        return without emitting anything — a known miss, never a guess that could
        mis-attribute tools to the wrong agent.
        """
        elts = self._resolve_bound_tools(node)
        if elts is None:
            return

        agent_tools: list[Tool] = []
        for elt in elts:
            tool = self._tool_from_element(elt)
            if tool is not None:
                agent_tools.append(tool)

        loc = SourceLocation(
            file=self.path,
            line=node.lineno,
            column=node.col_offset,
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
        )

        agent = Agent(
            name=self._bind_tools_agent_name(),
            location=loc,
            framework="langgraph",
            tools=agent_tools,
        )
        self.agents.append(agent)

    def _bind_tools_agent_name(self) -> str:
        """Name a bind_tools agent: assignment target > enclosing function > fallback."""
        for target in reversed(self._assign_target_stack):
            if target:
                return target
        if self._func_stack:
            return self._func_stack[-1].name
        return "bind_tools"

    def _resolve_bound_tools(self, node: ast.Call) -> list[ast.expr] | None:
        """Return the element list bound via ``bind_tools(...)``, or None if it
        cannot be resolved to a same-scope literal list.

        Accepts ``bind_tools([...])`` (positional) and ``bind_tools(tools=[...])``.
        A bare Name argument is resolved against the enclosing function's local
        list-literal assignments (innermost first) and then module scope, with a
        source-order guard (the binding must appear before this call).
        """
        arg: ast.expr | None = None
        if node.args:
            arg = node.args[0]
        else:
            for kw in node.keywords:
                if kw.arg == "tools":
                    arg = kw.value
                    break
        if arg is None:
            return None

        if isinstance(arg, (ast.List, ast.Tuple, ast.Set)):
            return list(arg.elts)

        if isinstance(arg, ast.Name):
            literal = self._lookup_list_literal(arg.id, node.lineno)
            if literal is not None:
                return list(literal.elts)
        # BinOp concat, comprehension, call, attribute, cross-module import:
        # not statically resolvable in-file → leave unextracted.
        return None

    def _lookup_list_literal(
        self, name: str, before_line: int
    ) -> ast.List | ast.Tuple | ast.Set | None:
        """Resolve a Name to a same-file literal list assigned before ``before_line``.

        Search order: enclosing functions innermost-first, then module scope.
        """
        for func in reversed(self._func_stack):
            found = self._func_local_list(func, name, before_line)
            if found is not None:
                return found
        module_literal = self._module_lists.get(name)
        if isinstance(module_literal, (ast.List, ast.Tuple, ast.Set)) and (
            module_literal.lineno < before_line
        ):
            return module_literal
        return None

    @classmethod
    def _func_local_list(
        cls,
        func: ast.FunctionDef | ast.AsyncFunctionDef,
        name: str,
        before_line: int,
    ) -> ast.List | ast.Tuple | ast.Set | None:
        """Find ``name = [literal]`` within ``func`` before ``before_line``.

        Recurses through compound statements (if/for/with/try) but stops at
        nested function/class scopes, so a same-named binding in an inner scope
        can't be picked up here. Last write before the call wins.
        """
        found: ast.List | ast.Tuple | ast.Set | None = None
        for stmt in cls._iter_same_scope(func.body):
            if (
                isinstance(stmt, ast.Assign)
                and isinstance(stmt.value, (ast.List, ast.Tuple, ast.Set))
                and stmt.lineno < before_line
            ):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        found = stmt.value
        return found

    @classmethod
    def _iter_same_scope(cls, body: list[ast.stmt]) -> Iterator[ast.stmt]:
        """Yield statements in ``body`` and nested compound blocks, without
        descending into nested function/class scopes."""
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            yield stmt
            for field_name in ("body", "orelse", "finalbody"):
                inner = getattr(stmt, field_name, None)
                if isinstance(inner, list):
                    yield from cls._iter_same_scope(inner)
            for handler in getattr(stmt, "handlers", []) or []:
                yield from cls._iter_same_scope(handler.body)

    def _find_tools_arg(self, node: ast.Call) -> ast.expr | None:
        for kw in node.keywords:
            if kw.arg == "tools":
                return kw.value
        for arg in node.args:
            if isinstance(arg, (ast.List, ast.Tuple, ast.Set)):
                return arg
        return None

    def _extract_tools(self, node: ast.Call) -> list[Tool]:
        """Extract tools directly from the ``tools=[...]`` list elements.

        Mirrors the CrewAI/LlamaIndex direct-extraction approach: every list
        element is turned into a Tool by its identity, regardless of whether
        the underlying callable is ``@tool``-decorated in this file. A
        decorated tool that was pre-registered is reused (it carries the
        docstring-derived description); anything else — a plain undecorated
        function, a class instance, or a name imported from elsewhere — is
        classified directly by name via the taxonomy.
        """
        tools_arg = self._find_tools_arg(node)
        if not isinstance(tools_arg, (ast.List, ast.Tuple, ast.Set)):
            return []

        result: list[Tool] = []
        for elt in tools_arg.elts:
            tool = self._tool_from_element(elt)
            if tool is not None:
                result.append(tool)
        return result

    def _tool_from_element(self, elt: ast.expr) -> Tool | None:
        tool_name: str | None = None
        if isinstance(elt, ast.Name):
            tool_name = elt.id
        elif isinstance(elt, ast.Attribute):
            tool_name = elt.attr
        elif isinstance(elt, ast.Call):
            # Class instantiation: TavilySearch(), create_handoff_tool(...) →
            # the callee's base name.
            tool_name = call_base_name(elt)
        # else: starred unpack, runtime expression — skip.
        if tool_name is None:
            return None

        # Prefer a pre-registered @tool-decorated tool: richer metadata.
        registered = self._tools_by_name.get(tool_name)
        if registered is not None:
            return registered

        return self._make_tool_from_name(tool_name, elt)

    def _make_tool_from_name(self, tool_name: str, elt: ast.expr) -> Tool:
        loc = SourceLocation(
            file=self.path,
            line=elt.lineno,
            column=elt.col_offset,
            end_line=getattr(elt, "end_lineno", None),
            end_column=getattr(elt, "end_col_offset", None),
        )
        entry = self.taxonomy.classify(tool_name, None)
        if entry is None:
            tool = Tool(
                name=tool_name,
                location=loc,
                classification=ToolClassification.NEUTRAL,
            )
        else:
            tool = Tool(
                name=tool_name,
                location=loc,
                classification=entry.classification,
                privilege=entry.privilege,
                trust_of_output=entry.trust_of_output,
                reversible=entry.reversible,
                matched_pattern=entry.pattern,
            )
        # Count freshly-extracted tools toward tools_seen. Pre-registered
        # decorated tools are already in self.tools and are not re-added.
        self.tools.append(tool)
        return tool

    def _analyze_prompt(
        self, node: ast.Call
    ) -> tuple[SourceLocation | None, bool, list[str]]:
        prompt_arg: ast.expr | None = None
        for kw in node.keywords:
            if kw.arg in ("prompt", "system_prompt", "state_modifier", "instructions"):
                prompt_arg = kw.value
                break
        if prompt_arg is None:
            return None, False, []

        loc = SourceLocation(
            file=self.path,
            line=prompt_arg.lineno,
            column=prompt_arg.col_offset,
            end_line=getattr(prompt_arg, "end_lineno", None),
            end_column=getattr(prompt_arg, "end_col_offset", None),
        )

        dynamic, sources = classify_prompt_expr(prompt_arg, module=self.module_ctx)
        return loc, dynamic, sources

    def _extract_string_list(self, node: ast.Call, kw_name: str) -> list[str]:
        for kw in node.keywords:
            if kw.arg == kw_name and isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
                out: list[str] = []
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        out.append(elt.value)
                return out
        return []
