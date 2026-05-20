"""§18 (amended) — assignment inside ``with`` block does NOT resolve.

Original spec proposal was conditional resolution; the amendment
simplifies to "do not resolve" for consistency with §16/§17. The
``with open(...) as f: prompt = "lit"`` pattern is rare in real agent
code; the implementation cost of distinguishing this case from §16/§17
isn't worth the marginal corpus benefit.
"""

from agents import Agent, function_tool


@function_tool
def lookup(key: str) -> str:
    return ""


def make_agent():
    with open("/dev/null") as f:
        PROMPT = "with-block literal"
    return Agent(
        name="with-block",
        instructions=PROMPT,
        tools=[lookup],
        model="gpt-4o",
    )
