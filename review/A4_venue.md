# Venue / Reporting-Standard Review — A4 (Independent Venue Reviewer)

**Role:** BMC Anesthesiology handling-editor lens + reporting-standard (TRIPOD+AI / BMC policy) auditor
**Manuscript:** "Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: model development and internal validation in the MOVER/SIS cohort" (single author, Y. Yang)
**Article type declared:** clinical prediction model, TRIPOD type 2a (development + internal validation)
**Target journal:** BMC Anesthesiology (BMC / Springer Nature; fully open access; anesthesiology & perioperative prediction scope)
**Review status assumed:** first submission.

---

## 1. BMC Anesthesiology format compliance

### 1.1 Abstract length and structure — COMPLIANT
【Problem】 None material.
【Evidence】 Structured abstract with explicit **Background / Methods / Results / Conclusions** subheadings (manuscript lines 14–41). Word count ≈ 305 words (Background ≈57 + Methods ≈115 + Results ≈96 + Conclusions ≈37), **within the 350-word limit**.
【Why it matters】 BMC Anesthesiology permits structured abstracts; staying under 350 words avoids automatic technical-check rejection.
【Specific fix】 No change required. (Optional: trim the Methods sub-anchor percentages ("82.0%; … 18.0%") if later cuts are needed — not necessary now.)

### 1.2 Keywords — COMPLIANT
【Problem】 None.
【Evidence】 Lines 43–44: "intraoperative hypotension; machine learning; clinical prediction model; mean arterial pressure; perioperative medicine; calibration; TRIPOD" = **7 keywords**, within the 3–10 range and MeSH-aligned.
【Why it matters】 Within policy.
【Specific fix】 No change.

### 1.3 Declarations subheadings — COMPLIANT (all present)
【Problem】 None — the 9 standard BMC subheadings are all present and correctly named:
- Ethics approval and consent to participate (502)
- Consent for publication (511)
- Availability of data and materials (513)
- Competing interests (524)
- Funding (526)
- Authors' contributions (529)
- Acknowledgements (533)
- Authors' information (536)
- **Use of artificial intelligence** (540) ✅ present — required by BMC/SN since 2024.
【Why it matters】 Completeness of Declarations is a routine technical-check gate.
【Specific fix】 No structural change. (Substantive fix needed inside the Ethics entry — see §2.)

---

## 2. Ethics declaration — HIGH RISK (likely technical-check / editorial hold)

【Problem】 The ethics statement asserts that approval is *not required* and that *no determination was sought*:
> "…research using exclusively pre-existing de-identified data does not require prospective ethical approval; **a formal determination was therefore not sought, and no approval number is reported.**" (lines 505–508)

【Evidence】 manuscript lines 502–509, especially 507–508. The approving/exempting body is named only in general ("the policy of the Institutional Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine"), but **no committee decision, waiver letter, or reference number is cited**.

【Why it matters】 Springer Nature / BMC Anesthesiology policy requires that *either* (a) an IRB/ethics-committee approval number be given, *or* (b) a **formal exemption/waiver be stated with the name of the committee that granted it and its reference**. A self-assertion that "we did not seek a determination" is the weakest possible posture: it is the *authors' interpretation* of the policy, not a documented institutional exemption. This is a classic reason for a query at technical check, and in the absence of any IRB documentation it can become a rejection.

【Specific fix】 Obtain a written exemption/waiver from the named IRB and revise the statement to the BMC-safe form, e.g.:
> "This study was exempted from prospective ethical review by the Ethics Committee of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine (Exemption/Letter ref: [X]) because it used pre-existing, de-identified data obtained under a signed data use agreement; the requirement for informed consent was waived on the same basis. The study was conducted in accordance with the Declaration of Helsinki."
If the committee can only issue a verbal/policy-based exemption with no number, attach the policy citation or the IRB's written response as supporting documentation at submission and name the committee explicitly. **Do not submit with "no determination sought."** This is the single most likely blocker and should be resolved before submission.

---

## 3. Data availability — MOSTLY COMPLIANT (minor tightening recommended)

【Problem】 The statement is acceptable in substance but could be tightened for BMC's data-policy expectations.
【Evidence】 Lines 513–522. It correctly: (i) names the source (MOVER/UCI) and the access path (DUA + URLs/DOI); (ii) states patient-level data cannot be redistributed under the DUA; (iii) points to a GitHub reproduction package (v1.0.0) holding code, config, audit trail, and aggregate result files; (iv) notes the per-case matrices are regenerable under DUA.
【Why it matters】 BMC requires that data underpinning the results be available *or* a valid restriction be clearly stated with the access path. Restricted patient-level data due to a DUA is an accepted restriction. The only soft points are (a) GitHub alone lacks a persistent DOI/archive, and (b) "minimal dataset" is not explicitly labelled as deposited.
【Specific fix】 (a) Deposit the reproduction package (or at least the aggregate/result files + MANIFEST) in a persistent repository with a DOI (Zenodo/Dryad/OSF) in addition to GitHub, or add a Zenodo archival DOI to the GitHub repo; (b) explicitly state "The minimal dataset supporting the conclusions (aggregate result files and audit trail) is available in [repository/DOI]; individual-level data require a data use agreement from UCI." No ethical issue, but improves technical-check smoothness.

---

## 4. Novelty vs existing MOVER literature + orphan references — MAJOR

### 4.1 Refs [14] and [15] are never cited — ORPHAN REFERENCES
【Problem】 References 14 (Chiu et al., BMC Anesthesiol. 2025;25:351) and 15 (Cheun et al., BMC Anesthesiol. 2026;26:334) are listed in the reference section but **appear nowhere in the body text**.
【Evidence】 Grep of the manuscript body for `[14]`, `[15]`, `[16]` returned **no matches** (only `[13]` is cited, at line 432). The reference list itself (lines 587–592) contains both entries.
【Why it matters】 Both are BMC Anesthesiology papers built on the *same MOVER resource* — i.e., the two most directly comparable published studies in the very journal being targeted. An orphan reference is a formatting/copyedit defect that BMC's technical check will flag, but more importantly it signals the manuscript **never engages the existing MOVER prediction literature in this journal**, leaving the novelty/jurisdiction question unanswered.
【Specific fix】 Either (a) **cite** refs 14 and 15 in the Background ("Relation to previous work") and explicitly differentiate this study (endpoint = cumulative IOH burden at the induction anchor with an explicit leakage audit and recording-density analysis, versus ICU-admission prediction [14] and postoperative-complication prediction [15]); or (b) if they are not genuinely relevant, **delete them from the reference list**. Do not leave them as orphans. Reference [16] (Walsh 2013) is likewise uncited — same treatment.

### 4.2 Differentiation from published MOVER work is unaddressed
【Problem】 The "Relation to previous work" section (lines 423–440) engages only [4] (Alrantisi preprint), [5], [13], and [6]; it does **not** position the work against the two in-journal MOVER prediction papers [14][15].
【Why it matters】 Without this positioning, an editor/reviewer may perceive redundancy with MOVER-based prediction papers already published in BMC Anesthesiology, or assume the literature was not canvassed — a plausible reject/major-revision reason.
【Specific fix】 Add 2–3 sentences in Background or Discussion stating how this study differs (different clinical question — anticipation at induction vs intraoperative monitoring/index; different endpoint — cumulative burden vs ICU admission / postoperative complications; added value — 14-definition sensitivity matrix, leakage audit, recording-density quantification). Cite [14][15] there.

---

## 5. TRIPOD+AI reporting-standard adherence — GAP

【Problem】 The manuscript states it is "reported in accordance with TRIPOD+AI [7]" (line 91) but **no TRIPOD+AI checklist is provided as a supplementary file**, and the Additional files section lists only "Additional file 1" (audit trail; lines 615–618).
【Evidence】 Lines 91, 569 (ref 7 = TRIPOD+AI statement), and the Additional files section (615–618) which contains no reporting-checklist item.
【Why it matters】 BMC/SN editorial policy expects the relevant reporting-guideline checklist to be submitted as supplementary material and to be completed item-by-item. Missing checklists are routinely requested at technical check and can delay peer review.
【Specific fix】 Complete the TRIPOD+AI (2024) checklist, mapping each item to a manuscript section/table, and add it as **Additional file 2**. State in the Methods ("Study design and data source") that the completed checklist is provided as supplementary. Given the manuscript is TRIPOD type 2a, the "model updating / external validation" items should be explicitly marked N/A with rationale.

---

## 6. Competing interests / Funding / AI disclosure — COMPLIANT

【Problem】 None.
【Evidence】 Competing interests: "The author declares no competing interests" (524). Funding: "no grant or monetary support" (526). AI disclosure: present and appropriately worded — states an LLM assisted with code/drafting but all design decisions, results and final text are the author's sole responsibility, and the assistant is not an author (540–543).
【Why it matters】 All three are mandatory BMC declarations and are correctly satisfied.
【Specific fix】 No change. (The AI statement is a model of good practice and should be retained verbatim.)

---

## 7. Reference-list hygiene — DEFECT (must clean before submission)

【Problem】 The reference list contains **internal provenance/verification annotations** that are inappropriate for a submitted manuscript.
【Evidence】 e.g. line 550 "*(verified 2026-10-19)*"; line 554 "*(verified 2026-10-20; PMID 32065827)*"; line 560 "*(unrefereed single-author preprint by Alrantisi KMM; posted 17 Mar 2026; verified 2026-10-20)*"; similar tags on refs 1,2,3,4,5,6,7,8,10,11,12,13.
【Why it matters】 These are audit/traceability notes from the author's internal pipeline; their presence in the reference list looks unprofessional and suggests the manuscript was not finalised for submission.
【Specific fix】 Strip every "*(verified …)*" / "*(unrefereed …)*" annotation from all 16 references before submission. Keep only the standard bibliographic citation (author, title, journal, year, vol, pages, DOI).

### 7.1 Reference formatting — minor
【Problem】 References use full journal names rather than NLM/Vancouver abbreviations (e.g., "J Mach Learn Res", "J Clin Monit Comput" are abbreviated but "Anesthesiology", "JAMA", "BMJ" are not).
【Why it matters】 BMC copyediting will normalise this; not a blocker, but inconsistent style invites queries.
【Specific fix】 Apply consistent Vancouver/NLM abbreviation across all references (or follow the journal's most recent published articles as the house style). Confirm every DOI resolves (refs 4 and 13 are preprints — verify the DOI/URL is live and correctly formatted: Preprints.org uses `https://doi.org/10.20944/preprints202603.1373.v1`; medRxiv uses `https://doi.org/10.1101/2026.08.26.26361468`).

---

## 8. Desk-reject risk assessment

Potential desk-reject triggers evaluated:

1. **Scope mismatch** — NO. ML prediction of intraoperative hypotension from a perioperative vitals repository is squarely within BMC Anesthesiology's scope (perioperative prediction models are core content).
2. **Missing ethics approval** — RISK (conditional). Not an automatic desk reject if an IRB exemption/waiver letter can be supplied, but "no determination sought" is the kind of statement that triggers an immediate editorial hold. *Critical.* (See §2.)
3. **Redundancy with published MOVER papers (Chiu 2025; Cheun 2026)** — RISK (medium). Currently unaddressed because [14][15] are orphan references and never compared against. Fixable via citation + differentiation (§4); if left unaddressed, a reviewer could recommend reject on novelty grounds.
4. **Over-claiming vs internal-validation-only** — NO. The manuscript is commendably restrained ("modest but non-null discrimination", "External validation is required before clinical application", Limitations item 1). This *reduces* desk-reject risk substantially and is a strength.
5. **Missing reporting checklist** — RISK (low–medium). BMC routinely requests TRIPOD+AI checklist at technical check; not a desk reject but a predictable delay (§5).
6. **Orphan references / leaked provenance annotations** — RISK (low). Will be caught at technical check/copyedit, not a desk reject (§4.1, §7).
7. **Single-author, no external validation** — NO as a desk-reject basis. BMC Anesthesiology publishes single-author and internally-validated prediction models; the honest framing mitigates this. The single-author structure is unusual but not disqualifying.

**Overall desk-reject probability: LOW–MODERATE.** The scientific content is sound and honestly reported; the dominant risks are *administrative* (ethics documentation) and *presentation* (orphan references, missing checklist, leaked annotations), not substantive.

---

## 9. Scope-fit and journal-style notes
- **Title** is long but informative and matches BMC's descriptive style; acceptable.
- **Abstract** matches journal style (structured, ≤350 words).
- **Single-author "Authors' contributions"** stating "YY is the sole author" is acceptable to BMC but the editor may ask whether any statistical/methodological oversight was obtained; consider a one-line note that the analysis was independently reproducible from the deposited pipeline (already supported by Additional file 1).
- The **recording-density / leakage-audit framing** is a genuine methodological strength and differentiates the work from the "near-perfect AUROC" literature; lean into this in the cover letter to the editor.

---

## § Stands up (≥3 things done well / that hold up)
1. **Honest, non-over-claimed framing** throughout (explicit "modest but non-null", mandatory external validation before clinical use, 8-item Limitations). This is exactly what BMC editors want from a type-2a prediction paper and materially lowers reject risk.
2. **Internal numerical consistency verified.** Every reported figure I could trace matches the audit trail / cohort JSON / config: cohort 19,114→16,861 with exclusions 8/1,632/371/242 (s1_cohort.json; audit rows 2–7); anchor 13,834/3,027; outcome D1 2,622 (15.55%); 206 features; leakage audit all-pass (max interval 0.00 min); XGBoost patient AUPRC 0.347/AUROC 0.722, LightGBM 0.337/0.724, full logistic 0.301, baseline 0.234; calibration Brier 0.191→0.119, slope 0.909, intercept 0.008; all subgroup AUPRCs and predictor gains match (s4_audit_trail.csv rows 48–94). The reproducibility claim is credible.
3. **Use of artificial intelligence declaration** is present, correctly worded, and a model example for BMC's 2024 policy.
4. **Complete Declarations subheadings** (all 9, including AI) — passes the routine technical-check gate.
5. **Leakage audit + 14-definition sensitivity matrix** is a real contribution that addresses a documented problem in perioperative ML (selection/label leakage, incomparable endpoints) and should be foregrounded in the editor cover letter.

## § Questions for the authors
1. Can you provide a **formal IRB exemption/waiver letter (with a reference number)** from the Second Affiliated Hospital of Fujian University of TCM? If yes, the ethics statement can be made BMC-compliant; if no, how do you propose to satisfy the "name the exempting committee + reference" requirement?
2. Why are **refs [14] (Chiu 2025) and [15] (Cheun 2026)** — both MOVER-based prediction papers in BMC Anesthesiology — listed but never cited? Are they genuinely not comparable, or should they be cited and differentiated in the text?
3. Is a **TRIPOD+AI checklist** available (completed, item-by-item)? If not, will you prepare it as Additional file 2?
4. Will you **deposit the reproduction package in a persistent repository with a DOI** (Zenodo/OSF) alongside GitHub, to satisfy BMC's data-availability expectations?
5. The "verified 2026-10-xx" annotations in the references — were these intended for internal tracking only? They must be removed before submission; confirm.

## § What I actually checked
- Read the full manuscript (manuscript_v0.1.md, 619 lines).
- Verified abstract word count and structure; keyword count; Declarations subheadings.
- Cross-checked every quantitative claim I could trace against `results/s4_audit_trail.csv`, `results/s1_cohort.json`, and `config/config.yaml` (cohort flow, anchors, outcome D1, 206 features, leakage audit, model metrics, calibration, subgroups, predictor gains, temporal split configuration) — all consistent.
- Grep-confirmed that references [14], [15], [16] are **not** cited in the body (orphan references); only [13] is cited.
- Confirmed TRIPOD+AI is claimed but no checklist is provided as supplementary (only Additional file 1, the audit trail).
- Assessed ethics/data/AI declarations against BMC/SN policy; assessed desk-reject risk across scope, ethics, novelty, over-claiming, and reporting-standard dimensions.

## § Verdict
**Major revision (not a desk reject), with the ethics documentation as the critical blocker.**

Rationale: The science is internally consistent, methodologically careful, and commendably honest about its limits — well suited to BMC Anesthesiology's scope and standards. The blocking and near-blocking issues are administrative/presentational rather than substantive:
- **Must fix (blocker):** ethics statement must move from "no determination sought" to a named-committee exemption/waiver with a reference (§2).
- **Must fix:** resolve orphan refs [14][15][16] — cite-and-differentiate the in-journal MOVER papers, or delete (§4).
- **Should fix:** provide a completed TRIPOD+AI checklist as supplementary (§5); strip the "verified …" provenance annotations from all references (§7); deposit a DOI-archived reproduction package (§3).
- **Minor:** reference-style normalisation (§7.1).

Desk-reject risk rating: **LOW–MODERATE** — driven almost entirely by the ethics-statement wording, which is fully remediable by supplying IRB documentation. With the above changes, the manuscript is a reasonable candidate for peer review at BMC Anesthesiology.
