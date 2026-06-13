"""Loader and matcher for the source/sink taxonomy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from agentic_guard.ir import ToolClassification, TrustLevel

_DEFAULT_TAXONOMY_PATH = Path(__file__).parent / "taxonomy.yaml"

# Compiled once — used by _to_tokens().
_PASCAL_LOWER_TO_UPPER = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_PASCAL_UPPER_SEQUENCE = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALNUM = re.compile(r"[^a-zA-Z0-9]+")


def _to_tokens(text: str) -> frozenset[str]:
    """Tokenize a tool name or taxonomy pattern into lowercase word tokens.

    Handles:
    - snake_case:   ``read_file``        → {read, file}
    - PascalCase:   ``FileReadTool``     → {file, read, tool}
    - camelCase:    ``readEmailTool``    → {read, email, tool}
    - Acronyms:     ``EXAAnswerTool``    → {exa, answer, tool}

    Tokens shorter than 2 characters are excluded.
    """
    s = _PASCAL_LOWER_TO_UPPER.sub(" ", text)
    s = _PASCAL_UPPER_SEQUENCE.sub(" ", s)
    parts = _NON_ALNUM.split(s)
    return frozenset(p.lower() for p in parts if len(p) >= 2)


def _tokens_match(pattern_tokens: frozenset[str], name_tokens: frozenset[str]) -> bool:
    """Return True if every pattern token is covered by a name token.

    Coverage rules for pattern token ``p`` against name token set ``T``:
    - Exact match: ``p in T``
    - Prefix match: ``∃ t ∈ T`` such that ``t.startswith(p)`` and ``len(p) >= 4``

    The ``len(p) >= 4`` guard prevents short tokens (e.g. ``pay``, ``run``)
    from matching via prefix — those must hit exactly, limiting false positives.
    An empty pattern token set never matches.
    """
    if not pattern_tokens:
        return False
    return all(
        any(t == p or (len(p) >= 4 and t.startswith(p)) for t in name_tokens)
        for p in pattern_tokens
    )


@dataclass(frozen=True)
class TaxonomyEntry:
    pattern: str
    classification: ToolClassification
    privilege: int = 0
    trust_of_output: TrustLevel = TrustLevel.TRUSTED
    reversible: bool = True
    rationale: str | None = None


@dataclass
class Taxonomy:
    """Catalog of tool-name patterns and their security classification."""

    entries: list[TaxonomyEntry]

    @classmethod
    def load(cls, path: Path | None = None) -> Taxonomy:
        """Load the taxonomy from YAML. Defaults to the bundled file."""
        target = path or _DEFAULT_TAXONOMY_PATH
        with target.open("r", encoding="utf-8") as f:
            raw: dict[str, list[dict[str, Any]]] = yaml.safe_load(f) or {}

        entries: list[TaxonomyEntry] = []
        for kind, classification in (
            ("sources", ToolClassification.SOURCE),
            ("sinks", ToolClassification.SINK),
            ("both", ToolClassification.BOTH),
        ):
            for item in raw.get(kind, []) or []:
                entries.append(
                    TaxonomyEntry(
                        pattern=str(item["pattern"]).lower(),
                        classification=classification,
                        privilege=int(item.get("privilege", 0)),
                        trust_of_output=TrustLevel(
                            item.get(
                                "trust_of_output",
                                "untrusted" if classification != ToolClassification.SINK else "trusted",
                            )
                        ),
                        reversible=bool(item.get("reversible", True)),
                        rationale=item.get("rationale"),
                    )
                )
        return cls(entries=entries)

    def classify(self, tool_name: str, description: str | None = None) -> TaxonomyEntry | None:
        """Return the best-matching entry for a given tool name and (optional) docstring.

        Matching strategy (in priority order):
        1. Token-set match on the tool name — normalizes PascalCase/camelCase/snake_case
           to word tokens before comparing, so ``FileReadTool`` matches ``read_file``.
        2. Literal substring match on the description — natural-language docstrings are
           already human-readable; token splitting is not helpful there.

        The longest matching pattern wins (``send_email`` beats ``send`` when both match).
        """
        name_tokens = _to_tokens(tool_name)
        desc_lower = description.lower() if description else ""

        best: TaxonomyEntry | None = None
        for entry in self.entries:
            pattern_tokens = _to_tokens(entry.pattern)
            matched = _tokens_match(pattern_tokens, name_tokens) or (
                bool(desc_lower) and entry.pattern in desc_lower
            )
            if matched and (best is None or len(entry.pattern) > len(best.pattern)):
                best = entry
        return best
