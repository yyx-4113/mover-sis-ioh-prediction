# A1 — Clinical / domain review (anaesthesiology, intraoperative hypotension, perioperative prediction models)

**Manuscript:** `manuscript/manuscript_v0.1.md` — MOVER/SIS development + VitalDB external check, target *BMC Anesthesiology*
**Reviewer stance:** first submission, independent. All quantitative statements below were recomputed by me from the artefacts or from the raw MOVER CSVs; nothing is taken on trust from the manuscript or from prior rounds.

**中文摘要（一句话）**：论文方法学扎实、多数数字可追溯且水文密度报告诚实，但主要结局 D1 并非真正的"累积时间剂量"、外部队列的同一标签已变成另一种暴露定义、亚组 AUPRC 差异几乎完全由各层患病率驱动、以及外推"概率未迁移"实为未校准模型所致——这四项足以构成大修；另有多处文本级缺陷（含一段残缺的 Limitations 段落）需先修复。

---

## Executive summary

The paper is unusually self-critical for this literature: the leakage audit is real, the recording-density reporting is real, the MAP-only benchmark is real, and the Interpretation/Discussion concede openly that the model is largely an extrapolation of current pre-anchor pressure. Almost every number in the tables traces to an artefact, and the ones I could recompute from raw data (anthropometric cleaning, the pre-OR baseline claim, the anchor-timing IQR) are correct.

However, four problems are serious enough to require major revision, and one of them goes to the identity of the endpoint:

1. **D1 is a proportion of *recorded samples*, not a cumulative time-dose.** The number of sub-65 mmHg readings required for a positive label scales from 3 to 77 across the cohort purely as a function of how often the nurse recorded a blood pressure. The title, Abstract and Background all call this "cumulative burden".
2. **In VitalDB the same "D1" label is a genuine time-dose.** Because MAP is sampled ~30×/minute there, "≥30% below 65 mmHg" means roughly 44 cumulative minutes below threshold, versus ~9 isolated readings in MOVER. The Methods statement that "the outcome D1 was computed identically" is therefore false in the only sense that matters.
3. **The subgroup AUPRC ordering is a prevalence artefact.** Stratum prevalence and subgroup AUPRC correlate at Spearman ρ = 0.88 (p = 0.0016); once normalised by prevalence there is no age gradient and no sex difference. The Abstract-level claim "Performance was higher in women and younger patients" does not survive normalisation.
4. **The external "probabilities did not transfer" conclusion is an artefact of what was transported.** The raw class-weighted model is already grossly miscalibrated *internally* (mean predicted risk 0.404 vs prevalence 0.156); the internally isotonic-recalibrated model — the actual deployable artefact — was never applied externally.

In addition the Limitations section contains a **truncated, unnumbered paragraph fragment** (lines 606–612) whose opening sentence is missing, and the "What this study adds" section says it contributes "four elements" and then lists five.

**Verdict: Major revisions.** Single most improving change: re-specify and re-label the outcome so that it is either an honest time-based cumulative exposure or an honestly named sample proportion, recompute the external check on that common definition, and report subgroup AUPRC normalised by stratum prevalence.

---

# SEVERE findings

## S1. D1 is not a cumulative time-dose, and the absolute burden it demands scales 26-fold with recording density

**【Problem】** The primary endpoint is presented in the title, Abstract, Background and Implications as a *cumulative burden* of hypotension in the sense of Salmasi et al., but operationally it is the proportion of *recorded* non-invasive MAP samples below 65 mmHg, so the absolute exposure implied by a positive label varies from 3 to 77 hypotensive readings depending only on how densely the case was monitored.

**【Evidence】**
- `manuscript/manuscript_v0.1.md:1` ("cumulative intraoperative hypotension burden"), `:17-18`, `:61-62` ("That shift created a demand… from the lowest recorded value towards the *cumulative burden*"), `:541-545` ("cumulative-burden outcomes are feasible on sparse data in a way that sustained-duration outcomes are not").
- Definition: `results/s1_outcomes_postanchor.json` → `D1 = {type: exposure_fraction, threshold: 65, min_measurements: 10, fraction: 0.3}`. A case is positive iff `n_below_65 ≥ ceil(0.30 × n_total)` and `n_total ≥ 10`.
- Recomputed from `results/s1_anchor.csv` (column `post_nmap_measurements`, n = 16,861): p05 = 8, p25 = 18, p50 = 30, p75 = 48, p95 = 86, max = 255. Therefore the **required number of sub-65 mmHg readings** is: minimum 3 (at n = 10), p25 = 6, **median 9** (at n = 30), p75 = 15, **p95 = 26** (at n = 86), **maximum 77** (at n = 255).
- Post-anchor MAP density recomputed as `post_nmap_measurements / post_window_minutes`: median **21.8 readings per 100 minutes** (p5–p95 4.2–35.0). So the "30%" is computed over roughly one fifth of the minutes of the outcome window.
- The two anchor strata are internally inconsistent as well: for the Intubation-anchor stratum (median post-anchor n = 33) a positive label needs **10** sub-65 readings; for the Surgery-start-proxy stratum (median n = 16) it needs **5** (`results/s1_anchor.csv`, grouped by `anchor_source`: Intubation p50 post_nmap 33, post_window 166 min; Surgery_start p50 post_nmap 16, post_window 75 min).
- The manuscript is honest that the ≥10/≥30% rule is the authors' choice (`:130`) — but the Abstract (`:22-23`) states the rule with no such flag, and the paper's own framing invites the reader to read it as Salmasi-like.

**【Why it matters】** Salmasi et al. [1] is a *time-dose* exposure: cumulative minutes below threshold. A proportion of intermittent samples is not that. Under ~22% minute-level sampling, a case monitored only during stable intervals can be recorded as burden-free, and conversely three isolated low readings in a 10-reading case earn the same label as 26 in an 86-reading case. Every headline number in the paper (prevalence 15.55%, AUPRC 0.347, the 14-definition sensitivity table, the external prevalence 5.73%) is conditional on this definition, and the paper's central claim that "cumulative-burden outcomes are feasible on sparse data in a way that sustained-duration outcomes are not" is true only for the sample-proportion version, not for a time-dose. A clinician reader will reasonably conclude the endpoint is not the one the title promises.

**【Specific fix】** (a) Replace the title/Abstract/Background wording so the endpoint is named for what it is. Paste-ready replacement for the Abstract Methods sentence (`:22-23`):

> "The primary outcome (D1) was an exposure-fraction definition: at least 10 mean arterial pressure (MAP) measurements after the anchor, of which at least 30% were below 65 mmHg; the ≥10-measurement and ≥30%-below thresholds are the authors' operational choice, and because recordings cover a median of 21.8 MAP readings per 100 post-anchor minutes, D1 is a proportion of recorded samples rather than a cumulative time below threshold."

(b) Add one paragraph to Limitations (as a new item, after the current item 9) with this text:

> "D1 is a proportion of recorded samples, not a cumulative time-dose. A case is labelled positive when the number of sub-65 mmHg readings reaches 30% of all post-anchor readings; because post-anchor recording density ranges from 4 to 35 MAP readings per 100 minutes (5th–95th percentile), the absolute exposure required for a positive label ranges from 3 to 77 hypotensive readings (median 9). The label is therefore not comparable across cases with different monitoring intensity, and the same nominal rule requires 10 sub-65 readings in the intubation-anchored stratum but 5 in the surgery-start-proxy stratum. Readers should interpret D1 as 'a high proportion of the blood pressures that were recorded were low', not as 'a large cumulative hypotensive time'."

(c) Add a sensitivity analysis to Table 2 / Results: for each case compute `minutes_below_65` on the existing 1-minute grid (NaN counted as interruption, per the current engine) and `frac_minutes_below_65 = minutes_below_65 / minutes_with_any_MAP`, and report a new definition D3 = "≥10 recorded minutes and ≥30% of *recorded minutes* below 65 mmHg", plus D4 = "≥10 cumulative minutes below 65 mmHg". Report n and prevalence for D3/D4 alongside the existing 14. This directly quantifies how much of the headline performance is an artefact of sample-proportion versus time-proportion.

---

## S2. In VitalDB the same label "D1" denotes a different exposure, so the external check is not validating the same endpoint

**【Problem】** The external cohort is described as having the outcome "computed identically", but because VitalDB records arterial MAP at ~30 samples per minute, the 30% rule there is a near-continuous *time* fraction, so the external model is scored against a materially stricter and different endpoint than the one it was trained on.

**【Evidence】**
- `manuscript/manuscript_v0.1.md:189-190`: "The outcome D1 was computed identically over [opstart, opend]."
- Recomputed from `results/ext/vitaldb_labels.csv` (n = 3,735): `n_post_map` p25 = 2,551, **p50 = 4,356**, p95 = 10,967; MAP samples per minute of the [opstart, opend] window: p05 = 0, **p50 = 29.94**, p95 = 30.09 (window duration p50 = 150 min).
- Therefore a positive external label requires ≈ 0.30 × 4,356 = **1,307 hypotensive samples ≈ 44 minutes of continuous MAP < 65 mmHg** at the observed median sampling rate. The equivalent MOVER figure is **9 isolated readings** (median n = 30, S1 above). The two labels differ by more than an order of magnitude in absolute exposure.
- This is the parsimonious explanation for the prevalence gap the paper attributes to case-mix: `results/ext/external_validation.json` external prevalence 0.0573 vs internal 0.1555.
- Related: 214 of the 3,735 external cases have `n_post_map == 0` (i.e. every one of the "fewer than 10 post-anchor measurements" cases has *zero* arterial MAP samples in [opstart, opend] despite having been selected for having an arterial MAP track; median window 67.2 min, range 10.8–266 min). These are silently labelled negative. Coincidentally the number of D1-positive external cases is also 214, which the text places adjacent to the exclusion count (`:446-448`) and reads confusingly.
- Limitation 10 (`:606`) mentions "a different recording architecture (continuous arterial pressure rather than intermittent non-invasive measurement)" but frames it only as a source of *discrimination* inflation; Limitation 1 (`:571-573`) repeats the same framing. Neither states that the **label itself** changes meaning.

**【Why it matters】** The external section is one of the paper's four claimed contributions, and the Conclusions state "External validation confirmed transfer of discrimination". If the endpoint being scored externally is not the endpoint that was trained on, then "discrimination transferred" is a statement about ranking patients by a *different* quantity, and the AUPRC comparison (external 0.160 vs internal 0.321 for the same 53 features) is not a like-for-like number at all. This is exactly the class of problem a *BMC Anesthesiology* reviewer will look for, and it is currently invisible to the reader.

**【Specific fix】** (a) Amend `:189-190` to:

> "The same D1 rule was applied over [opstart, opend]; however, because VitalDB samples arterial MAP at a median of 29.9 values per minute while MOVER records a median of 21.8 non-invasive MAP readings per 100 post-anchor minutes, the 30% threshold denotes approximately 30% of elapsed time below 65 mmHg in VitalDB but 30% of intermittent samples in MOVER. The external label is therefore a stricter, time-based exposure and the two prevalences are not directly comparable."

(b) Add to Limitations (new item, after current item 10):

> "The external endpoint is not the same quantity as the internal endpoint. With continuous arterial sampling, a positive D1 label in VitalDB requires roughly 1,300 hypotensive samples (about 44 minutes below 65 mmHg at the median case), whereas the median MOVER case requires 9 isolated low readings. The external AUPRC and prevalence should therefore be read as performance against a time-based exposure, not as a replication of the internal sample-fraction endpoint; a common, time-based definition applied to both cohorts is the appropriate next analysis."

(c) New analysis spec: recompute D1 on a **1-minute grid in both cohorts** (MAP resampled/averaged to one value per minute; minutes with no MAP treated as missing and excluded from the denominator but counted as interruption for sustained definitions), and report internal (full 206-feature and 53-feature) and external AUPRC/AUROC/Brier on that common definition. Also report, for the 214 zero-sample external cases, whether the arterial track is time-aligned with opstart/opend at all, and exclude rather than negative-label them if it is not.

---

## S3. The subgroup AUPRC ordering is a prevalence artefact; "higher in women and younger patients" does not survive normalisation

**【Problem】** Table 5 and the Interpretation present the sex and age gradients in AUPRC as findings about the model, but AUPRC scales with the event rate within the stratum, and the stratum-specific prevalence ordering accounts for almost all of the observed gradient.

**【Evidence】**
- `manuscript/manuscript_v0.1.md:394-398`: "AUPRC was higher in women than men, declined monotonically with age… These patterns were reproduced on the temporal split for sex and age." `:503-507`: "Performance declined sharply with age, which is the opposite of what a purely risk-factor-based model would predict, and was higher in women." Abstract `:34`: "Performance was higher in women and younger patients."
- I recomputed stratum-specific D1 prevalence from `results/s1_labels_postanchor.csv` × `results/s2_features.csv` (n = 16,861) and divided the manuscript's own subgroup AUPRCs (`results/s3_subgroups.json`) by it:

| Stratum | n | events | prevalence | AUPRC (patient) | **lift** | AUPRC (temporal) | **lift** |
|---|---|---|---|---|---|---|---|
| Men | 8,355 | 1,153 | 13.80% | 0.299 | 2.17 | 0.267 | 1.93 |
| Women | 8,506 | 1,469 | 17.27% | 0.357 | 2.07 | 0.370 | 2.14 |
| Age <50 | 6,915 | 1,389 | 20.09% | 0.380 | 1.89 | 0.377 | 1.88 |
| Age 50–64 | 5,366 | 765 | 14.26% | 0.324 | **2.28** | 0.305 | 2.14 |
| Age ≥65 | 4,580 | 468 | 10.22% | 0.186 | 1.82 | 0.194 | 1.90 |
| BMI <18.5 | 512 | 95 | 18.55% | 0.616 | 3.32 | 0.382 | 2.06 |
| BMI 18.5–24.9 | 5,926 | 1,112 | 18.76% | 0.392 | 2.09 | 0.354 | 1.88 |
| BMI 25–29.9 | 5,355 | 779 | 14.55% | 0.286 | 1.96 | 0.306 | 2.10 |
| BMI ≥30 | 4,906 | 611 | 12.45% | 0.257 | 2.07 | 0.330 | 2.65 |
| Overall | 16,861 | 2,622 | 15.55% | 0.347 | 2.23 | 0.339 | 2.18 |

- Spearman rank correlation between stratum prevalence and subgroup AUPRC: **ρ = 0.883, p = 0.0016** (patient split); **ρ = 0.817, p = 0.0072** (temporal split), n = 9 strata.
- The lift ordering is flat or reversed: the age gradient 0.380 → 0.324 → 0.186 becomes 1.89 → **2.28** → 1.82 (the middle band has the *best* relative performance), and men (2.17) slightly outperform women (2.07). BMI lifts are 2.09 / 1.96 / 2.07 — indistinguishable.
- Table 5's caption (`:414-417`) flags small stratum counts but never flags prevalence dependence.

**【Why it matters】** The Abstract, Results and Interpretation all assert a directional finding ("higher in women", "declined monotonically with age", "reproduced on the temporal split") and then build a physiological interpretation on it ("compatible with the model tracking pre-anchor pressure levels, whose distribution and prognostic weight differ across these strata"). That interpretation is not supported: the data show the AUPRC gradient is what any model would produce on strata with different event rates. A statistical reviewer will spot this immediately, and it undermines the credibility of the rest of the subgroup narrative, including the honest underweight caveat.

**【Specific fix】** (a) Add two columns to Table 5 — "Events in stratum (cohort)" and "Stratum prevalence" — and one column "AUPRC / prevalence". (b) Replace `:394-398` with:

> "AUPRC was higher in women than men and declined with age (Table 5). Because AUPRC scales with the event rate within a stratum, Table 5 also reports each stratum's outcome prevalence and the ratio of AUPRC to prevalence. Normalised this way, the age gradient largely disappears (ratio 1.89, 2.28 and 1.82 for the three age bands) and the sex difference reverses (men 2.17, women 2.07); the unnormalised gradients therefore reflect differences in stratum event rates rather than differences in discrimination. Stratum-specific AUROC, which is not prevalence-dependent, is reported alongside."

(c) Add AUROC by stratum (same 9 strata, both splits) to `results/s3_subgroups.json` and to Table 5, and rewrite `:503-507` to remove the "opposite of what a purely risk-factor-based model would predict" claim unless the AUROC analysis supports it.

---

## S4. The external "probabilities did not transfer" conclusion is an artefact of transporting the uncalibrated class-weighted model

**【Problem】** The paper reports that external validation "confirmed transfer of discrimination but not of absolute probabilities" and attributes this to case-mix, but the model that was transported was the raw class-weighted model, whose probabilities were never calibrated even in the development cohort; the internally isotonic-recalibrated model — the deployable artefact — was never applied externally.

**【Evidence】**
- `manuscript/manuscript_v0.1.md:35-39`, `:456-458`, `:576-577`, `:650-652` all frame non-transfer of probabilities as a property of the external cohort.
- `results/s3_metrics.json`: XGBoost patient split `pred_mean = 0.3969`; full logistic 0.4338; baseline logistic 0.4867 — against a test-set prevalence of 525/3,373 = 15.56%.
- `results/ext/core_benchmark.json`: the **53-feature model that was actually transported** has internal `pred_mean = 0.4044` (patient) and `0.4134` (temporal) against prevalence 0.1555 — i.e. the raw model over-predicts risk by **2.6× internally**.
- `results/ext/external_validation.json`: external `pred_mean = 0.365` against observed prevalence 0.0573 (6.4×).
- So the external mean predicted risk (0.365) is *lower* than the internal mean predicted risk of the same model (0.404). The internal uncalibrated Brier is 0.1984 against a no-information Brier of 0.1555 × 0.8445 = 0.1313 — the raw model is worse than a constant predictor at prevalence, exactly as the paper itself states for the full model (`:372-374`).
- The internally calibrated model exists (`results/s3_calib_dca.json`: isotonic on out-of-fold predictions, Brier 0.1905 → 0.119, slope 0.909, intercept 0.008) but `scripts/ext_*.py` applied the raw model with "no external refitting or recalibration" (`:200-203`).
- Nowhere in the manuscript is the internal mean predicted risk reported, so a reader cannot make this comparison.

**【Why it matters】** The Abstract and Conclusions present calibration non-transfer as a finding about generalisability and derive a deployment recommendation ("requiring local recalibration before clinical use"). In fact the dominant cause is that a class-weighted model was transported without the calibration step that the paper itself shows is necessary. Presenting an internal artefact as an external property overstates the transportability problem in one direction while hiding the real one (the authors *had* a calibrated model and chose not to transport it). It also means the paper's own "well calibrated" claim (`:41-42`, `:649`) applies only to the internally recalibrated model, which is not the model that was externally tested.

**【Specific fix】** (a) Report the internal mean predicted risk of the transported 53-feature model (0.404 patient / 0.413 temporal, from `results/ext/core_benchmark.json`) in Table 7 or the text. (b) Replace `:456-458` with:

> "Absolute probabilities did not transfer: the mean predicted risk was 0.37 against an observed prevalence of 0.057 (external Brier score 0.179). This must be read alongside the internal behaviour of the same model, whose raw class-weighted predictions averaged 0.404 against an internal prevalence of 0.156 — the transported artefact was the uncalibrated model, whereas the internally calibrated model (out-of-fold isotonic, Brier 0.190 → 0.119) was not applied externally. The failure to transfer absolute probabilities therefore reflects the absence of the calibration step rather than case-mix shift alone, and the appropriate external test of the deployable artefact is the isotonic-recalibrated model."

(c) New analysis spec: apply the existing out-of-fold isotonic map (fitted on MOVER training data) unchanged to the VitalDB predictions in `results/ext/vitaldb_predictions.csv`; report external calibration intercept, slope, Brier, and a calibration-in-the-large figure. This costs nothing — the predictions are already stored — and converts a misleading claim into a genuinely informative one.

---

# MAJOR findings

## M1. Limitations contains a truncated, unnumbered paragraph fragment whose opening sentence is missing

**【Problem】** The Limitations list ends at item 10 and is followed by a dangling paragraph that begins mid-sentence, so the manuscript as submitted has a structurally broken numbered list.

**【Evidence】** `manuscript/manuscript_v0.1.md:606` ends item 10 ("…not as evidence of intrinsically better discrimination than the development cohort."). Lines 607–612 then read: "*pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg. The model therefore largely extrapolates the patient's current pressure rather than discovering independent risk…*" — grammatically the tail of an item 11 whose head ("Most of the predictive information resided in the …") has been lost. Items 1–10 are each introduced by a bolded lead-in; this fragment has none.

**【Why it matters】** This is the first thing an editor or reviewer will see in the Limitations section. It makes the manuscript look unreviewed and will likely trigger an editorial return before scientific review; it also means one substantive limitation (the dominance of pre-anchor MAP) is currently stated without its framing sentence.

**【Specific fix】** Restore the missing head of item 11, or delete the fragment (its content duplicates `:493-501` and `:549-554`). Paste-ready replacement if restored:

> **11. Dominance of the pre-anchor pressure level.** Most of the predictive information resided in the pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg. The model therefore largely extrapolates the patient's current pressure rather than discovering independent risk, and adds limited information beyond what a clinician reading the bedside monitor already has; a decision-curve benchmark against a MAP-only logistic model showed the full model's incremental net benefit was only 0.013 at threshold 0.15 (Figure 4).

## M2. "What this study adds" promises four elements and delivers five

**【Problem】** The section's own framing contradicts its list length.

**【Evidence】** `manuscript/manuscript_v0.1.md:616-617`: "this study contributes **four** elements that are under-reported…" — followed by five numbered items: 1 leakage audit, 2 the 14-definition sensitivity analysis, 3 the spectrum-bias accounting, 4 the MAP-only benchmark, 5 the external validation. (The parallel "Four implications follow" at `:541` is correct — it lists exactly four.)

**【Why it matters】** A self-contradicting count in a summary section is a reporting defect that a copy-editor will flag and that signals weak internal QA; it also matters because the fifth item (the external validation) is the paper's most contested claim and should not appear to be an afterthought bolted onto a list of four.

**【Specific fix】** Change `:616-617` to: "Beyond the modest absolute performance, this study contributes five elements that are under-reported in perioperative hypotension prediction and that hold independently of the discrimination achieved."

## M3. Undisclosed feature-distribution shift: four of the 53 "transportable" features are recording-cadence counters whose external values are 30–150× outside the development range

**【Problem】** The transportability framing omits that several features in the 53-feature subset are pure monitoring-intensity counters that take values in VitalDB far outside anything seen in MOVER, so the externally applied model is not the same function of its inputs.

**【Evidence】** Recomputed from `results/s2_features.csv` (MOVER) and `results/ext/vitaldb_features.csv` (external), median values:

| feature (all in the 53-feature core, `results/ext/core_cols.json`) | MOVER median | VitalDB median | ratio |
|---|---|---|---|
| `map_n` | 3 (max 15) | 450 | 150× |
| `map_n_below_65` | 0 (p75 = 0) | 23 (p75 = 142.5) | — |
| `vitals_window_n_records` | 14 | 450 | 32× |
| `map_minutes_since_last` | 1.0 min | 0.02 min | 50× |
| `map_frac_below_65` | 0 (p75 = 0) | 0.06 (p75 = 0.33) | — |
| `map_slope` | non-null for 10,658/16,861 (63.2%) | non-null for 3,490/3,491 (93.4%) | — |

`map_slope`, `map_minutes_since_last`, `map_n_below_65`, `map_n_below_55` and the two QA counters are also **absent from the prose description** of the 53-feature subset at `:192-199`, which describes only "the fraction of pre-anchor MAP readings below 65 and 55 mmHg" (two of the four below-threshold features are *counts*, not fractions).

**【Why it matters】** Gradient-boosted trees extrapolate as a constant outside the training range, so `map_n`, `map_n_below_65` and `vitals_window_n_records` contribute nothing (or a constant) externally while being mid-importance features internally (`pip_n` is rank 12 by gain at 40.3; `map_n_below_65` rank 19 at 36.0). The claim that "ranking transferred" is therefore a claim about a partly degenerate model, and the paper never says so. It also means the external AUROC of 0.751 is, if anything, surprisingly good — which deserves comment rather than a "consistency rather than superiority" reading.

**【Specific fix】** (a) Add a limitation item:

> "Four of the 53 transportable features are recording-cadence counters (`map_n`, `map_n_below_65`, `map_minutes_since_last`, `vitals_window_n_records`). Their values in VitalDB are 30–150 times larger than any seen in MOVER (median `map_n` 450 vs 3), so tree splits fitted on MOVER densities cannot be exercised externally and these features are effectively degenerate in the external application. The external AUROC should accordingly be read as the performance of a reduced feature set, and a density-matched external re-analysis (e.g. restricting VitalDB predictors to the first k arterial samples, or reporting performance stratified by pre-anchor sampling density) is needed before 'transportability' is claimed."

(b) Correct the prose at `:192-199` to enumerate the actual 53 columns, distinguishing fractions from counts.

## M4. 34 cases have an "anaesthesia induction" anchor 2–12.5 hours after OR start

**【Problem】** The anchor definition retains cases whose first recorded Intubation event is hours after OR start, for which the "pre-anchor 15-minute window" is not pre-induction physiology and the "remainder of surgery" is a fragment.

**【Evidence】** Recomputed from `results/s1_anchor.csv` (n = 16,861): `anchor_minus_or_start` > 60 min in **325 cases (1.93%)**; > 120 min in **34 cases (0.20%)**; > 240 min in 3 cases; maximum **751 minutes (12.5 h)**. D1 prevalence among the >120-min group is 8.82% vs 15.55% overall. The pipeline excluded 242 cases for "anchor falling outside the OR window" (`:114-115`, `results/s1_cohort.json: excl_bad_anchor 242`) but applied no upper bound on anchor lateness. By anchor source (`results/s1_anchor.csv`): Intubation anchors p25/p50/p75 = 11/14/18 min (p95 32, max 751); Surgery-start anchors p25/p50/p75 = 28/34/43 min (p95 65).

**【Why it matters】** The paper's core framing is prediction "from data available at anaesthesia induction" (title, `:17-18`, `:88-89`, `:647`). For at least 34 cases — and for the 325 cases more than an hour after OR start — the predictor window contains mid- or late-intraoperative physiology, and the outcome window is truncated. Because the anchor-to-OR-start interval is itself the 5th-ranked predictor (gain 64.1), the model is sensitive to exactly this variable. None of this appears in Limitations.

**【Specific fix】** Add to Limitations (or to Cohort):

> "Anchor timing was not constrained to a plausible induction window. In 325 cases (1.9%) the first recorded Intubation event was more than 60 minutes after OR start and in 34 cases (0.2%) more than 120 minutes (maximum 751 minutes); for these cases the 15-minute pre-anchor window is not pre-induction physiology and the post-anchor window is truncated. We retained them because excluding them would change the cohort definition post hoc, but a sensitivity analysis excluding anchors later than 60 minutes after OR start should be performed."

And add that sensitivity analysis (report AUPRC/AUROC on the 16,536 retained cases).

## M5. The "1,496 negative by construction" figure is 1,332 cases with a known count below 10 plus 164 cases whose count is unknown — and the 164 contradict the paper's own characterisation of that group

**【Problem】** The headline spectrum-bias number conflates "fewer than 10 post-anchor measurements" with "post-anchor measurement count not determinable", and the paper's description of the excluded group is wrong for 164 of them.

**【Evidence】** `results/s1_anchor.csv` column `post_nmap_measurements`: **NaN for 164 cases**, 0 for none, <10 for **1,332**, ≥10 for 15,365. 1,332 + 164 = **1,496**, which is the number in the manuscript (`:130-132`, `:596-600`, `:630-632`) and in the audit trail (`outcome.D1.n_cases_lt10_postanchor_map,1496`). `results/s1_data_quality.json` reports only `n_lt_5 = 306` and `n_ge_10 = 15,365` on the 16,697 non-NaN cases — it does not contain 1,496. All 164 NaN cases are D1-negative. Their `post_window_minutes` has **median 216.5 min (min 25, max 803)** — i.e. *longer* than the cohort median of 147 min. By contrast the 1,332 cases with 1–9 readings have a median window of 88 min. Limitation 7 states: "the excluded cases are exactly those with the sparsest monitoring (typically shorter or less-invasive cases)" (`:597-599`).

**【Why it matters】** The 8.9% / 17.1% pair is used twice as quantitative evidence of spectrum bias and is one of the paper's four claimed contributions. The 164 cases are not "shorter or less-invasive" — they have the longest outcome windows in the cohort and no measurable MAP at all, which points to a data-alignment or recording failure rather than to a monitoring-intensity spectrum. Reporting them as "fewer than 10 measurements" hides a distinct data-quality problem.

**【Specific fix】** Amend `:130-132` and `:596-600` to:

> "Cases with fewer than 10 post-anchor measurements, or with no determinable post-anchor MAP count, were classified as negative by construction; this applied to 1,496 cases (8.9%), of whom 1,332 had 1–9 recorded post-anchor MAP values and 164 had none. Because the definition deliberately requires a minimum amount of evidence before a burden can be asserted, this is a spectrum effect: the 1,332 sparsely-monitored cases had a median post-anchor window of 88 minutes, whereas the 164 cases with no measurable post-anchor MAP had a median window of 217 minutes, indicating a recording or time-alignment failure rather than short cases. The conditional prevalence among cases with at least 10 measurements was 17.1% (2,622 of 15,365)."

## M6. The decision-curve analysis over-claims its useful range and never defines the decision being modelled

**【Problem】** The DCA is presented as showing positive net benefit "up to approximately 0.58", which is true only at a magnitude of 10⁻⁴, and the clinical decision the curve is supposed to inform is never specified.

**【Evidence】** Recomputed from `results/s3_calib_dca.json` (`net_benefit_model` arrays, 99 thresholds 0.01–0.99):
- Patient split: NB > 0 for thresholds 0.01–0.58, but **NB < 0.01 from threshold 0.36 onward**; NB at 0.58 = **9.88 × 10⁻⁵** (the audit trail records `dca.patient.net_benefit_at_crossing = 9.9e-05`). Treat-all NB at 0.10 = 0.0618 vs model 0.0787 — the model beats treat-all by only 0.017 at that threshold.
- Temporal split: NB > 0 for 0.01–**0.45** (0.46 is the first negative threshold, so the manuscript's "0.46" at `:381-382` and `:485` is off by one grid point), then negative 0.46–0.65, then positive again only 0.66–**0.73** (not 0.66–0.74 as at `:382-383`), with a maximum of 5.8 × 10⁻⁴. NB < 0.01 from threshold 0.35.
- The decision is never defined: no statement of what "treat" means, no harm:benefit justification for the 0.10–0.15 range, and no account of the fact that the calibrated model assigns >0.30 predicted risk to only ~10% of patients (top calibration decile `mean_pred` = 0.4357).
- `:386-389` prints the same two number pairs twice in consecutive sentences (0.050/0.058 at 0.15 and 0.079/0.085 at 0.10).

**【Why it matters】** DCA is one of the paper's headline analyses and is named in the Abstract. "Positive net benefit up to 0.58" reads as sustained clinical usefulness when the curve is below 1% from 0.36 and effectively zero at the crossing. And without a defined decision, the reader cannot judge whether a threshold of 0.10 is plausible for "vasopressor-readiness or enhanced monitoring".

**【Specific fix】** (a) Replace `:379-383` with:

> "In decision curve analysis, the calibrated model's net benefit exceeded that of the 'treat none' strategy across thresholds 0.01–0.58 on the patient-level split, but the magnitude was material (≥0.01) only up to threshold 0.35 and fell to 9.9 × 10⁻⁵ at the 0.58 crossing; on the temporal split net benefit was positive for 0.01–0.45 and again only for 0.66–0.73, with a maximum of 5.8 × 10⁻⁴ in the second interval. The 'treat all' strategy had a small positive net benefit at the lowest evaluated thresholds (0.062 at threshold 0.10) but became strongly negative at higher thresholds (−2.13 at 0.73). The absolute net benefit at the decision-relevant thresholds was small (0.079 and 0.085 at 0.10; 0.050 and 0.058 at 0.15 on the patient and temporal splits), so the clinical usefulness demonstrated by the curve is modest."

(b) Add one sentence defining the decision and its threshold justification, e.g.:

> "The decision curve is reported for the illustrative decision of pre-emptive arterial cannulation with vasopressor readiness in patients flagged at induction; a threshold of 0.10–0.15 corresponds to accepting roughly 6–10 false positives per true positive, which is plausible for a low-harm monitoring intervention but is a clinical judgement that this analysis does not settle."

(c) Delete the duplicated sentence at `:388-389`.

## M7. Must-cite literature is missing, and the "prior work" section rests on two preprints

**【Problem】** Several methods that the paper uses as headline evidence are uncited, and no peer-reviewed MOVER-derived or VitalDB-derived hypotension-prediction study is referenced.

**【Evidence】** The reference list (`:719-764`) contains 18 items. Missing, in my judgement as a domain reviewer:
- **PROBAST** — Wolff RF, Moons KGM, Riley RD, et al. *PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies.* Ann Intern Med. 2019. The paper reports TRIPOD+AI (`:98`) but never mentions risk-of-bias assessment; for a prediction-model paper in *BMC Anesthesiology* this is close to mandatory.
- **Decision-curve analysis** — Vickers AJ, Elkin EB. *Decision curve analysis: a novel method for evaluating prediction models.* Med Decis Making. 2006. DCA is a headline analysis (`:217-218`, Figure 4) and is uncited.
- **Calibration** — Van Calster B, Nieboer D, Vergouwe Y, et al. *Calibration: the Achilles heel of predictive analytics.* BMC Med. 2019. "Well calibrated" is a headline claim (`:41-42`, `:649`) and is uncited.
- **Hypotension Prediction Index derivation** — Hatib F, Jian Z, Buddinger S, et al. *Machine-learning algorithm to predict hypotension based on high-fidelity arterial pressure waveform analysis.* Anesthesiology. 2018. The paper cites the two HPI randomised trials [2,3] but not the derivation of the index itself, which is the relevant methodological comparator for "what can be predicted from a waveform".
- **Sample-size justification for prediction models** — Riley RD, Snell KIE, Ensor J, et al. *Calculating the sample size required for developing a clinical prediction model.* BMJ. 2020. The paper fits 206 predictors on ~2,100 training events and never addresses events-per-variable or minimum sample size.
- **IOH–outcome breadth**: the claim that IOH "is associated with kidney and myocardial injury" (`:53`) rests on Salmasi [1], Sun [16] and Walsh [15]. The classic perioperative literature is not represented at all — e.g. Bijker et al. on IOH and perioperative ischaemic cardiac/neurologic complications, and Monk et al. on intraoperative hypotension and one-year mortality (verify volume/page before submission).
- **Prior work on the actual resources**: the only MOVER-derived prediction work cited is a Preprints.org preprint [4] and a medRxiv preprint [12]; there is no peer-reviewed MOVER-derived model and no prior VitalDB hypotension-prediction study, despite VitalDB being the external cohort. References [4], [5], [6], [12] and [14] are all 2026-dated, three of them preprints.

**【Why it matters】** Uncited headline methods (DCA, calibration, PROBAST) are a standard reviewer complaint and easy to fix. More substantively, a "Relation to previous work" section built on two preprints — one of which the paper criticises for implausible performance — is a weak foundation for a *BMC* submission, and the absence of any prior MOVER or VitalDB hypotension-prediction citation makes the novelty claim ("Other investigators have developed machine-learning models for intraoperative risk from comparable operating-room resources, including external-validation studies [14,15]" — neither of which is a hypotension-prediction study) look thin.

**【Specific fix】** Add the five method references above (PROBAST, Vickers 2006, Van Calster 2019, Hatib 2018, Riley 2020), add 2–3 peer-reviewed IOH–outcome studies, and either add at least one peer-reviewed hypotension-prediction study on MOVER or on VitalDB or state explicitly that none exists. Renumber Vancouver references accordingly and re-check every in-text citation number.

---

# MINOR findings

*(Each stated in the same four-part contract, in compact form.)*

## m1. Table 3 omits a predictor domain and its predictor column does not sum to the stated 206
**【Problem】** Table 3 lists 12 of the 13 predictor domains, so its predictor column sums to 204 rather than the 206 stated in the text.
**【Evidence】** `manuscript/manuscript_v0.1.md:144-148` lists 13 domains summing to 206 (anchor 3, demographics 6, surgical group 14, anaesthesia technique 12, NIBP 36, derived NIBP 6, QA counters 2, invasive 32, ventilation 47, medication 26, derived medication 2, laboratories 12, fluid/bleeding 8). Table 3 (`:326-339`) lists only 12 rows and omits "Derived medication indices (2 predictors, 56.3% coverage)"; its predictor column sums to **204**. `results/s2_data_quality.json: domain_coverage.medication_derived` = `{n_features: 2, mean_non_null_pct: 0.5625}`.
**【Why it matters】** A reader reconciling the table against the Methods will find a two-predictor discrepancy in the paper's own description of its model inputs; it is the kind of internal inconsistency that erodes confidence in the rest of the accounting.
**【Specific fix】** Add the row `| Derived medication indices | 2 | — | 56.3 | 0.00 |` to Table 3.

## m2. Table 3's invasive-monitoring coverage mixes definitions
**【Problem】** The 14.8% coverage shown for the 32-predictor invasive-monitoring domain is the arterial subset only, understating the domain's availability.
**【Evidence】** Table 3 (`:337`) reports "Invasive monitoring | 32 | 2,503 | 14.8". `results/s2_data_quality.json: invasive_monitoring` also gives `temp_coverage_pct: 0.3544` and `cvp_coverage_pct: 0.1558`, so the domain is populated for 35.4% of cases via temperature.
**【Why it matters】** The table is the paper's evidence for Limitation 6 ("Unequal domain coverage"); a reader who checks the artefact will find a different number and may conclude the coverage accounting is unreliable.
**【Specific fix】** Footnote Table 3: "Coverage for the invasive-monitoring domain is the proportion with an arterial trace; temperature was available for 35.4% and central venous pressure for 15.6% of cases."

## m3. Table 7 reports the cohort prevalence in a column that reads as the test-set prevalence
**【Problem】** The prevalence column mixes the development-cohort prevalence with the external-cohort prevalence, so the internal rows cannot be reproduced from the n and Events columns beside them.
**【Evidence】** `:466-467` gives the temporal row prevalence as 15.55%, but the temporal test set has 291 events in 1,818 cases = **16.01%** (`results/s3_metrics.json`). The patient row (525/3,373 = 15.56%) is likewise the cohort figure.
**【Why it matters】** AUPRC's no-skill baseline is the *test-set* prevalence, so a reader who divides the reported AUPRC by the reported prevalence gets a slightly wrong lift; more importantly it is an unexplained inconsistency inside a table.
**【Specific fix】** Relabel the column "Cohort prevalence (%)" and add a footnote: "Test-set prevalence was 15.56% (patient) and 16.01% (temporal); no-skill AUPRC equals the test-set prevalence."

## m4. Table 5's BMI rows silently drop 32 test cases
**【Problem】** The BMI stratification covers 32 fewer test cases than the sex and age stratifications, with no note explaining the difference.
**【Evidence】** BMI stratum n values in the audit trail sum to 98 + 1,202 + 1,064 + 977 = **3,341**, whereas the sex and age rows sum to 3,373 (= n_test). The gap is 32 cases with non-computable BMI (162 cohort-wide; 162 × 0.2 = 32.4).
**【Why it matters】** A reader summing the column will find a 32-case hole; it also means the BMI subgroup AUPRCs are computed on a slightly selected subset, which is relevant given that the paper flags BMI-stratum instability elsewhere.
**【Specific fix】** Add a Table 5 footnote: "BMI strata cover 3,341 of 3,373 test cases; 32 cases (0.9%) had non-computable BMI after plausibility filtering."

## m5. "12 categories" for surgical group versus 13 rows in Table 1
**【Problem】** The stated number of surgical-group categories does not match the number of groups the paper actually reports.
**【Evidence】** `:158-160` says "keyword mapping into 12 categories with a controlled fuzzy fallback… The residual 'other' category contained 348 cases". `results/s2_data_quality.json: procedure_groups.counts` has 13 keys: 11 named groups + OTHER (348) + NO_SURGERY (6), and Table 1 (`:263-275`) lists all 13.
**【Why it matters】** Minor, but it is a direct text/table contradiction in the cohort description and trivial to fix.
**【Specific fix】** Change to "11 named categories plus a residual 'other' category (348 cases, 2.1%) and a 'no surgery recorded' group (6 cases)".

## m6. The prose description of the 53-feature transportable subset is incomplete
**【Problem】** The Methods describe a subset that does not match the 53 columns actually used.
**【Evidence】** `:192-199` describes "the fraction of pre-anchor MAP readings below 65 and 55 mmHg" and omits `map_n_below_65`, `map_n_below_55` (counts, not fractions), `map_slope`, `map_minutes_since_last`, `vitals_window_actual_min` and `vitals_window_n_records` — compare the actual list in `results/ext/core_cols.json` (53 columns).
**【Why it matters】** The external validation is the paper's most contested claim, and its feature set is described inaccurately; a reader cannot tell from the text that four of the transported features are recording-cadence counters (see M3).
**【Specific fix】** Enumerate the columns or point to `results/ext/core_cols.json`, and distinguish counts from fractions.

## m7. Internal tension: the paper says the data are too sparse for pressure dynamics, yet ships a slope feature
**【Problem】** The Discussion claims the model cannot characterise arterial-pressure dynamics, but two dynamics features are in the transported model.
**【Evidence】** `:522-525`: "Our recording density (median 3 MAP readings in the 15-minute pre-anchor window) is too sparse to characterise such dynamics, so our model necessarily leans on the static pre-anchor level." But `map_slope` and `map_minutes_since_last` are both in the 53-feature transportable core (`results/ext/core_cols.json`), and `map_slope` is computable for 10,658 of 16,861 MOVER cases (63.2%) while being near-complete externally (3,490/3,491).
**【Why it matters】** The sentence is one of the paper's more careful concessions and is used to explain why the model leans on the static level; a reader who inspects the feature list will find it contradicted.
**【Specific fix】** Either drop the two dynamics features and say so, or amend to: "Our model includes a crude pre-anchor slope computed from a median of three readings, which is too sparse to characterise arterial-pressure dynamics; the model therefore leans predominantly on the static pre-anchor level."

## m8. Undisclosed medication unit inconsistency in the source data
**【Problem】** The Methods disclose data cleaning only for height/weight/BMI, although the medication domain also contains a material unit inconsistency.
**【Evidence】** `results/s2_data_quality.json: medication_unit_mismatch` records 1,981 of 17,683 propofol rows in **mcg** (vs expected mg) and 6 of 1,903 phenylephrine rows in **drops**. The Methods describe cleaning only for height/weight/BMI (`:162-167`). I checked `drug_propofol_total_mg` in `results/s2_features.csv` (median 140 mg, max 1,680 mg, no value >5,000), which indicates the pipeline unit-filtered correctly — so this is a disclosure gap, not an error.
**【Why it matters】** Given that the paper is explicitly a data-quality-aware contribution, an undisclosed 11% unit error in a 26-predictor domain looks like selective reporting.
**【Specific fix】** Add to Methods: "Medication records contained unit inconsistencies (1,981 of 17,683 propofol rows recorded in mcg and 6 of 1,903 phenylephrine rows in 'drops'); each dose feature was therefore restricted to rows carrying its expected unit before summation."

## m9. Clinically impossible pre-anchor procedure events are never mentioned
**【Problem】** The anchor definition rests entirely on procedure-event timestamps that contain clinically impossible sequences, which the paper does not report.
**【Evidence】** From the raw `patient_procedure_events.csv` restricted to events at or before the anchor (n = 17,337 rows): 4 cases have an **Extubation** event before the anchor (19–1,440 min before), 1 has **CPR** (45 min before) and 3 have **Mayfield** (0–2,853 min before). Intubation accounts for 13,835 rows over 13,834 cases (one case has two).
**【Why it matters】** Small in count, but it is direct evidence that the event clock in this resource is unreliable — which bears on the credibility of the anchor, on the leakage audit's "zero unparseable timestamps", and on M4 (late anchors).
**【Specific fix】** Add one sentence to Cohort or Limitations: "Procedure-event timestamps contained clinically implausible sequences (4 cases with an extubation and 1 with a cardiopulmonary-resuscitation event dated before the anchor, 3 with Mayfield pinning up to 48 hours before the anchor); these are retained because no rule could be applied post hoc without changing the cohort, but they indicate event-timestamp noise in the source."

## m10. The nominal 15-minute pre-anchor window is not a fixed window, and its effective length is never reported
**【Problem】** For nearly half the cohort the nominal pre-anchor window reaches into a period with essentially no blood-pressure data, and the effective window length is not reported anywhere.
**【Evidence】** 7,794 of 16,861 cases (46.2%) have `anchor_minus_or_start < 15`, so the nominal pre-anchor window extends before OR start — where I verified from the raw `patient_vitals.csv` that only 43 cases (0.26%) have any MAP reading. `results/s2_data_quality.json: vitals_window.window_actual_min_p50 = 13.0` (5th percentile of `anchor_minus_or_start` = 7.0), and `vitals_window.n_pids_no_vital_in_window = 121`.
**【Why it matters】** The predictor that dominates the model is a summary of this window; a reader deserves to know that its effective length ranges from about 1 to 15 minutes and that it is not the same window across cases. The authors did include `vitals_window_actual_min` as a feature, which is good practice, but never explain it.
**【Specific fix】** Report the effective pre-anchor window length (median 13 min, 5th percentile 7 min) in the Predictor availability section, and note that for 46% of cases the nominal window reaches into the pre-OR period in which essentially no blood pressure is recorded.

## m11. Three stale or incorrect values in artefacts that the audit trail points to
**【Problem】** The audit trail and feature dictionary, which the manuscript presents as the traceability layer, contain three values that disagree with the cohort data.
**【Evidence】** (a) `results/s2_feature_dictionary.json` header says `n_features: 207` while the `features` list contains 206 and the audit trail says 206. (b) `results/s4_audit_trail.csv:143` records `cohort.female_n = 8506`, whereas `results/s2_data_quality.json: demographics.gender_values` gives F = 8,502 (plus 4 unknown) and Table 1 (`:248-249`) reports 8,502 (50.4%) and 4 unknown — the audit-trail value appears to fold the 4 unknown-sex cases into female. (c) `results/s1_outcomes_postanchor.json: note` states the anchor is "中位 OR_start+13min" whereas every other artefact and the manuscript say 15 min.
**【Why it matters】** The manuscript claims that "every number reported in this manuscript … is traceable through an audit trail" (`:226-229`, `:789-790`); if the audit trail itself contains values that contradict the manuscript, that claim is not safe to make.
**【Specific fix】** Correct 207 → 206, 8,506 → 8,502 (and add a `sex_unknown_n = 4` row), and update or delete the stale note.

---

# § Stands up (things I suspected but verified as correct)

1. **Limitation 3's pre-OR baseline claim is correct, and I verified it from source.** The manuscript states (`:582-583`) "Fewer than 1% of cases had any MAP recording in the 30 minutes before OR start". I recomputed this from the raw 200 MB `patient_vitals.csv`, deriving OR start as `anchor_time − anchor_minus_or_start` from `results/s1_anchor.csv` and counting non-null nMAP in [OR_start − 30 min, OR_start): **43 of 16,861 cases (0.26%)** have ≥1 such reading (distribution among them: median 2, p95 6, max 10). The claim is honest and, if anything, conservative.

2. **The anthropometric cleaning numbers are exactly right.** I recomputed from the raw `patient_information.csv` on the 16,861-case analytic cohort: heights outside 100–220 cm = 23 in (0,100) + 14 >220 = **37** ✓; weights outside 25–300 kg = 4 zeros + 9 in (0,25) + 5 >300 = **18** ✓; BMI outside 10–80 kg/m² among cases with valid height and weight = **6** ✓ (49 cases fall outside the BMI range overall, but 43 of those are consequences of already-invalid height/weight). `ht_missing = 141` = 104 source-missing + 37 implausible ✓. The stated extremes are also correct for the analytic cohort: minimum non-zero height 2 cm, maximum weight 839 kg, maximum BMI 2.2 × 10⁵ kg/m².

3. **Every number in Tables 1, 2, 4, 5, 6 and 7 traces to an artefact, to the last digit.** I checked each one against `results/s1_cohort.json`, `s1_outcomes_postanchor.json`, `s1_data_quality.json`, `s2_data_quality.json`, `s3_metrics.json`, `s3_subgroups.json`, `s3_feature_importance.json`, `s3_calib_dca.json`, `ext/core_benchmark.json` and `ext/external_validation.json`. All 14 Table-2 prevalences, all 16 Table-4 AUPRC/AUROC/Brier/CI entries, all 18 Table-5 AUPRCs, all 10 Table-6 gains and all 9 Table-7 cells match. Table 1's IQRs, which I could not find in the audit trail, are also correct: age 54 (39–66), BMI 26.6 (23.1–30.9), height 167 (160–175), weight 76 (63–90), pre-anchor mean MAP 87.7 (77.7–98.5), pre-anchor MAP count 3 (2–4), anchor 15 (11–24) min after OR start — all recomputed from `results/s2_features.csv` and `results/s1_anchor.csv`.

4. **The suspected "monitoring-intensity shortcut" is absent.** I suspected that because D1 requires ≥10 post-anchor measurements, the model might learn to predict post-anchor monitoring density from pre-anchor recording counts (a feature that is available: `map_n`, and `vitals_window_n_records`). It cannot: the Pearson correlation between pre-anchor `map_n` and post-anchor `post_nmap_measurements` is **r = −0.0015** (n = 16,036), and median post-anchor count is 29–33 readings at every value of pre-anchor `map_n` from 1 to 8. The negative-by-construction rule does not create a learnable shortcut through the available features.

5. **D1 prevalence is not mechanically driven by recording density.** I stratified D1 prevalence by post-anchor MAP count: 20.65% (10–14 readings), 18.34% (15–19), 18.55% (20–29), 15.76% (30–44), 14.33% (45–59), 15.59% (60–89), 17.01% (≥90). The relationship is non-monotonic, so the label is not a simple function of how much was recorded — the definition is fragile (S1) but not circular.

6. **The leakage audit is genuinely clean, not a reported formality.** `results/s2_data_quality.json: leakage_audit` shows `max_used_time_minus_anchor = 0.0` and `n_time_nat = 0` for all seven time-stamped domains, with row-level before/after counts (e.g. patient_vitals 3,397,487 merged → 314,398 after the anchor filter → 215,658 inside the 15-minute window). I independently re-derived the pre-anchor event set from the raw `patient_procedure_events.csv` and confirmed that no used event postdates its case's anchor.

7. **The anchor-stratum prevalence difference is small, which supports the proxy being defensible.** D1 prevalence is 15.38% in the Intubation-anchored stratum and 16.32% in the Surgery-start-proxy stratum — a 0.94-percentage-point difference, so the proxy does not appear to import a large outcome shift (though see M4 on anchor lateness).

8. **The paper's honesty about the MAP-only benchmark and the "extrapolation of current pressure" reading is a genuine strength, not boilerplate.** The incremental net benefit of 0.013 at both 0.10 and 0.15 (`results/s3_calib_dca.json: map_only_benchmark`, 0.0132 and 0.0131) and the MAP-only AUPRC of 0.284 versus 0.347 are reported plainly, and the Interpretation (`:493-501`), Implications (`:549-554`) and Conclusions (`:653-655`) all state the limitation in the authors' own words rather than burying it.

---

# § Questions for the authors

1. In the external cohort, 214 of 3,735 cases have **zero** arterial MAP samples in [opstart, opend] despite being selected for having an arterial MAP track, with a median window of 67 minutes. Is the arterial waveform time-aligned with `opstart`/`opend` in those cases, or is this a track-selection/offset problem? If the former, why are they labelled D1-negative rather than excluded?
2. What were the reasons for excluding the 2,653 VitalDB cases that did not enter the external cohort (6,388 → 3,735), and how many were excluded for invalid `opstart`/`opend` versus absent arterial track? Without this, "selection we could not characterise fully" cannot be assessed.
3. Was the out-of-fold isotonic calibration map fitted once on the 80% training split and then frozen, or refitted per fold? Was the same frozen map available at the time the external model was applied, and if so why was the raw model transported instead?
4. For Table 5, what were the stratum-specific event counts and prevalences in the held-out test sets? (I have computed the cohort-level figures and they change the interpretation — see S3.)
5. Why was the anchor allowed to fall up to 751 minutes after OR start? Was any upper bound considered, and what is the clinical interpretation of the 34 cases above 120 minutes?
6. `results/s2_feature_dictionary.json` reports `n_features: 207` while listing 206 features. Which is correct?
7. `results/s4_audit_trail.csv` records `cohort.female_n = 8506` while the cohort has 8,502 female and 4 unknown-sex cases. Is 8,506 intended to include the unknown-sex cases?
8. The Discussion states that recording density is too sparse to characterise arterial-pressure dynamics, yet `map_slope` and `map_minutes_since_last` are in the transported 53-feature model. Were they retained deliberately, and what is their contribution?
9. Does any peer-reviewed hypotension-prediction model exist on MOVER or on VitalDB that should be cited? If not, the "Relation to previous work" section should say so explicitly rather than implying one does.
10. Was the 80/20 patient-level split repeated over multiple seeds? A single split with 525 test events gives an AUPRC bootstrap CI of 0.309–0.387, i.e. ±0.04, which is wider than the difference between XGBoost and LightGBM (0.347 vs 0.337).

---

# § What I actually checked

**Files read in full**
- `review/REVIEW_round6_2026-10-20/_PANEL_BRIEF.md`
- `manuscript/manuscript_v0.1.md` (all 794 lines: Abstract, Background, Methods, Results, all 7 tables, Discussion incl. Limitations and "What this study adds", Conclusions, abbreviations, Declarations, 18 references, 6 figure legends, 2 additional files)
- `results/s1_cohort.json`, `results/s1_outcomes_postanchor.json`, `results/s1_data_quality.json`, `results/s2_data_quality.json`, `results/s2_feature_dict.json`, `results/s2_feature_dictionary.json`
- `results/s3_metrics.json`, `results/s3_subgroups.json`, `results/s3_feature_importance.json`, `results/s3_calib_dca.json`, `results/s4_audit_trail.csv`
- `results/ext/external_validation.json`, `results/ext/core_cols.json`, `results/ext/core_benchmark.json`, `results/ext/vitaldb_features_qa.json`
- Raw data (read-only, chunked): `data_raw/_sis_emr_x/EMR/patient_information.csv`, `patient_procedure_events.csv`, `patient_vitals.csv` (200 MB, streamed)
- Derived data: `results/s1_anchor.csv`, `results/s1_labels_postanchor.csv`, `results/s2_features.csv`, `results/ext/vitaldb_labels.csv`, `results/ext/vitaldb_features.csv`, `results/ext/vitaldb_predictions.csv`

**Commands run** (Python 3.13.12 / pandas 2.3.3 / numpy 2.4.6 / scikit-learn 1.9.0, `envs/default`): five analysis scripts covering (i) DCA threshold crossings and positive intervals for both splits; (ii) outcome-stratified characteristics, pre-anchor MAP count distribution, Table 5 stratum-n arithmetic; (iii) anchor timing IQR, post-anchor measurement percentiles, D1 scale-dependence, density-band prevalence, pre/post density correlation; (iv) the NaN decomposition of the 1,496 figure; (v) VitalDB `n_post_map` and sampling-rate distribution and the implied time-based threshold; (vi) MOVER-vs-VitalDB feature distribution comparison; (vii) raw-data verification of the pre-OR 30-minute MAP claim and of the anthropometric cleaning counts; (viii) raw-data verification of pre-anchor procedure events.

**Values recomputed versus the manuscript**

| Claim | Manuscript | My recomputation | Status |
|---|---|---|---|
| Cohort waterfall 19,114 → 16,861 | `:110-116` | 19,114 − 8 − 1,632 − 371 − 242 = 16,861; `or_window_observations` 3,559,993; `or_min_median` 167 | ✓ |
| D1 prevalence | 15.55% (2,622/16,861) | 2,622/16,861 = 15.5507% | ✓ |
| Negative by construction | 1,496 (8.9%) | 1,332 (count <10) + 164 (count missing) = 1,496; 8.874% | ✓ but decomposed (M5) |
| Conditional prevalence | 17.1% (2,622/15,365) | 17.065% | ✓ |
| All 14 Table-2 prevalences | `:290-303` | matched `s1_outcomes_postanchor.json` exactly | ✓ |
| Table 4 (16 metric rows + CIs) | `:359-366` | matched `s3_metrics.json` exactly | ✓ |
| Calibration | Brier 0.191→0.119, slope 0.909, intercept 0.008 | 0.1905→0.1190, 0.9092, 0.0083 | ✓ |
| DCA NB @0.10 / @0.15 | 0.079/0.085 and 0.050/0.058 | 0.07866/0.08477 and 0.05035/0.05789 | ✓ |
| DCA treat-all @0.10 / @0.73 | ≈0.06 / ≈−2.1 | 0.06183 / −2.12723 | ✓ |
| DCA "positive up to" | 0.58 (patient), 0.46 (temporal) | 0.58 and 0.45; NB <0.01 from 0.36/0.35; crossing values 9.9e-05 / 1.6e-04 | ⚠ over-claim (M6) |
| Table 5 (18 AUPRCs) | `:404-412` | matched `s3_subgroups.json` exactly | ✓ |
| Table 5 BMI stratum n | 98+1,202+1,064+977 | sums to 3,341 vs n_test 3,373 (32 BMI-missing dropped) | ⚠ (m4) |
| Table 6 (10 gains) | `:431-440` | matched `s3_feature_importance.json` exactly | ✓ |
| Table 7 internal 53-feature rows | 0.321/0.698 and 0.314/0.710 | matched `ext/core_benchmark.json` (0.3206/0.6979; 0.3135/0.7095) | ✓ |
| Table 7 temporal prevalence | 15.55% | 291/1,818 = 16.01% | ⚠ (m3) |
| External AUPRC/AUROC/Brier | 0.160/0.751/0.179 | 0.1600 (0.1291–0.2021), 0.7507 (0.7133–0.7844), 0.1789 | ✓ |
| External mean predicted risk | 0.37 vs 0.057 | 0.365 vs 0.0573; internal 53-feature raw `pred_mean` 0.4044/0.4134 (never reported) | ⚠ (S4) |
| Recording density | MAP 19.89%, SBP 19.99%, DBP 19.95%, HR 94.8%, SpO₂ 96.1% | 0.1989/0.1999/0.1995/0.9479/0.9608 | ✓ |
| MAP segments | 637,188; 96.2% single-minute; median 1 min | exact match | ✓ |
| MAP per case | median 33 (p5–p95 12–90) | exact match | ✓ |
| Post-anchor MAP count | p5–p95 not reported; ≥10 in 15,365 | p05 8, p25 18, p50 30, p75 48, p95 86, max 255; n≥10 = 15,365 | ✓ (used for S1) |
| Anchor timing | median 15 (IQR 11–24) | p25 11, p50 15, p75 24 | ✓ |
| Pre-anchor window post-anchor window | median 147 (49–440) | exact match | ✓ |
| Anthropometric cleaning | 37 heights, 18 weights, 6 BMI; BMI computable 16,699 (99.0%) | 37 / 18 / 6 verified from raw; 16,699 (99.04%) | ✓ |
| "Other" surgical group | 348 (2.1%) | 348 (2.06%) | ✓ |
| Pre-anchor MAP readings | median 3 (IQR 2–4); ≥1 in 16,036 (95.1%) | p25 2, p50 3, p75 4; 16,036 (95.11%) | ✓ |
| Pre-OR 30-min baseline | <1% of cases | 43/16,861 = 0.26% (from raw `patient_vitals.csv`) | ✓ |
| Predictor count | 206 across 13 domains | domain list sums to 206; Table 3 sums to 204 (omits derived medication) | ⚠ (m1) |
| Feature dictionary | — | header `n_features: 207` vs 206 listed | ⚠ (m11) |
| Audit-trail female_n | — | 8,506 vs 8,502 (F) + 4 unknown | ⚠ (m11) |
| Stale JSON note | — | "median OR_start + 13 min" vs 15 min everywhere else | ⚠ (m11) |
| Outcome-positive vs negative | age 48 vs 55; BMI 25.4 vs 26.8; MAP 79.5 vs 89.0; min 72 vs 81 | 48/55; 25.39/26.84; 79.50/89.00; 72/81 | ✓ |
| Pre-anchor event anomalies | not reported | 4 Extubation, 1 CPR, 3 Mayfield before anchor (max lag 2,853 min) | ⚠ (m9) |
| Late anchors | not reported | 325 >60 min (1.93%), 34 >120 min, max 751 min | ⚠ (M4) |
| Medication units | not reported | 1,981/17,683 propofol rows in mcg; 6/1,903 phenylephrine in drops | ⚠ (m8) |
| VitalDB outcome construct | "computed identically" | median 4,356 samples, 29.94/min ⇒ ≈1,307 hypotensive samples ≈ 44 min | ⚠ (S2) |
| VitalDB cadence features | not reported | `map_n` 3→450, `map_n_below_65` 0→23, `vitals_window_n_records` 14→450, `map_minutes_since_last` 1.0→0.02 min | ⚠ (M3) |
| Subgroup AUPRC vs prevalence | "higher in women and younger patients" | Spearman ρ = 0.883 (p = 0.0016) patient, 0.817 (p = 0.0072) temporal; lift 1.89/2.28/1.82 by age, 2.17/2.07 by sex | ⚠ (S3) |

**Not checked (outside my remit or infeasible)**: the content of references [4], [5], [6], [12] (2026 preprints/journal articles I cannot retrieve here); the internal correctness of `scripts/s3_models.py` and `scripts/ext_*.py` estimator/CI code; `scripts/s5_gate.py` execution; the `.docx` rendering; the cover letter; figure image content (I confirmed all six figure files exist in `results/figs/` and matched them to their legends, but did not inspect the pixels).

---

# Verdict

**Major revisions.**

The study is methodologically careful and unusually honest about its own limitations, and the quantitative core is reproducible — I could not find a single wrong number in the tables. But the manuscript's central endpoint is not the quantity its title and Abstract claim, the external check scores the model against a different quantity under the same name, the headline subgroup finding is an artefact of AUPRC's prevalence dependence, and the headline calibration finding is an artefact of transporting an uncalibrated model. In addition, the Limitations section is structurally broken and one summary section contradicts itself. None of these requires new data collection; all are addressable with re-analysis of existing artefacts plus text revision.

**The single change that would most improve the paper:** re-specify the outcome as an explicit, time-anchored cumulative exposure computed on the 1-minute grid in *both* cohorts (reporting both the sample-fraction D1 and a time-based D3/D4 in Table 2), re-run the external check on that common definition, and report subgroup AUPRC alongside stratum prevalence and the AUPRC:prevalence ratio. That single change fixes the endpoint's clinical defensibility, makes the external comparison interpretable, and removes the subgroup artefact — the three problems that most damage the paper's conclusions.
