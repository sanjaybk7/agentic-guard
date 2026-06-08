"""§2 Negative — Agent(...) in a file that does NOT import crewai.

"Agent" is a common name. The parser must require a crewai import to avoid
false-positives in non-CrewAI code that happens to define or use an Agent class.
"""


class Agent:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


agent = Agent(
    role="Researcher",
    goal="Do research",
    backstory="Expert",
)
