# IG002 Post-Fix Delta — agentic-guard v0.2+57dc46b

**Pre-fix engine:** main @ `031e781` (Taxonomy matcher fix, pre PR #12)
**Post-fix engine:** main @ `57dc46b` (PR #12 squash: KL-002 + IfExp + SDK allowlist)
**Corpus:** 126 repos at pinned SHAs (same corpus as the frozen-eval scan)
**Re-scan date:** 2026-06-14
**Sample referenced:** `eval/ig002_sample.md` (45 findings, stratified, seed 42)
**Labels referenced:** `eval/ig002_labels.md` (4 TP, 3 AMB, 38 FP)

---

## Headline numbers

| Metric | Pre-fix | Post-fix | Δ |
|--------|---------|----------|---|
| Total IG002 findings (126-repo corpus) | **148** | **106** | **−42 (−28.4%)** |
| Sample (45) — labelable findings | 42 | 29 | −13 |
| Sample precision (TP / labelable) | **4/42 ≈ 9.5%** | **4/29 ≈ 13.8%** | +4.3 pp |
| Population-weighted precision estimate | **8.1%** | **11.4%** | +3.3 pp (≈ +40% relative) |
| **True positives lost** | — | **0** | **safety property held** |

---

## Critical safety check — all 4 TPs still fire

| ID | Repo · file:line | Pre-fix | Post-fix |
|----|------------------|---------|----------|
| F10 | `liangdabiao/crewai_stock_analysis_system` · `src/crews/data_collection_crew.py:207` | fires | **fires ✓** |
| F14 | `AbubakrChan/crewai-UI-business-product-launch` · `main.py:27` | fires | **fires ✓** |
| F17 | `liangdabiao/crewai_stock_analysis_system` · `src/crews/data_collection_crew.py:269` | fires | **fires ✓** |
| F21 | `xark-argo/argo` · `argo/backend/core/agent/tool_agent_runner.py:65` | fires | **fires ✓** |

**Zero true positives were lost.** Verified per (repo, file_path, line) match between pre-fix `ig002_findings.json` and post-fix re-scan output.

---

## Per-fix expected silencing — confirmed

### KL-002 (F01–F05, OpenCMO `build_prompt`)

All 5 silenced:

| ID | Pre | Post |
|----|-----|------|
| F01 | fires | silenced ✓ |
| F02 | fires | silenced ✓ |
| F03 | fires | silenced ✓ |
| F04 | fires | silenced ✓ |
| F05 | fires | silenced ✓ |

### SDK allowlist — `RECOMMENDED_PROMPT_PREFIX` (F09, F11, F12, F19, F34)

All 5 silenced:

| ID | Pre | Post |
|----|-----|------|
| F09 | fires | silenced ✓ |
| F11 | fires | silenced ✓ |
| F12 | fires | silenced ✓ |
| F19 | fires | silenced ✓ |
| F34 | fires | silenced ✓ |

### IfExp — F41

F41 (`Shaurya-Sethi/circuitron` · `circuitron/agents.py:176`) **still fires** post-fix.

**Why:** F41 is a compound case (IfExp + cross-module constant). The IfExp branches are `CODE_GENERATION_PROMPT` and `CODE_GENERATION_PROMPT_NO_FOOTPRINT`, both imported from `.prompts`. In `prompts.py`, each is defined as `f"""{RECOMMENDED_PROMPT_PREFIX}\n..."""` — an f-string with a third-party interpolation. `_value_to_symbol` only exports plain string literals or constant f-strings; an f-string with `FormattedValue` children returns `None`, so neither constant is exported as `STR_LITERAL` by `prompts.py`'s `ModuleSymbols`. The cross-module resolver therefore reports both branches as unresolved, the IfExp branch sees both as dynamic, and the expression stays dynamic.

This is bucket-(b)/bucket-(f) compound territory identified in the KL-004 investigation — Fix 2 (IfExp) alone is necessary but not sufficient for F41. The IfExp branch fires correctly for ternaries between literally-resolved constants (verified by the `test_ifexp_between_constants_no_findings` regression test). Population-wide impact of the IfExp branch is therefore non-zero but not measurable from the sample.

### Demo-data-conditional (F06–F08, `langgraph-swarm` `make_prompt`)

F06, F07, F08 silenced.

**Note on F06–F08:** Per the labels these are FP (demo-data-conditional). The post-fix analyzer silenced them via Fix 1 (KL-002 short-circuit) because `make_prompt(literal_str)` is a Call whose only Name is `make_prompt`, which resolves to a `function_def` in the same module. The narrowing rule says "all names resolve → static."

This is a subtle alignment: `make_prompt` does NOT return a static string — it returns a *closure* that reads `RESERVATIONS[user_id]` and `datetime.now()` at invocation time. The analyzer cannot see inside the returned closure, so the KL-002 fix silences this Call even though the closure is dynamic at runtime. Per the assigned labels, this is consistent (label = FP, silenced = no firing). In a deployment where `RESERVATIONS`/`FLIGHTS`/`HOTELS` were sourced from real user data instead of hardcoded toy lists, this would become a missed TP — the closure-staticness limitation should be tracked as a known scope of KL-002.

### AMBIGUOUS (F16, F32, F44)

All 3 still fire — the fixes do not target these patterns. Consistent with the pre-fix labels (origin-undeterminable, not unresolved-static).

### Author-controlled FPs (Decepticon cluster + 8 others)

All still fire — the fixes do not address author-controlled parameterization (would require deployment-context information).

---

## Per-stratum precision

| Stratum | Pre-fix pop | Post-fix pop | Pre TP/AMB/FP / labelable / precision | Post TP/AMB/FP / labelable / precision |
|---------|-------------|--------------|--------------------------------------|---------------------------------------|
| Callable/opaque | 29 | **1** | 0/0/8 / 8 / **0%** | 0/0/0 / 0 / *n/a* |
| F-string | 30 | **19** | 3/1/8 / 11 / **27.3%** | 3/1/4 / 7 / **42.9%** |
| Plain variable | 89 | **86** | 1/2/22 / 23 / **4.3%** | 1/2/21 / 22 / **4.5%** |
| **Total** | **148** | **106** | 4/3/38 / 42 / **9.5%** | 4/3/25 / 29 / **13.8%** |

Post-fix populations from re-running the v2 stratification classifier on the 106 post-fix findings. Post-fix per-stratum sample counts only include the still-firing sample findings (silenced ones are dropped from both numerator and denominator).

**Callable-stratum interpretation:** 28 of 29 callable-stratum population findings were silenced. The 1 surviving callable-stratum finding is outside the 45-sample so its label is unknown; per-stratum precision for callable is undefined post-fix.

---

## Population-weighted precision arithmetic

### Pre-fix (from `eval/ig002_labels.md`, reproduced)

```
P_pre = (29/148)(0/8) + (30/148)(3/11) + (89/148)(1/23)
      = 0 + 90/1628 + 89/3404
      = 3049/37444
      ≈ 0.0814 ≈ 8.1%
```

### Post-fix

Per-stratum sample precision applied to *post-fix* per-stratum populations:

```
P_post = (1/106) × (per-stratum precision for callable, n/a → drop)
       + (19/106)(3/7)
       + (86/106)(1/22)

       = 0  (callable contribution drops; 0 labelable in sample)
       + (19 × 3) / (106 × 7)
       + (86 × 1) / (106 × 22)

       = 57/742 + 86/2332

   57/742  ≈ 0.07682
   86/2332 ≈ 0.03688

P_post ≈ 0.07682 + 0.03688 = 0.11370 ≈ 11.4%
```

**Net change:** +3.3 percentage points absolute, ≈ +40% relative.

### Bounding the callable contribution

We dropped the callable stratum from the weighted sum because the post-fix sample has zero labelable findings in that stratum. If the 1 surviving callable-stratum finding were a TP, the contribution would be `(1/106)(1/1) ≈ 0.0094`, lifting `P_post` to ≈ 12.3%. If it were FP, contribution is 0 and `P_post` stays 11.4%. Either way, the headline conclusion ("precision improved by ~3.3 pp absolute") is preserved.

---

## Caveats

- Single labeler, n=45 stratified sample.
- AMBIGUOUS findings (3) excluded from precision denominator in both pre and post; their proportion is unchanged.
- 29 of 42 silenced findings are outside the 45-sample. We have not labeled the unsampled silenced findings; we project from the labels of the in-sample silenced findings (13/13 FP per labels) that the unsampled silenced findings follow the same patterns. This is an inference, not a measurement.
- Per-stratum precisions are computed from the same sample for both pre and post — the sample wasn't re-drawn, so changes are driven by which sampled findings still fire post-fix.
- The post-fix population stratification used the same v2 classifier as the pre-fix profile; counts may shift by 1–2 due to taint-extraction differences after the fix (e.g., the SDK-allowlisted `RECOMMENDED_PROMPT_PREFIX` no longer appears in taint lists, changing some f-string findings to "no taints → callable" classification by the v2 heuristic).

---

## Complete pre/post status table (all 45)

| ID | Stratum | Label | Pre | Post | Notes |
|----|---------|-------|-----|------|-------|
| F01 | callable | FP | fires | silenced | KL-002 `build_prompt` |
| F02 | callable | FP | fires | silenced | KL-002 |
| F03 | callable | FP | fires | silenced | KL-002 |
| F04 | callable | FP | fires | silenced | KL-002 |
| F05 | callable | FP | fires | silenced | KL-002 |
| F06 | callable | FP | fires | silenced | demo-data closure; silenced via KL-002 rule |
| F07 | callable | FP | fires | silenced | demo-data closure |
| F08 | callable | FP | fires | silenced | demo-data closure |
| F09 | f-string | FP | fires | silenced | SDK `RECOMMENDED_PROMPT_PREFIX` |
| **F10** | **f-string** | **TP** | **fires** | **fires ✓** | **TP preserved** |
| F11 | f-string | FP | fires | silenced | SDK |
| F12 | f-string | FP | fires | silenced | SDK |
| F13 | f-string | FP | fires | fires | enum ternary (author-controlled) |
| **F14** | **f-string** | **TP** | **fires** | **fires ✓** | **TP preserved** |
| F15 | f-string | FP | fires | fires | KL-003 dedent |
| F16 | f-string | AMB | fires | fires | file content |
| **F17** | **f-string** | **TP** | **fires** | **fires ✓** | **TP preserved** |
| F18 | f-string | FP | fires | fires | KL-003 dedent |
| F19 | f-string | FP | fires | silenced | SDK |
| F20 | f-string | FP | fires | fires | loop var over literal list |
| **F21** | **plain variable** | **TP** | **fires** | **fires ✓** | **TP preserved** |
| F22 | plain variable | FP | fires | fires | Decepticon library param |
| F23 | plain variable | FP | fires | fires | GUI-authored JSON |
| F24 | plain variable | FP | fires | fires | cross-module f-string with SDK interp |
| F25 | plain variable | FP | fires | fires | dict subscript |
| F26 | plain variable | FP | fires | fires | default-static param |
| F27 | plain variable | FP | fires | fires | third-party Call wrapper |
| F28 | plain variable | FP | fires | fires | HarnessConfig default |
| F29 | plain variable | FP | fires | fires | factory param |
| F30 | plain variable | FP | fires | fires | script-style import |
| F31 | plain variable | FP | fires | fires | Decepticon |
| F32 | plain variable | AMB | fires | fires | DB-sourced profile context |
| F33 | plain variable | FP | fires | fires | CrewAI Studio UI |
| F34 | plain variable | FP | fires | silenced | SDK (misclassified stratum) |
| F35 | plain variable | FP | fires | fires | SwarmSubAgent config |
| F36 | plain variable | FP | fires | fires | Decepticon |
| F37 | plain variable | FP | fires | fires | Decepticon |
| F38 | plain variable | FP | fires | fires | constructor param |
| F39 | plain variable | FP | fires | fires | KL-003 dedent (plain string) |
| F40 | plain variable | FP | fires | fires | module-level `.format()` Call result |
| F41 | plain variable | FP | fires | fires | IfExp + cross-module f-string constant (compound) |
| F42 | plain variable | FP | fires | fires | `apply_prompt_template` |
| F43 | plain variable | FP | fires | fires | workspace markdown files |
| F44 | plain variable | AMB | fires | fires | LLM-generated task description |
| F45 | plain variable | FP | fires | fires | Decepticon |

**Summary:**
- Still firing: 32 / 45 (4 TP, 3 AMB, 25 FP)
- Silenced: 13 / 45 (0 TP, 0 AMB, 13 FP) — every silenced finding was a labeled FP
- TPs preserved: **4 / 4 ✓**

---

## Result framing

**The fix worked, modestly.** Population-weighted IG002 precision improved from ~8% to ~11% — a 40% relative reduction in FPs without any TP loss. The biggest single effect was the SDK allowlist + KL-002 generic-Call short-circuit, which together eliminated the entire callable-stratum population (28 of 29) and the RECOMMENDED_PROMPT_PREFIX f-string cluster.

**The variable-stratum FP rate is essentially unchanged** (4.3% → 4.5%), because the variable stratum is dominated by author-controlled parameterization (Decepticon library cluster, factory params, agent-authoring tools) which fundamentally requires deployment-context information that static analysis can't provide. Those patterns will not be addressable by any narrowing extension to `classify_prompt_expr` alone.

**One known scope-limit of Fix 1 to track:** the KL-002 short-circuit can silence closure-returning callables (F06–F08 pattern) whose closures read dynamic state at invocation time. Per the labels these were FP, but in a real-data deployment they would be TP and the analyzer would now miss them. The fix is correct in its current narrowing form (all names provably resolve) but should be revisited if interprocedural analysis becomes available.
