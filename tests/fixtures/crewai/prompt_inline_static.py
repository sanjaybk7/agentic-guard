"""§4 IG002 — inline literal role/goal/backstory → system_prompt_is_dynamic=False.

All three fields are string literals. classify_prompt_expr returns False for each.
This is the C5-style non-YAML-backed case. IG002 must NOT fire.
"""

from crewai import Agent

agent = Agent(
    role="Analyst",
    goal="Analyze market data carefully and produce structured reports.",
    backstory="You are a seasoned analyst with ten years of experience in financial markets.",
)
