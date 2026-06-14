# IG002 Post-Fix Delta — agentic-guard v0.2 (kl002-narrow)

**Pre-fix engine:** main @ `031e781` (Taxonomy matcher fix; analyzer at the SHA used for the frozen-eval labeling pass).
**Post-fix engine:** branch `kl002-narrow` @ `4acc781`, parented on main @ `57dc46b` (PR #12) with the KL-002 short-circuit narrowed from a broad all-resolve guard to the explicit `STATIC_COMPOSER_FUNCTIONS` allowlist.
**Corpus:** 126 repos at pinned SHAs (same corpus as the frozen-eval scan).
**Re-scan dates:** 2026-06-14 (pre-fix re-confirmation, buggy-broad scan, narrowed scan).
**Sample referenced:** `eval/ig002_sample.md` (45 findings, stratified, seed 42, per-repo cap 5).
**Labels referenced:** `eval/ig002_labels.md` (4 TP / 3 AMBIGUOUS / 38 FP).

---

## Headline finding — two classes of IG002 false positive

The KL-002 labeling exercise and the post-fix re-scan together reveal that IG002 false
positives are not a single phenomenon. They split into two classes with very different
prospects for static-analysis fixes:

### Class (a) — Resolvable. **Fixed.**

| Pattern | Sample findings | Fix | Status |
|---------|----------------|-----|--------|
| Callable-static-composition: a pure string-composer function called with literal args (e.g. `build_prompt(base_instructions="literal")`) | F01–F05 (5) | `STATIC_COMPOSER_FUNCTIONS` allowlist gates a generic-Call short-circuit; `build_prompt` is in the list. | **silenced ✓** |
| Third-party SDK constants the symbol table cannot reach (e.g. `RECOMMENDED_PROMPT_PREFIX` from `agents.extensions.handoff_prompt`) | F09, F11, F12, F19, F34 (5) | `KNOWN_STATIC_NAMES` allowlist, gated by import presence so a same-named local binding can't accidentally inherit trust. | **silenced ✓** |
| Ternary between two literally-resolved branches (`A if cond else B`) where both `A` and `B` resolve to static | (no in-sample finding cleanly hit this without cross-module compound — see Class (b)/F41 below) | New `ast.IfExp` branch in `classify_prompt_expr` that classifies both branches recursively. | **mechanism verified** by regression test `test_ifexp_between_constants_no_findings` |

These FPs share a structural property: the engine had all the information needed to
prove staticness — it just lacked a rule. They are amenable to focused narrowing fixes.

### Class (b) — Irreducible without deployment context. **Not fixable by static analysis alone.**

| Pattern | Sample findings | Why static analysis can't close it |
|---------|----------------|-----------------------------------|
| Library extension point: a `system_prompt` parameter exposed for callers to override, with all in-codebase call sites using the default (e.g. Decepticon `create_<role>_agent()` family) | F22, F31, F36, F37, F45 (Decepticon cluster, 5) | The parameter exists *to be supplied at integration time* by external library users. Static analysis can't enumerate the universe of callers. |
| Agent-authoring tool where the application user IS the agent author (CrewAI Studio's Streamlit UI; CrewAI-GUI-Qt's workflow JSON) | F23, F33 (2) | The "user input" is the developer's own configuration; there is no separation between attacker and author. Static analysis sees a runtime input it can't distinguish from a deployment input. |
| Factory parameter with literal default; runtime override possible by config | F26, F28, F29, F35, F42 (5) | The static path resolves to a literal; the override path requires knowing who configures the harness — a deployment fact, not a code fact. |
| Author-provided workspace content (markdown files, soul.md/user.md/agent.md) | F43 (1) | The file path is project-relative and the content ships with the repo; whether the operator's deployment makes those files externally writable is invisible to the scanner. |
| Enum-ternary in f-string where all call sites use hardcoded enum members | F13 (1) | All possible runtime values are author-defined enum members; the engine sees an unknown runtime value. |

These FPs share a structural property: closing them requires knowing *who controls a
parameter at call time* — a deployment fact, not a code fact. **No narrowing rule on
`classify_prompt_expr` will eliminate them without false negatives.**

The author-controlled cluster dominates the plain-variable stratum (13 of 22 still-firing
FPs in the post-fix sample). It is the floor on what static-pattern detection can achieve
for IG002.

### Implication for the IG002 rule's framing

IG002 as it stands flags a *structural form* (dynamic prompt) without resolving whether
the dynamic content is *influenceable*. The (a)/(b) split is the operational consequence
of that scope: the resolvable FPs are an analyzer scope-gap and are closeable; the
irreducible FPs reflect a fundamental category the rule conflates with real injection.
Closing this honestly would require either (i) narrower rule scope (only fire when
external-source taint can be traced, which would require interprocedural taint analysis
not in v0.2), or (ii) explicit threat-model annotations on agent parameters (out of
scope for static analysis alone).

---

## Numbers, before vs after

### Totals

| Metric | Pre-fix (`031e781`) | Narrowed (`4acc781`) | Δ |
|--------|---------------------|---------------------|---|
| Total IG002 findings (126-repo corpus) | **148** | **110** | **−38 (−25.7%)** |
| Sample (45) — labelable (TP + FP) | 42 | 32 | −10 |
| Sample precision | 4/42 ≈ 9.5% | 4/32 ≈ **12.5%** | +3.0 pp |
| Population-weighted precision | **8.1%** | **11.0%** | **+2.8 pp (≈ +35% relative)** |
| **True positives lost** | — | **0** | **safety property held** |

### Per-stratum

| Stratum | Pre-fix pop | Narrowed pop | Δ pop | Pre sample TP/AMB/FP / lblbl / prec | Narrowed sample TP/AMB/FP / lblbl / prec |
|---------|-------------|--------------|-------|---|---|
| Callable/opaque | 29 | **5** | **−24 (−83%)** | 0/0/8 / 8 / 0.0% | 0/0/3 / 3 / 0.0% |
| F-string | 30 | **19** | **−11 (−37%)** | 3/1/8 / 11 / 27.3% | 3/1/4 / 7 / **42.9%** |
| Plain variable | 89 | **86** | **−3 (−3%)** | 1/2/22 / 23 / 4.3% | 1/2/21 / 22 / 4.5% |
| **Total** | **148** | **110** | **−38** | 4/3/38 / 42 / 9.5% | 4/3/28 / 32 / 12.5% |

The two-class finding is right here in the table: **the callable stratum collapsed
(29 → 5, −83%) and the f-string stratum was substantially trimmed (30 → 19, −37%)**,
because both strata are dominated by Class (a) resolvable patterns. **The plain-variable
stratum barely moved (89 → 86, −3%)** because it is dominated by Class (b) author-
controlled patterns the fixes cannot reach.

### Population-weighted precision arithmetic

**Pre-fix** (from `eval/ig002_labels.md`, reproduced for context):

```
P_pre = (29/148)(0/8) + (30/148)(3/11) + (89/148)(1/23)
      = 0 + 90/1628 + 89/3404
      = 3049/37444
      ≈ 0.0814 ≈ 8.1%
```

**Narrowed**:

```
P_narrow = (5/110)(0/3) + (19/110)(3/7) + (86/110)(1/22)

         = 0 + (19 × 3)/(110 × 7) + (86 × 1)/(110 × 22)
         = 0 + 57/770 + 86/2420

   57/770   ≈ 0.07403
   86/2420  ≈ 0.03554

P_narrow ≈ 0.07403 + 0.03554 = 0.10957 ≈ 11.0%
```

**Δ = +2.8 pp absolute, +34.6% relative.**

The callable stratum contributes nothing to either weighted total (precision = 0 in the
sample for both pre and post). The arithmetic improvement comes almost entirely from the
f-string stratum, where post-fix precision rose from 27.3% to 42.9% while the stratum
shrank by a third.

---

## Safety + integrity record

### All 4 TPs fire across every scan

| TP | Pre (`031e781`) | Buggy broad (PR #12, `57dc46b`) | Narrowed (`4acc781`) |
|----|------|-------|----------|
| F10 (`liangdabiao/crewai_stock_analysis_system` · `data_collection_crew.py:207`) | fires | fires | **fires ✓** |
| F14 (`AbubakrChan/crewai-UI-business-product-launch` · `main.py:27`) | fires | fires | **fires ✓** |
| F17 (`liangdabiao/crewai_stock_analysis_system` · `data_collection_crew.py:269`) | fires | fires | **fires ✓** |
| F21 (`xark-argo/argo` · `tool_agent_runner.py:65`) | fires | fires | **fires ✓** |

Verified per (repo, file_path, line) match against each scan's findings JSON.

### Recorded false-negative episode — PR #12 broad-rule revert

The first KL-002 implementation in PR #12 short-circuited any generic `Call` whose
argument Names all resolve to static — intended to silence the OpenCMO `build_prompt`
cluster. The post-fix verification probe (`tests/fixtures/vulnerable/closure_captures_external.py`)
exposed a false-negative pathway: the rule had no visibility into the *returned object*
of an arbitrary function call. A `make_prompt`-style callable that returns a closure
capturing external runtime state (e.g. `state["user_input"]`) was silenced even though
the closure dynamically embeds external content at invocation time. In a deployment that
passes real user data to such a closure, IG002 would miss the injection vector.

This was caught **before any results document was committed** by the verification step
the user defined in advance: "Confirm WHY KL-002 silenced [F06–F08]: would IG002 still
fire if the closure embedded a genuinely external value?" — and the answer was no.

The narrowed fix replaces the broad rule with `STATIC_COMPOSER_FUNCTIONS`, an explicit
allowlist of source-audited string-composing functions (currently `build_prompt`).
A generic non-allowlisted `Call` returns dynamic with filtered taints, the conservative
pre-PR #12 default. Two permanent regression tests guard the boundary:

- `test_closure_captures_external_state_still_fires` — the `make_prompt` FN repro
  fixture **must** fire IG002. If this ever fails, the broad rule has been reintroduced.
- `test_generic_callable_literal_args_still_fires` — a non-allowlisted callable with
  literal args **must** fire IG002 (the conservative default for unaudited functions).

This episode is documented here as evidence of the protocol working: the labeling pass
identified F06–F08 as "FP-but-demo-data-conditional"; the post-fix verification step
checked whether the analyzer's silencing matched the *reason* for the label (it didn't);
the rule was narrowed before the result was reported.

### What the narrowed analyzer silenced in the 45-sample (10 total, all FPs by label)

| ID | Pre | Narrowed | Class | Mechanism |
|----|-----|----------|-------|-----------|
| F01–F05 | fires | silenced | (a) | `STATIC_COMPOSER_FUNCTIONS` — `build_prompt` |
| F09, F11, F12, F19, F34 | fires | silenced | (a) | `KNOWN_STATIC_NAMES` — `RECOMMENDED_PROMPT_PREFIX` |

The buggy-broad fix additionally silenced F06–F08 (the `make_prompt` closure case); the
narrowed analyzer **does not silence them**, consistent with the FN-closure regression
test. F06–F08 are labeled FP because in this specific demo the closure draws from
hardcoded `RESERVATIONS`/`FLIGHTS`/`HOTELS`, not because the analyzer can verify the
closure is static.

---

## Caveats

- **Single labeler, n = 45 stratified sample.** Confidence intervals at this scale are
  wide; report raw counts alongside percentages and treat the precision figures as
  estimates not measurements.
- **Variable-stratum precision rests on 1 TP.** The plain-variable per-stratum precision
  is 1/22 = 4.5%. Adding or removing a single TP from the variable stratum would shift
  the per-stratum precision dramatically (1 → 0 = 0%; 1 → 2 = 9.1%). The 86-finding
  population estimate inherits this fragility. Treat the variable-stratum number as the
  least-trustworthy component of the weighted estimate.
- **AMBIGUOUS findings (3) excluded from precision denominator** in both pre and post.
  If all 3 are TP, sample precision rises to 7/35 ≈ 20%; if all 3 are FP, it stays
  4/32 ≈ 12.5%. The headline 11% is computed without them; the band 8%–20% bounds the
  honest uncertainty.
- **28 of 38 silenced findings are outside the 45-sample.** The labels exist only for
  the 45; we infer that the unsampled silenced findings follow the same patterns as the
  in-sample silenced findings (10/10 of the in-sample silenced are labeled FP). This is
  an inference, not a measurement, and rests on the assumption that the sampling was
  representative across construction-form strata.
- **Per-stratum precisions are computed from the same 45-sample for both pre and post**
  — the sample was not re-drawn. Changes are driven purely by which sampled findings
  still fire post-fix.

---

## Deferred limitations (not addressed by this fix; logged)

| Pattern | In-sample exemplar | Bucket from KL-004 investigation |
|---------|-------------------|----------------------------------|
| Function-local `prompt = IfExp(...)` not propagated as static even when both branches resolve | None in sample (F41 fires via a different path; see below) | PR #5 binding-extraction gap (literal-only RHS) |
| F41 compound: IfExp branches are cross-module constants whose definitions are f-strings containing third-party interpolations → `_value_to_symbol` returns `None` → not exported by symbol table | F41 (`Shaurya-Sethi/circuitron` · `agents.py:176`) | Bucket (b)/(f) compound: cross-module f-string-with-FormattedValue not exportable as STR_LITERAL |
| Dict-of-literals subscript (`config["instructions"]`) | F25 | Bucket (c): needs container-literal tracking |
| Module-level `.format()` result assigned to a Name | F40 | Bucket (d): module-level Call results not exported |
| Comprehension/for-loop iterator variable over a literal container | F20 | Bucket (e'): comprehension scope deliberately excluded from binding extraction (§1.6 PR #5) |
| Constructor parameter, all call sites pass literal | F38 | Bucket (h): no call-site-literal traceback through parameter |
| Script-style absolute import where module path doesn't match the scanner's derived dotted path | F30 | Bucket (b): path-resolution mismatch |

Each is a localized scope-limit. None addresses Class (b) author-controlled FPs;
collectively, all of them together would shave a small additional fraction off the
remaining FP population, but the bulk of the residual FPs is the irreducible Class (b).

---

## Result framing — for downstream summaries

> IG002 false positives split into two classes. The **resolvable** class — callable-
> static-composition, third-party SDK constants, ternary-between-constants — is fixable
> by narrowing rules in `classify_prompt_expr` and is now substantially closed: the
> callable stratum collapsed 29 → 5 (−83%) and the f-string stratum trimmed 30 → 19
> (−37%). The **irreducible** class — author-controlled parameterization (library
> extension points, agent-authoring tools where user == author, factory parameters with
> deployment-time overrides) — is not fixable by static analysis alone, because closing
> it requires knowing *who controls a parameter at call time*: a deployment fact, not a
> code fact. The plain-variable stratum, which is dominated by Class (b), barely moved
> (89 → 86, −3%) and remains the floor on what IG002 can achieve as currently scoped.
>
> Numerically: pre-fix 148 findings / 8.1% population-weighted precision → narrowed
> 110 findings / 11.0% (+2.8 pp absolute, +35% relative). All 4 IG002 TPs fire across
> pre-fix, buggy-broad, and narrowed scans; one false-negative episode (PR #12's broad
> Call short-circuit) was caught in post-fix verification before any results were
> reported and is closed with a permanent regression test.
>
> Single labeler, n = 45 stratified sample, wide confidence at this scale. The
> variable-stratum estimate rests on 1 TP; treat as an estimate not a measurement.

---

## Complete per-finding pre/post table (all 45)

| ID | Stratum | Label | Pre | Narrowed | Class | Notes |
|----|---------|-------|-----|----------|-------|-------|
| F01 | callable | FP | fires | **silenced** | (a) | `STATIC_COMPOSER_FUNCTIONS` — `build_prompt` |
| F02 | callable | FP | fires | **silenced** | (a) | same |
| F03 | callable | FP | fires | **silenced** | (a) | same |
| F04 | callable | FP | fires | **silenced** | (a) | same |
| F05 | callable | FP | fires | **silenced** | (a) | same |
| F06 | callable | FP | fires | fires | (b-adjacent) | demo-data closure; correctly NOT silenced by narrowed analyzer (would be TP under real data) |
| F07 | callable | FP | fires | fires | (b-adjacent) | same |
| F08 | callable | FP | fires | fires | (b-adjacent) | same |
| F09 | f-string | FP | fires | **silenced** | (a) | `KNOWN_STATIC_NAMES` — `RECOMMENDED_PROMPT_PREFIX` |
| **F10** | f-string | **TP** | fires | **fires ✓** | — | TP preserved |
| F11 | f-string | FP | fires | **silenced** | (a) | SDK allowlist |
| F12 | f-string | FP | fires | **silenced** | (a) | SDK allowlist |
| F13 | f-string | FP | fires | fires | (b) | enum ternary (author-controlled) |
| **F14** | f-string | **TP** | fires | **fires ✓** | — | TP preserved |
| F15 | f-string | FP | fires | fires | deferred | KL-003 dedent defect |
| F16 | f-string | AMB | fires | fires | (b) | file content; origin-undeterminable |
| **F17** | f-string | **TP** | fires | **fires ✓** | — | TP preserved |
| F18 | f-string | FP | fires | fires | deferred | KL-003 dedent defect |
| F19 | f-string | FP | fires | **silenced** | (a) | SDK allowlist |
| F20 | f-string | FP | fires | fires | deferred | comprehension iterator over literal list |
| **F21** | plain variable | **TP** | fires | **fires ✓** | — | TP preserved |
| F22 | plain variable | FP | fires | fires | (b) | Decepticon library extension point |
| F23 | plain variable | FP | fires | fires | (b) | GUI-authored workflow JSON |
| F24 | plain variable | FP | fires | fires | deferred | cross-module f-string with SDK interp not exported |
| F25 | plain variable | FP | fires | fires | deferred | dict subscript |
| F26 | plain variable | FP | fires | fires | (b) | factory default param |
| F27 | plain variable | FP | fires | fires | deferred | third-party Call wrapper |
| F28 | plain variable | FP | fires | fires | (b) | HarnessConfig default |
| F29 | plain variable | FP | fires | fires | (b) | deer-flow factory param |
| F30 | plain variable | FP | fires | fires | deferred | script-style absolute import |
| F31 | plain variable | FP | fires | fires | (b) | Decepticon |
| F32 | plain variable | AMB | fires | fires | (b) | DB-sourced profile context |
| F33 | plain variable | FP | fires | fires | (b) | CrewAI Studio authoring UI |
| F34 | plain variable | FP | fires | **silenced** | (a) | SDK allowlist (f-string misclassified to variable stratum during sampling) |
| F35 | plain variable | FP | fires | fires | (b) | `SwarmSubAgent` config field |
| F36 | plain variable | FP | fires | fires | (b) | Decepticon |
| F37 | plain variable | FP | fires | fires | (b) | Decepticon |
| F38 | plain variable | FP | fires | fires | deferred | constructor parameter |
| F39 | plain variable | FP | fires | fires | deferred | KL-003 dedent (plain string) |
| F40 | plain variable | FP | fires | fires | deferred | module-level `.format()` Call result |
| F41 | plain variable | FP | fires | fires | deferred | IfExp + cross-module f-string-with-FV compound |
| F42 | plain variable | FP | fires | fires | (b) | `apply_prompt_template` from app-config |
| F43 | plain variable | FP | fires | fires | (b) | author-provided workspace markdown |
| F44 | plain variable | AMB | fires | fires | (b) | LLM-generated task description |
| F45 | plain variable | FP | fires | fires | (b) | Decepticon |

Summary: 10 silenced / 32 still firing (4 TP / 3 AMBIGUOUS / 25 FP). **TPs preserved: 4 / 4 ✓.**
