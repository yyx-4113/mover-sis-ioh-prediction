# A4 — Journal fit / formatting / ethics review (BMC Anesthesiology)

**Reviewer role:** A4 — venue fit, BMC structure, Declarations, Vancouver references, ethics-statement compliance, cover-letter alignment, English/formatting.
**Round:** 5 (residual-risk pass; prior rounds not re-litigated).
**Files read:** `manuscript/manuscript_v0.1.md`, `manuscript/cover_letter_bmc_anesthesiology.md`, `review/REVIEW_round5_2026-10-20/_PANEL_BRIEF.md`.
**Date:** 2026-10-20.

---

## Executive summary

The manuscript largely satisfies BMC Anesthesiology's structural skeleton — the five IMRaD sections are present, the abstract is a correct four-paragraph (Background/Methods/Results/Conclusions) block at ~340 words, there are 7 keywords, and all 7 required Declarations subheads are present and (except one wording nuance) correctly populated. The data-availability URL is consistent between manuscript and cover letter, and no "available on request" language remains. The ethics statement is internally consistent with the cover letter and contains no leftover waiver-letter phrasing. Spot-check of **Ref 16 (Walsh 2013) passes**: its DOI `10.1097/ALN.0b013e3182a10e26` and author list are correct.

However, three residual risks survive and would trigger desk edits or a reviewer query:

1. **SEVERE — Ref 19 (VitalDB) is wrong on every citable field.** The DOI `10.1038/s41597-022-01794-9` does not resolve to the real paper; the correct DOI is `10.1038/s41597-022-01411-5`. The author list `Lee S, Park J, Lee S, Park Y, Kim S, Kim T, et al.` does not match the actual authors (`Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW`), and the title omits "multi-parameter". This is a broken, partly fabricated citation for the study's external-validation cohort — a reference-integrity failure.
2. **MAJOR — Cover-letter title misstates the external-validation scope** and disagrees with the manuscript title.
3. **MAJOR — Figures 2, 3 and 5 are never cited in the text body**, breaching BMC's "all figures/tables must be cited" rule (3 of 6 figures).

Two further MAJOR/MINOR items: a self-referential reference (Ref 9 = "This manuscript, Table 2") is an improper Vancouver entry, and the ethics exemption is self-asserted without noting that the IRB determination is documented/on file. None of these are fatal; all are fixable with targeted edits.

**Verdict: Major revisions** (one SEVERE citation error plus structural fixes; not rejectable as-is, but not accept-as-is).

---

## Findings table

| Severity | Location | Issue | Concrete fix |
|---|---|---|---|
| SEVERE | Ref 19, lines 758 (and in-text [19] at line 180) | VitalDB citation is wrong on DOI, authors and title. Manuscript gives `doi:10.1038/s41597-022-01794-9`; authors `Lee S, Park J, Lee S, Park Y, Kim S, Kim T, et al.`; title "VitalDB, a high-fidelity vital signs database in surgical patients". The real paper is Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity **multi-parameter** vital signs database in surgical patients. Sci Data. 2022;9(1):279. **doi:10.1038/s41597-022-01411-5**. | Replace the entire Ref 19 entry with: `Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients. Sci Data. 2022;9(1):279. doi:10.1038/s41597-022-01411-5.` Verify the DOI resolves. |
| MAJOR | Cover letter title, line 10; vs manuscript title, line 1 | Cover-letter title reads "model development and internal and external validation in the MOVER/SIS and VitalDB cohorts", which (a) misstates scope — external validation was performed **only in VitalDB**, internal validation only in MOVER/SIS — and (b) disagrees with the manuscript title, which correctly separates them ("development and internal validation in MOVER/SIS with external validation in VitalDB"). | Align the cover-letter title to the manuscript title verbatim, or at minimum change to "development and internal validation in MOVER/SIS with external validation in VitalDB" and drop "model". Titles must match exactly. |
| MAJOR | Figure legends lines 767–777 (Fig 2, Fig 3, Fig 5); text body | Figures 2, 3 and 5 are defined in the legend block but **never cited** in the Results/Discussion prose. Text cites only Figure 1 (line 109), Figure 4 (lines 386, 606) and Figure 6 (line 455). BMC requires every figure/table to be explicitly referenced. | Add citations: Fig 2 near line 278 ("…span a very wide prevalence range (Table 2, Figure 2)"); Fig 3 near line 344 ("…on the patient-level split (Table 4, Figure 3)"); Fig 5 near line 417 ("…dominated (Table 6, Figure 5)"). |
| MAJOR | Ref 9, lines 736 (and in-text [9] at line 133) | Ref 9 is "This manuscript, Table 2 (all 14 definitions computed for every case; see Additional file 1)" — a self-referential entry that is not a proper bibliographic item and violates Vancouver. The in-text "[9]" is redundant with the explicit "Table 2". | Delete Ref 9 and the in-text "[9]" at line 133 (keep "(Table 2)"). Renumber refs 10–19 → 9–18 and update all in-text citations [10–12] (line 227) and the rest accordingly. Alternatively, if a software/checklist pointer is intended, cite Additional file 1 narratively instead of as a numbered reference. |
| MINOR | Declarations, lines 701–708 | The 7 required subheads (lines 667–699) are **all present and correctly populated** — compliant. Two extra subheads appear: "Authors' information" (701–703, redundant with the title-page author block) and "Use of artificial intelligence" (705–708). The AI statement is good (BMC now requires it); "Authors' information" is optional/redundant. | No mandatory change. Optional: move "Authors' information" into a separate optional block or delete, since author details already appear on the title page. Keep the AI-use statement. |
| MINOR | Ethics statement, lines 667–674 (esp. line 674) | Statement is internally consistent and matches the cover letter (line 23); no approval number, no waiver language — good. Two residual nuances: (i) line 674 "All procedures were conducted in accordance with the Declaration of Helsinki" sits awkwardly with a no-consent, de-identified analysis; (ii) the IRB exemption is self-asserted ("Under the policy of the IRB… is exempt") with no note that a documented exemption determination is on file. | Reword line 674 to "This retrospective analysis of de-identified data was deemed exempt by the IRB of [institution] under its policy for secondary-use de-identified data; the exemption determination is documented and available on request. No identifiable data were accessed, and the study was conducted in accordance with the Declaration of Helsinki and applicable local regulations." |
| MINOR | Title, line 1; body usage | Title calls the endpoint "sustained intraoperative hypotension burden", but the outcome D1 (lines 126–130) and the entire body consistently call it a "cumulative burden" (exposure-fraction) definition, explicitly contrasting it with "sustained" duration definitions (lines 132–138, 278–305, 539–540). "Sustained" in the title is therefore mildly inconsistent with the method. | Change title to "…cumulative intraoperative hypotension burden…" to match the body, or add "cumulative" alongside "sustained". Consistency improves discoverability and avoids reviewer pushback. |
| MINOR (note) | Ref 8, lines 734–735 | Data citation "MOVER (Medical Informatics Operating Room Vitals and Events Repository). UCI Machine Learning Repository. doi:10.24432/C5VS5G." lacks an author/corporate author and access date; acceptable to BMC as a data citation but stylistically thin. | Optional: format as a data citation with corporate author "University of California, Irvine" and an accessed date, e.g. "University of California, Irvine. MOVER… UCI Machine Learning Repository [dataset]. 2023. doi:10.24432/C5VS5G." |

---

## Detailed notes (supporting the table)

### 1. BMC structural compliance — PASS (with the exceptions above)
- **IMRaD sections:** Background (L50), Methods (L93), Results (L229), Discussion (L470), Conclusions (L639) — all present. ✓
- **Abstract:** four bold paragraphs — Background (L14), Methods (L20), Results (L30), Conclusions (L40). Gate reports 340 words (≤350). ✓
- **Keywords:** 7 terms (L45–46), within 3–10. ✓
- **Declarations:** all 7 BMC-required subheads present and populated (L667–699). Consent for publication = "Not applicable" (L676) — appropriate, no identifiable images/data. ✓
- **Data availability:** URL `https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.0` is identical in manuscript (L684) and cover letter (L24). No "available on request" anywhere. ✓
- **6 figures / 7 tables:** counts correct; all 7 tables are cited (Table 1 L234, 2 L278, 3 L309, 4 L344, 5 L390, 6 L417, 7 L440/455). Figures 2/3/5 are the gap (see MAJOR above).

### 2. Reference spot-checks
- **Ref 16 (Walsh 2013) — PASS.** DOI `10.1097/ALN.0b013e3182a10e26` confirmed correct via PubMed (PMID 23835589; Anesthesiology 2013;119(3):507–15). Author list "Walsh M, Devereaux PJ, Garg AX, et al." (3 + et al. for a 9-author paper) is correct Vancouver. ✓
- **Ref 19 (VitalDB) — FAIL (SEVERE).** See table. The correct citation is Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW, *Sci Data* 2022;9(1):279, doi:10.1038/s41597-022-01411-5. The submitted DOI `…01794-9` does not resolve to this article; the author surnames supplied do not match the real authors. Because VitalDB is the external-validation cohort, a wrong citation here undermines the paper's provenance claim and will be caught by the journal's reference check.

### 3. Cover-letter vs manuscript alignment
- Ethics paragraph (cover L23) matches manuscript L667–674 exactly — good; no waiver-letter residue. ✓
- Data-availability paragraph (cover L24) matches manuscript L678–687 — good. ✓
- **Title mismatch (MAJOR):** the only material divergence is the title; the cover-letter version both adds "model" and rephrases the validation scope in a way that implies external validation also occurred in MOVER/SIS. This should be corrected before submission.

### 4. Ethics-statement policy check (BMC)
BMC's editorial policy permits an IRB exemption for retrospective/secondary analyses of de-identified data *provided the exemption is stated*. The manuscript does state it and matches the cover letter. This is compliant in principle. The only residual exposure is that the exemption is asserted from institutional policy rather than accompanied by a note that a documented exemption determination exists; adding one sentence (see MINOR fix) pre-empts an editorial request for evidence. No approval number and no waiver language is the correct posture for this study type.

---

## Verdict

**Major revisions.**

Rationale: one SEVERE reference-integrity defect (Ref 19 — wrong DOI, authors and title for the external-validation cohort) that must be corrected before the manuscript can pass the journal's reference check, plus a cover-letter title that misstates validation scope and disagrees with the manuscript, three uncited figures, and an improper self-referential reference. None are conceptual or ethical blockers; all are mechanical fixes. After correcting Ref 19, aligning the cover-letter title, adding the three figure citations, and removing/re-numbering Ref 9, the manuscript would meet BMC Anesthesiology's formatting and venue-fit bar. The ethics statement is otherwise compliant and consistent with the cover letter.
