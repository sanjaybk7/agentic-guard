"""§4 IG002 — f-string role/goal → system_prompt_is_dynamic=True, taint source captured.

Evidenced in liangdabiao/crewai_stock_analysis_system/src/crews/data_collection_crew.py
(goal=f"收集{company}的市场趋势..."). Not hypothetical — real pattern in the corpus.
classify_prompt_expr detects the JoinedStr node and extracts "company" as a taint source.
IG002 must fire on this agent.
"""

from crewai import Agent


def make_agent(company: str) -> Agent:
    return Agent(
        role=f"Analyst for {company}",
        goal=f"Analyze {company}'s financial position and market standing.",
        backstory="You are an expert financial analyst.",
    )
