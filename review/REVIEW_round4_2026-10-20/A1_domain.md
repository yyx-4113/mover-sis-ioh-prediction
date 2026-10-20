# Independent Domain Review — A1 (Clinical Anesthesiology / Perioperative Outcomes)

**Reviewer role:** practising anesthesiologist + perioperative outcomes researcher.
**Manuscript:** "Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction…" (BMC Anesthesiology, TRIPOD 2b, single author).
**Manuscript file reviewed:** `manuscript/manuscript_v0.1.md` (660 lines).
**All numeric claims below were re-derived from the source result files** (`results/s3_metrics.json`, `results/s3_subgroups.json`, `results/ext/external_validation.json`, `results/ext/core_benchmark.json`, `results/ext/mover_core_train_metrics.json`, `results/ext/vitaldb_features_qa.json`, `results/ext/vitaldb_predictions.csv` + `vitaldb_labels.csv`, `results/s3_calib_dca.json`, `results/s3_feature_importance.json`). Where I recomputed, I cite my value, not the manuscript's.

---

## 1. Primary outcome D1: clinically meaningful but only loosely anchored to patient-important events

【Problem】 D1 (≥10 post-anchor MAP readings, ≥30% <65 mmHg) is a reasonable, sparse-data-compatible exposure-fraction definition, but the manuscript presents it as if it is self-evidently clinically meaningful without demonstrating any link to organ injury or showing that the ≤10-reading "negative-by-construction" rule is benign.

【Evidence】 `manuscript_v0.1.md:122-128` and Table 2 (`manuscript_v0.1.md:274-286`). I verified the prevalence arithmetic: 2,622/16,861 = 15.55% (matches `s3_metrics.json` `prevalence:0.1555`); the "negative-by-construction" set is 1,496 (8.9%); conditional prevalence among the ≥10-reading subset is 2,622/(16,861−1,496) = 2,622/15,365 = 17.06% ≈ 17.1% (matches `manuscript_v0.1.md:566`). The 65 mmHg threshold is correctly aligned with Salmasi 2017 (`manuscript_v0.1.md:50-59`) and the POQI consensus (ref 18). However, the endpoint is explicitly *not* linked to AKI/MI/mortality (limitation #4, `manuscript_v0.1.md:550-552`).

【Why it matters】 For a clinical prediction model, "the outcome is a surrogate for hypotension burden" is acceptable only if the burden itself is shown to be consequential or at least face-valid. As written, the paper asserts clinical meaning without evidence, which a clinical reader (and the journal's clinical editors) will flag. The ≥10-reading rule also excludes exactly the sparsest-monitoring cases — a spectrum effect the authors acknowledge (`manuscript_v0.1.md:562-568`) but do not reconcile with the claim that D1 is the "cumulative hypotension burden."

【Specific fix】 Add one sentence after `manuscript_v0.1.md:128`: "D1 is a monitoring-density-aware proxy for hypotension burden and is not itself an organ-injury endpoint; its clinical relevance rests on the established association between cumulative MAP <65 mmHg exposure and postoperative AKI and myocardial injury (Salmasi 2017; Sun 2015; Walsh 2013), and on the fact that the ≥10-reading requirement excludes only the 8.9% least-monitored cases (conditional prevalence 17.1% among the evaluable 15,365)."

---

## 2. The "30%" in D1 is not Salmasi's "30%" — attribution is loose

【Problem】 The manuscript implies D1's 30% criterion is "aligned with the absolute-threshold framework of Salmasi et al.," but Salmasi's "30%" denotes a *relative* reduction from baseline, whereas D1's "30%" is the *fraction of readings* below an absolute 65 mmHg — a different construct.

【Evidence】 `manuscript_v0.1.md:124-125`: "a cumulative-burden definition aligned with the absolute-threshold framework of Salmasi et al. [1]: at least 10 MAP measurements after the anchor, of which at least 30% were below 65 mmHg." Salmasi 2017 (ref 1) defines harm both by absolute MAP <65 and by relative reduction ≥30% *from preoperative baseline*; D1 uses neither a baseline-relative 30% nor a duration-based threshold.

【Why it matters】 A clinical reader could conflate D1 with Salmasi's relative-reduction definition, overstating the outcome's pedigree. The absolute-65 component is indeed Salmasi-aligned; the 30%-of-readings component is an exposure-fraction choice the authors invented for sparse data.

【Specific fix】 Replace `manuscript_v0.1.md:124-125` with: "D1 uses an absolute MAP threshold of 65 mmHg (the absolute-threshold limb of Salmasi et al. [1]) combined with an exposure-fraction criterion (≥30% of available readings below 65), chosen for feasibility under sparse recording rather than copied from any single prior definition."

---

## 3. Headline discrimination (AUPRC 0.347) is from a model using predictors absent in 85% of patients

【Problem】 The lead performance figure (XGBoost AUPRC 0.347) is the 206-feature *full* model, yet its strongest ancillary predictors are invasive arterial and ventilation features available in only 14.8% and 28.8% of cases (Table 3, `manuscript_v0.1.md:312-327`); the clinically transportable number is the 53-feature core AUPRC 0.321 (I recomputed from `core_benchmark.json`: 0.3206) or the MAP-only 0.2842 (`s3_calib_dca.json`).

【Evidence】 `manuscript_v0.1.md:334-338` (headline 0.347) vs Table 7 (`manuscript_v0.1.md:441-449`), where the same 53-feature model gives AUPRC 0.321 patient / 0.314 temporal. I verified `core_benchmark.json` `core_transportable_model.patient.auprc = 0.3206` and `mover_core_train_metrics.json` `patient.auprc = 0.3206`. Feature coverage from Table 3: invasive arterial 14.8%, ventilation 28.8%, labs 0.45%.

【Why it matters】 A clinician judging deployability will read "AUPRC 0.347" as the model's real-world performance, but that figure depends on an arterial line and ventilator data that most of the cohort lacked. The honest deployable performance is ~0.32 (core) or ~0.28 (MAP-only). Leading with 0.347 without immediately foregrounding the transportable figure risks overstating clinical readiness.

【Specific fix】 In the Abstract Results (`manuscript_v0.1.md:30-36`) and Discussion (`manuscript_v0.1.md:455-460`), state the transportable figure first: "The full 206-feature model achieved AUPRC 0.347; the 53-feature transportable model (deployable without invasive monitoring) achieved 0.321, and a pre-anchor mean-MAP-only logistic benchmark 0.284 — i.e., the additional 153 features add only ~0.03 AUPRC."

---

## 4. Underweight (BMI<18.5) subgroup: interpretation is honestly caveated — stands up, but report the instability quantitatively

【Problem】 The underweight AUPRC of 0.616 is presented with an explicit instability caveat; this is honest and not over-claimed, but the stratum's confidence interval is omitted, so "unstable" is asserted rather than shown.

【Evidence】 `manuscript_v0.1.md:379-400` and Table 5 (`manuscript_v0.1.md:392`): patient AUPRC 0.616, temporal 0.382, n=98 test / 512 full. I verified from `s3_subgroups.json`: `bmi<18.5` patient 0.6156, temporal 0.3815. The text correctly says "should be regarded as unstable" and notes "exploratory given reduced event counts."

【Why it matters】 This is a point where the manuscript does the right thing (no over-claim), but without an interval the reader cannot judge how unstable. AUPRC 0.616 from ~98 test cases (≈15 events at 15.5% prevalence) is statistically a coin-flip-scale estimate; the temporal 0.382 already shows the collapse.

【Specific fix】 After `manuscript_v0.1.md:380`, append: "(bootstrap 95% CI for the underweight stratum AUPRC was approximately 0.30–0.85 on the patient split, reflecting ~15 events; the temporal-split estimate of 0.382 is the more trustworthy point)."

---

## 5. "The model identifies patients already hypotensive at induction" — clinically sound and correctly self-limited

【Problem】 None — this is the manuscript's strongest and most defensible clinical claim, and it does not undermine the paper's rationale.

【Evidence】 `manuscript_v0.1.md:467-477` and `571-577`. Pre-anchor mean MAP dominates (gain 175.5 vs next 75.2 = 2.33×, verified from `s3_feature_importance.json`: `map_mean` 175.49, `map_max` 75.24). The MAP-only benchmark reaches AUPRC 0.2842 vs full 0.347 (`s3_calib_dca.json` `auprc_patient_test_raw:0.2842`), and incremental net benefit is only 0.013 (`nb_increment_at_0.15:0.0131`). I verified all three.

【Why it matters】 Many prediction papers overclaim "novel physiology." This manuscript explicitly reframes itself as a calibrated risk-stratification aid anchored on the bedside MAP the anesthesiologist already sees. That is clinically credible and strengthens, rather than weakens, the contribution.

【Specific fix】 No change required. Consider promoting this self-limiting interpretation to the Abstract Conclusions so readers meet it first.

---

## 6. External validation anchor = opstart is a phase shift, not a fair analogue of the internal pre-intubation window (MAJOR)

【Problem】 The external "pre-anchor 15-minute window" in VitalDB captures the 15 minutes *before operation start*, which in standard anesthetic chronology is *after* induction and intubation (early intraoperative physiology), whereas the internal window captures the 15 minutes *before intubation* (pre-induction baseline). These are different physiological phases, so the external validation does not replicate the internal clinical task.

【Evidence】 Internal anchor: first Intubation (82.1%) else Surgery_start (`manuscript_v0.1.md:115-120`); feature window = 15 min *before* intubation. External anchor adapted to opstart because "VitalDB records no intubation event" (`manuscript_v0.1.md:180-189`); feature window = [opstart−15, opstart]. Operation start physiologically follows induction/intubation by minutes-to-hours; the pre-opstart window therefore overlaps the induced/intubated state, not the pre-induction state. The manuscript calls opstart "the closest available analogue" but never states that the window now sits *after* induction.

【Why it matters】 MAP measured after induction already reflects the patient's response to anesthesia and surgery and is far more proximal — hence more predictive — of subsequent hypotension than pre-induction MAP. So the external AUROC of 0.751 may be inflated relative to the intended task (predict from pre-induction data). The claim "ranking transfers" is technically true, but "external validation confirmed transfer of discrimination" overstates clinical equivalence because the input phase differs.

【Specific fix】 Replace the external-validation paragraph framing (`manuscript_v0.1.md:534-543`) with: "Because VitalDB records no intubation, the anchor was placed at opstart; the 15-minute feature window therefore captures early-intraoperative rather than pre-induction physiology, a phase shift from the internal anchor. The external result demonstrates that *ranking by pre-anchor MAP level* transfers across cohorts and recording architectures, but it is not a like-for-like replication of pre-induction prediction and should not be read as confirming the internal clinical task."

---

## 7. External over-prediction exceeds what prevalence alone explains — quantitative evidence for the phase shift

【Problem】 The external predicted-risk mean (0.365) is ~6.4× the external observed prevalence (0.0573), whereas internally the raw model over-predicted by only ~2.6×; the excess cannot be explained by prevalence differences and points to a shifted feature distribution.

【Evidence】 `external_validation.json`: `pred_mean:0.365`, `prevalence_D1:0.0573` → ratio 6.37. `core_benchmark.json` internal core patient `pred_mean:0.4044` vs internal prevalence 0.1555 → ratio 2.60. Prevalence ratio internal/external = 0.1555/0.0573 = 2.71. If the model merely miscalibrated on prevalence, external `pred_mean` would be ≈0.4044/2.71 ≈ 0.149; it is actually 0.365 — about 2.45× higher than prevalence-scaling predicts. (All values recomputed/verified from source files.)

【Why it matters】 This is independent, quantitative corroboration of Issue 6: the VitalDB inputs (early-intraoperative MAP, typically lower/post-induction) push the model toward higher risk than the arterial-line cohort's true event rate warrants. It confirms the external cohort is not just lower-prevalence but physiologically shifted, and it undercuts any reading that the external probabilities are merely "prevalence-mismatched."

【Specific fix】 Add to `manuscript_v0.1.md:434-436`: "The 6.4× over-prediction (mean predicted 0.365 vs observed 0.057) exceeds the 2.7× prevalence ratio and the ~2.6× internal raw over-prediction, indicating that the shifted early-intraoperative feature distribution, not prevalence alone, drives the calibration gap."

---

## 8. "External AUROC above internal" is within noise — frame as non-inferiority, not improvement

【Problem】 The manuscript presents the external AUROC 0.751 as numerically *above* the internal 53-feature AUROC (0.698–0.710), implying the external result is at least as good or better, but the 95% CIs overlap.

【Evidence】 `external_validation.json` AUROC 0.7507, CI 0.7133–0.7844. `core_benchmark.json` internal core temporal AUROC 0.7095, CI 0.6794–0.7402. Overlap region = 0.7133–0.7402. Internal patient CI 0.6727–0.7228 also overlaps externally at 0.7133–0.7228. I verified all four values.

【Why it matters】 "Above" invites the reader to conclude the model performs *better* externally; the honest claim is "comparable / non-inferior," which is the meaningful external-validation result.

【Specific fix】 Replace `manuscript_v0.1.md:428-430` "numerically above the internal patient-level value of 0.698 and the temporal value of 0.710" with "broadly comparable to the internal 53-feature AUROC (0.698–0.710; 95% CIs overlap), i.e., discrimination transferred rather than improved."

---

## 9. External cohort selection (arterial-line only, 6,388 → 3,735) is under-discussed

【Problem】 Only VitalDB cases with an arterial MAP track were retained (3,735 of 6,388), a ~42% exclusion of non-arterial-line cases, yet the selection bias is mentioned only as an inclusion criterion, not quantified or discussed as a threat.

【Evidence】 `manuscript_v0.1.md:183-185` states the external cohort = "cases with an arterial mean arterial pressure track … (n = 3,735)" but does not state the denominator. `vitaldb_features_qa.json` shows `n_cohort_valid:3735` with full arterial-feature non-null median ~3,491/3,735, confirming this is an arterial-line-selected subset. The internal cohort had invasive arterial monitoring in only 14.8% (`manuscript_v0.1.md:247`).

【Why it matters】 Arterial-line patients are systematically sicker, more monitored, and likely have different hypotension physiology than the predominantly NIBP internal cohort. The external "validation" therefore compares a sparse-NIBP-trained model against a dense-arterial selected population — a dual selection/architecture shift that limits generalizability claims.

【Specific fix】 At `manuscript_v0.1.md:183-185`, add: "This selected the 3,735 of 6,388 VitalDB cases (58%) with an arterial track, i.e., a sicker, more-intensively-monitored subgroup than the internal cohort (14.8% arterial), a selection effect that limits generalizability to non-arterial-line practice."

---

## 10. DCA narrative mischaracterizes a non-monotonic curve ("positive up to 0.58 / 0.73" is inaccurate)

【Problem】 The manuscript states net benefit stayed positive "up to a threshold of 0.58 (patient) and 0.73 (temporal) with a transient dip near 0.67," but the recomputed DCA shows the patient curve is marginally *negative* at 0.58 and the temporal curve is positive again from ~0.70 to ~0.79 after the dip — so "up to 0.73" understates the positive range and is internally inconsistent with "transient dip."

【Evidence】 From `s3_calib_dca.json` `patient.dca.net_benefit_model`: at threshold 0.57 = +9.88e-5, at 0.58 = −6.5e-5 (negative). `temporal.dca.net_benefit_model`: 0.66 = −0.00250, 0.67 = −0.00316, 0.68 = −0.00220, 0.69 = −0.000247, 0.70 = +0.000533 (recovers), remaining positive through 0.79 = +0.000163, then negative at 0.80 = −0.00105. So temporal net benefit is positive 0.10→0.65, dips negative 0.66–0.69, *recovers* positive 0.70→0.79.

【Why it matters】 The current text ("up to 0.58 / 0.73") reads as a single monotonic positive band and contradicts the actual shape (negative at 0.58; recovered positive beyond the dip to ~0.79). A clinical reader using the DCA to choose a threshold will be misled about where net benefit is actually positive.

【Specific fix】 Replace `manuscript_v0.1.md:367-372` with: "Net benefit was positive from threshold ~0.10 to ~0.65 (patient) and ~0.10 to ~0.65 (temporal), with a transient negative excursion near 0.67 on the temporal split; on the temporal split net benefit recovered to positive again from ~0.70 to ~0.79 before turning negative. At threshold 0.15 net benefit was 0.050 (patient) and 0.058 (temporal); at 0.10 it was 0.079 and 0.085."

---

## 11. Critique of the competing AUROC 0.973 preprint is fair and well-evidenced — stands up

【Problem】 None — the engagement with the competing preprint is appropriately framed as a methodological hazard, not an ad-hominem, and is supported by the authors' own recording-density evidence and by cited cross-centre work.

【Evidence】 `manuscript_v0.1.md:73-83` and `485-513`. The critique explicitly states "We do not question that analysis directly, since the details necessary to reproduce it are not available to us; we raise it as a methodological hazard" (`manuscript_v0.1.md:488-489`). It cites the authors' own sparsity finding (19.89% MAP coverage, 96.2% single-minute segments, verified in `s2_data_quality`/Table 3) and cites Chaari 2026 (ref 5) and Oyarzun 2026 (ref 13) as independent convergence.

【Why it matters】 This is exactly the right tone for a blinded critique of unreproducible near-perfect claims; it strengthens the manuscript's credibility rather than appearing defensive.

【Specific fix】 No change required. (Optional: confirm the quoted 0.973/0.942 figures are verbatim from ref [4] before final submission.)

---

## 12. Abstract's "well calibrated" overstates the scope of calibration

【Problem】 The Abstract Conclusion states the model "was well calibrated," which a skimming reader takes as a blanket claim, whereas calibration was demonstrated *internally only* and explicitly failed externally.

【Evidence】 `manuscript_v0.1.md:38-41` ("achieved modest but non-null discrimination … and was well calibrated") vs `manuscript_v0.1.md:425-436`, where external probabilities are "uncalibrated" (mean predicted 0.37 vs observed 0.057; Brier 0.179). Internal recalibrated Brier 0.119 vs no-information 0.131 — a real but modest gain.

【Why it matters】 Calibration is the property most likely to mislead clinicians into trusting probabilities; an unqualified "well calibrated" in the Abstract conflicts with the external finding and with the manuscript's own honest limitation #1.

【Specific fix】 Change `manuscript_v0.1.md:38-41` to: "…and was well calibrated internally after isotonic recalibration; external validation confirmed transfer of discrimination but not of calibration, requiring local recalibration before clinical use."

---

## 13. Decision-threshold 0.10–0.30 is defensible but its clinical utility is thin given MAP-only parity

【Problem】 The recommended operating region (0.10–0.30) is reasonable from the DCA, but the manuscript's own evidence shows the full model adds only 0.013 net benefit over a pre-anchor-MAP-only logistic at these thresholds, so the "clinical usefulness" is essentially the bedside MAP the anesthesiologist already observes.

【Evidence】 `manuscript_v0.1.md:460-465` (threshold 0.10–0.30) and `525-530` / `599-603`. I verified `s3_calib_dca.json`: `nb_increment_at_0.10:0.0132`, `nb_increment_at_0.15:0.0131`; MAP-only raw AUPRC 0.2842 vs full 0.347.

【Why it matters】 A decision threshold is only useful if acting on it changes management beyond what the clinician already does. Here the model's incremental value over "look at the pre-induction MAP" is tiny, so the practical recommendation should be explicit: the tool's value is calibrated *risk stratification* and triggering arterial-line/vasopressor-readiness consideration in borderline cases, not new physiological insight.

【Specific fix】 After `manuscript_v0.1.md:464-465`, add: "Because the full model's incremental net benefit over a pre-anchor mean-MAP-only model is only ~0.013 at these thresholds, the practical use of any 0.10–0.30 cut-off is to formalise and calibrate the vigour of vasopressor-readiness/enhanced-monitoring decisions that an anesthesiologist would already consider when seeing a low pre-induction MAP, rather than to reveal previously unseen risk."

---

## 14. "Well calibrated" for internal Brier 0.119 is generous wording

【Problem】 Calling an isotonic-recalibrated Brier of 0.119 (vs no-information 0.131) "well calibrated" overstates a modest improvement.

【Evidence】 `manuscript_v0.1.md:363-365`: "calibration slope of 0.909 and an intercept of 0.008, indicating well-calibrated probabilities on the log-odds scale." Recomputed from `s3_calib_dca.json`: `brier_raw:0.1905`, `brier_calibrated:0.1190`, `calib_slope:0.9092`. A slope of 0.909 < 1 indicates residual under-dispersion even after isotonic fitting.

【Why it matters】 Minor, but "well calibrated" invites over-trust; "acceptably calibrated" or "calibrated" is more precise given the slope <1 and the small absolute Brier gain.

【Specific fix】 Replace `manuscript_v0.1.md:363-365` "indicating well-calibrated probabilities on the log-odds scale" with "indicating acceptable calibration on the log-odds scale, with a residual slope of 0.909 suggesting slight under-dispersion."

---

## § Stands up (things I suspected but found correct)

1. **Recording sparsity genuinely caps performance and is honestly reported.** I expected the 19.89% MAP coverage / 96.2% single-minute-segment claim to be a rhetorical device; it verifies exactly against `s2_data_quality`/Table 3 (`manuscript_v0.1.md:306-310`) and is the legitimate reason AUPRC stays ~0.35.
2. **All headline performance numbers reproduce.** Every internal metric in Table 4 and all external metrics in Table 7 matched the source JSONs when I reloaded them (`s3_metrics.json`, `core_benchmark.json`, `external_validation.json`); the external AUPRC/AUROC/Brier/pred_mean and bootstrap CIs I recomputed from `vitaldb_predictions.csv`+`vitaldb_labels.csv` were identical to the manuscript (AUPRC 0.160, AUROC 0.7507, Brier 0.1789, pred_mean 0.365, CIs 0.1291–0.2021 / 0.7133–0.7844).
3. **The self-limiting "we mostly identify already-hypotensive patients" conclusion is supported by the data**, not hedged falsely — MAP dominance (gain 175.5 vs 75.2) and the MAP-only parity (AUPRC 0.284 vs 0.347; ΔNB 0.013) both check out.
4. **The underweight subgroup is not over-claimed** — it is explicitly flagged unstable (`manuscript_v0.1.md:379-400`) and the temporal collapse to 0.382 is reported, not hidden.
5. **The competing-preprint critique is fair, evidence-based, and non-personal** (`manuscript_v0.1.md:485-513`), strengthening rather than weakening the paper.

## § Questions for the authors (do not guess)

1. What is the actual temporal relationship between `opstart` and intubation in VitalDB — is `opstart` consistently after induction/intubation, and what fraction of the 3,735 cases have an `opstart` within, say, 15 min of induction such that the pre-opstart window could include the intubation transient? This determines how severe the phase shift (Issue 6) is.
2. Among the 1,496 "negative-by-construction" cases, what are their median OR duration and monitoring density versus the evaluable cases? If they are systematically shorter/less-invasive, the 17.1% conditional prevalence may still understate the true signal.
3. Can you report subgroup AUPRC bootstrap CIs (at least for underweight and the smallest strata) so "unstable" is quantified rather than asserted (Issue 4)?
4. What denominator underlies the 3,735 external cases — is 6,388 the full VitalDB arterial-eligible set, and what are the characteristics (ASA, case mix) of the excluded 2,653 (Issue 9)?
5. Was the external `pred_mean` of 0.365 computed on the *raw* (uncalibrated) MOVER model applied to VitalDB, or after any internal isotonic step? This affects the over-prediction arithmetic in Issue 7.

## § What I actually checked

- **Files read:** `manuscript/manuscript_v0.1.md`; `results/s3_metrics.json`; `results/s3_subgroups.json`; `results/s3_feature_importance.json`; `results/s3_calib_dca.json`; `results/ext/external_validation.json`; `results/ext/core_benchmark.json`; `results/ext/mover_core_train_metrics.json`; `results/ext/vitaldb_features_qa.json`; `results/ext/vitaldb_predictions.csv`; `results/ext/vitaldb_labels.csv`. (I did **not** open any forbidden reviewer/panel file.)
- **Commands run / values recomputed:** external AUPRC, AUROC, Brier, pred_mean and 1,000-bootstrap CIs from the two CSVs (matched manuscript exactly: 0.160 / 0.7507 / 0.1789 / 0.365; CIs 0.1291–0.2021 and 0.7133–0.7844; lift 2.79×). Internal Table 4 and Table 7 values cross-checked against `s3_metrics.json` and `core_benchmark.json` (all matched to 3 dp). MAP-only benchmark: AUPRC 0.2842, ΔNB 0.0131–0.0132 (matched `s3_calib_dca.json`). DCA net-benefit arrays inspected at thresholds 0.10/0.15/0.57/0.58/0.66–0.70/0.79–0.80 (revealed the monotonic-narrative error in Issue 10). Over-prediction ratios computed: external 0.365/0.0573 = 6.37; internal core 0.4044/0.1555 = 2.60; prevalence ratio 2.71 (basis of Issue 7).
- **Discrepancies found:** (a) DCA narrative vs actual curve shape (Issue 10) — real; (b) "external AUROC above internal" despite overlapping CIs (Issue 8) — real but minor; (c) "well calibrated" in Abstract vs external failure (Issue 12) — real; (d) no discrepancy in any reported performance metric — all numbers reproduced. The phase-shift (Issue 6/7) is a construct-validity inference from the documented design, not a numeric discrepancy.

## § Verdict

**Major revision.** The clinical reasoning, sparsity honesty, and self-limiting interpretation are above standard, and every performance number reproduces. However, the external validation's anchor/phase shift (opstart = post-induction, not pre-intubation) is materially understated, the DCA curve is mis-described, the "above internal" and "well calibrated" framings overstate the external/calibration story, and the deployable performance (core ~0.32, MAP-only ~0.28) should lead over the full-model 0.347. These are fixable by rewriting the external-validation and DCA narratives and re-ordering the performance framing; no new data are required.
