# IG001 Findings — Pre-labeling Dossier

**Corpus scan date:** 2026-06-10  
**Analyzer version:** v0.2 (post-PR #5), branch `fix-3-function-local-binding`  
**Corpus:** SHA-pinned (126 repos). Scan produced 6 IG001 findings across 3 repos.  
**SHA mismatch:** `chopratejas/headroom` (local HEAD ≠ pinned). None of the 6 findings
are from that repo; all come from correctly-pinned checkouts.

Labels are NOT assigned here. This dossier assembles the evidence the labeling
methodology (§3.1) needs to make TP/FP/AMBIGUOUS calls. Labeling is done separately.

---

## Finding #1

**Repo:** `tonykipkemboi/crewai-gmail-automation`  
**Pinned SHA:** `0946e1747effa5930d133a7fb3febdd537f2ad6c`  
**File:line:** `src/gmail_crew_ai/crew.py:80`  
**Scanner severity:** LOW

### Agent

```python
# crew.py:78–84
@agent
def organizer(self) -> Agent:
    """The email organization agent."""
    return Agent(
        config=self.agents_config['organizer'],
        tools=[GmailOrganizeTool(), FileReadTool()],
        llm=self.llm,
    )
```

**Framework:** CrewAI  
**Agent name (from YAML):** `organizer`  
**Role (agents.yaml):** "Email Organization Specialist"  
**Goal:** "Apply Gmail's organizational features (stars, labels, priority markers) consistently and effectively based on email categorization"

### Source tool

**Name:** `GmailOrganizeTool`  
**Taxonomy match:** pattern `gmail_organize`, classification `BOTH`, trust_of_output `mixed`, privilege `1`  
**Why scanner treats it as source:** `ToolClassification.BOTH` → `Tool.is_source = True`
(`ir.py:76`). Scanner's `_select_worst_source` selects it first because it appears
before `FileReadTool` in the tools list (same trust/priv score; sort is stable).

**Actual implementation** (`tools/gmail_tools.py:457–505`):

```python
class GmailOrganizeTool(GmailToolBase):
    name: str = "organize_email"
    description: str = "Organizes emails using Gmail's priority features based on category and priority"

    def _run(self, email_id: str, category: str, priority: str,
             should_star: bool = False, labels: List[str] = None) -> str:
        # Connects to Gmail via IMAP
        mail = self._connect()
        mail.select("INBOX")
        # Applies flags/labels based on agent-supplied parameters
        if category == "Urgent Response Needed" and priority == "High":
            if should_star:
                mail.store(email_id, '+FLAGS', '\\Flagged')
            mail.store(email_id, '+FLAGS', '\\Important')
        for label in labels:
            mail.create(label)
            mail.store(email_id, '+X-GM-LABELS', label)
        return f"Email organized: Starred={should_star}, Labels={labels}"
```

The tool receives all parameters from the agent (category, priority, labels, should_star)
and applies IMAP writes. It does NOT read email body content; it does NOT return email
body content. Return value is a static status string.

Note: the agent also has `FileReadTool`, which the organization_task description
explicitly uses first: *"read the categorization report from
`output/categorization_report.json` using the `FileReadTool`"* — a file produced by
the upstream categorizer agent (which processed actual email bodies).

### Sink tool

**Name:** `GmailOrganizeTool` (same tool — BOTH classification)  
**Taxonomy match:** pattern `gmail_organize`, classification `BOTH`, privilege `1`, reversible `True`  
**Actual behavior as sink:** applies IMAP labels/stars/flags to a specific email by ID.
Privilege 1 (own-state write). Reversible (labels/flags can be removed).

### Gate

No `requires_approval` on `GmailOrganizeTool`. No `interrupts_before` in the `Crew`
(Process.sequential, no HITL). Crew config:

```python
return Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True
)
```

### Agent wiring

The organization_task description (tasks.yaml) says:

> First, read the categorization report from `output/categorization_report.json` using
> the `FileReadTool`. For each email, organize it using Gmail's priority features with
> the `organize_email` tool.

Plausible data path: `FileReadTool` reads `categorization_report.json` (content derived
from upstream email processing) → LLM decides category/priority/labels → `GmailOrganizeTool`
applies them. The scanner reports `GmailOrganizeTool` as both source and sink (not
`FileReadTool` as source), because BOTH-classified tools satisfy `is_source=True`.

---

## Finding #2

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**File:line:** `m1l2/m1l2_agent.py:46`  
**Scanner severity:** HIGH

### Agent

```python
# m1l2_agent.py:46–91
searcher = Agent(
    role="网络调研专家",
    goal="通过系统化的网络搜索和信息提取，完成用户指定的调研任务，并生成结构化的Markdown格式调研报告写入文件",
    backstory="""...必须使用网页抓取工具（ScrapeWebsiteTool）深入抓取这些网页的完整内容...""",
    tools=[ScrapeWebsiteTool(), BaiduSearchTool(), FileWriterTool()],
    memory=True,
    max_iter=100,
    llm=aliyun_llm.AliyunLLM(model="qwen-plus", ...),
)
```

**Framework:** CrewAI  
**Agent name:** `searcher` (role: 网络调研专家 — "Web Research Expert")

### Source tool

**Name:** `ScrapeWebsiteTool`  
**Taxonomy match:** pattern `scrape`, classification `SOURCE`, trust_of_output `untrusted`, privilege `0`

**Actual behavior:** Standard `crewai_tools.ScrapeWebsiteTool` — given a URL, fetches and
returns the full HTML/text content of that page. Entire response is externally controlled
by whoever operates or injects content into the target URL.

Backstory explicitly instructs the agent to use it:

> "必须使用网页抓取工具（ScrapeWebsiteTool）深入抓取这些网页的完整内容"  
> ("you MUST use the web scraping tool (ScrapeWebsiteTool) to deeply scrape the full
> content of these web pages")

### Sink tool

**Name:** `FileWriterTool`  
**Taxonomy match:** pattern `write_file`, classification `SINK`, privilege `2`, reversible `True`

**Actual behavior:** Standard `crewai_tools.FileWriterTool` — writes agent-supplied text
to a local file at a path chosen by the agent. Privilege 2 (own-system write).

### Gate

No `requires_approval`. No `interrupts_before`. Single-agent `Crew(verbose=True)` with no
HITL configuration.

### Agent wiring

Task `expected_output`:

> "完整的Markdown格式研究报告并写入文件...输出文件：`{主题}-最终报告.md`"

`ScrapeWebsiteTool` returns full web page text → LLM synthesizes into a research report →
`FileWriterTool` writes the report to disk. The backstory mandates scraping at least 3–5
pages per search result; scraped content flows directly through the LLM context into the
file output.

---

## Finding #3

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**File:line:** `m3l19/m3l19_context_mgmt.py:281`  
**Scanner severity:** HIGH

### Agent

```python
# m3l19_context_mgmt.py:279–299
@agent
def assistant_agent(self) -> Agent:
    return Agent(
        role="XiaoPaw 个人助手",
        goal="帮助晓寒高效完成各类任务，严谨、结果导向",
        backstory=build_bootstrap_prompt(WORKSPACE_DIR),
        llm=aliyun_llm.AliyunLLM(model="qwen3.6-max-preview", ...),
        tools=[
            BaiduSearchTool(),
            ScrapeWebsiteTool(),
            FileWriterTool(),
            FileReadTool(),
            FixedDirectoryReadTool(directory=str(WORKSPACE_DIR)),
        ],
        verbose=True,
        max_iter=50,
    )
```

**Framework:** CrewAI  
**Agent name:** `XiaoPaw 个人助手` (Personal Assistant)

### Source tool

**Name:** `BaiduSearchTool`  
**Taxonomy match:** pattern `baidu_search`, classification `SOURCE`, trust_of_output `untrusted`, privilege `0`

**Actual implementation** (`tools/baidu_search.py:119–342`):

```python
class BaiduSearchTool(BaseTool):
    name: str = "search_web"
    # Makes a live HTTP POST to Baidu Qianfan API:
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    # Returns formatted search results: title, URL, content summaries
    # from real Baidu web search. Content is externally-authored.
```

The tool registers itself as `name = "search_web"` but is in fact a Baidu API wrapper.
Returns a formatted string of web page titles, URLs, and content summaries scraped from
external sites — fully externally-authored content.

### Sink tool

**Name:** `FileWriterTool`  
**Taxonomy match:** pattern `write_file`, classification `SINK`, privilege `2`, reversible `True`  
**Actual behavior:** crewai_tools standard file writer.

### Gate

The `@before_llm_call` hook (`before_llm_hook`) does session management: restores history,
prunes old tool results, optionally compresses context. It does NOT intercept or gate tool
calls. No `requires_approval`, no `interrupts_before`.

```python
@before_llm_call
def before_llm_hook(self, context: LLMCallHookContext) -> bool | None:
    # prune_tool_results + maybe_compress only — returns None (continue)
    prune_tool_results(context.messages)
    maybe_compress(context.messages, context)
    return None
```

### Agent wiring

`DEMO_ROUNDS[0]`:

> "帮我调研极客时间平台上多智能体相关课程的现状，生成一份调研报告保存到文件"  
> ("Help me research the current state of multi-agent courses on the GeekTime platform,
> generate a research report and save to file")

`BaiduSearchTool` returns web search results → LLM synthesizes them into a report →
`FileWriterTool` writes the file. Task expected_output: "针对用户请求的完整回复" (complete
reply) — in rounds 1 and 3 this explicitly includes file writing.

---

## Finding #4

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**File:line:** `m1l3/m1l3_multi_agent.py:92`  
**Scanner severity:** MEDIUM

### Agent

```python
# m1l3_multi_agent.py:92–177
writer = Agent(
    role="报告撰写研究员",
    goal="按照研究步骤和大纲，撰写高质量的研究报告，确保信息准确、引用完整、格式规范",
    backstory="""...
    1. 初始化阶段：读取研究专家生成的任务步骤和报告大纲
    2. 分步研究撰写：委托网络搜索专家收集信息，撰写步骤报告
    3. 报告整合：读取大纲和步骤报告文件，整合成最终报告，写入文件
    ...""",
    tools=[FileWriterTool(), FileReadTool(), FixedDirectoryReadTool()],
    allow_delegation=True,
    memory=True,
    max_iter=100,
    llm=aliyun_llm.AliyunLLM(model="qwen-plus", ...),
)
```

**Framework:** CrewAI  
**Agent name:** `writer` (role: 报告撰写研究员 — "Report Writer/Researcher")

### Source tool

**Name:** `FileReadTool`  
**Taxonomy match:** pattern `read_file`, classification `SOURCE`, trust_of_output `mixed`, privilege `1`

**Actual behavior:** crewai_tools standard file reader — reads content from any local file
path the agent specifies. The files it reads in this workflow:
- The researcher agent's outline/task-steps output (agent-generated)
- Intermediate step-report `.md` files (written by this same writer agent)
- Those step reports are populated with search results obtained by delegating to the
  `searcher` agent (`allow_delegation=True`), which uses `BaiduSearchTool` and
  `ScrapeWebsiteTool`

The writer agent itself does not hold `BaiduSearchTool` or `ScrapeWebsiteTool`; it
obtains external content indirectly via delegation to the `searcher` agent.

### Sink tool

**Name:** `FileWriterTool`  
**Taxonomy match:** pattern `write_file`, classification `SINK`, privilege `2`, reversible `True`  
**Actual behavior:** crewai_tools file writer.

### Gate

`allow_delegation=True` (to editor agent for review). No `requires_approval`, no
`interrupts_before`, no HITL before file writes.

### Agent wiring

The writer backstory step 2:

> "委托网络搜索专家：明确告知需要搜索的信息点，要求快速高效地返回结构化的信息列表"  
> ("Delegate to the network search expert…")

And step 4:

> "使用FixedDirectoryReadTool读取当前目录, 读取报告大纲文件和所有步骤报告文件, 整合…写入文件"

Path: writer delegates to searcher (BaiduSearchTool/ScrapeWebsiteTool) → searcher results
are written to step-report files → writer uses `FileReadTool` to read those files →
LLM consolidates → `FileWriterTool` writes final report.  
The `FileReadTool` content in this agent's own context is the intermediate files that
contain externally-sourced search results.

---

## Finding #5

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**File:line:** `m2l8/m2l8_tools_call.py:127`  
**Scanner severity:** MEDIUM

### Agent

```python
# m2l8_tools_call.py:127–180
crontab_manager_agent = Agent(
    role="定时任务管理专家",
    goal="根据用户需求，记录和维护定时任务情况",
    backstory="""你是一位定时任务记录专家...
    1. 根据用户的需求，生成crontab语法的定时任务，写入CRONTAB.md
    2. 当用户询问或修改定时任务时，读取CRONTAB.md，根据需求回答或调整
    ...""",
    tools=[FileWriterTool(), FileReadTool()],
    verbose=True,
    allow_delegation=False,
    llm=aliyun_llm.AliyunLLM(model="qwen-plus", ...),
)
```

**Framework:** CrewAI  
**Agent name:** `crontab_manager_agent` (role: 定时任务管理专家 — "Cron Task Manager")

### Source tool

**Name:** `FileReadTool`  
**Taxonomy match:** pattern `read_file`, classification `SOURCE`, trust_of_output `mixed`, privilege `1`

**Actual behavior:** reads the content of `CRONTAB.md` — a file containing crontab
entries written previously by this same agent or initialized from user input.

The file's content is agent-generated crontab syntax derived from the `{user_input}`
interpolation in the task description:

```python
base_task = Task(
    description="根据用户的需求，完成对定时任务的记录和维护。用户的输入为：{user_input}",
    ...
)
```

Example inputs (from kickoff calls):

```python
crew.kickoff(inputs={"user_input": "帮我创建一个周一到周五每天早上9点的任务，..."})
crew.kickoff(inputs={"user_input": "查一下我现在的定时任务"})
crew.kickoff(inputs={"user_input": "帮我把查询阿里股价的任务改到9点半"})
```

### Sink tool

**Name:** `FileWriterTool`  
**Taxonomy match:** pattern `write_file`, classification `SINK`, privilege `2`, reversible `True`  
**Actual behavior:** writes updated crontab entries to `CRONTAB.md`.

### Gate

The `@before_tool_call` hook (`file_path_hook`) intercepts `FileWriterTool` and
`FileReadTool` calls to validate and redirect file paths to a per-user workspace:

```python
@before_tool_call
def file_path_hook(context):
    tools_list = ["File Writer Tool", "Read a file's content"]
    if context.tool_name in tools_list:
        # path traversal check: rejects paths outside WORKSPACE_BASE_PATH / uid
        original_file_path_abs.relative_to(base_path_abs)  # raises ValueError if outside
        ...
    return None  # continue execution
```

This is a **path-traversal security control**, NOT a human-in-the-loop gate. It does not
prompt a human or pause for approval; it redirects the path and lets the tool call proceed.  
No `requires_approval`, no `interrupts_before`.

### Agent wiring

The agent reads and writes a single file (`CRONTAB.md`) that stores user-provided cron
task descriptions. `FileReadTool` reads existing cron entries → LLM processes them along
with the new `user_input` → `FileWriterTool` writes the updated file.  
The `{user_input}` variable is the direct user request injected into the task description,
not content from an external web source.

---

## Finding #6

**Repo:** `lesteroliver911/llamaindex-agentworkflow-browse-agent`  
**Pinned SHA:** `71bf390641ca16a7c5846d3811ffbbc3812ec161`  
**File:line:** `main.py:75`  
**Scanner severity:** HIGH

### Agent

```python
# main.py:75–85
browser_agent = FunctionAgent(
    name="BrowserAgent",
    description="Agent capable of web browsing and interaction",
    system_prompt=(
        "You are a web browsing agent that can navigate websites, click elements, "
        "and search for text on pages. You can also take screenshots of the current page."
    ),
    llm=llm,
    tools=[navigate_to, click_element, search_text, take_screenshot],
    can_handoff_to=["AnalysisAgent"],
)
```

**Framework:** LlamaIndex `AgentWorkflow` / `FunctionAgent`  
**Agent name:** `BrowserAgent`

### Source tool

**Name:** `navigate_to`  
**Taxonomy match:** pattern `navigate_to`, classification `SOURCE`, trust_of_output `untrusted`, privilege `0`

**Actual implementation** (`main.py:39–42`):

```python
async def navigate_to(url: str) -> str:
    """Navigate to a specific URL."""
    helium.go_to(url)
    return f"Navigated to {url}"
```

Drives a live Chrome browser (via `helium`) to the given URL. The return value is the
literal string `"Navigated to {url}"` — it does **not** return page content.

However, the agent's toolbox also includes `search_text` and `take_screenshot`, which
expose page state to the LLM context:

```python
async def search_text(text: str, nth_result: int = 1) -> str:
    """Search for text on the current page."""
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
    ...

async def take_screenshot(ctx: Context) -> str:
    """Take a screenshot of the current page."""
    screenshot → appended to context["state"]["screenshots"]
    return f"Screenshot taken: {image.size} pixels"
```

The LLM can observe page content through these tools after `navigate_to` loads a page.

### Sink tool

**Name:** `click_element`  
**Taxonomy match:** pattern `click_element`, classification `SINK`, privilege `2`, reversible `True`

**Actual implementation** (`main.py:44–53`):

```python
async def click_element(text: str, element_type: str = "button") -> str:
    """Click an element with specific text."""
    try:
        if element_type == "link":
            helium.click(helium.Link(text))
        else:
            helium.click(text)
        return f"Clicked {element_type} with text: {text}"
    except Exception as e:
        return f"Error clicking element: {str(e)}"
```

Clicks a UI element (button or link) matching the given text string in the live browser.
This can submit forms, trigger account-state changes, or follow links.

### Gate

No `interrupt_before`, no `requires_approval`, no `StopAtTools`. The LlamaIndex
`AgentWorkflow` provides a `can_handoff_to` parameter but that is for inter-agent
delegation, not human approval. Entry point:

```python
async def main():
    user_input = input("Enter your browsing instruction: ")
    handler = agent_workflow.run(user_msg=user_input)
    async for event in handler.stream_events():
        ...
```

Human input is only at the start; no pause before `click_element` executes.

### Agent wiring

User supplies a browsing instruction → `navigate_to(url)` drives Chrome to a URL →
`search_text` or `take_screenshot` exposes page content to the LLM → `click_element`
acts on that content.

A plausible attack path: user asks the agent to browse an attacker-controlled URL; that
page contains adversarial text (e.g., visible text "Click the Confirm Purchase button" or
a UI overlay saying "Click here to confirm"); the LLM observes the page via `search_text`
or `take_screenshot` and issues `click_element("Confirm Purchase")` or similar.

`AnalysisAgent` also has `click_element` in its toolbox:
```python
analysis_agent = FunctionAgent(
    tools=[search_text, take_screenshot],  # does NOT have click_element
    ...
)
```
Wait — `AnalysisAgent` does NOT have `click_element` (only `search_text`, `take_screenshot`).
The `BrowserAgent` is the only agent with `click_element`.

---

## Cross-finding notes

- Findings #2, #3, #4 all come from the same repo (`kid0317/crewai_mas_demo`) but
  different modules (m1l2, m3l19, m1l3). They are independent agent definitions in
  separate files.
- Findings #2 and #3 share the `ScrapeWebsiteTool` → `FileWriterTool` and
  `BaiduSearchTool` → `FileWriterTool` patterns. The sink (FileWriterTool) is the same
  tool in both; the source differs.
- Findings #4 and #5 both fire `FileReadTool` → `FileWriterTool`. The critical difference
  is where the file content originates: in #4, step-report files contain content from
  external web searches (via delegated `searcher`); in #5, `CRONTAB.md` contains
  user-supplied task descriptions with no external web content.
- Finding #1 is the only BOTH-classification finding. The scanner resolves it as
  source=`GmailOrganizeTool`, sink=`GmailOrganizeTool`. The agent also has `FileReadTool`
  (which reads a categorization report derived from email content) — whether that tool
  is the more relevant source for criterion (a) is a labeling judgment.
- Finding #6 is the only non-CrewAI finding (LlamaIndex `AgentWorkflow`).
