# A1 — Clinical / Domain Review (Anesthesiology, Intraoperative Hypotension)
**Round 5 — Residual-risk review of `manuscript_v0.1.md` + `cover_letter_bmc_anesthesiology.md`**
Reviewer focus: clinical plausibility of D1, interpretation of the external VitalDB AUROC 0.751, honesty of Limitations, and over/under-claim in Conclusions.

---

## Executive summary

This is an unusually transparent perioperative-prediction manuscript. The leakage audit, the 14-definition outcome sensitivity analysis, the MAP-only benchmark, and the explicit "transportability check, not like-for-like validation" framing are genuine strengths that prior rounds clearly established. **No fatal (SEVERE) clinical flaw survives:** the model is correctly described as modest, the calibration failure is openly stated, and the dominant-predictor-is-current-BP caveat is repeated in three places.

However, four **MAJOR** interpretation/framing risks remain that a clinician reader (or an editor skimming the abstract) could misread, plus four **MINOR** clarity issues. The core problem is a persistent tension between the careful Methods/Limitations language ("transportability check … adapted anchor … not like-for-like") and the upbeat Abstract/Conclusion language ("external validation confirmed," "retained discrimination"). The external AUROC 0.751 is also presented as if it measures *model* transportability, without acknowledging that VitalDB's **continuous arterial** recording measures both the MAP-based outcome and the MAP-based predictors far more cleanly than MOVER's **sparse intermittent NIBP**, which can inflate the external AUROC through better outcome ascertainment and through BP autocorrelation rather than through genuine generalisability.

**Verdict: Major revisions** — the fixes are mostly textual/conceptual, but the external-result interpretation and the endpoint's clinical grounding need substantive rewording before the claims are safe for a clinical readership.

---

## Findings table

| Severity | Location | Issue | Concrete fix |
|---|---|---|---|
| MAJOR | Lines 126–130 (Outcome D1) | "Aligned with the absolute-threshold framework of Salmasi et al." overstates clinical grounding; the ≥30%-of-≥10-readings rule is author-invented and sampling-dependent under sparse NIBP. | Reword to share only the 65 mmHg threshold with Salmasi/POQI; state the 30%/10 cut-points are pragmatic (event-count adequacy, Table 2), not clinically derived; add that the fraction is sensitive to *when* sparse readings occur. |
| MAJOR | Lines 445–455, 524–526 | External AUROC 0.751 framed as "ranking transferred" without noting the **measurement-density confound**: VitalDB arterial MAP makes both the outcome (≥30% fraction) and the MAP predictors cleaner, and MAP is autocorrelated, so the AUROC may be inflated by better ascertainment, not transportability. | Add explicit caveat that the higher external AUROC may partly reflect denser arterial measurement and BP autocorrelation; label it a *consistency* signal, not evidence of deployable discrimination. |
| MAJOR | Abstract l.42; Conclusion l.644–645 | "External validation confirmed transfer of discrimination" / "the same model retained discrimination (AUROC 0.751) without refitting" drops the "transportability check, adapted anchor" qualifier carried in Methods/Limitations; risks over-reading as a standard external validation. | Mirror the qualifier in Abstract and Conclusion: "external transportability check (adapted operation-start anchor)…" so headline framing matches the caveats. |
| MAJOR | Conclusion l.648–651 | "Prioritise local recalibration at deployment" is imprecise: the external cohort used a *different anchor* (opstart, post-induction), so the task differs; recalibration alone cannot transpose a VitalDB result to induction use. | Scope recalibration to the induction-anchor internal model; state the VitalDB result cannot substitute for induction-anchor validation and that re-anchoring/re-evaluation is required before any deployment. |
| MINOR | Lines 396–413 (Table 5) | Subgroup AUPRCs (female>male, age<50>≥65) lack confidence intervals / significance tests; differences could be within noise despite temporal replication. | Add CIs or a statement that subgroup gaps are not formally tested; note event counts supporting each stratum. |
| MINOR | Table 5 l.405; l.392–394 | BMI<18.5 = 0.616 reported prominently with only a prose instability caveat; no table-level flag. | Add a table footnote "unstable — n=98 test / 512 cohort" directly on the row. |
| MINOR | Title l.1 vs Abstract l.14, 30; Discussion l.539 | Title says "sustained intraoperative hypotension" but D1 is an *exposure-fraction* (cumulative-burden), not a sustained-duration, definition. "Sustained" connotes continuous duration (cf. O1–O4) and can mislead. | Use "cumulative-burden" (or "recurrent") consistently; avoid "sustained" in title/abstract unless defined as fraction-based. |
| MINOR | Abstract l.36 vs l.452, 571 | Predicted-risk mean quoted as 0.365 (abstract) vs 0.37 (text/limitations). | Harmonise to one value (0.37 or 0.365) throughout. |

---

## Detailed findings

### 1. MAJOR — D1 endpoint: "aligned with Salmasi" overstates clinical grounding (lines 126–130)

**Text:** "The primary outcome (D1) was a cumulative-burden definition **aligned with the absolute-threshold framework of Salmasi et al. [1]**: at least 10 MAP measurements after the anchor, of which at least 30% were below 65 mmHg. Cases with fewer than 10 post-anchor measurements were classified as negative by construction…"

**Problem (clinical):** Salmasi et al. (2017, Ref 1) studied *time-based* exposure — minutes below an absolute MAP threshold (with 1/5/10/15/20/30/60-min duration criteria) and relative reductions from baseline. They did **not** define hypotension as "≥30% of measurements below threshold." So D1 shares only the 65 mmHg cut-point with Salmasi; the ≥30%-of-≥10-readings operationalization is author-derived. Calling it "aligned with the absolute-threshold framework of Salmasi et al." implicitly borrows Salmasi's clinical authority for a rule that is actually pragmatic.

**Additional clinical risk — sampling dependence:** Under MOVER's sparse intermittent NIBP (19.89% case-minute density; median 3 readings in the 15-min pre-anchor window, line 255/314), the *fraction* of readings below 65 is highly sensitive to *when* the few readings happen. Two physiologically identical patients can land on opposite sides of D1 purely by reading timing. The manuscript flags sparsity (Limitations #2, #7) but never states that the **fraction itself is a sampling artifact** of intermittent measurement — a distinct clinical-meaning limitation from "outcome unmeasurable."

**Concrete rewrite (lines 126–130):**
> "The primary outcome (D1) used the absolute MAP threshold of 65 mmHg endorsed by Salmasi et al. [1] and the POQI consensus [18], operationalized as a **cumulative-exposure-fraction** definition: ≥10 MAP measurements after the anchor, of which ≥30% were below 65 mmHg. The 30%-and-10-readings cut-points are pragmatic, chosen for adequate event count (Table 2) rather than derived from a clinical threshold, and are sensitivity-analysed across 14 definitions. Because non-invasive MAP is recorded intermittently (median 3 readings per 15-min window; 19.89% of case-minutes), the ≥30% fraction is sensitive to reading timing and should be read as a monitoring-density-dependent proxy for burden, not a physiologically fixed quantity. Cases with fewer than 10 post-anchor measurements were classified negative by construction (1,496 cases, 8.9%)."

---

### 2. MAJOR — External AUROC 0.751: "ranking transferred" omits the measurement-density confound (lines 445–455, 524–526)

**Text:** "Discrimination transferred: the external AUROC was 0.751 (95% CI 0.713–0.784), numerically above the internal… value… although the confidence intervals overlap… so the difference should be read as consistency rather than superiority." (l.445–448); "Absolute probabilities did not transfer: the mean predicted risk was 0.37 against an observed prevalence of 0.057… the model would require local recalibration" (l.452–454).

**Problem (clinical):** The "ranking transferred" interpretation is defensible *as far as it goes*, but it is incomplete in a way that flatters the result. Two structural facts are acknowledged only as reasons *AUPRC cannot be compared* (Limitation #1, l.566–569), never as reasons the **AUROC itself may be inflated**:

1. **VitalDB uses continuous arterial pressure; MOVER uses intermittent NIBP.** In VitalDB the D1 outcome (≥30% of readings <65) is computed from a *dense, regular* MAP series, so the "burden fraction" is a far more reliable quantity than in MOVER. Better outcome ascertainment alone raises discrimination independent of model quality.
2. **The dominant predictor is pre-anchor MAP and the outcome is post-anchor MAP burden — the same variable at adjacent times.** Blood pressure is strongly autocorrelated minute-to-minute. Under dense arterial recording this autocorrelation is measured cleanly, so a model that "ranks by current BP" will look better externally *precisely because the data are denser*, not because the model generalises. This is the exact mechanism of Limitation #9 ("the model largely reflects the present blood pressure"), yet it is never connected to *why the external AUROC looks strong*.

A clinician reading "external AUROC 0.751" will reasonably infer the model discriminates well in an independent cohort. The manuscript should state plainly that part of that number may be an artifact of superior measurement, not transportability.

**Concrete rewrite (add after l.448, before l.449):**
> "This consistency should not be read as deployable external discrimination. VitalDB records continuous arterial pressure, so both the D1 outcome (a MAP-based burden fraction) and the MAP predictors are measured far more reliably than in the sparse intermittent NIBP of MOVER; and because the strongest predictor (pre-anchor MAP) and the outcome are the same autocorrelated physiological signal at adjacent times, denser recording inflates apparent ranking ability independently of true generalisability. The external AUROC therefore indicates *consistency of signal under denser measurement*, not validated transportability of the induction-anchor model."

Also adjust Discussion l.524–526 to add the same qualifier (currently it says the finding "strengthens rather than weakens the caution" — good direction, but pair it with the density confound).

---

### 3. MAJOR — Abstract/Conclusion framing drops the transportability qualifier (Abstract l.42; Conclusion l.644–645)

**Text:** Abstract l.42 — "External validation confirmed transfer of discrimination but not of absolute probabilities, which would require local recalibration before clinical use." Conclusion l.644–645 — "In an independent external cohort (VitalDB, n = 3,735) the same model retained discrimination (AUROC 0.751) without refitting, although absolute probabilities were not calibrated to that cohort and would require local updating."

**Problem (clinical communication):** Both sentences are individually true but omit the qualifier that the Methods (l.179, 183–187) and Limitations (l.553–558) explicitly carry: the external step is a *transportability check with an adapted (operation-start) anchor*, **not** a like-for-like validation. "External validation confirmed" (Abstract) and "independent external cohort… retained discrimination" (Conclusion) are exactly the phrases a clinician or editor scans, and they can be read as a standard, successful external validation — contradicting the manuscript's own careful framing elsewhere.

**Concrete rewrite:**
- Abstract l.42 → "An external **transportability check** (VitalDB, adapted operation-start anchor, no refitting) showed consistency of ranking (AUROC 0.751) but not of calibration; probabilities would require local recalibration before any clinical use — and even then only under an induction-equivalent anchor."

- Conclusion l.644–645 → "In an independent external cohort (VitalDB, n = 3,735) used as a **transportability check with an adapted operation-start anchor**, the unchanged model showed consistency of ranking (AUROC 0.751) without refitting, but absolute probabilities were not calibrated to that cohort and would require local updating; because the external anchor postdates induction, this result speaks to ranking under an operation-start anchor, not to deployment at induction."

---

### 4. MAJOR — "Local recalibration at deployment" recommendation is imprecise (Conclusion l.648–651)

**Text:** "We recommend that future work on this and similar resources prioritise local recalibration at deployment, explicit reporting of the outcome definition and its prevalence, and routine quantification of recording density…"

**Problem (clinical):** The recalibration recommendation is framed as if the *external* result were a deployable model needing only probability rescaling. But the external cohort's anchor is **operation start, which postdates induction** (l.183–187). The external test therefore evaluates a *different prediction task* — using early-intraoperative physiology to predict remaining-intraoperative burden — not the paper's stated induction-triage task. Recalibrating probabilities cannot fix a mismatched predictor window; the VitalDB result cannot substitute for an induction-anchor external validation.

**Concrete rewrite (l.648–651):**
> "We recommend that future work prioritise (i) **local recalibration of the induction-anchor model** to local prevalence before any deployment at induction; (ii) explicit reporting of the outcome definition and its prevalence; and (iii) routine quantification of recording density. The VitalDB step was a transportability check under an adapted operation-start anchor and **must not be read as external validation of induction-time use**; induction-anchor external validation with an induction-equivalent predictor window remains required."

---

### 5. MINOR — Subgroup AUPRCs lack CIs / significance (lines 396–413)

**Text:** Table 5 reports AUPRC by sex (women 0.357 vs men 0.299), age (<50 0.380 vs ≥65 0.186), BMI. Lines 411–412: "Subgroup AUPRCs are exploratory given the reduced event counts within strata."

**Problem:** The sex/age gaps are *temporally replicated* (a real strength) but no CIs or significance tests are given, so a clinician cannot tell whether the female>male or age-gradient differences exceed noise. Each sex stratum has ~1,684 test cases (~260 events); an AUPRC gap of 0.058 could plausibly be within bootstrap noise.

**Fix:** Add bootstrap CIs to Table 5 (or a sentence: "none of the subgroup AUPRC gaps reached formal significance at α=0.05 under 1,000 bootstrap resamples"). The existing "exploratory" caveat is adequate in spirit but should be backed by intervals.

---

### 6. MINOR — BMI<18.5 row lacks a table-level instability flag (Table 5 l.405; l.392–394)

**Text:** "BMI < 18.5 kg/m² | 98 | 0.616 | 0.382" with prose caveat at l.392–394 ("should be regarded as unstable").

**Fix:** Add a direct footnote on the row: "† unstable estimate — 98 test / 512 cohort cases; not interpretable." This prevents a skimming reader from treating 0.616 as a real subgroup effect.

---

### 7. MINOR — "Sustained" in title vs "cumulative burden" in body (Title l.1; Abstract l.14,30; Discussion l.539)

**Problem:** Title: "Prediction of **sustained** intraoperative hypotension burden." But D1 is an *exposure-fraction* (≥30% of readings), explicitly contrasted with the sustained-grid definitions O1–O4 (l.288–291). "Sustained" connotes continuous duration and will mislead clinicians scanning the title.

**Fix:** Retitle as "Prediction of **cumulative-burden** intraoperative hypotension…" and use "cumulative-burden" (or "recurrent") uniformly in the abstract; reserve "sustained" only for the O1–O4 definitions where it is technically correct.

---

### 8. MINOR — Predicted-risk mean inconsistency (Abstract l.36 vs l.452, 571)

Abstract l.36: "predicted-risk mean 0.365 vs observed 0.057." Text l.452 / Limitations l.571: "mean predicted risk was 0.37." Harmonise to a single value (0.37, or 0.365) across all three locations.

---

## Cross-cutting clinical assessment

- **D1 defensibility:** Defensible as a research construct and honestly sensitivity-analysed, but its *clinical face-validity* is weaker than the "aligned with Salmasi" phrasing implies, and its sampling-dependence under sparse NIBP is under-acknowledged. (Findings 1, partly 2.)
- **External AUROC 0.751 honesty:** Directionally honest (calibration failure stated) but **under-claims the confound** — it presents the number as evidence of transportability while the denser arterial measurement and BP autocorrelation likely inflate it. This is the single most important residual risk for a clinical reader. (Findings 2, 3.)
- **Limitations honesty:** Strong — anchor-phase shift (l.553–558), feature-meaning shift (l.559–562), and nMAP sparsity (l.573–575) are all present and clear. The gap is that the *Abstract and Conclusion* do not carry the same qualifier, creating a headline-vs-caveat mismatch. (Findings 3, 4.)
- **Conclusions over/under-claim:** Body of Conclusion is appropriately modest ("modest but non-null," "most information in pre-anchor MAP"). The risk is the external-anchored sentences (l.644–645, l.648–651) over-reading the external step as validation. Not an over-claim of raw performance, but an over-reading of *what the external number means*. (Findings 3, 4.)
- **Subgroup stability:** Female>male and age-gradient claims are tempered by temporal replication and an "exploratory" note, which is adequate; adding CIs (Finding 5) and a BMI footnote (Finding 6) would close the gap. The BMI<18.5 = 0.616 instability is already well caveated in prose.

---

## Verdict

**Major revisions.**

No SEVERE (fatal) clinical flaw survives Round 4: the modest-performance framing, the open calibration failure, the MAP-only benchmark, and the dominant-predictor-is-current-BP caveat are all sound and honest. However, four MAJOR issues remain that a clinician or editor could misread:
1. the endpoint's "aligned with Salmasi" grounding is overstated and its sampling-dependence is under-stated;
2. the external AUROC 0.751 is presented as transportability without acknowledging the arterial-density / autocorrelation confound that likely inflates it;
3. the Abstract and Conclusion drop the "transportability check, adapted anchor" qualifier that Methods/Limitations carry, reading as a standard external validation;
4. the "local recalibration at deployment" recommendation ignores that the external anchor differs, so the VitalDB result cannot support induction-time use.

These are conceptually and textually fixable without new modelling, but they materially change how the external result and the endpoint should be read, so they exceed cosmetic "minor" edits. With the proposed rewrites (and the four MINOR clarifications), the manuscript would be suitable for acceptance.
