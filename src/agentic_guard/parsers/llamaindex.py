"""LlamaIndex parser.

Recognizes:
  - X.from_tools(...) where X ∈ {ReActAgent, OpenAIAgent, FunctionCallingAgent}
  - FunctionAgent(...) constructor
  - AgentWorkflow is deliberately excluded — it is an orchestrator, not an agent
  - tools= keyword or first positional arg (from_tools passes tools positionally in real code)
  - tool elements: ast.Name (.id), ast.Attribute (.attr), ast.Call (call_base_name)
  - system_prompt= kwarg classified for IG002; chat_history= without system_prompt= is a
    known v1 gap — emitted as static with no location rather than hallucinated dynamic

Agent name resolution: name= literal → synthetic agent_N.
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
)

_LLAMA_PREFIX = "llama_index"

# Classmethod form: X.from_tools(...) — receiver must be in this set.
# Matching on "from_tools" alone would fire on any library's from_tools factory.
_FROM_TOOLS_CLASSES = {"ReActAgent", "OpenAIAgent", "FunctionCallingAgent"}

# Constructor form: direct callee-name match (like CrewAI's "Agent").
_CONSTRUCTOR_CLASSES = {"FunctionAgent"}


def _is_from_tools_call(node: ast.Call) -> bool:
    """Return True iff node is X.from_tools(...) where X is in the agent receiver set.

    Both conditions must hold together — this is the correctness-critical predicate
    that prevents false positives from unrelated from_tools factories.
    """
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "from_tools"
        and isinstance(func.value, ast.Name)
        and func.value.id in _FROM_TOOLS_CLASSES
    )


class LlamaIndexParser(FrameworkParser):
    """Parse LlamaIndex agent constructors into IR."""

    framework = "llama-index"

    def matches_file(self, source: str, tree: ast.Module) -> bool:
        imports = collect_imports(tree)
        return any(
            imp == _LLAMA_PREFIX or imp.startswith(_LLAMA_PREFIX + ".")
            for imp in imports
        )

    def extract(
        self, path: Path, source: str, tree: ast.Module
    ) -> tuple[list[Tool], list[Agent]]:
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

    def visit_Call(self, node: ast.Call) -> None:
        if _is_from_tools_call(node) or call_base_name(node) in _CONSTRUCTOR_CLASSES:
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
        self.agents.append(
            Agent(
                name=name,
                location=loc,
                framework="llama-index",
                tools=agent_tools,
                system_prompt_location=prompt_loc,
                system_prompt_is_dynamic=prompt_dynamic,
                system_prompt_taint_sources=prompt_taint,
                interrupts_before=[],
                interrupts_after=[],
            )
        )

    # -- tool extraction -------------------------------------------------

    def _find_tools_arg(self, node: ast.Call) -> ast.expr | None:
        for kw in node.keywords:
            if kw.arg == "tools":
                return kw.value
        if node.args:
            return node.args[0]
        return None

    def _extract_tools(self, node: ast.Call) -> list[Tool]:
        tools_arg = self._find_tools_arg(node)
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
                tool_name = call_base_name(elt)

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
        for kw in node.keywords:
            if kw.arg == "system_prompt":
                expr = kw.value
                dynamic, sources = classify_prompt_expr(expr, module=self.module_ctx)
                loc = SourceLocation(
                    file=self.path,
                    line=expr.lineno,
                    column=expr.col_offset,
                    end_line=getattr(expr, "end_lineno", None),
                    end_column=getattr(expr, "end_col_offset", None),
                )
                return loc, dynamic, list(sources)
        # §5.2 v1 gap: chat_history= without system_prompt= — emit static, no location.
        return None, False, []

    # -- name resolution -------------------------------------------------

    def _resolve_name(self, node: ast.Call) -> str:
        for kw in node.keywords:
            if (
                kw.arg == "name"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                return kw.value.value
        self._agent_counter += 1
        return f"agent_{self._agent_counter}"
