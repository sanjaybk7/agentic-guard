"""CrewAI parser — red-half stub, not yet implemented.

See docs/design/crewai-parser.md for the full specification.
This stub exists solely so the fixture tests can be imported and fail
at the assertion level rather than at collection time.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_guard.ir import Agent, Tool
from agentic_guard.parsers.base import FrameworkParser


class CrewAIParser(FrameworkParser):
    """Parse CrewAI Agent(...) constructor calls into IR. Not yet implemented."""

    framework = "crewai"

    def matches_file(self, source: str, tree: ast.Module) -> bool:
        return False

    def extract(self, path: Path, source: str, tree: ast.Module) -> tuple[list[Tool], list[Agent]]:
        return [], []
