# A3 — Independent provenance / reproducibility review (Round 6)

**Manuscript:** `manuscript/manuscript_v0.1.md` (+ `.docx`) — "Prediction of cumulative intraoperative hypotension burden from data available at anaesthesia induction: development and internal validation in MOVER/SIS with external validation in VitalDB"
**Reviewer role:** statistical programmer recomputing every headline number from source artefacts and raw data, and auditing the code that produced them.
**Verdict:** **Major revisions** (0 SEVERE, 3 MAJOR, 11 MINOR).

---

## Executive summary

I recomputed the manuscript from the ground up: the cohort waterfall and all 14 outcome definitions from the nine raw EMR CSVs; Tables 1–7 from the result artefacts; the external-validation metrics from the saved per-case predictions; and the bootstrap, calibration, decision-curve and split logic by reading the producing code line by line. The good news is substantial and is reported in § Stands up: every performance, calibration, DCA, subgroup, importance and external number I could recompute reproduced exactly, the primary outcome engine agrees case-by-case (0/16,861 disagreements), the bootstrap resampling is correctly aligned, the "no external refitting" claim is literally true in code, and the quality gate passes 10/10. No number I checked was fabricated.

However, three problems prevent acceptance as it stands. (1) The cohort sentence "16,861 cases contributing 3,559,993 one-minute OR observations" is wrong: the value is computed on a 19,106-case denominator inside `s1_cohort.py` and never refreshed; the true figure for the analysed cohort is 3,379,173 (−5.1%). (2) The manuscript's central reproducibility guarantee — "Every number reported in this manuscript is … traceable through an audit trail (Additional file 1)" — is false for the entire external-validation block and roughly fifteen other reported quantities, and the external pipeline is not reachable from the deposit's own entry point. (3) The external "unchanged 53-feature model" is scored on features whose distributions are up to ~150× outside the training range (pre-anchor MAP count median 450 vs 3), a shift the paper describes qualitatively but never quantifies. Eleven minor items include a mis-rounded anchor percentage that contradicts Figure 1, an audit-trail value (female n) that contradicts the manuscript, a mislabelled exclusion rule, and a mislabelled recording-density quantity.

---

## Findings

### MAJOR-1 — The "3,559,993 one-minute OR observations" is computed on the wrong cohort (19,106 cases, not 16,861)

**【Problem】** The manuscript attributes 3,559,993 OR observations to the 16,861-case analysis cohort, but the value is computed before the short-window, underage and anchor exclusions are applied to the vitals table and is never refreshed.

**【Evidence】** `scripts/s1_cohort.py:124` sets `flow["or_window_observations"] = int(len(vit_w))` while `vit_w` still contains rows for all 19,106 post-implausible PIDs; `vit_w` is restricted to the analysis cohort only later (line 136 after the first `save_json`, line 168 after the anchor exclusion), and the flow dictionary is re-saved at line 180 without recomputing the field. My independent recomputation from `data_raw/_sis_emr_x/EMR/patient_information.csv` + `patient_vitals.csv` (OR-window filter, mirroring the script): **3,559,993 rows for 19,106 PIDs; 3,424,366 for the 17,103-case cohort; 3,379,173 for the final 16,861-case cohort**. There are 0 duplicate (PID, minute) rows, so a row count *is* a valid one-minute-observation count — for the wrong denominator. The sentence appears at `manuscript_v0.1.md:115-116` (and once in the docx). The value is absent from `results/s4_audit_trail.csv`, so the paper's own consistency gate cannot see the error. (By contrast, `or_min_median` = 167 is identical for both cohorts — I verified 167.0 for the final 16,861 — so only the observation count is affected.)

**【Why it matters】** A cohort-level number in the Methods is wrong by 180,820 observations (5.1%). The recording-density argument that anchors the paper's critique of near-perfect AUROCs on sparse data rests on observation counts, so precision matters, and a journal copy-editor or referee recomputing from the deposited pipeline will get a different number than the one printed.

**【Specific fix】** Replace with: "…yielding an analysis cohort of **16,861** cases contributing **3,379,173** one-minute OR observations (3,559,993 before exclusion of 1,632 short-recording, 371 underage and 242 anchor-less cases). Median OR duration was 167 minutes." Add a corresponding row to `s4_audit_trail.csv` (`cohort.or_window_observations, 3379173, results/s1_cohort.json, python scripts/s1_cohort.py`) after recomputing the field on the final cohort.

---

### MAJOR-2 — The central reproducibility claim is false: the audit trail omits the entire external-validation block and ~15 other reported quantities

**【Problem】** The manuscript states that every reported number is traceable through Additional file 1 with its source artefact and reproduce command, but the audit trail contains no external-validation row at all and lacks many other reported quantities.

**【Evidence】** `results/s4_audit_trail.csv` (154 rows) contains **zero** rows matching any of: 6,388; 3,735; 214; 5.73%; 6.1%; AUPRC 0.160 (0.129–0.202); AUROC 0.751 (0.713–0.784); Brier 0.179; mean predicted 0.37; internal 53-feature 0.698 / 0.710 / 0.321 / 0.314 / 0.198 / 0.199 and their CIs. Also missing: 3,559,993 observations; 167-min median OR duration; anchor median 15 min and IQR 11–24 (only p05/p50/p95 = 7/15/46 exist, in `s1_data_quality.json`); post-anchor window p05/p95 (49/440); treat-all net benefit ≈0.06 @0.10 and ≈−2.1 @0.73; the 2.23× AUPRC lift; the 0.131 no-information Brier; pulse-rate density 95.9%; Table-1 height (167) and weight (76) medians; sex-unknown (4); the 13 surgical-group counts; the seed 12,345. The trail generator `scripts/s4_report.py` adds no `results/ext/` row (grep for ext-related `add(` calls: none), and `scripts/run_all.py` runs only s1–s4, so `ext_download.py`, `ext_build.py` and `ext_core_benchmark.py` — the scripts that actually produce every external number — have no reproduce command anywhere in the deposit.

**【Why it matters】** The data/code availability statement is the load-bearing credibility claim of a first submission, and the external validation is the paper's most novel element. As deposited, a reader following Additional file 1 cannot reproduce it, which falls short of the reproducibility expectations the manuscript itself invokes (TRIPOD+AI; references [9–11] on software).

**【Specific fix】** Extend the audit trail with (a) an external block — one row per Table-7 cell plus `ext.n_cases=3735`, `ext.n_events=214`, `ext.prevalence=5.73`, `ext.n_excluded_lt10_post_map=214`, `ext.conditional_prevalence=6.1`, `ext.pred_mean=0.365`, `ext.observed_prevalence=0.057`, each sourced to `results/ext/external_validation.json` with reproduce command `python scripts/ext_build.py apply` (and `python scripts/ext_core_benchmark.py` for the internal 53-feature rows) — and (b) rows for the quantities listed above. Add the three `ext_*.py` stages to `run_all.py` (or document the two-stage external entry point explicitly in the release manifest).

---

### MAJOR-3 — The external "unchanged 53-feature model" is applied to features whose distributions are up to ~150× outside the training range; the shift is never quantified

**【Problem】** Six of the 53 "transportable" features are recording-count/density features that occupy, in VitalDB, a region of feature space essentially empty in MOVER, so "applied without refitting" transports feature names but not feature semantics.

**【Evidence】** Recomputed from `results/ext/vitaldb_features.csv` vs `results/s2_features.csv`: `map_n` median **450 vs 3** (p10–p90: 420–450 vs 1–5); **93.3%** of external cases have >50 pre-anchor MAP readings vs **0.00%** of MOVER cases; `map_minutes_since_last` median 0.02 vs 1.0 min; `vitals_window_n_records` median 450 vs 14; `map_sd` median 11.5 vs 6.4; `vitals_window_actual_min` 14.97 vs 13.0. The external Brier (0.179) and the mean predicted risk of 0.365 against an observed 0.057 therefore reflect this extrapolation in addition to the prevalence and anchor differences the paper does discuss. Limitation 10 (`manuscript_v0.1.md:606`) mentions recording density qualitatively but gives no numbers, and the Methods (`manuscript_v0.1.md:191-203`) presents the 53-feature subset as "transportable" without any distributional check.

**【Why it matters】** Readers cannot apportion the external miscalibration between prevalence shift, anchor shift and feature extrapolation, and the claim that "discrimination transferred" is harder to interpret when the model scores cases in an empty region of its own feature space. This is the difference between a transportability check and an untested assumption.

**【Specific fix】** Add to the external-validation section: "We compared the distribution of the 53 transported features between cohorts (Additional file): the pre-anchor MAP reading count had a median of 450 in VitalDB versus 3 in MOVER/SIS (93.3% vs 0.0% of cases above 50 readings), and minutes-since-last-MAP a median of 0.02 versus 1.0 minutes; count- and density-based features were therefore extrapolations outside the training range." And add the sensitivity analysis: "Re-applying the model without the six count/density features (map_n, map_sd, map_last, map_minutes_since_last, vitals_window_n_records, vitals_window_actual_min; 47 features), the external AUROC was X (95% CI …) and AUPRC Y." (These columns are populated in the external matrix — map_n non-null in 3,491/3,735 cases — so the run is a one-line column subset.)

---

### MINOR-1 — Anchor-share percentages are mis-rounded (82.1%/17.9% should be 82.0%/18.0%) and contradict Figure 1

**【Problem】** The manuscript's intubation/surgery-start anchor shares do not follow from the counts and disagree with the paper's own Figure 1.

**【Evidence】** 13,834/16,861 = **82.047%** → 82.0%; 3,027/16,861 = **17.953%** → 18.0%. Figure 1 (`results/figs/fig1_cohort.png`) prints "Intubation 13,834 (82.0%) | Surgery start 3,027 (18.0%)". The manuscript prints 82.1%/17.9% in the Abstract (`manuscript_v0.1.md:22`), Methods (120-121), Table 1 (253-254) and Limitations (588).

**【Why it matters】** A rounding inconsistency between text, table and figure in four places is exactly what copy-editors flag, and it slightly misstates the proxy-anchor proportion that Limitation 5 builds on.

**【Specific fix】** Replace all four occurrences of "82.1%" with "82.0%" and "17.9%" with "18.0%".

---

### MINOR-2 — The audit trail records female n = 8,506; the manuscript (correctly) reports 8,502

**【Problem】** Additional file 1 contradicts Table 1 on the female count.

**【Evidence】** `scripts/s4_report.py:370` computes `cohort.female_n` as `(_feat["male"] == 0).sum()` = **8,506**, folding the 4 unknown-sex cases (gender values "  Unknown" ×2, " Unknown" ×2 in `results/s2_data_quality.json` → demographics.gender_values) into female. Table 1 (`manuscript_v0.1.md:248`) reports 8,502 (50.4%), which matches the artefact's F count.

**【Why it matters】** The one audit-trail value that directly contradicts the manuscript undermines the trail's authority precisely where it claims to be the single source of truth.

**【Specific fix】** In `s4_report.py`, replace the female-n row with a count of Gender == "F" (8,502, from `s2_data_quality.json` gender_values) and add a row `cohort.sex_unknown_n, 4`.

---

### MINOR-3 — "OR window shorter than 60 minutes" mislabels the implemented exclusion rule

**【Problem】** The cohort flow describes an exclusion by window duration that the code implements as an exclusion by recorded-observation count.

**【Evidence】** `config/config.yaml:34` (`min_or_window_minutes: 60`) is applied in `scripts/s1_cohort.py:113-114` as a count of vitals rows in the OR window (`obs_per_pid >= 60`), not as a duration. My raw recomputation: of the 1,632 excluded cases, **383 had OR windows ≥ 60 minutes** (sparse recording), and **7 retained cases had windows < 60 minutes**. The count 1,632 is correct for the implemented rule; the wording (Cohort section `manuscript_v0.1.md:112-113`; Figure 1 legend line 769-771; figure box "OR window < 60 min") misdescribes ~23% of that exclusion group.

**【Why it matters】** The exclusion reason is part of the spectrum-bias accounting (Limitation 7); describing it inaccurately overstates how much of the exclusion is genuinely short surgery.

**【Specific fix】** "1,632 records with fewer than 60 recorded one-minute observations in the OR window (under the observed ~95% heart-rate recording this approximates an OR window shorter than 60 minutes; 383 of the excluded cases had OR windows of at least 60 minutes but sparser recording)".

---

### MINOR-4 — "19.89% of case-minutes" mislabels the artefact quantity (it is a whole-table row rate; the true OR-window case-minute rate is 19.78%)

**【Problem】** The headline recording-density percentage is a table-level row non-null rate, not a case-minute rate.

**【Evidence】** `scripts/s1_cohort.py:78` computes the rate over the **entire** `patient_vitals` table (3,595,591 rows, 19,023 PIDs, any timestamp; I reproduced 0.1989 exactly), stored as `column_non_null_rate` in `results/s1_data_quality.json`. Recomputed on the correct basis — non-null nMAP rows inside OR windows for the 16,861 cohort (668,486) over OR-window rows (3,379,173) — the rate is **19.78%**. The same artefact is internally inconsistent: per-case mean 39.86 × 16,861 = 672,113 (≈ my 668,486) but 0.1989 × 3,559,993 = 708,083. The same class of number applies to nSBP 19.99%, nDBP 19.95%, HR 94.8%, HRp 95.9%, SpO2 96.1%.

**【Why it matters】** The qualitative claim ("fewer than one in five case-minutes") survives, but the printed number is not the quantity its label promises, and a referee recomputing case-minutes will get 19.8%, not 19.89%.

**【Specific fix】** Either relabel — "non-invasive MAP was recorded in 19.9% of vital-sign rows in the source table and in 19.8% of OR-window case-minutes" — or recompute all six rates on the OR-window case-minute basis and update the manuscript and artefact together.

---

### MINOR-5 — Calibration slope/intercept are described as "on the log-odds scale" but are computed on the probability scale

**【Problem】** The manuscript mislabels the estimator used for the calibration statistics.

**【Evidence】** `scripts/s3_models.py:215`: `sl, ic = np.polyfit(p_cal, yte.values, 1)` — ordinary least squares of the binary outcome on the calibrated probability. The conventional calibration slope/intercept regress the outcome on the **logit** of the prediction. The values (0.909, 0.008) are unremarkable, but the sentence "indicating well-calibrated probabilities on the log-odds scale" (`manuscript_v0.1.md:375-376`) describes a different statistic.

**【Why it matters】** Calibration slope/intercept have a standard definition; reporting a linear-probability-model fit under the log-odds label invites a methodological query from referees.

**【Specific fix】** "Out-of-fold isotonic recalibration reduced the Brier score to 0.119, with a calibration slope of 0.909 and an intercept of 0.008 from linear regression of the observed outcome on the predicted probability, indicating well-calibrated probabilities."

---

### MINOR-6 — "Two hundred and six candidate predictors" overstates the model input by one column

**【Problem】** The predictor count includes a non-numeric column that the modelling code drops.

**【Evidence】** `results/s2_feature_dictionary.json` counts 206 features, including the string column `surg_group`; `scripts/s3_models.py:71-72` drops non-numeric columns (`PID`, `anchor_source`, `surg_group`), so every fitted matrix has **205** numeric predictors (208 CSV columns − 3). The domain breakdown in `manuscript_v0.1.md:144-148` sums to 206 with the same inclusion.

**【Why it matters】** Predictor count feeds the events-per-variable discussion; a one-column discrepancy is trivial numerically but is the kind of definitional slippage a careful referee will find.

**【Specific fix】** "Two hundred and five numeric candidate predictors were constructed across 13 domains (206 columns in the feature dictionary, one of which — surgical group — is retained as a categorical label and excluded from the model matrices)."

---

### MINOR-7 — Two artefacts report slightly different full-model temporal metrics (run-to-run nondeterminism)

**【Problem】** The deposit does not reproduce its own numbers bit-for-bit.

**【Evidence】** `results/s3_metrics.json` temporal XGBoost: AUPRC 0.3392, AUROC 0.7328, Brier 0.1935, pred_mean 0.4098. `results/ext/core_benchmark.json` "full_model" temporal (a refit with the same seed and hyperparameters): AUPRC 0.3396, AUROC 0.7326, Brier 0.1937, pred_mean 0.4095; bootstrap CI bounds differ in the 4th decimal. The manuscript correctly follows `s3_metrics.json`, but rerunning the pipeline does not reproduce the printed values exactly — consistent with XGBoost `n_jobs=-1` histogram nondeterminism.

**【Why it matters】** The reproducibility statement promises traceability; a rerun that yields 0.3396 where the paper prints 0.339 forces an explanation and weakens the audit-trail claim further.

**【Specific fix】** Set `n_jobs=1` for the deposited model-fitting runs (runtime is minutes at this data size), or record per-artefact SHA-256 checksums in the promised `MANIFEST.csv` and state that exact reproduction requires the pinned single-thread configuration.

---

### MINOR-8 — Two of the eight fluid/bleeding features are mislabeled by the code (one identically zero; one stores negated intake under an output name)

**【Problem】** A silent classification bug corrupts the fluid domain's feature definitions.

**【Evidence】** `scripts/s2_features.py:425-437`: `_io_class` never returns `"crystalloid"`, but the rename map at lines 444-445 expects it — so `crystalloid_in_ml` is **0.0 for all 16,861 cases** (verified in `results/s2_features.csv`). All crystalloid intake (pre-anchor rows: Plasmalyte 1,173, lactated ringers 876, 0.9% NaCl 292, D5W 209, …) falls into `"other_out"` and is then **sign-flipped** into `other_output_ml` (observed range −4,000 to +950 mL). Tree models are sign-invariant, so the reported metrics are unaffected; the feature dictionary nonetheless misdescribes 2 of the 8 fluid features the Methods count.

**【Why it matters】** It is a correctness defect in the deposited code that a code-reading referee will find, and it silently zeroes one predictor.

**【Specific fix】** In `_io_class`, return `"crystalloid"` for positive-volume inputs that are not blood/colloid/urine/ebl, and drop the negation for `other_output_ml` (keep it for urine/ebl); regenerate `s2_features.csv` and re-run s3, or — minimally — state in the feature dictionary that `other_output_ml` equals minus crystalloid input.

---

### MINOR-9 — The fuzzy surgical-group fallback is described as "edit distance ≤ 1" but implemented as similarity ratio ≥ 0.90

**【Problem】** The Methods misdescribe the fuzzy-matching rule.

**【Evidence】** `scripts/_common.py:110-114` requires the same initial letter, length ≥ 7, |length difference| ≤ 1 **and** `SequenceMatcher` ratio ≥ 0.90. For a 7-character keyword a single substitution yields ratio 6/7 = 0.857 and is rejected, so the implemented rule is stricter than "edit distance ≤ 1" (`manuscript_v0.1.md:158-160`). 45 cases were fuzzy-matched (`s2_data_quality.json` → procedure_groups.fuzzy_matched_n).

**【Why it matters】** The matching rule determines the surgical-group features (GI is the 7th-highest-gain predictor); the description should match the code so the grouping is reproducible.

**【Specific fix】** "…a controlled fuzzy fallback (same initial letter, minimum length 7 characters, length difference ≤ 1, sequence-similarity ratio ≥ 0.90)".

---

### MINOR-10 — Artefact note misstates the intubation-anchor median (13 vs recomputed 14 min); s2 docstring cites a stale cohort size

**【Problem】** Internal notes contradict the data (the manuscript-facing anchor statistic is correct).

**【Evidence】** The note in `results/s1_outcomes_postanchor.json` and `scripts/s1_cohort.py:35,140` state the first Intubation event occurs at a median of OR_start + 13 min (a6 audit: p05/p50/p95 = 5/13/32). Recomputed from `results/s1_anchor.csv`: intubation-only p05/p50/p95 = **6/14/32**. The manuscript's all-anchor statement (median 15 min, IQR 11–24) is correct and verified. Additionally, the `s2_features.py` docstring still says "分析队列 17,103 行" while the script in fact processes 16,861.

**【Why it matters】** Notes inside deposited artefacts are part of the audit trail; stale numbers there erode trust in the rest of the provenance chain.

**【Specific fix】** Update the note to "median OR_start + 14 min (p05–p95: 6–32)" and the s2 docstring to 16,861.

---

### MINOR-11 — Median imputation for the logistic models is fit on the full cohort before splitting

**【Problem】** The imputation design does not literally implement "within the training data".

**【Evidence】** `scripts/s3_models.py:79-81` fits `SimpleImputer` on all 16,861 cases; the split occurs at line 176. With n = 16,861 the median shift from the 20% test share is negligible and the tree models are unaffected (native NaN handling), but the imputer's medians and missingness indicators do see test-set values.

**【Why it matters】** It is a protocol-purity issue that a methods-focused referee can raise from the code alone; the fix costs nothing.

**【Specific fix】** Move the imputer inside the split (fit on the training partition only, transform both), or state in the Methods that medians were computed on the full cohort before splitting.

---

## § Stands up (verified correct, with evidence)

1. **Cohort waterfall — reproduced exactly from raw data.** My independent mirror of `s1_cohort.py` over the nine raw CSVs reproduces 19,114 screened → 8 implausible (4 non-positive duration, 4 > 1,440 min, max observed 3,156,668 min) → 1,632 short-recording → 371 underage → 17,103 → 242 bad anchor → **16,861**, with `excl_missing_or_window` = 0; Figure 1's intermediate boxes (19,106 / 17,474 / 17,103) are all correct, and the anchor counts (13,834 / 3,027) match.
2. **All 14 Table-2 definitions — reproduced exactly from raw data.** Re-running the 1-minute-grid outcome engine (NaN = interruption) on the raw post-anchor windows reproduces every count: O1 15, O2 54, O3 2, O4 27, S1 1,214, B1 7,240, B2 5,192, B3 1,159, D1 2,622, D2 91, E1 3,770, E2 11,091, O5 1,292, O6 572 — and the per-case D1 labels agree with `s1_labels_postanchor.csv` for **0/16,861 disagreements**. The v1.1.0 "dropna compresses the time axis" defect is genuinely absent from the current engine (`s1_cohort.py:189-197` re-expands to a full minute grid before run detection).
3. **Table 4 — all eight model×split rows match `s3_metrics.json` to the printed precision**, including all 16 bootstrap CI bounds, and the derived statements check out: 2.23× lift (0.3473/0.1555 = 2.233), no-information Brier 0.131 (0.1555 × 0.8445), and the "no-skill AUPRC = prevalence" statement is internally consistent.
4. **The bootstrap CI method is sound.** `s3_models.py:91-103` (and `ext_core_benchmark.py:63-70`, `ext_build.py:242-250`) draw one index vector `s` and evaluate `fn(yt[s], yp[s])` on the same resample — features and labels cannot be misaligned; there is no analogue of the `fit(Xp, yb)` class of bug. 1,000 resamples, percentile method, seed 12,345, as stated.
5. **The patient-level split and every Table-5 stratum size reproduce exactly**: re-running `train_test_split(..., test_size=0.2, random_state=12345, stratify=y)` on `s2_features.csv` + labels yields 13,488/3,373 with 525 test events, and stratum n's of 1,689/1,684 (sex), 1,402/1,044/927 (age), 98/1,202/1,064/977 (BMI) — identical to Table 5; all 18 subgroup AUPRCs match `s3_subgroups.json` within rounding.
6. **Calibration and DCA verified in full**: 0.191→0.119 with slope 0.909 / intercept 0.008 (patient) and 0.194→0.122 with 0.934 / 0.006 (temporal); net benefit 0.079/0.050 (patient) and 0.085/0.058 (temporal) at thresholds 0.10/0.15; the sign pattern is exactly as described (patient positive 0.01–0.58, first negative 0.59; temporal positive 0.01–0.45, negative 0.46–0.65, positive 0.66–0.73); treat-all ≈0.06 at 0.10 and ≈−2.1 at 0.73; MAP-only benchmark AUPRC 0.284 with incremental net benefit 0.013 at both thresholds. The calibration protocol itself is correct: isotonic fitted on 5-fold out-of-fold training predictions, applied unchanged to the test set (`s3_models.py:206-211`).
7. **External validation verified end-to-end.** Recomputing from `results/ext/vitaldb_predictions.csv` gives AUPRC 0.1600, AUROC 0.7507, Brier 0.1789, mean predicted 0.3650 — exact matches — and the bootstrap CIs reproduce exactly ([0.1291, 0.2021]; [0.7133, 0.7844]) with seed 12,345. The "no refitting" claim is literally true: `ext_build.py:227-236` only calls `predict_proba` on the joblib-serialised MOVER model. The cohort derivation reproduces from `data_vitaldb/`: 6,388 cases, exactly 3,735 with a Solar8000/EV1000 ART_MBP track (all with valid opstart/opend), 214 events (5.73%), 214 negative-by-construction (6.1% of 3,521). The internal 53-feature numbers (0.698/0.710; 0.321/0.314; 0.198/0.199) match `ext/core_benchmark.json` and `ext/mover_core_train_metrics.json`, and the derived statements (2.8× vs 2.1× lift; CI overlap) are arithmetically correct.
8. **Leakage audit verified**: all seven time-stamped domains show maximum interval to anchor 0.00 min and zero unparseable timestamps (`s2_data_quality.json`; hard-exit guard at `s2_features.py:71-73`); the 15-minute pre-anchor truncation is implemented as described for vitals/observations/ventilator, and ≤anchor-only truncation for medication/labs/fluids/events.
9. **Descriptive statistics verified**: Table 1 medians/IQRs (age 54 [39–66]; height 167 [160–175]; weight 76 [63–90]; BMI 26.6 [23.1–30.9]; pre-anchor mean MAP 87.7 [77.7–98.5]; 3 [2–4] pre-anchor MAP readings), the outcome-group contrasts (48 vs 55 years; 25.4 vs 26.8 kg/m²; 79.5 vs 89.0 mmHg; 72 vs 81 mmHg), the 512-case underweight stratum, the BMI cleaning (37 heights, 18 weights, 6 BMI → NaN; 16,699 computable = 99.0%), surgical-group counts, all Table-3 coverage numbers (16,036 = 95.1% with ≥1 pre-anchor MAP reading; 2,503/4,852/76/2,794), segment statistics (637,188 segments, 96.2% single-minute, median 33 [12–90] MAP/case), and the "<1% of cases with any MAP in the 30 min before OR start" limitation (43/16,861 = 0.26%). Anchor timing (median 15, IQR 11–24) and post-anchor window (147; 49–440) verified from `s1_anchor.csv`.
10. **Software environment matches the manuscript**: Python 3.13.14, pandas 2.3.3, scikit-learn 1.9.0, XGBoost 3.4.1, LightGBM 4.7.0 in the project venv — exactly the versions claimed.
11. **`scripts/s5_gate.py` runs clean: Overall PASS (10/10 checks)** — verbatim output in § What I actually checked.

---

## § Questions for the authors

1. Should `or_window_observations` be recomputed on the 16,861-case cohort (3,379,173), and is the intended denominator for the Methods sentence the analysed cohort (as written) or the eligible cohort?
2. Why is the external-validation block absent from Additional file 1, and can `ext_download.py` / `ext_build.py` / `ext_core_benchmark.py` be added to `run_all.py` and the release manifest so every Table-7 number has a reproduce command?
3. For the external model: was any check performed that the 53 transported features overlap in distribution (pre-anchor MAP count median 450 vs 3)? If not, can the shift table and the count/density-excluded sensitivity run be added?
4. Is the intended short-window rule the observation-count rule (as implemented) or the duration rule (as worded)? 383 cases are classified differently by the two rules.
5. Can you confirm that the 0.3392 vs 0.3396 temporal AUPRC difference between `s3_metrics.json` and `ext/core_benchmark.json` is XGBoost `n_jobs=-1` nondeterminism, and pin `n_jobs=1` for the deposit?
6. The 242 anchor-less cases contribute 45,193 OR-window vitals rows (186.7 per case vs a cohort mean of 201.5) — were they audited for systematic differences (e.g., pre-OR-recorded Surgery_start timestamps) beyond the exclusion itself?
7. The `s1_outcomes_postanchor.json` note cites a 13-minute intubation-anchor median; the recomputed value is 14 minutes — which is authoritative?

---

## § What I actually checked

**Files read (complete list):** `manuscript/manuscript_v0.1.md`; `manuscript/manuscript_v0.1.docx` (text extraction); `results/s1_cohort.json`, `s1_data_quality.json`, `s1_outcomes.json`, `s1_outcomes_postanchor.json`, `s1_anchor.csv` (header/sample), `s1_labels_postanchor.csv`, `s2_data_quality.json`, `s2_feature_dictionary.json`, `s2_features.csv`, `s3_metrics.json`, `s3_calib_dca.json`, `s3_subgroups.json`, `s3_feature_importance.json`, `s4_audit_trail.csv`, `results/ext/{external_validation.json, core_benchmark.json, core_cols.json, mover_core_train_metrics.json, vitaldb_features_qa.json, vitaldb_features.csv, vitaldb_labels.csv, vitaldb_predictions.csv}`, `data_vitaldb/{cases.csv, trks.csv}`, `results/figs/fig1_cohort.png` (viewed); scripts `s1_cohort.py`, `s2_features.py`, `s3_models.py`, `s4_report.py` (audit-trail section), `s5_gate.py`, `run_all.py`, `_common.py`, `ext_pipeline.py`, `ext_build.py`, `ext_core_benchmark.py`; `config/config.yaml`. Raw data: `data_raw/_sis_emr_x/EMR/{patient_information.csv, patient_vitals.csv, patient_procedure_events.csv}` (full); `patient_vitals.csv` verified to have 0 duplicate (PID, minute) rows.

**Commands run** (Python 3.13.14, pandas 2.3.3, sklearn 1.9.0, XGBoost 3.4.1, LightGBM 4.7.0, project venv):
1. Artefact-level recomputation of all ten manuscript claim groups (waterfall, Table 2, anchor timing, Table 1/Table 3, Table 4, calibration/DCA, subgroups/importance, external metrics from saved predictions, density, audit-trail coverage).
2. Raw-data recomputation mirroring `s1_cohort.py` (waterfall, anchors, OR-window observation counts, per-case MAP statistics, D1 labels).
3. Raw-data recomputation of all 14 outcome definitions with the 1-minute-grid engine (3m13s runtime).
4. External cohort derivation from `data_vitaldb` raw extracts; MOVER-vs-VitalDB feature-distribution comparison; reproduction of the patient-level split and all Table-5 stratum sizes; docx text extraction and key-number cross-check.
5. `python scripts/s5_gate.py` — verbatim output:

```
Overall: PASS
[PASS] Abstract word count <= 350 :: 346 words (limit 350)
[PASS] Total word count reported :: 8335 words
[PASS] References count == 18 :: 18 references found
[PASS] References numbered contiguously 1..N :: 1..18
[PASS] docx embeds 6 figures :: 6 images
[PASS] docx has 7 tables :: 7 tables
[PASS] Key headline numbers present :: all 34 present
[PASS] DCA net benefit @0.15 matches s3 :: patient @0.15=0.050 vs ms 0.050 (Δ0.0003); temporal @0.15=0.058 vs ms 0.058 (Δ0.0001)
[PASS] DCA sign guard (temporal<0 @0.50, patient>0 @0.50) :: temporal@0.50=-0.0022, patient@0.50=0.0033
Report written: .../review/quality_gate_2026-10-20.md
```

Note on the gate: it verifies that key numbers are *present* and that two DCA values equal hard-coded manuscript constants — it cannot detect a wrong number that is consistently wrong, and indeed it passes while MAJOR-1 and MINOR-1 stand.

**Values recomputed vs the manuscript — discrepancies found:**

| Manuscript value | My recomputation | Status |
|---|---|---|
| 16,861 cases contributing 3,559,993 OR observations | 3,379,173 for 16,861 (3,559,993 = 19,106-case denominator) | **WRONG (MAJOR-1)** |
| Anchor 82.1% / 17.9% | 82.047% / 17.953% → 82.0% / 18.0% (Figure 1 agrees with me) | **WRONG (MINOR-1)** |
| Audit trail "every number … traceable" | external block + ~15 quantities absent; female n 8,506 vs 8,502 | **FALSE (MAJOR-2, MINOR-2)** |
| "19.89% of case-minutes" | 19.89% = whole-table row rate; case-minute rate = 19.78% | **MISLABELLED (MINOR-4)** |
| "OR window shorter than 60 minutes" (n=1,632) | rule = <60 recorded rows; 383 had windows ≥60 min | **MISLABELLED (MINOR-3)** |
| "206 candidate predictors" | 205 numeric columns enter the model | **OFF BY ONE (MINOR-6)** |
| Calibration "on the log-odds scale" | polyfit on probability scale | **MISLABELLED (MINOR-5)** |
| Full-model temporal AUPRC 0.339 (s3_metrics) vs 0.3396 (core_benchmark) | both artefacts exist; rerun not bit-reproducible | **NONDETERMINISM (MINOR-7)** |
| Fluid features (8) | crystalloid_in_ml ≡ 0; other_output_ml = −(crystalloid intake) | **CODE BUG (MINOR-8)** |
| Fuzzy "edit distance ≤ 1" | ratio ≥ 0.90 (stricter) | **MISLABELLED (MINOR-9)** |
| Note: intubation anchor median 13 min | 14 min (6/14/32) | **STALE NOTE (MINOR-10)** |
| Waterfall 19,114→17,103→16,861; exclusions 8/1,632/371/242; OR median 167 min; anchor 15 (11–24); window 147 (49–440); all Table-1, Table-2 (14/14), Table-3, Table-4 (8/8 + 16 CIs), Table-5 (18 AUPRCs + 9 stratum n's), Table-6 (10 gains), Table-7, calibration, DCA, MAP-only benchmark, density, BMI cleaning, leakage audit, external metrics + CIs + cohort derivation | all reproduce exactly | **VERIFIED** |

---

## Verdict

**Major revisions.** Nothing I could recompute was fabricated, and the statistical core (splits, bootstrap, calibration protocol, outcome engine, external application) is sound and honest about its limitations; but a headline cohort number is computed on the wrong denominator, the manuscript's central traceability guarantee is false for the entire external-validation block, and the external feature shift is unquantified.

**The single change that would most improve the paper:** rebuild Additional file 1 so that every reported number — above all the entire external-validation block, which currently has no row and no reproduce command — appears with its source artefact and reproducing command, correcting in the same pass the two numbers that currently contradict the artefacts (3,559,993 → 3,379,173 OR observations for the 16,861-case cohort; 82.1%/17.9% → 82.0%/18.0%). That one change converts the paper's reproducibility claim from aspirational to true and forces the remaining numeric slips into the open.
