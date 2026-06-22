"""LG-3 regression guard: a ``def bind_tools`` METHOD must not create an agent.

Fake/stub chat models in test suites commonly define their own ``bind_tools``
method (returning self) so the agent runtime can call it. That is a method
*definition*, not a tool-binding *call*, and must never be mistaken for an agent.
The only real call here, ``self.bind_tools(...)`` inside the method, binds a
runtime ``tools`` parameter (not a literal), so it is also correctly skipped.
"""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeChatModel(GenericFakeChatModel):  # type: ignore[misc]
    def bind_tools(self, tools, **kwargs):
        """Override bind_tools to return self."""
        return self
