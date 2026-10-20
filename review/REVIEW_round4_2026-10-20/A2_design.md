# Independent Design / Methodology Review — Round 4 (2026-10-20)

**Manuscript:** "Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: development and internal validation in MOVER/SIS with external validation in VitalDB" (BMC Anesthesiology, TRIPOD 2b).
**Reviewer role:** Biostatistician + ML-validation methodologist. Focus: study design, leakage, validation integrity, statistical correctness.
**Independence:** This review was written without reading any other reviewer file, any prior review, or any author-response/verification statement. Every number below was recomputed or read by me from the manuscript, scripts, config, or result files listed under "What I actually checked."

---

## 1. Anchor-phase mismatch — a confounded (not like-for-like) external transfer (MAJOR)

【Problem】 The external anchor is VitalDB `opstart` (operation START), which occurs *after* induction and intubation, whereas the internal anchor is the first `Intubation` event (pre-/at-induction); the external "pre-anchor 15-min window" therefore captures a different physiological phase than the internal pre-intubation window, so the external validation does not test the same clinical task the model was built for.

【Evidence】
- Internal anchor: `manuscript_v0.1.md:117-120` — "first recorded Intubation event (n = 13,834; 82.1%)"; anchor median 15 min after OR start.
- External anchor: `manuscript_v0.1.md:181-183` — "the prediction anchor was adapted from the MOVER intubation anchor to the operation start time (opstart)"; feature window `[opstart−15 min, opstart]`, outcome `D1` over `[opstart, opend]`.
- Feature derivation confirms the phase: `scripts/ext_build.py:100-101,113` builds `pre = (t_s >= opstart − 900) & (t_s <= opstart)` for the *vitals* window, i.e. the 15 minutes immediately before surgery start, which in VitalDB is the induction/intubation period, not the pre-induction period used internally.
- Leakage check (directly answering the brief): the external feature window ends exactly at `opstart` and the outcome window begins at `opstart`; there is **no label–feature window overlap and no leakage** (also confirmed by the internal leakage audit, `results/s2_data_quality.json:64-130`, all domains `max_used_time_minus_anchor = 0.00`, `leakage_audit_all_pass = true`, and `scripts/s3_models.py:73-74` BANNED-column guard). The problem is *confounding*, not leakage.

【Why it matters】 The model's dominant predictor is pre-anchor mean MAP (`manuscript_v0.1.md:414`), and the stated clinical question is prediction *from data available at induction* (`manuscript_v0.1.md:18,86-88`). In VitalDB the "pre-anchor" MAP now includes the induction/intubation hypotension period, which is intrinsically more informative about *intra*-operative hypotension than pre-induction MAP. Two consequences follow: (i) the external evaluation tests a related but **different** predictor set (post-induction MAP), so it is not a fair test of the induction-anchor model; (ii) the fact that external AUROC (0.751) *exceeds* the internal 53-feature AUROC (0.698–0.710, `manuscript_v0.1.md:443-444`) is consistent with the external feature window being the more prognostically loaded one — i.e. the external result may *overstate* generalisability rather than conservatively demonstrate it. The outcome window is also phase-shifted (post-opstart vs post-intubation), contributing to the prevalence gap (5.73% vs 15.55%). The current text discloses the anchor *adaptation* but not that the *phase* (and hence the feature semantics and label window) differs, so the conclusion "the same model retained discrimination … without refitting" (`manuscript_v0.1.md:615-616`) overstates what was shown.

【Specific fix】 Insert an explicit method/limitation statement and temper the conclusion. Suggested replacement for `manuscript_v0.1.md:536-543` (Limitation 1) and the parallel Discussion sentence:

> "Because VitalDB records no intubation event, the external anchor is operation start (opstart), which follows induction and intubation. The external pre-anchor 15-min feature window therefore captures a *post-induction, intra-operative* physiological phase, whereas the MOVER anchor (first intubation) precedes induction; the external outcome window also begins later than the internal one. Both the feature and label windows are phase-shifted. We interpret the external AUROC as evidence that the *ranking signal* in perianaesthetic MAP generalises across centres and recording architectures — not as evidence that a strictly pre-induction model generalises unchanged. No label–feature overlap occurs because the external feature window ends at opstart, the exact onset of the outcome window."

And revise `manuscript_v0.1.md:615-616` ("the same model retained discrimination … without refitting") to "the model's *discrimination* (ranking) transferred to an independent cohort under an adapted, later anchor, while calibration did not."

---

## 2. `anchor_minus_or_start` is silently redefined to a different quantity in VitalDB (MODERATE, linked to #1)

【Problem】 A top-five predictor — "Interval from OR start to anchor" (gain rank 5, `manuscript_v0.1.md:418`) — is fed to the external model with a **redefined meaning** that is disclosed in the config but not in the manuscript.

【Evidence】
- MOVER semantics: time from OR start to the intubation anchor; `results/s2_data_quality.json:8-12` gives median 15 min (IQR 11–24).
- VitalDB semantics: `scripts/ext_build.py:147` sets `feat["anchor_minus_or_start"] = float(opstart)/60.0` — i.e. *case-start to opstart*, a different quantity; `config/config_vitaldb.yaml:67` acknowledges "VitalDB 重定义为 anchor_minus_case_start".
- Manuscript disclosure (`manuscript_v0.1.md:186-188`) lists only `anchor_is_intubation = 0` and `or_year = 0` as "not derivable from VitalDB" and set to zero; the redefinition of `anchor_minus_or_start` is **not** mentioned.

【Why it matters】 Feeding a mis-semantic feature to a tree model is a silent transportability bug: the splits the model learned on MOVER's "OR-start→intubation interval" no longer correspond to anything coherent in VitalDB. Because this feature ranked among the strongest (`manuscript_v0.1.md:418`), the external predictions partly rest on an incoherent input, further weakening the "fair external validation" interpretation and compounding Issue #1.

【Specific fix】 Either (a) set `anchor_minus_or_start = 0` in VitalDB with the same rationale as `anchor_is_intubation` and disclose it explicitly, or (b) if a comparable quantity exists, define and report it identically. Add to `manuscript_v0.1.md:186-188`: "the MOVER feature `anchor_minus_or_start` (OR-start to intubation interval) is not reproducible in VitalDB and was set to 0 / redefined; this timing feature ranked among the top predictors internally, so its altered meaning is a further transportability limitation of the external evaluation."

---

## 3. External selection bias: the excluded denominator and selection effect are undisclosed (MODERATE)

【Problem】 The external cohort is restricted to VitalDB cases with an arterial MAP track, but the manuscript reports only the included numerator (n = 3,735) and never the excluded denominator or the characteristics of excluded cases, leaving the direction and magnitude of selection bias unknown.

【Evidence】
- `manuscript_v0.1.md:183-184`: "The external cohort comprised cases with an arterial mean arterial pressure track (Solar8000/ART_MBP or EV1000/ART_MBP) and valid opstart/opend times (n = 3,735)." No denominator, no count of cases lacking an arterial track, no comparison of included vs excluded.
- `results/ext/vitaldb_features_qa.json:1-7` reports `n_cohort_valid = 3735`, `n_d1_positive = 214`, `prevalence_D1 = 0.0573`, but contains **no** field describing how many VitalDB cases were screened or excluded for lacking an arterial MAP track.
- Internal precedent for disclosure exists: `manuscript_v0.1.md:562-568` (Limitation 7) explicitly reports the 1,496 internally excluded-by-construction cases and the conditional prevalence, so the omission externally is inconsistent.

【Why it matters】 Arterial-line placement is not random; it tracks higher acuity, longer, and more invasive cases. Restricting to arterial-MAP cases therefore induces a spectrum effect whose sign is uncertain (it could raise *or* lower external prevalence and discrimination). Without the denominator and a description of excluded cases, a reader cannot judge whether the 5.73% prevalence and the 0.751 AUROC are representative of VitalDB at large or of a selected subgroup. This is the same "selection bias can inflate apparent performance" hazard the manuscript itself raises (`manuscript_v0.1.md:477, 553-558`).

【Specific fix】 Add to `manuscript_v0.1.md:183-184` (and to Limitation 1) the screening funnel: number of VitalDB cases assessed, number excluded for lacking an arterial MAP track (and for invalid opstart/opend), and a brief description (or availability of) how included cases differ (e.g. age, ASA if present, case duration, surgery type). At minimum state the denominator explicitly, e.g. "of 6,388 VitalDB cases with an arterial MAP track, 3,735 had valid opstart/opend times."

---

## 4. External Brier 0.179 presented in Table 7 invites cross-cohort misreading (MINOR)

【Problem】 Table 7 lists the external Brier (0.179) alongside the internal Brier scores (0.198, 0.199) without a non-comparability note, inviting the misleading inference that the external model is "better calibrated."

【Evidence】 `manuscript_v0.1.md:441-445` (Table 7) places `Brier 0.179` in the same column as internal `0.198`/`0.199`; the text correctly interprets 0.179 as miscalibration (`manuscript_v0.1.md:434-435, 542-543`), but the table itself does not.
- Recomputed external Brier = 0.1789 (`results/ext/external_validation.json:16`; my recompute: 0.1789), and the external no-information Brier would be 0.0573×(1−0.0573) = 0.0538, so 0.179 ≫ 0.054 confirms miscalibration — but a reader scanning the table could compare 0.179 vs 0.198 directly.

【Why it matters】 Brier is prevalence-dependent and not comparable across cohorts of different base rates; placing the values in one column without qualification can be misread as a calibration comparison, undercutting the manuscript's own correct caveat.

【Specific fix】 Add a Table 7 footnote: "Brier is prevalence-dependent and is not comparable between the internal (prevalence 15.55%) and external (5.73%) cohorts; the external Brier 0.179 reflects miscalibration (predicted mean 0.365 vs observed 0.057), not good calibration."

---

## 5. Abstract under-specifies that the externally applied model is the 53-feature core subset (MINOR)

【Problem】 The abstract's external-validation sentence says "the unchanged model retained discrimination" without stating it is the 53-feature core subset, which could be read as the full 206-feature model.

【Evidence】 `manuscript_v0.1.md:35-36` ("the unchanged model retained discrimination (AUROC 0.751 …; AUPRC 0.160 …)"). The Methods correctly specify the 53-feature core subset (`manuscript_v0.1.md:185-189`), and Table 7 carries the note (`manuscript_v0.1.md:447-449`), but the abstract is the most-read section.

【Why it matters】 Conflation of the headline full-model result (AUPRC 0.347) with the externally tested core model (internal AUPRC 0.321) is a known over-claim risk; precision in the abstract prevents it.

【Specific fix】 Change `manuscript_v0.1.md:35-36` to: "Externally (VitalDB, prevalence 5.7%), the unchanged **53-feature core** model retained discrimination (AUROC 0.751 …; AUPRC 0.160 …) but probabilities were uncalibrated."

---

## 6. Subgroup AUPRC lacks confidence intervals; the unstable underweight estimate is flagged but not quantified (MINOR)

【Problem】 Table 5 reports point-estimate AUPRC per subgroup with no bootstrap CIs, so the instability of small strata (e.g. underweight AUPRC 0.616) is asserted but not quantified.

【Evidence】 `manuscript_v0.1.md:383-400` (Table 5) gives only point AUPRC; `manuscript_v0.1.md:379-381, 399-400` correctly cautions that underweight is unstable (98 test cases, 512 cohort) but provides no interval. The main model reports 1,000-bootstrap CIs (`manuscript_v0.1.md:27, 348-354`), so the subgroups are inconsistent by comparison.

【Why it matters】 Without CIs the reader cannot tell whether, e.g., the underweight 0.616 vs overall 0.347 difference is noise from ~15 events. The manuscript's own honesty agenda is better served by quantifying uncertainty.

【Specific fix】 Add 1,000-bootstrap 95% CIs to Table 5 (or at least to the underweight and age<50 strata), computed analogously to `scripts/s3_models.py:91-103` but stratified; state the per-stratum event counts alongside n.

---

## 7. Temporal split relies on a single test year (2018) — acceptable but thin (context, MINOR)

【Problem】 The secondary "temporal" split trains on ≤2017 and tests on 2018 only, yielding a single thin test year (n = 1,818; 291 events).

【Evidence】 `manuscript_v0.1.md:197-198` and `scripts/s3_models.py:178-180` (`te_mask = (year == 2018)`). Results are closely similar to patient-split (`manuscript_v0.1.md:340-354`), supporting stability, but the test set is small.

【Why it matters】 A single-year test is a reasonable robustness check but cannot fully separate calendar drift from sampling; it should be framed as such, not as strong evidence against drift.

【Specific fix】 In `manuscript_v0.1.md:340-341` add: "The temporal test set is a single year (2018, n = 1,818; 291 events); the similarity to the patient-level split supports stability but is a limited test of calendar drift."

---

## § Stands up (verified correct)

1. **Bootstrap resampling is correctly aligned and reproducible.** `scripts/s3_models.py:91-103` indexes both `y_true` and `y_pred` by the same bootstrap index `s` (no feature/label mismatch — the prior project bug is resolved); 1,000 resamples; `np.random.default_rng(seed)` with fixed `seed = 12345` (`scripts/s3_models.py:52,92`). The external bootstrap (`scripts/ext_build.py:241-250`) likewise uses `rng.choice` over aligned `(y, p)` with seed 12345 and 1,000 resamples.
2. **Core-vs-full distinction is clearly maintained.** `manuscript_v0.1.md:447-449` and Table 7 note state the external/internal comparison uses the identical 53-feature core model and that the 0.347/0.722 headline is the full 206-feature model. Recomputed internal core (patient) AUPRC 0.3206 / AUROC 0.6979 (`results/ext/core_benchmark.json:54-65`) rounds to the manuscript's 0.321/0.698 (`manuscript_v0.1.md:443`) — consistent, no conflation.
3. **AUPRC non-comparability across prevalence is honestly handled.** `manuscript_v0.1.md:431-433` and `540-541` explicitly state the lower external AUPRC reflects prevalence (5.73% vs 15.55%), that AUPRC is not directly comparable, and that AUROC is the comparable discriminator. The 2.8× lift (0.160/0.0573, recomputed 2.79) and 2.1× internal core lift are correctly computed.
4. **No external recalibration is correctly NOT transferred.** The internal "well calibrated" claim (`manuscript_v0.1.md:39, 363-365`) is scoped to the internal isotonic recalibration (Brier 0.191→0.119); externally the manuscript correctly reports miscalibration (mean predicted 0.37 vs observed 0.057; Brier 0.179) and requires local recalibration (`manuscript_v0.1.md:434-435, 542-543`). It does **not** present Brier 0.179 as calibration evidence in the text.
5. **DCA last-positive thresholds verified.** Recomputed from `results/s3_calib_dca.json`: patient-split net benefit last positive at threshold **0.58** (matches `manuscript_v0.1.md:369`), temporal-split last positive at **0.73** with a negative band at 0.55–0.65 and a positive band 0.66–0.73 (the "transient dip near 0.67" at `manuscript_v0.1.md:369` is consistent). The prior 0.45-vs-0.58 patient bug is fixed. Net-benefit values at 0.10/0.15 (patient 0.079/0.050; temporal 0.085/0.058) match the manuscript (`manuscript_v0.1.md:370-371`).
6. **Conditional prevalence formula verified.** 2,622 / (16,861 − 1,496) = 2,622 / 15,365 = 0.1706 = 17.1% (`manuscript_v0.1.md:566`; denominator cross-checked against `results/s1_cohort.json:14` analytic_pids = 16,861 and `manuscript_v0.1.md:127` excluded = 1,496).
7. **External metrics independently recomputed and match.** From `results/ext/vitaldb_predictions.csv` + `vitaldb_labels.csv` (n = 3,735; events = 214; prevalence 0.0573): AUPRC = 0.1600, AUROC = 0.7507, Brier = 0.1789, predicted-mean = 0.3650; bootstrap 95% CI AUPRC [0.1291, 0.2021], AUROC [0.7133, 0.7844] — identical to `results/ext/external_validation.json` and `manuscript_v0.1.md:445`. The `apply` stage loads the saved `mover_core_model.joblib` (`scripts/ext_build.py:233`) and does **not** refit — confirmed.
8. **Leakage audit is sound for both cohorts.** Internal: all seven time-stamped domains truncated at anchor, max interval 0.00 min, zero unparseable timestamps (`results/s2_data_quality.json:64-130, 301`). External: feature window `[opstart−15, opstart]` ends exactly where the outcome window `[opstart, opend]` begins (`scripts/ext_build.py:84,100-101`) — no overlap, no leakage.

---

## § Questions for the authors

1. What is the VitalDB screening denominator? Of how many total VitalDB cases (with an arterial MAP track, and overall) were 3,735 selected, and how do included vs excluded cases differ (acuity, duration, surgery type, age)? Please report the funnel.
2. For the external cohort, what is the distribution of `anchor_minus_or_start` (= opstart/60) actually fed to the model, and did you consider setting it to 0 (like `anchor_is_intubation`) to avoid feeding a mis-semantic feature? Did removing/zeroing it change the external AUROC materially?
3. In VitalDB, what fraction of the pre-anchor 15-min window actually lies *before* induction vs *during* induction/intubation? If most of it is post-induction, the "pre-induction prediction" claim for the external site does not hold — can you characterise this?
4. Did you verify that the external outcome window `[opstart, opend]` is, on average, a later and/or shorter exposure period than the internal `[intubation, OR_end]`, and could this explain part of the prevalence drop from 15.55% to 5.73%?
5. Can you provide per-subgroup bootstrap CIs for Table 5, and the per-stratum event counts, so the underweight instability is quantified rather than asserted?

---

## § What I actually checked

**Files read (full text):** `manuscript/manuscript_v0.1.md` (660 lines); `scripts/s3_models.py`; `scripts/ext_build.py`; `config/config_vitaldb.yaml`; `results/s3_metrics.json`; `results/s3_calib_dca.json`; `results/s2_data_quality.json`; `results/s1_cohort.json`; `results/s1_outcomes_postanchor.json`; `results/ext/external_validation.json`; `results/ext/core_benchmark.json`; `results/ext/mover_core_train_metrics.json`; `results/ext/vitaldb_features_qa.json`; `review/REVIEW_round4_2026-10-20/_PANEL_BRIEF.md` (permitted round-4 brief only).

**Forbidden files avoided:** no `REVIEW_round*.md` except the round-4 brief, no `A1/A2/A3/A4_*.md`, no `Round1_review*`, no `quality_gate*`, `reference_verification*`, `journal_verification*`, `external_validation_plan.md`, `.workbuddy/`, `author_verification_statement.md`, `GITHUB_DEPOSIT_SOP.md`, and no other reviewer files in the round-4 folder.

**Commands run (Python 3, `C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe`):**
- Merged `results/ext/vitaldb_predictions.csv` (cols `caseid, y, p`, n = 3,735) with `vitaldb_labels.csv` on `caseid`; computed AUPRC = 0.1600, AUROC = 0.7507, Brier = 0.1789, predicted-mean = 0.3650; 1,000-bootstrap CI AUPRC [0.1291, 0.2021], AUROC [0.7133, 0.7844]; lift = 2.79. All match the manuscript.
- Conditional prevalence: 2,622 / (16,861 − 1,496) = 0.1706.
- Parsed `results/s3_calib_dca.json` DCA arrays: confirmed patient last-positive net-benefit threshold = 0.58 and temporal = 0.73 (with the 0.55–0.65 negative / 0.66–0.73 positive band), matching the manuscript's reported thresholds and the "dip near 0.67."

**Discrepancies found:** None in the recomputed numbers versus the manuscript. The substantive issues (anchor-phase mismatch, silent `anchor_minus_or_start` redefinition, undisclosed external selection denominator, Brier-table framing, abstract core-specification, missing subgroup CIs) are **interpretation/disclosure** problems, not arithmetic errors. The prior-known bootstrap index-mismatch bug and the 0.45-vs-0.58 DCA bug are **resolved** in the current code/manuscript.

---

## § Verdict: **Major (revise)**

The internal development and validation are methodologically sound and refreshingly honest about sparsity, spectrum bias, and the dominance of present blood pressure. The leakage audit, bootstrap procedure, DCA, and non-comparability of AUPRC are all correct and verified. However, the **external validation's central conclusion is overstated**: because the VitalDB anchor is operation start (post-induction) rather than intubation (pre-induction), the external features and labels are phase-shifted, the `anchor_minus_or_start` feature is silently redefined, and the selection denominator is undisclosed. The manuscript discloses the anchor *adaptation* but not that the evaluation tests a different physiological phase and a different (later, more prognostically loaded) feature window — which threatens the "discrimination transfers" claim and may even flatter it. These are fixable with explicit disclosure and tempered wording (Issues #1–#3); once corrected, the paper would be suitable for acceptance. Issues #4–#7 are minor polish.
