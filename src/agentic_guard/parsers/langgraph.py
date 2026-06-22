"""LangGraph (and adjacent LangChain) agent parser.

Recognizes:
  - Functions decorated with `@tool` from langchain_core.tools / langchain.tools
  - `create_react_agent(...)` calls (and similar agent factories) from langgraph.prebuilt
  - Tools listed in `tools=[...]` by direct extraction (mirrors CrewAI/LlamaIndex):
    ast.Name (plain function or variable), ast.Attribute, and ast.Call
    (class instantiations like `TavilySearch()`). A pre-registered `@tool`
    function is reused for its metadata; everything else is classified by name.
  - System prompts / instructions passed via `prompt=` or `state_modifier=` args
  - Human-approval gates via `interrupt_before=[...]` / `interrupt_after=[...]`

This is best-effort static parsing; we don't run the code, so we infer based on
syntactic patterns. False positives and negatives are managed via the taxonomy
and rule severity scoring.
"""

from __future__ import annotations

import ast
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._maybe_register_tool(node)
        self._enter_function_scope(node)
        try:
            self.generic_visit(node)
        finally:
            self._exit_function_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._maybe_register_tool(node)
        self._enter_function_scope(node)
        try:
            self.generic_visit(node)
        finally:
            self._exit_function_scope(node)

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
