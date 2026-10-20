# Independent Review Panel — Brief (REVIEW round 4, 2026-10-20, CURRENT manuscript)

## Manuscript under review
- **File:** `manuscript/manuscript_v0.1.md` (full text, ~660 lines). Single-author clinical
  prediction-model paper: *"Prediction of sustained intraoperative hypotension burden from data
  available at anaesthesia induction: model development and internal and external validation in the
  MOVER/SIS and VitalDB cohorts."* Target journal: **BMC Anesthesiology**. Article type: **TRIPOD
  type 2b** (development + internal validation + external validation).
- **One-line claim:** a gradient-boosted model using only pre-anchor (pre-induction) data predicts a
  cumulative hypotension-burden outcome (D1) with internal AUPRC ≈ 0.35 / AUROC ≈ 0.72, and
  transfers *ranking* ability to an independent public cohort (VitalDB arterial, n=3,735) with
  external AUROC 0.751 but external AUPRC 0.160 (prevalence 5.7%), requiring local recalibration
  before clinical use.
- **Design snapshot (context only — verify everything yourself):**
  - Source (internal): MOVER/SIS (UCI), 9 linked tables, de-identified, DUA.
  - Internal cohort: 19,114 → 17,103 → **16,861** analysed adult cases.
  - Internal anchor: first Intubation (82.1%) else Surgery_start (17.9%).
  - Outcome D1: ≥10 post-anchor MAP measurements, ≥30% <65 mmHg; prevalence 15.55% (n=2,622).
  - 206 predictors truncated at anchor; 4 models; patient-level (primary) + temporal (secondary) split.
  - Primary metric AUPRC; 1,000 bootstrap CIs; OOF isotonic calibration; DCA.
  - **External cohort (NEW):** VitalDB (public, open API). Anchor adapted = operation start (opstart)
    because VitalDB has no intubation event. Feature window = [opstart−15 min, opstart]. Applied model
    = MOVER **core 53-column subset** (demographics + pre-anchor 6 vitals), reproduced (seed 12345),
    **no external refit or recalibration**. Results: n=3,735, events=214, prevalence 5.73%, AUPRC
    0.160 (0.129–0.202), AUROC 0.751 (0.713–0.784), Brier 0.179, predicted-risk mean 0.365.

## Independence discipline (MANDATORY)
You are reviewing this as if you have **never seen it**. Do NOT read ANY of these files:
`review/REVIEW_round*.md`, `review/A1_domain.md`, `review/A2_design.md`, `review/A3_provenance.md`,
`review/A4_venue.md`, `review/Round1_review_2026-10-19.md`, `review/_PANEL_BRIEF.md`,
`review/quality_gate_2026-10-20.md`, `review/reference_verification_2026-10-20.md`,
`review/journal_verification_2026-10-19.md`, `external_validation_plan.md`, any file under
`.workbuddy/`, `author_verification_statement.md`, `GITHUB_DEPOSIT_SOP.md`.
Also: do NOT read any other reviewer's output in `review/REVIEW_round4_2026-10-20/`.
Do not assume the manuscript is mature or has passed prior review. Treat it as a first submission.
Every judgement must come from text or source data you read yourself.
**Any claim in the manuscript that you CAN verify against a source file, you MUST verify** — not
recomputing a number means your review is incomplete for that item.

## Source-data pointers (read these yourself to verify)
- `results/s4_audit_trail.csv` — traceability ledger (metric, value, source_file, reproduce command).
- `results/s3_metrics.json` — model performance (AUPRC/AUROC/Brier + 95% CI) for 4 models × 2 splits.
- `results/s3_subgroups.json` — AUPRC by subgroup (sex/age/BMI) × 2 splits.
- `results/s3_feature_importance.json` — top XGBoost gain predictors.
- `results/s3_calib_dca.json` — calibration + DCA curves, and the MAP-only benchmark.
- `results/s2_data_quality.json` — leakage audit, coverage, demographics, BMI cleaning.
- `results/s1_outcomes_postanchor.json`, `results/s1_cohort.json` — outcome prevalences, cohort counts.
- `config/config.yaml` — internal design decisions.
- `config/config_vitaldb.yaml` — external design.
- `scripts/s3_models.py` — model training (verify fit/predict matrices, bootstrap resampling indices).
- `scripts/ext_build.py` — external pipeline (features/train/apply); verify apply does NOT refit.
- `scripts/ext_core_benchmark.py` — MOVER core 53-col benchmark.
- `results/ext/external_validation.json` — final external metrics (verify against raw below).
- `results/ext/core_benchmark.json` — MOVER core benchmark (verify internal core numbers).
- `results/ext/mover_core_train_metrics.json` — MOVER core train metrics.
- `results/ext/vitaldb_features_qa.json` — external QA (n, prevalence, missingness).
- `results/ext/vitaldb_predictions.csv`, `results/ext/vitaldb_labels.csv` — recompute external
  AUPRC/AUROC yourself from these two files (predicted probability + binary label).
- `manuscript/cover_letter_bmc_anesthesiology.md` — verify manuscript↔cover-letter consistency.

## Environment traps (so you don't burn budget rediscovering them)
- **Recording sparsity is the central constraint** (internal): non-invasive MAP in ~19.9% of
  case-minutes; 96.2% of non-empty segments are isolated single minutes. This caps performance.
- **BMI unit-entry errors** in source (height 2 cm, weight 839 kg → BMI ~2.2×10⁵) set to missing, not
  imputed; plausibility height 100–220 cm, weight 25–300 kg, BMI 10–80. Verify cleaning precedes
  BMI-feature derivation.
- **Anchor = "first Intubation" but 17.9% is "Surgery_start" proxy.** Reported; judge honesty.
- **Outcome window is anchor→OR_end (median 147 min), NOT config `horizon_minutes: 60`** (unused).
- **"Negative by construction":** 1,496 cases (8.9%) with <10 post-anchor measurements are D1-negative.
- **EXTERNAL anchor mismatch (NEW, important):** MOVER anchor = Intubation (induction). VitalDB has no
  intubation → anchor = opstart (operation START, which is AFTER induction+intubation). So the
  external "pre-anchor 15-min window" captures a DIFFERENT physiological phase than MOVER's
  pre-intubation window. Assess whether this is a fair/valid external validation or a confounded
  transfer, and whether it risks leakage or label–feature window overlap.
- **Core-vs-full model (NEW, important):** external validation used the **53-column core subset**, NOT
  the 205-column full model. The headline internal AUPRC 0.347 (full model) is NOT what was validated
  externally. Verify the manuscript distinguishes these clearly and does not let readers conflate them.
- **AUPRC not comparable across prevalence:** external prevalence 5.73% vs internal 15.55%. AUPRC
  anchors to prevalence; AUROC is the comparable discriminator. Verify the honest interpretation.
- **No external recalibration:** predicted-risk mean 0.365 vs observed 0.057 externally. The internal
  "well calibrated" claim must NOT be transferred; Brier 0.179 on a miscalibrated external model is
  interpretable only as discrimination-adjacent, not as calibration evidence.
- **External selection:** only VitalDB cases with an arterial MAP track (Solar8000/ART_MBP) were used
  (3,735 of 6,388). Assess selection bias and disclosure.

## Output contract (every item needs all four parts)
- 【Problem】 one sentence.
- 【Evidence】 pinned to `manuscript_v0.1.md:line` or table/section + exact numbers; numbers you cite
  must be ones you recomputed/verified yourself.
- 【Why it matters】 concrete effect on conclusions / credibility / acceptance.
- 【Specific fix】 a paste-ready English replacement sentence, OR an explicit spec for a new analysis.
  "Consider strengthening the discussion" is banned.

## Also required at the end of your file
- **§ Stands up (≥3)**: things you suspected but found correct — explicitly. This is a deliverable.
- **§ Questions for the authors**: what you need to know; do not guess answers.
- **§ What I actually checked**: files read, commands run, values recomputed vs the manuscript, with
  discrepancies stated.
- **§ Verdict**: Major / Minor / Accept (one-line rationale) for this manuscript's readiness.
