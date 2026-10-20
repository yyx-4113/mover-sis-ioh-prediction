# Round-5 Independent Panel Brief — MOVER/SIS IOH Prediction

**Date:** 2026-10-20
**Manuscript:** `manuscript/manuscript_v0.1.md` (BMC Anesthesiology, TRIPOD type 2b — development + internal + external validation)
**Cover letter:** `manuscript/cover_letter_bmc_anesthesiology.md`
**Gate report:** `review/quality_gate_2026-10-20.md` (PASS: abstract 340 words, 19 refs, 6 figs, 7 tables, 34 key numbers, DCA@0.15 consistent)

## Charge to reviewers
You are an independent reviewer for a BMC Anesthesiology submission. The manuscript has already passed 4 prior review rounds and a consistency gate. Your job in Round 5 is to find **residual risks that survive the previous rounds** — not to re-litigate settled decisions. Be specific: cite line numbers, quote the offending text, give a concrete rewrite, and assign severity (SEVERE / MAJOR / MINOR).

## Critical constraint — avoid contamination
- DO NOT read `review/REVIEW_round1..4*` or any `A1..A4_*.md` from prior rounds. Judge the manuscript on its own merits.
- DO NOT read other Round-5 agent outputs. Each reviewer works independently.

## What the manuscript currently claims (verified facts — check them against the text)
- **Outcome D1:** ≥10 MAP measurements after anchor AND ≥30% of those <65 mmHg (cumulative burden). Internal prevalence 15.55% (2,622/16,861 modelling cohort).
- **Anchor:** intubation (82.1%) / surgery_start fallback (17.9%). Internal XGBoost AUPRC 0.347 (0.309–0.387), AUROC 0.722; temporal AUPRC 0.339.
- **External validation (VitalDB):** framed as a *transportability check*, NOT like-for-like. 6,388 screened → 3,735 eligible (arterial MAP track + valid opstart/opend). 214 event-negative-by-construction excluded (same rule as internal). External prevalence 5.73% (214/3,735). Unchanged 53-feature core model (no refit, no recalibration) applied: AUPRC 0.160 (0.129–0.202), AUROC 0.751 (0.713–0.784), Brier 0.179. Predicted-risk mean 0.365 vs observed 0.057.
- **Disclosed transportability caveats:** (a) external anchor = operation start, which *postdates* induction (internal anchor), so it is a phase-shifted test; (b) `anchor_minus_or_start` feature is re-derived under opstart and its *meaning changes* (OR-start-to-intubation internally vs opstart-based externally); (c) denominator and exclusion rule disclosed; (d) AUPRC not comparable across prevalences — only AUROC is.
- **Ethics:** retrospective analysis of pre-existing de-identified data under a data use agreement; exempt from prospective IRB review and individual consent per the institution's IRB policy; **no approval number, no waiver-letter language**.
- **Novelty risk disclosed:** a competing preprint (Preprints.org 202603.1373) claims AUROC 0.973 on MOVER XGBoost, deemed implausible given nMAP non-null rate 19.89%; our 0.723 aligns with medRxiv external-validation magnitudes.

## Review dimensions (assign one primary focus each)
- **A1 — Clinical / domain (anesthesiology, IOH):** clinical plausibility of D1 definition, interpretation of the external AUROC 0.751 as "transportability of ranking not probability", honesty of limitations, whether conclusions over- or under-claim.
- **A2 — Study design / TRIPOD+AI methodology:** protocol adherence, the anchor-phase-shift handling, feature-meaning shift, whether "transportability check" framing is defensible vs. must be downgraded to "exploratory", missing-data sparsity (nMAP 19.89%) treatment, subgroup claims.
- **A3 — Statistics / reproducibility / provenance:** bootstrap CI integrity, AUPRC-vs-AUROC comparability statements, calibration (Brier 0.1905→0.1190 internal; 0.179 external), DCA net-benefit wording, any number that doesn't trace to `results/` artifacts, gate residual risks.
- **A4 — Journal fit / formatting / ethics (BMC Anesthesiology):** BMC section structure, Declarations (7 subheads), Vancouver refs (19), abstract ≤350 four-paragraph, cover letter alignment with manuscript, ethics-statement compliance with BMC policy, any English/formatting issues that would trigger desk edits.

## Deliverable
Each reviewer writes `review/REVIEW_round5_2026-10-20/A<n>_*.md` with: executive summary, findings table (severity | location | issue | concrete fix), and a verdict (Accept-as-is / Minor revisions / Major revisions / Reject).
