# A2 — Independent review: study design / TRIPOD+AI methodology

**Manuscript:** `manuscript/manuscript_v0.1.md` — "Prediction of cumulative intraoperative hypotension burden from data available at anaesthesia induction: development and internal validation in MOVER/SIS with external validation in VitalDB" (target: BMC Anesthesiology)
**Reviewer role:** statistician with epidemiology and clinical-prediction-model expertise; reviewed as a first submission.
**Date:** 2026-10-20

---

## Executive summary

The engineering of this pipeline is unusually disciplined for a single-author study: every headline number I checked reproduces exactly from the artefacts, the split logic, calibration protocol and cohort waterfall all match the prose, and an independent refit of the XGBoost on the same split returned AUPRC 0.3473 / AUROC 0.7223 — identical to the manuscript to four decimals. The problems are therefore not in the arithmetic but in the design arguments the paper does **not** make, and in two places where the prose overclaims relative to what the code actually does.

Three findings would each alone justify major revisions. (1) The full logistic model is fitted on a 335-parameter design with 2,097 training events — events per variable ≈ 6.3 — and the manuscript contains no sample-size, EPV or shrinkage discussion at all, while the gradient-boosted models get no effective-degrees-of-freedom argument either. (2) The leakage audit, which the paper markets as a core contribution ("zero residual horizon overlap"), only verifies that features do not postdate the anchor; it never checks that the label window excludes the feature window. Both windows are closed at the anchor minute, and I quantify the overlap: 4,787 cases (28.4%) have a MAP reading exactly at the anchor, 648 of them below 65 mmHg, and 769 of the 2,622 D1-positive cases (29.3%) have that value inside their own label. (3) The external analysis is called a "transportability check" in the body — correctly — but the title, the abstract's first sentence, the TRIPOD type 2b claim and "What this study adds" item 5 still sell it as external validation; and the transported 53-feature model derives 10.8% of its gain from recording-density features on which the external cohort has *zero* training support (VitalDB density ≈ 450 samples vs a MOVER maximum of 16), while its second-highest-gain feature is frozen at a constant. A sensitivity analysis restricting the cohort to the 15,365 evaluable cases is the single missing analysis that most directly tests whether the headline is inflated by the negative-by-construction rule.

Verdict: **Major revisions.** No finding invalidates a reported number; all are fixable by analysis additions and honest re-framing.

---

## Findings

### MAJOR 1 — No events-per-variable or shrinkage accounting anywhere, despite a 335-parameter logistic design on 2,097 events

【Problem】The manuscript fits a logistic model with all 206 candidate predictors plus missingness indicators (a 335-column design matrix) on 2,097 training events — events per variable ≈ 6.3 — and never mentions EPV, sample size, shrinkage or penalisation anywhere in Methods, Results or Limitations; the tree models get no effective-degrees-of-freedom argument either.

【Evidence】I recomputed from `results/s2_features.csv`: 205 numeric model columns (206 dictionary features plus `anchor_source`, minus the two object columns `anchor_source`/`surg_group` dropped at `scripts/s3_models.py:71-72`), of which 130 contain missing values; `scripts/s3_models.py:79-81` applies `SimpleImputer(strategy="median", add_indicator=True)`, giving a design width of 205 + 130 = **335 columns**. The patient-level training split contains 13,488 cases with 525 test events out of 2,622 total, i.e. **2,097 training events** → EPV = 2,097/335 = **6.3** (full-cohort EPV 7.8). The manuscript's "Model development" section (`manuscript_v0.1.md:169-177`) lists hyperparameters only; the words "events per variable", "shrinkage", "overfitting" and "penal" do not appear. Note also that `scripts/s3_models.py:128-133` relies on scikit-learn's default L2 (C = 1.0), which the manuscript does not disclose as a regulariser.

【Why it matters】EPV ≈ 6 is roughly a third of the classical ≥ 20 rule (and below even the lenient ≥ 10), and it is the number a prediction-model reviewer will compute in the first ten minutes. Without an EPV statement, a shrinkage argument (e.g. penalisation strength chosen by cross-validation, or uniform shrinkage of the logistic linear predictor), or an honest effective-df statement for the boosted models, the full logistic's 0.301 AUPRC cannot be interpreted, and TRIPOD+AI's sample-size item is unanswered. The tree models are less exposed (300 trees × depth 4, lr 0.05, min_child_weight 10, subsample/colsample 0.8 on 13,488 cases is a conservative configuration), but the paper never says so, and no tuning procedure is reported, so a reader cannot tell whether the hyperparameters are pre-specified or post hoc.

【Specific fix】Add to Methods (Model development), after the hyperparameter sentence: "With 2,097 outcome events in the training split and a 335-column design matrix after missingness indicators, the full logistic model operates at approximately 6 events per variable; it was therefore fitted with L2 penalisation (C = 1.0, the scikit-learn default) on standardised predictors, and its apparent performance should be read as potentially optimistic. The boosted models were fitted with fixed, pre-specified hyperparameters (300 trees, depth 4, learning rate 0.05, minimum child weight 10, 0.8 row and column subsampling), a configuration whose effective degrees of freedom are bounded by the number of leaves and shrinkage rather than by the 205 predictors; no hyperparameter search was performed, and the held-out test set was used once." Optionally add a penalised-logistic row (e.g. L2 with C chosen by 5-fold CV on training only) to Table 4.

---

### MAJOR 2 — The leakage audit never checks the label window; features and label share the anchor minute

【Problem】The audit verifies that no used observation postdates the anchor (maximum interval 0.00 min) but never verifies that the outcome window excludes the feature window — and in fact both windows are closed at the anchor minute, so a MAP reading at exactly the anchor time simultaneously feeds a predictor and the D1 label.

【Evidence】Label window: `scripts/s1_cohort.py:185` filters `post_w` to `Obs_time >= anchor_time` (inclusive). Feature window: `scripts/s2_features.py:62` keeps `time <= anchor` and `:81` keeps `_pre_min >= 0`, i.e. `[anchor − 15 min, anchor]` inclusive. The audit field is `max_used_time_minus_anchor <= 0` (`scripts/s2_features.py:71-73`), which *cannot* detect the shared instant. I recomputed the overlap from `data_raw/_sis_emr_x/EMR/patient_vitals.csv` joined to `results/s1_anchor.csv`: **4,787 cases (28.4% of 16,861) have a non-missing nMAP reading at exactly the anchor minute; 648 of those readings are < 65 mmHg and therefore enter both the pre-anchor feature statistics (`map_mean`, `map_frac_below_65`, …) and the post-anchor label (the ≥ 10-measurement count and the ≥ 30% fraction); 769 of the 2,622 D1-positive cases (29.3%) have their label computed over a window that includes the anchor-minute value.** The same closed–closed boundary exists in the external pipeline (`scripts/ext_build.py:84` label `>= opstart`; `:100/:113` features `<= opstart`). The manuscript advertises the opposite: "across all seven time-stamped domains the maximum interval between any used observation and the anchor was 0.00 minutes" (`manuscript_v0.1.md:154-156`), "All seven time-stamped predictor domains were truncated at the prediction origin with zero residual horizon overlap" (`:619-623`).

【Why it matters】The magnitude per case is small (one reading among ≥ 10 label measurements and among ~3 feature-window statistics), so the bias is almost certainly minor in direction and size — but the paper's own headline methodological claim is that horizon overlap is zero, and a careful reader who checks the boundary condition will find that claim false as stated. This is exactly the class of defect (label–feature window overlap) that the manuscript itself flags as a hazard in the literature it criticises (`:532-535`), so surviving it here would cost credibility disproportionately to its size.

【Specific fix】Make the boundaries half-open: label window `(anchor, OR_end]` (strictly after the anchor) with the feature window `[anchor − 15 min, anchor]`, or the reverse, and re-run s1–s3; then restate the audit sentence as: "The leakage audit verified that no used observation postdated the anchor (maximum interval 0.00 minutes) and that the outcome window began strictly after the feature window ended, so no measurement contributed to both a predictor and the label." If re-running is not feasible, disclose: "A MAP reading coincident with the anchor minute (present in 4,787 cases, 28.4%; < 65 mmHg in 648) is included in both the pre-anchor feature statistics and the post-anchor outcome window; the resulting overlap is bounded at one measurement per case and its effect is expected to be negligible, but it was not eliminated."

---

### MAJOR 3 — Imputation preprocessing is fitted on the full cohort, including the test set

【Problem】The median imputation and missingness indicators used by both logistic models are computed on all 16,861 cases before any split, so the held-out test set contributes to the preprocessing that the model consumes.

【Evidence】`scripts/s3_models.py:79-81`: `imp = SimpleImputer(strategy="median", add_indicator=True)` then `imp.fit_transform(X)` on the full `X` (all 16,861 cases); the resulting `X_log` is subsetted per split at `:193-194`. The tree models are unaffected (native missing handling), but both logistic rows in Table 4 use `X_log`. The manuscript's leakage-control narrative (`:150-156`, `:619-623`) does not mention preprocessing.

【Why it matters】The leak is label-agnostic (medians of feature columns), so the optimism is negligible in practice — but the paper's central methodological selling point is a strict, audited separation of training and test information, and this is a visible hole in it. A statistical reviewer will note that TRIPOD+AI expects all data-driven preprocessing to be fitted within training data only.

【Specific fix】Wrap the logistic branch in a `Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True)), ("scaler", StandardScaler()), ("clf", LogisticRegression(...))])` fitted on the training split only, and add to Methods: "Median imputation, missingness indicators and standardisation were fitted within the training split only and applied unchanged to the test split."

---

### MAJOR 4 — The negative-by-construction rule is a missing-not-at-random label mechanism with a visible model proxy, and no sensitivity analysis is reported

【Problem】1,496 cases (8.9%) with fewer than 10 post-anchor MAP measurements are labelled D1-negative by construction; this is MNAR with respect to monitoring intensity, the model can see a strong proxy for it, and the paper reports no analysis of how much of the headline discrimination this rule manufactures.

【Evidence】Recomputed from `results/s1_anchor.csv` + `results/s1_labels_postanchor.csv`: 1,496 = 1,332 cases with 1–9 post-anchor measurements + 164 cases with none; all are D1 = 0 by rule; conditional prevalence among the 15,365 evaluable cases is 2,622/15,365 = 17.1% (as the manuscript states at `:597-600`). The visible proxy: **42.9% of negative-by-construction cases have a Surgery-start anchor versus 18.0% of the cohort overall** (recomputed from `results/s2_features.csv`), and `anchor_is_intubation` is the third-highest-gain feature of the headline model (gain 72.2, `results/s3_feature_importance.json`). The model indeed scores these cases lower: mean predicted probability 0.309 for negative-by-construction cases vs 0.406 for evaluable negatives (recomputed on the patient-level test split with the manuscript's exact XGBoost specification). The manuscript's limitation 7 (`:596-602`) acknowledges the spectrum effect descriptically and "What this study adds" item 3 (`:630-633`) calls the accounting "transparent", but no restricted-cohort re-analysis exists in any artefact.

【Why it matters】Part of the model's apparent discrimination may be the ability to recognise "this case will not be monitored enough to count" (short, non-intubated, Surgery-start-anchored cases) rather than physiological hypotension risk — an inflation channel that runs directly into the paper's AUPRC headline. The direction is plausible but unbounded; the fix is cheap and would either confirm the headline or quantify its inflation. Leaving it unquantified while calling the accounting "transparent" invites a harsher reviewer response than the analysis itself would.

【Specific fix】Add a pre-specified-style sensitivity analysis: restrict to the 15,365 cases with ≥ 10 post-anchor MAP measurements, repeat the identical patient-level split, four models, isotonic-OOF calibration and bootstrap, and report a one-row-per-model table (n_train, n_test, events, AUPRC, AUROC, Brier) beside Table 4, with the sentence: "Restricting the cohort to the 15,365 evaluable cases (conditional prevalence 17.1%) changed XGBoost AUPRC from 0.347 to X and AUROC from 0.722 to Y, indicating that the negative-by-construction rule did / did not materially inflate the headline." Also report the mean predicted risk of the 1,496 excluded cases versus evaluable negatives as a diagnostic of proxy exploitation.

---

### MAJOR 5 — Title, abstract, TRIPOD type and the contribution list sell an "external validation" that the body itself calls a transportability check

【Problem】The manuscript's own Limitations and Conclusions correctly downgrade the VitalDB application to "a transportability check rather than a like-for-like validation", but the title, the abstract's opening claim, the TRIPOD type 2b classification and contribution item 5 still present it as external validation — an internal contradiction on the paper's most consequential framing question.

【Evidence】Title (`manuscript_v0.1.md:1`): "…with external validation in VitalDB". Abstract (`:16-18`): "We developed and validated (internally and externally) a model…". Methods (`:98-99`): "it corresponds to TRIPOD type 2b (development with internal and external validation)". "What this study adds" item 5 (`:639-643`): "**An honest external validation on an independent resource.**" Against: Abstract (`:37-39`) "this is a transportability check, not a like-for-like validation"; Conclusions (`:651-652`) "a transportability check rather than a like-for-like validation, because the external anchor (operation start) postdates induction"; Limitations 1 (`:558-577`). The adaptations are real and self-declared: anchor phase shift (opstart postdates induction), the re-derived timing feature changes meaning (`:196-200`), selection to 3,735 of 6,388 cases (58.5%), and 214 external cases negative by construction (5.7% of the external cohort).

【Why it matters】A reviewer or editor who reads only the title, abstract and type claim will evaluate the paper as a type 2b development-and-external-validation study and then discover in the Limitations that the external piece has a different anchor phase, a 53-feature subset instead of the 206-feature headline model, and a frozen predictor. That gap between claim and content is the single most likely trigger for a major-revision or desk-reject reaction, and it is entirely avoidable because the body already contains the honest framing.

【Specific fix】Retitle to "…development and internal validation in MOVER/SIS with a transportability assessment in VitalDB"; change the abstract to "We developed a model and assessed its internal validity and its transportability to an independent cohort (VitalDB)"; change the type statement to "TRIPOD type 1b (development with internal validation), accompanied by a transportability analysis in an external cohort"; and retitle contribution item 5 "An honest transportability assessment on an independent resource."

---

### MAJOR 6 — The "transportable" 53-feature subset contains features on which the external cohort has zero training support, and the second-highest-gain feature is frozen at a constant; the shift is nowhere quantified

【Problem】The 53-feature core model applied unchanged to VitalDB derives 10.8% of its total gain from recording-density features whose external values (median ≈ 450 samples) lie far outside the entire MOVER training range (maximum 16), freezes its second-highest-gain feature at a constant 0, and applies a timing feature whose median shifts from 15 to 41 minutes — none of which is quantified anywhere in the manuscript.

【Evidence】Recomputed from `results/ext/mover_core_model.joblib` and `results/ext/vitaldb_features.csv` vs `results/s2_features.csv`: density/count features (`*_n` plus `vitals_window_*`) carry 162.6 of 1,498.4 total gain = **10.8%**; MOVER `map_n` median 3 (p95 6, max ≤ 16) vs VitalDB median 450 — **zero of 16,861 MOVER cases reach the VitalDB 5th percentile (366)** for either `map_n` or `vitals_window_n_records`; `anchor_is_intubation` (gain 76.9, second-highest) is constant 0 in VitalDB (`scripts/ext_build.py:146`) versus a 82.1/17.9 split in MOVER; `anchor_minus_or_start` (gain 50.4) has MOVER median 15 (IQR 11–24) vs VitalDB median 41.0 (p05 19.8, p95 72.5), i.e. roughly half the external cohort exceeds the MOVER p95 of 46; `or_year` is constant 0. Two further construction asymmetries: `vitals_window_n_records` counts *all* vitals rows in MOVER (`scripts/s2_features.py:258-260`) but *MAP rows only* in VitalDB (`scripts/ext_build.py:132`), so the feature's meaning changes as well as its scale; and `map_sd`/`map_slope` are computed from ~3 points in MOVER versus ~450 in VitalDB. The observable consequence: external predictions are inflated across the whole range — top decile mean predicted risk 0.804 vs observed 0.190, overall 0.365 vs 0.057 (recomputed from `results/ext/vitaldb_predictions.csv`).

【Why it matters】The paper's external claim is that "ranking transferred" (AUROC 0.751). Ranking can transfer *despite* the density extrapolation, but a reader cannot judge how much of the transported model's behaviour is driven by splits on features that are constant, shifted or out-of-support in the external cohort — 10.8% of gain on out-of-support features plus 5.1% on a frozen feature plus 3.4% on a shifted feature is not a rounding error. The manuscript discloses the anchor adaptation qualitatively (`:186-200`, `:561-576`) but never tells the reader these numbers, and the `vitals_window_n_records` definitional asymmetry is not disclosed at all.

【Specific fix】Add a short "feature-space shift" paragraph (or Table) to the external-validation section reporting, for the 53 core features: the MOVER median (IQR) vs the VitalDB median (IQR) for `map_n`, `vitals_window_n_records`, `anchor_minus_or_start`, `map_mean`; the share of MOVER training cases below the VitalDB 5th percentile for each density feature; and the gain share of features that are constant, out-of-support or re-defined externally. Add one sentence: "Because `vitals_window_n_records` counts all vital-sign records in MOVER but arterial MAP records only in VitalDB, this feature is not strictly comparable across cohorts and was a candidate for exclusion; its gain in the core model was 26.2 (1.7% of total)."

---

### MAJOR 7 — Subgroup claims: a 10-event stratum, prevalence-confounded AUPRC comparisons, no interval estimates

【Problem】Table 5 presents nine subgroup AUPRCs per split with no confidence intervals, no stratum prevalences and no multiplicity control, and the text converts the point estimates into systematic claims — while one stratum rests on 10 events and stratum prevalences differ by more than twofold, which alone moves AUPRC.

【Evidence】Recomputed on the patient-level test split (reproducing the manuscript's exact XGBoost fit): BMI < 18.5 kg/m² has n = 98 and **10 events** (AUPRC 0.616 as reported); age ≥ 65 has n = 927 and 84 events (AUPRC 0.186). Stratum **prevalence ranges from 9.1% (age ≥ 65) to 20.1% (age < 50)** — women 16.9% vs men 14.2%; BMI < 18.5 10.2% vs BMI 18.5–25 19.8% — so the "monotonic decline with age" and "highest in underweight patients" patterns are partly mechanical (AUPRC scales with the base rate), not purely discrimination differences. The manuscript's own caveat (`:415-417`) flags the underweight stratum as unstable but the Results and Discussion still assert "Performance varied systematically" (`:394-396`) and "declined sharply with age" (`:503-504`), and the underweight 0.616 appears in the abstract-adjacent narrative without its 10-event basis.

【Why it matters】Subgroup AUPRCs without CIs or stratum prevalences are not interpretable, and 0.616 on 10 events is noise with a decimal point. Presented as "systematic", these patterns invite clinical inferences (e.g. "the model fails in the elderly") that the analysis cannot support — and a methods reviewer will read the table as unadjusted multiple testing (9 strata × 2 splits).

【Specific fix】Extend Table 5 with per-stratum columns n, events, prevalence, AUROC and a bootstrap 95% CI for AUPRC, and add: "Subgroup AUPRCs are exploratory, are reported without adjustment for multiple comparisons, and are not directly comparable across strata because stratum prevalence ranged from 9.1% to 20.1%; strata with fewer than ~50 events (BMI < 18.5 kg/m², 10 events) are reported for completeness only." Compute subgroup metrics on the raw (uncalibrated) scores.

---

### MAJOR 8 — Calibration slope and intercept are mislabeled: the computation is on the probability scale, the text claims the log-odds scale

【Problem】The manuscript reports "a calibration slope of 0.909 and an intercept of 0.008, indicating well-calibrated probabilities on the log-odds scale", but the computation is an ordinary least-squares regression of the outcome on the predicted probability — a different, non-standard quantity from the logistic-recalibration slope/intercept that readers will assume.

【Evidence】`scripts/s3_models.py:215`: `sl, ic = np.polyfit(p_cal, yte.values, 1)` — i.e. y regressed on p (probability scale), not logit(y) ~ a + b·logit(p) as in the standard Van Calster calibration assessment. The manuscript text at `:374-376` states "with a calibration slope of 0.909 and an intercept of 0.008, indicating well-calibrated probabilities on the log-odds scale" (and `:377` repeats it for the temporal split).

【Why it matters】"Calibration slope/intercept on the log-odds scale" has a precise meaning in the prediction-model literature (slope 1, intercept 0 after logistic recalibration); the reported numbers are from a different regression, so a reader benchmarking this model against the literature will compare non-comparable quantities. The numbers themselves are favourable, so this is a labelling defect rather than a false claim — but it sits in the paper's calibration paragraph, the section a statistical reviewer reads most closely.

【Specific fix】Either compute the standard quantity — fit `LogisticRegression` on logit(p_cal) against y on the test set and report its slope and intercept — or restate: "Regressing the observed outcome on the calibrated predicted probability gave a slope of 0.909 and an intercept of 0.008, indicating good agreement on the probability scale; the calibration curve is shown in Figure 4."

---

### MINOR 1 — Tension between "the protocol was fixed before modelling" and a data-informed choice of the primary outcome

【Problem】The manuscript states the analysis protocol was fixed before modelling, but the configuration shows the primary outcome D1 was selected from the 14 candidates with knowledge of their event counts (the rejected O2 had "only 60 events"), which is outcome selection informed by the data.

【Evidence】`config/config.yaml:45-47`: "Round 1 审查建议值；原 O2（MAP<55>=5min）在网格法下仅 60 事件，不可用作主结局。⚠️ 待 protocol 冻结时由作者最终确认。" against `manuscript_v0.1.md:603-604`: "The analysis protocol was fixed before modelling but was not publicly registered." The manuscript presents D1 as "our operational choice" (`:130-132`) and reports all 14 prevalences transparently (Table 2, verified), which mitigates but does not remove the selection.

【Why it matters】Selecting the endpoint on observed event counts is a recognised optimism channel; with the 14-definition table the paper is more transparent than most, but the "fixed before modelling" sentence is stronger than the record supports, and one contrary sensitivity result would close the gap.

【Specific fix】Soften to: "The outcome definition was chosen before model fitting from a pre-specified candidate set on the basis of clinical interpretability and adequate event count; all 14 candidate definitions and their prevalences are reported (Table 2)." And add one sensitivity row: XGBoost AUPRC/AUROC under, e.g., B2 (≥ 5 readings < 65 within 60 min; prevalence 30.8%) or D1 with the fraction threshold moved to 20%/40%, fitted and evaluated identically.

---

### MINOR 2 — "No material calendar-time drift" overstates what a single 2018 boundary with 291 events can show

【Problem】The temporal split is a single boundary (2018 vs ≤ 2017) with 291 test events, yet the text concludes "indicating no material calendar-time drift", and the temporal split's role as a drift test is itself weakened by cohort-wide feature engineering and outcome selection.

【Evidence】Temporal test: 1,818 cases, 291 events (`results/s3_metrics.json`); XGBoost AUPRC 0.339 with bootstrap CI 0.291–0.395, i.e. ± 0.05 around a point estimate 0.008 below the patient-split value — a drift of that size or larger is entirely compatible with the interval. The year distribution is 2015 (95), 2016 (5,867), 2017 (9,081), 2018 (1,818), so "temporal" is effectively one year against three. The surgical-group keyword map was iterated to a target on the full cohort (`config/config.yaml:88-89`: "由 scripts/audit/a6_procedure_groups.py 迭代至 OTHER=2.48%"), and D1 was chosen with full-cohort event counts, so the 2018 test cases participated in feature/outcome construction.

【Why it matters】"No calendar-time drift" is an absence-of-evidence claim presented as a positive finding; the honest version is "no drift was detectable at this boundary and sample size". This matters because the drift check is one of the two validations the title advertises.

【Specific fix】Replace "indicating no material calendar-time drift" (`:352-353`) with: "Performance on the temporal split was statistically indistinguishable from the patient-level split (AUPRC 0.339, 95% CI 0.291–0.395 vs 0.347, 0.309–0.387); with 291 events in the temporal test set, this comparison can exclude only large drift, and feature and outcome construction used the full cohort, so the temporal split should be read as a robustness check rather than a pure prospective-style validation."

---

### MINOR 3 — Three different predictor counts circulate; the fitted design width is never stated

【Problem】The manuscript says "206 candidate predictors", the feature dictionary reports 207 features, and the fitted model uses 205 numeric columns (335 after missingness indicators) — none of which is reconciled in the text.

【Evidence】`results/s2_feature_dictionary.json` `n_features: 207`; `results/s2_features.csv` has 207 columns = 206 dictionary features + `anchor_source`; `scripts/s3_models.py:71-72` drops two object columns, leaving 205; the logistic design is 205 + 130 indicators = 335 (recomputed). Manuscript: "Two hundred and six candidate predictors were constructed across 13 domains" (`:144-148`) with per-domain counts that do sum to 206.

【Why it matters】Individually trivial; collectively they make the EPV audit trail (MAJOR 1) harder for a reader to reproduce, and "206 predictors" vs "205 fitted" is the kind of small inconsistency that erodes trust in an otherwise exact paper.

【Specific fix】Add one sentence to Methods: "Of the 206 constructed candidate predictors, 205 entered the models (two string columns, anchor source and surgical-group label, were encoded as indicators); the logistic design additionally contained one missingness indicator per column with missing data, for 335 fitted parameters."

---

### MINOR 4 — Subgroup AUPRCs are computed on isotonic-calibrated (piecewise-constant) predictions

【Problem】Subgroup AUPRCs in Table 5 are computed on the isotonic-calibrated probabilities, whose flat regions create ties that perturb precision–recall curves relative to the raw scores.

【Evidence】`scripts/s3_models.py:237` calls `subgroup_auprc(yte.values, p_cal, Xte, split)`. I recomputed the patient-split subgroup AUPRCs on raw scores with the identical model: BMI < 18.5 gives 0.632 (calibrated 0.6156) and age < 50 gives 0.398 (calibrated 0.3801) — differences of 0.01–0.02 created purely by tie-handling in the step-function calibration map.

【Why it matters】The effect is small and does not change any conclusion, but subgroup metrics should be computed on the ranking score (calibration is monotone and cannot change a *strictly* computed AUPRC), and the discrepancy means Table 5 cannot be exactly reproduced from the raw model.

【Specific fix】Compute subgroup AUPRC/AUROC on the uncalibrated test predictions and state this in the Table 5 footnote.

---

### MINOR 5 — Orphan fragment in the Limitations list

【Problem】An unnumbered, mid-sentence fragment follows limitation 10, duplicating content already in the Interpretation section — a broken list that will read as a production error.

【Evidence】`manuscript_v0.1.md:607-612`: "pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg. The model therefore largely extrapolates…" — begins mid-sentence (the sentence's subject is missing), carries no list number or bold lead-in, and repeats `:493-501` and `:607-612` vs `:549-554`.

【Why it matters】A visible text defect in the Limitations of a first submission signals weak proofreading and invites line-by-line scrutiny of the rest.

【Specific fix】Delete lines 607–612, or restore the intended numbered item in full: "11. **Dominance of the pre-anchor pressure level.** The strongest predictor was the pre-anchor mean MAP, and the next strongest were the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg; the model therefore largely extrapolates the patient's current pressure rather than discovering independent risk."

---

### MINOR 6 — "What this study adds" promises four elements and delivers five

【Problem】The section claims "four elements" but the numbered list contains five items.

【Evidence】`manuscript_v0.1.md:616`: "this study contributes four elements" followed by items 1–5 at `:619-643`.

【Why it matters】Trivial to fix, visible to any reader; exactly the kind of stale-count error that survives revisions.

【Specific fix】Change "four elements" to "five elements" (or merge items 1 and 3, which both concern spectrum/leakage accounting).

---

### MINOR 7 — Small wording and disclosure gaps

【Problem】A garbled abstract clause and two undisclosed implementation details.

【Evidence】(a) `manuscript_v0.1.md:27-28`: "1,000 bootstrap confidence intervals were secondary" reads as if the interval count were the quantity; (b) the external model was fitted on **all 16,861** MOVER cases (`scripts/ext_build.py:216`, `mfinal.fit(X, y)`), while Table 7's internal comparator rows come from models trained on 80% (`scripts/ext_core_benchmark.py:82`) — the manuscript never states the external model's training set; (c) the four sex-unknown cases are coded `male = 0`, i.e. folded into female, by `scripts/s2_features.py:140` without mention.

【Why it matters】(a) is a desk-edit trigger; (b) matters because the external-vs-internal AUROC comparison (0.751 vs 0.698/0.710) mixes training-set sizes, and the direction (external model trained on more data) makes the comparison mildly conservative — worth one sentence; (c) is negligible but belongs in the footnote of Table 1.

【Specific fix】(a) "…with 95% confidence intervals from 1,000 bootstrap resamples"; (b) add to the external-validation Methods: "The transported model was fitted on the full MOVER cohort (all 16,861 cases) with the 53 core features; the internal comparator in Table 7 was refitted on the training split only, so the comparison is slightly conservative."; (c) add to Table 1 footnote: "The four cases with unrecorded sex were coded as female in the model."

---

## Stands up (verified correct)

1. **Every headline number reproduces from the artefacts.** I re-derived: the cohort waterfall (19,114 = 0 + 8 + 1,632 + 371 + 242 + 16,861, `results/s1_cohort.json`); all 14 Table-2 counts against `results/s1_outcomes_postanchor.json` (D1 2,622/15.55%; O1 15; E2 11,091; …); all eight Table-4 rows with CIs against `results/s3_metrics.json`; calibration (0.191→0.119, slope 0.909, intercept 0.008; temporal 0.194→0.122, 0.934, 0.006) against `results/s3_calib_dca.json`; all nine subgroup rows × 2 splits against `results/s3_subgroups.json`; Table 6 gains against `results/s3_feature_importance.json`; Table 7 and the external row against `results/ext/core_benchmark.json` and `results/ext/external_validation.json`; Table 1 medians and the outcome-positive/negative contrasts against `results/s2_features.csv`. An independent refit of the manuscript's exact XGBoost on the identical split returned AUPRC 0.3473 / AUROC 0.7223 — matching to four decimals.
2. **The isotonic calibration protocol is correctly implemented with no fold leakage.** `scripts/s3_models.py:205-211` obtains 5-fold out-of-fold predictions via `cross_val_predict` on the training split only, fits the isotonic map on those OOF pairs, and applies it unchanged to the test set; the test labels never enter calibration. The modest OOF-to-full-model scale mismatch (calibrator fitted on 4/5-data models, applied to a full-data model) is handled acceptably — calibrated Brier 0.119 vs no-information 0.131.
3. **The core leakage claim (no post-anchor features) is true.** All seven time-stamped domains show `max_used_time_minus_anchor = 0.0` with zero unparseable timestamps in `results/s2_data_quality.json`; the `BANNED` guards in `scripts/s2_features.py:474-477` and `scripts/s3_models.py:73-74` hard-fail if `post_window_minutes`, `post_nmap_measurements`, `or_min` or `or_end` ever reach the matrix; the label window is genuinely post-anchor (`scripts/s1_cohort.py:185`), so the full-window label leakage the pipeline's own notes warn about has been eliminated. (The remaining gap is the boundary case, MAJOR 2.)
4. **The DCA narrative is accurate.** Recomputed from `results/s3_calib_dca.json`: model net benefit at 0.10 = 0.079/0.085 and at 0.15 = 0.050/0.058 (patient/temporal); patient-split benefit positive through 0.58; temporal positive 0.01–0.45 and again 0.66–0.73; treat-all ≈ 0.06 at 0.10 and −2.13/−2.11 at 0.73 — all consistent with `:379-390` (the temporal "positive up to 0.46" is one 0.01-step off; the artefact shows 0.45).
5. **The temporal split has no calendar gap and the counts are exact.** All cases fall in 2015–2018 (95 / 5,867 / 9,081 / 1,818; the data end 2018-10-03 per `config/config.yaml:79-82`), so 15,043 + 1,818 = 16,861 with no orphan years — a failure mode I specifically checked for.
6. **The anthropometric cleaning is implemented exactly as reported.** 37 implausible heights, 18 weights, 6 BMI values set to missing (not imputed), BMI computable for 16,699 (99.0%) — verified against both `scripts/s2_features.py:144-178` and `results/s2_data_quality.json`, with hard assertions guarding the ranges.
7. **The external application is genuinely unrefitted and unrecalibrated, and the frozen predictors are disclosed in code.** `results/ext/mover_core_model.joblib` is trained on MOVER core features only and applied directly to `vitaldb_features.csv`; `anchor_is_intubation = 0`, `or_year = 0` and the re-derived `anchor_minus_or_start = opstart/60` are explicit in `scripts/ext_build.py:146-148` and disclosed in the manuscript (`:196-200`). Package versions in the manuscript (Python 3.13, pandas 2.3.3, scikit-learn 1.9.0, XGBoost 3.4.1, LightGBM 4.7.0) all match the environment; `scripts/s5_gate.py` runs clean (PASS on all checks, including the DCA cross-check against s3).
8. **The negative-by-construction count is exact and internally consistent.** 1,496 = 1,332 cases with 1–9 post-anchor measurements + 164 with none; conditional prevalence 2,622/15,365 = 17.1%; no case with < 10 measurements is ever labelled positive (verified: 0 such cases).

---

## Questions for the authors

1. How were the four models' hyperparameters chosen — pre-specified from prior work, or any tuning on this cohort? Was the full logistic's implicit L2 penalty (scikit-learn default C = 1.0) a deliberate choice given EPV ≈ 6?
2. Was the D1 definition (threshold 65, ≥ 10 measurements, ≥ 30%) fixed before any event counts were computed, or selected after seeing the 14 candidate prevalences? The config comment ("Round 1 审查建议值… 原 O2 … 仅 60 事件") suggests the latter; please clarify the timeline relative to protocol freezing.
3. What is the evidence for "fewer than 1% of cases had any MAP recording in the 30 minutes before OR start" (`:582-583`)? The pipeline filters vitals to `[OR_start, OR_end]`, so this claim rests on raw-table inspection not shown in any artefact.
4. Was the shared anchor minute (feature window `[anchor−15, anchor]` closed, label window `[anchor, OR_end]` closed) a deliberate convention? 4,787 cases have a MAP reading at exactly the anchor, 648 of them < 65 mmHg.
5. Please confirm that the transported model was fitted on all 16,861 MOVER cases while Table 7's internal rows come from 80%-trained models, and state this in the text.
6. Should the imputation medians/indicators have been fitted within the training split only? If re-running, the logistic rows will change slightly.
7. Is `vitals_window_n_records` intended to count all vital-sign records (MOVER) or arterial MAP records only (VitalDB)? As implemented, the feature means different things in the two cohorts.
8. Is there any plan for per-stratum bootstrap CIs or multiplicity handling for Table 5, and can stratum prevalence be reported alongside AUPRC?

---

## What I actually checked

**Files read in full:** `manuscript/manuscript_v0.1.md`; `scripts/s1_cohort.py`, `s2_features.py`, `s3_models.py`, `ext_pipeline.py`, `ext_core_benchmark.py`, `ext_build.py`; `config/config.yaml`, `config/config_vitaldb.yaml`; artefacts `results/s1_cohort.json`, `s1_outcomes_postanchor.json`, `s1_data_quality.json`, `s1_labels_postanchor.csv`, `s1_anchor.csv`, `s2_feature_dictionary.json`, `s2_data_quality.json`, `s2_features.csv`, `s3_metrics.json`, `s3_calib_dca.json`, `s3_subgroups.json`, `s3_feature_importance.json`, `s4_audit_trail.csv`, `ext/external_validation.json`, `ext/core_benchmark.json`, `ext/vitaldb_features_qa.json`, `ext/vitaldb_features.csv`, `ext/vitaldb_predictions.csv`, `ext/mover_core_model.joblib` (loaded, gains extracted); raw `data_raw/_sis_emr_x/EMR/patient_vitals.csv` (anchor-minute join).

**Commands run (Python: `C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe`, pandas 2.3.3 / sklearn 1.9.0 / xgboost 3.4.1 / lightgbm 4.7.0):** recomputation of D1 counts, negative-by-construction (incl. the 164 zero-measurement cases), anchor timing quartiles, feature-matrix width and missingness-indicator count, EPV, year distribution, anchor-minute boundary overlap from raw vitals, DCA positive-benefit intervals and treat-all values from the artefact arrays, core-model gain decomposition, MOVER-vs-VitalDB feature distribution comparison, external calibration by decile, an independent XGBoost refit reproducing AUPRC 0.3473 / AUROC 0.7223, and `scripts/s5_gate.py` (Overall: PASS).

**Recomputed vs manuscript — matches:** cohort waterfall; all 14 Table-2 counts; all 8 Table-4 rows and CIs; calibration values both splits; DCA net benefits at 0.10/0.15, positivity ranges (0.58 patient; 0.01–0.45 and 0.66–0.73 temporal), treat-all ≈ 0.06 @ 0.10 and ≈ −2.1 @ 0.73; all 18 subgroup values; Table 6 top-10 gains; Table 7 internal/external rows and CIs; 214/3,735 = 5.73%, 214/3,521 = 6.1%; lifts 2.23×, 2.8×, 2.1×; no-information Brier 0.131; Table 1 medians/IQRs and sex counts; recording-density statistics (19.89% MAP, 637,188 segments, 96.2% single-minute, median 33, p5–p95 12–90); anthropometric cleaning counts; leakage-audit zeros; package versions; s5_gate PASS.

**Recomputed vs manuscript — discrepancies found:** (i) temporal DCA "positive up to 0.46" vs artefact 0.45 (one step; covered by "approximately"); (ii) predictor counts 206 (text) vs 207 (dictionary) vs 205 (fitted) vs 335 (logistic design); (iii) the DCA-threshold prose ("positive up to approximately 0.58/0.46", "0.66–0.74", "≈−2.1 at 0.73") and several derived quantities (2.23×, 17.1%, "four elements") are not rows in `results/s4_audit_trail.csv` (154 rows), so the claim that *every* number is traceable through the audit trail is stronger than the trail supports; (iv) `scripts/s2_features.py` docstring says "分析队列 17,103 行" while the matrix has 16,861 rows (stale comment, no numerical consequence); (v) the manuscript does not disclose that the external model was trained on all 16,861 cases.

**Could not verify from artefacts:** the "< 1% of cases with any MAP recording in the 30 minutes before OR start" claim (raw pre-OR-start vitals not inspected by the pipeline's quality reports); hyperparameter selection provenance; the TRIPOD+AI checklist content itself (`results/s4_tripod_ai.md` — another reviewer's lane).

---

## Verdict

**Major revisions.**

The pipeline is reproducible and the reported numbers are honest to four decimals; nothing here requires re-analysis of the headline from scratch. But four must-fix items stand between this draft and a positive decision: (1) an explicit EPV/shrinkage and effective-df accounting (EPV ≈ 6.3 for the logistic design; MAJOR 1); (2) a leakage audit that covers the label boundary, or an honest disclosure of the shared anchor minute (MAJOR 2); (3) the ≥ 10-measurement sensitivity analysis that tests whether the negative-by-construction rule inflates the headline (MAJOR 4); and (4) re-framing the VitalDB analysis as a transportability assessment in the title, abstract, TRIPOD type and contribution list, with the feature-space shift quantified (MAJOR 5–6).

**The single change that would most improve the paper:** re-frame the VitalDB application as what the paper's own Limitations already say it is — a transportability check, not an external validation — in the title, abstract, TRIPOD type and "what this study adds", and support that re-framing with a quantified feature-space-shift table for the 53 transported features (density features with 0% external training support carrying 10.8% of gain; the frozen second-ranked predictor; the 15→41-minute shift in the re-derived timing feature). That one change converts the paper's largest internal contradiction into its most distinctive methodological contribution. The runner-up, and the analysis I would most want added: the pre-specified sensitivity analysis restricted to the 15,365 evaluable cases.
