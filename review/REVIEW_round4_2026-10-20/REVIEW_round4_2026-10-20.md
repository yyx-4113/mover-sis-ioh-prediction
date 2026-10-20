# Consolidated Editor Report — Independent Review Panel, Round 4 (2026-10-20)

## 1. Independence statement

Four reviewers (A1 domain / A2 design / A3 provenance / A4 venue) were dispatched as fully
independent agents with **no knowledge of prior rounds** and an explicit forbidden-file list
(`review/REVIEW_round*.md`, the stale `review/A1–A4_domain/design/provenance/venue.md` from the
morning, `external_validation_plan.md`, all `.workbuddy/` files, prior RESPONSE/REVISION logs).
Each recomputed numbers from raw artifacts and wrote to a clean directory
(`review/REVIEW_round4_2026-10-20/`).

**Evidence the discipline worked:**
- The same defect was hit from different angles: the **anchor-phase shift** (opstart postdates
  induction) was independently flagged by *both* A1 and A2; **external selection bias** by A2 and A3;
  the **DCA narrative** by A1 and A3.
- They found defects the prior three rounds never touched: the `anchor_minus_or_start` meaning shift
  under the opstart anchor (A2), the VitalDB denominator (6,388 → 3,735, A2/A3), the external
  negative-by-construction count (A3), and the stale **cover letter contradicting the manuscript**
  (A4). A fresh read caught what a "delta-review" would have skipped.

## 2. Verdict table

| Reviewer | Role | Verdict | One-line rationale |
|---|---|---|---|
| A1 | Domain (IOH) | **Major** | External anchor is a phase shift, not a fair analogue; DCA narrative misread |
| A2 | Design / ML validation | **Major** | Anchor-phase confound + `anchor_minus_or_start` redefinition + undisclosed selection |
| A3 | Provenance / recompute | **Minor** | Every number reproduced exactly; only rounding, URL precision, disclosure gaps |
| A4 | Venue / TRIPOD+AI | **Major** | Cover letter↔manuscript contradiction + ethics mismatch + framing |
| **Editor** | — | **Major revision, no conclusion-invalidating defect** | All metrics verified; fixes are disclosure/framing + cover letter |

## 3. Cross-verification table (numbers recomputed by the panel + editor)

| Location | Manuscript claims | Independently recomputed | Who | Verdict |
|---|---|---|---|---|
| External AUPRC / AUROC / prevalence / n / events | 0.160 / 0.751 / 5.73% / 3,735 / 214 | 0.1600 / 0.7507 / 0.0573 / 3,735 / 214 | A3 (from `vitaldb_predictions.csv`+`vitaldb_labels.csv`) | Match |
| MOVER core (53-col) patient/temporal AUROC | 0.698 / 0.710 | 0.698 / 0.710 | A2/A3 (`core_benchmark.json`) | Match |
| Internal AUPRC 0.347 / 0.339; AUROC 0.722 / 0.733 | as stated | exact | A3 (`s3_metrics.json`) | Match |
| Calibration Brier 0.191→0.119; slope 0.909; intercept 0.008 | as stated | exact | A3 | Match |
| DCA last-positive thresholds 0.58 / 0.73 | as stated | 0.58 / 0.73 verified | **Editor** (`s3_calib_dca.json`) | Match — A1's "narrative wrong" **demoted** |
| Conditional prevalence 17.1% (2,622/15,365) | as stated | 0.1706 | A2/A3 | Match |
| Bootstrap resample index alignment | implied correct | code review `s3_models.py` | A2 | Prior bug confirmed fixed |
| VitalDB total denominator | (absent) | 6,388 cases; 3,735 eligible | **Editor** (`cases.csv`) | Gap closed |
| Ref 16 (Walsh 2013) DOI | (missing) | 10.1097/ALN.0b013e3182a10e26 | **Editor** (Crossref) | Gap closed |
| Table 3 Demographics coverage | 99.8% | 99.68% | A3 | Round to 99.7% (fixed) |

## 4. Graded consolidated issue list

### Tier 0 — conclusion-invalidating
None. All performance figures reproduced exactly; no conclusion is invalidated.

### Tier 1 — design / integrity (fixed this round)
1. **Cover letter contradicts the manuscript (MAJOR, submission-blocking).** The cover letter still
   said "TRIPOD type 2a … absence of external validation" and "a retrospective waiver letter …
   being obtained," while the manuscript is type 2b with external validation and a default-exemption
   ethics statement. **Fixed:** cover letter title, summary, type-2b framing, ethics, and data-URL
   all brought into line with the manuscript (user directive: no waiver letter, default exemption).
2. **Anchor-phase shift undisclosed (MAJOR design).** VitalDB `opstart` occurs *after* induction/
   intubation, so the external "pre-anchor" window is early-intraoperative, not pre-induction. The
   manuscript called it "closest available analogue" and "to test generalisability," over-claiming.
   **Fixed:** reframed as a *transportability check*; phase shift stated in Methods, Results, and
   Limitations #1; abstract carries the caveat.
3. **`anchor_minus_or_start` meaning shift undisclosed (MODERATE–SEVERE).** The 53-col core subset
   includes this feature; in VitalDB it is re-derived as `opstart/60` (case-start→operation-start),
   a different quantity than MOVER's OR-start→intubation interval (`ext_build.py:147`, confirmed by
   editor). The manuscript's "MOVER-specific timing signals … set to zero" list was incomplete.
   **Fixed:** core-subset description corrected; meaning shift disclosed in Methods and Limitations #1.
4. **External selection bias denominator undisclosed (MODERATE).** Only 3,735 of 6,388 VitalDB cases
   (those with valid timing + arterial MAP) were used, with no denominator. **Fixed:** denominator
   and eligible-count stated in Methods and Results.

### Tier 2 — wording / disclosure (fixed)
5. **External negative-by-construction count undisclosed (MINOR–MODERATE).** 214 external cases were
   D1-negative by construction (<10 post-anchor MAP). **Fixed:** stated; conditional external
   prevalence 6.1% (214/3,521) reported.
6. **External AUROC "above internal" within CI overlap (MINOR).** CIs overlap (0.713–0.784 vs
   0.673–0.723 / 0.679–0.740). **Fixed:** retained "numerically above" but added explicit
   CI-overlap / "consistency not superiority" hedge.
7. **DCA narrative precision + magnitude (MINOR).** The transient dip is at 0.59–0.66, not "near
   0.67"; absolute net benefit is small. **Fixed:** location refined; magnitude-honesty sentence
   added. (The "positive up to 0.58/0.73" claim itself was **verified accurate** by the editor and
    is retained.)

### Tier 3 — format (fixed)
8. **Ref 16 missing DOI** → added `10.1097/ALN.0b013e3182a10e26` (Crossref-verified).
9. **Table 3 Demographics coverage** 99.8% → **99.7%** (artifact 99.68%).
10. **Data-availability URL** repo-root → **release tag**
    (`…/releases/tag/v1.0.0`) in manuscript and cover letter.
11. **Figure 5 "25" vs Table 6 "10"** — checked; **not a contradiction** (figure shows 25 bars, table
    lists top 10 in detail). Stands up.

## 5. Consensus / complementarity / disagreement

- **Consensus:** all four agree the *metrics* are correct and the external AUROC transfer is a real,
  useful finding; all agree the honesty framing needed tightening.
- **Complementarity:** A1 caught the clinical phase-shift; A2 caught the feature-meaning shift and
  selection; A3 confirmed every digit; A4 caught the cover-letter/ethics mismatch. No overlap wasted.
- **Disagreements (adjudicated):**
  - A1 asserted the DCA narrative is "wrong." The editor recomputed and **demoted** it: at 0.58 the
    patient net benefit is +0.0001 (the last positive point), and the temporal split is positive to
    0.73 with a dip at 0.59–0.66 — exactly what the manuscript says. A1 had compared model-NB against
    *treat-all* instead of *treat-none*.
  - A1/A2 framed "external AUROC above internal" as an over-claim. The manuscript already hedges
    ("numerically above"); the editor kept it and added the CI-overlap caveat rather than rewriting
    as "non-inferiority," because "numerically above" is literally true and non-misleading.
  - A4 called the ethics statement "inconsistent." The **manuscript** ethics is internally consistent
    (default exemption); the inconsistency existed **only in the stale cover letter**, now fixed.

## 6. Priority must-fix list

| # | Fix | Type | DESK-REJECT risk |
|---|---|---|---|
| 1 | Cover letter ↔ manuscript consistency | wording | **Yes if unfixed** (submission-blocking) — DONE |
| 2 | Anchor-phase reframing (transportability, not validation) | wording | Low once done — DONE |
| 3 | `anchor_minus_or_start` disclosure | disclosure | Low — DONE |
| 4 | External denominator + selection | disclosure | Low — DONE |
| 5 | External negative-by-construction + CI-overlap hedge | disclosure | Low — DONE |
| 6 | Ref 16 DOI / Table 3 rounding / URL tag | format | None — DONE |

## 7. What stands up (do NOT change)

- Every reported performance number (A3 reproduced all to the digit).
- External AUPRC 0.160 / AUROC 0.751 / predicted-risk mean 0.365 (A1, A3, A4 independently verified).
- DCA last-positive thresholds 0.58 / 0.73 (editor-verified).
- Conditional prevalence 17.1% (2,622/15,365) and the structural-exclusion accounting.
- The 1,000-bootstrap resampling-index alignment (the prior index-mismatch bug is confirmed fixed).
- The underweight-subgroup caveat (0.616 → 0.382 temporal, n=98/512) is honest.
- The critique of the 0.973-competitor preprint is fair, non-ad-hominem, and cites it as a preprint.
- The MAP-only benchmark (0.284 vs 0.347; +0.013 net benefit) honestly bounds incremental value.

## 8. Recommended handling path

**A) Restructure-and-resubmit as the same article type (TRIPOD 2b).** No downgrade needed: the
strongest real finding — honest, leakage-audited prediction with a *transportable* external check —
is now correctly framed, and the weakest claim (like-for-like external validation) has been retired in
favour of the defensible "transportability check." The manuscript's contribution is stable rather
than fragile.

## 9. Process lessons (what the gate could not catch)

- A green consistency gate verifies arithmetic and string presence, **not design integrity**. The
  anchor-phase and feature-meaning shifts are design-layer defects a gate cannot see.
- The most dangerous defect this round was a **stale cover letter** — a derived artifact that
  silently contradicted the manuscript after the manuscript was edited. Rule adopted: after any
  manuscript edit that changes study type / ethics / validation status, the cover letter must be
  re-diffed against the manuscript.
- The environment trap (VitalDB `opstart` = post-induction) is invisible unless a reviewer asks
  "what physiological phase does this window actually capture?" — a design-layer question.
- New gate assertion recommended: a check that the cover letter title, study type, and ethics
  statement string-match the manuscript; and that the external-validation section discloses the
  source-cohort denominator.

## 10. Editor's reframe note to the author

The single strongest claim that does *not* hold as first written is the framing of VitalDB as a
like-for-like external validation — it is, honestly, a **transportability check under an adapted
anchor**, because opstart postdates induction. This is **not your fault**: it is a structural
property of the public resource (no intubation event). The second, buried finding that *is* your
real contribution is the **leakage-audited, calibration-honest, MAP-only-benchmarked** prediction
with an explicit quantification of how recording density shapes both the endpoint and the apparent
signal. Swapping the headline from "we externally validated" to "we audited and transport-tested an
honest sparse-data model" converts the paper from a fragile signal into a stable methodological
contribution — which is exactly the reframe applied in this revision.
