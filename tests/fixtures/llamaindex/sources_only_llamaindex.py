"""§7 IG001 precision — source-only tools → (a) agent + tools detected, (b) IG001 NOT fire.

Tool names match existing taxonomy SOURCE patterns (search_web, read_email) so the
rule engine can evaluate them without a LlamaIndex taxonomy extension PR.
"""

from llama_index.core.agent import ReActAgent

search_web = None  # ast.Name; "search_web" matches taxonomy SOURCE pattern
read_email = None  # ast.Name; "read_email" matches taxonomy SOURCE pattern

agent = ReActAgent.from_tools(tools=[search_web, read_email], verbose=True)
