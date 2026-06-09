# LlamaIndex Corpus Scan Results

**Branch:** `llamaindex-parser`  
**Parser commit:** `8b44ec0869a4073d5f9034376dc7f41b834f0f61`  
**Scan date:** 2026-06-08  
**Engine:** LlamaIndexParser only (isolated from CrewAI/LangGraph/OpenAI parsers)

---

## Corpus scope

27 repos in `eval/repos/` import `llama_index` in Python source or config files.
Of these, `run-llama/llama_index` is the framework's own example/notebook collection
and has been **excluded from the corpus** (added to `EXCLUDED_REPOS` in
`eval/prep_corpus.py` on the `eval-corpus` branch; corpus size 127 → 126). Its
150 pedagogical-notebook agents would distort per-application metrics.

The 26 remaining repos are the application corpus scanned here.

---

## Headline numbers (application corpus only)

| Metric | Value |
|--------|------:|
| Repos scanned | 26 |
| Repos with ≥ 1 agent | 10 |
| **LlamaIndex agents (application repos)** | **35** |
| IG001 findings | 0 |
| IG002 findings | 4 |
| Agent location collisions | 0 |

run-llama (excluded) contributed 156 additional agents and 5 IG002 findings from its
own examples; not counted in application totals.

---

## Per-Repo Results (26 application repos)

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
| RyjoxTechnologies | 0 | 0 | 0 | 0 |
| SageMindAI | 0 | 0 | 0 | 0 |
| snekkenull | 0 | 0 | 0 | 0 |
| sulaiman-shamasna | 0 | 0 | 0 | 0 |
| szczyglis-dev | 4 | 0 | 4 | 0 |
| TuanaCelik | 0 | 0 | 0 | 0 |
| velocitybolt | 0 | 0 | 0 | 0 |
| victordibia | 1 | 0 | 0 | 0 |
| vstorm-co | 0 | 0 | 0 | 0 |
| **TOTAL** | **35** | **0** | **4** | **0** |

---

## Recovery

**10 of 11 agent-bearing llama-index repos recovered.** The one real miss is
**blairhudson**, which uses `OpenAIAgent.from_llm()` — a different classmethod not in
the receiver set. The remaining 16 repos at zero are genuine non-agent cases:

- RAG/vector store use (AgentOps-AI, henrii1, LianjiaTech, OpenBMB, sulaiman-shamasna,
  velocitybolt)
- Observability/tracing wrapper (comet-ml)
- Requirements-only reference — no Python import (MODSetter, RyjoxTechnologies, vstorm-co)
- AutoGen/different framework with llama_index as dependency (microsoft, SageMindAI)
- Meta-tool that analyzes llama_index imports as strings (HeadyZhang)
- Workflow subclass paradigm (TuanaCelik — `llama_index.core.workflow.Workflow`, §8.1 gap)
- LLM client use, not agent framework (snekkenull, Decade-qiu)

---

## Agent Totals and Distribution

35 agents across 10 application repos.

| Repo | Agents | Notes |
|------|-------:|-------|
| alirezadir | 14 | Tutorial/course repo (Agentic-AI-Systems); multiple worked examples |
| szczyglis-dev | 4 | py-gpt production desktop app; FunctionAgent in workflow providers |
| Repello-AI | 3 | Agent-Wiz example |
| AstraBert | 2 | Two variants (Docker/script) of the same docs agent |
| lesteroliver911 | 2 | Two FunctionAgent constructors in an agentworkflow demo |
| Andrew-Tsegaye | 1 | ReActAgent.from_tools in a code-generation agent |
| denniszielke | 1 | ReActAgent in react-agent-li.py |
| NetEase-Media | 1 | OpenAIAgent.from_tools in a llamaindex AI agent client |
| victordibia | 1 | FunctionAgent hello-world sample |

---

## Construction-Form Breakdown

Across all 185 agents including run-llama (35 application + 150 run-llama examples):

| Form | Receiver/Class | Count | % |
|------|---------------|------:|--:|
| `FunctionAgent(...)` constructor | FunctionAgent | 162 | 87.6% |
| `X.from_tools(...)` classmethod | ReActAgent | 18 | 9.7% |
| `X.from_tools(...)` classmethod | OpenAIAgent | 5 | 2.7% |
| `X.from_tools(...)` classmethod | **FunctionCallingAgent** | **0** | **0%** |

The FunctionAgent constructor dominates at 88%, confirming the design doc's survey
finding that the v2 workflow API is the current construction pattern. from_tools survives
in older examples and tutorial code.

**FunctionCallingAgent appeared 0 times across the full scan** (including run-llama's
own example corpus). Per §8.2 it is kept in `_FROM_TOOLS_CLASSES` at zero marginal cost;
if prevalence remains zero through the next two framework scans, consider dropping it in
a batched cleanup.

---

## Findings

### IG001 (Confused Deputy)

**0 findings** across all 26 application repos.

Expected: LlamaIndex tool classes (`QueryEngineTool`, `FunctionTool`) are classified
NEUTRAL in the current taxonomy. Without a SOURCE or SINK taxonomy entry, no IG001
trigger is possible regardless of tool combination. This is a taxonomy gap, not a
false negative.

### IG002 (Dynamic System Prompt)

**4 application-repo findings** (all szczyglis-dev/py-gpt). An additional 5 findings
in run-llama example notebooks are excluded from application totals (pedagogical).

**szczyglis-dev/py-gpt (4 IG002) — production code:**
All four agents receive `system_prompt=` via runtime-injected prompt strings, consistent
with a user-configurable desktop AI app. Detections are sound; pending labeling, not
verified as exploitable.

```
provider/agents/llama_index/workflow/planner.py:177   — PlannerExecutor, taint: `prompt`
provider/agents/llama_index/workflow/supervisor.py:333 — Supervisor, taint: `prompt`
provider/agents/llama_index/workflow/supervisor.py:339 — Worker, taint: `prompt`
provider/agents/llama_index/workflow/openai.py:180    — OpenAIWorkflowAgent, taint: `prompt`
```

---

## Collisions

**0 agent_location_collisions.** No file triggered both LlamaIndexParser and another
parser at the same (file, line, col).

---

## Known Gaps

**`from_llm()` classmethod (1 occurrence — blairhudson):** `OpenAIAgent.from_llm()` is
a different factory from `from_tools()` and is not in the receiver set. 1 real miss in
the corpus. Defer to a batched small-additions PR unless prevalence rises.

**`chat_history=` without `system_prompt=` (§5.2 v1 gap):** Agent constructed with
`chat_history=` instead of `system_prompt=` emits `system_prompt_is_dynamic=False,
location=None`. Local-variable tracking deferred to a follow-on PR.

**`Workflow` subclass paradigm (§8.1):** Custom classes subclassing
`llama_index.core.workflow.Workflow` are not detected. TuanaCelik is the only corpus
instance; prevalence too low to prioritize.

---

## Zero-Agent Remainder (16 application repos)

| Repo | Reason |
|------|--------|
| AgentOps-AI | RAG/observability use (`VectorStoreIndex`, `Settings`); no agent constructor |
| blairhudson | Uses `OpenAIAgent.from_llm()` — real miss; `from_llm` not in receiver set |
| comet-ml | Observability tracing wrapper; no agent construction |
| Decade-qiu | RAG (`llama-index==0.14.9` in requirements); no agent constructor in source |
| HeadyZhang | Meta-tool inspecting llama_index import strings; llama_index is a string, not an import |
| henrii1 | `RouterQueryEngine` pattern; no agent constructor |
| LianjiaTech | RAG vector store backend (bella-rag); no agent constructor |
| microsoft | AutoGen repo; llama_index only in docs/requirements — no Python import |
| MODSetter | Requirements-only reference; no Python source that imports llama_index |
| OpenBMB | RAG chat engine (`FunctionCallingLLM`, `ChatPromptTemplate`); no agent constructor |
| RyjoxTechnologies | Requirements-only reference; no Python source import |
| SageMindAI | AutoGen repo listing `llama_index==0.9.8` (v0) as dep; no llama_index agent usage |
| snekkenull | LLM client use (Groq via llama_index); not agent framework |
| sulaiman-shamasna | RAG chatbot (`SimpleDirectoryReader`); no agent constructor |
| TuanaCelik | Custom `Workflow` subclass (§8.1 gap); uses `llama_index.core.workflow`, not agent constructors |
| velocitybolt | `SimpleWebPageReader` for data extraction; no agent constructor |
| vstorm-co | Requirements-only reference; no Python source import |
