"""§7 IG001 precision — CrewAI agent with only SINK tools; IG001 must NOT fire.

Tool names use existing taxonomy patterns (send_email, write_file) so the rule
engine can classify them without waiting for the CrewAI taxonomy PR. No source
tool means no attacker-controlled input can flow into the sink — IG001 requires
both a SOURCE and a SINK to fire.
"""

from crewai import Agent

send_email = None  # ast.Name; "send_email" matches taxonomy SINK pattern
write_file = None  # ast.Name; "write_file" matches taxonomy SINK pattern

agent = Agent(
    role="Communicator",
    goal="Send emails and write files on behalf of users.",
    backstory="Expert communication assistant.",
    tools=[send_email, write_file],
)
