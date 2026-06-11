# IG001 Labels — First Labeling Pass

**Labeling date:** 2026-06-10  
**Analyzer version:** v0.2 (post-PR #5), frozen for evaluation  
**Methodology:** `docs/eval/LABELING_METHODOLOGY.md` §3.1  
**Labeler:** Sanjay Belaturu Krishnegowda (single labeler)  
**Dossier source:** `eval/ig001_findings_for_labeling.md` (commit `80fa4732`)

---

## Results summary

| Label | Count |
|---|---|
| TP | 4 |
| FP | 1 |
| AMBIGUOUS | 1 |
| **Total** | **6** |

**Precision (labelable N=5, AMBIGUOUS excluded):** 4/5 = 0.80

**Caveat:** N=5 is too small to treat 0.80 as a stable precision rate.
Reported as raw counts only. Single labeler; no second-reviewer confirmation at this
stage. Confidence interval is wide at this N. Confirmed TPs (PoC/maintainer disclosure)
per §7 are a separate step.

---

## Finding #1 — FP

**Repo:** `tonykipkemboi/crewai-gmail-automation`  
**Pinned SHA:** `0946e1747effa5930d133a7fb3febdd537f2ad6c`  
**Agent:** `organizer` (CrewAI)  
**Source tool:** `GmailOrganizeTool` — pattern `gmail_organize`, classification `BOTH`  
**Sink tool:** `GmailOrganizeTool` — same tool, classification `BOTH`, privilege 1, reversible

**Label: FP**

**Reasoning:**

Criterion (a) fails. The `BOTH` classification causes `GmailOrganizeTool` to satisfy
`is_source = True`, but the tool's actual `_run()` method does not return externally-
influenceable content:

```python
return f"Email organized: Starred={should_star}, Labels={labels}"
```

The return value is a static status string constructed entirely from the agent's own
inputs (category, priority, should_star, labels). The tool never reads email body
content; it only applies IMAP flags/labels that the agent supplied. An attacker cannot
inject a payload through this tool's output — there is no externally-authored text
flowing back into the LLM context via this tool's source-side.

This is a false positive arising from the `BOTH` classification being coarser than the
tool's actual source behavior. The taxonomy rationale for `gmail_organize` is "reads
email metadata (untrusted SOURCE) and archives/labels/moves messages (SINK)" — but the
implementation does not read metadata back through its return value; the source-side
behavior exists only in the sense that it connects to Gmail IMAP, not in the sense that
it returns attacker-controllable content to the LLM.

Note: the agent also holds `FileReadTool` (which reads `output/categorization_report.json`,
a file derived from email content). If `FileReadTool` had been the scanner's selected
source, criterion (a) would be closer to satisfied — but the scanner's `_select_worst_source`
picked `GmailOrganizeTool` first (same trust/priv score, appears first in the tools list),
so the filed finding is on GmailOrganizeTool-as-source.

Criteria (b) and (c): priv=1 passes the privilege threshold; no gate is present. But (a)
failure is sufficient to call FP under methodology §3.1.

**Known limitation triggered:** see `eval/known_limitations.md` — BOTH-classification
single-tool co-membership FP.

---

## Finding #2 — TP

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**Agent:** `searcher` (role: 网络调研专家, m1l2/m1l2_agent.py:46) — CrewAI  
**Source tool:** `ScrapeWebsiteTool` — pattern `scrape`, classification `SOURCE`, trust `untrusted`, privilege 0  
**Sink tool:** `FileWriterTool` — pattern `write_file`, classification `SINK`, privilege 2, reversible

**Label: TP**

**Reasoning:**

(a) ✓ — `ScrapeWebsiteTool` fetches the full HTML/text content of any URL the agent
navigates to. The page content is entirely externally-authored and attacker-controllable
if the attacker controls or can inject into any page the agent visits. Trust `untrusted`.

(b) ✓ — `FileWriterTool` writes to the local filesystem. Privilege 2. The agent's task
explicitly produces a file as final output (`{主题}-最终报告.md`). Privilege threshold
met.

(c) ✓ — No gate. No `requires_approval` on `FileWriterTool`. No `interrupts_before` in
the single-agent `Crew`. The backstory mandates scraping at least 3–5 pages per search;
scraped content flows directly into the file output without any human checkpoint.

Wiring is direct and explicit: `ScrapeWebsiteTool` output → LLM synthesizes into report
→ `FileWriterTool` writes it. All three criteria satisfied; textbook confused-deputy
pattern.

---

## Finding #3 — TP

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**Agent:** `assistant_agent` (role: XiaoPaw 个人助手, m3l19/m3l19_context_mgmt.py:281) — CrewAI  
**Source tool:** `BaiduSearchTool` — pattern `baidu_search`, classification `SOURCE`, trust `untrusted`, privilege 0  
**Sink tool:** `FileWriterTool` — pattern `write_file`, classification `SINK`, privilege 2, reversible

**Label: TP**

**Reasoning:**

(a) ✓ — `BaiduSearchTool._run()` makes live HTTP POST requests to Baidu's Qianfan search
API (`https://qianfan.baidubce.com/v2/ai_search/web_search`) and returns real web search
results: page titles, URLs, and content summaries scraped from external sites. This content
is authored by third parties and is externally-influenceable. Trust `untrusted`.

(b) ✓ — `FileWriterTool` at privilege 2 writes to the local filesystem. The first
`DEMO_ROUNDS` task explicitly requests "生成一份调研报告保存到文件" (generate a research
report and save to file).

(c) ✓ — No gate. The `@before_llm_call` hook does session management (prune/compress)
only; it does not intercept tool calls or require human approval. No `requires_approval`,
no `interrupts_before`.

Wiring: `BaiduSearchTool` returns web content → LLM synthesizes → `FileWriterTool`
writes. All three criteria satisfied.

---

## Finding #4 — TP

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**Agent:** `writer` (role: 报告撰写研究员, m1l3/m1l3_multi_agent.py:92) — CrewAI  
**Source tool:** `FileReadTool` — pattern `read_file`, classification `SOURCE`, trust `mixed`, privilege 1  
**Sink tool:** `FileWriterTool` — pattern `write_file`, classification `SINK`, privilege 2, reversible

**Label: TP**

**Reasoning:**

(a) ✓ with note — `FileReadTool` has trust `mixed`, which qualifies under §3.1(a) ("both
qualify; trust level affects only severity, not firing"). The criterion requires that the
source's output be externally-influenceable; here it is, but transitively:

The `writer` agent delegates research to the `searcher` agent (`allow_delegation=True`).
The `searcher` uses `BaiduSearchTool` and `ScrapeWebsiteTool` to collect external web
content, then writes that content to intermediate step-report `.md` files. The `writer`
subsequently reads those files via `FileReadTool`. The files therefore contain externally-
authored web content; `FileReadTool`'s output in this context carries attacker-influenced
data from the upstream delegation chain.

This is a transitive externality case — the external influence arrives via an upstream
agent's file write, not directly through the flagged tool's own network call. The static
analyzer cannot distinguish files-containing-external-content from files-containing-
internal-content; it correctly fires on the co-membership pattern. The actual data path
confirms criterion (a) is met.

(b) ✓ — `FileWriterTool` at privilege 2. The writer produces a consolidated final report
file.

(c) ✓ — `allow_delegation=True` is to the `editor` agent for review, not a HITL gate on
file writes. No `requires_approval`, no `interrupts_before`.

All three criteria satisfied. Note: the finding's "externality is transitive" character
is recorded here for completeness, not as grounds for FP — criterion (a) asks whether the
source's output can carry externally-influenceable data in the deployment context, and in
this deployment context it can.

---

## Finding #5 — AMBIGUOUS

**Repo:** `kid0317/crewai_mas_demo`  
**Pinned SHA:** `d5cfc79d3f61687c777b2e1328d1a265762f72fc`  
**Agent:** `crontab_manager_agent` (role: 定时任务管理专家, m2l8/m2l8_tools_call.py:127) — CrewAI  
**Source tool:** `FileReadTool` — pattern `read_file`, classification `SOURCE`, trust `mixed`, privilege 1  
**Sink tool:** `FileWriterTool` — pattern `write_file`, classification `SINK`, privilege 2, reversible

**Label: AMBIGUOUS**

**Reasoning:**

Criterion (a) is undeterminable from static analysis. `FileReadTool` reads `CRONTAB.md`,
a file that contains cron task entries the agent itself previously wrote, derived from the
`{user_input}` template variable:

```python
Task(description="根据用户的需求...用户的输入为：{user_input}", ...)
```

Example `user_input` values are direct conversational requests ("create a Monday–Friday
9am task", "show me my current tasks", "change the task to 9:30"). This is user-supplied
configuration input, not content fetched from an external web source or from an attacker-
controllable third-party channel.

The question is whether user-supplied configuration — authored by the deploying user, not
by an external attacker — qualifies as "externally-influenceable" under criterion (a).
The methodology defines this as content "not within the author's (developer's) control,"
which covers adversarial external channels (email body, web page, file from untrusted
third party). Routine end-user input to a task-management tool is outside the developer's
control in a trivial sense, but is not the attacker-controlled channel the confused-deputy
pattern is designed to catch.

Forcing a TP call would overstate the pattern (any tool that reads a user-writable file
would always fire). Forcing an FP call would require asserting that user-supplied input
can never carry injection payloads, which is also not generally true.

Per methodology §4: AMBIGUOUS findings are excluded from the precision denominator.
This finding is excluded from the 4/5 precision calculation above.

---

## Finding #6 — TP

**Repo:** `lesteroliver911/llamaindex-agentworkflow-browse-agent`  
**Pinned SHA:** `71bf390641ca16a7c5846d3811ffbbc3812ec161`  
**Agent:** `BrowserAgent` (LlamaIndex FunctionAgent, main.py:75)  
**Source tool:** `navigate_to` — pattern `navigate_to`, classification `SOURCE`, trust `untrusted`, privilege 0  
**Sink tool:** `click_element` — pattern `click_element`, classification `SINK`, privilege 2, reversible

**Label: TP**

**Reasoning:**

(a) ✓ — `navigate_to` itself returns only `"Navigated to {url}"` (not the page content).
However, the page content reaches the LLM through companion tools in the same toolbox:
`search_text` returns text found on the active page, and `take_screenshot` appends a
screenshot into the agent's context state. An attacker who controls the navigated-to URL
controls what the LLM perceives after `navigate_to` completes. The classification as
`SOURCE` (trust `untrusted`) is correct for the toolbox as a whole: `navigate_to` +
`search_text`/`take_screenshot` together make page content accessible to the LLM. The
finding fires on `navigate_to` as the source; the companion tools are the mechanism by
which the source's (attacker-controlled) content enters the LLM context.

(b) ✓ — `click_element` drives a live Chrome browser via `helium.click(text)`. It can
submit forms, follow navigation links, trigger account-state changes. Privilege 2,
reversible in principle. Threshold met.

(c) ✓ — No `interrupt_before`, no `requires_approval`, no `StopAtTools`. The workflow
runs to completion from a single `input()` call with no mid-execution human checkpoint.
`can_handoff_to=["AnalysisAgent"]` is inter-agent delegation, not a HITL gate.

Wiring: user instruction → `navigate_to(url)` → `search_text`/`take_screenshot` expose
page content to LLM → `click_element` acts on that content. A page with adversarial
visible text (e.g., "Click the Confirm Payment button") can cause the agent to issue
`click_element("Confirm Payment")` on whatever page is currently loaded. All three
criteria satisfied.
