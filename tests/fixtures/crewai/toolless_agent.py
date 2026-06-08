"""§5 Emit tool-less — no tools= kwarg; agent still emitted with tools=[].

Config-only and no-tools agents (e.g., google-gemini/crewai-quickstart) must
increment agent_count even when tools cannot be extracted. tools=[] is correct;
the parser must not skip the agent simply because it has no tool list.
"""

from crewai import Agent

agent = Agent(
    role="Writer",
    goal="Write clear and concise reports",
    backstory="You are a skilled technical writer.",
)
