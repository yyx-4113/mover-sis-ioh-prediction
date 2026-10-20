# Submission bundle - BMC Anesthesiology

**Submission site (Editorial Manager):** https://www.editorialmanager.com/BANE
**Journal home page:** https://bmcanesthesiol.biomedcentral.com/
**ISSN:** 1471-2253

Everything needed for the online submission is in this folder.
Upload order in the Editorial Manager wizard:

| Step in wizard | File in this folder |
|---|---|
| 1. Article type | Original Article (Research) |
| 2. Manuscript | `01_Manuscript.docx` |
| 3. Cover letter | `02_Cover_letter.docx` |
| 4. Figures (upload individually) | `03_Figures/` |
| 5. Additional files | `04_Additional_file_1_audit_trail.csv`, `05_Additional_file_2_TRIPOD_AI.docx` |

Figures included (300 dpi):
   - Fig1_cohort.png
   - Fig2_definitions.png
   - Fig3_pr_roc.png
   - Fig4_calib_dca.png
   - Fig5_importance.png
   - Fig6_external_transportability.png

Additional file 1 has 250 rows: every number reported in the manuscript,
the result file that produced it, and the command that reproduces it.

## Points to check before clicking Submit

- Author name carries **no academic title** (no MD/PhD); ORCID 0009-0004-9698-6552 is
  linked in the manuscript title page.
- Ethics statement: retrospective analysis of de-identified data under a signed data
  use agreement; exempt under the author institution's IRB policy; **no approval number
  is claimed** because none was assigned. Do not invent one.
- Data availability points at the public reproduction package release tag, not
  "available on request".
- Reporting checklist (TRIPOD+AI 2024) is attached as Additional file 2 and is in English.
- The cover letter and the manuscript report the same numbers (external AUROC 0.744,
  AUPRC 0.158, mean predicted risk 0.36, external Brier 0.176, n = 3,735, events 214).

## Reproducibility

Regenerate this bundle at any time with:

    python scripts/s7_submission_pack.py

It reads only from `manuscript/` and `results/` and never edits a source file.
