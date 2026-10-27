# MOVER/SIS Intraoperative Hypotension Prediction — Reproduction Package

This repository contains the analysis code, configuration, audit trail, and aggregate
result files for the manuscript:

> Prediction of sustained intraoperative hypotension burden from data available at
> anaesthesia induction: model development and internal validation in the MOVER/SIS cohort
> Yongxin Yang (single author). Target journal: BMC Medical Informatics and Decision Making.

## Data access

The analysis uses the **MOVER** (Medical Informatics Operating Room Vitals and Events
Repository) database, University of California Irvine, distributed through the UCI Machine
Learning Repository (doi:10.24432/C5VS5G). Access requires a signed Data Use Agreement (DUA)
with UCI. **Patient-level data are not redistributed in this repository.** The raw MOVER extract
must be obtained by the user under the DUA and placed at `data_raw/_sis_emr_x/EMR/` relative to
the workspace root (see `config/config.yaml`).

## What is included

- `config/config.yaml` — single source of truth: paths, random seed, outcome definitions,
  prediction anchor, surgical-group keyword map, and model hyperparameters.
- `scripts/` — the full pipeline:
  - `s1_cohort.py` — cohort construction + outcome derivation (engine v1.1.0, 1-minute grid).
  - `s2_features.py` — feature engineering (BMI, surgical grouping, early-window vitals).
  - `s3_models.py` — modelling + patient-level / temporal validation, curves, calibration, DCA.
  - `s4_report.py` / `s4_figures.py` — tables, figures, TRIPOD+AI checklist.
  - `s5_docx.py` / `s5_gate.py` — manuscript docx conversion and wordcount/consistency gate.
  - `run_all.py` — orchestrator (runs s1 → s2 → s3 → s4).
  - `audit/` — Round-1 review audit scripts (independent reproduction of every headline number).
- `results/` — aggregate result files (JSON / small CSV) and figure PNGs. The audit trail
  `results/s4_audit_trail.csv` maps every reported number to its producing artefact and the exact
  command that reproduces it.
- `manuscript/` — manuscript source (`manuscript_v0.1.md`, `manuscript_v0.1.docx`).
- `protocol/`, `review/` — pre-specified protocol and review records.
- `MANIFEST.csv` — SHA-256 checksums of all tracked result files.
- `workflows/release.yml` — GitHub Actions CI workflow (syntax-checks the pipeline scripts and
  validates `config/config.yaml`). **Note on location:** the file is stored here rather than the
  canonical `.github/workflows/` path because the repository was published from a constrained
  environment that blocks writes to `.github/workflows/`. To enable CI, copy it to
  `.github/workflows/release.yml`.

## What is NOT included (and why)

The following patient-level derived files are **not redistributed** because the DUA does not
permit redistribution of patient-level data:

- `results/s1_anchor.csv`
- `results/s1_labels.csv`
- `results/s1_labels_postanchor.csv`
- `results/s2_features.csv`

They are fully regenerable from the MOVER source under the DUA by running the pipeline (step 4
below), so reproducibility is preserved without redistributing protected data.

## Reproduction

**Requirements:** Python 3.13.12 with pandas 2.3.3, numpy 2.4.6, scikit-learn 1.9.0,
xgboost 3.4.1, lightgbm 4.7.0.

1. Obtain MOVER under the DUA; place the nine EMR CSVs under `data_raw/_sis_emr_x/EMR/`.
2. (Optional) adjust `config/config.yaml` `paths.workspace_root` / `sis_emr_dir` if your layout
   differs.
3. Run the pipeline:
   ```
   python scripts/run_all.py
   ```
   This executes s1 → s2 → s3 → s4 and regenerates all `results/` artefacts.
4. Verify reported numbers against `results/s4_audit_trail.csv` and `MANIFEST.csv`.

To inspect the already-computed aggregate results and figures without re-running, open the files
under `results/` directly.

## Key design decisions (frozen)

- **Primary outcome D1** — exposure-fraction definition: at least 10 MAP measurements after the
  prediction anchor, of which at least 30% are below 65 mmHg (aligned with Salmasi et al., 2017).
- **Prediction anchor** — first recorded Intubation event; Surgery_start used as proxy when no
  intubation event exists (18.0% of cases). The outcome window is the remainder of surgery
  (anchor → OR_end; median 147 min).
- **Surgical groups** — 12 keyword-mapped categories with a controlled fuzzy fallback
  (residual OTHER = 2.1%).
- **Validation** — patient-level 80/20 split (primary); temporal split (secondary). Primary metric
  AUPRC; out-of-fold isotonic calibration; decision-curve analysis; 1000-bootstrap CIs. Seed =
  12345.

## Caveats

Sparse non-invasive blood pressure (nMAP recorded in 19.89% of case-minutes; 96.2% of non-empty
segments are isolated single minutes) caps achievable performance and makes sustained-duration
definitions unidentifiable. No ASA, no pre-operative baseline BP (0.8% coverage), no
post-operative outcomes in the source. Single-centre (UCI). Internal validation only — external
validation is required before clinical use. See `manuscript/manuscript_v0.1.md`
(Discussion → Limitations) and `NOTES_zh.md`.

## Citation

See `CITATION.cff`.
