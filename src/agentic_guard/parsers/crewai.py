"""CrewAI parser.

Recognizes:
  - ``Agent(...)`` constructor calls in files that import from ``crewai``
  - Direct calls, ``crewai.Agent(...)``, and calls inside ``@agent``-decorated methods
  - ``tools=[...]`` kwarg with ast.Name, ast.Attribute, and ast.Call (class instantiation) forms
  - System prompts via ``role=`` / ``goal=`` / ``backstory=`` kwargs; detects f-strings and
    concatenation for IG002. YAML-backed agents (``config=`` only, no inline fields) are
    always static — no YAML I/O.
  - Tool-less and config-only agents are emitted with ``tools=[]``

Agent name resolution (first match wins):
  role= literal string → enclosing @agent method name → config[key] string → agent_N
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_guard.ir import Agent, SourceLocation, Tool, ToolClassification
from agentic_guard.parsers.base import (
    FrameworkParser,
    ModuleContext,
    call_base_name,
    classify_prompt_expr,
    collect_imports,
    collect_module_context,
    decorator_base_name,
)

_AGENT_CLASS_NAMES = {"Agent"}
_AGENT_DECORATOR_NAMES = {"agent"}
_CREWAI_PREFIX = "crewai"


class CrewAIParser(FrameworkParser):
    """Parse CrewAI ``Agent(...)`` constructor calls into IR."""

    framework = "crewai"

    def matches_file(self, source: str, tree: ast.Module) -> bool:
        imports = collect_imports(tree)
        return any(
            imp == _CREWAI_PREFIX or imp.startswith(_CREWAI_PREFIX + ".")
            for imp in imports
        )

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
        self._agent_counter = 0
        # Stack of @agent-decorated method names for the name-resolution fallback.
        self._method_name_stack: list[str] = []

    # -- method scope tracking -------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        is_agent_method = any(
            decorator_base_name(dec) in _AGENT_DECORATOR_NAMES
            for dec in node.decorator_list
        )
        if is_agent_method:
            self._method_name_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            if is_agent_method:
                self._method_name_stack.pop()

    # -- agent detection -------------------------------------------------

    def visit_Call(self, node: ast.Call) -> None:
        if call_base_name(node) in _AGENT_CLASS_NAMES:
            self._register_agent(node)
        self.generic_visit(node)

    def _register_agent(self, node: ast.Call) -> None:
        loc = SourceLocation(
            file=self.path,
            line=node.lineno,
            column=node.col_offset,
            end_line=getattr(node, "end_lineno", None),
            end_column=getattr(node, "end_col_offset", None),
        )

        agent_tools = self._extract_tools(node)
        prompt_loc, prompt_dynamic, prompt_taint = self._analyze_prompt(node)
        name = self._resolve_name(node)

        self.agents.append(Agent(
            name=name,
            location=loc,
            framework="crewai",
            tools=agent_tools,
            system_prompt_location=prompt_loc,
            system_prompt_is_dynamic=prompt_dynamic,
            system_prompt_taint_sources=prompt_taint,
            interrupts_before=[],
            interrupts_after=[],
        ))

    # -- tool extraction -------------------------------------------------

    def _extract_tools(self, node: ast.Call) -> list[Tool]:
        tools_arg: ast.expr | None = None
        for kw in node.keywords:
            if kw.arg == "tools":
                tools_arg = kw.value
                break
        if not isinstance(tools_arg, (ast.List, ast.Tuple, ast.Set)):
            return []

        result: list[Tool] = []
        for elt in tools_arg.elts:
            tool_name: str | None = None
            if isinstance(elt, ast.Name):
                tool_name = elt.id
            elif isinstance(elt, ast.Attribute):
                tool_name = elt.attr
            elif isinstance(elt, ast.Call):
                # Class instantiation: SerperDevTool() → "SerperDevTool"
                tool_name = call_base_name(elt)
            # else: starred unpack, runtime expression — skip

            if tool_name is None:
                continue

            elt_loc = SourceLocation(
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
                    location=elt_loc,
                    classification=ToolClassification.NEUTRAL,
                )
            else:
                tool = Tool(
                    name=tool_name,
                    location=elt_loc,
                    classification=entry.classification,
                    privilege=entry.privilege,
                    trust_of_output=entry.trust_of_output,
                    reversible=entry.reversible,
                    matched_pattern=entry.pattern,
                )
            result.append(tool)
        return result

    # -- system prompt analysis ------------------------------------------

    def _analyze_prompt(
        self, node: ast.Call
    ) -> tuple[SourceLocation | None, bool, list[str]]:
        """Classify role/goal/backstory kwargs for dynamic content (IG002).

        When all three come from ``config=...`` (YAML-backed), no inline fields
        are present — return static without any YAML I/O.
        """
        inline: dict[str, ast.expr] = {
            kw.arg: kw.value
            for kw in node.keywords
            if kw.arg in ("role", "goal", "backstory")
        }
        if not inline:
            # YAML-backed (config= only) or truly field-less — always static.
            return None, False, []

        all_taint: list[str] = []
        first_dynamic_loc: SourceLocation | None = None

        for field_name in ("role", "goal", "backstory"):
            expr = inline.get(field_name)
            if expr is None:
                continue
            dynamic, sources = classify_prompt_expr(expr, module=self.module_ctx)
            if dynamic:
                if first_dynamic_loc is None:
                    first_dynamic_loc = SourceLocation(
                        file=self.path,
                        line=expr.lineno,
                        column=expr.col_offset,
                        end_line=getattr(expr, "end_lineno", None),
                        end_column=getattr(expr, "end_col_offset", None),
                    )
                for s in sources:
                    if s not in all_taint:
                        all_taint.append(s)

        if first_dynamic_loc is not None:
            return first_dynamic_loc, True, all_taint

        # All inline fields are static literals — return a location but not dynamic.
        first_expr = next(iter(inline.values()))
        static_loc = SourceLocation(
            file=self.path,
            line=first_expr.lineno,
            column=first_expr.col_offset,
        )
        return static_loc, False, []

    # -- name resolution -------------------------------------------------

    def _resolve_name(self, node: ast.Call) -> str:
        # Priority 1: role= literal string
        for kw in node.keywords:
            if (
                kw.arg == "role"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                return kw.value.value

        # Priority 2: enclosing @agent-decorated method name
        if self._method_name_stack:
            return self._method_name_stack[-1]

        # Priority 3: config= subscript key (config=self.agents_config['key'])
        for kw in node.keywords:
            if kw.arg == "config" and isinstance(kw.value, ast.Subscript):
                slice_node = kw.value.slice
                if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                    return slice_node.value

        # Priority 4: synthetic name
        self._agent_counter += 1
        return f"agent_{self._agent_counter}"
