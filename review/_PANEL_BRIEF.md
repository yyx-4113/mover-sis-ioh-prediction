# Independent Review Panel — Brief (REVIEW round 1, 2026-10-20)

## Manuscript under review
- **File:** `manuscript/manuscript_v0.1.md` (full text, ~619 lines). A single-author clinical
  prediction-model paper: *"Prediction of sustained intraoperative hypotension burden from data
  available at anaesthesia induction: model development and internal validation in the MOVER/SIS
  cohort."* Target journal: **BMC Anesthesiology**. Article type: TRIPOD type 2a (development +
  internal validation).
- **Claim in one line:** a gradient-boosted model using only pre-induction/anchor data predicts a
  cumulative hypotension-burden outcome (D1) with AUPRC ≈ 0.35 / AUROC ≈ 0.72, modest but non-null,
  well calibrated, honestly reported under a leakage audit, with an explicit critique of a competing
  preprint claiming AUROC 0.973 on the same resource.
- **Design snapshot (for context only; verify everything yourself):**
  - Source: MOVER/SIS (UCI), 9 linked tables, de-identified, DUA.
  - Cohort: 19,114 → 17,103 → **16,861** analysed adult cases.
  - Anchor: first Intubation (82.0%) else Surgery_start (18.0%).
  - Outcome D1: ≥10 post-anchor MAP measurements, ≥30% <65 mmHg; prevalence 15.55% (n=2,622).
  - 206 predictors, truncated at anchor. 4 models. Patient-level (primary) + temporal (secondary) split.
  - Primary metric AUPRC; 1,000 bootstrap CIs; OOF isotonic calibration; DCA.

## Independence discipline (MANDATORY)
You are reviewing this as if you have **never seen it**. Do NOT read any of these files:
`REVIEW_*.md`, `RESPONSE_*.md`, `REVISION_*.md`, `Round1_review_2026-10-19.md`, `STATUS.md`,
`STATUS*.md`, any file under `.workbuddy/`, `author_verification_statement.md`,
`GITHUB_DEPOSIT_SOP.md`, `journal_verification_2026-10-19.md`, `reference_verification_2026-10-20.md`,
and **do not read any other reviewer's output in this `review/` directory**.
Do not assume the manuscript is mature or has passed prior review. Treat it as a first submission.
Every judgement must come from text or source data you read yourself.
**Any claim in the manuscript that you CAN verify against a source file, you MUST verify** — not
recomputing a number means your review is incomplete for that item.

## Source-data pointers (read these yourself to verify)
- `results/s4_audit_trail.csv` — the author's claimed traceability ledger (metric, value, source_file, reproduce command).
- `results/s3_metrics.json` — model performance (AUPRC/AUROC/Brier + 95% CI) for all 4 models × 2 splits.
- `results/s3_subgroups.json` — AUPRC by subgroup (sex/age/BMI) × 2 splits.
- `results/s3_feature_importance.json` — top XGBoost gain predictors.
- `results/s3_calib_dca.json` — calibration (raw/calibrated Brier, slope, intercept) + full DCA net-benefit curves for patient & temporal splits.
- `results/s2_data_quality.json` — leakage audit per domain, coverage, demographics, procedure groups, BMI cleaning.
- `results/s1_outcomes_postanchor.json` — 14 outcome-definition prevalences.
- `results/s1_cohort.json` — cohort counts, anchor counts.
- `config/config.yaml` — design decisions (primary_id D1, anchor, 12-group keywords).
- `scripts/` — the pipeline (s1_cohort.py, s2_features.py, s3_models.py, s4_report.py, s5_docx.py). Read only if needed to judge implementability; do not re-run unless you must.

## Environment traps (so you don't burn budget rediscovering them)
- **Recording sparsity is the central constraint:** non-invasive MAP is recorded in only ~19.9% of
  case-minutes; 96.2% of non-empty recording segments are isolated single minutes. This caps
  achievable performance and makes sustained-duration outcome definitions effectively unmeasurable.
- **BMI unit-entry errors in source** (height as low as 2 cm, weight up to 839 kg → BMI ~2.2×10⁵)
  were set to missing (not imputed); plausibility ranges height 100–220 cm, weight 25–300 kg,
  BMI 10–80. The manuscript reports this; verify the cleaning was applied before deriving BMI-based
  features/predictors, not only recorded.
- **Anchor = "first Intubation" but 18% is "Surgery_start" proxy** (no intubation recorded). The
  manuscript reports this; judge whether it is handled honestly.
- **Outcome window is anchor→OR_end (median 147 min), NOT the config `horizon_minutes: 60`**, which
  is unused. Verify the manuscript describes the actual behaviour.
- **"Negative by construction" cases:** 1,496 cases (8.9%) with <10 post-anchor measurements are
  classified D1-negative. Verify this is disclosed and its implications discussed.

## Output contract (every item needs all four parts)
- 【Problem】 one sentence.
- 【Evidence】 pinned to `file:line` of the manuscript, or table/section + exact numbers; numbers you
  cite must be ones you recomputed/verified yourself against the source files above.
- 【Why it matters】 concrete effect on conclusions / credibility / acceptance.
- 【Specific fix】 a paste-ready English (or Chinese-if-requested) replacement sentence, OR an
  explicit spec for a new analysis (variables, strata, output columns). "Consider strengthening the
  discussion" is banned.

## Also required at the end of your file
- **§ Stands up (≥3)**: things you suspected but found correct — explicitly. This is a deliverable.
- **§ Questions for the authors**: what you need to know; do not guess answers.
- **§ What I actually checked**: files read, commands run, values recomputed vs the manuscript, with
  discrepancies stated.
- **§ Verdict**: Major / Minor / Accept (with one-line rationale) for this manuscript's readiness.
