# IG002 sample dossier — 45 findings

**Sampling:** stratified by construction form, seed 42, per-repo cap 5.
**Strata:** callable/opaque 8, f-string 12, plain variable 25.
**No labels in this document** — evidence only, for review before labeling.

---

## Callable/opaque (8 findings)

### F01 — study8677/OpenCMO

| Field | Value |
|---|---|
| Repo | `study8677/OpenCMO` |
| Pinned SHA | `388cad4c9d48` |
| File:line | `src/opencmo/agents/producthunt.py:9` |
| Framework | `openai-agents` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | none |

**Source context:**
```python
         1: from agents import Agent
         2: 
         3: from opencmo.agents.prompt_contracts import build_prompt
         4: from opencmo.config import get_model
         5: 
         6: producthunt_expert = Agent(
         7:     name="Product Hunt Expert",
         8:     handoff_description="Hand off to this expert when the user needs content for Product Hunt.",
  >>>    9:     instructions=build_prompt(
        10:         base_instructions="""You are a Product Hunt launch specialist for tech products and startups.
        11: 
        12: Based on the product information provided by the CMO Agent, create Product Hunt launch copy.
        13: 
        14: ## Your Output Format
        15: 
        16: Use this exact output shape:
        17: 
        18: Tagline 1
        19: [tagline]
        20: 
        21: Tagline 2
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    handoff_description="Hand off to this expert when the user needs content for Product Hunt.",
    instructions=build_prompt(
        base_instructions="""You are a Product Hunt launch specialist for tech products and startups.

Based on the product information provided by the CMO Agent, create Produc
```

---

### F02 — study8677/OpenCMO

| Field | Value |
|---|---|
| Repo | `study8677/OpenCMO` |
| Pinned SHA | `388cad4c9d48` |
| File:line | `src/opencmo/agents/jike.py:9` |
| Framework | `openai-agents` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | none |

**Source context:**
```python
         1: from agents import Agent
         2: 
         3: from opencmo.agents.prompt_contracts import build_prompt
         4: from opencmo.config import get_model
         5: 
         6: jike_expert = Agent(
         7:     name="Jike Expert",
         8:     handoff_description="Hand off to this expert when the user needs content for 即刻 (Jike).",
  >>>    9:     instructions=build_prompt(
        10:         base_instructions="""You are a 即刻 (Jike) content specialist for indie developers and startup founders.
        11: 
        12: 即刻 is a popular Chinese social platform especially beloved by indie developers, startup founders, product managers, and tech enthusiasts. It has a strong "圈子" (circle/community) culture.
        13: 
        14: ## Your Output Format
        15: 
        16: Use this exact output shape:
        17: 
        18: 动态文案
        19: [post]
        20: 
        21: 配图建议
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    instructions=build_prompt(
        base_instructions="""You are a 即刻 (Jike)

`build_prompt` function body:
defined in prompt_contracts.py:
  66: def build_prompt(
  67:     *,
  68:     base_instructions: str,
  69:     task_contract: str | None = None,
  70:     channel_contract: str | None = None,
  71:     brand_overlay: str | None = None,
  72: ) -> str:
  73:     """Build a prompt from shared contracts plus local task/channel rules."""
  74:     if brand_overlay and "## Brand Overlay" not in brand_overlay:
  75:         brand_overlay = f"## Brand Overlay\n{brand_overlay.strip()}"
  76:     sections = [
  77:         base_instructions.rstrip(),
  78:         TRUTH_CONTRACT,
  79:         ANTI_SLOP_GUARDRAILS,
  80:         MARKETING_DECISION_FRAMEWORK,
  81:         MARKETING_OUTPUT_REQUIREMENTS,
  82:         USER_EXPERIENCE_CONTRACT,
  83:     ]
  84:     if task_contract:
  85:         sections.append(task_contract.strip())
  86:     if channel_contract:
```

---

### F03 — study8677/OpenCMO

| Field | Value |
|---|---|
| Repo | `study8677/OpenCMO` |
| Pinned SHA | `388cad4c9d48` |
| File:line | `src/opencmo/agents/gitcode.py:9` |
| Framework | `openai-agents` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | none |

**Source context:**
```python
         1: from agents import Agent
         2: 
         3: from opencmo.agents.prompt_contracts import build_prompt
         4: from opencmo.config import get_model
         5: 
         6: gitcode_expert = Agent(
         7:     name="GitCode Expert",
         8:     handoff_description="Hand off to this expert when the user needs content for GitCode.",
  >>>    9:     instructions=build_prompt(
        10:         base_instructions="""You are a GitCode content specialist for mirroring and promoting projects on CSDN's code platform.
        11: 
        12: GitCode is CSDN's code hosting platform (gitcode.com). It targets the large CSDN user base and offers project hosting and community features.
        13: 
        14: ## Your Output Format
        15: 
        16: Use this exact output shape:
        17: 
        18: 仓库镜像设置
        19: 仓库名称建议: [name]
        20: README 中文优化: [summary]
        21: 项目描述: [description]
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    instructions=build_prompt(
        base_instructions="""You are a GitCode content specialist for mirroring and promoting projects on CSDN's code platform.

GitCode is CSDN's code hosting platform (gitcode.com)

`build_prompt` function body:
defined in prompt_contracts.py:
  66: def build_prompt(
  67:     *,
  68:     base_instructions: str,
  69:     task_contract: str | None = None,
  70:     channel_contract: str | None = None,
  71:     brand_overlay: str | None = None,
  72: ) -> str:
  73:     """Build a prompt from shared contracts plus local task/channel rules."""
  74:     if brand_overlay and "## Brand Overlay" not in brand_overlay:
  75:         brand_overlay = f"## Brand Overlay\n{brand_overlay.strip()}"
  76:     sections = [
  77:         base_instructions.rstrip(),
  78:         TRUTH_CONTRACT,
  79:         ANTI_SLOP_GUARDRAILS,
  80:         MARKETING_DECISION_FRAMEWORK,
  81:         MARKETING_OUTPUT_REQUIREMENTS,
  82:         USER_EXPERIENCE_CONTRACT,
  83:     ]
  84:     if task_contract:
  85:         sections.append(task_contract.strip())
  86:     if channel_contract:
```

---

### F04 — study8677/OpenCMO

| Field | Value |
|---|---|
| Repo | `study8677/OpenCMO` |
| Pinned SHA | `388cad4c9d48` |
| File:line | `src/opencmo/agents/sspai.py:9` |
| Framework | `openai-agents` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | none |

**Source context:**
```python
         1: from agents import Agent
         2: 
         3: from opencmo.agents.prompt_contracts import build_prompt
         4: from opencmo.config import get_model
         5: 
         6: sspai_expert = Agent(
         7:     name="Sspai Expert",
         8:     handoff_description="Hand off to this expert when the user needs content for 少数派 (sspai).",
  >>>    9:     instructions=build_prompt(
        10:         base_instructions="""You are a 少数派 (sspai.com) content specialist for productivity tools and tech products.
        11: 
        12: 少数派 is China's premier platform for productivity tools, digital life, and tech enthusiasts. Known for high-quality, in-depth articles about tools and workflows.
        13: 
        14: ## Your Output Format
        15: 
        16: ### 少数派文章 (sspai Article)
        17: - **标题**: 突出工具价值和使用场景
        18:   - 好的例子："用 AI 重塑营销工作流：开源工具 OpenCMO 上手体验"
        19:   - 好的例子："独立开发者的营销自动化方案：我如何把零散动作收成一条工作流"
        20: - **正文** (2000-4000字):
        21:   1. **引言**：使用场景和痛点
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    instructions=build_prompt(
        base_instructions="""You are a 少数派 (sspai.com)

`build_prompt` function body:
defined in prompt_contracts.py:
  66: def build_prompt(
  67:     *,
  68:     base_instructions: str,
  69:     task_contract: str | None = None,
  70:     channel_contract: str | None = None,
  71:     brand_overlay: str | None = None,
  72: ) -> str:
  73:     """Build a prompt from shared contracts plus local task/channel rules."""
  74:     if brand_overlay and "## Brand Overlay" not in brand_overlay:
  75:         brand_overlay = f"## Brand Overlay\n{brand_overlay.strip()}"
  76:     sections = [
  77:         base_instructions.rstrip(),
  78:         TRUTH_CONTRACT,
  79:         ANTI_SLOP_GUARDRAILS,
  80:         MARKETING_DECISION_FRAMEWORK,
  81:         MARKETING_OUTPUT_REQUIREMENTS,
  82:         USER_EXPERIENCE_CONTRACT,
  83:     ]
  84:     if task_contract:
  85:         sections.append(task_contract.strip())
  86:     if channel_contract:
```

---

### F05 — study8677/OpenCMO

| Field | Value |
|---|---|
| Repo | `study8677/OpenCMO` |
| Pinned SHA | `388cad4c9d48` |
| File:line | `src/opencmo/agents/seo.py:20` |
| Framework | `openai-agents` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | none |

**Source context:**
```python
         9: from opencmo.tools.keyword_suggest import suggest_keywords
        10: from opencmo.tools.llmstxt import generate_llmstxt, validate_llmstxt
        11: from opencmo.tools.search import web_search
        12: from opencmo.tools.seo_audit import audit_page_seo
        13: from opencmo.tools.serp_tracker import check_keyword_ranking, get_serp_trends
        14: from opencmo.tools.site_audit import audit_site_pages
        15: from opencmo.tools.trends import get_seo_trends
        16: 
        17: seo_agent = Agent(
        18:     name="SEO Audit Expert",
        19:     handoff_description="Hand off to this expert when the user needs a technical SEO audit of a web page.",
  >>>   20:     instructions=build_prompt(
        21:         base_instructions="""You are an SEO audit specialist. You analyze web pages for technical SEO issues and provide actionable fix recommendations.
        22: 
        23: Think like a growth operator, not just a checker. Translate technical issues into lost visibility, missed demand capture, and concrete ranking opportunities.
        24: 
        25: ## Your Workflow
        26: 
        27: 1. **Run the audit**: Use `audit_page_seo` on the provided URL to get a structured SEO report covering:
        28:    - On-page elements (title, meta description, OG tags, headings, etc.)
        29:    - **Core Web Vitals** (LCP, CLS, TBT from Google PageSpeed Insights)
        30:    - **Structured data** (Schema.org / JSON-LD detection)
        31:    - **Crawlability** (robots.txt, sitemap.xml)
        32: 2. **Prioritize findings**: Sort issues by severity — [CRITICAL] first, then [WARNING], then [OK].
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    handoff_description="Hand off to this expert when the user needs a technical SEO audit of a web page.",
    instructions=build_prompt(
        base_instructions="""You are an SEO audit specialist. You analyze web pages for technical SEO issues and provide actionable fix recommendations.

Think like 
```

---

### F06 — langchain-ai/langgraph-swarm-py

| Field | Value |
|---|---|
| Repo | `langchain-ai/langgraph-swarm-py` |
| Pinned SHA | `de22626e3084` |
| File:line | `examples/customer_support/src/agent/customer_support.ipynb:112` |
| Framework | `langgraph` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
       117:         )
       118:         return [{"role": "system", "content": system_prompt}] + state["messages"]
       119: 
       120:     return prompt
       121: 
       122: 
       123: # Define agents
       124: flight_assistant = create_agent(
       125:     model,
       126:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
  >>>  127:     system_prompt=make_prompt("You are a flight booking assistant"),
       128:     name="flight_assistant",
       129: )
       130: 
       131: hotel_assistant = create_agent(
       132:     model,
       133:     tools=[search_hotels, book_hotel, transfer_to_flight_assistant],
       134:     system_prompt=make_prompt("You are a hotel booking assistant"),
       135:     name="hotel_assistant",
       136: )
       137: 
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    system_prompt=make_prompt("You are a flight booking assistant")

`make_prompt` function body:
defined in customer_support.py:
  97: def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
  98:     def prompt(state: dict, config: RunnableConfig) -> list:
  99:         user_id = config["configurable"].get("user_id")
  100:         current_reservation = RESERVATIONS[user_id]
  101:         system_prompt = (
  102:             base_system_prompt
  103:             + f"\n\nUser's active reservation: {current_reservation}"
  104:             + f"Today is: {datetime.datetime.now()}"
  105:         )
  106:         return [{"role": "system", "content": system_prompt}] + state["messages"]
  107: 
  108:     return prompt
  109: 
  110: 
  111: # Define agents
  112: flight_assistant = create_agent(
  113:     model,
  114:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
  115:     system_prompt=make_prompt("You are a flight booking assistant"),
  116:     name="flight_assistant",
  117: )
```

---

### F07 — langchain-ai/langgraph-swarm-py

| Field | Value |
|---|---|
| Repo | `langchain-ai/langgraph-swarm-py` |
| Pinned SHA | `de22626e3084` |
| File:line | `examples/customer_support/src/agent/customer_support.ipynb:119` |
| Framework | `langgraph` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
       124: flight_assistant = create_agent(
       125:     model,
       126:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
       127:     system_prompt=make_prompt("You are a flight booking assistant"),
       128:     name="flight_assistant",
       129: )
       130: 
       131: hotel_assistant = create_agent(
       132:     model,
       133:     tools=[search_hotels, book_hotel, transfer_to_flight_assistant],
  >>>  134:     system_prompt=make_prompt("You are a hotel booking assistant"),
       135:     name="hotel_assistant",
       136: )
       137: 
       138: # Compile and run!
       139: checkpointer = MemorySaver()
       140: builder = create_swarm(
       141:     [flight_assistant, hotel_assistant], default_active_agent="flight_assistant"
       142: )
       143: 
       144: # Important: compile the swarm with a checkpointer to remember
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    system_prompt=make_prompt("You are a hotel booking assistant")

`make_prompt` function body:
defined in customer_support.py:
  97: def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
  98:     def prompt(state: dict, config: RunnableConfig) -> list:
  99:         user_id = config["configurable"].get("user_id")
  100:         current_reservation = RESERVATIONS[user_id]
  101:         system_prompt = (
  102:             base_system_prompt
  103:             + f"\n\nUser's active reservation: {current_reservation}"
  104:             + f"Today is: {datetime.datetime.now()}"
  105:         )
  106:         return [{"role": "system", "content": system_prompt}] + state["messages"]
  107: 
  108:     return prompt
  109: 
  110: 
  111: # Define agents
  112: flight_assistant = create_agent(
  113:     model,
  114:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
  115:     system_prompt=make_prompt("You are a flight booking assistant"),
  116:     name="flight_assistant",
  117: )
```

---

### F08 — langchain-ai/langgraph-swarm-py

| Field | Value |
|---|---|
| Repo | `langchain-ai/langgraph-swarm-py` |
| Pinned SHA | `de22626e3084` |
| File:line | `examples/customer_support/src/agent/customer_support.py:123` |
| Framework | `langgraph` |
| Construction form | Callable/opaque |
| Severity | medium |
| Taint names | (none extracted) |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
       112: # Define agents
       113: flight_assistant = create_agent(
       114:     model,
       115:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
       116:     system_prompt=make_prompt("You are a flight booking assistant"),
       117:     name="flight_assistant",
       118: )
       119: 
       120: hotel_assistant = create_agent(
       121:     model,
       122:     tools=[search_hotels, book_hotel, transfer_to_flight_assistant],
  >>>  123:     system_prompt=make_prompt("You are a hotel booking assistant"),
       124:     name="hotel_assistant",
       125: )
       126: 
       127: # Compile and run!
       128: builder = create_swarm(
       129:     [flight_assistant, hotel_assistant], default_active_agent="flight_assistant"
       130: )
       131: app = builder.compile()
```

**Evidence (what the dynamic value resolves to):**
```
call expression:
    system_prompt=make_prompt("You are a hotel booking assistant")

`make_prompt` function body:
defined in customer_support.py:
  97: def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
  98:     def prompt(state: dict, config: RunnableConfig) -> list:
  99:         user_id = config["configurable"].get("user_id")
  100:         current_reservation = RESERVATIONS[user_id]
  101:         system_prompt = (
  102:             base_system_prompt
  103:             + f"\n\nUser's active reservation: {current_reservation}"
  104:             + f"Today is: {datetime.datetime.now()}"
  105:         )
  106:         return [{"role": "system", "content": system_prompt}] + state["messages"]
  107: 
  108:     return prompt
  109: 
  110: 
  111: # Define agents
  112: flight_assistant = create_agent(
  113:     model,
  114:     tools=[search_flights, book_flight, transfer_to_hotel_assistant],
  115:     system_prompt=make_prompt("You are a flight booking assistant"),
  116:     name="flight_assistant",
  117: )
```

---

## F-string (12 findings)

### F09 — serialx/vibecore

| Field | Value |
|---|---|
| Repo | `serialx/vibecore` |
| Pinned SHA | `8de60c7ad8f4` |
| File:line | `examples/customer_service.py:100` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `RECOMMENDED_PROMPT_PREFIX` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
        89:     Use the following routine to support the customer.
        90:     # Routine
        91:     1. Identify the last question asked by the customer.
        92:     2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
        93:     3. If you cannot answer the question, transfer back to the triage agent.""",
        94:     tools=[faq_lookup_tool],
        95: )
        96: 
        97: seat_booking_agent = Agent[AirlineAgentContext](
        98:     name="Seat Booking Agent",
        99:     handoff_description="A helpful agent that can update a seat on a flight.",
  >>>  100:     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
       101:     You are a seat booking agent. If you are speaking to a customer, you were transferred to from the triage agent.
       102:     Use the following routine to support the customer.
       103:     # Routine
       104:     1. Ask for their confirmation number.
       105:     2. Ask the customer what their desired seat number is.
       106:     3. Use the update seat tool to update the seat on the flight.
       107:     If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
       108:     tools=[update_seat],
       109: )
       110: 
       111: triage_agent = Agent[AirlineAgentContext](
       112:     name="Triage Agent",
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"""{RECOMMENDED_PROMPT_PREFIX}\n    You are a seat booking agent. If you are speaking to a customer, you were transferred to from the triage agent.\n    Use the following routine to support the custome'
  `RECOMMENDED_PROMPT_PREFIX`: imported at line 15:
    15: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
```

---

### F10 — liangdabiao/crewai_stock_analysis_system

| Field | Value |
|---|---|
| Repo | `liangdabiao/crewai_stock_analysis_system` |
| Pinned SHA | `aab66c6a5782` |
| File:line | `src/crews/data_collection_crew.py:207` |
| Framework | `crewai` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `company` |
| Pre-label FP signal | none |

**Source context:**
```python
       196:         """创建所有智能体"""
       197:         agents = []
       198: 
       199:         # 市场研究员 - 优化配置
       200:         try:
       201:             market_tools = [tool for tool in [serper_tool, scrape_tool] if tool is not None]
       202:             if CUSTOM_TOOLS_AVAILABLE and TechnicalAnalysisTool:
       203:                 market_tools.extend([TechnicalAnalysisTool()])
       204: 
       205:             market_researcher = Agent(
       206:                 role="市场研究员",
  >>>  207:                 goal=f"收集{company}的市场趋势、行业动态和相关新闻",
       208:                 backstory="你是一位经验丰富的市场研究员，擅长分析市场趋势和收集行业信息。请在2-3个步骤内完成任务。",
       209:                 verbose=True,
       210:                 tools=market_tools,
       211:                 allow_delegation=False,  # 禁用委托，避免循环调用
       212:                 max_iter=3,  # 减少迭代次数
       213:                 memory=False,  # 禁用内存，避免复杂状态
       214:                 cache=False,  # 禁用缓存，避免问题
       215:             )
       216:             agents.append(market_researcher)
       217:             logger.info("✓ 创建市场研究员智能体成功")
       218:         except Exception as e:
       219:             logger.error(f"✗ 创建市场研究员智能体失败: {str(e)}")
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"收集{company}的市场趋势、行业动态和相关新闻",\n                backstory="你是一位经验丰富的市场研究员，擅长分析市场趋势和收集行业信息。请在2-3个步骤内完成任务。",\n                verbose=True,\n                tools=market_tools,'
  `company`: appears to be function parameter at line 195:
    195: def create_agents(self, company: str, ticker: str) -> List[Agent]:
```

---

### F11 — serialx/vibecore

| Field | Value |
|---|---|
| Repo | `serialx/vibecore` |
| Pinned SHA | `8de60c7ad8f4` |
| File:line | `examples/customer_service.py:115` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `RECOMMENDED_PROMPT_PREFIX` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
       104:     1. Ask for their confirmation number.
       105:     2. Ask the customer what their desired seat number is.
       106:     3. Use the update seat tool to update the seat on the flight.
       107:     If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
       108:     tools=[update_seat],
       109: )
       110: 
       111: triage_agent = Agent[AirlineAgentContext](
       112:     name="Triage Agent",
       113:     handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
       114:     instructions=(
  >>>  115:         f"{RECOMMENDED_PROMPT_PREFIX} "
       116:         "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
       117:     ),
       118:     handoffs=[
       119:         faq_agent,
       120:         handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
       121:     ],
       122: )
       123: 
       124: faq_agent.handoffs.append(triage_agent)
       125: seat_booking_agent.handoffs.append(triage_agent)
       126: 
       127: 
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"{RECOMMENDED_PROMPT_PREFIX} "\n        "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."\n    ),\n    handoffs=['
  `RECOMMENDED_PROMPT_PREFIX`: imported at line 15:
    15: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
```

---

### F12 — PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK

| Field | Value |
|---|---|
| Repo | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` |
| Pinned SHA | `f49a98d003a9` |
| File:line | `Chapter6/handoff_prompt.py:19` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `RECOMMENDED_PROMPT_PREFIX` |
| Pre-label FP signal | none |

**Source context:**
```python
         8:     name="Complaints Agent",
         9:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Introduce yourself as the complaints agent. Handle any customer complaints with empathy and clear next steps."
        10: )
        11: inquiry_agent = Agent(
        12:     name="General Inquiry Agent",
        13:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Introduce yourself as the inquiry agent. Answer general questions about our services promptly."
        14: )
        15: 
        16: # Create the triage agent with handoffs
        17: triage_agent = Agent(
        18:     name="Triage Agent",
  >>>   19:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Triage the user's request and call the appropriate agent",
        20:     handoffs=[complaints_agent, inquiry_agent]
        21: )
        22: 
        23: while True:
        24:     question = input("You: ")
        25:     result = Runner.run_sync(triage_agent, question)
        26:     print("Agent: ", result.final_output)
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"{RECOMMENDED_PROMPT_PREFIX}. Triage the user\'s request and call the appropriate agent",\n    handoffs=[complaints_agent, inquiry_agent]\n)\n'
  `RECOMMENDED_PROMPT_PREFIX`: imported at line 2:
    2: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
```

---

### F13 — jkmaina/openai-agents-blueprint

| Field | Value |
|---|---|
| Repo | `jkmaina/openai-agents-blueprint` |
| Pinned SHA | `76cbbcb41a93` |
| File:line | `chapter4/03_content_moderation_minimal.py:53` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `level`, `level`, `ModerationLevel` |
| Pre-label FP signal | none |

**Source context:**
```python
        42:             r'\b(hate|violence|illegal)\b'
        43:         ]
        44:         
        45:         # Strict: Broader detection
        46:         self.strict_patterns = [
        47:             r'\b(hate|violence|illegal|inappropriate|offensive|harmful)\b',
        48:             r'\b(bypass|hack|exploit)\b'
        49:         ]
        50:         
        51:         self.agent = Agent(
        52:             name="Moderator",
  >>>   53:             instructions=f"""
        54:             Moderate content with {level.value} standards.
        55:             {'Block potentially harmful content.' if level == ModerationLevel.STRICT else 'Only block clearly harmful content.'}
        56:             """,
        57:             output_type=ModerationResult
        58:         )
        59:     
        60:     async def moderate(self, content: str) -> ModerationResult:
        61:         # Quick pattern check
        62:         patterns = self.strict_patterns if self.level == ModerationLevel.STRICT else self.lenient_patterns
        63:         
        64:         for pattern in patterns:
        65:             if re.search(pattern, content, re.IGNORECASE):
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"""\n            Moderate content with {level.value} standards.\n            {\'Block potentially harmful content.\' if level == ModerationLevel.STRICT else \'Only block clearly harmful content.\'}\n       '
  `level`: appears to be function parameter at line 37:
    37: def __init__(self, level: ModerationLevel):
  `level`: appears to be function parameter at line 37:
    37: def __init__(self, level: ModerationLevel):
  `ModerationLevel`: appears to be function parameter at line 37:
    37: def __init__(self, level: ModerationLevel):
```

---

### F14 — AbubakrChan/crewai-UI-business-product-launch

| Field | Value |
|---|---|
| Repo | `AbubakrChan/crewai-UI-business-product-launch` |
| Pinned SHA | `52a235f7eb62` |
| File:line | `main.py:27` |
| Framework | `crewai` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `product_name` |
| Pre-label FP signal | none |

**Source context:**
```python
        16:     )
        17: 
        18: duckduckgo_search = DuckDuckGoSearchRun()
        19: 
        20: #to keep track of tasks performed by agents
        21: task_values = []
        22: 
        23: def create_crewai_setup(product_name):
        24:     # Define Agents
        25:     market_research_analyst = Agent(
        26:         role="Market Research Analyst",
  >>>   27:         goal=f"""Analyze the market demand for {product_name} and 
        28:                  suggest marketing strategies""",
        29:         backstory=f"""Expert at understanding market demand, target audience, 
        30:                       and competition for products like {product_name}. 
        31:                       Skilled in developing marketing strategies 
        32:                       to reach a wide audience.""",
        33:         verbose=True,
        34:         allow_delegation=True,
        35:         tools=[duckduckgo_search],
        36:         llm=llm,
        37:     )
        38: 
        39:     technology_expert = Agent(
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"""Analyze the market demand for {product_name} and \n                 suggest marketing strategies""",\n        backstory=f"""Expert at understanding market demand, target audience, \n                 '
  `product_name`: defined at line 201 in same file:
    201:     product_name = st.text_input("Enter a product name to analyze the market and business strategy.")
    202: 
    203:     if st.button("Run Analysis"):
    204:         # Placeholder for stopwatch
    205:         stopwatch_placeholder = st.empty()
    206:         
```

---

### F15 — alexfazio/viral-clips-crew

| Field | Value |
|---|---|
| Repo | `alexfazio/viral-clips-crew` |
| Pinned SHA | `82888d948177` |
| File:line | `crew.py:56` |
| Framework | `crewai` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `dedent` |
| Pre-label FP signal | none |

**Source context:**
```python
        45: def main(extracts):
        46:     # Create the crew_output directory if it doesn't exist
        47:     os.makedirs("crew_output", exist_ok=True)
        48: 
        49:     # Read subtitles
        50:     subtitles = get_subtitles()
        51:     if subtitles is None:
        52:         logging.error("Failed to read subtitles. Exiting.")
        53:         return
        54: 
        55:     subtitler_agent_1 = Agent(
  >>>   56:         role=dedent((
        57:             f"""
        58:             Segment 1 Subtitler
        59:             """)),
        60:         backstory=dedent((
        61:             f"""
        62:             Experienced subtitler who writes captions or subtitles that accurately represent the audio, including dialogue, sound effects, and music. The subtitles need to be properly timed with the video using correct time codes.
        63:             """)),
        64:         goal=dedent((
        65:             f"""
        66:             Match a list of extracts from a video clip with the corresponding timed subtitles. Given the segments found by the Digital Producer, find the segment timings within the `.srt` file and return each segment as an `.srt` subtitle segment.
        67:             """)),
        68:         allow_delegation=False,
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"""\n            Segment 1 Subtitler\n            """)),'
  `dedent`: imported at line 6:
    6: from textwrap import dedent
```

---

### F16 — hellotinah/financial_agent

| Field | Value |
|---|---|
| Repo | `hellotinah/financial_agent` |
| Pinned SHA | `126c15ceb764` |
| File:line | `financial_research_agent/voice_chat.py:33` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | high |
| Taint names | `financial_report_content` |
| Pre-label FP signal | none |

**Source context:**
```python
        22:     name="Spanish",
        23:     handoff_description="A Spanish-speaking agent.",
        24:     instructions=prompt_with_handoff_instructions(
        25:         "You're speaking to a human, so be polite and concise. Speak in Spanish.",
        26:     ),
        27:     model="gpt-4o-mini",
        28: )
        29: 
        30: # Define Main Financial Assistant Agent
        31: agent = Agent(
        32:     name="Assistant",
  >>>   33:     instructions=prompt_with_handoff_instructions(
        34:         f"You're speaking to a human, so be polite and concise. "
        35:         f"You are a financial expert, and your job is to discuss the report with the user.\n\n"
        36:         f"Here is the financial report:\n{financial_report_content}"
        37:     ),
        38:     model="gpt-4o-mini",
        39:     handoffs=[spanish_agent],
        40: )
        41: 
        42: 
        43: class MyWorkflow(VoiceWorkflowBase):
        44:     def __init__(self, secret_word: str, on_start: Callable[[str], None]):
        45:         """
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"You\'re speaking to a human, so be polite and concise. "\n        f"You are a financial expert, and your job is to discuss the report with the user.\\n\\n"\n        f"Here is the financial report:\\n{fina'
  `financial_report_content`: defined at line 15 in same file:
    15:         financial_report_content = file.read()
    16: else:
    17:     print("financial_report.txt not found. It will be created after running the agent.")
    18:     financial_report_content = "No financial data available yet."
    19: 
    20: # Define Spanish Agent
```

---

### F17 — liangdabiao/crewai_stock_analysis_system

| Field | Value |
|---|---|
| Repo | `liangdabiao/crewai_stock_analysis_system` |
| Pinned SHA | `aab66c6a5782` |
| File:line | `src/crews/data_collection_crew.py:269` |
| Framework | `crewai` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `company` |
| Pre-label FP signal | none |

**Source context:**
```python
       258:                 cache=False,  # 禁用缓存
       259:             )
       260:             agents.append(technical_analyst)
       261:             logger.info("✓ 创建技术分析师智能体成功")
       262:         except Exception as e:
       263:             logger.error(f"✗ 创建技术分析师智能体失败: {str(e)}")
       264: 
       265:         # 数据验证专家 - 简化配置
       266:         try:
       267:             data_validator = Agent(
       268:                 role="数据验证专家",
  >>>  269:                 goal=f"验证收集的{company}数据的准确性和完整性",
       270:                 backstory="你是数据质量专家，擅长数据验证和清洗。请在1-2个步骤内完成任务。",
       271:                 verbose=True,
       272:                 allow_delegation=False,  # 禁用委托
       273:                 max_iter=2,  # 减少迭代次数
       274:                 memory=False,  # 禁用内存
       275:                 cache=False,  # 禁用缓存
       276:             )
       277:             agents.append(data_validator)
       278:             logger.info("✓ 创建数据验证专家智能体成功")
       279:         except Exception as e:
       280:             logger.error(f"✗ 创建数据验证专家智能体失败: {str(e)}")
       281: 
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"验证收集的{company}数据的准确性和完整性",\n                backstory="你是数据质量专家，擅长数据验证和清洗。请在1-2个步骤内完成任务。",\n                verbose=True,\n                allow_delegation=False,  # 禁用委托'
  `company`: appears to be function parameter at line 195:
    195: def create_agents(self, company: str, ticker: str) -> List[Agent]:
```

---

### F18 — alexfazio/viral-clips-crew

| Field | Value |
|---|---|
| Repo | `alexfazio/viral-clips-crew` |
| Pinned SHA | `82888d948177` |
| File:line | `crew.py:102` |
| Framework | `crewai` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `dedent` |
| Pre-label FP signal | none |

**Source context:**
```python
        91:         allow_delegation=False,
        92:         verbose=True,
        93:         max_iter=1,
        94:         max_rpm=1,
        95:         llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0801",
        96:                                    verbose=True,
        97:                                    temperature=0.0,
        98:                                    google_api_key=gemini_api_key)
        99:     )
       100: 
       101:     subtitler_agent_3 = Agent(
  >>>  102:         role=dedent((
       103:             f"""
       104:             Segment 3 Subtitler
       105:             """)),
       106:         backstory=dedent((
       107:             f"""
       108:             Experienced subtitler who writes captions or subtitles that accurately represent the audio, including dialogue, sound effects, and music. The subtitles need to be properly timed with the video using correct time codes.
       109:             """)),
       110:         goal=dedent((
       111:             f"""
       112:             Match a list of extracts from a video clip with the corresponding timed subtitles. Given the segments found by the Digital Producer, find the segment timings within the `.srt` file and return each segment as an `.srt` subtitle segment.
       113:             """)),
       114:         allow_delegation=False,
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"""\n            Segment 3 Subtitler\n            """)),'
  `dedent`: imported at line 6:
    6: from textwrap import dedent
```

---

### F19 — PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK

| Field | Value |
|---|---|
| Repo | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` |
| Pinned SHA | `f49a98d003a9` |
| File:line | `Chapter6/handoff_prompt.py:9` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `RECOMMENDED_PROMPT_PREFIX` |
| Pre-label FP signal | none |

**Source context:**
```python
         1: from agents import Agent, Runner
         2: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
         3: 
         4: print(RECOMMENDED_PROMPT_PREFIX)
         5: 
         6: # Create two agents
         7: complaints_agent = Agent(
         8:     name="Complaints Agent",
  >>>    9:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Introduce yourself as the complaints agent. Handle any customer complaints with empathy and clear next steps."
        10: )
        11: inquiry_agent = Agent(
        12:     name="General Inquiry Agent",
        13:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Introduce yourself as the inquiry agent. Answer general questions about our services promptly."
        14: )
        15: 
        16: # Create the triage agent with handoffs
        17: triage_agent = Agent(
        18:     name="Triage Agent",
        19:     instructions=f"{RECOMMENDED_PROMPT_PREFIX}. Triage the user's request and call the appropriate agent",
        20:     handoffs=[complaints_agent, inquiry_agent]
        21: )
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"{RECOMMENDED_PROMPT_PREFIX}. Introduce yourself as the complaints agent. Handle any customer complaints with empathy and clear next steps."\n)\ninquiry_agent = Agent(\n    name="General Inquiry Agent",'
  `RECOMMENDED_PROMPT_PREFIX`: imported at line 2:
    2: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
```

---

### F20 — PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK

| Field | Value |
|---|---|
| Repo | `PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK` |
| Pinned SHA | `f49a98d003a9` |
| File:line | `Chapter6/swarm.py:13` |
| Framework | `openai-agents` |
| Construction form | F-string |
| Severity | medium |
| Taint names | `role` |
| Pre-label FP signal | none |

**Source context:**
```python
         2: import concurrent.futures
         3: 
         4: # Create our agents
         5: roles = [
         6:     "Urban Planner", "Artist", "Chef", "Engineer", "Teacher",
         7:     "Doctor", "Mechanic", "Lawyer", "Historian", "Environmentalist"
         8: ]
         9: 
        10: city_agents = [
        11:     Agent(
        12:         name=f"{role} Agent",
  >>>   13:         instructions=f"You are a {role.lower()}. Answer the question: 'If you were to design your dream city from scratch, what would it have?' Be creative and imaginative, but concise"
        14:     ) for role in roles
        15: ]
        16: 
        17: # Define the summary agent
        18: summary_agent = Agent(
        19:     name="City Design Aggregator",
        20:     instructions="You are a city designer. You’ve just received 10 creative responses from different citizens. Read all of their responses and consolidate them into a cohesive, imaginative, and well-rounded city plan."
        21: )
        22: 
        23: # Create a session
        24: session = SQLiteSession("swarm")
        25: conversation_history = []
```

**Evidence (what the dynamic value resolves to):**
```
f-string expression:
    'f"{role} Agent",\n        instructions=f"You are a {role.lower()}. Answer the question: \'If you were to design your dream city from scratch, what would it have?\' Be creative and imaginative, but concis'
  `role`: not resolved in this file (possibly imported or set via injection)
```

---

## Plain variable (25 findings)

### F21 — xark-argo/argo

| Field | Value |
|---|---|
| Repo | `xark-argo/argo` |
| Pinned SHA | `615e92152915` |
| File:line | `argo/backend/core/agent/tool_agent_runner.py:65` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `self` |
| Pre-label FP signal | none |

**Source context:**
```python
        54: 
        55:         messages: list[BaseMessage] = []
        56:         if self.memory:
        57:             messages.extend(self.memory.buffer)
        58: 
        59:         messages.append(user_message)
        60: 
        61:         try:
        62:             agent = create_react_agent(
        63:                 model=self.model_config.llm_instance,
        64:                 tools=tools,
  >>>   65:                 prompt=self.instruction or "",
        66:             )
        67:         except NotImplementedError:
        68:             msg = translation_loader.translation.t("chat.tool_call_not_supported")
        69:             raise ValueError(msg)
        70:         except Exception as e:
        71:             raise e
        72: 
        73:         result = await agent.ainvoke(
        74:             input={"messages": messages},
        75:             config=RunnableConfig(callbacks=callbacks, recursion_limit=max_iteration_steps),
        76:         )
        77: 
```

**Evidence (what the dynamic value resolves to):**
```
`self` → not resolved in this file (possibly imported or set via injection)
```

---

### F22 — PurpleAILAB/Decepticon

| Field | Value |
|---|---|
| Repo | `PurpleAILAB/Decepticon` |
| Pinned SHA | `b5fa553b69b6` |
| File:line | `packages/decepticon/decepticon/agents/standard/contract_auditor.py:155` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       144:             role=_ROLE,
       145:             backend=backend,
       146:             llm=llm,
       147:             fallback_models=fallback_models,
       148:             sandbox=sandbox,
       149:         )
       150:     if system_prompt is None:
       151:         system_prompt = load_prompt(_ROLE, shared=["bash"])
       152: 
       153:     return create_agent(
       154:         llm,
  >>>  155:         system_prompt=system_prompt,
       156:         tools=tools,
       157:         middleware=middleware,
       158:         name=_ROLE,
       159:     ).with_config(
       160:         {
       161:             "recursion_limit": recursion_limit or _RECURSION_LIMIT,
       162:             "callbacks": load_plugin_callbacks(role=_ROLE, backend=backend),
       163:         }
       164:     )
       165: 
       166: 
       167: # Module-level graph for LangGraph Platform (langgraph serve)
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 94 in same file:
    94:     system_prompt: str | None = None,
    95:     # ── Tuning ───────────────────────────────────────────────────────
    96:     recursion_limit: int | None = None,
    97: ):
    98:     """Build the ContractAuditor agent.
    99: 
```

---

### F23 — LangGraph-GUI/CrewAI-GUI-Qt

| Field | Value |
|---|---|
| Repo | `LangGraph-GUI/CrewAI-GUI-Qt` |
| Pinned SHA | `463bb270ffea` |
| File:line | `src/WorkFlow.py:55` |
| Framework | `crewai` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `node` |
| Pre-label FP signal | none |

**Source context:**
```python
        44:     for tool_name in node.tools:
        45:         if tool_name == "KeyboardMouseTool":
        46:             tools.append(KeyboardMouseTool())
        47:         elif tool_name == "WebRequestTool":
        48:             tools.append(WebRequestTool())
        49:         elif tool_name == "FileOperationTool":
        50:             tools.append(FileOperationTool())
        51:         elif tool_name == "SystemCommandTool":
        52:             tools.append(SystemCommandTool())
        53:     
        54:     return Agent(
  >>>   55:         role=node.role,
        56:         goal=node.goal,
        57:         backstory=node.backstory,
        58:         verbose=True,
        59:         allow_delegation=False,
        60:         llm=llm,
        61:         tools=tools
        62:     )
        63: 
        64: def create_task(node: NodeData, agent: Agent, node_map: Dict[str, NodeData], task_map: Dict[str, Task]) -> Task:
        65:     steps = []
        66:     for step_id in node.nexts:
        67:         step_node = node_map[step_id]
```

**Evidence (what the dynamic value resolves to):**
```
`node` → defined at line 19 in same file:
    19:             node = NodeData.from_dict(node_data)
    20:             node_map[node.uniq_id] = node
    21:         return node_map
    22: 
    23: def find_nodes_by_type(node_map: Dict[str, NodeData], node_type: str) -> List[NodeData]:
    24:     return [node for node in node_map.values() if node.type == node_type]
```

---

### F24 — Shaurya-Sethi/circuitron

| Field | Value |
|---|---|
| Repo | `Shaurya-Sethi/circuitron` |
| Pinned SHA | `6e2be932deab` |
| File:line | `circuitron/agents.py:194` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `CODE_VALIDATION_PROMPT` |
| Pre-label FP signal | none |

**Source context:**
```python
       183: 
       184: def create_code_validation_agent() -> Agent:
       185:     """Create and configure the Code Validation Agent."""
       186:     model_settings = ModelSettings(
       187:         tool_choice=_tool_choice_for_mcp(settings.code_validation_model)
       188:     )
       189: 
       190:     tools: list[Tool] = [get_kg_usage_guide]
       191: 
       192:     return Agent(
       193:         name="Circuitron-Validator",
  >>>  194:         instructions=CODE_VALIDATION_PROMPT,
       195:         model=settings.code_validation_model,
       196:         output_type=CodeValidationOutput,
       197:         tools=tools,
       198:         mcp_servers=[mcp_manager.get_server()],
       199:         model_settings=model_settings,
       200:     )
       201: 
       202: 
       203: def create_code_correction_agent() -> Agent:
       204:     """Create and configure the Code Correction Agent."""
       205:     model_settings = ModelSettings(
       206:         tool_choice=_tool_choice_for_mcp(settings.code_correction_model)
```

**Evidence (what the dynamic value resolves to):**
```
`CODE_VALIDATION_PROMPT` → imported at lines 17-27 from `.prompts`:
    17: from .prompts import (
    27: CODE_VALIDATION_PROMPT,
  defined in prompts.py at line 770:
    770: CODE_VALIDATION_PROMPT = f"""{RECOMMENDED_PROMPT_PREFIX}
    771: You are Circuitron-Validator, a SKiDL QA expert.
    772: 
    773: **CRITICAL: TOOL USAGE REQUIREMENT**
    774: You have access to a comprehensive knowledge graph and documentation tools that are ESSENTIAL for validating SKiDL code. You MUST use these tools extensively to verify every API call, method, class, and function. Do not make assumptions about API validity - always verify using the available tools.
```

---

### F25 — jkmaina/openai-agents-blueprint

| Field | Value |
|---|---|
| Repo | `jkmaina/openai-agents-blueprint` |
| Pinned SHA | `76cbbcb41a93` |
| File:line | `chapter2/19_token_optimization.py:78` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `config` |
| Pre-label FP signal | none |

**Source context:**
```python
        67:                 ),
        68:                 "instructions": "Be creative but focused. Avoid unnecessary elaboration."
        69:             }
        70:         }
        71:         
        72:         config = optimizations.get(use_case, optimizations["quick_responses"])
        73:         
        74:         return Agent(
        75:             name=f"Optimized_{use_case}",
        76:             model=config["model"],
        77:             model_settings=config["settings"],
  >>>   78:             instructions=config["instructions"]
        79:         )
        80:     
        81:     async def execute_with_caching(self, agent: Agent, user_input: str) -> Dict[str, Any]:
        82:         """Execute with response caching for repeated queries."""
        83:         
        84:         # Simple cache key (in production, use more sophisticated hashing)
        85:         cache_key = f"{agent.name}:{hash(user_input)}"
        86:         
        87:         if cache_key in self.response_cache:
        88:             return {
        89:                 "response": self.response_cache[cache_key],
        90:                 "cached": True,
```

**Evidence (what the dynamic value resolves to):**
```
`config` → defined at line 72 in same file:
    72:         config = optimizations.get(use_case, optimizations["quick_responses"])
    73:         
    74:         return Agent(
    75:             name=f"Optimized_{use_case}",
    76:             model=config["model"],
    77:             model_settings=config["settings"],
```

---

### F26 — szczyglis-dev/py-gpt

| Field | Value |
|---|---|
| Repo | `szczyglis-dev/py-gpt` |
| Pinned SHA | `75bc06e0a0db` |
| File:line | `src/pygpt_net/provider/agents/llama_index/workflow/supervisor.py:339` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `prompt_worker` |
| Pre-label FP signal | none |

**Source context:**
```python
       328:     :return: SupervisorWorkflow instance
       329:     """
       330:     supervisor = FunctionAgent(
       331:         name="Supervisor",
       332:         llm=llm_supervisor,
       333:         system_prompt=prompt_supervisor,
       334:         tools=[],
       335:     )
       336:     worker = FunctionAgent(
       337:         name="Worker",
       338:         llm=llm_worker,
  >>>  339:         system_prompt=prompt_worker,
       340:         tools=tools,
       341:     )
       342: 
       343:     # separate memory for the worker
       344:     worker_memory = Memory.from_defaults(session_id=worker_memory_session_id, token_limit=40000)
       345: 
       346:     return SupervisorWorkflow(
       347:         supervisor=supervisor,
       348:         worker=worker,
       349:         worker_memory=worker_memory,
       350:         verbose=verbose,
       351:         timeout=120,
```

**Evidence (what the dynamic value resolves to):**
```
`prompt_worker` → defined at line 313 in same file:
    313:     prompt_worker: str = WORKER_PROMPT,
    314:     max_steps: int = 12,
    315:     worker_memory_session_id: str = "llama_worker_session"  # session ID for worker memory
    316: ):
    317:     """
    318:     Create a SupervisorWorkflow instance.
```

---

### F27 — Nishmithasshett/LLM-Agent

| Field | Value |
|---|---|
| Repo | `Nishmithasshett/LLM-Agent` |
| Pinned SHA | `aed7cb7b01f6` |
| File:line | `agent.py:94` |
| Framework | `langchain-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
        83:     # Include document_parser tool
        84:     tools = [
        85:         tavily_web_search,
        86:         document_parser  # ⭐ NEW TOOL
        87:     ]
        88: 
        89:     prompt = PromptTemplate.from_template(AGENT_PROMPT)
        90: 
        91:     agent = create_react_agent(
        92:         llm=llm,
        93:         tools=tools,
  >>>   94:         prompt=prompt,
        95:     )
        96: 
        97:     agent_executor = AgentExecutor(
        98:         agent=agent,
        99:         tools=tools,
       100:         verbose=True,
       101:         handle_parsing_errors=True,
       102:         max_iterations=10,
       103:         return_intermediate_steps=False,
       104:     )
       105: 
       106:     return agent_executor
```

**Evidence (what the dynamic value resolves to):**
```
`prompt` → defined at line 89 in same file:
    89:     prompt = PromptTemplate.from_template(AGENT_PROMPT)
    90: 
    91:     agent = create_react_agent(
    92:         llm=llm,
    93:         tools=tools,
    94:         prompt=prompt,
```

---

### F28 — evalops/agent-harness

| Field | Value |
|---|---|
| Repo | `evalops/agent-harness` |
| Pinned SHA | `8f11a6dc33f6` |
| File:line | `agent_harness.py:602` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `config` |
| Pre-label FP signal | none |

**Source context:**
```python
       591:         if config.temperature is not None:
       592:             model_config["temperature"] = config.temperature
       593:         if config.max_output_tokens:
       594:             model_config["max_tokens"] = config.max_output_tokens
       595:         if config.top_p is not None:
       596:             model_config["top_p"] = config.top_p
       597:         if config.stop_sequences:
       598:             model_config["stop"] = config.stop_sequences
       599: 
       600:         agent = Agent(
       601:             name="Agent",
  >>>  602:             instructions=config.system_prompt,
       603:             tools=tools,
       604:             model_config=model_config if model_config else None,
       605:         )
       606: 
       607:         return agent
       608: 
       609:     async def run(
       610:         self, prompt: str, config_override: Optional[HarnessConfig] = None
       611:     ) -> AgentResponse:
       612:         """Run OpenAI agent and return final response"""
       613:         from agents import Runner
       614: 
```

**Evidence (what the dynamic value resolves to):**
```
`config` → defined at line 615 in same file:
    615:         config = self._merge_config(config_override)
    616:         start_time = datetime.now()
    617: 
    618:         logger.info(
    619:             "openai.run.start",
    620:             extra={
```

---

### F29 — bytedance/deer-flow

| Field | Value |
|---|---|
| Repo | `bytedance/deer-flow` |
| Pinned SHA | `7679f21edf3f` |
| File:line | `backend/packages/harness/deerflow/agents/factory.py:143` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       132:         # Deduplicate by tool name — user-provided tools take priority.
       133:         existing_names = {t.name for t in effective_tools}
       134:         for t in extra_tools:
       135:             if t.name not in existing_names:
       136:                 effective_tools.append(t)
       137:                 existing_names.add(t.name)
       138: 
       139:     return create_agent(
       140:         model=model,
       141:         tools=effective_tools or None,
       142:         middleware=effective_middleware,
  >>>  143:         system_prompt=system_prompt,
       144:         state_schema=effective_state,
       145:         checkpointer=checkpointer,
       146:         name=name,
       147:     )
       148: 
       149: 
       150: # ---------------------------------------------------------------------------
       151: # Internal: feature-driven middleware assembly
       152: # ---------------------------------------------------------------------------
       153: 
       154: 
       155: def _assemble_from_features(
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 65 in same file:
    65:     system_prompt: str | None = None,
    66:     middleware: list[AgentMiddleware] | None = None,
    67:     features: RuntimeFeatures | None = None,
    68:     extra_middleware: list[AgentMiddleware] | None = None,
    69:     plan_mode: bool = False,
    70:     state_schema: type | None = None,
```

---

### F30 — langchain-ai/langgraph-swarm-py

| Field | Value |
|---|---|
| Repo | `langchain-ai/langgraph-swarm-py` |
| Pinned SHA | `de22626e3084` |
| File:line | `examples/research/src/agent/agent.ipynb:14` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `researcher_prompt` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
        40: planner_agent = create_agent(
        41:     model,
        42:     system_prompt=planner_prompt_formatted,
        43:     tools=[fetch_doc, transfer_to_researcher_agent],
        44:     name="planner_agent",
        45: )
        46: 
        47: # Researcher agent
        48: researcher_agent = create_agent(
        49:     model,
  >>>   50:     system_prompt=researcher_prompt,
        51:     tools=[fetch_doc, transfer_to_planner_agent],
        52:     name="researcher_agent",
        53: )
        54: 
        55: # Swarm
        56: checkpointer = InMemorySaver()
        57: agent_swarm = create_swarm(
        58:     [planner_agent, researcher_agent], default_active_agent="planner_agent"
        59: )
        60: app = agent_swarm.compile(checkpointer=checkpointer)
```

**Evidence (what the dynamic value resolves to):**
```
`researcher_prompt` → imported at line 3:
    3: from prompts import planner_prompt, researcher_prompt
```

---

### F31 — PurpleAILAB/Decepticon

| Field | Value |
|---|---|
| Repo | `PurpleAILAB/Decepticon` |
| Pinned SHA | `b5fa553b69b6` |
| File:line | `packages/decepticon/decepticon/agents/standard/ad_operator.py:155` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       144:             role=_ROLE,
       145:             backend=backend,
       146:             llm=llm,
       147:             fallback_models=fallback_models,
       148:             sandbox=sandbox,
       149:         )
       150:     if system_prompt is None:
       151:         system_prompt = load_prompt(_ROLE, shared=["bash"])
       152: 
       153:     return create_agent(
       154:         llm,
  >>>  155:         system_prompt=system_prompt,
       156:         tools=tools,
       157:         middleware=middleware,
       158:         name=_ROLE,
       159:     ).with_config(
       160:         {
       161:             "recursion_limit": recursion_limit or _RECURSION_LIMIT,
       162:             "callbacks": load_plugin_callbacks(role=_ROLE, backend=backend),
       163:         }
       164:     )
       165: 
       166: 
       167: # Module-level graph for LangGraph Platform (langgraph serve)
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 94 in same file:
    94:     system_prompt: str | None = None,
    95:     # ── Tuning ───────────────────────────────────────────────────────
    96:     recursion_limit: int | None = None,
    97: ):
    98:     """Build the ADOperator agent.
    99: 
```

---

### F32 — Cognitive-Stack/bull-vision-agent

| Field | Value |
|---|---|
| Repo | `Cognitive-Stack/bull-vision-agent` |
| Pinned SHA | `654d62e2f27f` |
| File:line | `app/bot/agent.py:163` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `self` |
| Pre-label FP signal | none |

**Source context:**
```python
       152:                     get_fund_listings,
       153:                     get_vcb_exchange_rate,
       154:                     get_sjc_gold_price,
       155:                     get_stocks_by_industry,
       156:                 ],
       157:                 mcp_servers=self.servers,
       158:             )
       159: 
       160:             # Create the main Bull Vision agent with trading expert as a handoff
       161:             return Agent[TradingContext](
       162:                 name="Bull Vision",
  >>>  163:                 instructions=self.get_prompt(),
       164:                 output_type=str,
       165:                 model=OpenAIChatCompletionsModel(
       166:                     model=deployment,
       167:                     openai_client=openai_client,
       168:                 ),
       169:                 tools=[
       170:                     get_stock_context,
       171:                     get_all_symbols,
       172:                     get_price_board,
       173:                     get_company_overview,
       174:                     get_balance_sheet,
       175:                     get_income_statement,
```

**Evidence (what the dynamic value resolves to):**
```
`self` → appears to be function parameter at line 69:
    69: def __init__(self, context: TradingContext, servers=None, portfolio_context: dict = None, profile_context: dict = None):
```

---

### F33 — strnad/CrewAI-Studio

| Field | Value |
|---|---|
| Repo | `strnad/CrewAI-Studio` |
| Pinned SHA | `c1dbabd48226` |
| File:line | `app/my_agent.py:58` |
| Framework | `crewai` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `self` |
| Pre-label FP signal | none |

**Source context:**
```python
        47:                 ks = next((k for k in ss.knowledge_sources if k.id == ks_id), None)
        48:                 if ks:
        49:                     try:
        50:                         knowledge_sources.append(ks.get_crewai_knowledge_source())
        51:                         valid_knowledge_source_ids.append(ks_id)
        52:                     except Exception as e:
        53:                         print(f"Error loading knowledge source {ks.id}: {str(e)}")
        54:         if knowledge_sources:
        55:             print(f"Loaded {len(knowledge_sources)} knowledge sources for agent {self.id}")
        56:             print(knowledge_sources)
        57:         return Agent(
  >>>   58:             role=self.role,
        59:             backstory=self.backstory,
        60:             goal=self.goal,
        61:             allow_delegation=self.allow_delegation,
        62:             verbose=self.verbose,
        63:             max_iter=self.max_iter,
        64:             cache=self.cache,
        65:             tools=tools,
        66:             llm=llm,
        67:             knowledge_sources=knowledge_sources if knowledge_sources else None
        68:         )
        69: 
        70:     def delete(self):
```

**Evidence (what the dynamic value resolves to):**
```
`self` → appears to be function parameter at line 11:
    11: def __init__(self, id=None, role=None, backstory=None, goal=None, temperature=None, allow_delegation=False, verbose=False, cache= None, llm_provider_model=None, max_iter=None, created_at=None, tools=None, knowledge_source_ids=None):
```

---

### F34 — AgentOps-AI/agentops

| Field | Value |
|---|---|
| Repo | `AgentOps-AI/agentops` |
| Pinned SHA | `a855a92dfaa7` |
| File:line | `examples/openai_agents/customer_service_agent.ipynb:51` |
| Framework | `langgraph` |
| Construction form | F-string (misclassified as variable; notebook source is f-string) |
| Severity | medium |
| Taint names | `RECOMMENDED_PROMPT_PREFIX` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
        89: async def on_seat_booking_handoff(context: RunContextWrapper[AirlineAgentContext]) -> None:
        90:     flight_number = f"FLT-{random.randint(100, 999)}"
        91:     context.context.flight_number = flight_number
        92: 
        93: 
        94: ### AGENTS
        95: 
        96: faq_agent = Agent[AirlineAgentContext](
        97:     name="FAQ Agent",
        98:     handoff_description="A helpful agent that can answer questions about the airline.",
  >>>   99:     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
       100:     You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
       101:     Use the following routine to support the customer.
       102:     # Routine
       103:     1. Identify the last question asked by the customer.
       104:     2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
       105:     3. If you cannot answer the question, transfer back to the triage agent.""",
       106:     tools=[faq_lookup_tool],
       107: )
       108: 
       109: seat_booking_agent = Agent[AirlineAgentContext](
```

**Evidence (what the dynamic value resolves to):**
```
`RECOMMENDED_PROMPT_PREFIX` → imported at line 37:
    37: from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX  # noqa: E402
```

---

### F35 — langchain-ai/deepagents

| Field | Value |
|---|---|
| Repo | `langchain-ai/deepagents` |
| Pinned SHA | `c160ea3eeda1` |
| File:line | `libs/partners/quickjs/langchain_quickjs/_swarm_task.py:304` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `sub` |
| Pre-label FP signal | none |

**Source context:**
```python
       293:         model = sub.model if sub.model is not None else default_model
       294:         middleware = list(sub.middleware)
       295:         spec = _AgentSpec(
       296:             model=model,
       297:             system_prompt=sub.system_prompt,
       298:             tools=sub.tools,
       299:             name=sub.name,
       300:             middleware=middleware,
       301:         )
       302:         agent = create_agent(
       303:             model=model,
  >>>  304:             system_prompt=sub.system_prompt,
       305:             tools=sub.tools,
       306:             name=sub.name,
       307:             middleware=middleware,
       308:         )
       309:         compiled[sub.name] = _CompiledAgent(agent=agent, spec=spec)
       310: 
       311:     subagent_names = [s.name for s in subs]
       312:     variant_cache = VariantCache()
       313: 
       314:     async def _run(
       315:         description: str,
       316:         subagent_type: str | None = None,
```

**Evidence (what the dynamic value resolves to):**
```
`sub` → not resolved in this file (possibly imported or set via injection)
```

---

### F36 — PurpleAILAB/Decepticon

| Field | Value |
|---|---|
| Repo | `PurpleAILAB/Decepticon` |
| Pinned SHA | `b5fa553b69b6` |
| File:line | `packages/decepticon/decepticon/agents/standard/reverser.py:149` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       138:             role=_ROLE,
       139:             backend=backend,
       140:             llm=llm,
       141:             fallback_models=fallback_models,
       142:             sandbox=sandbox,
       143:         )
       144:     if system_prompt is None:
       145:         system_prompt = load_prompt(_ROLE, shared=["bash"])
       146: 
       147:     return create_agent(
       148:         llm,
  >>>  149:         system_prompt=system_prompt,
       150:         tools=tools,
       151:         middleware=middleware,
       152:         name=_ROLE,
       153:     ).with_config(
       154:         {
       155:             "recursion_limit": recursion_limit or _RECURSION_LIMIT,
       156:             "callbacks": load_plugin_callbacks(role=_ROLE, backend=backend),
       157:         }
       158:     )
       159: 
       160: 
       161: # Module-level graph for LangGraph Platform (langgraph serve)
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 88 in same file:
    88:     system_prompt: str | None = None,
    89:     # ── Tuning ───────────────────────────────────────────────────────
    90:     recursion_limit: int | None = None,
    91: ):
    92:     """Build the Reverser agent.
    93: 
```

---

### F37 — PurpleAILAB/Decepticon

| Field | Value |
|---|---|
| Repo | `PurpleAILAB/Decepticon` |
| Pinned SHA | `b5fa553b69b6` |
| File:line | `packages/decepticon/decepticon/agents/standard/cloud_hunter.py:140` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       129:             role=_ROLE,
       130:             backend=backend,
       131:             llm=llm,
       132:             fallback_models=fallback_models,
       133:             sandbox=sandbox,
       134:         )
       135:     if system_prompt is None:
       136:         system_prompt = load_prompt(_ROLE, shared=["bash"])
       137: 
       138:     return create_agent(
       139:         llm,
  >>>  140:         system_prompt=system_prompt,
       141:         tools=tools,
       142:         middleware=middleware,
       143:         name=_ROLE,
       144:     ).with_config(
       145:         {
       146:             "recursion_limit": recursion_limit or _RECURSION_LIMIT,
       147:             "callbacks": load_plugin_callbacks(role=_ROLE, backend=backend),
       148:         }
       149:     )
       150: 
       151: 
       152: # Module-level graph for LangGraph Platform (langgraph serve)
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 79 in same file:
    79:     system_prompt: str | None = None,
    80:     # ── Tuning ───────────────────────────────────────────────────────
    81:     recursion_limit: int | None = None,
    82: ):
    83:     """Build the CloudHunter agent.
    84: 
```

---

### F38 — jkmaina/openai-agents-blueprint

| Field | Value |
|---|---|
| Repo | `jkmaina/openai-agents-blueprint` |
| Pinned SHA | `76cbbcb41a93` |
| File:line | `chapter1/14_production_example.py:140` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `instructions` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
       129:     
       130:     def __init__(self, name: str, instructions: str, **kwargs):
       131:         """
       132:         Initialize the production agent.
       133:         
       134:         Production tip: Always configure model settings explicitly.
       135:         Lower temperature (0.1-0.3) for consistent business logic,
       136:         higher temperature (0.7-0.9) for creative tasks.
       137:         """
       138:         self.agent = Agent[SessionContext](
       139:             name=name,
  >>>  140:             instructions=instructions,
       141:             model_settings=ModelSettings(
       142:                 temperature=kwargs.get('temperature', 0.3),  # Consistent responses
       143:                 max_tokens=kwargs.get('max_tokens', 1000)     # Control response length
       144:             ),
       145:             tools=[get_user_info, log_interaction],
       146:             **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
       147:         )
       148:         
       149:         # MEMORY MANAGEMENT: Store conversations per session
       150:         # Production tip: In real apps, store this in Redis/Database for persistence
       151:         self.conversations: Dict[str, List[dict]] = {}
       152:         
```

**Evidence (what the dynamic value resolves to):**
```
`instructions` → defined at line 140 in same file:
    140:             instructions=instructions,
    141:             model_settings=ModelSettings(
    142:                 temperature=kwargs.get('temperature', 0.3),  # Consistent responses
    143:                 max_tokens=kwargs.get('max_tokens', 1000)     # Control response length
    144:             ),
    145:             tools=[get_user_info, log_interaction],
```

---

### F39 — alejandro-ao/crewai-crash-course

| Field | Value |
|---|---|
| Repo | `alejandro-ao/crewai-crash-course` |
| Pinned SHA | `a11040354e24` |
| File:line | `src/agents.py:35` |
| Framework | `crewai` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `dedent` |
| Pre-label FP signal | none |

**Source context:**
```python
        24:         backstory=dedent("""\
        25:             As an Industry Analyst, your analysis will identify key trends,
        26:             challenges facing the industry, and potential opportunities that
        27:             could be leveraged during the meeting for strategic advantage."""),
        28:         verbose=True
        29:       )
        30:       
        31:     def meeting_strategy_agent(self):
        32:       return Agent(
        33:         role='Meeting Strategy Advisor',
        34:         goal='Develop talking points, questions, and strategic angles for the meeting',
  >>>   35:         backstory=dedent("""\
        36:             As a Strategy Advisor, your expertise will guide the development of
        37:             talking points, insightful questions, and strategic angles
        38:             to ensure the meeting's objectives are achieved."""),
        39:         verbose=True
        40:       )
        41:       
        42:     def summary_and_briefing_agent(self): 
        43:       return Agent(
        44:         role='Briefing Coordinator',
        45:         goal='Compile all gathered information into a concise, informative briefing document',
        46:         backstory=dedent("""\
        47:             As the Briefing Coordinator, your role is to consolidate the research,
```

**Evidence (what the dynamic value resolves to):**
```
`dedent` → imported at line 1:
    1: from textwrap import dedent
```

---

### F40 — langchain-ai/langgraph-swarm-py

| Field | Value |
|---|---|
| Repo | `langchain-ai/langgraph-swarm-py` |
| Pinned SHA | `de22626e3084` |
| File:line | `examples/research/src/agent/agent.py:29` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | high |
| Taint names | `PLANNER_PROMPT_FORMATTED` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
        18:     description="Transfer the user to the researcher_agent to perform research and implement the solution to the user's request.",
        19: )
        20: 
        21: # LLMS.txt
        22: LLMS_TXT = "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt"
        23: NUM_URLS = 3
        24: PLANNER_PROMPT_FORMATTED = planner_prompt.format(llms_txt=LLMS_TXT, num_urls=NUM_URLS)
        25: 
        26: # Planner agent
        27: planner_agent = create_agent(
        28:     model,
  >>>   29:     system_prompt=PLANNER_PROMPT_FORMATTED,
        30:     tools=[fetch_doc, transfer_to_researcher_agent],
        31:     name="planner_agent",
        32: )
        33: 
        34: # Researcher agent
        35: researcher_agent = create_agent(
        36:     model,
        37:     system_prompt=researcher_prompt,
        38:     tools=[fetch_doc, transfer_to_planner_agent],
        39:     name="researcher_agent",
        40: )
        41: 
```

**Evidence (what the dynamic value resolves to):**
```
`PLANNER_PROMPT_FORMATTED` → defined at line 24 in same file:
    24: PLANNER_PROMPT_FORMATTED = planner_prompt.format(llms_txt=LLMS_TXT, num_urls=NUM_URLS)
    25: 
    26: # Planner agent
    27: planner_agent = create_agent(
    28:     model,
    29:     system_prompt=PLANNER_PROMPT_FORMATTED,
```

---

### F41 — Shaurya-Sethi/circuitron

| Field | Value |
|---|---|
| Repo | `Shaurya-Sethi/circuitron` |
| Pinned SHA | `6e2be932deab` |
| File:line | `circuitron/agents.py:176` |
| Framework | `openai-agents` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       165:     model_settings = ModelSettings(
       166:         tool_choice=_tool_choice_for_mcp(settings.code_generation_model)
       167:     )
       168: 
       169:     prompt = (
       170:         CODE_GENERATION_PROMPT
       171:         if settings.footprint_search_enabled
       172:         else CODE_GENERATION_PROMPT_NO_FOOTPRINT
       173:     )
       174:     return Agent(
       175:         name="Circuitron-Coder",
  >>>  176:         instructions=prompt,
       177:         model=settings.code_generation_model,
       178:         output_type=CodeGenerationOutput,
       179:         mcp_servers=[mcp_manager.get_server()],
       180:         model_settings=model_settings,
       181:     )
       182: 
       183: 
       184: def create_code_validation_agent() -> Agent:
       185:     """Create and configure the Code Validation Agent."""
       186:     model_settings = ModelSettings(
       187:         tool_choice=_tool_choice_for_mcp(settings.code_validation_model)
       188:     )
```

**Evidence (what the dynamic value resolves to):**
```
`prompt` → defined at line 109 in same file:
    109:     prompt = PARTFINDER_PROMPT
    110:     if footprint_search_enabled:
    111:         tools.append(search_kicad_footprints)
    112:     else:
    113:         prompt = PARTFINDER_PROMPT_NO_FOOTPRINT
    114: 
```

---

### F42 — bytedance/deer-flow

| Field | Value |
|---|---|
| Repo | `bytedance/deer-flow` |
| Pinned SHA | `7679f21edf3f` |
| File:line | `backend/packages/harness/deerflow/agents/lead_agent/agent.py:501` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `apply_prompt_template`, `subagent_enabled`, `max_concurrent_subagents`, `resolved_app_config`, `set`, `setup` |
| Pre-label FP signal | none |

**Source context:**
```python
       490:     skills_for_tool_policy = _load_enabled_skills_for_tool_policy(available_skills, app_config=resolved_app_config)
       491: 
       492:     if is_bootstrap:
       493:         # Special bootstrap agent with minimal prompt for initial custom agent creation flow
       494:         raw_tools = get_available_tools(model_name=model_name, subagent_enabled=subagent_enabled, app_config=resolved_app_config) + [setup_agent]
       495:         filtered = filter_tools_by_skill_allowed_tools(raw_tools, skills_for_tool_policy)
       496:         final_tools, setup = _assemble_deferred(filtered, enabled=resolved_app_config.tool_search.enabled)
       497:         return create_agent(
       498:             model=create_chat_model(name=model_name, thinking_enabled=thinking_enabled, app_config=resolved_app_config, attach_tracing=False),
       499:             tools=final_tools,
       500:             middleware=_build_middlewares(config, model_name=model_name, app_config=resolved_app_config, deferred_setup=setup),
  >>>  501:             system_prompt=apply_prompt_template(
       502:                 subagent_enabled=subagent_enabled,
       503:                 max_concurrent_subagents=max_concurrent_subagents,
       504:                 available_skills=set(["bootstrap"]),
       505:                 app_config=resolved_app_config,
       506:                 deferred_names=setup.deferred_names,
       507:             ),
       508:             state_schema=ThreadState,
       509:         )
       510: 
       511:     # Custom agents can update their own SOUL.md / config via update_agent.
       512:     # The default agent (no agent_name) does not see this tool.
       513:     extra_tools = [update_agent] if agent_name else []
```

**Evidence (what the dynamic value resolves to):**
```
`apply_prompt_template` → imported at line 30:
    30: from deerflow.agents.lead_agent.prompt import apply_prompt_template
`subagent_enabled` → defined at line 339 in same file:
    339:     subagent_enabled = cfg.get("subagent_enabled", False)
    340:     if subagent_enabled:
    341:         max_concurrent_subagents = cfg.get("max_concurrent_subagents", 3)
    342:         middlewares.append(SubagentLimitMiddleware(max_concurrent=max_concurrent_subagents))
    343: 
    344:     # LoopDetectionMiddleware — detect and break repetitive tool call loops
`max_concurrent_subagents` → defined at line 341 in same file:
    341:         max_concurrent_subagents = cfg.get("max_concurrent_subagents", 3)
    342:         middlewares.append(SubagentLimitMiddleware(max_concurrent=max_concurrent_subagents))
    343: 
    344:     # LoopDetectionMiddleware — detect and break repetitive tool call loops
    345:     loop_detection_config = resolved_app_config.loop_detection
    346:     if loop_detection_config.enabled:
```

---

### F43 — kid0317/crewai_mas_demo

| Field | Value |
|---|---|
| Repo | `kid0317/crewai_mas_demo` |
| Pinned SHA | `d5cfc79d3f61` |
| File:line | `m5l30/demo.py:107` |
| Framework | `crewai` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `backstory` |
| Pre-label FP signal | example/tutorial-dir |

**Source context:**
```python
        96: 
        97:     model_name = os.environ.get("AGENT_MODEL", "qwen-plus")
        98:     base_url = os.environ.get(
        99:         "OPENAI_API_BASE",
       100:         "https://dashscope.aliyuncs.com/compatible-mode/v1",
       101:     )
       102:     llm = LLM(model=model_name, base_url=base_url)
       103: 
       104:     agent = Agent(
       105:         role="数字员工",
       106:         goal="根据用户请求，调用合适的 Skill 高效完成任务",
  >>>  107:         backstory=backstory,
       108:         llm=llm,
       109:         verbose=True,
       110:         tools=[skill_tool],
       111:     )
       112: 
       113:     task = Task(
       114:         description=(
       115:             f"用户请求：{task_desc}\n\n"
       116:             "请先调用 skill_loader 工具加载合适的 Skill 获取工作指引，"
       117:             "然后严格按照指引完成任务。"
       118:         ),
       119:         expected_output="按照 Skill 指引产出的完整交付物",
```

**Evidence (what the dynamic value resolves to):**
```
`backstory` → defined at line 89 in same file:
    89:     backstory = build_bootstrap_prompt(WORKSPACE_DIR)
    90: 
    91:     skill_tool = SkillLoaderTool(
    92:         skills_dir=str(SKILLS_DIR),
    93:         sandbox_mcp_url=SANDBOX_MCP_URL,
    94:         sandbox_mount_desc=SANDBOX_MOUNT_DESC,
```

---

### F44 — pipeshub-ai/pipeshub-ai

| Field | Value |
|---|---|
| Repo | `pipeshub-ai/pipeshub-ai` |
| Pinned SHA | `18c880291ceb` |
| File:line | `pipeshub-ai/backend/python/app/modules/agents/deep/sub_agent.py:508` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       497:                 "duration_ms": (time.perf_counter() - start_time) * 1000,
       498:             }
       499: 
       500:         log.info("Sub-agent %s: %d tools loaded", task_id, len(tools))
       501: 
       502:         # Create isolated agent
       503:         from langchain.agents import create_agent
       504: 
       505:         agent = create_agent(
       506:             state["llm"],
       507:             tools,
  >>>  508:             system_prompt=system_prompt,
       509:         )
       510: 
       511:         # Build ISOLATED messages - only the task, not full conversation
       512:         messages = [HumanMessage(content=task_desc)]
       513: 
       514:         # Inject user attachment blocks using simple PDF extraction for sub-agents
       515:         sub_agent_att_blocks = await _resolve_sub_agent_attachments(state)
       516:         if sub_agent_att_blocks:
       517:             from app.utils.attachment_utils import inject_attachment_blocks  # noqa: PLC0415
       518:             inject_attachment_blocks(messages, sub_agent_att_blocks)
       519: 
       520:         # Create streaming callback for tool events
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 478 in same file:
    478:         system_prompt = _build_system_message_with_context(
    479:             SUB_AGENT_SYSTEM_PROMPT,
    480:             {
    481:                 "task_description": task_desc,
    482:                 "task_scope_block": _format_task_scope_block(task),
    483:                 "tool_schemas": tool_schemas_text or "No tool schemas available.",
```

---

### F45 — PurpleAILAB/Decepticon

| Field | Value |
|---|---|
| Repo | `PurpleAILAB/Decepticon` |
| Pinned SHA | `b5fa553b69b6` |
| File:line | `packages/decepticon/decepticon/agents/standard/wireless_operator.py:115` |
| Framework | `langgraph` |
| Construction form | Plain variable |
| Severity | medium |
| Taint names | `system_prompt` |
| Pre-label FP signal | none |

**Source context:**
```python
       104:             skill_sources=[*_SKILL_SOURCES, *benchmark_skill_sources()],
       105:             backend=backend,
       106:             llm=llm,
       107:             fallback_models=fallback_models,
       108:             sandbox=sandbox,
       109:         )
       110:     if system_prompt is None:
       111:         system_prompt = load_prompt(_ROLE, shared=["bash"])
       112: 
       113:     return create_agent(
       114:         llm,
  >>>  115:         system_prompt=system_prompt,
       116:         tools=tools,
       117:         middleware=middleware,
       118:         name=_ROLE,
       119:     ).with_config(
       120:         {
       121:             "recursion_limit": recursion_limit or _RECURSION_LIMIT,
       122:             "callbacks": load_plugin_callbacks(role=_ROLE, backend=backend),
       123:         }
       124:     )
       125: 
       126: 
       127: # Module-level graph for LangGraph Platform (langgraph serve)
```

**Evidence (what the dynamic value resolves to):**
```
`system_prompt` → defined at line 81 in same file:
    81:     system_prompt: str | None = None,
    82:     recursion_limit: int | None = None,
    83: ):
    84:     """Build the WirelessOperator agent."""
    85:     if llm is None or fallback_models is None:
    86:         factory = LLMFactory()
```

---

## Appendix: draw metadata

| Parameter | Value |
|---|---|
| Random seed | 42 |
| Per-repo cap | 5 |
| Population | 148 IG002 findings, main engine 031e781 |
| Stratum: callable/opaque | 8 drawn / 29 in population |
| Stratum: f-string | 12 drawn / 30 in population |
| Stratum: plain variable | 25 drawn / 89 in population |

**Realized per-repo counts in sample:**

| Repo | N |
|---|---|
| study8677/OpenCMO | 5 |
| langchain-ai/langgraph-swarm-py | 5 |
| PurpleAILAB/Decepticon | 5 |
| PacktPublishing/Building-Agents-with-OpenAI-Agents-SDK | 3 |
| jkmaina/openai-agents-blueprint | 3 |
| serialx/vibecore | 2 |
| liangdabiao/crewai_stock_analysis_system | 2 |
| alexfazio/viral-clips-crew | 2 |
| Shaurya-Sethi/circuitron | 2 |
| bytedance/deer-flow | 2 |
| AbubakrChan/crewai-UI-business-product-launch | 1 |
| hellotinah/financial_agent | 1 |
| xark-argo/argo | 1 |
| LangGraph-GUI/CrewAI-GUI-Qt | 1 |
| szczyglis-dev/py-gpt | 1 |
| Nishmithasshett/LLM-Agent | 1 |
| evalops/agent-harness | 1 |
| Cognitive-Stack/bull-vision-agent | 1 |
| strnad/CrewAI-Studio | 1 |
| AgentOps-AI/agentops | 1 |
| langchain-ai/deepagents | 1 |
| alejandro-ao/crewai-crash-course | 1 |
| kid0317/crewai_mas_demo | 1 |
| pipeshub-ai/pipeshub-ai | 1 |