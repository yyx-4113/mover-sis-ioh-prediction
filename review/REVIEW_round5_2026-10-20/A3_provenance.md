# A3 — Statistics / Reproducibility / Provenance Review (Round 5)

**Target manuscript:** `manuscript/manuscript_v0.1.md` (BMC Anesthesiology, TRIPOD type 2b)
**Reviewer focus:** A3 — bootstrap CI integrity, AUPRC-vs-AUROC comparability, calibration, DCA wording, number-to-artifact provenance.
**Artifacts verified:** `results/s3_metrics.json`, `results/s3_calib_dca.json`, `results/ext/external_validation.json`, `results/ext/core_benchmark.json`, `results/ext/mover_core_train_metrics.json`, `results/s3_subgroups.json`, `results/s3_feature_importance.json`, `results/s1_cohort.json`, `results/s4_audit_trail.csv`.

---

## Executive summary

The manuscript's quantitative core is **reproducible and internally consistent**. Every headline metric I checked (bootstrap CIs, calibration Brier/slope/intercept, DCA net benefit at 0.10/0.15, external validation, Table 5/6/7, cohort counts) traces exactly to a `results/` artifact, and the audit trail (`s4_audit_trail.csv`, 155 rows mapping each number to its source file and reproduce command) is in place — the provenance mechanism works. **No sign of the previously-known bootstrap index-mismatch (features-vs-labels) bug**: all reported 95% CIs are symmetric about their point estimates and contain the point estimate.

The one substantive residual risk is a **factual mis-description of the decision-curve analysis (DCA) for the temporal split** — the manuscript claims the temporal model net benefit "remains positive up to 0.73" with only a "transient negative dip between 0.59 and 0.66," but the underlying `s3_calib_dca.json` curve shows the temporal net benefit is *below* treat-none across a wide band (0.46–0.65) and is only transiently positive in a narrow 0.66–0.73 recovery. This error is repeated in the Discussion and overstates where the temporal model is usable. It is fixable by a text edit and requires no re-analysis.

A secondary, lower-severity tension: the manuscript correctly asserts AUPRC is not comparable across prevalences, yet highlights a "2.8× vs 2.1×" external-vs-internal *lift* comparison that is itself prevalence-driven and partially undercuts that careful stance.

**Verdict: Minor revisions.** No data integrity problem; all numbers trace; the single MAJOR finding is a figure-description correction.

---

## Findings table

| Severity | Location | Issue | Concrete fix | Verification source |
|---|---|---|---|---|
| MAJOR | Lines 377–381 (Results) and 480 (Discussion) | DCA temporal threshold range mis-described. Text: net benefit "remain[s] positive up to a threshold of 0.73 on the temporal split, with a transient negative dip … between roughly 0.59 and 0.66." Data show temporal `net_benefit_model` is **negative from 0.46 to 0.65** (a wide band below treat-none = 0) and only **transiently positive from 0.66 to 0.73**. The patient-split claim (positive up to 0.58) is correct. Discussion line 480 repeats "positive net benefit … up to 0.58 (patient-level) and 0.73 (temporal)," which is false across 0.46–0.65 for temporal. | Rewrite temporal description: "On the temporal split, net benefit was positive only below ~0.45 and in a narrow band 0.66–0.73, falling below the treat-none strategy across 0.46–0.65; the model therefore offers no net benefit over that clinically relevant mid-range." Update line 480 to "up to 0.58 (patient) and only in a narrow 0.66–0.73 band (temporal)." | `results/s3_calib_dca.json` → `temporal.dca.net_benefit_model`: last positive threshold = 0.73, but first non-positive at 0.46; values negative 0.46→0.65, positive 0.66→0.73, negative after 0.74. |
| MINOR | Lines 377–379 | Treat-all net benefit described as "strongly negative at these prevalences." At the decision-relevant thresholds the text actually cares about (0.10–0.15), `net_benefit_treat_all` is **+0.062 (0.10)** and **+0.007 (0.15)** — positive, not strongly negative. Treat-all only turns strongly negative above ~0.17. | Change to "becomes strongly negative at thresholds above ~0.17." | `s3_calib_dca.json` → `patient.dca.net_benefit_treat_all`: 0.10→0.0618, 0.15→0.0066, 0.16→−0.0052. |
| MINOR | Lines 449–451 (and the comparability framing at 451–452, 567–569) | The manuscript correctly states AUPRC is not comparable across prevalences, but then highlights "external AUPRC … exceeded the external prevalence by a factor of 2.8, a larger relative lift than the 2.1-fold internal value." Lift ratios also scale with prevalence (a fixed AP yields different lift at different prevalence), so this "larger lift" is largely a prevalence artifact and softens the careful comparability claim of lines 567–569. | Either drop the 2.8×-vs-2.1× lift sentence, or append an explicit caveat: "lift ratios are themselves prevalence-dependent and should not be read as superior PR-space performance." | `ext/external_validation.json` (auprc 0.16, prevalence 0.0573 → 2.79×); `ext/core_benchmark.json` patient (auprc 0.3206 / 0.1555 → 2.06× ≈ "2.1-fold"). |
| MINOR | Lines 30–31, 344–345, 359–364, 462–464 | External AUPRC CI width (0.2021−0.1291 = 0.073) is *slightly narrower* than the internal width (0.3875−0.3089 = 0.079) despite ~2.5× fewer events (214 vs 525). Plausible (larger total N = 3,735; AUPRC variance at low AP/prevalence behaves differently) but warrants a one-line methods confirmation. **No sign of the index-mismatch bug** — all CIs are symmetric about the point estimate and contain it (internal XGB AUPRC CI centre 0.348 vs 0.347; AUROC centre 0.721 vs 0.722; external AUPRC centre 0.166 vs 0.160; AUROC centre 0.749 vs 0.751). | Add to Methods (line ~199) a sentence confirming the 1,000 bootstrap resamples were drawn on the full external cohort (n = 3,735), with the same engine as the internal splits, and (optionally) that resampling was not event-only. | `s3_metrics.json` (xgboost patient/temporal CIs), `ext/external_validation.json` (auprc_ci95, auroc_ci95). |
| (Strength — no action) | Lines 451–452, 567–569, 568 | AUPRC-vs-AUROC comparability is otherwise stated consistently: no direct 0.347-vs-0.160 comparison; external AUROC framed as the transportability signal; "external AUPRC cannot be compared directly with the internal value" is explicit. | None. | Manuscript text vs `ext/external_validation.json`, `ext/core_benchmark.json`. |
| (Strength — no action) | Lines 370–375, 452–453 | Calibration honestly presented. Internal OOF isotonic: Brier 0.1905→0.1190, slope 0.9092, intercept 0.0083; temporal 0.1935→0.1217, slope 0.9338, intercept 0.0058. External (uncalibrated) Brier 0.179 with mean predicted 0.365 vs observed 0.057 — a real, disclosed calibration gap consistent with the "ranking not probability" claim. | None. | `s3_calib_dca.json` (patient/temporal brier_raw, brier_calibrated, calib_slope, calib_intercept); `ext/external_validation.json` (brier 0.1789, pred_mean 0.365, prevalence 0.0573). |
| (Strength — no action) | Tables 1–7, Abstract | All 34 key numbers I spot-checked trace to artifacts: Table 4 Brier/AUPRC/AUROC match `s3_metrics.json`; Table 5 subgroup AUPRCs match `s3_subgroups.json`; Table 6 gains match `s3_feature_importance.json` (e.g., map_mean 175.49→175.5); Table 7 internal 53-feature values match `core_benchmark.json` (auprc 0.3206→0.321, auroc 0.6979→0.698, brier 0.1984→0.198); cohort counts match `s1_cohort.json`; DCA @0.10/@0.15 match `s3_calib_dca.json` and the gate check. | None. | `s4_audit_trail.csv` (155 rows, metric→source_file→reproduce command). |

---

## Detailed verification notes

### 1. Bootstrap CI integrity — clean (no index-mismatch bug)
- **Internal XGBoost (patient, n_test = 3,373, events = 525):** AUPRC 0.3473 → ms 0.347; CI [0.3089, 0.3875] → ms 0.309–0.387; AUROC 0.7223 → ms 0.722; CI [0.6969, 0.7453] → ms 0.697–0.745; Brier 0.1905 → ms 0.191. (Source: `s3_metrics.json`.)
- **External (VitalDB, n = 3,735, events = 214):** AUPRC 0.160 → ms 0.160; CI [0.1291, 0.2021] → ms 0.129–0.202; AUROC 0.7507 → ms 0.751; CI [0.7133, 0.7844] → ms 0.713–0.784; Brier 0.1789 → ms 0.179; pred_mean 0.365 → ms 0.37. (Source: `ext/external_validation.json`.)
- **Symmetry / containment check:** every CI is symmetric about its point estimate and contains it → no evidence of the features-vs-labels index-mismatch defect. The only residual question (CI width vs event count) is noted as MINOR above and is plausibly explained by total-N and low-AP variance behaviour.

### 2. AUPRC-vs-AUROC comparability — mostly consistent, one soft contradiction
- Correct, explicit statements at lines 451–452 ("lower absolute AUPRC reflects the much lower external prevalence … rather than a loss of ranking ability") and 567–569 ("external AUPRC cannot be compared directly with the internal value; the external AUROC … indicates that ranking transferred").
- No direct 0.347-vs-0.160 comparison is drawn. The only tension is the "2.8× vs 2.1× lift" sentence (lines 449–450), which is itself prevalence-driven and partially undercuts the comparability stance — flagged MINOR.

### 3. Calibration — honestly presented
- Internal recalibration Brier 0.1905→0.1190, slope 0.9092, intercept 0.0083 (patient) and 0.1935→0.1217, slope 0.9338, intercept 0.0058 (temporal) — exact matches to `s3_calib_dca.json`.
- External Brier 0.179 (uncalibrated) with predicted 0.365 vs observed 0.057 is disclosed and consistent with "ranking transfers, probabilities do not" — no overclaim.

### 4. DCA net-benefit wording — MAJOR mis-statement for temporal split
- Verified values: patient `net_benefit_model` @0.10 = 0.07866 → ms 0.079; @0.15 = 0.05035 → ms 0.050 (correct). Temporal @0.10 = 0.08477 → ms 0.085; @0.15 = 0.05789 → ms 0.058 (correct).
- **Error:** the manuscript's upper-bound claim for the *temporal* split is wrong. The temporal curve is positive 0.01–0.45, **negative 0.46–0.65** (below treat-none), positive again 0.66–0.73, then negative. The text's "positive up to 0.73" and "transient dip 0.59–0.66" both mis-read this: the dip is far larger (0.46–0.65) and the 0.66–0.73 segment is the *transient* positive one. This overstates the temporal model's usable decision range and is repeated in the Discussion (line 480). The clinically emphasized 0.10–0.30 region is positive for both splits, so the central conclusion is not harmed, but the specific threshold-range statement must be corrected. (Source: `s3_calib_dca.json`.)

### 5. Provenance — no gaps found among checked numbers
- The audit trail (`s4_audit_trail.csv`, 155 rows) maps each reported quantity to a producing artifact and a reproduce command, satisfying the manuscript's provenance claim (lines 224–227). All key metrics, subgroup AUPRCs, predictor gains, Table 7 internal 53-feature values, cohort counts, and DCA anchor points I examined trace exactly. No number was found that lacks an artifact source.

---

## Verdict

**Minor revisions.**

Rationale: (a) reproducibility and provenance are sound — all checked numbers trace to `results/` artifacts and the audit trail is complete; (b) no evidence of the bootstrap index-mismatch bug; (c) calibration and the AUPRC-comparability message are honestly and consistently handled; (d) the single MAJOR finding (DCA temporal threshold-range mis-description) is a **text-accuracy error, not an analytic flaw**, and is corrected by editing the Results (lines 377–381) and Discussion (line 480) paragraphs — no re-running of analyses is required. The MINOR items (treat-all wording, lift-comparison framing, bootstrap-resampling one-liner) are likewise editorial. No grounds for Major revisions or Reject.
