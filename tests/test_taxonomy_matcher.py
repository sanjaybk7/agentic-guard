"""Tests for the token-set taxonomy matcher (Phase 1 — matcher fix).

The existing taxonomy uses snake_case patterns (read_file, web_search, ...).
Before this fix, PascalCase tool names like FileReadTool resolved to NEUTRAL
because "filereadtool" doesn't contain the substring "read_file" (underscore
missing). The fix tokenizes both sides before comparing.

These tests prove:
1. New classifications enabled by the fix (PascalCase tools now hit snake_case patterns).
2. Control set: names that must stay NEUTRAL — no over-matching introduced.
3. Existing snake_case tool names unchanged — no regressions.
4. _to_tokens() and _tokens_match() unit contracts.
"""

from __future__ import annotations

import pytest

from agentic_guard.ir import ToolClassification
from agentic_guard.taxonomy import Taxonomy, _to_tokens, _tokens_match


@pytest.fixture(scope="module")
def taxonomy() -> Taxonomy:
    return Taxonomy.load()


# ---------------------------------------------------------------------------
# Unit tests for _to_tokens
# ---------------------------------------------------------------------------


def test_to_tokens_snake_case() -> None:
    assert _to_tokens("read_file") == {"read", "file"}


def test_to_tokens_pascal_case() -> None:
    assert _to_tokens("FileReadTool") == {"file", "read", "tool"}


def test_to_tokens_camel_case() -> None:
    assert _to_tokens("readEmailTool") == {"read", "email", "tool"}


def test_to_tokens_acronym_prefix() -> None:
    assert _to_tokens("EXAAnswerTool") == {"exa", "answer", "tool"}


def test_to_tokens_filters_single_chars() -> None:
    tokens = _to_tokens("AStockDataTool")
    assert "a" not in tokens
    assert "stock" in tokens
    assert "data" in tokens
    assert "tool" in tokens


def test_to_tokens_snake_plus_digits() -> None:
    tokens = _to_tokens("web_search_tool")
    assert tokens == {"web", "search", "tool"}


def test_to_tokens_camelcase_mixed() -> None:
    assert _to_tokens("vectorSearch") == {"vector", "search"}


# ---------------------------------------------------------------------------
# Unit tests for _tokens_match
# ---------------------------------------------------------------------------


def test_tokens_match_exact_subset() -> None:
    assert _tokens_match(frozenset({"read", "file"}), frozenset({"file", "read", "tool"}))


def test_tokens_match_prefix_at_min_length() -> None:
    # "write" (5 chars ≥ 4) should prefix-match "writer"
    assert _tokens_match(frozenset({"write", "file"}), frozenset({"file", "writer", "tool"}))


def test_tokens_match_prefix_below_min_length_no_match() -> None:
    # "pay" (3 chars < 4) must hit exactly; "payment" is not "pay"
    assert not _tokens_match(frozenset({"pay"}), frozenset({"payment", "gateway"}))


def test_tokens_match_empty_pattern_never_matches() -> None:
    assert not _tokens_match(frozenset(), frozenset({"read", "file", "tool"}))


def test_tokens_match_partial_pattern_no_match() -> None:
    # "email" present but "send" absent → no match
    assert not _tokens_match(frozenset({"send", "email"}), frozenset({"email", "reader"}))


def test_tokens_match_requires_all_tokens() -> None:
    # Only "read" matches, "file" missing → no match
    assert not _tokens_match(frozenset({"read", "file"}), frozenset({"read", "database"}))


# ---------------------------------------------------------------------------
# Phase 1: new classifications from the matcher fix
# (PascalCase tool class names that previously resolved to NEUTRAL)
# ---------------------------------------------------------------------------


def test_file_read_tool_classifies_source(taxonomy: Taxonomy) -> None:
    """FileReadTool hits the existing read_file SOURCE pattern via token-set match."""
    entry = taxonomy.classify("FileReadTool")
    assert entry is not None, "FileReadTool must classify (not NEUTRAL)"
    assert entry.classification == ToolClassification.SOURCE
    assert entry.pattern == "read_file"


def test_file_writer_tool_classifies_sink(taxonomy: Taxonomy) -> None:
    """FileWriterTool hits write_file SINK via prefix match: write→writer."""
    entry = taxonomy.classify("FileWriterTool")
    assert entry is not None, "FileWriterTool must classify (not NEUTRAL)"
    assert entry.classification == ToolClassification.SINK
    assert entry.pattern == "write_file"


def test_vector_search_classifies_source(taxonomy: Taxonomy) -> None:
    """vectorSearch (camelCase) hits the vector_search SOURCE pattern."""
    entry = taxonomy.classify("vectorSearch")
    assert entry is not None, "vectorSearch must classify (not NEUTRAL)"
    assert entry.classification == ToolClassification.SOURCE
    assert entry.pattern == "vector_search"


# ---------------------------------------------------------------------------
# Existing matches: must be preserved (no regressions from the old matcher)
# ---------------------------------------------------------------------------


def test_scrape_website_tool_still_source(taxonomy: Taxonomy) -> None:
    """ScrapeWebsiteTool must still classify SOURCE (via scrape pattern)."""
    entry = taxonomy.classify("ScrapeWebsiteTool")
    assert entry is not None
    assert entry.classification == ToolClassification.SOURCE
    assert entry.pattern == "scrape"


def test_shell_executor_tool_still_sink(taxonomy: Taxonomy) -> None:
    """ShellExecutorTool must still classify SINK (via shell pattern)."""
    entry = taxonomy.classify("ShellExecutorTool")
    assert entry is not None
    assert entry.classification == ToolClassification.SINK
    assert entry.pattern == "shell"


def test_web_search_tool_still_source(taxonomy: Taxonomy) -> None:
    """web_search_tool must still classify SOURCE.

    Both 'web_search' and 'search_web' are same-length patterns; either
    can win disambiguation. We assert classification only.
    """
    entry = taxonomy.classify("web_search_tool")
    assert entry is not None
    assert entry.classification == ToolClassification.SOURCE
    assert entry.pattern in ("web_search", "search_web")


# ---------------------------------------------------------------------------
# Existing snake_case tool names: unchanged behavior
# ---------------------------------------------------------------------------


def test_read_email_snake_case_unchanged(taxonomy: Taxonomy) -> None:
    entry = taxonomy.classify("read_email")
    assert entry is not None
    assert entry.classification == ToolClassification.SOURCE


def test_send_email_snake_case_unchanged(taxonomy: Taxonomy) -> None:
    entry = taxonomy.classify("send_email")
    assert entry is not None
    assert entry.classification == ToolClassification.SINK


def test_write_file_snake_case_unchanged(taxonomy: Taxonomy) -> None:
    entry = taxonomy.classify("write_file")
    assert entry is not None
    assert entry.classification == ToolClassification.SINK


def test_search_web_snake_case_unchanged(taxonomy: Taxonomy) -> None:
    entry = taxonomy.classify("search_web")
    assert entry is not None
    assert entry.classification == ToolClassification.SOURCE


# ---------------------------------------------------------------------------
# Control set: names that must STAY NEUTRAL after the fix
# (no new over-matching)
# ---------------------------------------------------------------------------


def test_serper_dev_tool_classifies_source(taxonomy: Taxonomy) -> None:
    """Phase 3 added 'serper' pattern — SerperDevTool now classifies SOURCE."""
    entry = taxonomy.classify("SerperDevTool")
    assert entry is not None, "SerperDevTool must classify after Phase 3 taxonomy addition"
    assert entry.classification == ToolClassification.SOURCE
    assert entry.pattern == "serper"


def test_gmail_delete_tool_classifies_sink(taxonomy: Taxonomy) -> None:
    """Phase 3 added 'gmail_delete' pattern — GmailDeleteTool now classifies SINK."""
    entry = taxonomy.classify("GmailDeleteTool")
    assert entry is not None, "GmailDeleteTool must classify after Phase 3 taxonomy addition"
    assert entry.classification == ToolClassification.SINK
    assert entry.pattern == "gmail_delete"


def test_calculator_tool_stays_neutral(taxonomy: Taxonomy) -> None:
    assert taxonomy.classify("CalculatorTool") is None


def test_fake_tool_stays_neutral(taxonomy: Taxonomy) -> None:
    assert taxonomy.classify("FakeTool") is None


def test_bare_tool_name_stays_neutral(taxonomy: Taxonomy) -> None:
    """The single word 'tool' must never auto-match any pattern."""
    assert taxonomy.classify("tool") is None


def test_report_writing_tool_stays_neutral(taxonomy: Taxonomy) -> None:
    """ReportWritingTool: write_file needs the 'file' token; absent here.
    Correct — this is a Phase 2 investigation item.
    """
    assert taxonomy.classify("ReportWritingTool") is None


def test_dall_e_tool_stays_neutral(taxonomy: Taxonomy) -> None:
    """DallETool has no existing pattern — stays NEUTRAL (Phase 3: skip)."""
    assert taxonomy.classify("DallETool") is None
