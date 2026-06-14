# IG002 Labeling Results — agentic-guard v0.2

**Eval branch:** eval-corpus  
**Main engine SHA frozen for eval:** 031e781  
**Labeling date:** 2026-06-13  
**Methodology:** docs/eval/LABELING_METHODOLOGY.md  
**Population profile:** eval/ig002_population_profile.md  
**Sample dossier:** eval/ig002_sample.md  
**Single labeler:** Sanjay Belaturu Krishnegowda  

---

## Summary

| Metric | Value |
|--------|-------|
| Population | 148 IG002 findings across 32 repos |
| Sample (stratified, seed 42, per-repo cap 5) | 45 findings |
| TP (confirmed injection risk) | 4 |
| FP (false positive) | 38 |
| AMBIGUOUS (origin undeterminable) | 3 |
| **Sample precision (TP / labelable)** | **4/42 ≈ 9.5%** |
| **Population-weighted precision estimate** | **≈ 8.1%** |

> **Result framing (verbatim):** "IG002 raw sample precision is low (~10%, 4/42 labelable). FPs are not
> random: they decompose into (1) unresolved static bindings (largest, fixable — KL-004),
> (2) author-controlled parameterization points (fundamental static-analysis limit without
> deployment context), (3) the KL-003 dedent defect, and (4) demo-data-conditional cases.
> IG001 precision (4/5) vs IG002 (~1/10) is reported honestly; the asymmetry reflects that
> IG002 currently flags a structural form (dynamic prompt) without resolving whether the
> content is genuinely influenceable. Single labeler, n=45 stratified sample."

---

## Population-Weighted Precision Estimate

The sample was stratified; raw 4/42 ≠ population precision. Each stratum is weighted by
its share of the 148-finding population.

### Per-stratum results (AMBIGUOUS excluded from precision denominator)

| Stratum | Population N | Sample drawn | Sample TP | Sample AMB | Sample FP | Stratum precision |
|---------|-------------|--------------|-----------|------------|-----------|-------------------|
| Callable/opaque | 29 | 8 | 0 | 0 | 8 | 0/8 = 0.000 |
| F-string | 30 | 12 | 3 | 1 | 8 | 3/11 = 0.2727 |
| Plain variable | 89 | 25 | 1 | 2 | 22 | 1/23 = 0.0435 |
| **Total** | **148** | **45** | **4** | **3** | **38** | — |

### Weighted estimate arithmetic

```
P_weighted = Σ (N_stratum / N_total) × (TP_sample / (TP_sample + FP_sample))

= (29/148) × (0/8)
+ (30/148) × (3/11)
+ (89/148) × (1/23)

= 0
+ (30 × 3) / (148 × 11)
+ (89 × 1) / (148 × 23)

= 0 + 90/1628 + 89/3404

= 45/814 + 89/3404        [reducing 90/1628 by GCD 2]

Common denominator = LCM(814, 3404) = 37444
  45/814  = 2070/37444
  89/3404 =  979/37444

= 3049/37444 ≈ 0.0814 ≈ 8.1%
```

**Reported estimate: ~8% (range consistent with 5–15% given n=45, single labeler).**

**Caveats:**
- Stratified sample, n=45 of 148. Confidence intervals at this scale are wide.
- Single labeler — no inter-rater agreement computed.
- AMBIGUOUS findings (F16, F32, F44) excluded from precision denominator; if all are TP, estimate rises to ~13%; if all are FP, estimate stays ~8%.
- Report these as raw counts with an explicit estimate, not a precise rate.

---

## FP Decomposition

38 FPs break into four classes:

### Class 1 — Unresolved static bindings (18 FPs)

Module-level constants, SDK constants, cross-module imported prompts, dict-of-literals,
`.format()` with literal-only args, ternaries selecting between module constants, loop
variables over literal lists, and callables that compose only static string arguments —
all flagged IG002 because the engine cannot resolve the binding to a literal at
construction time.

**Addressable:** extending PR#5 literal-binding resolution across module boundaries,
through dict/.format/ternary selection, and to callable returns that compose only literals
(see KL-004).

Sub-classes:
- **KL-002 callable static composition** (F01–F05, 5 findings): `build_prompt()` takes only
  literal string args and returns `str`; engine flags the call as dynamic.
- **KL-004 cross-module/SDK constant** (F09, F11, F12, F19, F20, F24, F25, F27, F30, F34,
  F38, F40, F41 — 13 findings): prompt values are module-level string constants or SDK
  constants that the engine cannot resolve across import boundaries.

### Class 2 — Author-controlled parameterization (14 FPs)

System prompt is a function/constructor parameter whose value is set by the
application author, not by external users. Includes: Decepticon library extension points
(all in-codebase callers use no-arg form), factory params with static defaults, agent-
authoring tools where the user IS the author (CrewAI Studio, CrewAI-GUI-Qt), eval
harness config, and workflow/workspace file content provided by the application developer.

Not directly fixable by literal-binding improvement — requires deployment-context
information about who controls the parameter at call time.

Findings: F13, F22, F23, F26, F28, F29, F31, F33, F35, F36, F37, F42, F43, F45 (14)

### Class 3 — KL-003 dedent defect (3 FPs)

`dedent(f"literal")` or `dedent("""literal""")` flagged as dynamic because the engine
treats the callable name `dedent` as an interpolated taint variable. The f-string (or
plain string) passed to `dedent` contains zero `{var}` interpolations. See KL-003.

Findings: F15, F18, F39 (3)

### Class 4 — Demo-data-conditional (3 FPs)

The `make_prompt()` closure in `langgraph-swarm` is genuinely dynamic (embeds
`RESERVATIONS[user_id]` and `datetime.now()` per invocation), but the underlying data
(`FLIGHTS`, `HOTELS`, `RESERVATIONS`) is hardcoded toy data. TP under a real-data
deployment; FP in the demo codebase.

Findings: F06, F07, F08 (3)

---

## Known Limitations Logged

### KL-002 — Callable instructions composing static strings flagged IG002

**Triggered by:** F01–F05 (`study8677/OpenCMO`, `build_prompt()`)  
**Count in sample:** 5/8 callable-stratum findings  
**Description:** A helper callable that accepts only literal string arguments and returns
`str` by concatenating module-level constants is flagged IG002 as dynamic. The engine
cannot determine that the callable's return value is statically composed.  
**Candidate fix:** Recognize helper callables that return statically-composed strings (e.g.,
via return-type annotation + function body analysis). Analyzer frozen for eval.

### KL-003 — `dedent(f"literal")` flagged as dynamic via taint-name misidentification

**Triggered by:** F15, F18 (f-string stratum); F39 (variable stratum)  
**Count in sample:** 3  
**Description:** Taint extraction flags `dedent(f'literal')` or `dedent("""literal""")` as
dynamic by treating the `dedent` callable name as an interpolated variable, even when the
f-string or plain string passed to `dedent` has zero `{var}` interpolations.  
**Candidate fix:** A `dedent`-wrapped f-string with no `{var}` interpolations is static;
filter callable names from taint extraction. Analyzer frozen for eval.

### KL-004 — Module-level / cross-module / imported constant prompts flagged IG002

**Triggered by:** F09, F11, F12, F19, F20, F24, F25, F27, F30, F34, F38, F40, F41 (13 findings)  
**Description:** Prompt values defined as module-level string constants, imported SDK
constants (`RECOMMENDED_PROMPT_PREFIX`), dict-of-literal selections, `.format()` with
literal-only substitutions, and ternaries selecting between module constants are all
flagged IG002 because the binding resolver (PR#5 scope: function-local literals) does not
extend to cross-module imports, dict subscript accesses, `.format()` calls, or ternary
expressions.  
**Largest IG002 FP class (13/38 FPs, plus 5 KL-002 cases for 18 total in the
"unresolved static" umbrella).**  
**Candidate fix:** Extend PR#5 literal-binding resolution: (a) resolve `from mod import X`
to module-level assignments, (b) resolve `dict["key"]` when dict is a literal, (c) resolve
`.format(k=literal, ...)` when all args are literals, (d) resolve ternaries where both
branches are literals. Analyzer frozen for eval.

---

## AMBIGUOUS Findings (3)

| ID | Repo | Reason |
|----|------|--------|
| F16 | `hellotinah/financial_agent` · `voice_chat.py:33` | `financial_report.txt` is read at module load; content is external file data, but whether the file is operator-authored or written from external data is not statically determinable — AMBIGUOUS on origin-undeterminable grounds |
| F32 | `Cognitive-Stack/bull-vision-agent` · `app/bot/agent.py:163` | `portfolio_context`/`profile_context` from per-user DB records; whether user-supplied values can contain injection strings depends on unseen `setup_portfolio`/`setup_profile` handlers |
| F44 | `pipeshub-ai/pipeshub-ai` · `sub_agent.py:508` | `task_desc` = orchestrator LLM output derived from user query placed into sub-agent system prompt — indirect injection pathway exists but LLM mediation makes taint chain non-trivially traceable |

---

## Complete Finding Labels

### Stratum 1: Callable/Opaque (F01–F08)

| ID | Repo | File:line | Construction form | Label | One-line reason |
|----|------|-----------|-------------------|-------|-----------------|
| F01 | `study8677/OpenCMO` | `agents/prompt_contracts.py:~call` | callable | FP-static | `build_prompt()` accepts only literal string args and returns `str` composed of module-level constants; KL-002 |
| F02 | `study8677/OpenCMO` | `agents/prompt_contracts.py:~call` | callable | FP-static | Same `build_prompt()` pattern; different agent call site; KL-002 |
| F03 | `study8677/OpenCMO` | `agents/prompt_contracts.py:~call` | callable | FP-static | Same `build_prompt()` pattern; KL-002 |
| F04 | `study8677/OpenCMO` | `agents/prompt_contracts.py:~call` | callable | FP-static | Same `build_prompt()` pattern; KL-002 |
| F05 | `study8677/OpenCMO` | `agents/prompt_contracts.py:~call` | callable | FP-static | Same `build_prompt()` pattern; KL-002 |
| F06 | `langchain-ai/langgraph-swarm-py` | `examples/customer_support/…/customer_support.py` | callable | FP (demo-data-conditional) | `make_prompt()` is genuinely dynamic (RESERVATIONS + datetime.now()); FP because FLIGHTS/HOTELS/RESERVATIONS are hardcoded toy data |
| F07 | `langchain-ai/langgraph-swarm-py` | `examples/customer_support/…/customer_support.py` | callable | FP (demo-data-conditional) | Same `make_prompt()` closure; second agent; demo-data FP |
| F08 | `langchain-ai/langgraph-swarm-py` | `examples/customer_support/…/customer_support.py` | callable | FP (demo-data-conditional) | Same `make_prompt()` closure; third agent; demo-data FP |

**Stratum 1 note:** F06–F08 are demo-data-conditional FPs. `make_prompt` would be TP under a real-data deployment (RESERVATIONS drawn from live user bookings). Recorded per batch-1 review.

### Stratum 2: F-string (F09–F20)

| ID | Repo | File:line | Construction form | Label | One-line reason |
|----|------|-----------|-------------------|-------|-----------------|
| F09 | `serialx/vibecore` | `examples/customer_service.py:87` | f-string | FP-static | `RECOMMENDED_PROMPT_PREFIX` is an OpenAI Agents SDK string constant; KL-004 |
| F10 | `liangdabiao/crewai_stock_analysis_system` | `src/crews/data_collection_crew.py:207` | f-string | **TP** | `company` flows from HTTP form input / CLI user input directly into agent `goal` field |
| F11 | `serialx/vibecore` | `examples/customer_service.py:100` | f-string | FP-static | Same `RECOMMENDED_PROMPT_PREFIX` SDK constant as F09; KL-004 |
| F12 | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` | `Chapter6/handoff_prompt.py:9` | f-string | FP-static | Same SDK constant; textbook chapter demo; KL-004 |
| F13 | `jkmaina/openai-agents-blueprint` | `chapter4/03_content_moderation_minimal.py:55` | f-string | FP-author-controlled | `level: ModerationLevel` enum; all call sites pass hardcoded enum members; ternary produces one of two fixed literals |
| F14 | `AbubakrChan/crewai-UI-business-product-launch` | `main.py:27` | f-string | **TP** | `product_name = st.text_input(…)` — direct Streamlit end-user input flows into system prompt without sanitization |
| F15 | `alexfazio/viral-clips-crew` | `crew.py` (first dedent agent) | f-string | FP-static | `dedent` is `textwrap.dedent`; engine misidentifies callable name as taint variable; f-string has zero interpolations; KL-003 |
| F16 | `hellotinah/financial_agent` | `financial_research_agent/voice_chat.py:33` | f-string | **AMBIGUOUS** | `financial_report_content = file.read()` — real file read flows into prompt; whether file is operator-authored or externally written is not statically determinable; AMBIGUOUS on origin-undeterminable grounds |
| F17 | `liangdabiao/crewai_stock_analysis_system` | `src/crews/data_collection_crew.py:229` | f-string | **TP** | Same `company` taint as F10; second agent in same function; user-supplied via web form or CLI |
| F18 | `alexfazio/viral-clips-crew` | `crew.py` (second dedent agent) | f-string | FP-static | Same KL-003 dedent defect as F15 |
| F19 | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` | `Chapter6/handoff_prompt.py:13` | f-string | FP-static | Same SDK constant as F12; second agent in same file; KL-004 |
| F20 | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` | `Chapter6/swarm.py:13` | f-string | FP-static | `role` iterates over a hardcoded 10-element string list; all values are fixed literals; KL-004 |

### Stratum 3: Plain Variable (F21–F45)

| ID | Repo | File:line | Construction form | Label | One-line reason |
|----|------|-----------|-------------------|-------|-----------------|
| F21 | `xark-argo/argo` | `backend/core/agent/tool_agent_runner.py:65` | plain variable | **TP** | `self.instruction` originates from a prompt template string filled with user-supplied `inputs` dict via `_fill_in_inputs_from_external_data_tools`; caller-controlled strings reach the system prompt |
| F22 | `PurpleAILAB/Decepticon` | `agents/standard/contract_auditor.py:155` | plain variable | FP-author-controlled | `system_prompt: str|None=None`; all in-codebase callers use no-arg form → `load_prompt(_ROLE)` with hardcoded role; library extension point, no external-user-data path in codebase |
| F23 | `LangGraph-GUI/CrewAI-GUI-Qt` | `src/WorkFlow.py:55` | plain variable | FP-author-controlled | `node.role` from GUI-authored workflow JSON; no author/attacker separation — the workflow author defines and runs the agents |
| F24 | `Shaurya-Sethi/circuitron` | `circuitron/agents.py:194` | plain variable | FP-static | `CODE_VALIDATION_PROMPT` is an imported module-level constant composed of SDK constant + literal text; KL-004 |
| F25 | `jkmaina/openai-agents-blueprint` | `chapter2/19_token_optimization.py:78` | plain variable | FP-static | `config["instructions"]` selects from a dict literal with three hardcoded string values; all possible values are static; KL-004 |
| F26 | `szczyglis-dev/py-gpt` | `provider/agents/llama_index/workflow/supervisor.py:339` | plain variable | FP-author-controlled | `prompt_worker` defaults to `WORKER_PROMPT` (module constant); any override is internal application code, not external user input |
| F27 | `Nishmithasshett/LLM-Agent` | `agent.py:94` | plain variable | FP-static | `AGENT_PROMPT` is a module-level string literal; `PromptTemplate.from_template` introduces no dynamic content; KL-004 |
| F28 | `evalops/agent-harness` | `agent_harness.py:602` | plain variable | FP-author-controlled | `HarnessConfig.system_prompt` defaults to literal `"You are a helpful assistant."`; override is by eval operator configuration, not external users |
| F29 | `bytedance/deer-flow` | `deerflow/agents/factory.py:143` | plain variable | FP-author-controlled | `system_prompt` factory parameter defaults to None; only test code supplies non-None (literal) values; no external user data path in production |
| F30 | `langchain-ai/langgraph-swarm-py` | `examples/research/src/agent/agent.ipynb:14` | plain variable | FP-static | `researcher_prompt` is a module-level string literal in `prompts.py`; example notebook; KL-004 |
| F31 | `PurpleAILAB/Decepticon` | `agents/standard/ad_operator.py:155` | plain variable | FP-author-controlled | Identical to F22 — Decepticon library pattern; all in-codebase callers use no-arg form |
| F32 | `Cognitive-Stack/bull-vision-agent` | `app/bot/agent.py:163` | plain variable | AMBIGUOUS | `get_prompt()` formats `BULL_VISION_PROMPT` with `portfolio_context`/`profile_context` from per-user DB records; whether user-supplied profile/portfolio values can contain injection strings depends on unseen setup handlers |
| F33 | `strnad/CrewAI-Studio` | `app/my_agent.py:58` | plain variable | FP-author-controlled | `self.role` entered via CrewAI Studio authoring UI (`st.text_input`); person entering the role is the agent author who also deploys and runs the agent |
| F34 | `AgentOps-AI/agentops` | `examples/openai_agents/customer_service_agent.ipynb:51` | f-string (misclassified as variable) | FP-static | `RECOMMENDED_PROMPT_PREFIX` is SDK constant; f-string misclassified to variable stratum — same pattern as F09/F11/F12/F19; example notebook; KL-004 |
| F35 | `langchain-ai/deepagents` | `langchain_quickjs/_swarm_task.py:304` | plain variable | FP-author-controlled | `SwarmSubAgent.system_prompt` is a required configuration field supplied by library users at agent specification time; not from runtime external input |
| F36 | `PurpleAILAB/Decepticon` | `agents/standard/reverser.py:149` | plain variable | FP-author-controlled | Identical to F22/F31 — Decepticon library pattern |
| F37 | `PurpleAILAB/Decepticon` | `agents/standard/cloud_hunter.py:140` | plain variable | FP-author-controlled | Identical to F22/F31/F36 — Decepticon library pattern |
| F38 | `jkmaina/openai-agents-blueprint` | `chapter1/14_production_example.py:140` | plain variable | FP-static | `instructions: str` constructor parameter; all call sites in this textbook example use literal string instructions; KL-004 |
| F39 | `alejandro-ao/crewai-crash-course` | `src/agents.py:35` | plain variable | FP-static | `backstory=dedent("""literal""")` — plain string (not even f-string); same KL-003 defect as F15/F18; `dedent` misidentified as taint variable |
| F40 | `langchain-ai/langgraph-swarm-py` | `examples/research/src/agent/agent.py:29` | plain variable | FP-static | `PLANNER_PROMPT_FORMATTED = planner_prompt.format(llms_txt=LLMS_TXT, num_urls=NUM_URLS)` — both substituted values are module-level literal constants; KL-004 |
| F41 | `Shaurya-Sethi/circuitron` | `circuitron/agents.py:176` | plain variable | FP-static | `prompt` is one of two imported module-level string constants selected by a boolean config flag; all possible values are static; KL-004 |
| F42 | `bytedance/deer-flow` | `deerflow/agents/lead_agent/agent.py:501` | plain variable | FP-author-controlled | `apply_prompt_template()` composes system prompt from application configuration flags and module-level constants; no external user data flows into the formatted string |
| F43 | `kid0317/crewai_mas_demo` | `m5l30/demo.py:107` | plain variable | FP-author-controlled | `build_bootstrap_prompt(WORKSPACE_DIR)` reads author-provided workspace markdown files from a project-relative directory; configuration, not external input; example dir |
| F44 | `pipeshub-ai/pipeshub-ai` | `backend/python/app/modules/agents/deep/sub_agent.py:508` | plain variable | AMBIGUOUS | `task_desc` = orchestrator LLM output derived from user query embedded in sub-agent system prompt — indirect injection pathway exists; LLM mediation makes taint chain non-trivially traceable statically |
| F45 | `PurpleAILAB/Decepticon` | `agents/standard/wireless_operator.py:115` | plain variable | FP-author-controlled | Identical to F22/F31/F36/F37 — Decepticon library pattern; fifth Decepticon agent in sample |

---

## Appendix: Sampling Parameters

| Parameter | Value |
|-----------|-------|
| Random seed | 42 |
| Per-repo cap | 5 |
| Population | 148 IG002 findings, main engine 031e781 |
| Callable/opaque stratum | 8 drawn / 29 population |
| F-string stratum | 12 drawn / 30 population |
| Plain variable stratum | 25 drawn / 89 population |
