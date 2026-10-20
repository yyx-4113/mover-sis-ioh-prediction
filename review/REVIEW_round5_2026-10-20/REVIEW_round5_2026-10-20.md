# Round-5 Consolidated Editor Report — MOVER/SIS IOH Prediction

**Date:** 2026-10-20 · **Editor:** BMC Anesthesiology (acting) · **Manuscript:** `manuscript/manuscript_v0.1.md` (TRIPOD 2b)
**Panel:** 4 independent reviewers, each isolated from prior rounds and from each other.
**Verdicts:** A1 = Major revisions · A2 = Major revisions · A3 = Major revisions · A4 = Major revisions.
**Editor action:** all SEVERE and MAJOR findings addressed; gate re-run → **PASS**.

---

## 1. SEVERE (fixed, verified against primary source)
**A4 — Ref 19 (VitalDB) reference-integrity failure.** The citation carried a wrong DOI (`10.1038/s41597-022-01794-9`), wrong author list (`Lee S, Park J, Lee S, Park Y, Kim S, Kim T, et al.`) and an incomplete title (`a high-fidelity vital signs database`). Independently verified via WebSearch against the publisher page: the correct reference is **Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients. Sci Data. 2022 Jun 8;9(1):279. doi:10.1038/s41597-022-01411-5. PMID: 35676300; PMCID: PMC9178032.** Corrected in text and reference list.

## 2. MAJOR (all fixed)
| # | Source | Issue | Fix |
|---|--------|-------|-----|
| M1 | A4 | Ref 9 was self-referential ("This manuscript, Table 2") — improper Vancouver. | Removed the in-text `[9]` and the entry; renumbered 10→18. Reference count now 18 (gate updated + contiguity check added). |
| M2 | A4 | Figures 2, 3, 5 were defined but never cited in the body (BMC cite-all rule). | Added `(Figure 2)` at the 14-definitions description, and `Figure 3`/`Figure 5` sentences in the model-performance and predictor-importance paragraphs. |
| M3 | A4 | Cover-letter title misstated scope ("internal and external validation in the MOVER/SIS and VitalDB cohorts") and disagreed with the manuscript title. | Cover-letter title rewritten to match the manuscript exactly. |
| M4 | A1/A4 | Title said "sustained" while the body consistently uses "cumulative burden" (and explicitly contrasts the two). | Title harmonized to "cumulative intraoperative hypotension burden" in both manuscript and cover letter. |
| M5 | A2 | Terminology oscillated between "TRIPOD external validation", "transportability check", and unqualified "external validation". | Anchored the framing: external step is consistently described as a *transportability check* (anchor adaptation + feature-meaning shift disclosed in Methods/Limitations); the qualifier is mirrored in Abstract and Conclusions. |
| M6 | A2 | Abstract/Conclusions juxtaposed external AUROC 0.751 (53-feature) against the internal headline 0.722 (206-feature) — apples-to-oranges. | Abstract and Conclusions now compare to the like-for-like internal 53-feature value (0.698–0.710). |
| M7 | A2 | "consistency rather than superiority" (Results) contradicted "above"/"exceeding" (Discussion/Conclusions). | Discussion and Conclusions reworded to "in the same range as and overlapping the confidence interval of the internal 0.698–0.710". |
| M8 | A3 | **Temporal DCA threshold range was wrong.** Text claimed the temporal model was "positive up to 0.73 with a transient dip 0.59–0.66". Source `s3_calib_dca.json` shows temporal model NB is negative 0.46–0.66 and only briefly positive 0.66–0.74. | Results and Discussion DCA paragraphs corrected to the actual behaviour; cover letter "0.73 (temporal)" → "0.46 (temporal)". Added a gate sign-guard (temporal NB < 0 at 0.50; patient NB > 0 at 0.50) to prevent regression. |
| M9 | A3 | "treat all … strongly negative at these prevalences" is false at low thresholds (treat-all NB ≈ +0.06 at 0.10). | Reworded: treat-all is slightly positive at the lowest thresholds and strongly negative only at high thresholds (≈ −2.1 at 0.73). |
| M10 | A1 | D1 "aligned with the absolute-threshold framework of Salmasi" overstated — the ≥10-measurement / ≥30%-below rule is author-derived, not from Salmasi. | Reworded to adopt Salmasi's <65 mmHg absolute threshold while stating the cumulative-burden rule is our operational choice. |
| M11 | A1 | External AUROC 0.751 could be inflated by VitalDB's dense continuous arterial recording (defines outcome and supplies predictors more cleanly; BP autocorrelation under dense sampling). | Added Limitation #10 (recording-density confound on external discrimination). |
| M12 | A2 | D1 exposure-fraction assumes recorded MAP ≈ true MAP; under 19.89% density with 96.2% isolated single minutes this label-validity bias was never flagged. | Added Limitation #9 (outcome-label validity under sparse sampling). |
| M13 | A1 | "local recalibration at deployment" implied a VitalDB result could be transposed to induction-time use, ignoring the phase shift. | Reworded to "local recalibration on the deployment cohort's own anchor and recording regime". |

## 3. MINOR (noted, low priority)
- A4: "Authors' information" sub-item in Declarations is redundant with the title block — left as-is (BMC permits it).
- A1/A2: subgroup AUPRCs lack CIs and a multiplicity note — already caveated in Table 5 footnote ("exploratory … reduced event counts within strata"); BMI<18.5 instability flagged in text. No change.
- A2: external flow diagram (TRIPOD item 3/13) — the cohort construction is described in prose (6,388 → 3,735 → 214) and Table 7; a dedicated diagram was judged optional.

## 4. Verification
- `scripts/s5_gate.py` → **PASS**: abstract 346 words (≤350); 18 references, contiguous; 6 figures / 7 tables embedded in docx; 34 key numbers present; DCA@0.15 matches `s3_calib_dca.json` (patient 0.050, temporal 0.058); DCA sign-guard passes (temporal@0.50 = −0.0022, patient@0.50 = +0.0033).
- VitalDB reference re-checked against the publisher DOI landing page.

## 5. Editor assessment
No SEVERE or unresolved MAJOR issue remains. The manuscript is materially stronger: a reference-integrity defect (the external-validation cohort citation) is corrected, the DCA description now matches the source data, and the transportability framing is internally consistent. Remaining items are MINOR and do not block submission. **Recommendation: proceed to submission-ready state (Round-5 cleared).**
