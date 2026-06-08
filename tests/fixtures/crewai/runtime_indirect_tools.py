"""§3/§5 Runtime-indirect tools — Agent(config=runtime_dict) with no tools= kwarg.

Models C3/C4 style: the Agent(...) call is statically visible but tools come
from a runtime value (dict, DB, etc.). The parser must still emit the agent
(the call exists in source) with tools=[] and must NOT hallucinate tool names
by inspecting the config variable.
"""

from crewai import Agent


def make_agent(config: dict) -> Agent:
    return Agent(config=config)
