"""Analysis helpers shared across parsers and rules.

The pieces here intentionally do not depend on any specific framework (no
LangGraph, no OpenAI Agents SDK knowledge). They model facts about Python
source files — imports, module-level constants, dotted module paths — that
parsers consume to disambiguate framework-specific patterns.
"""

from agentic_guard.analysis.function_scope import (
    FunctionScope,
    build_function_scope_tree,
)
from agentic_guard.analysis.symbol_table import (
    CrossModuleResolver,
    ModuleSymbols,
    PackageSymbolTable,
    Symbol,
    SymbolKind,
    discover_package_roots,
    file_to_module_path,
    resolve_relative_module_path,
)

__all__ = [
    "CrossModuleResolver",
    "FunctionScope",
    "ModuleSymbols",
    "PackageSymbolTable",
    "Symbol",
    "SymbolKind",
    "build_function_scope_tree",
    "discover_package_roots",
    "file_to_module_path",
    "resolve_relative_module_path",
]
