# Reviewer A3 — Provenance / Recomputation audit (REVIEW round 4, 2026-10-20)

**Manuscript:** `manuscript/manuscript_v0.1.md` (v0.1, ~660 lines)
**Role:** Independent implementation/provenance auditor. Every numeric claim I could recompute against a source artefact was recomputed by me from the raw files; numbers below are ones I verified myself.
**Tooling:** Python (analysis environment) used to recompute external AUPRC/AUROC/Brier and to re-derive coverage/threshold quantities from `results/s2_features.csv`. Source files read: `results/ext/external_validation.json`, `results/ext/core_benchmark.json`, `results/ext/mover_core_train_metrics.json`, `results/ext/vitaldb_predictions.csv`, `results/ext/vitaldb_labels.csv`, `results/s3_metrics.json`, `results/s3_subgroups.json`, `results/s3_calib_dca.json`, `results/s1_cohort.json`, `results/s2_data_quality.json`, `results/s4_audit_trail.csv`, `results/s3_feature_importance.json`, `scripts/ext_build.py`, `scripts/s2_features.py`, `manuscript/manuscript_v0.1.md`.

---

## 1. External validation (priority 1) — RECOMPUTED FROM RAW CSVs

I loaded `vitaldb_predictions.csv` (columns `caseid, y, p`) and `vitaldb_labels.csv` (columns `caseid, D1, …`), merged on `caseid`, and recomputed the metrics with scikit-learn directly.

| Quantity | Manuscript / `external_validation.json` | My recomputation from raw CSVs | Match |
|---|---|---|---|
| n | 3,735 | 3,735 rows | ✓ |
| events (D1+) | 214 | 214 | ✓ |
| prevalence | 5.73% (0.0573) | 0.0573 | ✓ |
| AUPRC | 0.160 | 0.1600 | ✓ |
| AUPRC 95% CI | 0.129–0.202 | 0.1291–0.2021 | ✓ |
| AUROC | 0.751 | 0.7507 | ✓ |
| AUROC 95% CI | 0.713–0.784 | 0.7133–0.7844 | ✓ |
| Brier | 0.179 | 0.1789 | ✓ |
| predicted-risk mean | 0.37 (text) / 0.365 (json) | 0.365 | ✓ |

I also confirmed (a) `pred.y` equals `D1` for all 3,735 rows (0 mismatches), so the prediction file's label column is consistent with the label file, and (b) the bootstrap CI reproduces exactly under `np.random.default_rng(12345)` with 1,000 resamples, so the reported CIs are reproducible. **Table 7's VitalDB row is correct in every digit.** The `external_validation.json` claimed values are faithfully reproduced by the raw artefacts.

Internal cross-check on the same table: the external AUROC 0.751 is described as "numerically above the internal patient-level value of 0.698 and the temporal value of 0.710 for the same 53-feature model." From `core_benchmark.json` / `mover_core_train_metrics.json`, patient AUROC = 0.6979 → 0.698, temporal AUROC = 0.7095 → 0.710. ✓. The "2.8-fold lift over external prevalence" (0.160/0.0573 = 2.79) and "2.1-fold internal lift for that model" (0.3206/0.1555 = 2.06) both check out.

---

## 2. MOVER core benchmark (priority 2)

`core_benchmark.json` and `mover_core_train_metrics.json` agree exactly (patient AUPRC 0.3206, temporal 0.3135; patient AUROC 0.6979, temporal 0.7095; Brier 0.1984/0.1987). **Table 7's two internal "MOVER/SIS (development)" rows match these artefacts:**

- Patient: AUPRC 0.321 (0.284–0.362), AUROC 0.698 (0.673–0.723), Brier 0.198. (Artefact 0.3206; CI 0.2843–0.3615 → 0.284–0.362; 0.6979; CI 0.6727–0.7228 → 0.673–0.723; 0.1984.) ✓
- Temporal: AUPRC 0.314 (0.269–0.365), AUROC 0.710 (0.679–0.740), Brier 0.199. (Artefact 0.3135; CI 0.2693–0.3651 → 0.269–0.365; 0.7095; CI 0.6794–0.7402 → 0.679–0.740; 0.1987.) ✓

Note: the panel brief's shorthand "temporal 0.313" is the unrounded artefact value; the manuscript correctly rounds it to 0.314. No error.

---

## 3. "Apply did not refit" (priority 3) — CODE REVIEW

In `scripts/ext_build.py`:
- `stage_train()` (lines 178–223) fits the MOVER core XGBoost on MOVER data (`results/s2_features.csv` × `core_feature_list`, labels `s1_labels_postanchor.csv`) and saves `results/ext/mover_core_model.joblib` (line 218).
- `stage_apply()` (lines 227–269) **loads** that saved model (`joblib.load(…/mover_core_model.joblib)`, line 233) and calls `m.predict_proba(X)` (line 236). There is no `.fit(...)` call on VitalDB anywhere in the apply stage. The only operations are predict → metric computation → bootstrap CI → save predictions.

**The model applied to VitalDB was trained exclusively on MOVER; it is not re-fitted or recalibrated on VitalDB.** This is exactly what the manuscript claims ("applied without refitting", line 427; "no external refitting or recalibration", line 189). The model's training provenance is MOVER-only. Confirmed.

---

## 4. Internal numbers regression check (priority 4)

All 8 model rows in `s3_metrics.json` match `manuscript_v0.1.md` Table 4 (values agree to the printed decimals; full-model AUPRC 0.3473→0.347, AUROC 0.7223→0.722, Brier 0.1905→0.191; LightGBM AUROC 0.7236→0.724; etc.). Calibration (`s3_calib_dca.json`): patient brier_raw 0.1905→0.191, calibrated 0.119, slope 0.9092→0.909, intercept 0.0083→0.008; temporal brier_raw 0.1935→0.194, calibrated 0.1217→0.122, slope 0.9338→0.934, intercept 0.0058→0.006 — all match lines 360–365. DCA net benefit: patient 0.050 at threshold 0.15 and 0.079 at 0.10; temporal 0.058 at 0.15 and 0.085 at 0.10; MAP-only increment 0.013 at both 0.10/0.15; MAP-only raw AUPRC 0.2842→0.284 (line 527) — all match. Subgroups (`s3_subgroups.json`, 18 values) match Table 5 exactly. Feature-importance top-10 gains (`s3_feature_importance.json`) match Table 6 exactly (175.5/75.2/72.2/69.1/64.1/52.9/48.6/45.0/44.7/43.2). Prevalence 15.55% (2,622/16,861), anchors 13,834/3,027 (82.1%/17.9%), conditional 17.1% (2,622/15,365), negative-by-construction 1,496 (8.9%) all match `s1_cohort.json`. Cohort construction (19,114 → 17,103 → 16,861; exclusions 8/1,632/371/242) matches `s1_cohort.json`. **No internal regression found.**

---

## 5. BMI cleaning order (priority 5) — CODE REVIEW

In `scripts/s2_features.py` (lines 141–150): implausible height is set to missing (`feat["height_cm"] = _raw_h.where(...)`, line 147), implausible weight is set to missing (line 148), and **only then** is BMI derived from the already-cleaned height/weight (`_raw_bmi = feat["weight_kg"]/(feat["height_cm"]/100.0)**2`, line 149) and the derived BMI further plausibility-filtered (line 150). The order is correct: implausible values are removed *before* BMI-feature derivation. Three `assert`s (lines 174–176) then enforce the plausibility ranges. The earlier "recorded but didn't clean" bug is **not** present in this version. Confirmed correct.

---

## 6. DCA threshold consistency (priority 6)

From `s3_calib_dca.json` I extracted the net-benefit-positive thresholds per split:
- Patient split: net benefit positive from threshold 0.01 up to **0.58**, then negative from 0.59. **Last positive = 0.58** (manuscript 0.58). ✓
- Temporal split: net benefit negative for 0.10–0.65, positive only in a narrow band **0.66–0.73**, then negative again from 0.74. **Last positive = 0.73** (manuscript 0.73). ✓

The patient-split last-positive threshold is 0.58 (not 0.45), as required. Both thresholds in the manuscript and in the DCA artefact agree.

---

## 7. Cross-location consistency & transfer URL (priority 7–8)

Grep across the manuscript confirms the headline numbers are used consistently in the abstract, Results, Table 4, Table 7, Discussion and Conclusions: full-model 0.347/0.722; core-53 model 0.321/0.698 (patient) and 0.314/0.710 (temporal); external 0.160/0.751/5.73%/3,735/214/0.179. The core-vs-full distinction is maintained everywhere (the manuscript never lets a reader conflate the 0.347 full-model headline with the 0.321 core model that was externally validated — Table 7's footnote at line 448 makes this explicit). No stale or duplicated contradictory numbers were found.

The data-availability statement (line 655) reads `https://github.com/yyx-4113/mover-sis-ioh-prediction (v1.0.0 reproduction package)`. The "(v1.0.0 reproduction package)" label is present, but the URL points to the repository root rather than the specific tagged release `https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.0`. This is a precision issue, not an error (see finding B).

---

## Discrepancies / issues requiring author attention

### Finding A — Demographics coverage rounded to 99.8% instead of 99.7%

【Problem】 Table 3 lists Demographics coverage as 99.8%, but the underlying value is 99.68%, which rounds to 99.7%.
【Evidence】 `manuscript_v0.1.md:317` ("Demographics | 6 | — | 99.8 |"); `results/s2_data_quality.json` `domain_coverage.demographics.mean_non_null_pct = 0.9968`; independently recomputed from `results/s2_features.csv` as 99.68%.
【Why it matters】 It is a 0.1-point rounding/transcription slip in a table that is otherwise exact; a meticulous reviewer or meta-analyst tracing the number will notice the mismatch with the artefact, slightly eroding confidence in the rest of the table.
【Specific fix】 Change "99.8" to "99.7" in Table 3 (line 317).

### Finding B — Release URL points to repo root, not the v1.0.0 tag

【Problem】 The data-availability statement cites the repository root rather than the specific v1.0.0 release tag, weakening reproducibility precision.
【Evidence】 `manuscript_v0.1.md:655` uses `https://github.com/yyx-4113/mover-sis-ioh-prediction (v1.0.0 reproduction package)`; the requested/canonical URL is `…/releases/tag/v1.0.0`. The "(v1.0.0 reproduction package)" label is present, but the hyperlink target is not the tagged release.
【Why it matters】 BMC/TRIPOD reproducibility expectations favour a frozen, version-pinned artefact. A moving `main` branch can diverge from the analysed code, so the tag is the stronger claim.
【Specific fix】 Replace with: `https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.0 (v1.0.0 reproduction package)`.

### Finding C — Temporal DCA framing overstates continuity of net benefit

【Problem】 The text says the calibrated model's net benefit "remains positive up to … 0.73 on the temporal split (with a transient dip near 0.67)," which misdescribes the temporal net-benefit curve.
【Evidence】 `manuscript_v0.1.md:369`; `results/s3_calib_dca.json` temporal `dca.net_benefit_model`. By my recomputation the temporal net benefit is *negative* for thresholds 0.10–0.65, becomes positive only in a narrow band 0.66–0.73, then negative again from 0.74. The numeric thresholds (0.58 patient, 0.73 temporal) are correct, but "remains positive up to 0.73" implies a continuous positive run that does not exist on the temporal split.
【Why it matters】 The headline thresholds are verifiably correct, but the surrounding narrative could mislead a reader about how broadly the model is decision-useful on the temporal split; it is decision-useful only in a narrow band there.
【Specific fix】 Replace with: "On the temporal split the calibrated model's net benefit exceeded both defaults only in a narrow band (≈0.66–0.73), reaching a last-positive threshold of 0.73; on the patient-level split it stayed positive up to 0.58."

### Finding D — External arterial-track selection denominator not disclosed

【Problem】 The external cohort reports only the retained n = 3,735 with an arterial MAP track, but not the denominator of arterial-eligible VitalDB cases that were dropped (brief cites 6,388 screened).
【Evidence】 `manuscript_v0.1.md:183–184` states "n = 3,735" with the arterial track and valid opstart/opend, with no statement of how many cases were excluded for lacking an arterial track. `scripts/ext_build.py` `stage_features` selects `Solar8000/ART_MBP` or `EV1000/ART_MBP` tracks and filters to valid opstart/opend, so a substantial drop is implied but unquantified.
【Why it matters】 Selection bias is a stated limitation theme of the paper; failing to report the arterial-track selection denominator prevents readers from judging the external cohort's representativeness and the magnitude of selection.
【Specific fix】 Add a sentence such as: "Of 6,388 cases with a candidate arterial track, X were excluded for missing/invalid opstart–opend times, leaving 3,735 for analysis," using the figure from `vitaldb_features_qa.json` (`n_cohort_valid` / `n_map_track_missing`).

### Finding E — Audit-trail traceability gap for Table 1 descriptors and MAP coverage

【Problem】 The manuscript claims every reported number is traceable through the audit trail (Additional file 1), but several Table 1 cohort descriptors and the 16,036 NIBP coverage figure are not present in `s4_audit_trail.csv`.
【Evidence】 `manuscript_v0.1.md:214–217` ("Every number reported in this manuscript is generated from a result file by the analysis pipeline and is traceable through an audit trail"). `results/s4_audit_trail.csv` contains no entries for median age 54, median BMI 26.6, height/weight medians, anchor timing, or the MAP-specific pre-anchor coverage of 16,036. I verified 16,036 = `map_mean` non-null in `s2_features.csv` (95.11%) and map_n median 3 (IQR 2–4), but these resolve to `s2_features.csv`, not the declared audit trail.
【Why it matters】 The reproducibility claim is stronger than the artefact supports; an auditor following the manuscript's own instructions cannot resolve these numbers from Additional file 1 alone.
【Specific fix】 Extend `s4_audit_trail.csv` (or a companion sheet) to include the Table 1 descriptive statistics and the MAP-window coverage row, each with its producing script, so the "every number traceable" claim holds.

### Finding F — External "negative-by-construction" analogue not reported

【Problem】 The external pipeline also sets VitalDB cases with <10 post-anchor MAP measurements to D1 = 0 (mirroring the internal negative-by-construction rule), but the manuscript does not report how many external cases this affects or its effect on external prevalence.
【Evidence】 `scripts/ext_build.py:88` (`d1 = int((n_post >= 10) and (frac65 >= 0.30)) if n_post >= 10 else 0`); no corresponding count is reported in the external Results or `vitaldb_features_qa.json` is not surfaced in the text.
【Why it matters】 This is the same spectrum-bias mechanism the authors carefully disclose internally (1,496 internal cases, conditional prevalence 17.1%); omitting its external analogue leaves the external prevalence (5.73%) only partially explained and breaks the symmetry of the internal honesty.
【Specific fix】 Report the external count of cases set negative-by-construction and the corresponding conditional external prevalence, paralleling lines 562–566.

### Finding G — External anchor is phase-shifted (interpretive, not a number error)

【Problem】 The external anchor is `opstart` (operation start, after induction/intubation), whereas the MOVER anchor is the intubation event at induction, so the external "pre-anchor 15-min window" captures a post-intubation, pre-incision phase that is physiologically different from MOVER's pre-intubation window.
【Evidence】 `manuscript_v0.1.md:181–188` and `scripts/ext_build.py:147` (`anchor_minus_or_start = opstart/60`). The authors disclose this as an adaptation (limitations #1, lines 534–543). I confirmed there is **no label–feature window overlap** externally: features are strictly before `opstart` (line 100) and the outcome is over `[opstart, opend]` (line 84), so leakage is not a concern.
【Why it matters】 Because the phase differs, the external result is a confounded/phase-shifted transfer test rather than a like-for-like validation. The honest disclosure is present, but the Discussion could more explicitly state that the external "transfer of discrimination" is demonstrated across a different physiological phase, which limits how strongly one can claim the *same* induction-time signal generalises.
【Specific fix】 Add one sentence in the Discussion (near line 504–507): "Note that the external pre-anchor window is anchored at operation start (post-intubation), i.e. a later physiological phase than MOVER's intubation anchor; the demonstrated transfer is therefore across a phase-shifted feature set and should be read as a conservative generalisation test rather than a like-for-like validation."

---

## § Stands up (claims I verified and found correct)

1. **External validation metrics** recomputed from the raw `vitaldb_predictions.csv`/`vitaldb_labels.csv` reproduce AUPRC 0.160, AUROC 0.7507, Brier 0.1789, prevalence 0.0573, n 3,735, events 214, and the bootstrap CIs exactly. Table 7's VitalDB row is correct to the digit.
2. **Table 7 internal core rows** match `core_benchmark.json` and `mover_core_train_metrics.json` (patient 0.321/0.698/0.198; temporal 0.314/0.710/0.199), and the manuscript correctly rounds 0.3135 → 0.314.
3. **"Apply did not refit"** confirmed in code: `stage_apply` loads `mover_core_model.joblib` (trained on MOVER in `stage_train`) and predicts only; no `.fit` on VitalDB.
4. **All internal performance numbers** in Table 4, calibration (Brier 0.191→0.119, slope 0.909, intercept 0.008; temporal 0.194→0.122, slope 0.934, intercept 0.006), DCA net benefits (0.050/0.079 patient; 0.058/0.085 temporal; MAP-only increment 0.013), and Table 5 subgroups (all 18 values) match `s3_metrics.json`/`s3_calib_dca.json`/`s3_subgroups.json`.
5. **Feature-importance top-10 gains** (175.5 … 43.2) match `s3_feature_importance.json` exactly.
6. **Cohort/anchor/outcome accounting** (16,861; 13,834/3,027 anchors; 2,622/15.55%; conditional 17.1%/15,365; 1,496/8.9%) matches `s1_cohort.json`.
7. **BMI cleaning order** in `s2_features.py` sets implausible height/weight to missing *before* deriving BMI features; the prior "record-but-don't-clean" bug is absent.
8. **DCA last-positive thresholds** are 0.58 (patient) and 0.73 (temporal) in both the artefact and the manuscript — including the required "not 0.45" check for the patient split.
9. **NIBP coverage** 16,036 (95.1%) reconciles exactly with MAP-specific `map_mean` non-null count in `s2_features.csv`; pre-anchor MAP readings median 3 (IQR 2–4) also confirmed.

---

## § Questions for the authors

1. What is the external arterial-track selection denominator (total arterial-eligible VitalDB cases, and how many dropped for invalid opstart/opend)? Please report it for Finding D.
2. How many external VitalDB cases were set D1 = 0 by the <10-post-anchor-measurements rule (the negative-by-construction analogue), and what is the conditional external prevalence? (Finding F)
3. Is `s4_audit_trail.csv` intended to cover Table 1 descriptive statistics and the MAP-window coverage, or is a separate sheet expected? (Finding E)
4. Can the release be pinned to the `v1.0.0` tag URL rather than the repo root? (Finding B)
5. Were the external predictions/curves generated with `scripts/ext_build.py apply` exactly as shipped, or were any manual edits applied to `vitaldb_predictions.csv` after generation? (I confirmed internal consistency, but a provenance confirmation is useful.)

---

## § What I actually checked

**Files read:** `manuscript/manuscript_v0.1.md`; `results/ext/external_validation.json`, `core_benchmark.json`, `mover_core_train_metrics.json`, `vitaldb_predictions.csv`, `vitaldb_labels.csv`; `results/s3_metrics.json`, `s3_subgroups.json`, `s3_calib_dca.json`, `s3_feature_importance.json`; `results/s1_cohort.json`, `s2_data_quality.json`, `s4_audit_trail.csv`; `scripts/ext_build.py`, `scripts/s2_features.py`.

**Commands run (recomputations):**
- Merged predictions↔labels; recomputed AUPRC/AUROC/Brier and 1,000-sample bootstrap CIs with `np.random.default_rng(12345)`. Results: AUPRC 0.1600, AUROC 0.7507, Brier 0.1789, prev 0.0573, n 3,735, pos 214, CI 0.1291–0.2021 / 0.7133–0.7844. Matches `external_validation.json` and Table 7.
- Derived, from `s3_calib_dca.json`, the net-benefit-positive thresholds per split: patient last-positive 0.58; temporal positive band 0.66–0.73, last-positive 0.73.
- Recomputed coverage and MAP statistics from `s2_features.csv`: any-of-6 vital means non-null = 16,622 (98.58%); `map_mean` non-null = 16,036 (95.11%); `map_n` median 3, IQR 2–4; demographics mean non-null = 99.68%.

**Discrepancies table:**

| # | Item | Manuscript | Source/Recomputed | Verdict |
|---|---|---|---|---|
| A | Demographics coverage | 99.8% (T3:317) | 99.68% → 99.7% | Minor (rounding) |
| B | Release URL | repo root | should be `/releases/tag/v1.0.0` | Minor (precision) |
| C | Temporal DCA framing | "remains positive up to 0.73" | positive only 0.66–0.73 | Minor (narrative) |
| D | External selection denominator | not reported | 6,388 screened (brief) | Minor (disclosure) |
| E | Audit-trail coverage of Table 1 / 16,036 | claim "every number traceable" | not in `s4_audit_trail.csv` | Minor (provenance) |
| F | External negative-by-construction count | not reported | set in `ext_build.py:88` | Minor (disclosure) |
| G | External anchor phase-shift | disclosed as adaptation | no leakage; phase differs | Interpretive note |
| — | External metrics, Table 7, internal metrics, calibration, DCA NBs, subgroups, feature gains, cohort/anchor/outcome, BMI order, DCA thresholds, NIBP coverage | as printed | all recomputed/confirmed | Correct |

No numeric *error* was found in any performance, calibration, external-validation, subgroup, or feature-importance figure. All discrepancies are minor (rounding, URL precision, narrative framing, disclosure completeness, and one interpretive note about the external anchor phase).

---

## § Verdict

**Minor.** The manuscript's quantitative claims — including the externally recomputed AUPRC 0.160 / AUROC 0.751, the internal core-benchmark Table 7 rows, the "apply did not refit" code path, all internal model metrics, calibration, DCA thresholds, subgroups and feature importances — were independently recomputed from the raw artefacts and are correct to the digit. The only issues are (a) one 0.1 rounding slip in Table 3 (99.8 → 99.7), (b) a release-URL precision preference (tag vs root), (c) a slightly misleading temporal-DCA narrative, and (d) a few disclosure/provenance gaps (external selection denominator, external negative-by-construction count, audit-trail completeness). None affect the conclusions. With these minor fixes the provenance audit is satisfied and the manuscript is suitable for acceptance on numerical grounds.
