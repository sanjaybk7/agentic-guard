# Precision/recall evaluation — labeling methodology

Labeling criteria and process for the agentic-guard v0.2 precision/recall
evaluation. The analyzer is frozen at the v0.2 snapshot during evaluation;
no changes to the analyzer are made as a result of labeling decisions.

---

## 1. Purpose and scope

This document defines how each IG001 and IG002 finding is classified as
TP, FP, or AMBIGUOUS during the precision/recall evaluation of
agentic-guard v0.2.

**Analyzer version:** v0.2 (post-PR #5), frozen for the duration of the
evaluation. Commit SHA to be recorded when evaluation begins.

**Corpus target:** 150 agent repositories, SHA-pinned. Each repo's exact
commit SHA is recorded in the evaluation dataset before any scan runs. No
repo is re-cloned during evaluation; all measurements use the pinned
checkout.

**Anti-fabrication:** per `docs/REVIEW_PROTOCOL.md`, every count in the
results doc must be backed by the labeled dataset. No category-level
estimates stated as fact.

---

## 2. Taxonomy — actual source and sink patterns (v0.2)

Labels are anchored to the live taxonomy at
`src/agentic_guard/taxonomy.yaml`. The lists below are the complete v0.2
taxonomy; any discrepancy between this section and the YAML file is
resolved in favor of the YAML file.

### 2.1 Source patterns (trust_of_output: untrusted or mixed)

| Pattern | Trust | Privilege | Notes |
|---|---|---|---|
| `read_email` | untrusted | 1 | Email body is attacker-controllable |
| `get_email` | untrusted | 1 | |
| `fetch_email` | untrusted | 1 | |
| `search_web` | untrusted | 0 | SEO / injected HTML |
| `web_search` | untrusted | 0 | |
| `browse` | untrusted | 0 | |
| `fetch_url` | untrusted | 0 | |
| `read_url` | untrusted | 0 | |
| `scrape` | untrusted | 0 | |
| `read_pdf` | untrusted | 1 | PDFs can embed adversarial text |
| `read_document` | untrusted | 1 | |
| `read_file` | mixed | 1 | May contain user-supplied or pasted content |
| `load_file` | mixed | 1 | |
| `get_ticket` | untrusted | 1 | Support tickets are user-submitted |
| `get_issue` | untrusted | 1 | |
| `read_slack` | untrusted | 1 | |
| `read_message` | untrusted | 1 | |
| `query_database` | mixed | 1 | |
| `rag_lookup` | mixed | 0 | RAG indexes can be poisoned |
| `vector_search` | mixed | 0 | |
| `query_user_db` | mixed | 2 | **BOTH** class — also a sink; see §2.3 |

### 2.2 Sink patterns (privilege ≥ 1)

The rule suppresses sinks with `privilege < 1`; in practice all taxonomy
sinks have `privilege ≥ 2`.

| Pattern | Privilege | Reversible | Notes |
|---|---|---|---|
| `send_email` | 2 | false | Cannot be unsent; exfiltrates data |
| `send_message` | 2 | false | |
| `post_message` | 2 | false | |
| `post_to_slack` | 2 | false | |
| `send_slack` | 2 | false | |
| `tweet` | 3 | false | |
| `post_tweet` | 3 | false | |
| `transfer_money` | 3 | false | |
| `make_payment` | 3 | false | |
| `pay` | 3 | false | |
| `delete_file` | 2 | false | |
| `write_file` | 2 | true | |
| `edit_file` | 2 | true | |
| `run_shell` | 3 | false | |
| `execute_command` | 3 | false | |
| `shell` | 3 | false | |
| `deploy` | 3 | false | |
| `create_pr` | 2 | true | |
| `merge_pr` | 3 | false | |
| `http_post` | 2 | false | Outbound POST can exfiltrate |
| `http_request` | 2 | false | |
| `webhook` | 2 | false | |
| `query_user_db` | 2 | true | **BOTH** class — also a source; see §2.3 |

### 2.3 BOTH classification

`query_user_db` is classified as BOTH source and sink. A tool with this
pattern counts simultaneously toward the source check and the sink check
in IG001. Labelers should note when a single tool satisfies both criteria.

---

## 3. Labeling categories

### 3.1 IG001 — Confused-deputy

**TP** — all three hold:

(a) The agent's toolbox contains ≥1 source tool (any pattern from §2.1,
    regardless of whether trust_of_output is `untrusted` or `mixed` —
    both qualify; trust level affects only severity, not firing).

(b) The toolbox contains ≥1 sink tool with `privilege ≥ 1` (any pattern
    from §2.2; in practice all taxonomy sinks have privilege ≥ 2).

(c) No recognized gate suppresses the sink. The tool recognizes exactly
    two gate mechanisms:
    - `sink.requires_approval = True` on the tool definition
    - The sink's name appears in the agent's `interrupts_before` list
      (LangGraph) or equivalent `StopAtTools` / `stop_on_first_tool`
      construct (OpenAI Agents SDK)

    **Note on context isolation:** split-agent architectures where the
    source and sink are in separate agents with no shared LLM context are
    a valid architectural mitigation, but the tool cannot detect this from
    static analysis in all cases. A finding where context isolation is
    demonstrably in place is labeler-classified FP even if the tool fires.
    HITL callbacks not representable as `requires_approval` or
    `interrupts_before` are handled the same way.

**FP** — ≥1 of (a)/(b)/(c) fails:
- The matched source pattern is in the codebase but the tool's output is
  not externally influenceable in the deployment context
- The matched sink pattern does not perform a privileged or irreversible
  action in the deployment context (e.g., a function named `send_email`
  that only logs locally)
- An unrecognized gate exists (context isolation, HITL callback not
  representable as `requires_approval` / `interrupts_before`, framework-
  level approval gate the parser doesn't extract)

**AMBIGUOUS** — (a) or (b) undeterminable from static code alone:
- Source or sink pattern matched but requires runtime context or
  deployment knowledge not visible in source (e.g., the tool delegates
  to a runtime-injected function; the sink's privilege depends on
  configuration)

### 3.2 IG002 — Dynamic system prompt

**TP** — both hold:

(a) The system prompt is built at runtime from a non-statically-resolvable
    value. This includes: f-strings with variables, string concatenation
    with non-literal operands, `.format()` with runtime arguments, values
    loaded from external sources (file, DB, API) at call time. It excludes
    values the analyzer resolves as static: plain string literals, module-
    level string constants (PR #1), function-local string literals (PR #5).

(b) The interpolated value can carry externally-influenceable data (user
    input, request parameters, content fetched from an external system).

**Note:** the tool fires whenever `system_prompt_is_dynamic` is True,
without checking (b). The `_USER_CONTROLLED_HINTS` check
(`request`, `user_input`, `message`, `query`, `body`, `content`, `text`,
`input`, `raw`, `params`, `form`, `data`, `payload`) affects only severity
(HIGH if a hint matches, MEDIUM otherwise), not whether the finding fires.
A finding where (a) holds but (b) does not is labeler-classified FP or
AMBIGUOUS, even though the tool fires.

**FP** — (a) or (b) fails:
- The prompt resolves to a static literal (including module-level
  constants and function-local literal bindings) — the tool should not
  fire post-v0.2; if it does, that is itself a bug to report separately
- The `instructions=callable` form where the callable produces a static
  result the analyzer cannot yet resolve
- The interpolated value is provably author-controlled (e.g., a
  configuration constant read once at startup with no external input path)

**AMBIGUOUS** — (b) undeterminable:
- The interpolated value's origin is not traceable from static code (the
  variable is imported from a module the scanner doesn't have, or set via
  a dependency-injection pattern)

---

## 4. AMBIGUOUS handling

AMBIGUOUS findings are **excluded from the precision denominator**.
Precision is computed as TP / (TP + FP); the AMBIGUOUS count is reported
separately alongside precision.

Forcing a TP or FP call on a genuinely unclear finding is deliberately
avoided — doing so would either overstate precision (forcing AMBIGUOUS
into FP) or understate it (forcing into TP). The AMBIGUOUS count is itself
a signal about the limits of static analysis on this corpus.

---

## 5. Precision

```
Precision = TP / (TP + FP)
```

AMBIGUOUS excluded. Reported as a fraction and percentage, alongside:
- Total findings labeled
- TP count
- FP count
- AMBIGUOUS count (and percentage of total)
- Per-rule breakdown (IG001 precision, IG002 precision)

---

## 6. Recall — tool-blind audited subset

A subset of repos is audited manually for recall measurement. The auditor
finds all IG001- and IG002-class issues present in the repo **without
viewing agentic-guard's output first**. After the manual audit is
complete, the tool output is revealed and compared.

```
Recall = findings_caught_by_tool / total_issues_found_by_audit
```

**Subset size and selection:** target ~15–20 repos from the 150-repo
corpus, selected to span:
- Multiple frameworks (OpenAI Agents SDK, LangGraph, CrewAI)
- Multiple complexity levels (simple single-agent, multi-agent)
- Both positive (expected findings) and negative (expected clean) repos

The selection and rationale are recorded before scanning begins. Post-hoc
selection of repos based on scan results is not permitted.

---

## 7. TP confirmation

For approximately 10–15 TP findings, escalate to **confirmed TP** via one
of:

1. **Minimal PoC:** construct a prompt payload that, when returned by the
   source tool, causes the agent to invoke the sink tool on the attacker's
   behalf (IG001), or causes the agent's system prompt to be overwritten
   with attacker-controlled content (IG002).
2. **Filed maintainer issue:** open a vulnerability report to the repo
   maintainer describing the finding; record acknowledgment (or
   non-response after 30 days) as the confirmation artifact.

Confirmed TPs serve as the primary ground-truth integrity mechanism in
lieu of a second independent labeler. The confirmed-TP list is recorded in
the results doc with PoC or issue link.

---

## 8. Threats to validity

- **Single primary labeler:** mitigated by rigid per-criterion labeling
  (criteria in §3 leave limited judgment space), plus confirmed TPs
  as an independent ground-truth anchor.
- **Corpus selection bias:** the 150-repo corpus is selected from GitHub
  trending / topic search for agent frameworks. This oversamples
  open-source demo code relative to production deployments; real-world
  precision/recall may differ.
- **Taxonomy-dependence of labels:** TP/FP calls for IG001 depend on the
  tool taxonomy in `taxonomy.yaml`. A tool not in the taxonomy is not
  classified as source or sink, so IG001 cannot fire for it — this is a
  recall ceiling, not a labeling error. Findings from unlisted tool
  patterns are outside the v0.2 scope.
- **v0.2-frozen snapshot:** labels apply to the analyzer at v0.2. Future
  PRs (IG003, `self.X` pattern, SHA-pinned corpus eval) may change the
  TP/FP composition.

---

## 9. Anti-fabrication

Per `docs/REVIEW_PROTOCOL.md`: every count in the eventual results doc
must be backed by the labeled dataset. No count is stated without the
corresponding rows in the dataset that produce it. Category-level
estimates stated as facts are a known failure mode in this project's
history (see the ~16 function-local FP projection, corrected in
`docs/eval/PR-5-corpus-results.md`).
