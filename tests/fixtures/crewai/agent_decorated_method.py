"""§2/§6 Detection — @agent-decorated method returning Agent(...).

The @agent decorator is registration metadata only; the Agent(...) call node
is the detection anchor. Agent name comes from the method name ("researcher"),
not from role= (which is YAML-backed via config=).
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
        )
