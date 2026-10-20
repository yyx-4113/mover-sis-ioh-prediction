# Round-6 Independent Panel Brief — MOVER/SIS IOH Prediction

**Date:** 2026-10-20 (evening)
**Manuscript:** `manuscript/manuscript_v0.1.md` (target: BMC Anesthesiology; TRIPOD+AI type 2b — development with internal and external validation)
**Cover letter:** `manuscript/cover_letter_bmc_anesthesiology.md`
**Project root:** `D:/2026.10/Mover数据库/directions/01_SIS术中低血压预测/`

## Independence discipline (mandatory — read first)

You are reviewing this manuscript **as if it were a first submission**.

**Forbidden to read (do not open these files at any point):**
- `review/REVIEW_round1*` … `review/REVIEW_round5*` (all directories and files)
- `review/REVIEW_round4_2026-10-20/`, `review/REVIEW_round5_2026-10-20/` and every `A1..A4_*.md` anywhere under `review/`
- `review/Round1_review_2026-10-19.md`, `review/journal_verification_2026-10-19.md`, `review/reference_verification_2026-10-20.md`
- `STATUS.md`, `NOTES_zh.md`, `GITHUB_DEPOSIT_SOP.md`, `author_verification_statement.md`, `external_validation_plan.md`
- Other reviewers' outputs in `review/REVIEW_round6_2026-10-20/` — you work alone.

**Do not assume the manuscript is mature.** It has survived prior internal rounds; your value is finding what still survives them. Every judgement must come from text or source data you read yourself. Any claim in the manuscript that you CAN verify, you MUST verify — a review that only reads prose is incomplete.

Do not mention what tools you use; write review comments only.

## What the manuscript currently claims (verify these against the text and artefacts — do not trust this list)

- **Cohort:** 19,114 screened → 17,103 (cohort layer) → **16,861 (modelling layer)**; median OR duration 167 min; 3,559,993 one-minute OR observations.
- **Outcome D1:** ≥10 post-anchor MAP measurements AND ≥30% of them <65 mmHg; prevalence 15.55% (2,622/16,861); 1,496 cases (8.9%) negative-by-construction.
- **Anchor:** first Intubation (13,834; 82.1%), Surgery start proxy (3,027; 17.9%); anchor median 15 min (IQR 11–24) after OR start; post-anchor window median 147 min (p5–p95 49–440).
- **Performance (patient-level split, primary):** XGBoost AUPRC 0.347 (0.309–0.387), AUROC 0.722 (0.697–0.745); LightGBM 0.337/0.724; full logistic 0.301/0.707; baseline (age/sex/BMI) 0.234/0.626. Temporal split: XGBoost 0.339/0.733. MAP-only logistic AUPRC 0.284.
- **Calibration:** OOF isotonic Brier 0.191→0.119, slope 0.909, intercept 0.008 (patient); temporal 0.194→0.122, slope 0.934, intercept 0.006.
- **DCA:** net benefit @0.10 = 0.079/0.085; @0.15 = 0.050/0.058; positive to ≈0.58 (patient); temporal positive 0.66–0.74 only, negative 0.46–0.66; treat-all ≈0.06 @0.10, ≈−2.1 @0.73. MAP-only incremental net benefit 0.013 @0.10 and @0.15.
- **Subgroups (Table 5):** women 0.357 > men 0.299; age <50 0.380, 50–64 0.324, ≥65 0.186; BMI <18.5 0.616 (n=98 test / 512 cohort, flagged unstable; temporal 0.382).
- **Recording density:** nMAP non-null in 19.89% of case-minutes (SBP 19.99%, DBP 19.95%); HR 94.8%; SpO2 96.1%; 637,188 non-empty MAP segments, 96.2% single-minute; median 33 MAP/case over OR window (p5–p95 12–90); median 3 MAP readings in 15-min pre-anchor window (IQR 2–4).
- **External (VitalDB, transportability check):** 6,388 → 3,735 eligible; 214 events (5.73%); +214 negative-by-construction (conditional prevalence 6.1%, 214/3,521); unchanged 53-feature core model: AUPRC 0.160 (0.129–0.202), AUROC 0.751 (0.713–0.784), Brier 0.179; mean predicted risk 0.37 vs observed 0.057. Internal same-53-feature model: AUROC 0.698 (patient) / 0.710 (temporal), AUPRC 0.321/0.314.
- **Top features (XGBoost gain):** mean pre-anchor MAP 175.5; max MAP 75.2; anchor-is-intubation 72.2; intubation event 69.1; OR-start→anchor interval 64.1; fraction below 65 52.9.
- **14 candidate definitions (Table 2):** O1 15 (0.09%), O2 54 (0.32%), O3 2 (0.01%), O4 27 (0.16%), S1 1,214 (7.20%), B1 7,240 (42.94%), B2 5,192 (30.79%), B3 1,159 (6.87%), D1 2,622 (15.55%), D2 91 (0.54%), E1 3,770 (22.36%), E2 11,091 (65.78%), O5 1,292 (7.66%), O6 572 (3.39%).
- **Ethics:** exemption declaration (pre-existing de-identified data + DUA, institution IRB policy, no approval number, no waiver-letter language).

## Where things live

- Manuscript: `manuscript/manuscript_v0.1.md` (+ `.docx`)
- Cover letter: `manuscript/cover_letter_bmc_anesthesiology.md`
- Pipeline: `scripts/s1_cohort.py`, `s2_features.py`, `s3_models.py`, `s4_report.py`, `s4_figures.py`, `s5_docx.py`, `s5_gate.py`, `ext_*.py`
- Config: `config/config.yaml`, `config/config_vitaldb.yaml`
- Artefacts: `results/*.json|csv` (s1_*, s2_*, s3_*, s4_audit_trail.csv), `results/ext/` (external), `results/figs/`, `results/s3_figs/`
- Audit scripts: `scripts/audit/a1..a6_*.py`
- Source data (read-only): `D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/` (9 CSVs); VitalDB extracts in `data_vitaldb/`
- Python: `C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe` (venv with pandas/sklearn/xgboost/lightgbm at `C:\Users\Administrator\.workbuddy\binaries\python\envs\default\`)

## Environment traps for this data source (do not rediscover these the hard way)

- MOVER `Ht/Wt` contain unit-entry errors (height as low as 2 cm, weight up to 839 kg → BMI up to 2.2×10^5). The pipeline sets implausible values to NaN (Ht 100–220, Wt 25–300, BMI 10–80). Any BMI analysis must reproduce this filter.
- `patient_ventilator.csv` time column format is `%m/%d/%y %H:%M` (not ISO).
- `s1_outcomes_postanchor.json` has non-outcome top-level keys (`primary_id`, `engine_version`, `anchor_source_counts`, `note`); filter `isinstance(v, dict) and 'definition' in v`.
- Outcome engine uses a 1-minute grid where NaN counts as interruption. An older version used `dropna` and inflated prevalence 3.9–41.3×; verify the current engine does not compress the time axis.
- pandas: `df._name` is reserved (use `df["_name"]`); `DataFrame.update()` silently drops new columns.
- If you recompute from raw CSVs, expect the pipeline to take minutes; use the artefacts for cross-checks first.

## Review dimensions (one primary focus each)

- **A1 — Clinical / domain (anaesthesiology, intraoperative hypotension):** Is D1 clinically defensible as stated? Is the "cumulative burden over remainder of surgery" task coherent with the anchor? Are the interpretation, subgroup narrative, limitations and conclusions clinically honest? Any must-cite literature missing (e.g., IOH definitions, consensus, prior MOVER-based work)?
- **A2 — Study design / TRIPOD+AI methodology:** sample-size/event-per-variable adequacy for 206 predictors; split strategy; the transportability framing (defensible or must be downgraded to exploratory?); missing-data handling; negative-by-construction rule; subgroup claims; leakage-audit completeness; spectrum-bias accounting.
- **A3 — Statistics / provenance / reproducibility:** every number in the manuscript must trace to an artefact. Recompute at least: (i) cohort waterfall 19,114→17,103→16,861 from `results/s1_cohort.json`; (ii) D1 prevalence and the Table-2 14-definition counts from `results/s1_labels_postanchor.csv` or `s1_outcomes_postanchor.json`; (iii) XGBoost AUPRC/AUROC + bootstrap CI from `results/s3_metrics.json`; (iv) calibration numbers from `results/s3_calib_dca.json`; (v) external numbers from `results/ext/`; (vi) recording-density statistics from `results/s1_data_quality.json` / `s2_data_quality.json`. Also read `scripts/s3_models.py` and `scripts/ext_*.py` for estimator/CI correctness, and run `scripts/s5_gate.py` yourself. Report any double-rounding, unit mismatch, CI-method mismatch, or number that appears in the manuscript but in no artefact.
- **A4 — Journal fit / reporting / ethics (BMC Anesthesiology):** section structure vs BMC requirements (Background/Methods/Results/Discussion/Conclusions; Declarations seven subheads; abstract ≤350 words four-paragraph; Vancouver numbering); cover letter vs manuscript consistency; TRIPOD+AI checklist honesty (`results/s4_tripod_ai.md` / Additional file 2); English quality; anything that would trigger a desk edit. Check figure legends and table captions against the actual figure/table content.

## Output contract (all four parts mandatory for every finding)

- **【Problem】** one sentence
- **【Evidence】** pinned to file:line, or table/section + exact numbers; numbers you cite must be ones you recomputed yourself
- **【Why it matters】** concrete effect on conclusions / credibility / acceptance
- **【Specific fix】** a paste-ready English replacement sentence, or an explicit spec for a new analysis (variables, strata, output columns)

"Consider strengthening the discussion" is banned. Also required:
- **§ Stands up (≥3 items, with evidence)** — things you suspected but verified as correct. This is a deliverable, not filler.
- **§ Questions for the authors** — what you need to know; do not guess answers.
- **§ What I actually checked** — files read, commands run, values recomputed vs the manuscript's, with the discrepancy stated.

## Deliverable

Write your report to `review/REVIEW_round6_2026-10-20/A<n>_<role>.md` with: executive summary, graded findings (SEVERE / MAJOR / MINOR), the four-part contract per finding, and a final verdict (Accept-as-is / Minor revisions / Major revisions / Reject) with the single change that would most improve the paper.
