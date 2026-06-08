"""§6 Name resolution — @agent method name fallback when role= is absent (YAML-backed).

When Agent(config=...) provides no inline role= literal, the enclosing @agent
method name ("researcher") is the fallback. Parser must set agent.name = "researcher".
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"])
