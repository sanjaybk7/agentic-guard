# IG001 Recall Audit — Blind Materials

**Purpose:** Human auditors identify confused-deputy risk from agent+tool definitions,
without reference to scanner output.

**Instructions for auditors:**
1. For each agent, read the tool list and behavioral descriptions.
2. Mark any agent you believe poses confused-deputy risk: it accepts untrusted external
   input via one tool and takes a privileged action via another, with no human gate.
3. Record your reasoning. Do NOT refer to scanner results.

**Selection:** 12 repos, stratified by framework, seed=42.
Allocations: langgraph=3, openai-agents=4, crewai=4, llama-index=1.

**Coverage note (extraction, not scanner output):**
- 8 of 12 repos yielded agents with resolvable tool lists.
- 60 of 211 detected agent definitions have tool lists.
- Agents omitted: either no `tools=[...]` argument at call site, or tools imported from
  an unresolved package (e.g., SDK-built WebSearchTool, activity_as_tool wrappers).
- Repos with 0 auditable agents: the gap is a parser coverage limit, not evidence of safety.

---

## Repo 01: `langchain-ai/langgraph-swarm-py`

- **Framework:** langgraph
- **Pinned SHA:** `de22626e30844858b5eec1bb6d5a14008db8b773`
- **Agent definitions found:** 4 total; 4 with tool lists; 4 shown

### Agent 01.1: `flight_assistant`

- **Definition:** `examples/customer_support/src/agent/customer_support.py:113`
- **Human gate:** none detected

**Tools (3):**

- **`search_flights`** — Search flights.
- **`book_flight`** — Book a flight.
- **`transfer_to_hotel_assistant`** — (no description found)

### Agent 01.2: `hotel_assistant`

- **Definition:** `examples/customer_support/src/agent/customer_support.py:120`
- **Human gate:** none detected

**Tools (3):**

- **`search_hotels`** — Search hotels.
- **`book_hotel`** — Book a hotel.
- **`transfer_to_flight_assistant`** — (no description found)

### Agent 01.3: `planner_agent`

- **Definition:** `examples/research/src/agent/agent.py:27`
- **Human gate:** none detected

**Tools (2):**

- **`fetch_doc`** — Fetch a document from a URL and return the markdownified text.
- **`transfer_to_researcher_agent`** — (no description found)

### Agent 01.4: `researcher_agent`

- **Definition:** `examples/research/src/agent/agent.py:35`
- **Human gate:** none detected

**Tools (2):**

- **`fetch_doc`** — Fetch a document from a URL and return the markdownified text.
- **`transfer_to_planner_agent`** — (no description found)

## Repo 02: `MODSetter/SurfSense`

- **Framework:** langgraph
- **Pinned SHA:** `61adc80615bbfc853c3c5116386fe4f47685f07a`
- **Agent definitions found:** 7 total; 1 with tool lists; 1 shown
  _(Note: 6 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 02.1: `create_agent`

- **Definition:** `surfsense_backend/app/app.py:534`
- **Human gate:** `checkpointer=<set>`

**Tools (2):**

- **`_warmup_tool_a`** — Warmup tool A — never actually invoked.
- **`_warmup_tool_b`** — Warmup tool B — never actually invoked.

## Repo 03: `JoshuaC215/agent-service-toolkit`

- **Framework:** langgraph
- **Pinned SHA:** `5b3945f48e41a193816d7710b275eb89b90568ee`
- **Agent definitions found:** 14 total; 3 with tool lists; 3 shown
  _(Note: 11 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 03.1: `sub-agent-math_expert`

- **Definition:** `src/agents/langgraph_supervisor_agent.py:33`
- **Human gate:** none detected

**Tools (2):**

- **`add`** — Add two numbers.
- **`multiply`** — Multiply two numbers.

### Agent 03.2: `sub-agent-research_expert`

- **Definition:** `src/agents/langgraph_supervisor_agent.py:40`
- **Human gate:** none detected

**Tools (1):**

- **`web_search`** — Search the web for information.

### Agent 03.3: `sub-agent-math_expert`

- **Definition:** `src/agents/langgraph_supervisor_hierarchy_agent.py:11`
- **Human gate:** none detected

**Tools (2):**

- **`add`** — Add two numbers.
- **`multiply`** — Multiply two numbers.

## Repo 04: `jkmaina/openai-agents-blueprint`

- **Framework:** openai-agents
- **Pinned SHA:** `76cbbcb41a938531a9b85375210ed328d9014606`
- **Agent definitions found:** 122 total; 31 with tool lists; 15 shown (capped at 15)
  _(Note: 91 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 04.1: `Enterprise Vision Analyst`

- **Definition:** `chapter8/advanced_multi-modal.py:282`
- **Human gate:** none detected

**Tools (3):**

- **`fetch_and_analyze_image`** — Fetch an online image and prepare it for analysis.
- **`validate_image_quality`** — Validate image quality and technical specifications.
- **`escalate_vision_analysis`** — Escalate vision analysis to human review when confidence is low.

### Agent 04.2: `Customer Service Assistant`

- **Definition:** `chapter8/observability.py:165`
- **Human gate:** none detected

**Tools (3):**

- **`get_weather`** — Get current weather information for a city.
- **`get_time`** — Get current time - quick internal operation
- **`calculate_tip`** — Calculate tip amount for a given bill - computational task

### Agent 04.3: `Enterprise Customer Service AI`

- **Definition:** `chapter8/custom_metrics.py:350`
- **Human gate:** none detected

**Tools (5):**

- **`get_weather`** — Get current weather information for a city.
- **`get_time`** — Get current time - quick internal operation
- **`calculate_tip`** — Calculate tip amount for a given bill - computational task
- **`search_knowledge_base`** — Search internal knowledge base - simulates complex retrieval
- **`escalate_to_human`** — Escalate complex issues to human agents

### Agent 04.4: `Agent`

- **Definition:** `chapter1/14_production_example.py:138`
- **Human gate:** none detected

**Tools (2):**

- **`get_user_info`** — Example tool that accesses user context.
- **`log_interaction`** — Log interaction for audit purposes.

### Agent 04.5: `MemoAssistant`

- **Definition:** `chapter1/12_advanced_context_memory.py:54`
- **Human gate:** none detected

**Tools (2):**

- **`remember_fact`** — Store a user-supplied fact in long-term memory.
- **`recall_facts`** — Return everything the assistant knows so far.

### Agent 04.6: `PersonalAssistant`

- **Definition:** `chapter1/11_context_memory.py:51`
- **Human gate:** none detected

**Tools (1):**

- **`get_user_preference`** — user = wrapper.context

### Agent 04.7: `Data Analyst`

- **Definition:** `chapter6/03_code_interpreter.py:17`
- **Human gate:** none detected

**Tools (1):**

- **`<CodeInterpreterTool(...)>`** — (no description found)

### Agent 04.8: `Math Tutor`

- **Definition:** `chapter6/03_code_interpreter.py:33`
- **Human gate:** none detected

**Tools (1):**

- **`<CodeInterpreterTool(...)>`** — (no description found)

### Agent 04.9: `Creative Assistant`

- **Definition:** `chapter6/05_image_generation.py:17`
- **Human gate:** none detected

**Tools (1):**

- **`<ImageGenerationTool(...)>`** — (no description found)

### Agent 04.10: `Marketing Designer`

- **Definition:** `chapter6/05_image_generation.py:34`
- **Human gate:** none detected

**Tools (1):**

- **`<ImageGenerationTool(...)>`** — (no description found)

### Agent 04.11: `Concept Artist`

- **Definition:** `chapter6/05_image_generation.py:51`
- **Human gate:** none detected

**Tools (1):**

- **`<ImageGenerationTool(...)>`** — (no description found)

### Agent 04.12: `Document Assistant`

- **Definition:** `chapter6/04_file_search.py:17`
- **Human gate:** none detected

**Tools (1):**

- **`<FileSearchTool(...)>`** — (no description found)

### Agent 04.13: `Legal Research Assistant`

- **Definition:** `chapter6/04_file_search.py:32`
- **Human gate:** none detected

**Tools (1):**

- **`<FileSearchTool(...)>`** — (no description found)

### Agent 04.14: `Policy Analyst`

- **Definition:** `chapter6/04_file_search.py:47`
- **Human gate:** none detected

**Tools (1):**

- **`<FileSearchTool(...)>`** — (no description found)

### Agent 04.15: `Content Analyst`

- **Definition:** `chapter6/06_async_tools.py:120`
- **Human gate:** none detected

**Tools (2):**

- **`fetch_random_post`** — Fetch a random post from JSONPlaceholder API.
- **`fetch_user_info`** — Fetch user information from JSONPlaceholder API.

## Repo 05: `hellotinah/financial_agent`

- **Framework:** openai-agents
- **Pinned SHA:** `126c15ceb7644269610edd37d11f66daa5828122`
- **Agent definitions found:** 8 total; 0 with tool lists; 0 shown
  _(Note: 8 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 06: `temporal-community/openai-agents-demos`

- **Framework:** openai-agents
- **Pinned SHA:** `ee5f871b48cb26ec28239ef7a4719ab10c4903e8`
- **Agent definitions found:** 10 total; 4 with tool lists; 4 shown
  _(Note: 6 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 06.1: `Hello world`

- **Definition:** `openai_agents/workflows/tools_workflow.py:16`
- **Human gate:** none detected

**Tools (1):**

- **`<activity_as_tool(...)>`** — Wraps a Temporal workflow activity as a callable tool.

### Agent 06.2: `ImageGenAgent`

- **Definition:** `openai_agents/workflows/research_agents/imagegen_agent.py:61`
- **Human gate:** none detected

**Tools (1):**

- **`<activity_as_tool(...)>`** — Wraps a Temporal workflow activity as a callable tool.

### Agent 06.3: `PDFGeneratorAgent`

- **Definition:** `openai_agents/workflows/research_agents/pdf_generator_agent.py:49`
- **Human gate:** none detected

**Tools (1):**

- **`<activity_as_tool(...)>`** — Wraps a Temporal workflow activity as a callable tool.

### Agent 06.4: `Search agent`

- **Definition:** `openai_agents/workflows/research_agents/search_agent.py:15`
- **Human gate:** none detected

**Tools (1):**

- **`<WebSearchTool(...)>`** — Web search — returns live search results for a query.

## Repo 07: `Shaurya-Sethi/circuitron`

- **Framework:** openai-agents
- **Pinned SHA:** `6e2be932deab505464b62e1981eec55c997e8859`
- **Agent definitions found:** 12 total; 0 with tool lists; 0 shown
  _(Note: 12 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 08: `yuriwa/crewai-sheets-ui`

- **Framework:** crewai
- **Pinned SHA:** `46ee39143ff99052c29d1dc9805133c2de81dd25`
- **Agent definitions found:** 1 total; 0 with tool lists; 0 shown
  _(Note: 1 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 09: `NanGePlus/CrewAITest`

- **Framework:** crewai
- **Pinned SHA:** `17ee7bf1d0799172ae5dffbec34975eb17aed88d`
- **Agent definitions found:** 24 total; 12 with tool lists; 12 shown
  _(Note: 12 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 09.1: `Agent`

- **Definition:** `crewAIWithHumanFeedback/crew.py:54`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.2: `Agent`

- **Definition:** `crewAIWithHumanFeedback/crew.py:63`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.3: `Agent`

- **Definition:** `crewAIWithPipelines/crewPipeline.py:46`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.4: `Agent`

- **Definition:** `crewAIWithPipelines/crewPipeline.py:55`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.5: `Agent`

- **Definition:** `crewAIWithPipelines/crew.py:31`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.6: `Agent`

- **Definition:** `crewAIWithPipelines/crew.py:40`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.7: `Agent`

- **Definition:** `crewAIWithMarketingStrategy/crew.py:54`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.8: `Agent`

- **Definition:** `crewAIWithMarketingStrategy/crew.py:63`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.9: `Agent`

- **Definition:** `crewAIWithRag/crew.py:31`
- **Human gate:** none detected

**Tools (1):**

- **`vectorSearch`** — global CHROMADB_COLLECTION_NAME

### Agent 09.10: `Agent`

- **Definition:** `crewAIWithRag/crew.py:40`
- **Human gate:** none detected

**Tools (1):**

- **`saveText2Pdf`** — 使用这个工具来保存任务输出为PDF文件，支持中文。

### Agent 09.11: `Agent`

- **Definition:** `crewAIWithFlows/crews/marketAnalystCrew/marketAnalystCrew.py:29`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

### Agent 09.12: `Agent`

- **Definition:** `crewAIWithFlows/crews/contentCreatorCrew/contentCreatorCrew.py:30`
- **Human gate:** none detected

**Tools (2):**

- **`<SerperDevTool(...)>`** — Web search via Serper.dev API — returns Google search results for a query.
- **`<ScrapeWebsiteTool(...)>`** — Fetches and returns the text content of a given URL.

## Repo 10: `tonykipkemboi/crewai-streamlit-demo`

- **Framework:** crewai
- **Pinned SHA:** `653549a53d3c085471405c5952d9258045a0f056`
- **Agent definitions found:** 1 total; 1 with tool lists; 1 shown

### Agent 10.1: `Research Analyst`

- **Definition:** `src/components/researcher.py:108`
- **Human gate:** none detected

**Tools (1):**

- **`<EXAAnswerTool(...)>`** — A tool that asks Exa a question and returns the answer.

## Repo 11: `liangdabiao/easy_investment_Agent_crewai`

- **Framework:** crewai
- **Pinned SHA:** `ec73a6cb337ff8d6d18040c4893efe16bada5df3`
- **Agent definitions found:** 8 total; 4 with tool lists; 4 shown
  _(Note: 4 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 11.1: `Agent`

- **Definition:** `stock_analysis_a_stock/src/a_stock_analysis/crew.py:45`
- **Human gate:** none detected

**Tools (3):**

- **`<AStockDataTool(...)>`** — 获取A股和港股的实时行情、历史数据、财务信息等，支持上交所、深交所和港股
- **`<FinancialAnalysisTool(...)>`** — 深度分析A股公司财务报表，包括财务比率、趋势分析和同业对比
- **`<CalculatorTool(...)>`** — Useful to perform any mathematical calculations, like sum, minus, multiplication, division, etc. The input to this tool should be a mathematical  expression, a couple examples are `200*7` or `5000/2*10.

### Agent 11.2: `Agent`

- **Definition:** `stock_analysis_a_stock/src/a_stock_analysis/crew.py:65`
- **Human gate:** none detected

**Tools (3):**

- **`<AStockDataTool(...)>`** — 获取A股和港股的实时行情、历史数据、财务信息等，支持上交所、深交所和港股
- **`<FinancialAnalysisTool(...)>`** — 深度分析A股公司财务报表，包括财务比率、趋势分析和同业对比
- **`<CalculatorTool(...)>`** — Useful to perform any mathematical calculations, like sum, minus, multiplication, division, etc. The input to this tool should be a mathematical  expression, a couple examples are `200*7` or `5000/2*10.

### Agent 11.3: `Agent`

- **Definition:** `stock_analysis_a_stock/src/a_stock_analysis/crew.py:85`
- **Human gate:** none detected

**Tools (2):**

- **`<AStockDataTool(...)>`** — 获取A股和港股的实时行情、历史数据、财务信息等，支持上交所、深交所和港股
- **`<MarketSentimentTool(...)>`** — 分析A股市场情绪，包括资金流向、新闻情绪和技术情绪

### Agent 11.4: `Agent`

- **Definition:** `stock_analysis_a_stock/src/a_stock_analysis/crew.py:104`
- **Human gate:** none detected

**Tools (1):**

- **`<CalculatorTool(...)>`** — Useful to perform any mathematical calculations, like sum, minus, multiplication, division, etc. The input to this tool should be a mathematical  expression, a couple examples are `200*7` or `5000/2*10.

## Repo 12: `Andrew-Tsegaye/Advanced-AI-Code-Generation-Agent`

- **Framework:** llama-index
- **Pinned SHA:** `0fb975afba4e2858ad9124cdf0ebe935e64614bd`
- **Agent definitions found:** 0 total; 0 with tool lists; 0 shown

_No agents with resolvable tool lists found in this repo._

---

_End of blind audit materials._