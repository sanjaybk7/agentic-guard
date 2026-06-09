"""§2/§3.1 Negative — ReActAgent.from_tools(...) without any llama_index import → NOT detected.

File match requires an import from llama_index (or llama_index.*). Without it the
parser must skip the file even if a from_tools call is syntactically present.
"""

# No llama_index import anywhere in this file.
ReActAgent = None  # dummy; no llama_index import so file must not match
agent = ReActAgent.from_tools(tools=["tool1"], verbose=True)
