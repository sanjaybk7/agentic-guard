# LlamaIndex Corpus Scan Results

**Branch:** `llamaindex-parser`  
**Parser commit:** `8b44ec0869a4073d5f9034376dc7f41b834f0f61`  
**Scan date:** 2026-06-08  
**Engine:** LlamaIndexParser only (isolated from CrewAI/LangGraph/OpenAI parsers)

---

## Scope

Identified 27 repos in `eval/repos/` that reference `llama_index` in Python source or
config files (grep across `*.py`, `*.txt`, `*.toml`, `*.cfg`). These repos were scanned
with the current engine at pinned local SHAs.

---

## Per-Repo Results

| Repo | Agents | IG001 | IG002 | Collisions |
|------|-------:|------:|------:|-----------:|
| AgentOps-AI | 0 | 0 | 0 | 0 |
| alirezadir | 14 | 0 | 0 | 0 |
| Andrew-Tsegaye | 1 | 0 | 0 | 0 |
| AstraBert | 2 | 0 | 0 | 0 |
| blairhudson | 0 | 0 | 0 | 0 |
| comet-ml | 0 | 0 | 0 | 0 |
| Decade-qiu | 0 | 0 | 0 | 0 |
| denniszielke | 1 | 0 | 0 | 0 |
| HeadyZhang | 0 | 0 | 0 | 0 |
| henrii1 | 0 | 0 | 0 | 0 |
| lesteroliver911 | 2 | 0 | 0 | 0 |
| LianjiaTech | 0 | 0 | 0 | 0 |
| microsoft | 0 | 0 | 0 | 0 |
| MODSetter | 0 | 0 | 0 | 0 |
| NetEase-Media | 1 | 0 | 0 | 0 |
| OpenBMB | 0 | 0 | 0 | 0 |
| Repello-AI | 3 | 0 | 0 | 0 |
| run-llama | 156 | 0 | 5 | 0 |
| RyjoxTechnologies | 0 | 0 | 0 | 0 |
| SageMindAI | 0 | 0 | 0 | 0 |
| snekkenull | 0 | 0 | 0 | 0 |
| sulaiman-shamasna | 0 | 0 | 0 | 0 |
| szczyglis-dev | 4 | 0 | 4 | 0 |
| TuanaCelik | 0 | 0 | 0 | 0 |
| velocitybolt | 0 | 0 | 0 | 0 |
| victordibia | 1 | 0 | 0 | 0 |
| vstorm-co | 0 | 0 | 0 | 0 |
| **TOTAL** | **185** | **0** | **9** | **0** |

---

## Recovery

**10 of 27 repos move from 0 → ≥ 1 agent** after the LlamaIndex parser lands.

Before this parser, all 27 repos had 0 detected LlamaIndex agents (no parser existed).
The 10 repos that now have coverage: alirezadir (14), AstraBert (2), Andrew-Tsegaye (1),
denniszielke (1), lesteroliver911 (2), NetEase-Media (1), Repello-AI (3), run-llama (156),
szczyglis-dev (4), victordibia (1).

---

## Agent Totals and Distribution

185 agents total across 27 repos.

| Repo | Agents | Notes |
|------|-------:|-------|
| run-llama | 156 | The llama_index library repo itself; 150 from 107 example notebooks, ~6 from .py |
| alirezadir | 14 | Tutorial/course repo (Agentic-AI-Systems); multiple worked examples |
| szczyglis-dev | 4 | py-gpt production app; FunctionAgent in workflow providers |
| Repello-AI | 3 | Agent-Wiz example file |
| AstraBert | 2 | Two nearly-identical Docker/script variants of the same agent |
| lesteroliver911 | 2 | Two FunctionAgent constructors in an agentworkflow demo |
| Andrew-Tsegaye | 1 | Single ReActAgent.from_tools in code-generation agent |
| denniszielke | 1 | Single ReActAgent in react-agent-li.py |
| NetEase-Media | 1 | Single OpenAIAgent.from_tools in llamaindex AI agent client |
| victordibia | 1 | Single FunctionAgent in hello-world sample |

run-llama inflates the raw count significantly. Excluding it: **29 agents across 9 user repos**.

---

## Construction-Form Breakdown

Across all 185 agents (LlamaIndex parser's `_is_from_tools_call` vs `call_base_name` in
`_CONSTRUCTOR_CLASSES`):

| Form | Receiver/Class | Count | % |
|------|---------------|------:|--:|
| `FunctionAgent(...)` constructor | FunctionAgent | 162 | 87.6% |
| `X.from_tools(...)` classmethod | ReActAgent | 18 | 9.7% |
| `X.from_tools(...)` classmethod | OpenAIAgent | 5 | 2.7% |
| `X.from_tools(...)` classmethod | FunctionCallingAgent | **0** | 0% |

**FunctionCallingAgent never appeared across the full scan.** The design doc (§8.2) noted
it as "documented-but-unseen at zero marginal cost." That holds: adding it to
`_FROM_TOOLS_CLASSES` costs nothing and provides future coverage if the API sees adoption,
but it contributed 0 detections in this corpus.

The FunctionAgent constructor dominates at 88%, confirming the survey finding that the
v2 workflow API (`llama_index.core.agent.workflow`) is the current construction pattern.
from_tools survives in older examples and tutorial code.

---

## Findings: IG001 and IG002

### IG001 (Confused Deputy)

**0 findings** across all 27 repos.

Expected: LlamaIndex tool classes (`QueryEngineTool`, `FunctionTool`) are classified
NEUTRAL in the current taxonomy — no taxonomy extension PR has been filed. Without a
taxonomy entry mapping these tool names to SOURCE or SINK, no IG001 trigger is possible.
This is a taxonomy gap, not a false negative.

### IG002 (Dynamic System Prompt)

**9 findings** across 2 repos.

**run-llama (5 IG002):**
All in notebook examples. The `system_prompt=` arguments are interpolated f-strings or
variables passed at runtime in tutorial code. These are pedagogical examples showing
parameterized agent construction — not indicators of vulnerable production code. Reported
as detections, not verified vulnerabilities.

```
docs/examples/agent/openai_agent_context_retrieval.ipynb:19   — taint: `context`
docs/examples/tools/llama-index-tools-shopify/.../shopify.ipynb:7 — taint: `query`
docs/examples/agent/agent_builder.ipynb:49                    — taint: `system_prompt`
docs/examples/agent/multi_document_agents-v1.ipynb:68         — taint: `file_base`
docs/examples/agent/return_direct_agent.ipynb:22              — taint: `system_prompt`
```

**szczyglis-dev (4 IG002):**
Production code in `py-gpt` — a desktop AI client. All four agents (PlannerExecutor,
Supervisor, Worker, OpenAIWorkflowAgent) receive `system_prompt=` via runtime-injected
prompt strings, consistent with a user-configurable app. Detections are sound: the
system prompt is demonstrably runtime-dynamic. Not verified as exploitable.

```
provider/agents/llama_index/workflow/openai.py:180    — taint: `prompt`
provider/agents/llama_index/workflow/planner.py:177   — taint: `prompt`
provider/agents/llama_index/workflow/supervisor.py:333 — taint: `prompt`
provider/agents/llama_index/workflow/supervisor.py:339 — taint: `prompt`
```

---

## Collisions

**0 agent_location_collisions.** No file triggered both LlamaIndexParser and another
parser at the same (file, line, col). Expected: LlamaIndex construction forms are
syntactically distinct from CrewAI/LangGraph/OpenAI patterns.

---

## Zero-Agent Remainder (17 repos)

17 of 27 repos remain at 0 agents after the parser. One-line reason for each:

| Repo | Reason |
|------|--------|
| AgentOps-AI | RAG/observability use (`VectorStoreIndex`, `Settings`); no agent constructor |
| blairhudson | Uses `OpenAIAgent.from_llm()` — different factory method, not `from_tools()`; not in receiver set |
| comet-ml | Observability tracing wrapper for llama_index; no agent construction |
| Decade-qiu | RAG use (`llama-index==0.14.9` in requirements); no agent constructor found in source |
| HeadyZhang | Meta-tool that inspects llama_index import strings (agent-audit repo); llama_index is a string constant, not an import |
| henrii1 | Uses `RouterQueryEngine` pattern; no agent constructor |
| LianjiaTech | RAG vector store backend (bella-rag); no agent constructor |
| microsoft | AutoGen repo; llama_index only in docs/requirements referencing Ollama — no Python import |
| MODSetter | llama_index in requirements only; no Python source that imports it |
| OpenBMB | Uses llama_index for RAG chat engine (`FunctionCallingLLM`, `ChatPromptTemplate`); no agent constructor |
| RyjoxTechnologies | llama_index in requirements only; no Python source import |
| SageMindAI | AutoGen-based repo listing `llama_index==0.9.8` (v0) as dep; no llama_index agent usage |
| snekkenull | Uses llama_index LLM client (Groq) for translation; not agent framework |
| sulaiman-shamasna | RAG chatbot (`SimpleDirectoryReader`); no agent constructor |
| TuanaCelik | Custom `Workflow` subclass pattern (§8.1 design doc gap); uses `llama_index.core.workflow`, not agent constructors |
| velocitybolt | Uses `SimpleWebPageReader` for data extraction; no agent constructor |
| vstorm-co | llama_index in requirements only; no Python source import |

The blairhudson case (`from_llm()` vs `from_tools()`) is the only one that represents an
actual missed agent. All others are genuinely not using the LlamaIndex agent construction
APIs the parser targets.

---

## Summary

| Metric | Value |
|--------|------:|
| Repos scanned | 27 |
| Repos with ≥ 1 agent (recovery) | 10 |
| Total agents | 185 |
| Total agents (excl. run-llama library repo) | 29 |
| IG001 findings | 0 |
| IG002 findings | 9 |
| Agent location collisions | 0 |
| FunctionCallingAgent appearances | 0 |
| FunctionAgent constructor share | 88% |
| from_tools share | 12% |
