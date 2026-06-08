"""§4 IG002 — config=self.agents_config['x'] (YAML-backed) → system_prompt_is_dynamic=False.

All role/goal/backstory come from a YAML file loaded at runtime. The YAML loader
cannot produce f-strings or concatenation, so the result is always static.
Parser must set system_prompt_is_dynamic=False WITHOUT opening or parsing any YAML file.
"""

from crewai import Agent
from crewai.project import CrewBase, agent


@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"

    @agent
    def analyst(self) -> Agent:
        return Agent(config=self.agents_config["analyst"])
