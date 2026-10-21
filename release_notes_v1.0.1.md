# v1.0.1 — Reproduction package (revised)

Snapshot of the analysis code, configuration, audit trail, and aggregate result files from which every number in the manuscript *"Prediction of intraoperative hypotension exposure from data available at anaesthesia induction: development and internal validation in MOVER/SIS with an external transportability check in VitalDB"* (BMC Anesthesiology submission) is generated.

## Scope
This repository is the verbatim reproduction package. Patient-level data are **not** redistributed, in accordance with the MOVER data use agreement; per-case derived files are regenerable from the MOVER source by running `scripts/run_all.py`.

## Changes from v1.0.0

The **analysis is unchanged** — every statistic in this package is bit-identical to v1.0.0 (same code, same config, same seed). v1.0.1 is a manuscript-framing and package-hygiene revision following an independent four-expert review (2026-10-20):

1. **Outcome naming (endpoint honesty).** The primary outcome D1 is an *exposure-fraction* definition (≥30% of recorded post-anchor MAP readings below 65 mmHg among ≥10 readings), not a cumulative time below threshold. Title, abstract, discussion and cover letter re-framed accordingly; the discussion now reports decision-curve net benefit with verified magnitudes (below 0.01 at decision-relevant thresholds 0.10–0.30; at most 9.9×10⁻⁵ at 0.58) instead of threshold-range claims.
2. **Package hygiene (T0-8).** Removed from the public tree: internal review files (`review/`), working status/notes (`STATUS.md`, `NOTES_zh.md`, `external_validation_plan.md`), an intermediate profiling artefact (`results/_round1_subgroup_n.json`), an unused IRB-waiver template that contradicted the ethics statement (`manuscript/irb_waiver_request_template.md`), and per-case derived CSVs that the release notes had promised not to ship (`results/s2_features_halfopen.csv`, `results/s3_test_predictions_*.csv`, `results/s6_external_grid_labels.csv`, `scripts/results/`). These remain available in the working directory; the published tree ships aggregate artefacts only.
3. **Release-note figures corrected.** External metrics now read AUPRC 0.158 / AUROC 0.744 (verified against `results/ext/external_validation.json`; v1.0.0 notes carried stale 0.160 / 0.751 values). Title wording aligned with the manuscript.
4. **MANIFEST rebuilt** with a generator script (`scripts/build_manifest.py`) covering scripts, config, protocol, aggregate results, figures and manuscript — 60 files with SHA-256 checksums (v1.0.0 shipped 28).

## Key results (this snapshot)
- **Internal** (MOVER/SIS, n = 16,861; prevalence 15.55%): XGBoost AUPRC 0.347 (AUROC 0.722); temporal validation AUPRC 0.339 (AUROC 0.733)
- **Restricted evaluable cohort** (n = 15,365; conditional prevalence 17.06%): AUPRC 0.401 (AUROC 0.735)
- **External transportability check** (VitalDB arterial cohort, n = 3,735; prevalence 5.73%): AUPRC 0.158 (AUROC 0.744) — discrimination transferred, calibration did not
- See `results/ext/external_validation.json`, `results/s6_sensitivity.json` and `results/s4_audit_trail.csv` for the full traceable set.

## Ethics
Retrospective analysis of pre-existing de-identified data obtained under a data use agreement; exempt from prospective ethical review, no approval number reported.
