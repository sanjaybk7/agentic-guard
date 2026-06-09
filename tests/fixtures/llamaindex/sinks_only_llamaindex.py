"""§7 IG001 precision — sink-only tools → (a) agent + tools detected, (b) IG001 NOT fire.

Tool names match existing taxonomy SINK patterns (send_email, write_file) so the
rule engine can evaluate them without a LlamaIndex taxonomy extension PR.
"""

from llama_index.core.agent import ReActAgent

send_email = None  # ast.Name; "send_email" matches taxonomy SINK pattern
write_file = None  # ast.Name; "write_file" matches taxonomy SINK pattern

agent = ReActAgent.from_tools(tools=[send_email, write_file], verbose=True)
