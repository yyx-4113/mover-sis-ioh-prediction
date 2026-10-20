# TRIPOD+AI (2024) checklist — 01 SIS intraoperative hypotension prediction

> Status legend: **Met** = satisfied / backed by a product file; **Partial** = partly met / needs author follow-up; **To-do** = pending (manuscript stage).
> Each item cites "manuscript section / product file" for pre-submission verification.

| # | TRIPOD+AI item | Status | Location / evidence |
|---|---|---|---|
| 1 | **Title**: identified as a prediction-model study (with ML) | Met | manuscript_v0.1.md title |
| 2 | **Abstract**: structured, with data source, model, performance | Met | structured abstract completed (within 350 words) |
| 3 | **Objectives**: clear clinical question and prediction target | Met | protocol §1; post-anchor cumulative IOH burden |
| 4 | **Data sources**: source, period, retrieval | Met | `s1_cohort.json`; SIS EMR nine tables, 2015-11 to 2018-10 |
| 5 | **Eligibility**: inclusion / exclusion criteria | Met | protocol §2; `s1_cohort.json` (cohort waterfall and self-consistency) |
| 6 | **Outcome**: definition and ascertainment | Met | protocol §3; 14-definition sensitivity matrix `s1_outcomes_postanchor.json` |
| 7 | **Predictors**: all candidate predictors, definitions, timing | Met | `s2_feature_dictionary.json` (206 features, domain / source / window per feature) |
| 8 | **Temporal / leakage**: predictors must precede prediction time | Met (strong) | `s2_data_quality.json.leakage_audit`: every domain `max_used_time_minus_anchor ≤ 0`, ALL_PASS = True |
| 9 | **Missing data**: handling | Met | native NaN for tree models; median imputation + missing indicators for logistic (`s3_models.py`) |
| 10 | **Statistical / ML methods**: model family, hyperparameters, software versions | Met | `s3_metrics.json` (fixed seed / hyperparameters); config `runtime` records versions |
| 11 | **Sample size / EPV**: justification | Met | n = 16,861, events 2,622 (adequate EPV); see `s1_outcomes_postanchor.json` |
| 12 | **Validation**: internal / external strategy | Met | patient-level (primary) + temporal (secondary); `s3_metrics.json` |
| 13 | **Performance measures**: primary metric and uncertainty | Met | primary AUPRC; 1,000-bootstrap 95% CI; `s3_metrics.json` |
| 14 | **Calibration**: assessment and method | Met | OOF isotonic; `s3_calib_dca.json` (logit-slope 0.9087, intercept −0.1831) |
| 15 | **Clinical utility**: decision curve / net benefit | Met | DCA; `s3_calib_dca.json.dca` |
| 16 | **Participants**: participant characteristics described | Met | `s2_data_quality.json` (demographics / BMI / procedure-group distributions) |
| 17 | **Model specification**: final model obtainable | Met | scripts + products fully reproducible; code repository recommended |
| 18 | **Subgroups**: subgroup performance | Met | `s3_subgroups.json` (sex / age / BMI) |
| 19 | **Limitations**: limitations (incl. bias sources) | Met | protocol §9; report §8 (Limitations 1–14) |
| 20 | **Interpretation**: clinical interpretability | Met | `s3_feature_importance.json` (MAP-dominated, internally consistent) |
| 21 | **Ethics / IRB**: approval and consent | Partial | retrospective de-identified data; **author must confirm institutional IRB status** |
| 22 | **Data availability**: data and code obtainable | Partial | products complete; **real repository URL / DOI required** (never "available on request") |
| 23 | **Funding / COI** | To-do | author to supply |
| 24 | **Registration**: study registration | Partial | protocol versioned; three design decisions signed-off and frozen (2026-10-20); pre-registration number recommended before submission |

## Blocking pre-submission gaps (2)
1. **Ethics / IRB status** must be confirmed in writing by the author (item 21): retrospective waiver / filing letter (no number, no date; route B honestly declared).
2. **Public data / code** must resolve to a real repository URL (item 22); "available on request" is prohibited (real named-repository URL already used).

## Closed
- **Three design decisions signed-off and frozen (2026-10-20)**: primary outcome D1, prediction anchor Intubation, procedure-group mapping table.
- Manuscript passed an independent 4-reviewer panel (Round-6) and a consistency gate (13/13: abstract ≤350 words, 18 contiguous references, 8 tables / 6 figures in docx, no placeholders, anchor & external blocks present, all 16 product-derived model metrics present, DCA net benefit @0.15 = 0.051 / 0.058 with correct sign, Limitations 1–14). Round-7 verification corrected the abstract and Table 4 to exact product values (baseline AUPRC 0.233, LightGBM AUPRC 0.338).
