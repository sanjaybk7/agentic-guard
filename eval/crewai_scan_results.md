# CrewAI Corpus Scan Results

Scan date: 2026-06-07  
Branch: `crewai-parser`  
Scanner: `agentic-guard` with `CrewAIParser` (green implementation)  
Corpus: 25 crewai-tagged repos from `eval/corpus.json` (eval-corpus branch)

---

## Summary

| Metric | Value |
|--------|-------|
| Repos scanned | 25 |
| Files scanned | 567 |
| Agents detected | 188 |
| Repos with ≥1 agent | 24 / 25 |
| Recovery (pre-scan zeros → agent found) | 23 / 24 (95.8 %) |
| IG001 findings | 0 |
| IG002 findings | 28 across 8 repos |
| Cross-parser collisions | 0 |

---

## Recovery

24 of 25 repos had `agents_seen = 0` before the CrewAI parser was added (one repo,
`LangGraph-GUI/CrewAI-GUI-Qt`, already had 1 agent detected by another parser).
After the scan, 23 of those 24 recovered to ≥ 1 agent. The remaining repo
(`HeadyZhang/agent-audit`) is discussed in [Zero-agent remainder](#zero-agent-remainder).

---

## Per-repo table

| Repo | SHA | Pre | Agents | IG001 | IG002 | Collisions | Files |
|------|-----|----:|-------:|------:|------:|-----------:|------:|
| strnad/CrewAI-Studio | c1dbabd4 | 0 | 1 | 0 | 1 | 0 | 27 |
| alexfazio/viral-clips-crew | 82888d94 | 0 | 3 | 0 | 3 | 0 | 9 |
| liangdabiao/easy_investment_Agent_crewai | ec73a6cb | 0 | 8 | 0 | 0 | 0 | 16 |
| NanGePlus/CrewAITest | 17ee7bf1 | 0 | 24 | 0 | 0 | 0 | 48 |
| LangGraph-GUI/CrewAI-GUI-Qt | 463bb270 | 1 | 2 | 0 | 1 | 0 | 18 |
| AbubakrChan/crewai-UI-business-product-launch | 52a235f7 | 0 | 3 | 0 | 3 | 0 | 1 |
| tonykipkemboi/crewai-gmail-automation | 0946e174 | 0 | 5 | 0 | 0 | 0 | 8 |
| bhancockio/crewai-updated-tutorial-hierarchical | b5f255aa | 0 | 4 | 0 | 0 | 0 | 6 |
| bhancockio/automate-youtube-with-crewai | 0f46a5c4 | 0 | 5 | 0 | 0 | 0 | 6 |
| liangdabiao/crewai_stock_analysis_system | aab66c6a | 0 | 24 | 0 | 5 | 0 | 19 |
| tonykipkemboi/resume-optimization-crew | 46a5d328 | 0 | 5 | 0 | 0 | 0 | 6 |
| bhancockio/crewai-rag-deep-dive | a17d88e9 | 0 | 9 | 0 | 0 | 0 | 6 |
| bhancockio/nextjs-crewai-basic-tutorial | 959e7bc0 | 0 | 2 | 0 | 1 | 0 | 10 |
| NanGePlus/CrewAIFlowsFullStack | c29e3909 | 0 | 3 | 0 | 0 | 0 | 8 |
| kid0317/crewai_mas_demo | d5cfc79d | 0 | 30 | 0 | 10 | 0 | 174 |
| alejandro-ao/crewai-instagram-example | c0439bec | 0 | 4 | 0 | 0 | 0 | 5 |
| bhancockio/crewai-groq-tutorial | d390d847 | 0 | 2 | 0 | 0 | 0 | 3 |
| OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI | 7dde376e | 0 | 42 | 0 | 0 | 0 | 33 |
| alejandro-ao/crewai-crash-course | a1104035 | 0 | 4 | 0 | 4 | 0 | 4 |
| yuriwa/crewai-sheets-ui | 46ee39143 | 0 | 1 | 0 | 0 | 0 | 26 |
| tonykipkemboi/crewai-streamlit-demo | 653549a5 | 0 | 1 | 0 | 0 | 0 | 6 |
| google-gemini/crewai-quickstart | 5978d64a | 0 | 2 | 0 | 0 | 0 | 4 |
| luandev/ComfyUI-CrewAI | c19cac0a | 0 | 1 | 0 | 0 | 0 | 12 |
| HeadyZhang/agent-audit | 27c8416b | 0 | 0 | 0 | 0 | 0 | 81 |
| blairhudson/fastapi-agents | 2f58a991 | 0 | 3 | 0 | 0 | 0 | 31 |
| **TOTAL** | | **1** | **188** | **0** | **28** | **0** | **567** |

---

## IG001 findings (0)

No IG001 findings. Expected: CrewAI ecosystem tools (SerperDevTool, FileReadTool,
etc.) are classified `NEUTRAL` until the CrewAI taxonomy extension PR lands. Without
taxonomy entries that tag tools as SOURCE or SINK, the confused-deputy rule has no
cross-classification pair to fire on.

---

## IG002 findings (28 across 8 repos)

| Repo | Count | Pattern observed |
|------|------:|-----------------|
| strnad/CrewAI-Studio | 1 | f-string in role/goal/backstory |
| alexfazio/viral-clips-crew | 3 | f-string in role/goal/backstory |
| LangGraph-GUI/CrewAI-GUI-Qt | 1 | f-string in role/goal/backstory |
| AbubakrChan/crewai-UI-business-product-launch | 3 | f-string in role/goal/backstory |
| liangdabiao/crewai_stock_analysis_system | 5 | `goal=f"收集{company}的市场趋势..."` and similar Chinese-language f-strings |
| bhancockio/nextjs-crewai-basic-tutorial | 1 | f-string in role/goal/backstory |
| kid0317/crewai_mas_demo | 10 | f-strings across multiple agent definitions |
| alejandro-ao/crewai-crash-course | 4 | f-string in role/goal/backstory |

The `liangdabiao/crewai_stock_analysis_system` pattern was the corpus evidence
used to promote §4's "Hypothetical dynamic case" to "Dynamic case (evidenced in corpus)"
in the design doc.

---

## Cross-parser collisions (0)

Zero collisions across all 25 repos. The `both_import_collision.py` regression test
confirms the dedup path works; the corpus result confirms that real CrewAI repos do
not mix `from crewai import Agent` with `from agents import ...` in a way that triggers
the OpenAI Agents parser's `matches_file` on the same file.

---

## Zero-agent remainder

**`HeadyZhang/agent-audit`** (81 files, 0 agents detected).

Manual inspection: this repo uses a custom `BaseAgent` abstraction and does not call
the `crewai.Agent(...)` constructor directly at the AST level. Agents are instantiated
at runtime via factory methods that return `Agent`-subclass objects assembled from
config. The static constructor anchor `Agent(...)` is absent from parsed source, so
the parser correctly emits nothing rather than hallucinating detections.

This is a known limitation of AST-level static analysis: factory-pattern or fully
config-driven CrewAI usage falls outside detection scope. The design doc §5
("Tool-less agents and config-only agents") acknowledges that runtime-assembled
agents cannot be statically detected.
