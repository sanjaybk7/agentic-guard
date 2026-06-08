"""§7 IG001 precision — CrewAI agent with only SOURCE tools; IG001 must NOT fire.

Tool names use existing taxonomy patterns (search_web, read_email) so the rule
engine can classify them without waiting for the CrewAI taxonomy PR. This test
verifies that the source+sink-pair requirement from IG001 is enforced on
crewai-emitted agents, preventing the DeepGit-class false positive (agent present,
tools present, but no confused-deputy risk because no sink exists).
"""

from crewai import Agent

search_web = None  # ast.Name; "search_web" matches taxonomy SOURCE pattern
read_email = None  # ast.Name; "read_email" matches taxonomy SOURCE pattern

agent = Agent(
    role="Researcher",
    goal="Search the web and read emails to gather information.",
    backstory="Expert information gatherer.",
    tools=[search_web, read_email],
)
