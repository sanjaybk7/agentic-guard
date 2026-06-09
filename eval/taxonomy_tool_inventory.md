# Taxonomy Tool Inventory — CrewAI + LlamaIndex Corpus Scan

**Date:** 2026-06-09
**Branch:** eval-corpus @ `dd091fa`
**Engine source:** main @ `7d10737` (parsers read via `git show`)
**Scope:** All repos with `framework_tag == "crewai"` (25) or `framework_tag == "llama-index"` (4)
**Script:** `/tmp/tool_inventory.py` (standalone AST extractor, replicates parser tool-extraction logic)

---

## Key Finding Up Front

The existing taxonomy uses snake_case patterns (`read_file`, `web_search`, `send_email`).
CrewAI tool classes are PascalCase (`FileReadTool`, `SerperDevTool`). The taxonomy's
substring match lowercases the tool name — `FileReadTool` → `filereadtool` — which does
NOT contain `read_file` (the underscore is absent). This pattern mismatch causes nearly
all CrewAI tool classes to resolve as NEUTRAL, which is why IG001 fires 0.

**Current taxonomy hits from the corpus: 3 of 61 distinct names.**

| Currently matched | Pattern that hits | Classification |
|-------------------|-------------------|----------------|
| `ScrapeWebsiteTool` | `scrape` | SOURCE |
| `ShellExecutorTool` | `shell` | SINK |
| `web_search_tool` | `web_search` | SOURCE |

Everything else is NEUTRAL.

---

## Step 1 — Raw Inventory

### 1a. CrewAI (25 repos scanned, 55 distinct tool names)

Repos: strnad/CrewAI-Studio, alexfazio/viral-clips-crew, liangdabiao/easy\_investment\_Agent\_crewai, NanGePlus/CrewAITest, LangGraph-GUI/CrewAI-GUI-Qt, AbubakrChan/crewai-UI-business-product-launch, tonykipkemboi/crewai-gmail-automation, bhancockio/crewai-updated-tutorial-hierarchical, bhancockio/automate-youtube-with-crewai, liangdabiao/crewai\_stock\_analysis\_system, tonykipkemboi/resume-optimization-crew, bhancockio/crewai-rag-deep-dive, bhancockio/nextjs-crewai-basic-tutorial, NanGePlus/CrewAIFlowsFullStack, kid0317/crewai\_mas\_demo, alejandro-ao/crewai-instagram-example, bhancockio/crewai-groq-tutorial, OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI, alejandro-ao/crewai-crash-course, yuriwa/crewai-sheets-ui, tonykipkemboi/crewai-streamlit-demo, google-gemini/crewai-quickstart, luandev/ComfyUI-CrewAI, HeadyZhang/agent-audit, blairhudson/fastapi-agents

| Tool name | Freq | Repos |
|-----------|-----:|-------|
| `ScrapeWebsiteTool` | 16 | NanGePlus/CrewAIFlowsFullStack, NanGePlus/CrewAITest, kid0317/crewai\_mas\_demo, tonykipkemboi/resume-optimization-crew |
| `FileReadTool` | 15 | OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI, kid0317/crewai\_mas\_demo, tonykipkemboi/crewai-gmail-automation |
| `SerperDevTool` | 13 | NanGePlus/CrewAIFlowsFullStack, NanGePlus/CrewAITest, tonykipkemboi/resume-optimization-crew |
| `ReportWritingTool` | 10 | liangdabiao/crewai\_stock\_analysis\_system |
| `search_tool` | 8 | OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI |
| `MDXSearchTool` | 8 | OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI |
| `IntermediateTool` | 7 | kid0317/crewai\_mas\_demo |
| `FakeTool` | 6 | kid0317/crewai\_mas\_demo |
| `FinancialCalculatorTool` | 5 | liangdabiao/crewai\_stock\_analysis\_system |
| `BaiduSearchTool` | 5 | kid0317/crewai\_mas\_demo |
| `FundamentalAnalysisTool` | 4 | liangdabiao/crewai\_stock\_analysis\_system |
| `FileWriterTool` | 4 | kid0317/crewai\_mas\_demo |
| `DallETool` | 4 | OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI |
| `AStockDataTool` | 3 | liangdabiao/easy\_investment\_Agent\_crewai |
| `CalculatorTool` | 3 | liangdabiao/easy\_investment\_Agent\_crewai |
| `search_internet` | 3 | alejandro-ao/crewai-instagram-example, bhancockio/crewai-updated-tutorial-hierarchical |
| `TechnicalAnalysisTool` | 3 | liangdabiao/crewai\_stock\_analysis\_system |
| `skill_tool` | 3 | kid0317/crewai\_mas\_demo |
| `FixedDirectoryReadTool` | 3 | kid0317/crewai\_mas\_demo |
| `SkillLoaderTool` | 3 | kid0317/crewai\_mas\_demo |
| `KnowledgeSearchTool` | 3 | kid0317/crewai\_mas\_demo |
| `FinancialAnalysisTool` | 2 | liangdabiao/easy\_investment\_Agent\_crewai |
| `DataExportTool` | 2 | liangdabiao/crewai\_stock\_analysis\_system |
| `pdf_search_tool` | 2 | bhancockio/crewai-rag-deep-dive |
| `rag_tool` | 2 | bhancockio/crewai-rag-deep-dive |
| `searchInternetTool` | 2 | bhancockio/nextjs-crewai-basic-tutorial |
| `youtubeSearchTool` | 2 | bhancockio/nextjs-crewai-basic-tutorial |
| `ShellExecutorTool` | 2 | kid0317/crewai\_mas\_demo |
| `tool` | 2 | kid0317/crewai\_mas\_demo |
| `LoopingTool` | 2 | kid0317/crewai\_mas\_demo |
| `MarketSentimentTool` | 1 | liangdabiao/easy\_investment\_Agent\_crewai |
| `vectorSearch` | 1 | NanGePlus/CrewAITest |
| `saveText2Pdf` | 1 | NanGePlus/CrewAITest |
| `duckduckgo_search` | 1 | AbubakrChan/crewai-UI-business-product-launch |
| `GmailOrganizeTool` | 1 | tonykipkemboi/crewai-gmail-automation |
| `SaveDraftTool` | 1 | tonykipkemboi/crewai-gmail-automation |
| `SlackNotificationTool` | 1 | tonykipkemboi/crewai-gmail-automation |
| `GmailDeleteTool` | 1 | tonykipkemboi/crewai-gmail-automation |
| `EmptyTrashTool` | 1 | tonykipkemboi/crewai-gmail-automation |
| `youtube_video_search_tool` | 1 | bhancockio/automate-youtube-with-crewai |
| `youtube_video_details_tool` | 1 | bhancockio/automate-youtube-with-crewai |
| `fetch_latest_videos_tool` | 1 | bhancockio/crewai-rag-deep-dive |
| `add_video_to_vector_db_tool` | 1 | bhancockio/crewai-rag-deep-dive |
| `fire_crawl_search_tool` | 1 | bhancockio/crewai-rag-deep-dive |
| `SpawnSubAgentTool` | 1 | kid0317/crewai\_mas\_demo |
| `SpawnParallelTool` | 1 | kid0317/crewai\_mas\_demo |
| `AddImageToolLocal` | 1 | kid0317/crewai\_mas\_demo |
| `skill_loader` | 1 | kid0317/crewai\_mas\_demo |
| `InjectableSearchTool` | 1 | kid0317/crewai\_mas\_demo |
| `wrapped` | 1 | kid0317/crewai\_mas\_demo |
| `secure_tool` | 1 | kid0317/crewai\_mas\_demo |
| `search_instagram` | 1 | alejandro-ao/crewai-instagram-example |
| `open_page` | 1 | alejandro-ao/crewai-instagram-example |
| `vision_tool` | 1 | OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI |
| `EXAAnswerTool` | 1 | tonykipkemboi/crewai-streamlit-demo |

### 1b. LlamaIndex (4 repos scanned, 7 distinct tool names)

Repos: NetEase-Media/grps\_trtllm, lesteroliver911/llamaindex-agentworkflow-browse-agent, AstraBert/llamaindex-docs-agent, Andrew-Tsegaye/Advanced-AI-Code-Generation-Agent

| Tool name | Freq | Repos |
|-----------|-----:|-------|
| `search_text` | 2 | lesteroliver911/llamaindex-agentworkflow-browse-agent |
| `take_screenshot` | 2 | lesteroliver911/llamaindex-agentworkflow-browse-agent |
| `router_tool` | 2 | AstraBert/llamaindex-docs-agent |
| `web_search_tool` | 2 | AstraBert/llamaindex-docs-agent |
| `tool` | 1 | NetEase-Media/grps\_trtllm |
| `navigate_to` | 1 | lesteroliver911/llamaindex-agentworkflow-browse-agent |
| `click_element` | 1 | lesteroliver911/llamaindex-agentworkflow-browse-agent |

### 1c. Notable absences

- `FunctionTool`, `QueryEngineTool` — neither appeared in the corpus. These are LlamaIndex's
  generic wrappers. Repos used either bare function names (snake\_case) or custom
  class names instead. Taxonomy entries for these are deferred to Step 3.

- `WebsiteSearchTool`, `CodeInterpreterTool`, `YoutubeVideoSearchTool` — standard
  `crewai_tools` package classes not present in this corpus. No corpus data to validate
  their classification; not included in this proposal.

---

## Step 2 — Proposed Classification Table

Proposed patterns use lowercase substrings that uniquely identify each tool class under
the existing case-insensitive substring matcher.

### 2a. High-confidence SOURCE — external web / search

| Tool class | Freq | FW | Proposed | trust\_of\_output | privilege | reversible | Proposed pattern | Reasoning |
|------------|-----:|-----|----------|-------------------|-----------|------------|-----------------|-----------|
| `ScrapeWebsiteTool` | 16 | CrewAI | SOURCE | untrusted | 0 | true | `scrape` *(already matches)* | Web scraping from arbitrary URLs; content is attacker-controlled. Currently classified correctly. |
| `SerperDevTool` | 13 | CrewAI | SOURCE | untrusted | 0 | true | `serperdev` | Serper.dev Google Search API; returns web results containing attacker-influenced content. |
| `BaiduSearchTool` | 5 | CrewAI | SOURCE | untrusted | 0 | true | `baidusearch` | Baidu web search; same trust model as any web search. |
| `search_internet` | 3 | CrewAI | SOURCE | untrusted | 0 | true | `search_internet` | Bare function name; name unambiguously identifies web search. |
| `searchInternetTool` | 2 | CrewAI | SOURCE | untrusted | 0 | true | `searchinternet` | PascalCase variant of above; same reasoning. |
| `youtubeSearchTool` | 2 | CrewAI | SOURCE | untrusted | 0 | true | `youtubesearch` | YouTube search API; results contain untrusted external content. |
| `fire_crawl_search_tool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `fire_crawl` | Firecrawl web crawling API; fetches external pages. |
| `youtube_video_search_tool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `youtube_video_search` | YouTube search; untrusted external content. |
| `youtube_video_details_tool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `youtube_video_details` | Fetches YT video metadata; untrusted. |
| `fetch_latest_videos_tool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `fetch_latest_videos` | Fetches YouTube video listings; untrusted. |
| `duckduckgo_search` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `duckduckgo` | DuckDuckGo web search. |
| `EXAAnswerTool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `exaanswer` | Exa AI web search engine. |
| `search_instagram` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `search_instagram` | Reads Instagram posts; external untrusted content. |
| `web_search_tool` | 2 | LlamaIndex | SOURCE | untrusted | 0 | true | `web_search` *(already matches)* | Already classified correctly. |
| `search_text` | 2 | LlamaIndex | SOURCE | untrusted | 0 | true | `search_text` | Browser automation text search; reads page content at attacker-controlled URL. |

### 2b. High-confidence SOURCE — file / document / RAG

| Tool class | Freq | FW | Proposed | trust\_of\_output | privilege | reversible | Proposed pattern | Reasoning |
|------------|-----:|-----|----------|-------------------|-----------|------------|-----------------|-----------|
| `FileReadTool` | 15 | CrewAI | SOURCE | mixed | 1 | true | `fileread` | Reads files from local filesystem. Files may contain pasted external content. Privilege=1: leak risk, no write. |
| `MDXSearchTool` | 8 | CrewAI | SOURCE | mixed | 0 | true | `mdxsearch` | Searches MDX docs files; file-based, trust=mixed (docs may include external text). |
| `FixedDirectoryReadTool` | 3 | CrewAI | SOURCE | mixed | 1 | true | `fixeddirectoryread` | Reads files from a fixed directory; same trust model as FileReadTool. |
| `KnowledgeSearchTool` | 3 | CrewAI | SOURCE | mixed | 0 | true | `knowledgesearch` | Searches knowledge base; RAG-style, trust=mixed (index can be poisoned). |
| `rag_tool` | 2 | CrewAI | SOURCE | mixed | 0 | true | `rag_tool` | RAG retrieval; same trust model as `rag_lookup`. |
| `pdf_search_tool` | 2 | CrewAI | SOURCE | mixed | 1 | true | `pdf_search` | PDF search; PDFs can embed adversarial text. |
| `vectorSearch` | 1 | CrewAI | SOURCE | mixed | 0 | true | `vectorsearch` | Vector DB search; trust=mixed (indexes can be poisoned). |

### 2c. High-confidence SOURCE — external data APIs

| Tool class | Freq | FW | Proposed | trust\_of\_output | privilege | reversible | Proposed pattern | Reasoning |
|------------|-----:|-----|----------|-------------------|-----------|------------|-----------------|-----------|
| `AStockDataTool` | 3 | CrewAI | SOURCE | untrusted | 0 | true | `astockdata` | Fetches live stock market data from external API. Trust=untrusted (external feed). |
| `MarketSentimentTool` | 1 | CrewAI | SOURCE | untrusted | 0 | true | `marketsentiment` | Fetches market sentiment from external source; untrusted. |

### 2d. High-confidence SINK

| Tool class | Freq | FW | Proposed | trust\_of\_output | privilege | reversible | Proposed pattern | Reasoning |
|------------|-----:|-----|----------|-------------------|-----------|------------|-----------------|-----------|
| `ShellExecutorTool` | 2 | CrewAI | SINK | — | 3 | false | `shell` *(already matches)* | Shell execution; currently classified correctly. Highest privilege. |
| `FileWriterTool` | 4 | CrewAI | SINK | — | 1 | false | `filewriter` | Writes files to disk; privileged write action. Privilege=1 (local only, no external party). Not reversible — file persists. |
| `SlackNotificationTool` | 1 | CrewAI | SINK | — | 2 | false | `slacknotification` | Sends Slack message to external channel; irreversible, visible to other parties. |
| `GmailDeleteTool` | 1 | CrewAI | SINK | — | 2 | false | `gmaildele` | Permanently deletes Gmail messages; irreversible destruction of user data. |
| `EmptyTrashTool` | 1 | CrewAI | SINK | — | 2 | false | `emptytrash` | Permanently deletes all trash emails; irreversible. |
| `saveText2Pdf` | 1 | CrewAI | SINK | — | 1 | false | `savetext2pdf` | Creates PDF file on disk; write action. |
| `add_video_to_vector_db_tool` | 1 | CrewAI | SINK | — | 1 | true | `add_video_to_vector_db` | Writes to vector database; privilege=1. Reversible (can delete entry). |
| `click_element` | 1 | LlamaIndex | SINK | — | 2 | false | `click_element` | Browser click — can trigger form submission, account action, purchase, file download. Side-effect risk is high even though the "action" is small. |

### 2e. High-confidence BOTH

| Tool class | Freq | FW | Proposed | trust\_of\_output | privilege | reversible | Proposed pattern | Reasoning |
|------------|-----:|-----|----------|-------------------|-----------|------------|-----------------|-----------|
| `GmailOrganizeTool` | 1 | CrewAI | BOTH | mixed | 1 | true | `gmailorganize` | Reads email headers/metadata AND modifies them (archive, label, move). Both a source of untrusted content AND a state-mutating action. Reversible (labels/archive can be undone). |

### 2f. High-confidence NEUTRAL (no taxonomy entry needed)

| Tool class | Freq | FW | Reasoning |
|------------|-----:|-----|-----------|
| `FinancialCalculatorTool` | 5 | CrewAI | Pure arithmetic computation; no external I/O. |
| `CalculatorTool` | 3 | CrewAI | Pure arithmetic; NEUTRAL. |
| `IntermediateTool` | 7 | CrewAI | Test fixture in kid0317/crewai\_mas\_demo; not a real external tool. |
| `FakeTool` | 6 | CrewAI | Test fixture; name confirms it. |
| `LoopingTool` | 2 | CrewAI | Test fixture (simulates looping behavior). |
| `skill_tool` | 3 | CrewAI | Generic placeholder in test harness. |
| `SkillLoaderTool` | 3 | CrewAI | Loads skill definitions; internal meta-operation, no external I/O visible at AST level. |
| `skill_loader` | 1 | CrewAI | Same as SkillLoaderTool. |
| `tool` | 2+1 | Both | Completely generic placeholder; cannot classify. |
| `wrapped` | 1 | CrewAI | Test wrapper fixture. |
| `secure_tool` | 1 | CrewAI | Security-wrapper fixture in test harness. |
| `InjectableSearchTool` | 1 | CrewAI | Kid0317 injection-testing fixture; not a real search tool. |
| `router_tool` | 2 | LlamaIndex | QueryEngine router — selects between tools but performs no I/O itself; routing is pure dispatch. |

---

## Step 3 — Hard Cases: Decisions Required

### HC-1: `search_tool` (freq=8, CrewAI, OneDuckyBoy/Awesome-AI-Agents-HUB-for-CrewAI)

**What it is:** A bare function name, likely wrapping a web search (context: an agent hub repo).
**The problem:** Name is too generic to commit to in the taxonomy. "search\_tool" could be a
web search, a local document search, or a vector search depending on implementation.
**Options:**
- (A) Classify as SOURCE(untrusted) based on "search" substring — catches this and any other `*search*` tool
- (B) Leave NEUTRAL — the name alone is insufficient; taxonomy should not guess
- (C) Add a `search_tool` exact pattern (very narrow, one repo)

_Recommendation pending your decision. Given freq=8, this is the highest-impact unresolved case._

### HC-2: `ReportWritingTool` (freq=10, CrewAI, liangdabiao)

**What it is:** Part of `liangdabiao/crewai_stock_analysis_system`'s custom tool suite.
**The problem:** "Writing" in the name strongly implies file output (→ SINK), but it could be
a function that formats and returns a text string (→ NEUTRAL).
**Options:**
- (A) SINK(privilege=1, reversible=false) — treat "writing" as evidence of file write
- (B) NEUTRAL — can't determine without reading the implementation
- (C) Flag for manual lookup in the repo before deciding

_Freq=10 makes this the highest-frequency unresolved case._

### HC-3: Financial analysis tools (CrewAI, liangdabiao)

`FundamentalAnalysisTool` (4), `TechnicalAnalysisTool` (3), `FinancialAnalysisTool` (2)

**What they are:** Custom tools in liangdabiao's financial analysis crew.
**The problem:** Could be (a) fetching live financial data from external API → SOURCE, or
(b) computing analysis from data already loaded in memory → NEUTRAL.
**Options:**
- (A) SOURCE(untrusted) — financial "analysis" tools typically need external data feeds
- (B) NEUTRAL — name says "analysis" (computation), not "fetch" or "get"
- (C) Inspect the liangdabiao repo to determine if these call external APIs

_These are single-repo tools. Decision has low corpus-wide impact but affects whether
IG001 fires on the liangdabiao financial agents._

### HC-4: `DallETool` (freq=4, CrewAI)

**What it is:** Calls the DALL-E image generation API.
**The problem:** This is an API call to an external service, but the result is AI-generated
image output — not attacker-controlled external text. It's not a traditional SOURCE
(no injection risk in image content returned to agent) and not a traditional SINK
(doesn't write to user-controlled systems).
**Options:**
- (A) SOURCE(trust=untrusted) — external API call, output is opaque to the agent
- (B) SINK(privilege=1) — API call has cost/rate-limit side effects; the agent is "spending" API credits
- (C) NEUTRAL — pure generation, no taint-flow relevance for IG001/IG002 detection

_Recommendation: (C) NEUTRAL. The threat model for IG001 is confused-deputy (agent uses SOURCE content to decide SINK actions). DALL-E output goes back to the agent but doesn't carry injection risk in image form. Open to override._

### HC-5: `navigate_to` (freq=1, LlamaIndex) and `open_page` (freq=1, CrewAI)

**What they are:** Browser navigation/page-loading functions in browser-automation agents.
**The problem:**
- SOURCE perspective: loads a web page, making the content (attacker-controlled HTML) available → SOURCE
- SINK perspective: initiates network request, changes browser state, could trigger redirects

**Options:**
- (A) SOURCE(untrusted) — the primary purpose is to read page content; treat as a read
- (B) SINK(privilege=1) — the navigation itself is a side-effect (changes browser state)
- (C) BOTH — reads content AND changes state

_The key question: should browser navigation be treated as SOURCE (for the purpose of detecting whether an agent's prompt can be poisoned by page content) or as SINK (for the purpose of detecting whether an attacker can redirect the agent's navigation)? For IG001, SOURCE seems more useful — if `navigate_to` is SOURCE and `click_element` is SINK, an agent with both is IG001-flaggable._

### HC-6: `SaveDraftTool` (freq=1, CrewAI, tonykipkemboi/crewai-gmail-automation)

**What it is:** Saves an email draft in Gmail (not yet sent).
**The problem:** A draft is a side effect (creates state in Gmail) but it's reversible (can delete before sending) and has no external impact until explicitly sent.
**Options:**
- (A) SINK(privilege=1, reversible=true) — creates state in Gmail; low privilege, reversible
- (B) NEUTRAL — a draft is just saved state with no external action; treat like a local variable
- (C) SINK(privilege=2, reversible=false) — treat the same as send, since draft → send is one click

### HC-7: `SpawnSubAgentTool` and `SpawnParallelTool` (freq=1 each, CrewAI)

**What they are:** Meta-tools from kid0317/crewai\_mas\_demo that spawn sub-agents at runtime.
**The problem:** These don't map to SOURCE/SINK in the traditional sense. The spawned sub-agents
may then perform SOURCE/SINK actions, but that's detected at the sub-agent parse level.
**Options:**
- (A) NEUTRAL — the spawn action itself is orchestration, not I/O
- (B) SINK(privilege=2) — spawning an agent is a privileged action (gives LLM control over agent creation)
- (C) No taxonomy entry (single-repo, non-generalizable)

_Recommendation: (C) No taxonomy entry. These are one-repo test constructs, not a pattern
seen in real-world agent code. If agent-spawning tools become prevalent, this deserves a
dedicated threat model entry._

### HC-8: `DataExportTool` (freq=2, CrewAI, liangdabiao)

**What it is:** Exports data — likely to CSV, file, or external system.
**The problem:** "Export" could mean (a) local file write → SINK(privilege=1), or (b) sending to external destination → SINK(privilege=2).
**Options:**
- (A) SINK(privilege=1, reversible=false) — conservative: local write only
- (B) SINK(privilege=2, reversible=false) — could export to external systems

### HC-9: Generic wrappers `FunctionTool` / `QueryEngineTool` (freq=0 in corpus)

**What they are:** LlamaIndex's generic tool wrappers. Any arbitrary Python function can be
wrapped — the wrapped function's risk is invisible to the parser.
**The problem:** If the taxonomy classifies `functiontool` as NEUTRAL (can't see what it wraps)
we miss high-risk wrapped sinks. If we classify it as SOURCE or SINK, we get false positives.

These did NOT appear in the corpus. But they're the standard LlamaIndex pattern, so they
will appear in the wild.

**Options:**
- (A) NEUTRAL — be conservative; the wrapper name carries no information
- (B) Add to the "known wrappers" list in a separate taxonomy section; flag them as
  "wrap-risk: unknown" to trigger a different warning (not IG001)
- (C) Defer — don't add until seen in corpus

_This is a design question, not just a classification question. Surface it for decision._

### HC-10: Bare search names that might generalize (`MDXSearchTool`, `KnowledgeSearchTool`)

Both are clearly search/retrieval tools → SOURCE. But should the taxonomy use:
- (A) Exact lowercase class name (`mdxsearch`, `knowledgesearch`) — precise, corpus-validated
- (B) Broader pattern matching `search` as a suffix/infix in any PascalCase tool name?

Option (B) would catch any `*SearchTool` automatically but risks false positives (e.g.,
`SearchRankingTool` that computes rank, not retrieves). The corpus has many search tools;
a broader pattern would be more future-proof.

---

## Pattern Mismatch — Architecture Note

The taxonomy pattern `read_file` does not substring-match `filereadtool` (no underscore in
the lowercased PascalCase name). Two fix paths:

**Path A (current approach — add new patterns):** Add patterns like `fileread`, `filewriter`
that are unique-enough substrings of the PascalCase names. Precise, no engine changes,
but requires adding one pattern per class name.

**Path B (engine change — normalize before match):** Convert tool names from PascalCase to
snake\_case before taxonomy lookup (`FileReadTool` → `file_read_tool`), then the existing
`read_file` pattern would match. This is a one-time engine change that makes ALL future
PascalCase tool names work with the existing pattern set.

_This is a design decision. Path B has higher up-front cost but better long-term coverage.
Surfacing it here since it affects whether we need to add dozens of class-specific patterns._
