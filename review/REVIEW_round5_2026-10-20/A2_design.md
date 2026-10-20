# A2 — Study design / TRIPOD+AI methodology review (Round 5)

**Reviewer focus:** A2 — Study design / TRIPOD+AI methodology
**Manuscript:** `manuscript/manuscript_v0.1.md` (TRIPOD type 2b — development + internal + external validation)
**Scope:** Residual risks surviving 4 prior rounds. Not re-litigating settled decisions.
**Numbers cross-checked against:** `results/ext/external_validation.json` and `config/config_vitaldb.yaml`.

---

## Executive summary

The manuscript is unusually candid for this literature and most transportability caveats (anchor phase-shift, feature-meaning shift, denominator/exclusion rule, non-comparable AUPRC across prevalences) are disclosed in the abstract, methods, and limitations. The "transportability check" framing itself is **defensible** and should not be further downgraded to "exploratory" — but its defensibility is undermined by **residual internal inconsistencies** in how the external step is labelled and quantified:

1. The study calls itself a TRIPOD **type 2b (development + external validation)** (L98) and the title says "external validation in VitalDB" (L1), yet the body and abstract repeatedly call it a "transportability check" (L37, L179, L553). Worse, the Discussion calls it "external validation" again (L524, L633), contradicting the cautious framing. This classification mismatch is the single largest residual risk.
2. The headline **external AUROC 0.751 (53-feature model)** is repeatedly juxtaposed against the internal **AUROC 0.722 (full 206-feature model)** in the abstract (L36) and conclusions (L645), implying external ≥ internal. These are different feature sets; the like-for-like internal 53-feature values are 0.698/0.710 (L462–463).
3. The cumulative-burden **outcome label itself** is computed on MAP recorded at only 19.89% density with 96.2% isolated single minutes (L316–318). The exposure-fraction definition treats recorded readings as a representative sample of minute-to-minute MAP — an assumption violated by non-random sampling — yet the manuscript only states the definition is "feasible on sparse data" (L539) and never flags that the label may be biased.
4. Subgroup findings are presented as results in the abstract (L34) without the "exploratory" hedge that appears in the body (L390–394, L411–413), and Table 5 carries no CIs despite 8 strata × 2 splits.

None of these are fatal, but items 1–3 can materially mislead a reader skimming the abstract/conclusions. Verdict: **Major revisions** (on A2 grounds; the fixes are textual and cheap).

---

## Findings table

| Severity | Location | Issue | Concrete fix |
|---|---|---|---|
| MAJOR | L1, L98, L524, L633 | Study self-labelled TRIPOD type 2b "external validation" but body calls it "transportability check"; Discussion re-uses "external validation" | Harmonise terminology: either relabel title/methods as "adapted external application / transportability check" and drop "type 2b external validation," or keep type 2b but never call the VitalDB step "external validation" in the Discussion |
| MAJOR | L36, L645 | External AUROC 0.751 (53-feature) compared against internal 0.722 (206-feature) — apples-to-oranges | In abstract & conclusions compare 0.751 to the same 53-feature internal values 0.698/0.710, or state the feature set explicitly each time |
| MAJOR | L447 vs L524/L634 | "read as consistency rather than superiority" contradicts "above"/"exceeding the internal" | Pick one hedged phrasing ("consistent with, numerically similar to") and apply it everywhere |
| MAJOR | L128–130, L316–318, L539 | D1 outcome computed on non-random MAP (19.89% density, 96.2% single-minute) treated as representative; label-validity under sparsity not addressed | Add a limitation: exposure-fraction outcome assumes recorded MAP ≈ true MAP, violated under this density; state labels are a *proxy* and quantify sensitivity (e.g., re-run D1 on a density-stratified subset) |
| MINOR→MAJOR | L34, L390–394, L411–413, Table 5 | Subgroup AUPRC stated as fact in abstract; Table 5 has no CIs; no multiplicity note across 8 strata × 2 splits | Add "exploratory" caveat to abstract subgroup sentence; add CIs to Table 5 or an explicit "no inference intended" note |
| MINOR | L762 (Fig 1) only | No external validation participant flow diagram (TRIPOD items 3/13); external 6,388→3,735 is text-only (L188, L441) | Add an external-cohort flow sub-figure or a compact diagram |
| MINOR | L189–193 | The 53-feature transportable subset is not enumerated in the manuscript (only in config/code) | List the 53 features (or cite `config_vitaldb.yaml` KEEP_PREFIX explicitly) so the "same model" claim is auditable |
| MINOR | L193–197, L560–562 | anchor-meaning shift disclosed but its cost on the 53-feature model not quantified (anchor_is_intubation=0, re-derived interval) | Report internal 53-feature performance with anchor_is_intubation=0 / re-derived interval to isolate the adaptation penalty |

---

## Detailed findings

### F1 — Classification mismatch: "type 2b external validation" vs "transportability check" (MAJOR)

The manuscript is commended for honesty, but it is internally inconsistent about what the VitalDB step *is*.

- L1 (title): "development and internal validation in MOVER/SIS with **external validation** in VitalDB"
- L98 (methods): "TRIPOD type 2b (development with **internal and external validation**)"
- L37 (abstract): "since the external anchor (operation start) postdates induction, this is a **transportability check rather than a like-for-like validation**"
- L179 (methods): "As a **transportability check rather than a like-for-like external validation**…"
- L553 (limitations): "External validation was performed as a **transportability check**…"
- L524 (Discussion): "We now provide such an **external validation** ourselves, in VitalDB…"
- L633 (What this adds): "An honest **external validation** on an independent resource."

The anchor is shifted (operation start postdates induction) and three MOVER-specific features are set to 0 (L193–197; confirmed in `config_vitaldb.yaml` L66–68, L102). Under a strict TRIPOD+AI reading this is **not** a type-2b external validation — it is an adapted/exploratory external application. Calling it both "external validation" (title/type-2b/Discussion) and "transportability check" (abstract/methods/limitations) lets a reader pick the more flattering label.

**Concrete rewrite (title):** "…development and internal validation in MOVER/SIS with an *adapted external transportability check* in VitalDB."
**Concrete rewrite (L98):** "TRIPOD type 2b for the development and internal validation; the VitalDB step is reported as an *adapted external transportability check* (not a like-for-like external validation)."
**Concrete rewrite (L524/L633):** replace "external validation" with "transportability check" so the Discussion matches the abstract/methods/limitations.

### F2 — Apples-to-oranges AUROC comparison (0.751 vs 0.722) (MAJOR)

- L36 (abstract): "Externally (VitalDB, prevalence 5.7%), the unchanged model retained discrimination (AUROC 0.751 …)" — placed right after the internal AUROC 0.722 (L31), implying external ≥ internal.
- L645 (conclusions): "In an independent external cohort (VitalDB, n = 3,735) the same model retained discrimination (AUROC 0.751)…"

But 0.722 is the **full 206-feature** XGBoost (Table 4 L359), whereas 0.751 is the **53-feature** transportable subset (Table 7 L464). The like-for-like internal 53-feature values are **0.698 (patient)** and **0.710 (temporal)** (L462–463). The manuscript does state this in Table 7 footnote (L466–468), but the abstract and conclusions omit the feature-set qualification at the point of comparison, which is where readers form the impression.

**Concrete fix (abstract L36):** "Externally (VitalDB, prevalence 5.7%), the unchanged **53-feature** model retained discrimination (AUROC 0.751, 95% CI 0.713–0.784), consistent with the internal **53-feature** value of 0.698–0.710."
**Concrete fix (L645):** same feature-set qualifier.

### F3 — "consistency" vs "above/exceeding" contradiction (MAJOR)

- L447: "the confidence intervals overlap … so the difference should be read as **consistency rather than superiority**."
- L524: "the model's ranking ability transferred (external AUROC 0.751, **above** the internal 0.698–0.710 for the same 53-feature model)"
- L634: "discrimination transferred (AUROC 0.751, **exceeding** the internal 0.698–0.710 for the same feature set)"

"Above"/"exceeding" contradicts the hedged "consistency rather than superiority." Pick one. Recommended: "external AUROC 0.751 was numerically similar to / consistent with the internal 53-feature 0.698–0.710 (CIs overlap)."

### F4 — Outcome-label validity under severe sparsity not addressed (MAJOR)

The definition D1 (L126–130) counts recorded MAP readings: ≥10 post-anchor measurements, ≥30% <65 mmHg. Recording density is 19.89% of case-minutes and 96.2% of non-empty segments are isolated single minutes (L316–318). The manuscript correctly notes this caps performance and makes sustained-duration definitions unmeasurable (L539, L573–575), and that the 1,496 negative-by-construction cases are spectrum-biased (L591–597).

**Residual gap:** the exposure-fraction *outcome label itself* assumes the recorded MAP readings are a representative sample of true minute-to-minute MAP. At 19.89% density with isolated single minutes, recordings are almost certainly **not** random (nurses sample when concerned), so "≥30% of recorded readings <65" is a biased proxy for "≥30% of true minutes <65." This biases both the outcome and the by-construction exclusion, yet the manuscript only says D1 is "feasible on sparse data" (L539), not that it may be a biased proxy.

**Concrete fix (add to Limitations, after item 2 L575):** "The D1 outcome is an *exposure-fraction* label computed on intermittently recorded MAP (19.89% of case-minutes; 96.2% of recorded segments a single minute). It assumes recorded readings represent true minute-to-minute MAP; under this non-random sampling the label is a proxy whose sensitivity to recording density is unknown. We report conditional prevalence (17.1%) but did not quantify label bias by recording density."

### F5 — Subgroup claims stated as fact in abstract; no CIs / multiplicity note (MINOR→MAJOR)

- L34 (abstract): "Performance was higher in women and younger patients" — stated as a result, no "exploratory" hedge.
- Table 5 (L396–408) reports subgroup AUPRC with **no confidence intervals**, across 8 strata × 2 splits (16 comparisons), with no multiplicity adjustment. The body flags underweight (n=98) as unstable (L392–394, L411–413) but the abstract sentence is unconditional.

**Concrete fix (abstract L34):** "In exploratory subgroup analyses, AUPRC was numerically higher in women and younger patients (no formal inference; Table 5)."
**Concrete fix (Table 5 caption):** add bootstrap CIs for each stratum or append: "Subgroup AUPRCs are descriptive; no multiplicity adjustment was applied."

### F6 — Missing external participant flow diagram (MINOR; TRIPOD items 3/13)

TRIPOD+AI requires participant flow for both development and external cohorts. Internal flow is Figure 1 (L762). The external 6,388 → 3,735 (214 event-negative-by-construction) is text-only (L188, L441–442). Add a compact external-flow sub-figure or a one-panel diagram.

### F7 — 53-feature transportable subset not enumerated (MINOR)

The "unchanged 53-feature core model" claim (L189, L462) is not auditable from the manuscript — the subset lives only in `config_vitaldb.yaml` KEEP_PREFIX (L52–68) and code. Enumerate the 53 features in a table or explicitly cite the config file + KEEP_PREFIX so the "same model" assertion is verifiable.

### F8 — Cost of anchor/feature adaptation not quantified (MINOR)

The adaptation penalty is disclosed qualitatively (L195–197, L560–562) but not measured. Since `anchor_is_intubation` (rank 3 by gain, L429) is set to 0 for all VitalDB cases and `anchor_minus_or_start` is re-derived, the internal 53-feature model's performance *with these adaptations applied to MOVER* would isolate how much of the external gap is transportability error vs. population shift. Report that number; it directly strengthens the "transportability check" defensibility.

---

## Cross-checks against `external_validation.json`

- n_cases 3735 ✓ (L440, L464); n_d1_positive 214 ✓ (L442); prevalence 0.0573 ✓ (L442, L464).
- auprc 0.160 (CI 0.1291–0.2021) ✓ (L449, L464); auroc 0.7507 (CI 0.7133–0.7844) ✓ (L445, L464); brier 0.1789 ✓ (L453, L464).
- pred_mean 0.365 — manuscript rounds to 0.37 (L453, L571), acceptable.
- `config_vitaldb.yaml` confirms anchor = operation_start (L41), anchor_is_intubation=0 and or_year=0 withheld (L66–68), anchor_minus_or_start redefined to case-start (L67) — consistent with the manuscript's disclosed transportability caveats. No numerical discrepancy found.

---

## Verdict

**Major revisions.**

Rationale: The transportability framing is honest and defensible, and all primary caveats are disclosed. However, residual inconsistencies survive prior rounds: (F1) the study is simultaneously called "type 2b external validation" and "transportability check," with the Discussion re-asserting "external validation"; (F2) the headline 0.751 is juxtaposed against the unequal 0.722 in the abstract/conclusions; (F3) "consistency" vs "above/exceeding" contradict; and (F4) the outcome-label validity under 19.89% non-random MAP density is never flagged. F1–F4 can mislead a reader of the abstract and conclusions and should be corrected before publication. F5–F8 are lower-severity completeness/strengthening items. The required changes are textual and low-effort; no new analysis is mandated except the optional F4 sensitivity and F8 adaptation-penalty (both recommended, not blocking).
