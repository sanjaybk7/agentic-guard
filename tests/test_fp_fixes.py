"""Tests for the false-positive fixes added after real-world scanning.

Each fixture in tests/fixtures/safe/ that exercises a previously-noisy pattern
has a corresponding assertion here that confirms it stays clean.
"""

from __future__ import annotations

from pathlib import Path

from agentic_guard.engine import Scanner

FIXTURES = Path(__file__).parent / "fixtures"


def _rule_ids(path: Path) -> set[str]:
    return {f.rule_id for f in Scanner().scan(path).findings}


def test_openai_constant_prompt_no_findings() -> None:
    """instructions=ANALYST_PROMPT where ANALYST_PROMPT = '...' must not fire IG002."""
    assert "IG002" not in _rule_ids(FIXTURES / "safe" / "openai_constant_prompt.py")


def test_openai_callable_instructions_no_findings() -> None:
    """instructions=callable_function must not fire IG002 (canonical SDK pattern)."""
    assert "IG002" not in _rule_ids(FIXTURES / "safe" / "openai_callable_instructions.py")


def test_openai_safe_helper_no_findings() -> None:
    """instructions=prompt_with_handoff_instructions('...') must not fire IG002."""
    assert "IG002" not in _rule_ids(FIXTURES / "safe" / "openai_safe_helper.py")


def test_langgraph_constant_prompt_no_findings() -> None:
    """prompt=SYSTEM_PROMPT where SYSTEM_PROMPT = '...' must not fire IG002."""
    assert "IG002" not in _rule_ids(FIXTURES / "safe" / "langgraph_constant_prompt.py")


def test_dynamic_prompt_still_fires() -> None:
    """Regression: f-string with truly user-controlled var must still fire IG002."""
    assert "IG002" in _rule_ids(FIXTURES / "vulnerable" / "dynamic_prompt.py")


def test_openai_dynamic_prompt_still_fires() -> None:
    """Regression: same for OpenAI SDK dynamic prompt fixture."""
    assert "IG002" in _rule_ids(FIXTURES / "vulnerable" / "openai_dynamic_prompt.py")


# -------- KL-002 / IfExp / SDK-allowlist fixes ---------------------------
# These fixes narrow `classify_prompt_expr` so previously-flagged FPs are
# correctly classified static. The dangerous direction of error is a false
# negative: a genuinely dynamic prompt newly classified static would let
# IG002 miss a real TP. Each "must-not-fire" case below targets a specific
# narrowing branch; the matching TP-preservation cases at the bottom prove
# the narrowing didn't bleed into a real injection pattern.


def test_callable_static_composition_no_findings() -> None:
    """KL-002: Agent(instructions=build_prompt(base_instructions="literal"))
    must not fire IG002 when the callee and every argument name resolves.
    """
    assert "IG002" not in _rule_ids(
        FIXTURES / "safe" / "callable_static_composition.py"
    )


def test_ifexp_between_constants_no_findings() -> None:
    """IfExp: instructions=PROMPT_A if flag else PROMPT_B must not fire
    when both branches resolve to module-level string constants.
    """
    assert "IG002" not in _rule_ids(
        FIXTURES / "safe" / "ifexp_between_constants.py"
    )


def test_sdk_allowlisted_name_no_findings() -> None:
    """SDK allowlist: f-string interpolation of RECOMMENDED_PROMPT_PREFIX
    (imported from agents.extensions.handoff_prompt) must not fire IG002.
    """
    assert "IG002" not in _rule_ids(
        FIXTURES / "safe" / "sdk_known_static_name.py"
    )


# -------- TP preservation: the 4 IG002 TPs MUST still fire ---------------
# F10/F17 (param into prompt), F14 (Streamlit input into prompt), F21
# (template substitution from user inputs). A failure here is the worst
# outcome — the narrowing fixes have introduced a false negative.


def test_param_into_prompt_still_fires() -> None:
    """F10/F17 TP: caller-supplied function parameter interpolated into
    a system-prompt f-string. Must still fire IG002 after the fixes.
    """
    assert "IG002" in _rule_ids(
        FIXTURES / "vulnerable" / "crewai_param_into_goal.py"
    ), "F10/F17 TP regressed: function parameter into prompt should fire IG002"


def test_streamlit_input_into_prompt_still_fires() -> None:
    """F14 TP: st.text_input() value interpolated into a system-prompt
    f-string. Must still fire IG002 after the fixes.
    """
    assert "IG002" in _rule_ids(
        FIXTURES / "vulnerable" / "streamlit_input_into_prompt.py"
    ), "F14 TP regressed: Streamlit input into prompt should fire IG002"


def test_template_user_inputs_still_fires() -> None:
    """F21 TP: user-supplied inputs interpolated into a prompt template,
    stored on self, passed as ``prompt=self.instruction or ""``. Must
    still fire IG002 after the fixes.
    """
    assert "IG002" in _rule_ids(
        FIXTURES / "vulnerable" / "template_user_inputs.py"
    ), "F21 TP regressed: template substitution from user inputs should fire IG002"
