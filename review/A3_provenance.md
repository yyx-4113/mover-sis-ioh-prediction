# A3 — Implementation / Provenance / Recompute Audit

**Role:** Independent recompute & traceability auditor (treated as first submission).
**Manuscript:** `manuscript/manuscript_v0.1.md`
**Source files audited:** `s1_cohort.json`, `s1_outcomes_postanchor.json`, `s2_data_quality.json`, `s3_metrics.json`, `s3_subgroups.json`, `s3_feature_importance.json`, `s3_calib_dca.json`, `config.yaml`, and `s4_audit_trail.csv` (the file the manuscript calls "Additional file 1").
**Headline claim under test (manuscript lines 192–195):** *"Every number reported in this manuscript is generated from a result file by the analysis pipeline and is traceable through an audit trail (Additional file 1) that records, for each quantity, its value, the producing artefact and the command that reproduces it."*

The recompute below shows that **most of the reported numbers are internally consistent with the result files** — the arithmetic is sound and the model/cohort tables match `s3_*.json` to the rounding. However, the manuscript's central traceability claim is **contradicted**: a substantial set of explicitly reported numbers is absent from `s4_audit_trail.csv`, and the audit trail records a *different metric* than what appears in Table 3 for 9 of 12 domains.

---

## A. Numeric recomputations that **MATCH** (the bulk of the paper is sound)

### Cohort arithmetic (Check 1)
- **Manuscript:** 19,114 screened; exclusions 8 + 1,632 + 371 + 242; analytic 16,861.
- **Source:** `s1_cohort.json` → `source_pids=19114`, `excl_implausible_or_window=8`, `excl_short_or_window=1632`, `excl_underage=371`, `excl_bad_anchor=242`, `analytic_pids=16861`.
- **Recompute:** 19114 − (8+1632+371+242) = 19114 − 2253 = **16,861**. ✅ MATCH.

### Anchor counts (Check 2)
- `s1_cohort.json` → Intubation 13,834, Surgery_start 3,027 (sum 16,861, no double counting). ✅ Values MATCH.
- **Minor rounding note (see Issue §M2):** 13,834/16,861 = 82.05% (→82.1% to 1 dp) and 3,027/16,861 = 17.95%; the manuscript's paired "82.0% / 18.0%" is internally inconsistent with standard rounding. Values themselves are correct.

### Outcome D1 (Check 3)
- 2,622 / 16,861 = 0.15546 → **15.55%**. `s1_outcomes_postanchor.json` → `positive_pids=2622`, `prevalence=0.1555`. ✅ MATCH.

### Table 2 — 14 definition prevalences (Check 4)
Recomputed % = n / 16,861 for all 14 rows. All match the manuscript (O1 0.09, O2 0.32, O3 0.01, O4 0.16, S1 7.20, B1 42.94, B2 30.79, B3 6.87, D1 15.55, D2 0.54, E1 22.36, E2 65.78, O5 7.66, O6 3.39). Each n also matches `s1_outcomes_postanchor.json`. ✅ MATCH (all 14).

### Table 4 — model metrics, 4 models × 2 splits (Check 5)
All 8 rows (AUPRC, AUROC, Brier, and both 95% CIs) recomputed from `s3_metrics.json`:
- Patient: baseline 0.234/0.626/0.239; full 0.301/0.707/0.216; XGBoost 0.347/0.722/0.191; LightGBM 0.337/0.724/0.183 — all match manuscript to rounding.
- Temporal: baseline 0.243/0.609/0.240; full 0.336/0.725/0.227; XGBoost 0.339/0.733/0.194; LightGBM 0.337/0.732/0.188 — all match.
- All 16 CI bounds match (e.g., XGBoost patient AUPRC CI [0.3089, 0.3875] → 0.309–0.387). ✅ MATCH (all 8 rows × 3 metrics × 2 CIs).

### Table 5 — subgroup AUPRC (Check 6, both splits)
All 9 patient-split and 9 temporal-split values match `s3_subgroups.json` to rounding (Men 0.299/0.267, Women 0.357/0.370, <50 0.380/0.377, 50–64 0.324/0.305, ≥65 0.186/0.194, BMI<18.5 0.616/0.382, BMI 18.5–25 0.392/0.354, BMI 25–30 0.286/0.306, BMI≥30 0.257/0.330). ✅ MATCH (all 18).

### Table 6 — top-10 feature gain (Check 7)
All 10 gains match `s3_feature_importance.json` to rounding (map_mean 175.489→175.5 … art_map_mean 43.221→43.2). "Mean MAP gain ≈ 2.3× next" = 175.5/75.2 = 2.33, consistent with text. ✅ MATCH (all 10).

### Calibration (Check 8, point values)
- Patient: brier 0.1905→0.191, 0.119; slope 0.9092→0.909; intercept 0.0083→0.008. `s3_calib_dca.json` patient. ✅ MATCH.
- Temporal: brier 0.1935→0.194, 0.1217→0.122; slope 0.9338→0.934; intercept 0.0058→0.006. ✅ MATCH (values correct; see §M1 for audit-trail absence).

### Table 3 leakage audit — max interval 0.00 for the 7 time-stamped domains (Check 10)
`s2_data_quality.json` → `leakage_audit` contains exactly 7 domains (procedure_events, patient_vitals, patient_observations, patient_ventilator, patient_medication, patient_labs, patient_input_output), **all** with `max_used_time_minus_anchor = 0.0` and `n_time_nat = 0`. ✅ MATCH. The leakage result itself is solid.

### Table 1 demographics / procedure groups / coverage counts (Check 11)
Sex (M 8355/49.6, F 8502/50.4, unknown 4/<0.1), BMI computable 16,699/99.0, all 12 procedure-group counts and % (GI 4916/29.2 … NO_SURGERY 6/<0.1), and the four coverage counts — invasive 2503/14.8, ventilation 4852/28.8, labs 76/0.45, fluids 2794/16.6 — all reconcile with `s2_data_quality.json` counts and 16,861 denominators. ✅ MATCH.

### Figure legends (Check 14)
`figs/fig1_cohort.png`, `fig2_definitions.png`, `fig3_pr_roc.png`, `fig4_calib_dca.png`, `fig5_importance.png` all exist and match the five legends; `s3_figs/` contains the same content (auprc/auroc/calibration/dca/importance). No missing or mismatched figure references; no broken markdown tables (all table column counts consistent). ✅ MATCH.

---

## B. Issues found

### 【Major】§P1 — DCA net-benefit numbers are absent from the audit trail (contradicts "every number")
- **【Problem】** The manuscript reports explicit DCA net-benefit values (lines 343–346): 0.050 & 0.058 at threshold 0.15, 0.079 & 0.085 at threshold 0.10, and "up to 0.58 (patient) / 0.45 (temporal)". None of these appear in `s4_audit_trail.csv`.
- **【Evidence】** `s4_audit_trail.csv` (lines 1–95) contains no `dca.*` / `net_benefit*` rows at all. The values are present only in `s3_calib_dca.json` (`dca.net_benefit_model` …). Manuscript lines 343–346.
- **【Why it matters】** This is the precise kind of number the manuscript says is "traceable through an audit trail (Additional file 1)." A reader opening Additional file 1 cannot find these values; the headline reproducibility claim (lines 192–195) is directly contradicted.
- **【Specific fix】** Add the DCA rows to `s4_audit_trail.csv` (per-threshold `net_benefit_model`, `net_benefit_treat_all`, `net_benefit_treat_none` for both splits, or at minimum the four reported points plus the two "up to" crossing thresholds), sourced from `s3_calib_dca.json`, with the reproducing command.

### 【Major】§P2 — Temporal calibration numbers are absent from the audit trail
- **【Problem】** The temporal calibration values (brier 0.194→0.122, slope 0.934, intercept 0.006; line 341) are not in `s4_audit_trail.csv`. Only **patient** calibration is recorded (lines 72–75: `calib.patient.*`). There is no `calib.temporal.*` row.
- **【Evidence】** `s4_audit_trail.csv` lines 72–75 cover patient only; `s3_calib_dca.json` "temporal" block has the values. Manuscript line 341.
- **【Why it matters】** Same traceability gap as §P1 — exactly half the calibration result cannot be traced through Additional file 1.
- **【Specific fix】** Add `calib.temporal.brier_raw/calibrated/slope/intercept` rows to the audit trail.

### 【Major】§P3 — Temporal subgroup AUPRC absent from the audit trail
- **【Problem】** Table 5 reports temporal-split AUPRC for all 9 subgroups, but `s4_audit_trail.csv` contains only `subgroup.patient.*` (lines 76–84). No `subgroup.temporal.*` rows exist.
- **【Evidence】** `s4_audit_trail.csv` lines 76–84 (patient only); `s3_subgroups.json` "temporal" block holds the values. Manuscript Table 5 (lines 358–368).
- **【Why it matters】** An entire column of Table 5 is untraceable through the audit trail.
- **【Specific fix】** Add `subgroup.temporal.*` rows to the audit trail.

### 【Major】§P4 — Table 3 "Coverage (%)" does not match the audit trail (different metric, 9 of 12 domains)
- **【Problem】** The audit trail records `features.coverage.<domain>.mean_non_null_pct` (mean non-null *across features*) but the manuscript's Table 3 "Coverage (%)" column is case-count coverage (cases with any data ÷ 16,861). The two disagree for 9 of 12 domains:
  - Demographics: audit 99.7% (0.9968) vs manuscript 99.8%
  - Anaesthesia technique: audit 100.0% (1.0) vs manuscript 98.2%
  - Medication: audit 100.0% (1.0) vs manuscript 98.3%
  - Non-invasive BP: audit 95.7% (0.9568) vs manuscript 95.1%
  - Ventilation: audit 32.8% (0.3283) vs manuscript 28.8%
  - Invasive monitoring: audit 15.0% (0.1502) vs manuscript 14.8%
  - Fluid/bleeding: audit 100.0% (1.0) vs manuscript 16.6%
  - Laboratories: audit 16.95% (0.1695) vs manuscript 0.45%
  - (Anchor 100%, Surgery 100%, Derived NIBP 89.8%, QA 99.6% happen to coincide.)
- **【Evidence】** `s4_audit_trail.csv` lines 35–47 (`features.coverage.*.mean_non_null_pct`) vs manuscript Table 3 (lines 292–305) and `s2_data_quality.json` `domain_coverage`. The manuscript's numbers reconcile with the *counts* in `s2_data_quality.json`, not with the audit-trail metric.
- **【Why it matters】** A reviewer verifying Table 3 against "the audit trail that records, for each quantity, its value" will find the values are simply not there / contradictory. This is the single largest provenance gap and undermines the reproducibility claim for the domain-coverage results (a core part of the leakage/strengths narrative).
- **【Specific fix】** Either (a) change the audit trail to record the same case-count coverage used in Table 3, or (b) add the case-count coverage as a separate, clearly labelled set of audit rows, and verify each cell ties out.

### 【Moderate】§P5 — "1,496 cases (8.9%)" with <10 post-anchor measurements is untraceable
- **【Problem】** Lines 123 and 471 state 1,496 (8.9%) cases had <10 post-anchor measurements. This n is in neither `s4_audit_trail.csv` nor any `s1_*/s2_*/s3_*.json` I was given (`s1_outcomes_postanchor.json` records only positive_pids and prevalences, not the <10 denominator).
- **【Evidence】** Manuscript lines 123, 471; absent from `s4_audit_trail.csv` and `s1_outcomes_postanchor.json`. (1,496/16,861 = 8.87% → 8.9% is arithmetically consistent, so the % is fine; the n is unverifiable from provided files.)
- **【Why it matters】** A reader cannot reproduce or locate this quantity; it is a derived count that should be emitted to the audit trail.
- **【Specific fix】** Emit `outcome.D1.n_lt10_measurements=1496` (and its denominator) to the audit trail.

### 【Moderate】§N1 — Patient DCA "positive up to 0.58" is inaccurate (recompute from source)
- **【Problem】** Line 344 claims net benefit is positive "up to 0.58" on the patient split. Recomputing from `s3_calib_dca.json`, `dca.net_benefit_model` (calibrated XGBoost) is positive through threshold **0.56** (value 9.88e-05 at index 55) and turns negative at **0.57** (value −6.5e-05 at index 56). Linear interpolation gives a zero-crossing at ≈ **0.566**, not 0.58.
- **【Evidence】** `s3_calib_dca.json` patient `dca.thresholds`/`net_benefit_model`: index 55 (threshold 0.56) = 9.882e-05 (>0); index 56 (0.57) = −6.508e-05 (<0). Temporal split is correct: index 44 (0.45) = +5.50e-04, index 45 (0.46) = −1.24e-03 → crosses at ≈0.452, matching manuscript "up to 0.45".
- **【Why it matters】** The patient upper bound is overstated by ~0.01–0.02 on the threshold axis; if a reader plots the DCA they will see the model curve cross zero near 0.56–0.57, not 0.58. It also feeds the Discussion's "up to about 0.20" contradiction (§C3).
- **【Specific fix】** Change "up to 0.58" to "up to about 0.56" (patient), or report the exact interpolated crossing from the source curve.

### 【Minor】§C1 — Orphan references [14], [15], [16]
- **【Problem】** Chiu 2025 (BMC Anesthesiol) [14], Cheun 2026 (BMC Anesthesiol) [15], and Walsh 2013 (Anesthesiology) [16] are listed in the References but are **never cited** anywhere in the body text. The body's last citation is [13] (Oyarzun).
- **【Evidence】** Manuscript References lines 587–595; full-text scan shows citations only up to [13] (lines 51, 58, 71, 76, 78, 91, 94, 127, 195, 426, 431, 432). No occurrence of "[14]", "[15]", or "[16]" in the text, and the authors Chiu/Cheun/Walsh are never named in the narrative.
- **【Why it matters】** Either these are stray references (should be removed) or they were intended to support a claim that is missing (e.g., external-validation context). Both are editorial defects; if they were meant to support the "external validation required" limitation they should be cited there.
- **【Specific fix】** Either delete [14–16] or insert the intended in-text citations (e.g., in the Limitations or Relation-to-previous-work sections).

### 【Minor】§C2 — Rounding inconsistency in anchor percentages
- **【Problem】** "82.0% / 18.0%" (lines 22, 113–114, 220–221). 13,834/16,861 = 82.05% (→82.1% to 1 dp) and 3,027/16,861 = 17.95%. The paired figures should be (82.1, 17.9) or (82.0, 18.0) only if each is first rounded to a whole percent then shown with a trailing ".0" — an unconventional convention that makes each value individually off by 0.1 pp.
- **【Evidence】** `s1_cohort.json` anchor_source_counts; manuscript lines 22, 113–114.
- **【Why it matters】** Trivial numerically, but a reviewer recomputing will note the mismatch; adopt one consistent rounding rule.
- **【Specific fix】** Report 82.1% / 17.9% (or 82% / 18% without a spurious decimal).

### 【Minor】§C3 — Internal contradiction on the "useful threshold range"
- **【Problem】** Results (line 344) says net benefit is positive "up to 0.58 (patient) / 0.45 (temporal)"; Discussion (lines 401–403) says the model is "clinically usable in a decision-analytic sense across threshold probabilities up to about 0.20." These are inconsistent, and the "0.20" figure is unsupported by any source file.
- **【Evidence】** Manuscript lines 344 vs 401–403; no source file contains "0.20" as a threshold bound.
- **【Why it matters】** Sends conflicting messages about clinical usefulness; the 0.20 bound appears to be invented.
- **【Specific fix】** Reconcile to a single, source-derived bound (≈0.56 patient / 0.45 temporal per §N1), and either drop "0.20" or define the criterion it refers to (e.g., where net benefit exceeds treat-all by a stated margin).

### 【Minor】§C4 — "2.23×" vs "2.2×"
- **【Problem】** Results line 313: AUPRC is "2.23 times the prevalence"; Discussion line 401: "approximately 2.2 times better than chance." 0.3473/0.1555 = 2.233, so 2.23 is exact; "2.2" is a looser restatement that disagrees at the first decimal.
- **【Evidence】** Manuscript lines 313, 401; `s3_metrics.json` XGBoost patient auprc 0.3473, `s1_outcomes_postanchor.json` prevalence 0.1555.
- **【Why it matters】** Cosmetic, but an independent reader may read 2.23 vs 2.2 as an inconsistency.
- **【Specific fix】** Use 2.23× (or "≈2.2×") consistently.

### 【Minor】§C5 — Table 3 says "seven time-stamped domains" but shows 10 rows with 0.00
- **【Problem】** Text (lines 147–148, 307) states "seven time-stamped domains" passed with max interval 0.00. Table 3 lists **10** rows with 0.00 (Anchor characteristics, Anaesthesia technique, Medication, Non-invasive BP, Derived NIBP, QA counters, Ventilation, Invasive monitoring, Fluid/bleeding, Laboratories), of which only 7 correspond to the 7 domains actually present in `s2_data_quality.json` `leakage_audit` (Anaesthesia technique, Derived NIBP and QA counters are not separate leakage-audit entries; procedure_events is the only events domain and is shown twice as "Anchor characteristics" and "Anaesthesia technique").
- **【Evidence】** Manuscript lines 147–148, 292–308; `s2_data_quality.json` `leakage_audit` (7 entries).
- **【Why it matters】** Minor internal inconsistency; a reader counting the table's 0.00 rows will see 10, not 7.
- **【Specific fix】** Either relabel the 3 non-leakage-audit rows' max-interval as "n/a (derived/static)" or add them to the leakage audit explicitly; keep the "seven" count tied to the actual audit.

### 【Minor】§C6 — Table 1 surgical-group sub-rows drop the "Surgical group:" prefix
- **【Problem】** The first surgical-group row reads "Surgical group: gastrointestinal — n (%) | 4,916 (29.2)" but the remaining 11 rows (lines 230–241) show only the group name (e.g., "| neurosurgical | 2,530 (15.0) |"), breaking the column's label convention.
- **【Evidence】** Manuscript Table 1 lines 229–241.
- **【Why it matters】** Cosmetic table-consistency issue; not a numeric error.
- **【Specific fix】** Prefix every surgical-group row with "Surgical group:" for consistency.

### 【Minor】§C7 — BMI subgroup n inconsistency in Table 5
- **【Problem】** Table 5 shows n = 512 for BMI<18.5 but "—" for BMI 18.5–24.9, 25–29.9, and ≥30 (lines 366–368). If AUPRC could be computed for those strata, the stratum sizes are trivially known; presenting "—" for three BMI rows while giving a number for the fourth is inconsistent. Moreover, none of these n values (including 512) are in `s4_audit_trail.csv` or `s3_subgroups.json`.
- **【Evidence】** Manuscript Table 5 lines 365–368; `s3_subgroups.json` holds only auprc, no n; `s4_audit_trail.csv` has no subgroup n.
- **【Why it matters】** Defensibility of the "—" is weak and the subgroup sizes are untraceable.
- **【Specific fix】** Report all stratum n (they are readily computable) and add them to the audit trail; or state once why the middle-BMI n were omitted.

---

## § Stands up (≥3 verified-correct pillars)

1. **Cohort construction arithmetic is exact and traceable** — 19,114 − (8+1,632+371+242) = 16,861, matching `s1_cohort.json` to the digit (Check 1).
2. **Model performance Table 4 is fully reproducible** — all 8 rows × 3 metrics × 2-sided 95% CIs reconcile with `s3_metrics.json` to rounding (Check 5). This is the paper's central quantitative claim and it holds.
3. **Leakage audit is sound** — all 7 time-stamped domains in `s2_data_quality.json` show `max_used_time_minus_anchor = 0.0` with zero unparseable timestamps (Check 10); the manuscript's strongest methodological claim is supported by the data.
4. **Outcome definition prevalence table (Table 2) and subgroup/feature tables (5,6) all recompute correctly** from `s1_outcomes_postanchor.json` and `s3_*.json` (Checks 4, 6, 7).

## § Questions for the authors

1. Additional file 1 (`s4_audit_trail.csv`) does **not** contain the DCA net-benefit values, the temporal calibration numbers, the temporal subgroup AUPRC, or the Table 3 coverage percentages. Was the audit trail generated before these results, or is the "every number traceable" statement intended to refer to the `s3_*.json` files rather than the CSV? Please reconcile the claim with the actual CSV contents.
2. Why does Table 3's "Coverage (%)" use case-count coverage while the audit trail records mean-non-null-across-features (differing by up to ~16 pp for Laboratories and ~83 pp for Fluid/bleeding)? Which metric is the intended one?
3. The patient DCA upper bound is stated as 0.58 but the source curve crosses zero at ≈0.566. Should this be corrected, and should the Discussion's "up to about 0.20" be retracted or re-derived?
4. References [14] Chiu 2025, [15] Cheun 2026, and [16] Walsh 2013 are never cited — were they meant to support a specific claim (e.g., external validation), or should they be removed?
5. Where does the count 1,496 (<10 post-anchor measurements) originate, and can it be added to the audit trail?

## § What I actually checked (full recomputation ledger)

| # | Check | Source | Result |
|---|---|---|---|
| 1 | Cohort 19114−(8+1632+371+242)=16861 | s1_cohort.json | ✅ MATCH |
| 2 | Anchor 13834/16861=82.05%, 3027/16861=17.95% | s1_cohort.json | ⚠️ values correct, rounding pair inconsistent (§C2) |
| 3 | D1 2622/16861=15.55% | s1_outcomes_postanchor.json | ✅ MATCH |
| 4 | Table 2 all 14 n & % | s1_outcomes_postanchor.json | ✅ MATCH (all 14) |
| 5 | Table 4 all 8 rows × 3 metrics × 2 CIs | s3_metrics.json | ✅ MATCH (all) |
| 6 | Table 5 9 patient + 9 temporal AUPRC | s3_subgroups.json | ✅ MATCH (all 18); temporal absent from audit trail (§P3) |
| 7 | Table 6 top-10 gain | s3_feature_importance.json | ✅ MATCH (all 10) |
| 8 | Calibration point values (patient & temporal) | s3_calib_dca.json | ✅ values correct; temporal absent from audit trail (§P2) |
| 9 | DCA "up to 0.58 / 0.45" crossing | s3_calib_dca.json | ⚠️ temporal 0.45 ✅; patient 0.58 ❌ should be ≈0.566 (§N1) |
| 9b | DCA net benefit 0.050/0.058 @0.15, 0.079/0.085 @0.10 | s3_calib_dca.json | ✅ match source; ❌ NOT in audit trail (§P1) |
| 10 | Leakage max interval 0.00 ×7 domains | s2_data_quality.json | ✅ MATCH (all 7) |
| 11 | Table 1 sex/BMI/procedure/coverage counts | s2_data_quality.json | ✅ MATCH |
| 12 | References [14][15][16] cited in text? | manuscript body | ❌ orphan references (§C1) |
| 13 | Internal contradictions (2.23×/2.2×; 167 vs 147; 0.20 vs 0.58) | manuscript + sources | ⚠️ 2.23/2.2 (§C4), 0.20/0.58 (§C3); 167 vs 147 are different windows, no conflict |
| 14 | Table/figure syntax & legends | figs/, s3_figs/ | ✅ all figures present & matching; minor table cosmetics (§C5, §C6) |
| — | Table 3 coverage % vs audit trail | s4_audit_trail.csv | ❌ 9/12 domains disagree (§P4) |
| — | "1,496 (8.9%)" traceability | s4 + s1/s2/s3 jsons | ❌ untraceable from provided files (§P5) |

## § Verdict

**Major revision required.** The analytical substance is reproducible where it matters most — cohort assembly, the full model-performance table, the leakage audit, the outcome-definition grid, and the subgroup/feature tables all recompute exactly from the `s3_*.json`/`s1_*.json`/`s2_*.json` sources. **However, the manuscript's central reproducibility claim (lines 192–195, "every number … traceable through an audit trail / Additional file 1") is false as written**: a material fraction of the reported numbers — the entire DCA net-benefit panel, the temporal calibration and temporal subgroup results, the Table 3 coverage column, and the 1,496 count — are absent from `s4_audit_trail.csv`, and Table 3's coverage percentages directly contradict the metric the audit trail actually stores. These are provenance/integrity defects, not arithmetic ones, but they go to the heart of the journal's TRIPOD+AI / reproducibility expectations.

Concrete blockers before acceptance:
- **§P1–§P4**: bring `s4_audit_trail.csv` into line with the manuscript (add DCA, temporal calibration, temporal subgroups, and a consistent coverage metric), or soften the "every number traceable through the audit trail" claim to reference the `s3_*.json` result files.
- **§N1 / §C3**: correct the patient DCA upper bound (0.58 → ≈0.56) and resolve the 0.20-vs-0.58 contradiction.
- **§C1**: fix the three orphan references.

The arithmetic backbone is sound enough that, once the audit trail is completed and the minor inconsistencies corrected, this can be a solid, honestly-reported study.
