"""Vulnerable (TP preservation): Streamlit ``st.text_input`` value flows
into a system-prompt f-string.

Mirrors F14 (AbubakrChan/crewai-UI-business-product-launch). The real
fixture uses CrewAI's ``goal=``; here we use LangGraph's ``prompt=`` so
the registered parser captures the agent. ``product_name`` is a
function-local Call result; PR #5 records it as ``locally_bound`` but
not as a literal binding, so the JoinedStr slot's name stays
unresolved.

Must still fire IG002 after the fixes — Fix 1's generic-Call short-
circuit does not apply at this site (the f-string is classified
directly; the surrounding ``st.text_input(...)`` Call lives on the
right-hand side of an assignment, not inside the prompt expression).
"""

import streamlit as st
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def lookup(key: str) -> str:
    """Look up a value."""
    return ""


def make_agent():
    product_name = st.text_input("Enter a product name to analyse.")
    return create_react_agent(
        model="claude-opus-4-7",
        tools=[lookup],
        prompt=f"You are a product analyst for {product_name}.",
    )
