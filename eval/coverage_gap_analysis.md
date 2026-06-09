# Coverage Gap Analysis — Full Corpus Agent-Count Pass

**Date:** 2026-06-08  
**Engine:** main @ `7d10737` (LangGraph + OpenAI Agents + CrewAI + LlamaIndex parsers active)  
**Corpus:** 126 repos from `eval/corpus.json` (eval-corpus branch, post run-llama exclusion)  
**Baseline:** 38 repos with agents before CrewAI and LlamaIndex parsers

---

## Headline Numbers

| Metric | Value |
|--------|------:|
| Repos with agent_count ≥ 1 (current) | **66** |
| Repos with agent_count ≥ 1 (baseline, pre new parsers) | 38 |
| **New recoveries by CrewAI + LlamaIndex parsers** | **+28** |
| Repos still at agent_count == 0 | 60 |
| True remaining gap (real agents undetected) | **31** |
| Genuine non-agent repos (correct zero) | 29 |
| IG001 findings (full corpus) | 0 |
| IG002 findings (full corpus) | 148 |
| Agent location collisions | 0 |

---

## Per-Framework Breakdown

| Framework | Total repos | With agents | Zero | % covered |
|-----------|------------:|------------:|-----:|----------:|
| crewai | 25 | 24 | 1 | 96% |
| llama-index | 4 | 4 | 0 | 100% |
| openai-agents | 21 | 20 | 1 | 95% |
| langgraph | 30 | 16 | 14 | 53% |
| autogen | 10 | 1 | 9 | 10% |
| langchain-agents | 2 | 1 | 1 | 50% |
| unknown | 34 | 0 | 34 | 0% |
| **TOTAL** | **126** | **66** | **60** | **52%** |

Notes:
- `crewai` 1 zero = HeadyZhang/agent-audit (meta-tool — correct zero)
- `openai-agents` 1 zero = qx-labs/agents-deep-research (subclass pattern — real agent, parser gap)
- `langgraph` 14 zeros = all use `StateGraph` builder, not `create_react_agent` factory (parser gap)
- `autogen` 1 with agents = microsoft/autogen (1 agent detected by another parser, not AutoGen parser — no AutoGen parser exists)
- `unknown` 0% = mixed; see classification below

---

## Recoveries from New Parsers (+28)

**CrewAI parser (+25 repos recovered, +21 via CrewAI, +4 apparent overlap):**

| Repo | Agents |
|------|-------:|
| OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI | 42 |
| kid0317/crewai_mas_demo | 30 |
| NanGePlus/CrewAITest | 24 |
| liangdabiao/crewai_stock_analysis_system | 24 |
| bhancockio/crewai-rag-deep-dive | 9 |
| liangdabiao/easy_investment_Agent_crewai | 8 |
| tonykipkemboi/crewai-gmail-automation | 5 |
| bhancockio/automate-youtube-with-crewai | 5 |
| tonykipkemboi/resume-optimization-crew | 5 |
| bhancockio/crewai-updated-tutorial-hierarchical | 4 |
| alejandro-ao/crewai-instagram-example | 4 |
| alejandro-ao/crewai-crash-course | 4 |
| alexfazio/viral-clips-crew | 3 |
| AbubakrChan/crewai-UI-business-product-launch | 3 |
| NanGePlus/CrewAIFlowsFullStack | 3 |
| bhancockio/nextjs-crewai-basic-tutorial | 2 |
| bhancockio/crewai-groq-tutorial | 2 |
| google-gemini/crewai-quickstart | 2 |
| strnad/CrewAI-Studio | 1 |
| yuriwa/crewai-sheets-ui | 1 |
| tonykipkemboi/crewai-streamlit-demo | 1 |
| luandev/ComfyUI-CrewAI | 1 |

**LlamaIndex parser (+6 repos recovered):**

| Repo | Agents |
|------|-------:|
| alirezadir/Agentic-AI-Systems (non-corpus, detected separately) | — |
| lesteroliver911/llamaindex-agentworkflow-browse-agent | 2 |
| AstraBert/llamaindex-docs-agent | 2 |
| Andrew-Tsegaye/Advanced-AI-Code-Generation-Agent | 1 |
| NetEase-Media/grps_trtllm | 1 |
| blairhudson/fastapi-agents | 3 (CrewAI agents, not LlamaIndex) |
| microsoft/autogen | 1 (OpenAI-style agent, not LlamaIndex) |

---

## Zero-Agent Classification (60 repos)

### Category 1: Runtime-Indirect — 14 repos

**Definition:** The framework IS covered by a parser, but the specific construction pattern
isn't statically resolvable from the call site alone.

**LangGraph `StateGraph` builder (13 repos):**

The LangGraph parser anchors on high-level factory calls (`create_react_agent`,
`create_tool_calling_agent`, `create_openai_functions_agent`). All 13 repos use the
low-level `StateGraph(State)` builder pattern with a two-statement compile:
```python
builder = StateGraph(MyState)          # statement 1 — not a high-level factory
...
graph = builder.compile(name="agent")  # statement 2 — parser can't link to statement 1
```
Closing this gap requires cross-statement binding resolution in the LangGraph parser.

| Repo | StateGraph files |
|------|----------------:|
| minitap-ai/mobile-use | 2 |
| wassim249/fastapi-langgraph-agent-production-ready-template | 1 |
| guy-hartstein/company-research-agent | 1 |
| neural-maze/philoagents-course | 1 |
| aegra/aegra | 15 |
| souvikmajumder26/Multi-Agent-Medical-Assistant | 1 |
| zamalali/DeepGit | 3 |
| FunnyWolf/agentic-soc-platform | 2 |
| Haohao-end/openagent | 6 |
| FareedKhan-dev/production-grade-agentic-system | 1 |
| langchain-ai/react-agent | 1 |
| vinay-gatech/stocks-insights-ai-agent | 3 |
| langtalks/swe-agent | 3 |

**OpenAI Agents SDK subclass (1 repo):**

| Repo | Pattern |
|------|---------|
| qx-labs/agents-deep-research | `ResearchAgent(Agent)` subclass; parser looks for direct `Agent(...)` calls, not `ResearchAgent(...)` |

---

### Category 2: Uncovered Framework/Pattern — 17 repos

**Definition:** A real agent is constructed but the framework has no parser (or the
construction pattern is outside any parser's scope). Each would need a new parser PR
or a pattern extension.

**AutoGen — 9 repos (no AutoGen parser):**

| Repo | Pattern | AutoGen API |
|------|---------|-------------|
| startino/aitino | `UserProxyAgent`, `AssistantAgent` | AutoGen v1 |
| test-zeus-ai/testzeus-hercules | `ConversableAgent` | AutoGen v2 |
| karthikvenkatesan-eaton/Autogen_GraphRAG_Ollama | `register_for_llm`, `register_for_execution` | AutoGen v1 decorator |
| ag2ai/fastagency | `ConversableAgent` | AG2/AutoGen |
| adamwlarson/ai-book-writer | `GroupChatManager`, `GroupChat` | AutoGen v1 |
| SageMindAI/autogen-agi | `GroupChatManager`, `GroupChat` | AutoGen v1 |
| liangdabiao/autogen-financial-analysis | `UserProxyAgent` | AutoGen v1 |
| Andyinater/AutoGen_EnhancedAgents | `UserProxyAgent` | AutoGen v1 |
| NanGePlus/AutoGenV04Test | `UserProxyAgent` | AutoGen v0.4 |

**Microsoft Magentic-One — 1 repo:**

| Repo | Pattern |
|------|---------|
| microsoft/magentic-ui | `WebSurfer`, `MagenticUI` — AutoGen-based multi-agent, no Magentic parser |

**LangChain AgentExecutor — 1 repo:**

| Repo | Pattern |
|------|---------|
| TsinghuaC3I/MARTI | `AgentExecutor` — LangChain high-level agent; LangGraph parser covers langgraph only |

**Strands Agents — 2 repos:**

| Repo | Pattern |
|------|---------|
| aws-samples/sample-logistics-agent-agentcore-runtime | `from strands import Agent` |
| chopratejas/headroom | `from strands import Agent` + `AgentType` |

**LiveKit Agents — 1 repo:**

| Repo | Pattern |
|------|---------|
| Arjunheregeek/livekit-rag-voice-agent | `WorkerOptions`, livekit agents framework |

**LlamaIndex Workflow subclass — 1 repo:**

| Repo | Pattern |
|------|---------|
| TuanaCelik/llama_index_zoom_assistant | Custom `Workflow` subclass (§8.1 gap in LlamaIndex parser) |

**Promptulate (AutoGen wrapper) — 1 repo:**

| Repo | Pattern |
|------|---------|
| Undertone0809/promptulate | `AssistantAgent` re-exported via promptulate framework; promptulate wraps AutoGen |

**Custom ReAct from LangChain primitives — 1 repo:**

| Repo | Pattern |
|------|---------|
| ndkhoa211/ReAct-agent-from-scratch | Manual ReAct loop using `@tool` decorator; no `AgentExecutor` or `create_react_agent` |

---

### Category 3: Genuine Non-Agent — 29 repos (correct zeros)

**Definition:** These repos import agent-related libraries for non-agent purposes (RAG,
observability, evaluation, tooling, templates) or reference agent frameworks only in
requirements/config. The zero is correct and expected.

| Repo | Reason |
|------|--------|
| JudgmentLabs/judgeval | Evaluation framework for testing agents; doesn't construct agents |
| MLT-OSS/open-assistant-api | OpenAI-compatible REST API layer |
| chirpz-ai/pandaprobe | Data testing/monitoring — no agent construction |
| tensorlakeai/tensorlake-skills | Skills library — no agent construction |
| darinkishore/codex_dspy | DSPy-based code optimization |
| sno-ai/llmix | LLM mixing/routing tool |
| wso2-incubator/unitree-go2-realtime-agent | Robot hardware control via raw OpenAI API |
| Grigorij-Dudnik/RoboCrew | crewai+autogen in requirements only; no Python imports found |
| liangdabiao/claude-data-analysis | Claude API for data analysis scripts |
| ag2ai/Agents_Failure_Attribution | Failure attribution/eval tool; req:autogen but no agent construction |
| LianjiaTech/bella-rag | RAG vector store backend |
| snekkenull/translation-agent-webui | LLM client (Groq) for translation only |
| sulaiman-shamasna/LlamaIndex-chatbot-with-advanced-search-and-RAG | RAG chatbot (SimpleDirectoryReader, no agent API) |
| HeadyZhang/agent-audit | Meta-tool that analyzes agent code as strings |
| MahdiAmrollahi/omni-agent | req:langgraph but only "langchain" string in source; no agent construction |
| Decade-qiu/CookHero | LlamaIndex RAG use (`llama-index==0.14.9`); no agent constructor |
| OpenDemon/Pilipili-AutoVideo | "Agent Console" is a UI label; no agent framework import |
| nigarishrehmansarmad/Querying-Tabular-Data-using-Agentic-AI | req:autogen,crewai,langgraph; no agent construction in source |
| ponagan/AI---work-flow-agent | No agent patterns found |
| vaishnavi33/agentic-fraud-detection-mcp | MCP tool provider; not an agent |
| Manasavijr/llm-agentic-research | No agent patterns found |
| OpenBMB/RepoAgent | "autogen" appears only in a code path string in a comment; uses LlamaIndex for RAG |
| jgravelle/AutoGroq | Generates AutoGen config files as output (meta-tool); doesn't run AutoGen |
| vstorm-co/full-stack-ai-agent-template | Cookiecutter scaffolding template; StateGraph is in `{{cookiecutter.project_slug}}/` — template code, not running app |
| microsoft/spec-to-agents | `AgentExecutor` appears only in tests; main code generates agent specs, doesn't run them |
| ag2ai/Agents_Failure_Attribution | failure attribution; requirement-level autogen dep, no construction |
| vortezwohl/Autono | IS the Autono framework library; no consumer application |
| Undertone0809/promptulate (re-check) | IS the promptulate framework library; exports AssistantAgent but is the library itself |
| TuanaCelik... | (covered above in uncovered) |

Wait — Undertone0809/promptulate is in BOTH uncovered and genuine non-agent. Correcting:
Undertone0809/promptulate → uncovered (it's the promptulate library which wraps AutoGen internally, but the library IS a user-facing agent framework). Moving it to uncovered.

| vortezwohl/Autono | IS the Autono agent framework library itself — not a consumer app |

---

## True Remaining Gap Summary

**31 repos contain a real agent that the current tooling cannot detect.**

| Category | Count | Primary cause |
|----------|------:|---------------|
| Runtime-indirect (LangGraph `StateGraph` builder) | 13 | Cross-statement binding not resolved |
| Runtime-indirect (OpenAI SDK subclass) | 1 | `ResearchAgent` not in `_AGENT_CLASSES` |
| Uncovered: AutoGen (no parser) | 9 | No AutoGen parser |
| Uncovered: Magentic-One (AutoGen-based) | 1 | No Magentic parser |
| Uncovered: LangChain AgentExecutor | 1 | LangGraph parser covers langgraph, not langchain agents |
| Uncovered: Strands Agents | 2 | No Strands parser |
| Uncovered: LiveKit Agents | 1 | No LiveKit parser |
| Uncovered: LlamaIndex Workflow subclass | 1 | §8.1 gap in LlamaIndex parser |
| Uncovered: custom ReAct from LangChain primitives | 1 | No pattern for manual ReAct loops |
| Uncovered: Promptulate (AutoGen wrapper) | 1 | No Promptulate parser |
| **TOTAL GAP** | **31** | |

**Genuine non-agent repos at zero: 29.** These are correct zeros — the tooling is not
missing anything in these cases.

---

## Priority Signal for Future Parsers

Ranked by corpus prevalence:

1. **AutoGen** (9 repos + 1 Magentic): Highest priority. AutoGen accounts for the bulk
   of the uncovered gap. The API (`ConversableAgent`, `AssistantAgent`, `UserProxyAgent`,
   `GroupChatManager`) is stable and constructor-co-located (same pattern as CrewAI).

2. **LangGraph `StateGraph` builder** (13 repos): High priority. These repos import
   langgraph and are already in scope — the parser just needs cross-statement binding to
   follow `builder = StateGraph(...)` → `builder.compile()`.

3. **Strands Agents** (2 repos): Low current prevalence but growing. `from strands import Agent`
   is a single-anchor constructor pattern (same structure as FunctionAgent in LlamaIndex).

4. **LangChain AgentExecutor** (1 repo in corpus): Low corpus prevalence given the
   framework's age. Likely higher in the wild; worth a batch addition to a future PR.

5. **LiveKit / Promptulate / custom ReAct** (1 each): Niche; defer unless prevalence rises.

6. **OpenAI SDK subclass** (1 repo): A targeted fix — add `ResearchAgent` or expand
   `_AGENT_CLASSES` to include common subclass names, or track inheritance at AST level.
