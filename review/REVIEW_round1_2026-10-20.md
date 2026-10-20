# Round-1 Editorial Review Synthesis — MOVER/SIS IOH Prediction Manuscript

**Role of this document:** Editor (consolidating 4 independent expert reviews — A1 domain / A2 design-biostatistics / A3 provenance-recompute / A4 venue-reporting) into a single action list and verifying each fix against the source artefacts.
**Manuscript:** `manuscript/manuscript_v0.1.md` (BMC Anesthesiology, TRIPOD type 2a)
**Date:** 2026-10-20

---

## 1. Independence & method note

Four reviewers were run in isolation (no access to each other's reports or to `STATUS.md` / `REVIEW_*` / `.workbuddy`). Every quantitative claim was re-checked against `s1_*`–`s4_*` result files, `config.yaml` and the modelling scripts. The convergence below is therefore cross-validated, not assumed.

---

## 2. Reviewer verdicts (as returned)

| Reviewer | Focus | Verdict | Dominant blocker(s) |
|---|---|---|---|
| A1 Domain | Clinical anesthesiology | **Minor revision** | model≈current MAP limitation under-stated; orphan citations; missing MAP-only DCA benchmark; coverage rounding slips |
| A2 Design | Biostatistics / TRIPOD | **Major revision** | "every number traceable" claim false (audit trail gaps); Table 5 subgroup ambiguity |
| A3 Provenance | Recompute / traceability | **Major revision** | same audit-trail gaps (DCA NB, temporal calib/subgroup, coverage metric); 1,496 & density untraceable |
| A4 Venue | BMC policy / TRIPOD+AI | **Major revision (not desk-reject)** | ethics "no determination sought" wording; orphan refs [14][15][16]; missing TRIPOD+AI checklist; leaked "verified" annotations |

---

## 3. Cross-validated convergent findings (≥2 reviewers, or 1 reviewer + editor confirmation)

### Tier-0 — Blocker / reproducibility integrity
1. **Audit trail does not back the "every number traceable" claim.** Temporal calibration block, *all* DCA net-benefit values, temporal subgroup AUPRC, and the Table 3 coverage column are absent from `s4_audit_trail.csv`; Table 3's "Coverage (%)" uses case-count coverage while the audit trail stores mean-non-null-across-features (differs for 9/12 domains). (A2 §1, A3 §P1–§P4, §P4) — **CONFIRMED by editor**: reproduced all gaps.
2. **Table 5 subgroup n is wrong.** Subgroup AUPRCs were computed on the **held-out test set** (`s3_models.py: subgroup_auprc(yte, p_cal, Xte)`), but the table reported full-cohort n (e.g., Men 8,355). Editor recomputed test-set n = 1,689 (male) / 1,684 (female) for the patient split. (A2 §2, A3 §C7) — **CONFIRMED**.
3. **Orphan references [14] Chiu 2025, [15] Cheun 2026, [16] Walsh 2013** are never cited in the body. (A1, A4 §4.1) — **CONFIRMED** (grep).

### Tier-1 — High-value scientific / presentation
4. **Ethics statement** "a formal determination was therefore not sought" is the weakest possible posture and is a likely technical-check / editorial hold at BMC. (A4 §2) — editor: strengthened to the institution's DUA-based exemption wording **without fabricating an approval number** (per author's stated route B).
5. **Calibration "mild over-fitting" understated**: uncalibrated Brier 0.191/0.194 > no-information Brier 0.131 → recalibration is essential, not cosmetic. (A2 §4) — **CONFIRMED** (0.1555×0.8445 = 0.1313).
6. **DCA bound mis-statement**: Results said "positive up to 0.58 (patient) / 0.45 (temporal)". Editor recomputed directly from `s3_calib_dca.json`: patient net-benefit last-positive threshold = 0.58 (manuscript was already correct); the *temporal* bound was mis-stated as 0.45 and is corrected to **0.73** (with a transient dip near 0.67). The separate Discussion line "usable up to about 0.20" was unsupported and is removed, replaced by the data-derived 0.58/0.73 bounds. (A3 §N1, §C3, A2 §6) — **CONFIRMED + corrected**.
7. **Model≈current MAP limitation not in the Limitations list** where clinicians read it. (A1 §2, §9) — editor: added as explicit limitation + 4th implication.
8. **0.97-AUROC critique over-stated** ("near-separation"; asserted leakage mechanism). (A1 §3) — softened to a neutral methodological hazard; kept "we do not question directly".
9. **Oyarzun's counter-claim** (predicts hypotension *beyond* current value) not engaged. (A1 §4) — editor: added balancing sentence.

### Tier-2 — Should-fix / hygiene
10. **Missing TRIPOD+AI checklist** as Additional file 2. (A2 §10, A4 §5) — added.
11. **Leaked "*(verified …)*" / "*(unrefereed …)*" annotations** in references. (A4 §7) — stripped.
12. **Missing must-cite threshold/organ-injury literature** (Sun 2015; POQI 2024 consensus). (A1 §6) — added as [17]/[18] and cited.
13. **Anchor-proxy limitation** under-discussed given `anchor_is_intubation` is the 3rd-strongest predictor. (A2 §7) — expanded.
14. **Negative-by-construction spectrum bias** (1,496 cases). (A2 §8) — added sensitivity framing + audit entry.
15. **Minor**: 82.0/18.0 → 82.1/17.9 rounding; 2.23 vs 2.2 consistency; Table 1 surgical-group row prefix; seven-vs-ten leakage rows footnote; bootstrap-CI framing sentence.

### Additional (editor-added, beyond reviewers)
16. **Decision-curve benchmark against a pre-anchor-MAP-only logistic** (the real bedside comparator). Implemented as `dca_map_benchmark` in `s3_calib_dca.json` and added to Figure 4, directly addressing A1 §7 / A2 §7's decisive-incremental-value test.

---

## 4. What stands up (verified correct — not to be "fixed" away)

- Cohort arithmetic 19,114 − (8+1,632+371+242) = 16,861.
- D1 prevalence 2,622/16,861 = 15.55%; all 14 definitions in Table 2.
- Table 4 (8 model rows × 3 metrics × 2 CIs) and Table 6 (top-10 gains) recompute exactly from `s3_metrics.json` / `s3_feature_importance.json`.
- Leakage audit: all 7 source tables max(observation−anchor) = 0.00, zero unparseable timestamps.
- Calibration point values (Brier 0.191→0.119, slope 0.909, intercept 0.008; temporal 0.194→0.122, slope 0.934, intercept 0.006) — all correct; the DCA slip was the *temporal* bound (0.45 → corrected to 0.73); the patient bound 0.58 was already correct.
- DCA net-benefit magnitudes at 0.15 (0.050/0.058) and 0.10 (0.079/0.085) — correct.
- Public, DUA-compliant reproduction package.

---

## 5. Action log (Round-1)

| # | Fix | File(s) | Status |
|---|---|---|---|
| 1 | Extend `s4_audit_trail.csv` (temporal calib, DCA NB, temporal subgroups, case-count coverage, density, 1,496, subgroup n, Table-1 descriptors) | `scripts/s4_report.py` → rerun | DONE |
| 2 | Correct Table 5 to **test-set** n + dataset/exploratory footnote | `manuscript_v0.1.md` | DONE |
| 3 | Cite [14][15][16]; add [17] Sun 2015, [18] POQI 2024; strip "verified" annotations | `manuscript_v0.1.md` | DONE |
| 4 | Strengthen ethics statement (DUA-based exemption, no fabricated number) | `manuscript_v0.1.md` | DONE |
| 5 | Calibration wording (recalibration essential) + slope/intercept clarification | `manuscript_v0.1.md` | DONE |
| 6 | DCA: temporal 0.45→0.73 (patient 0.58 verified correct); remove unsupported Discussion "0.20" | `manuscript_v0.1.md` | DONE |
| 7 | Add "model ≈ bedside MAP" limitation + 4th implication | `manuscript_v0.1.md` | DONE |
| 8 | Soften 0.97 critique; engage Oyarzun counter-claim | `manuscript_v0.1.md` | DONE |
| 9 | Expand anchor-proxy + spectrum-bias limitations; bootstrap-CI framing | `manuscript_v0.1.md` | DONE |
| 10 | TRIPOD+AI checklist finalised → Additional file 2 | `results/s4_tripod_ai.md` + manuscript | DONE |
| 11 | MAP-only logistic DCA benchmark → `s3_calib_dca.json` + Figure 4 | `scripts/_dca_map_benchmark.py` | DONE |
| 12 | Cosmetic: 82.1/17.9; 2.23 consistency; surgical-group prefix; 7-vs-10 footnote | `manuscript_v0.1.md` | DONE |
| 13 | Update `s5_gate.py` (references 16→18; key-number 82.0/18.0→82.1/17.9) + regenerate docx | `scripts/s5_gate.py`, `scripts/s5_docx.py` | DONE |

---

## 6. Residual items for the author (not fixable by editorial revision)

- **Formal IRB exemption/waiver letter** (with reference) — author is pursuing the retrospective-exemption route; the manuscript now states the DUA-based exemption basis honestly and must be backed by the letter before submission.
- **Zenodo/OSF DOI archive** for the reproduction package (BMC data-policy smoothing) — optional but recommended.
- **External validation** remains the decisive next step (Limitation #1); explicitly out of scope for this type-2a manuscript.

---

## 7. Round-2 plan

Re-run the 4-review panel on `manuscript_v0.2.md` with the consolidated fixes; target **"minor revision / acceptable"** consensus before author submission to BMC Anesthesiology.
