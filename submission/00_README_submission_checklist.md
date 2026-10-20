# Submission bundle - BMC Anesthesiology

**Submission site (SNAPP, Springer Nature Article Processing Platform):** https://submission.springernature.com/new-submission/12871/3
**Journal home page:** https://link.springer.com/journal/12871
**ISSN:** 1471-2253
**Springer Nature journal ID:** 12871

## How to reach the submission site

Open the journal home page and click **Submit your manuscript**; or paste the
direct link above. Either route lands on the Springer Nature sign-in page, which
states "continue with your submission to BMC Anesthesiology".

Sign in with **ORCID** (recommended, it links the submission to
0009-0004-9698-6552), or with a Springer Nature account, or with Google. The
account is created on first use.

Do **not** use an `editorialmanager.com` link for this journal. BMC titles have
moved off Editorial Manager onto SNAPP, and the old Editorial Manager address no
longer accepts new submissions.

Everything needed for the online submission is in this folder.
Upload order in the SNAPP submission wizard:

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
