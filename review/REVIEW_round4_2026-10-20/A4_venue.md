# Independent Venue / Reporting-Standard Audit — A4 (venue & TRIPOD+AI reporting)

**Manuscript:** `manuscript/manuscript_v0.1.md`
**Cover letter:** `manuscript/cover_letter_bmc_anesthesiology.md`
**Target journal:** BMC Anesthesiology · Article type (per manuscript): TRIPOD type 2b (development + internal + external validation)
**Reviewer role:** Journal editor + TRIPOD+AI reporting auditor (blinded peer review, round 4)
**Audit date:** 2026-10-20

This review judges (a) TRIPOD+AI type-2b reporting completeness, (b) BMC Anesthesiology format conformance, (c) ethics-statement defensibility, (d) manuscript↔cover-letter consistency, (e) data-availability statement consistency, (f) honesty/over-claim screening, and (g) the 0.973-competitor critique. Every judgement is pinned to text I read myself or to a number I recomputed from a source file.

---

## 1. TRIPOD+AI type-2b (external validation) reporting assessment

The author's own TRIPOD+AI checklist (`results/s4_tripod_ai.md`) marks items 1–20 as satisfied and flags item 21 (ethics/IRB) and 22 (data availability) as "⚠️ partial / needs author confirmation." On the *reporting* axis, the type-2b external-validation items are in fact present in the manuscript:

- **External cohort described:** `manuscript_v0.1.md:175–191` and Table 7 (`:438–449`) describe VitalDB, the anchor adaptation, the 53-feature transportable subset, and the no-refit/no-recalibration rule.
- **Transport of model WITHOUT refitting:** `:189` ("The MOVER core model (53 features, seed 12,345) was applied without any external refitting or recalibration").
- **Calibration in external cohort reported:** `:433–436` (mean predicted risk 0.37 vs observed 0.057; external Brier 0.179) and `:191` ("Calibration was assessed descriptively and was not updated on the external data").
- **Generalisability discussed:** Discussion `:504–507` and Limitations #1 `:534–543`.

So the *checklist* is formally satisfied. **However**, the scientific fairness of this external validation is compromised (see Issue C), and the reporting, while complete, does not fully insulate the claim from a reviewer who reads the anchor shift as a change of prediction problem. The items are reported but the validity caveat must be promoted from a softened limitation to an explicit framing decision.

---

## 2. BMC Anesthesiology format — recomputed checks

I recomputed the following programmatically (Python) against `manuscript_v0.1.md`:

- **Abstract word count:** 294 words total (Background 44, Methods 114, Results 106, Conclusions 30). **PASS** — ≤350 and under the author's own "350-word" claim.
- **Structured 4-part abstract:** Background/Methods/Results/Conclusions all present (`manuscript_v0.1.md:14,20,30,38`). **PASS.**
- **Keywords:** 7 keywords (`intraoperative hypotension; machine learning; clinical prediction model; mean arterial pressure; perioperative medicine; calibration; TRIPOD`, `:43–44`). **PASS** (3–10).
- **Declarations — all 7 subsections present:** Ethics approval & consent to participate (`:638`), Consent for publication (`:647`), Availability of data and materials (`:649`), Funding (`:662`), Competing interests (`:660`), Authors' contributions (`:665`), Acknowledgements (`:669`), plus BMC-required extras (Authors' information `:672`, Use of AI `:676`). **PASS** — no placeholders; "Consent for publication: Not applicable" is acceptable.
- **References:** 19 entries (`:683–729`), **exactly 19** as the brief predicted. All 19 are cited in text (verified: cited set = {1..19}, no orphans, no uncited entries). **PASS** on count and citation coverage.
- **Reference DOIs:** 15 of 19 carry a `doi:`. Missing: ref 9 (self-citation, acceptable), ref 10 (JMLR), ref 12 (NeurIPS), ref 16 (Anesthesiology 2013). See Issue E.
- **Figure legends:** Figures 1–6 all present and self-contained (`manuscript_v0.1.md:731–750`). **PASS.**
- **Table legends:** Tables 1–7 all present (`manuscript_v0.1.md:230,274,312,343,383,410,438`). **PASS.**
- **Title accuracy:** Manuscript title (`:1`) states "development and internal validation in MOVER/SIS **with external validation in VitalDB**" — accurate to content. **PASS** (but the cover-letter title is not — Issue A).

---

## 3. Issues (each with all four required parts)

### Issue A — MAJOR. Cover letter describes a different paper (TRIPOD type 2a, "no external validation") than the manuscript (type 2b, full VitalDB external validation).

【Problem】 The cover letter contradicts the manuscript on both study type and the presence of external validation, describing a type-2a internal-only study while the manuscript is a type-2b study with a complete VitalDB external validation.

【Evidence】
- Cover letter `cover_letter_bmc_anesthesiology.md:10` title: "…model development and **internal validation** in the MOVER/SIS cohort" — omits "external validation in VitalDB" present in the manuscript title `manuscript_v0.1.md:1`.
- Cover letter `:17`: "We deliberately present an **internal-validation study (TRIPOD type 2a)**, **explicitly state the absence of external validation**…"
- Cover letter `:12` (Summary) reports only internal results and makes **no mention** of VitalDB or external validation.
- Manuscript contradicts this directly: title `:1` (type 2b + external), abstract Methods `:25–27` ("the unchanged MOVER core model was also applied to the VitalDB arterial cohort … no refitting"), abstract Results `:35–36` ("Externally (VitalDB …) … AUROC 0.751"), Methods `:175–191`, Results `:425–449`.

【Why it matters】 A desk editor comparing the cover letter to the manuscript will see the two describe different studies. This is a submission-blocking inconsistency: it signals a stale cover letter, casts doubt on the authors' control of the submission, and will either trigger an immediate desk-reject or a mandatory "re-submit cover letter that matches the manuscript" cycle. It also undermines the TRIPOD type-2b claim at the very first editorial gate.

【Specific fix】 Rewrite the cover letter to match the manuscript. Replace `:10` title with the exact manuscript title and replace `:17` with: "We present a development-and-validation study reported as TRIPOD type 2b: internal validation in MOVER/SIS plus external validation of the unchanged 53-feature core model in the independent VitalDB arterial cohort (n = 3,735), where discrimination transferred (AUROC 0.751) but absolute probabilities did not and would require local recalibration." Add one sentence to the `:12` summary stating the external-validation result.

### Issue B — MAJOR. Ethics exemption is asserted as settled in the manuscript, but the cover letter says the IRB waiver letter is still "being obtained" — a documentation/desk-reject risk for BMC.

【Problem】 The manuscript asserts a definitive IRB exemption with no approval number, while the cover letter admits the waiver letter documenting that exemption is not yet in hand ("being obtained"), creating both an internal inconsistency and a BMC compliance risk.

【Evidence】
- Manuscript `manuscript_v0.1.md:641–645`: "Under the policy of the Institutional Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, retrospective research that uses exclusively pre-existing de-identified data obtained under a data use agreement is exempt from prospective ethical review and from individual consent; the study was conducted under this exemption and **no approval number is reported**."
- Cover letter `cover_letter_bmc_anesthesiology.md:23`: "…such research is exempt from prospective ethical review and individual consent; the study was conducted under this exemption, and a retrospective waiver letter documenting this basis is **being obtained** from the IRB. No approval number is reported because none was assigned."
- The author's own TRIPOD+AI checklist (`results/s4_tripod_ai.md:28`) flags item 21 ethics as "⚠️ 须由作者确认本单位伦理审批状态" (author must confirm IRB status) — confirming the status was unresolved.

【Why it matters】 BMC (Springer Nature) requires an ethics statement for any study involving human participants/data and, for exempt/retrospective de-identified work, normally expects the IRB's formal waiver/exemption confirmation (often the letter itself) to be supplied on request during peer review. Asserting exemption in the manuscript while the cover letter reveals the confirming letter is not yet obtained is inconsistent and invites a mandatory ethics-proof request or desk-reject if the letter cannot be produced. The "no approval number" wording is defensible only if the IRB's policy genuinely exempts and the exemption is confirmed in writing.

【Specific fix】 Before submission, obtain the IRB exemption/waiver letter and either (a) cite it: "The IRB confirmed this exemption in writing (reference [IRB ref/date]); no approval number was assigned as none is issued for exempt retrospective analyses," or (b) if BMC subsequently requires a number, provide the exemption reference. Make the manuscript and cover letter say the identical thing. Do not submit while the letter is only "being obtained."

### Issue C — MAJOR (validity/claim scope). The "external validation" changes the prediction problem (anchor shifted from intubation to operation start; arterial-only selection), so it is better framed as a transportability check than a clean type-2b external validation; the manuscript reports the caveats but under-sells their severity.

【Problem】 The external cohort's prediction origin is operation start (opstart), which is after induction/intubation, and only arterial-MAP cases were included — so the external task is not identical to the internal one, weakening the "external validation" label a TRIPOD-2b reviewer will scrutinise.

【Evidence】
- Manuscript `:180–184`: anchor adapted to opstart "the closest available analogue"; external cohort = cases with an arterial MAP track (Solar8000/ART_MBP or EV1000/ART_MBP), n = 3,735 of 6,388.
- Manuscript `:534–543` (Limitation #1) acknowledges the anchor adaptation and different recording architecture but frames the result as "transfer of discrimination."
- My recomputation from `results/ext/vitaldb_predictions.csv` + `vitaldb_labels.csv`: n=3,735, events=214, prevalence 0.0573, AUROC 0.7507 (manuscript 0.751, 95% CI 0.713–0.784), AUPRC 0.160 (0.129–0.202), predicted-risk mean 0.365 — i.e., predicted probabilities are ~6.4× the observed rate, confirming severe miscalibration that the authors themselves report.

【Why it matters】 TRIPOD+AI type-2b expects the *same* prediction problem transported to a new setting. Here the anchor (and thus the feature window and likely the label timing) shifted, and the population was restricted to arterial-monitored patients (a ~58% selection from 6,388). A reviewer may reasonably conclude this is a "model applied to a shifted anchor / selected subgroup" rather than a fair external validation, which would blunt the manuscript's central new claim. The numbers are honest and I verified them; the *framing* is the risk.

【Specific fix】 In the Abstract Results/Conclusions and the External-validation subsection (`manuscript_v0.1.md:425–449`), explicitly name this as a **transportability assessment under an adapted anchor and arterial-only selection**, e.g.: "Because VitalDB records no intubation event, the anchor was shifted to operation start and only arterial-MAP cases were eligible; this is a transportability check of the unchanged core model under a changed prediction origin and selected population, not a like-for-like external validation." Then state the implication (ranking transfers; probabilities and the absolute task do not) once, prominently.

### Issue D — MINOR (format/DOI). Reference 16 (Walsh et al., Anesthesiology 2013) is missing its DOI; refs 10 (JMLR) and 12 (NeurIPS) also lack DOIs, which BMC prefers for all citable items.

【Problem】 Three reference entries lack a DOI, and for ref 16 a DOI is definitely available, which BMC's reference standards discourage.

【Evidence】 `manuscript_v0.1.md:724–726` (ref 16) ends "Anesthesiology. 2013;119(3):507–515." with no `doi:`; refs 10 (`:708–709`, JMLR) and 12 (`:713–714`, NeurIPS) likewise. Refs 9 (self-citation), 10, 12, 16 are the four without DOIs; only ref 9 is legitimately DOI-less.

【Why it matters】 BMC/SN copyediting requires DOIs wherever the item has one; a missing DOI on a mainstream journal article (Anesthesiology) is a correctable formatting defect that will be flagged at proof stage and can delay production. JMLR and NeurIPS proceedings often lack DOIs (acceptable), but adding an arXiv/DOI where one exists is preferred.

【Specific fix】 Add to ref 16: "doi:10.1097/ALN.0b013e3182a10e26" (verify exact string). For ref 12, add the NeurIPS/arXiv DOI if available; for ref 10, JMLR articles are DOI-less by convention — leave as-is or add the JMLR URL.

### Issue E — MINOR (data-availability URL precision). The data-availability statement cites the GitHub repo root and "v1.0.0 reproduction package" but not an explicit release/tag URL.

【Problem】 The data-availability statement references a versioned package ("v1.0.0") but links only to the repository root, not to the specific `v1.0.0` release, so the version claim is not directly verifiable from the link.

【Evidence】 `manuscript_v0.1.md:654–655`: "available at https://github.com/yyx-4113/mover-sis-ioh-prediction (v1.0.0 reproduction package)"; cover letter `cover_letter_bmc_anesthesiology.md:24` repeats the same root URL. No `…/releases/tag/v1.0.0` link. The statement does **not** say "available on request" and correctly notes patient-level data are not redistributed under the DUA (`:652–658`) — this DUA/non-patient-data consistency is correct and should be kept.

【Why it matters】 BMC requires a specific, accessible data/code location; a versioned release tag makes the "every number is reproducible from v1.0.0" claim auditable. The current root link is acceptable but weaker than a pinned release; a reviewer verifying reproducibility will want the exact tag.

【Specific fix】 Change both occurrences to the explicit release URL: "https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.0". Keep the DUA/non-redistribution wording intact.

### Issue F — MINOR (internal legend/table consistency). Figure 5 legend says "Twenty-five highest-gain predictors" while Table 6 presents "Ten highest-gain predictors" — verify the figure actually plots 25 and reconcile the counts.

【Problem】 The Figure 5 legend and Table 6 disagree on how many predictors are shown, an internal inconsistency a copyeditor will flag.

【Evidence】 `manuscript_v0.1.md:748`: "**Figure 5. Predictor importance.** Twenty-five highest-gain predictors from XGBoost." vs `:410`: "**Table 6. Ten highest-gain predictors, XGBoost (patient-level split).**"

【Why it matters】 If Figure 5 genuinely plots 25 and Table 6 shows the top 10, the text is consistent but the divergent numbers look like an error; if Figure 5 actually shows 10, the legend is wrong. Either way it is a trivial-but-visible defect.

【Specific fix】 Confirm the figure content; if it shows 25, add to Table 6's intro "(full set of 25 shown in Figure 5)" so the counts are explicitly reconciled; if it shows 10, change the legend to "Ten highest-gain predictors."

### Issue G — PASS (no action). The 0.973 competitor critique is appropriately scholarly and does not leak into the abstract.

【Problem】 None — the critique of the near-perfect (AUROC 0.973) preprint is handled within scholarly-comment norms.

【Evidence】 Background `manuscript_v0.1.md:73–83` and Discussion `:487–513` cite the work as a preprint (ref 4, Preprints.org 2026) and explicitly disclaim a personal attack: "We do not question that analysis directly … we raise it as a methodological hazard rather than a claim about any specific report" (`:488–489`) and "We regard these as general methodological hazards … rather than criticisms specific to one report" (`:511–512`). The AUROC 0.973 figure appears only in Background/Discussion, never in the Abstract.

【Why it matters】 This is exactly the tone BMC and TRIPOD+AI expect when commenting on unpublished/preprint work; no desk-reject or tone risk.

【Specific fix】 No change required. Optionally soften "difficult to reconcile with the information content of the data" (`:77–78`) to "difficult to attribute to physiological signal under this recording density" to stay strictly descriptive — optional, not required.

---

## 4. Honesty-of-claims screen (subtle over-claims a desk editor would catch)

- **Full-model vs core-model conflation:** Checked and **cleared**. The abstract Methods `:25` explicitly says "the unchanged MOVER **core** model," the External-validation Methods `:185–189` restricts to the 53-feature subset, and Table 7's footnote `:447–449` states "the development manuscript headline (AUPRC 0.347, AUROC 0.722) is for the full 206-feature model. The external cohort had no refitting or recalibration." A reader cannot conflate the externally validated core with the internally headline full model. Good.
- **"Well calibrated" in the Abstract Conclusions `:38–39`:** Qualified immediately by "External validation confirmed transfer of discrimination but not of absolute probabilities" (`:39–41`), so it is correctly scoped to the internal cohort. Cleared.
- **External "validation" over-reach:** See Issue C — the label is technically reported but the anchor/population shift means it should be framed as transportability. This is the one place a careful desk editor could argue the claim slightly exceeds what was done, even though all numbers are honest.

---

## § Stands up (things I suspected but found correct)

1. **External metrics are honest and reproducible.** I recomputed AUROC 0.7507, AUPRC 0.160, predicted-risk mean 0.365, n=3,735, events=214, prevalence 0.0573, and bootstrap 95% CIs (AUROC 0.713–0.784; AUPRC 0.129–0.202) directly from `results/ext/vitaldb_predictions.csv` and `vitaldb_labels.csv`; all match `manuscript_v0.1.md:428–436` and `results/ext/external_validation.json` exactly. No number inflation.
2. **Abstract is within the 350-word limit and properly structured.** Recomputed at 294 words across the four mandated parts; the author's "≤350" claim holds.
3. **All 19 references are cited and there are no orphan/uncited entries** (cited set = {1..19}); reference count = 19 as expected.
4. **The core-vs-full model distinction is transparent** in both the abstract and Table 7, so the externally validated model is not conflated with the internal headline model.
5. **The 0.973 critique is scholarly and preprint-appropriate**, stays out of the abstract, and is framed as a general methodological hazard — no ad-hominem or result-leakage risk.
6. **Data-availability statement is DUA-consistent** (patient-level data not redistributed; code/aggregates on GitHub) and does not use "available on request."

## § Questions for the authors

1. Is the IRB exemption/waiver letter for this retrospective de-identified study now in hand, and can you provide its reference/date so the manuscript and cover letter can state it identically (Issue B)?
2. Given the external anchor was shifted from intubation to operation start and only arterial-MAP VitalDB cases were eligible (3,735 of 6,388), do you agree the result should be framed as a *transportability check* rather than a like-for-like external validation, and are you able to show the anchor shift does not itself drive the AUROC 0.751 (e.g., a sensitivity analysis holding the anchor definition constant)?
3. Does Figure 5 actually plot 25 predictors (reconciling with Table 6's 10), or should the legend read "ten"?
4. Can you confirm the GitHub `v1.0.0` release tag exists and is public, so the data-availability link can point to the exact release (Issue E)?
5. Will you add the missing DOI to ref 16 (and refs 10/12 where available)?

## § What I actually checked

- Read `manuscript/manuscript_v0.1.md` (full, 759 lines) and `manuscript/cover_letter_bmc_anesthesiology.md` (full, 38 lines).
- Read `results/s4_tripod_ai.md` (author's TRIPOD+AI checklist) to cross-check reported-item status.
- Read `results/ext/external_validation.json` and confirmed it matches the manuscript's external numbers.
- Recomputed, with Python (`C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe` + sklearn): external AUROC = 0.7507, AUPRC = 0.160, predicted-risk mean = 0.365, n = 3,735, events = 214, prevalence = 0.0573, bootstrap-1000 95% CIs AUROC 0.7133–0.7844 / AUPRC 0.1291–0.2021 — from `results/ext/vitaldb_predictions.csv` and `results/ext/vitaldb_labels.csv`. All match the manuscript.
- Recomputed with Python: abstract word count = 294 (Background 44 / Methods 114 / Results 106 / Conclusions 30); keyword count = 7; reference entries = 19; DOIs present = 15 of 19 (missing 9/10/12/16); cited reference set = {1..19} (no orphans); figure legends = {1,2,3,4,5,6}; table legends = {1,2,3,4,5,6,7}.
- Did NOT read any forbidden file (other reviewers' outputs, prior rounds, quality/reference/journal verification, briefs other than the round-4 panel brief, `.workbuddy/`, etc.).

## § Verdict

**Major.** The manuscript itself is well-formatted, honest, and internally consistent on nearly every BMC/TRIPOD+AI axis (abstract, keywords, declarations, references count/citation, figure/table legends, transparent core-vs-full distinction, scholarly competitor critique). The blocking problems are extrinsic to the science: (1) the cover letter describes a different study (type 2a / "no external validation") than the type-2b manuscript, which is a submission-blocking inconsistency (Issue A); (2) the IRB exemption is asserted in the manuscript while the cover letter admits the waiver letter is still "being obtained," a BMC ethics-proof/desk-reject risk (Issue B); and (3) the external-validation claim should be reframed as a transportability check under a shifted anchor and selected population (Issue C). Once the cover letter is resynced, the IRB documentation is secured, and the external claim is honestly reframed — plus the minor DOI/URL/legend fixes (D–F) — the manuscript is suitable for peer review. No recomputation revealed any fabricated or inflated performance number.
