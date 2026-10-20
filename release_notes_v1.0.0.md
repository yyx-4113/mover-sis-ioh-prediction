# v1.0.0 — Reproduction package

Snapshot of the analysis code, configuration, audit trail, and aggregate result files from which every number in the manuscript *"Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: model development and internal and external validation"* (BMC Anesthesiology submission) is generated.

## Scope
This repository is the verbatim reproduction package. Patient-level data are **not** redistributed, in accordance with the MOVER data use agreement; per-case derived files are regenerable from the MOVER source by running `scripts/run_all.py`.

## What is included
- `scripts/` — full pipeline (s1 outcomes → s5 gate), plus `scripts/ext_*` for the VitalDB external validation
- `results/` — aggregate artifacts only (audit trail, calibration/DCA, external-validation metrics); no patient-level CSV
- `manuscript/` — BMC Anesthesiology-formatted manuscript (v0.1) and the generated `.docx`
- `MANIFEST.csv` — file checksums for integrity verification

## Key results (this snapshot)
- **Internal** (MOVER/SIS, n = 16,861; prevalence 15.55%): XGBoost AUPRC 0.347 (AUROC 0.722); temporal validation AUPRC 0.339
- **External** (VitalDB arterial cohort, n = 3,735; prevalence 5.73%): AUPRC 0.160 (AUROC 0.751)
- See `results/ext/external_validation.json` for the external-validation metrics.

## Ethics
Retrospective analysis of pre-existing de-identified data obtained under a data use agreement; exempt from prospective ethical review, no approval number reported.
