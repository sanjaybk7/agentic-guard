"""Vulnerable (TP preservation): user-supplied inputs interpolated into a
prompt template, then stored on ``self`` and passed to an agent.

Mirrors F21 (xark-argo/argo): a bot-platform prompt template is filled
from user-supplied ``inputs`` via string substitution, stored on a
runner instance, and passed as ``prompt=self.instruction or ""``. The
classifier sees ``BoolOp(Or, Attribute(self, instruction), Constant(""))``
which is not handled by any narrowing branch — falls through to the
catch-all and stays dynamic. Must still fire IG002 after the fixes.
"""

from langgraph.prebuilt import create_react_agent


class BotRunner:
    def __init__(self, template: str, inputs: dict[str, str]) -> None:
        instruction = template
        for key, value in inputs.items():
            instruction = instruction.replace(f"{{{{{key}}}}}", str(value))
        self.instruction = instruction

    def build(self) -> object:
        return create_react_agent(
            model="claude-opus-4-7",
            tools=[],
            prompt=self.instruction or "",
        )
