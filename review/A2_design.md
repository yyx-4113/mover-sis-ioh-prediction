# Reviewer A2 — Design / Biostatistical Methodology Review

**Manuscript:** Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction
**Target journal:** BMC Anesthesiology
**TRIPOD type:** 2a (development + internal validation only), reported under TRIPOD+AI
**Reviewer role:** Independent design reviewer (biostatistics / clinical-prediction-model methodology / epidemiology)
**Independence note:** This review was written without access to other reviewers' reports or the author's response; every verifiable claim below was re-checked against the supplied source artifacts (`s1_*`–`s4_*` result files, `config.yaml`, `scripts/s3_models.py` where relevant).

---

## Issue 1 — The "every number is traceable" claim (lines 192–195) is demonstrably false

**【Problem】** The manuscript states verbatim: *"Every number reported in this manuscript is generated from a result file by the analysis pipeline and is traceable through an audit trail (Additional file 1) that records, for each quantity, its value, the producing artefact and the command that reproduces it."* This is overstated. Several numbers that appear in the manuscript are **absent from `s4_audit_trail.csv`**.

**【Evidence】**
- **Temporal calibration (lines 340–341):** "Brier 0.194→0.122, slope 0.934, intercept 0.006." `s4_audit_trail.csv` contains only `calib.patient.*` (rows 72–75: `brier_raw=0.1905`, `brier_calibrated=0.119`, `slope=0.9092`, `intercept=0.0083`). There is **no `calib.temporal.*` row at all**. The temporal values are present only in `s3_calib_dca.json` (brier_raw 0.1935, brier_calibrated 0.1217, calib_slope 0.9338, calib_intercept 0.0058) — i.e., they exist in a result file but are *not* in the audit trail that the manuscript claims is exhaustive.
- **All DCA net-benefit numbers (lines 343–346):** "up to 0.58 (patient) and up to 0.45 (temporal)"; "at a threshold of 0.15 … 0.050 and 0.058"; "at a threshold of 0.10 … 0.079 and 0.085." **No `net_benefit_*` row exists anywhere in `s4_audit_trail.csv`** (verified by scanning all 94 rows). These values are reproducible only from `s3_calib_dca.json`.
- **Table 1 cohort descriptive statistics (lines 208–242):** median age 54 (IQR 39–66), sex counts, height/weight/BMI medians, anchor timings, all 14 surgical-group counts, pre-anchor MAP medians (87.7 mmHg), and domain-availability counts (invasive 2,503; ventilation 4,852; labs 76; fluid 2,794) — none of these appear in the audit trail.
- **Recording-density statistics (lines 284–288):** "MAP recorded in 19.89% of case-minutes", "96.2% of segments are single minutes" — absent from the audit trail (the audit trail does record `features.coverage.*` percentages, but not these density figures).

**【Why it matters】** For a methods journal (BMC Anesthesiology) and under TRIPOD+AI's emphasis on transparency and reproducibility, an unqualified "every number" claim that is false undermines the credibility of the otherwise genuinely useful audit-trail infrastructure. It is also an internal-consistency defect: the audit trail is real and good, but the manuscript over-claims its coverage.

**【Specific fix】** Either (a) expand `s4_audit_trail.csv` to include every reported scalar — at minimum the temporal calibration block (`calib.temporal.brier_raw`, `brier_calibrated`, `slope`, `intercept`), the DCA net-benefit values at the thresholds cited (0.10, 0.15, and the crossing thresholds 0.58/0.45), the Table 1 descriptive statistics, and the recording-density percentages; or (b) soften the claim to something defensible, e.g., *"Every modeling-performance number in Tables 2, 4, 5 and 6, and the calibration block, is traceable through the audit trail (Additional file 1); cohort descriptive statistics and decision-curve values are reproducible from `s3_calib_dca.json` and `s2_data_quality.json`."* Option (a) is strongly preferred.

---

## Issue 2 — Subgroup analysis (Table 5, lines 348–368): dataset ambiguity, missing n, and no pre-specification

**【Problem】** The subgroup AUPRC table is internally ambiguous about (i) which dataset the AUPRC was computed on, (ii) why n is missing for three rows, and (iii) whether the subgroups were pre-specified or exploratory.

**【Evidence】**
- The `n` column for sex and age rows matches **full-cohort** counts from Table 1 (Men 8,355, Women 8,502, Age<50 6,915, Age50–65 5,366, Age≥65 4,580 — which sum to 16,861) and BMI<18.5 = 512. If the subgroup AUPRC were a held-out internal-validation estimate, n should be the *test-set* subgroup size (~20% of these). The fact that n equals the full-cohort count strongly suggests the subgroup AUPRC was computed on the **full cohort (train+test combined)**, not the held-out test set. The manuscript never states which.
- Three of nine rows — BMI 18.5–24.9, 25–29.9, ≥30 — show "—" for n (line 366–368), while the other six rows report n. There is no stated reason.
- The subgroups are not flagged as pre-specified vs exploratory, and no multiplicity consideration is given despite nine subgroup contrasts.

**【Why it matters】** If subgroup AUPRCs are computed on the full cohort, they are **not** internal-validation (held-out) estimates and are optimistic; they are not directly comparable to the primary Table 4 test-set estimates and would violate TRIPOD's requirement that performance be reported on the validation set. Mixed/omitted n also prevents the reader from judging precision and event counts per stratum.

**【Specific fix】** (1) State explicitly, in the Methods and in the Table 5 footnote, that subgroup AUPRCs are computed on the **test set** (or, if on the full cohort, relabel them as descriptive/exploratory and do not present them alongside held-out estimates). (2) Report n (and ideally event n) for **every** row, including the three BMI rows; if the full-cohort n is intended, say so and reconcile with the AUPRC computation set. (3) Add one sentence stating the subgroups were **exploratory** (post hoc) and that no multiplicity adjustment was applied, so the patterns (especially the unstable underweight stratum) should be interpreted with caution.

---

## Issue 3 — Leakage audit is sound for timestamps but is not a feature-provenance audit; counting inconsistency

**【Problem】** The leakage audit demonstrates that no used observation carries a post-anchor timestamp, but it does not (and cannot, as constructed) prove that *no post-anchor information leaks through any other route*. There is also a 7-vs-10 counting inconsistency between the text and Table 3.

**【Evidence】**
- `s2_data_quality.json` `leakage_audit` records 7 source tables, each with `max_used_time_minus_anchor = 0.0` and `n_time_nat = 0`. The field name `max_used_time_minus_anchor` is the maximum of (observation_time − anchor_time) among rows that survived the leak filter; a value of 0.0 means no surviving row is *after* the anchor. This is a genuine, correct check that the primary temporal-leakage route (using future vitals/labs/medications) is closed. The audit trail CSV (rows 28–34) and Table 3 (lines 294–305) are consistent with this.
- However, the audit operates at the level of **raw source rows**, not at the level of the 206 engineered features. It does not independently confirm that every derived feature (e.g., `map_frac_below_65`, the anchor-proxy indicators) was constructed strictly from the pre-anchor window. The burden of proof rests on the feature-engineering code, which is outside the audit.
- Two leakage-relevant design facts the audit does *not* capture: (a) the outcome label depends on the *count* of post-anchor measurements (the negative-by-construction rule), and (b) the anchor source itself (`anchor_is_intubation`, gain 72.2 — the 3rd most important predictor, `s3_feature_importance.json`) is a post-hoc categorization. Neither is a timestamp leakage, but both can carry post-anchor *information* indirectly (see Issues 4 and 6).
- Text line 147 says "across all **seven** time-stamped domains" while Table 3 shows `Max interval to anchor = 0.00` for **ten** non-static domains (Anchor, Anaesthesia technique, Medication, NIBP, Derived NIBP, QA, Ventilation, Invasive, Fluid, Labs). The "seven" refers to the seven underlying source tables; Table 3 presents ten feature-domain rows.

**【Why it matters】** TRIPOD+AI reviewers will probe leakage rigorously. The audit is a strength, but the manuscript should not imply it is a complete feature-level leakage certification.

**【Specific fix】** (1) Reword lines 146–148 to state precisely what was audited: *"no used observation had a timestamp after the anchor (maximum (t−anchor) = 0 across the seven underlying source tables; zero unparseable timestamps)."* (2) Add a sentence clarifying that the audit is a row-level timestamp check and that feature construction was additionally constrained to the pre-anchor window by design (point the reader to the feature-engineering script). (3) Reconcile the "seven" vs "ten" wording (e.g., footnote Table 3: "seven source tables map to the ten non-static feature domains shown").

---

## Issue 4 — Uncalibrated Brier is worse than the no-information Brier; "mild over-fitting" understates this

**【Problem】** The uncalibrated XGBoost Brier (0.1905 patient, 0.1935 temporal) is **higher** than the Brier of a trivial constant predictor, indicating substantial miscalibration — not merely "mild over-fitting" as stated (line 339).

**【Evidence】**
- No-information Brier = prevalence × (1 − prevalence) = 0.1555 × 0.8445 = **0.1313**.
- Patient raw Brier = 0.1905 (`s3_calib_dca.json`, also `s4_audit_trail.csv` row 56) > 0.1313. Temporal raw Brier = 0.1935 > 0.1313.
- After isotonic recalibration, Brier falls to 0.119 (patient) and 0.1217 (temporal), both **below** 0.1313 — i.e., recalibration is what makes the model's predictions better than predicting the average.

**【Why it matters】** A raw Brier worse than the constant-predictor Brier means the uncalibrated model is over-confident and its probability outputs are not usable as-is. Framing this as "mild over-fitting" understates the calibration problem and under-sells the importance of the recalibration step, which is in fact essential here rather than cosmetic.

**【Specific fix】** Revise lines 338–339 to state that the uncalibrated model was materially miscalibrated (raw Brier exceeded the no-information Brier of 0.131) and that isotonic recalibration was required to bring predictions to a usable calibration. Also clarify the terminology around the reported slope/intercept (see Issue 5).

---

## Issue 5 — Calibration "slope/intercept" terminology vs isotonic method is ambiguous

**【Problem】** The manuscript reports a "calibrated calibration slope of 0.909 and intercept of 0.008" (line 339) as if produced by isotonic recalibration, but isotonic regression has no slope/intercept parameters.

**【Evidence】** `config.yaml` `calibration: "isotonic_oof"`; `s3_calib_dca.json` reports `calib_slope`/`calib_intercept` alongside `calibration: "isotonic_oof"`. A slope/intercept pair is the output of a *logistic* recalibration (or a linear fit to the calibration plot), not of isotonic regression. The manuscript does not state how slope/intercept were obtained.

**【Why it matters】** Methodological clarity; a reader cannot tell whether a second (parametric) recalibration was applied on top of isotonic, or whether slope/intercept describe a linear fit to the isotonic curve.

**【Specific fix】** State explicitly: e.g., *"After isotonic recalibration, a logistic recalibration slope/intercept was 0.909/0.008 (patient)"* or *"the calibration slope/intercept were estimated by regressing the outcome on the recalibrated log-odds."* Distinguish the recalibration method from the summary metrics.

---

## Issue 6 — DCA "up to 0.58 / 0.45" is correct, but the framing is misleading and contradicts the Discussion

**【Problem】** The DCA claim (lines 343–346) is numerically verified, but two presentation issues remain: (a) the net benefit at the stated upper thresholds is essentially zero, so "positive up to 0.58" overstates the *clinically useful* range; (b) the Discussion (lines 401–403) states usefulness "up to about 0.20," contradicting the Results' 0.58/0.45.

**【Evidence】**
- `s3_calib_dca.json` patient `net_benefit_model`: last positive value is at threshold **0.58** = 9.88e-05 (≈0.0001), and it becomes negative at 0.59. Temporal: last positive at **0.45** = 0.00055, negative at 0.46. So "positive up to 0.58 (patient) / 0.45 (temporal)" is **correct** — the model's net benefit exceeds both `treat_all` and `treat_none` up to those thresholds. (This is *not* inconsistent with the data; the task's hypothesized inconsistency does not hold.)
- At those boundary thresholds the net benefit is ~0.0001–0.0005 — clinically negligible. The net benefit is substantial only at low thresholds (it peaks near threshold 0.01–0.05). So "positive up to 0.58" is technically true but practically vacuous at the top end.
- Discussion line 402–403: *"clinically usable in a decision-analytic sense across threshold probabilities up to about 0.20"* — this is **inconsistent** with the Results statement of 0.58/0.45 and with the DCA data.

**【Why it matters】** Internal inconsistency between Results and Discussion; and an over-generous reading of the DCA upper bound could mislead clinicians about where the model helps.

**【Specific fix】** (1) Align the Discussion with the DCA: state that net benefit exceeds both default strategies up to ~0.58 (patient) / ~0.45 (temporal), but that the *magnitude* is meaningful only at low thresholds, and report the threshold of maximum net benefit. (2) Optionally annotate Figure 4's DCA panel with the crossing points.

---

## Issue 7 — Anchor proxy (limitation #5, lines 466–467) is under-discussed given its predictive weight

**【Problem】** The proxy anchor (Surgery start for 18.0%) is flagged only briefly, yet the anchor source is itself a top predictor, suggesting the model may exploit proxy-driven heterogeneity.

**【Evidence】** `s3_feature_importance.json`: `anchor_is_intubation` gain = 72.16 (rank 3, after `map_mean` 175.5 and `map_max` 75.2). So ~18% of cases being anchored at Surgery start materially contributes to discrimination. Surgery-start-anchored cases may have different pre-anchor data density and different case complexity, so the anchor type can act as a proxy for unmeasured severity.

**【Why it matters】** A top predictor that is an artifact of anchor assignment (rather than physiology) can inflate apparent performance and reduce transportability. The limitation should acknowledge this explicitly, not just note "the direction of bias is uncertain."

**【Specific fix】** Expand limitation #5 to note that `anchor_is_intubation` is among the strongest predictors, that the proxy may encode case-mix/recording-density heterogeneity, and that external validation on data with consistent intubation recording is needed to separate this effect from physiology.

---

## Issue 8 — Negative-by-construction (1,496 cases, 8.9%) creates spectrum bias and dilutes the headline prevalence

**【Problem】** Cases with <10 post-anchor MAP measurements are forced to the negative label; this is defensible but biases the reported prevalence and risks spectrum bias.

**【Evidence】**
- `s1_outcomes_postanchor.json`: D1 positive = 2,622, denominator = 16,861, prevalence = 0.1555. The 1,496 negative-by-construction cases are included in the denominator.
- 1,496 / 16,861 = 8.87% ≈ 8.9% (line 123) ✓.
- Conditional prevalence *among cases with ≥10 measurements* = 2,622 / (16,861 − 1,496) = 2,622 / 15,365 = **17.06%**, diluted to the headline 15.55%.
- The negative-by-construction status depends on the *number* of post-anchor measurements, which is a post-anchor quantity and may be non-random (e.g., shorter surgeries, different monitoring intensity). If sparse-recording cases differ systematically, labeling them negative is a spectrum-bias source.

**【Why it matters】** The headline prevalence (and any AUPRC/lift computed against it) is diluted; the handling choice affects generalizability and should be stress-tested.

**【Specific fix】** Add a sensitivity analysis: (a) report conditional prevalence (17.06%) alongside the diluted 15.55%; (b) re-fit/score after excluding the 1,496 (or after a label-uncertainty treatment) to show stability; (c) in limitation #7, explicitly name the spectrum-bias risk rather than only listing it as a structural exclusion.

---

## Issue 9 — Bootstrap CIs are honestly described but should be framed as test-set (not optimism-corrected) CIs

**【Problem】** The 1,000-bootstrap CIs are described accurately as "of the test set" (line 180), but the manuscript does not make explicit that they quantify *test-set sampling variability*, not optimism or generalizability, and a single random split's CI is sensitive to that particular split.

**【Evidence】** `config.yaml`: `bootstrap_resamples: 1000`, `bootstrap_level: "patient"`. `s3_metrics.json` provides `auprc_ci95` / `auroc_ci95` per model-split. The manuscript does not claim optimism correction — so it is not dishonest — but the distinction is implicit.

**【Why it matters】** Readers may read the CI as a generalization interval. For internal validation, optimism-corrected CIs (bootstrap of the full train→validate pipeline, e.g., Harrell's method) or repeated (k-fold / multiple random) splits would better characterize uncertainty and stability.

**【Specific fix】** Add one sentence: *"The bootstrap CIs quantify sampling variability of the single test-set estimate and are not optimism-corrected; stability was additionally assessed via the temporal split and (optionally) repeated random splits."* Consider adding optimism-corrected CIs or a small repeated-split analysis as a robustness check.

---

## Issue 10 — TRIPOD+AI compliance: a completed checklist is not provided

**【Problem】** The manuscript states it is "reported in accordance with TRIPOD+AI" (line 91) but does not reference a completed TRIPOD+AI checklist as a supplementary file.

**【Evidence】** No TRIPOD+AI (or TRIPOD) checklist is mentioned in the manuscript text, Additional files (lines 615–618 list only the audit trail), or declared. TRIPOD+AI explicitly requires submission of a completed checklist.

**【Why it matters】** BMC Anesthesiology / TRIPOD+AI submissions are expected to include the checklist; its absence is a straightforward but real compliance gap.

**【Specific fix】** Complete the TRIPOD+AI checklist (type 2a) and submit it as Additional file 2; cite it in the Methods (line 91) and in Additional files.

---

## Minor / observational notes (no rewrite required, but worth a sentence)
- **AUPRC as primary metric (lines 178, 312–313):** choice is justified by 15.55% prevalence; lift 0.3473/0.1555 = 2.233 → "2.23×" is correct. Reasonable. One caveat to state: because the baseline logistic already reaches 1.50× prevalence (0.234), the *incremental* lift of XGBoost over the simplest clinical model is ~1.48×, which is the more conservative framing.
- **Temporal split validity (lines 174–176, 318–319):** `config.yaml` `train_end: 2017-12-31`, `test_start: 2018-01-01` verified; n_train 15,043 / n_test 1,818 verified against `s3_metrics.json`. Valid drift check; note the test window is short (<10 months, data ends 2018-10-03) and the temporal AUROC CI is wide (0.703–0.762), so "no material drift" is a reasonable but not high-powered conclusion.
- **Outcome-definition sensitivity (Table 2):** a genuine strength — 14 definitions with full prevalence range reported; this directly motivates the chosen D1. Well done.

---

## § Stands up (things done well)
1. **Honest, non-overclaimed discrimination framing.** The Discussion consistently calls AUPRC 0.347 / AUROC 0.722 "modest but non-null" and explicitly resists the near-perfect-discrimination claims in the literature (lines 397–440). This is appropriate and commendable for a methods-focused paper.
2. **Explicit, re-computable leakage audit.** The row-level timestamp check (`max(t−anchor)=0`, zero unparseable timestamps across seven source tables) is a real, verifiable safeguard and a genuine contribution to transparency in this literature.
3. **Outcome-definition sensitivity analysis (Table 2).** Reporting all 14 candidate definitions with prevalence spanning 0.01%–65.8% is exactly the kind of honesty about task-definition sensitivity that the field needs.
4. **Temporal validation showing no drift**, plus a public reproduction package (code, config, audit trail, MANIFEST) — strong reproducibility posture (marred only by the overstated "every number" claim in Issue 1).
5. **The DCA and calibration numbers themselves are correct** (verified against `s3_calib_dca.json` to 3–4 significant figures), and the "up to 0.58 / 0.45" claim is accurate, not the inconsistency hypothesized.

---

## § Questions for the authors
1. On which dataset were the Table 5 subgroup AUPRCs computed — the held-out test set, or the full cohort? The n values (e.g., Men 8,355) match full-cohort counts, which suggests full-cohort computation; please clarify and, if full-cohort, relabel as exploratory.
2. Given the "every number is traceable" claim (lines 192–195), why are the temporal calibration block and all DCA net-benefit values absent from `s4_audit_trail.csv`? Will the audit trail be expanded to cover them (and Table 1 / recording-density statistics)?
3. `anchor_is_intubation` is the 3rd strongest predictor (gain 72.2). Have you examined whether its predictive contribution reflects physiology or the anchor-proxy / case-mix heterogeneity discussed in limitation #5?
4. Was the 1,496 negative-by-construction handling sensitivity-analyzed (exclude vs label-negative)? What is the conditional prevalence among the ≥10-measurement cases, and how stable are the metrics to this choice?

---

## § What I actually checked
- **Manuscript:** `manuscript_v0.1.md` (full read), cross-referencing every quantitative claim to source files.
- **`s4_audit_trail.csv` (94 rows):** confirmed it contains cohort/anchor/outcome counts, feature n & coverage, the 8 model-split AUPRC/AUROC/Brier, `calib.patient.*` (4 rows), 18 subgroup AUPRCs, and 10 importance values. Confirmed **absence** of `calib.temporal.*` and of any `net_benefit_*` row.
- **`s3_calib_dca.json`:** verified patient/temporal calibration (Brier raw/calibrated, slope, intercept) and the full DCA `net_benefit_model`/`treat_all`/`treat_none` arrays; recomputed the last-positive thresholds (patient 0.58 = 9.88e-05; temporal 0.45 = 0.00055) and the cited NB values at 0.10/0.15.
- **`s3_metrics.json`:** verified AUPRC/AUROC point estimates and 95% CIs for all 8 model-split combinations against Table 4 and the Abstract.
- **`s3_subgroups.json`:** verified all nine patient and nine temporal subgroup AUPRCs match Table 5 within rounding.
- **`s3_feature_importance.json`:** verified Table 6 top-10 gains; noted `anchor_is_intubation` = 72.16 (rank 3).
- **`s2_data_quality.json`:** verified the 7-table leakage audit (all `max_used_time_minus_anchor=0.0`, `n_time_nat=0`), domain coverage, anchor-source counts, and vitals-window statistics.
- **`s1_outcomes_postanchor.json` / `s1_cohort.json`:** verified D1 prevalence 0.1555 (2,622/16,861), the 1,496 negative-by-construction share (8.87%), and cohort exclusion counts (8 / 1,632 / 371 / 242) against Figure 1.
- **`config.yaml`:** verified temporal-split boundaries (train_end 2017-12-31, test_start 2018-01-01), seed 12,345, bootstrap 1,000, calibration `isotonic_oof`, anchor_event/fallback.
- **Recomputations:** no-information Brier = 0.1555×0.8445 = 0.1313 (vs raw 0.1905/0.1935); conditional prevalence among ≥10-measurement cases = 2,622/15,365 = 17.06%; AUPRC lift = 0.3473/0.1555 = 2.233.

---

## § Verdict
**Major revision.**

The underlying science is sound and, importantly, *honest*: the discrimination is correctly framed as modest, the leakage audit is a genuine safeguard, the outcome-definition sensitivity analysis is exemplary, and the calibration/DCA numbers are numerically correct (the hypothesized "up to 0.45" inconsistency does not exist). However, two defects are substantial enough to require revision before acceptance:

1. **The unqualified "every number is traceable" claim (lines 192–195) is false** — the temporal calibration block and *all* DCA net-benefit values (and Table 1 / recording-density statistics) are missing from the audit trail. This is a reproducibility/integrity claim that must be corrected or the audit trail expanded.
2. **The subgroup analysis (Table 5) is ambiguous and partly incomplete** — it is unclear whether AUPRCs are held-out or full-cohort, n is missing for three rows, and pre-specification/multiplicity are unaddressed.

Together with the moderate issues (understated miscalibration in Issue 4, the Discussion↔Results DCA inconsistency in Issue 6, under-discussed anchor-proxy in Issue 7, spectrum bias in Issue 8, and the missing TRIPOD+AI checklist in Issue 10), the manuscript needs a revision round. None of these require new data or new modeling; they are clarifications, a traceability fix, and a subgroup-reporting fix. After these are addressed, the paper would be suitable for BMC Anesthesiology.
