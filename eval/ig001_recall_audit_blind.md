# IG001 Recall Audit — Blind Materials

**Purpose:** Human auditors identify confused-deputy risk from agent+tool definitions,
without reference to scanner output.

**Instructions for auditors:**
1. For each agent, read the tool list and behavioral descriptions.
2. Mark any agent you believe poses confused-deputy risk: it accepts untrusted external
   input via one tool and takes a privileged action via another, with no human gate.
3. Record your reasoning. Do NOT refer to scanner results.

**Selection:** 12 repos, stratified by framework, seed=42.
Allocations: langgraph=5, openai-agents=7.

**Coverage note (extraction, not scanner output):**
- 7 of 12 repos yielded agents with resolvable tool lists.
- 46 of 167 detected agent definitions have tool lists.
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

## Repo 04: `nuglifeleoji/Options-Analytics-Agent`

- **Framework:** langgraph
- **Pinned SHA:** `9de22c3184598440ae2209be87bcd764bd1349af`
- **Agent definitions found:** 1 total; 1 with tool lists; 1 shown

### Agent 04.1: `create_react_agent`

- **Definition:** `Week1/start-prebuiltagent.py:12`
- **Human gate:** `checkpointer=<set>`

**Tools (1):**

- **`get_weather`** — Get weather for a given city.

## Repo 05: `agentscope-ai/agentscope-runtime`

- **Framework:** langgraph
- **Pinned SHA:** `22072fd7075ce0c6f43cb39509d6a14b0e60ddb5`
- **Agent definitions found:** 1 total; 0 with tool lists; 0 shown
  _(Note: 1 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 06: `hellotinah/financial_agent`

- **Framework:** openai-agents
- **Pinned SHA:** `126c15ceb7644269610edd37d11f66daa5828122`
- **Agent definitions found:** 8 total; 0 with tool lists; 0 shown
  _(Note: 8 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 07: `temporal-community/openai-agents-sdk-deep-research-demo`

- **Framework:** openai-agents
- **Pinned SHA:** `c0761d82cfff65f972c333418b353215832c2f41`
- **Agent definitions found:** 8 total; 3 with tool lists; 3 shown
  _(Note: 5 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 07.1: `ImageGenAgent`

- **Definition:** `openai_agents/workflows/research_agents/imagegen_agent.py:61`
- **Human gate:** none detected

**Tools (1):**

- **`<activity_as_tool(...)>`** — (no description found)

### Agent 07.2: `PDFGeneratorAgent`

- **Definition:** `openai_agents/workflows/research_agents/pdf_generator_agent.py:46`
- **Human gate:** none detected

**Tools (1):**

- **`<activity_as_tool(...)>`** — (no description found)

### Agent 07.3: `Search agent`

- **Definition:** `openai_agents/workflows/research_agents/search_agent.py:20`
- **Human gate:** none detected

**Tools (1):**

- **`<WebSearchTool(...)>`** — (no description found)

## Repo 08: `Shaurya-Sethi/circuitron`

- **Framework:** openai-agents
- **Pinned SHA:** `6e2be932deab505464b62e1981eec55c997e8859`
- **Agent definitions found:** 12 total; 0 with tool lists; 0 shown
  _(Note: 12 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 09: `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK`

- **Framework:** openai-agents
- **Pinned SHA:** `f49a98d003a911201c471970ef896c190344b083`
- **Agent definitions found:** 94 total; 32 with tool lists; 15 shown (capped at 15)
  _(Note: 62 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 09.1: `Customer service agent`

- **Definition:** `Chapter8/input_guardrail.py:49`
- **Human gate:** none detected

**Tools (1):**

- **`get_order_status`** — Returns the status of an order given the customer's Order ID

### Agent 09.2: `Customer service agent`

- **Definition:** `Chapter8/input_guardrail_agent.py:62`
- **Human gate:** none detected

**Tools (1):**

- **`get_order_status`** — Returns the status of an order given the customer's Order ID

### Agent 09.3: `Customer service agent`

- **Definition:** `Chapter8/test_end_to_end.py:31`
- **Human gate:** none detected

**Tools (1):**

- **`get_order_status`** — Returns the status of an order given the customer's Order ID

### Agent 09.4: `Physics Agent`

- **Definition:** `Chapter8/visualization.py:15`
- **Human gate:** none detected

**Tools (1):**

- **`calculate_physics_equation`** — pass

### Agent 09.5: `Culture Agent`

- **Definition:** `Chapter8/visualization.py:22`
- **Human gate:** none detected

**Tools (1):**

- **`perform_culture_survey`** — pass

### Agent 09.6: `Research`

- **Definition:** `Chapter8/nested_spans.py:16`
- **Human gate:** none detected

**Tools (1):**

- **`get_fun_facts`** — return 'The Eiffel Tower is in Paris'

### Agent 09.7: `Text Generation`

- **Definition:** `Chapter8/nested_spans.py:23`
- **Human gate:** none detected

**Tools (1):**

- **`clean_up_poem`** — return poem_string.upper()

### Agent 09.8: `Triage Agent`

- **Definition:** `Chapter6/dynamic_approach.py:12`
- **Human gate:** none detected

**Tools (2):**

- **`complaints_agent.as_tool`** — [sub-agent wrapping: [agent: Complaints Agent]]
- **`inquiry_agent.as_tool`** — [sub-agent wrapping: [agent: General Inquiry Agent]]

### Agent 09.9: `Shipping Support Agent`

- **Definition:** `Chapter7/local_context.py:25`
- **Human gate:** none detected

**Tools (1):**

- **`get_shipping_status`** — Provide the shipping status for the current order.

### Agent 09.10: `QuestionAnswer`

- **Definition:** `Chapter5/ltm_structured_memory_recall.py:50`
- **Human gate:** none detected

**Tools (2):**

- **`save_memory`** — Saves a memory to a memory store.
- **`load_memory`** — Loads a set of memory from a memory store.

### Agent 09.11: `USConstitutionTool`

- **Definition:** `Chapter5/us_constitution_agent.py:7`
- **Human gate:** none detected

**Tools (1):**

- **`filesearchtool`** — (no description found)

### Agent 09.12: `Customer service agent`

- **Definition:** `Chapter3/customer_service_agent.py:37`
- **Human gate:** none detected

**Tools (1):**

- **`get_order_status`** — Returns the status of an order given the customer's Order ID

### Agent 09.13: `MortgageAdvisor`

- **Definition:** `Chapter4/mortgage_agent_force_tool_use.py:27`
- **Human gate:** `tool_use_behavior='stop_on_first_tool'`

**Tools (1):**

- **`calculate_mortgage`** — This function calculates the mortgage payment.

### Agent 09.14: `WebTool`

- **Definition:** `Chapter4/file_search_tool.py:7`
- **Human gate:** none detected

**Tools (1):**

- **`filesearchtool`** — (no description found)

### Agent 09.15: `Crypto Agent`

- **Definition:** `Chapter4/mcp_agent.py:14`
- **Human gate:** none detected

**Tools (1):**

- **`mcp_tool`** — (no description found)

## Repo 10: `OctagonAI/octagon-vc-agents`

- **Framework:** openai-agents
- **Pinned SHA:** `8af68fe6ea6f921fa17eb2d2ebb1c63c25d3aee1`
- **Agent definitions found:** 12 total; 2 with tool lists; 2 shown
  _(Note: 10 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

### Agent 10.1: `web-search-agent`

- **Definition:** `src/octagon_vc_agents/openai_agents.py:94`
- **Human gate:** none detected

**Tools (1):**

- **`<WebSearchTool(...)>`** — (no description found)

### Agent 10.2: `Agent`

- **Definition:** `src/octagon_vc_agents/openai_agents.py:111`
- **Human gate:** none detected

**Tools (11):**

- **`octagon_sec_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the SEC for public companies.]
- **`octagon_transcripts_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the transcripts of public companies.]
- **`octagon_stock_data_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the stock market for public companies.]
- **`octagon_financials_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the financials of public companies.]
- **`octagon_companies_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the private companies in the Octagon database.]
- **`octagon_funding_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the funding of public companies.]
- **`octagon_deals_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the deals of public companies.]
- **`octagon_investors_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the investors of public companies.]
- **`octagon_debts_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the debts of public companies.]
- **`octagon_scraper_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can scrape the website for information about a company.]
- **`web_search_agent.as_tool`** — [sub-agent wrapping: A helpful agent that can answer questions about the companies, such as news, articles, and social media.]

## Repo 11: `khaoss85/AI-Team-Orchestrator`

- **Framework:** openai-agents
- **Pinned SHA:** `cbdd9d9f87da97f8ce07346f5edf1dced55f1232`
- **Agent definitions found:** 5 total; 0 with tool lists; 0 shown
  _(Note: 5 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

## Repo 12: `evalops/agent-harness`

- **Framework:** openai-agents
- **Pinned SHA:** `8f11a6dc33f69f5e7199490d53dcefa318d52d1d`
- **Agent definitions found:** 1 total; 0 with tool lists; 0 shown
  _(Note: 1 agent definitions with no `tools=[...]` argument omitted — not auditable for IG001.)_

_No agents with resolvable tool lists found in this repo._

---

_End of blind audit materials._