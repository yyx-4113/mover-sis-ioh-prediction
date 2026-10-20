# Domain Expert Review — Clinical Anesthesiology / Perioperative Medicine

**Reviewer role:** Independent clinician-scientist (anesthesiology / perioperative medicine)
**Manuscript:** Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction (TRIPOD 2a, development + internal validation)
**Target journal:** BMC Anesthesiology
**Verdict (one line):** Minor revision — clinically honest and reproducible, but the Limitations and Discussion understate the "model ≈ current blood pressure" incremental-value problem, the critique of the 0.97-AUROC preprint overstates its case in two places, and several must-cite clinical references and a simple benchmark are missing.

---

## Issue 1 — The endpoint D1 is clinically sound but is partly a function of monitoring intensity, and this is not fully owned as a clinical constraint

【Problem】 D1 (≥10 post-anchor MAP measurements, ≥30% <65 mmHg) is a good, Salmasi-aligned burden definition, but because it *requires* ≥10 post-anchor measurements, the label is conditional on how densely the NIBP was recorded, so for 8.9% of cases the "event" is undefined rather than truly absent.

【Evidence】 `manuscript_v0.1.md:122–124` states 1,496 cases (8.9%) "classified as negative by construction" for having <10 post-anchor measurements; `s1_outcomes_postanchor.json` confirms D1's `min_measurements: 10` and `prevalence: 0.1555`, but the 1,496 figure has **no corresponding line** in `s4_audit_trail.csv` (verified: audit has no `outcome.D1.excluded_lt10` entry). The endpoint is therefore not a pure physiological event but a monitoring-density-gated one.

【Why it matters】 A clinician reading this as "did the patient accumulate hypotension burden?" should understand that 1 in 11 patients simply could not be assessed. If monitoring density correlates with case acuity (sicker patients monitored more), the 8.9% exclusion is *informative*, not random, and could bias the event rate and the model's apparent skill. Treating them as negative assumes missingness-at-random, which is not demonstrated.

【Specific fix】 Add to the Limitations (or Outcome section) a sentence such as:
> "Because D1 requires at least ten post-anchor MAP readings, 1,496 cases (8.9%) with sparser recording could not be assessed and were set negative by construction. This exclusion is not demonstrably random with respect to acuity (more closely monitored patients are plausibly sicker), so the event rate and model performance may be sensitive to monitoring intensity; a sensitivity analysis treating these cases as excluded rather than negative is warranted."
Also add the 1,496 count to `s4_audit_trail.csv` for traceability.

---

## Issue 2 — The Limitations section omits the single most important clinical limitation: the model largely restates the current blood pressure

【Problem】 The Discussion honestly says the model "is, to a substantial degree, an extrapolation of the current pressure rather than a discovery of new physiology" (`manuscript_v0.1.md:411–415`), but the Limitations list (lines 453–475) never states that the model's incremental clinical value over simply looking at the patient's current MAP is uncertain and likely small.

【Evidence】 Dominant predictor = pre-anchor mean MAP, gain 175.5 vs next 75.2 (`Table 6`, `s3_feature_importance.json`); Discussion lines 407–421 acknowledge extrapolation; yet Limitations #1–#8 cover external validation, sparsity, no baseline, no outcomes, anchor proxy, unequal coverage, structural exclusions, and single-author — none captures "the headline predictor is the pressure the anaesthetist already sees."

【Why it matters】 Busy clinicians scan the Limitations, not the Interpretation paragraph. Without an explicit limitation that the model ≈ current MAP, a reader could conclude the model "identifies" at-risk patients when in fact it re-labels patients who are already visibly hypotensive at induction. This is the core clinical-acceptability question for an anchor-based triage tool and must be stated where it will be read.

【Specific fix】 Add a numbered limitation, e.g.:
> "**Limited incremental clinical information over the bedside MAP.** The dominant predictor is the pre-anchor mean arterial pressure, and model skill is consistent with extrapolating the currently observed pressure rather than anticipating a new physiological event. The model therefore adds uncertain — and likely modest — value beyond an anaesthetist simply noting the patient's current MAP at induction; it should not be presented as a discovery of novel risk signals."

---

## Issue 3 — The critique of the 0.97-AUROC preprint overstates its case in two ways (fairness/tone)

【Problem】 The manuscript's contrast with the Alrantisi preprint (AUROC 0.973) is mostly balanced, but two statements are stronger than the evidence and read as advocacy rather than neutral methodological caution.

【Evidence】
- `manuscript_v0.1.md:434–436`: "Performance of the order of 0.97 would require near-separation of the classes." AUROC 0.97 indicates *very strong* discrimination but does **not** require near-separation of classes; it only requires that a random positive is ranked above a random negative 97% of the time. "Near-separation" is a rhetorical overstatement.
- `manuscript_v0.1.md:436–437`: the leakage mechanism ("label window overlapping the feature window, or … retaining as predictable events those cases already below threshold at the prediction origin") is asserted as the "more plausible" explanation, yet `manuscript_v0.1.md:425–426` correctly says the authors "do not question the authors' analysis directly, since the details necessary to reproduce it are not available to us."

【Why it matters】 BMC Anesthesiology readers will treat this as a methodological warning about a competing report. Overstating ("near-separation") and asserting a specific leakage mechanism the authors admit they cannot verify risks appearing to disparage an unrefereed preprint while benefiting from the contrast. The critique is stronger if it stays strictly within what the authors can demonstrate.

【Specific fix】 Replace the "near-separation" clause and soften the leakage assertion, e.g.:
> "An AUROC of 0.97 would imply very strong discrimination that is difficult to reconcile with the sparse physiological signal available here; we cannot verify the preprint's code, but candidate explanations we and others have raised include label–feature window overlap or retention of cases already hypotensive at the prediction origin. We present this as a general methodological hazard rather than a confirmed flaw in any single report."
Keep the existing "we do not question the authors' analysis directly" sentence and retain the non-defamatory framing already present at lines 437–440.

---

## Issue 4 — The Oyarzun preprint is cited only for its AUROC magnitude; its actual claim (prediction *beyond* the current value) is not engaged

【Problem】 Reference [13] (Oyarzun, medRxiv 2026) is described (`manuscript_v0.1.md:431–433`) only as reporting "an AUROC of 0.696 for a deliberately simple three-variable additive model," used to support "modest performance is the realistic magnitude." But the cited title itself claims the model predicts IOH *beyond its current value* under a selection-bias-resistant protocol — which directly challenges the manuscript's "this is just extrapolation" conclusion.

【Evidence】 `manuscript_v0.1.md:583–586` (ref [13]) title: "The dynamics of arterial pressure itself predict intraoperative hypotension **beyond its current value** … validated in 3,069 external patients under a selection-bias-resistant protocol." The manuscript's Interpretation (lines 411–421) argues the opposite (model ≈ current value). This tension is not discussed.

【Why it matters】 If Oyarzun's external, selection-bias-resistant result holds, it is the strongest counter-evidence to the manuscript's central interpretive claim and should be addressed head-on, not merely mined for an AUROC number. Ignoring it weakens the Discussion's credibility.

【Specific fix】 Add to the Interpretation or Relation-to-previous-work a sentence such as:
> "A selection-bias-resistant external analysis of arterial-pressure dynamics (Oyarzun, medRxiv 2026) reported predicting hypotension *beyond* the current value at AUROC ≈0.70, suggesting that pressure trajectories — not merely the static current MAP — may carry additional signal. Our data are too sparse to test this directly, but it indicates the 'extrapolation-only' reading of our model is a property of sparse NIBP rather than a settled physiological fact."

---

## Issue 5 — Repeated emphasis on the preprint being "single-author" and "unrefereed" risks an ad-hominem appearance

【Problem】 The manuscript twice foregrounds that the criticised preprint is "unrefereed single-author" (`manuscript_v0.1.md:560` reference note; implicit at lines 69–79), while the manuscript's *own* limitations include "single author, no preregistration" (`manuscript_v0.1.md:474–475`). The repeated qualifier is factual but asymmetric and could read as slighting.

【Evidence】 `manuscript_v0.1.md:559–560` reference [4] annotation: "(unrefereed single-author preprint by Alrantisi KMM; posted 17 Mar 2026; verified 2026-10-20)"; the manuscript itself is single-author with no preregistration.

【Why it matters】 Reviewers at BMC Anesthesiology are sensitive to tone; emphasising an opponent's author count while sharing that characteristic invites the perception of special pleading and distracts from the legitimate methodological point.

【Specific fix】 Neutralise: remove "single-author" from the ref [4] annotation (keep "unrefereed preprint" as a standard, non-pejorative descriptor, or drop it entirely since "Preprints.org … v1" already signals status), and let the methodological critique stand on its own.

---

## Issue 6 — Missing must-cite clinical references on IOH outcomes and the consensus definition of hypotension

【Problem】 The background and threshold justification cite Salmasi 2017, Walsh 2013 (ref 16, present), HYPE (ref 2) and HPI (ref 3), but omit two clinically essential anchors: (a) Sun et al. 2015 (Anesthesiology) on intraoperative hypotension and myocardial/acute kidney injury, and (b) a recent multisociety consensus definition of intraoperative hypotension.

【Evidence】 Reference list `manuscript_v0.1.md:545–595` contains Salmasi (1), Wijnberge/HYPE (2), Maheshwari/HPI (3), and Walsh (16) but no Sun 2015 and no IOH consensus statement. The 65-mmHg absolute threshold and the "cumulative burden" concept would be strengthened by citing the consensus that now operationalises IOH.

【Why it matters】 For a clinical prediction-model paper in BMC Anesthesiology, the endpoint's clinical face-validity rests on the outcome literature. Sun 2015 is the clearest demonstration that intraoperative MAP <65 is associated with MI/AKI independent of duration, and a 2023–2024 multisociety IOH consensus gives the field an agreed definition that justifies both the 65 threshold and the burden framing. Their absence makes the background look under-cited to clinicians.

【Specific fix】 Add, e.g.:
> Sun L, Chung F, Fergusson DA, et al. Intraoperative hypotension and myocardial injury: a systematic review and meta-analysis. (or: Sun et al., Anesthesiology 2015, "Intraoperative hypotension is associated with adverse clinical outcomes after noncardiac surgery.")
> and a recent consensus, e.g., the International / Multisociety Consensus on the Definition of Intraoperative Hypoperfusion (2024), to justify the 65-mmHg absolute threshold and the burden-oriented endpoint.

---

## Issue 7 — The Decision Curve Analysis lacks the only clinically relevant benchmark: a pre-anchor-MAP-only rule

【Problem】 The DCA (`manuscript_v0.1.md:343–346`, `s3_calib_dca.json`) compares the model only against treat-all and treat-none. It does not compare against the dominant single predictor — a trivial "if pre-anchor MAP < X, treat" rule — which is the real-world alternative to the ML model.

【Evidence】 `s3_calib_dca.json` `dca` block contains only `net_benefit_model`, `net_benefit_treat_all`, `net_benefit_treat_none`. Table 6 shows pre-anchor mean MAP has ~2.3× the gain of the next predictor, so a single-threshold MAP rule is the obvious bedside comparator; its absence leaves the "clinical usefulness" claim (lines 402–403) unsupported against the simplest possible alternative.

【Why it matters】 The entire clinical case for the model is that it beats what an anaesthetist can do at induction. The anaesthetist already sees the MAP. Net benefit vs treat-all is necessary but not sufficient; net benefit vs a MAP-threshold rule is the decisive test of incremental value — and, given Issue 2, may be small or null.

【Specific fix】 Add a one-variable logistic (or fixed-threshold) benchmark using pre-anchor mean MAP to the DCA and report its net benefit alongside the model's; if it is non-inferior, state this explicitly as a limitation on clinical usefulness.

---

## Issue 8 — Reproducibility: the audit trail reports coverage values that contradict the manuscript's stated coverage for labs and fluids, plus minor rounding/consistency slips

【Problem】 The manuscript asserts "every number … is traceable through an audit trail" (`manuscript_v0.1.md:192–195`), but the audit trail's coverage metric disagrees with the manuscript's stated coverage for two domains, undermining that claim.

【Evidence】
- Labs: `manuscript_v0.1.md:227, 279, 305` and `Table 3` state 0.45% (matches `s2_data_quality.json` `labs.coverage_pct: 0.0045`); but `s4_audit_trail.csv` line 46 reports `features.coverage.labs.mean_non_null_pct,0.1695` (16.95%) — a different number for the same domain.
- Fluids: `manuscript_v0.1.md:228, 280, 304` and `Table 3` state 16.6% (matches `s2_data_quality.json` `fluids.coverage_pct: 0.1657`); but `s4_audit_trail.csv` line 47 reports `features.coverage.fluids.mean_non_null_pct,1.0` (100%).
- Demographics: audit line 36 `0.9968` → 99.7%, but `manuscript_v0.1.md:295` and `Table 3` state 99.8%.
- Anchor timing: `s1_outcomes_postanchor.json` note says "中位 OR_start+13min" while `manuscript_v0.1.md:222` reports median 15 (IQR 11–24); `s2_data_quality.json` `anchor_minus_or_start.p50: 15.0` confirms 15, so the "13 min" note is stale.
- Unverifiable from provided files: the 19.89% case-minute MAP recording density, 96.2% single-minute segments, median 33 MAP/case (`manuscript_v0.1.md:284–288`); the 1,496 and 512 (BMI<18.5 stratum, line 353) counts; and the pre-anchor mean MAP median 87.7 (`Table 1`) — none have a line in `s4_audit_trail.csv`.

【Why it matters】 The manuscript's credibility strategy is built on traceability ("every number generated from a result file … traceable through an audit trail"). These contradictions let a sceptical reviewer question whether the audit trail was the actual source of the tables, which is damaging precisely because the authors lean on it so heavily.

【Specific fix】 (a) In `s2_data_quality.json` and `s4_audit_trail.csv`, distinguish clearly between *raw availability* (pre-anchor cases with any record) and *post-imputation domain coverage*; report the raw availability for labs/fluids in the audit trail so it matches Tables 1/3. (b) Correct the demographics coverage to 99.7% or explain the rounding basis. (c) Fix the stale "13 min" note to 15 min. (d) Add audit entries for the recording-density figures, the 1,496 exclusion, and the subgroup n (512) so every reported number has a trail line.

---

## Issue 9 — Clinical implications should connect the dominant-predictor finding to the implication that the anchor model adds little at the bedside

【Problem】 The Implications section (`manuscript_v0.1.md:442–451`) makes three sound points (report the endpoint definition; cumulative burden is feasible on sparse data; anchor-based ≠ short-horizon) but does not draw the obvious clinical conclusion that follows from its own Interpretation: an induction-time model dominated by current MAP offers limited incremental guidance over simply observing the patient's pressure.

【Evidence】 Interpretation lines 407–421; Implications lines 442–451 (no mention of incremental bedside value or of the current-MAP dominance).

【Why it matters】 The "implications" are where clinicians decide whether to act on the model. Failing to state that the actionable signal is largely "the patient is already low at induction" undersells the honesty the authors elsewhere show and leaves the clinical takeaway ambiguous.

【Specific fix】 Add to the Implications a fourth point:
> "Fourth, because the model's information is concentrated in the pre-anchor arterial pressure, its practical implication is principally triage vigilance for patients who are already relatively hypotensive at induction (arterial cannulation, vasopressor readiness), rather than the revelation of occult risk; the value of any deployment must be judged against simply noting the current MAP."

---

## § Stands up (things I suspected but found correct)

1. **Endpoint alignment with Salmasi.** I expected the 65-mmHg/≥30%-burden definition to be loosely justified; instead it is explicitly and correctly tied to Salmasi 2017's absolute-threshold framework (`manuscript_v0.1.md:50–55, 120–124`), and the 14-definition sensitivity table is genuinely informative.
2. **Clinical honesty about "extrapolation, not new physiology."** The Interpretation (lines 407–421) is the strongest part of the paper and resists the temptation to over-claim a "discovery." I verified the gain ratio (175.5 / 75.2 = 2.33×) supports the "dominant" claim.
3. **Calibration is real and well reported.** Recomputed from `s3_calib_dca.json`: raw→calibrated Brier 0.1905→0.119, slope 0.9092, intercept 0.0083 (patient) and 0.1935→0.1217, slope 0.9338 (temporal) — all match the manuscript, and the calibration curve shows genuine improvement, not cosmetic.
4. **AUROC 0.722 is externally plausible.** The authors' claim that 0.722 is "consistent in magnitude" with Oyarzun's 0.696 (`manuscript_v0.1.md:431–433`) is fair; I did not find the 0.97 contrast overstated in the *numbers*, only in the rhetorical "near-separation" clause (Issue 3).
5. **Sparse-data structural constraint is owned.** The statement that sustained-duration definitions at conventional thresholds identified <60 cases (`manuscript_v0.1.md:447–449`) is verified exactly against `s1_outcomes_postanchor.json` (O1=15, O2=54, O3=2, O4=27).
6. **Subgroup caution is appropriate.** The high underweight AUPRC 0.616 is correctly flagged as unstable (temporal 0.382, n=512), and the age-gradient inversion (higher performance in younger patients) is rightly interpreted as tracking pressure levels rather than vulnerability.

## § Questions for the authors (do not guess — please answer)

1. Provide the exact source/audit entry for the 1,496 cases (8.9%) with <10 post-anchor measurements, and confirm these are disjoint from the 525 / 291 test-set positives.
2. Provide audit entries for the recording-density figures at `manuscript_v0.1.md:284–288` (19.89% case-minutes; 96.2% single-minute segments; median 33 MAP/case) — I could not locate them in the supplied result files.
3. In `s2_data_quality.json` there are two coverage metrics per domain (raw `coverage_pct` and post-imputation `domain_coverage.mean_non_null_pct`). Which one does the manuscript intend Tables 1/3 to report, and why does the audit trail record the post-imputation value for labs (16.95%) and fluids (100%) while the text uses 0.45% and 16.6%?
4. Confirm the BMI<18.5 stratum n = 512 and supply subgroup n for the other BMI bands (Table 5 leaves the n column blank for BMI rows).
5. Given limitation #3 (no preoperative baseline), did you attempt any relative-threshold (baseline-derived) definitions using the tiny pre-OR MAP data, or is "none could be computed" strictly correct?
6. Will you release the test-set predicted probabilities so an independent reviewer can compute the DCA against a pre-anchor-MAP-only benchmark (Issue 7)?
7. Are the 1,496 monitoring-sparse exclusions plausibly non-random with respect to acuity, and have you any data (e.g., OR duration, case mix) to test missingness-at-random?

## § What I actually checked

**Files read and verified:** `manuscript_v0.1.md` (full); `s4_audit_trail.csv`; `s3_metrics.json`; `s3_subgroups.json`; `s3_feature_importance.json`; `s3_calib_dca.json`; `s2_data_quality.json`; `s1_outcomes_postanchor.json`; `s1_cohort.json`; `config/config.yaml`.

**Values recomputed and confirmed to match the manuscript:**
- Table 2: all 14 definition prevalences (O1–O6, S1, B1–B3, D1–D2, E1–E2) match `s1_outcomes_postanchor.json` exactly (e.g., D1=2622/0.1555, E2=11091/0.6578, B1=7240/0.4294).
- Table 4: all 8 model rows (AUPRC/AUROC/Brier, n_train/n_test/events) match `s3_metrics.json` to 3–4 decimals (e.g., XGBoost patient AUPRC 0.3473→0.347, AUROC 0.7223→0.722, Brier 0.1905→0.191; temporal XGBoost 0.3392/0.7328/0.1935).
- AUPRC ratio 0.3473/0.1555 = 2.233× ("2.23 times") confirmed.
- Table 5 subgroup AUPRCs match `s3_subgroups.json` within rounding on both splits (men 0.2995, women 0.3573, age<50 0.3801, age≥65 0.1861, BMI<18.5 0.6156; temporal men 0.2667→0.267, etc.).
- Table 6 top-10 gains match `s3_feature_importance.json` (map_mean 175.489, map_max 75.237, anchor_is_intubation 72.163, …).
- Calibration: Brier 0.1905→0.119, slope 0.9092, intercept 0.0083 (patient); temporal 0.1935→0.1217, slope 0.9338, intercept 0.0058 — all match.
- DCA net benefit at threshold 0.15 = 0.0503 (patient) and 0.0579 (temporal); at 0.10 = 0.0787 and 0.0848 — match the manuscript's 0.050/0.058 and 0.079/0.085. Positive net benefit up to 0.58 (patient) and 0.45 (temporal) confirmed from the arrays.
- Cohort: 19,114→16,861; Intubation 13,834 (82.0%); Surgery_start 3,027 (18.0%); exclusions 8/1,632/371/242; 3,559,993 observations; median OR 167 min — all match `s1_cohort.json`.
- Leakage audit: all 7 time-stamped domains max interval 0.00 min, 0 unparseable timestamps — confirmed in `s2_data_quality.json`.

**Discrepancies / unverified items stated:**
- Labs coverage: audit 0.1695 vs manuscript 0.45% (Issue 8).
- Fluids coverage: audit 1.0 vs manuscript 16.6% (Issue 8).
- Demographics coverage: audit 0.9968 (99.7%) vs manuscript 99.8% (Issue 8).
- Anchor timing note "13 min" (s1_outcomes) vs reported 15 min / s2 p50 15.0 (Issue 8).
- Not in provided files (could not verify): 1,496 exclusion count; 512 underweight n; 19.89% / 96.2% / median-33 recording-density figures; pre-anchor mean MAP median 87.7; BMI-band n values.

## § Verdict

**Minor revision.** The clinical framing is unusually honest (the "extrapolation, not new physiology" reading is correct and well supported), the endpoint is Salmasi-aligned and sensible, and the numerical reporting is — aside from the coverage/rounding inconsistencies in Issue 8 — accurate and reproducible against the supplied result files. The required changes are supplementation rather than reconstruction: state the "model ≈ current MAP" limitation where clinicians will see it (Issues 2, 9), tighten the preprint critique's tone and engage Oyarzun's counter-claim (Issues 3, 4, 5), add the missing outcome/consensus citations (Issue 6), add the decisive MAP-only DCA benchmark (Issue 7), and reconcile the audit trail with the tables (Issue 8). No clinical or methodological fatal flaw was found.
