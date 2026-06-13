# IG002 population profile

**Purpose:** characterize all 148 IG002 findings before any sampling or labeling.
All counts derive directly from the full-corpus scan (main engine at `031e781`,
126-repo corpus at pinned SHAs). No TP/FP calls are made here.

**Scan configuration:**
- Engine: `031e781` (main, "Taxonomy matcher fix + corpus-derived tool classifications")
- Corpus: 126 repos, all cloned at SHA-pinned commits (see `eval/corpus.json`)
- Test files excluded (engine skips `tests/`, `test_*.py`, `*_test.py`, `conftest.py`)
- Scan errors: 0 / 126 repos

---

## 1. Per-repo distribution

32 of 126 repos produced ≥1 IG002 finding. The distribution is heavily concentrated.

| Findings | % of 148 | Repo | Flag |
|---:|---:|---|---|
| 26 | 17.6 | study8677/OpenCMO | **>10%** |
| 20 | 13.5 | PurpleAILAB/Decepticon | **>10%** |
| 11 | 7.4 | Shaurya-Sethi/circuitron | |
| 10 | 6.8 | kid0317/crewai_mas_demo | |
| 8 | 5.4 | langchain-ai/langgraph-swarm-py | |
| 6 | 4.1 | AgentOps-AI/agentops | |
| 5 | 3.4 | MODSetter/SurfSense | |
| 5 | 3.4 | serialx/vibecore | |
| 5 | 3.4 | jkmaina/openai-agents-blueprint | |
| 5 | 3.4 | liangdabiao/crewai_stock_analysis_system | |
| 4 | 2.7 | bytedance/deer-flow | |
| 4 | 2.7 | langchain-ai/deepagents | |
| 4 | 2.7 | pipeshub-ai/pipeshub-ai | |
| 4 | 2.7 | PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK | |
| 4 | 2.7 | alejandro-ao/crewai-crash-course | |
| 4 | 2.7 | szczyglis-dev/py-gpt | |
| 3 | 2.0 | alexfazio/viral-clips-crew | |
| 3 | 2.0 | AbubakrChan/crewai-UI-business-product-launch | |
| 2 | 1.4 | openai/openai-cs-agents-demo | |
| 2 | 1.4 | OctagonAI/octagon-vc-agents | |
| 2 | 1.4 | Cognitive-Stack/bull-vision-agent | |
| 1 | 0.7 | JoshuaC215/agent-service-toolkit | |
| 1 | 0.7 | starpig1129/DATAGEN | |
| 1 | 0.7 | xark-argo/argo | |
| 1 | 0.7 | hellotinah/financial_agent | |
| 1 | 0.7 | khaoss85/AI-Team-Orchestrator | |
| 1 | 0.7 | temporal-community/openai-agents-sdk-deep-research-demo | |
| 1 | 0.7 | evalops/agent-harness | |
| 1 | 0.7 | strnad/CrewAI-Studio | |
| 1 | 0.7 | LangGraph-GUI/CrewAI-GUI-Qt | |
| 1 | 0.7 | bhancockio/nextjs-crewai-basic-tutorial | |
| 1 | 0.7 | Nishmithasshett/LLM-Agent | |

**Concentration:** the top 2 repos (OpenCMO + Decepticon) account for 46/148 = 31.1%.
The top 4 repos account for 67/148 = 45.3%. The remaining 28 repos contribute 81 findings
averaging 2.9 per repo.

**Architectural basis for top repos:**

- **OpenCMO (26):** one agent file per social/publishing platform (blog.py, twitter.py,
  linkedin.py, …). Each file defines one agent using the same `instructions=build_prompt(...)`
  call pattern. 26 distinct files, 1 finding per file — this is one architectural decision
  firing 26 times, not 26 independent scenarios.

- **Decepticon (20):** a large multi-agent security-testing system. Each agent file
  (`detector.py`, `scanner.py`, `analyst.py`, …) follows `instructions=system_prompt` where
  `system_prompt` is passed as a function parameter. 20 distinct files, 1 finding per file —
  again one architecture, 20 instances.

---

## 2. Per-framework distribution

Based on the `framework_tag` field assigned during corpus collection.

| Framework | Findings | % of 148 |
|---|---:|---:|
| openai-agents | 65 | 43.9 |
| langgraph | 54 | 36.5 |
| crewai | 28 | 18.9 |
| langchain-agents | 1 | 0.7 |
| llama-index | 0 | 0 |

**Note:** llama-index tagged repos produced zero IG002 findings. This is expected:
the LlamaIndex parser uses the `system_prompt=` kwarg and the parser recognizes it,
but the llama-index repos in the corpus do not appear to use dynamic system prompts
in the scanned files.

---

## 3. Duplication and clustering

**Exact duplicates:** 0. All 148 findings have unique (repo, file, line) tuples.

**Within-repo clustering (same file + same taint-name pattern, N > 1):**

| N | Repo/file | Taint pattern |
|---|---|---|
| 10 | Shaurya-Sethi/circuitron / agents.py | varies (PLAN_PROMPT, DOC_AGENT_PROMPT, …) |
| 5 | liangdabiao/crewai_stock_analysis_system / data_collection_crew.py | company |
| 4 | alejandro-ao/crewai-crash-course / agents.py | dedent |
| 3 | pipeshub-ai/pipeshub-ai / sub_agent.py | system_prompt |
| 3 | AgentOps-AI/agentops / customer_service_agent.ipynb | RECOMMENDED_PROMPT_PREFIX |
| 3 | AgentOps-AI/agentops / customer_service_agent.py | RECOMMENDED_PROMPT_PREFIX |
| 3 | PacktPublishing / handoff_prompt.py | RECOMMENDED_PROMPT_PREFIX |
| 3 | serialx/vibecore / customer_service.py | RECOMMENDED_PROMPT_PREFIX |
| 3 | alexfazio/viral-clips-crew / crew.py | dedent |
| 3 | AbubakrChan/crewai-UI-business-product-launch / main.py | product_name |
| 3 | kid0317/crewai_mas_demo / demo.py | backstory |
| 2 | langchain-ai/langgraph-swarm-py / customer_support.ipynb | (callable, no taints) |
| … | (3 more pairs) | … |

- **Findings in clusters:** 44
- **Repetition-findings (beyond first per cluster):** 29
- **Effectively distinct patterns:** 119 (148 − 29)

**Cross-repo identical patterns:** 0. No two repos share the same (filename, taint-name)
combination exactly — copy-paste spread is not a factor in this corpus.

---

## 4. Construction-form breakdown

Classification uses taint-source presence as the primary discriminator (the engine extracts
taint variable names when it can; when it cannot, the prompt-expression is opaque to it).
Source-file inspection confirms the form for a sample.

| Form | N | % | Description |
|---|---:|---:|---|
| plain variable | 90 | 60.8 | `instructions=VARNAME` — a bare name; engine extracted the variable name(s) from the taint list |
| f-string | 29 | 19.6 | `instructions=f"… {var} …"` — f-string in source window; engine extracted interpolated names |
| callable/opaque | 29 | 19.6 | `instructions=fn(...)` — a call expression; engine could not extract taint names (message: "rather than being a string constant") |
| str.format() | 0 | 0 | Not present in corpus |
| concatenation | 0 | 0 | Not confirmed (may be hidden inside the variable bucket) |

**Notable callable sub-patterns:**
- `instructions=build_prompt(base_instructions="""literal""", ...)` — OpenCMO pattern (24/29
  callable findings). The callable takes only string-literal arguments; the output is
  likely a static string. This is a strong FP signal for those 24 findings.
- `system_prompt=make_prompt("literal string")` — langgraph-swarm-py (4/29). Same pattern:
  callable with literal arguments.
- `system_prompt=None` — deer-flow (1/29). None is not attacker-controlled; this is a
  near-certain FP.

---

## 5. Obvious FP scan (light — no labels)

The engine already suppresses test files (test dirs, `test_*.py`, `*_test.py`, `conftest.py`).
The following are pre-labeling heuristic signals only — they calibrate expectations, not labels.

**Signal: example/tutorial directory** (32 findings, 21.6%)

| N | Repo | Directory evidence |
|---|---|---|
| 10 | kid0317/crewai_mas_demo | `m4l23/` tutorial module path |
| 8 | langchain-ai/langgraph-swarm-py | `src/agent/` (example notebooks) |
| 6 | AgentOps-AI/agentops | `examples/openai_agents/` |
| 3 | serialx/vibecore | `vibecore/examples/` |
| 2 | openai/openai-cs-agents-demo | repo name contains "demo" |
| 1 | jkmaina/openai-agents-blueprint | `chapter1/14_production_example.py` |
| 1 | temporal-community/openai-agents-sdk-deep-research-demo | repo name "demo" |
| 1 | bhancockio/nextjs-crewai-basic-tutorial | repo name "tutorial" |

**Signal: callable-with-literal-args** (24 findings, 16.2%)
`instructions=build_prompt(base_instructions="...", ...)` in OpenCMO. If `build_prompt()`
wraps its string argument without external input, these are FPs by IG002 criterion (a).

**Signal: system_prompt=None** (1 finding, 0.7%)
deer-flow line 340. `None` is not a runtime-constructed string; the finding should not fire.

**Rough calibration (not a count, not a label):** between the example-dir and
callable-literal signals, at least 57 findings (~38%) carry a pre-labeling FP indicator.
This is a calibration ceiling, not a precision estimate — overlap is possible and labeling
may reclassify findings in either direction.

---

## Summary for sampling design

Key facts this profile establishes before sampling:

1. **Concentration is real:** two repos (OpenCMO, Decepticon) contribute 31% of all findings
   from one architectural pattern each. A uniform random sample overweights them.

2. **Framework skew:** openai-agents (44%) and langgraph (36%) dominate; crewai (19%) is
   minority; llama-index contributes 0. A stratified sample must include crewai to avoid
   losing an entire framework.

3. **Construction form matters:** callable/opaque (29) and plain variable (90) have different
   FP risk profiles. The callable-with-literal-args subset (24) is a strong FP signal.

4. **Repetitions are real but modest:** 29 findings are within-repo repetitions of the same
   pattern. Sampling by distinct pattern (119) rather than raw finding count reduces noise.

5. **Example/tutorial code is a stratum:** 32 findings (22%) are in example/tutorial
   directories — expected higher FP rate. These should be a labeled stratum, not excluded.
