"""LlamaIndex parser (stub — red half, no implementation yet)."""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_guard.ir import Agent, Tool
from agentic_guard.parsers.base import FrameworkParser


class LlamaIndexParser(FrameworkParser):
    """Stub: matches no files and extracts nothing until the green implementation lands."""

    framework = "llama-index"

    def matches_file(self, source: str, tree: ast.Module) -> bool:
        return False

    def extract(
        self, path: Path, source: str, tree: ast.Module
    ) -> tuple[list[Tool], list[Agent]]:
        return [], []
