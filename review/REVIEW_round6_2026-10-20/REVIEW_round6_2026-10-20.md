# REVIEW_round6_2026-10-20 — Consolidated editor's report

**Manuscript:** `manuscript/manuscript_v0.1.md` (BMC Anesthesiology, TRIPOD+AI type 2b)
**Panel:** A1 clinical/domain · A2 design/TRIPOD+AI · A3 statistics/provenance · A4 venue/reporting
**Method:** four reviewers ran in parallel, mutually isolated, each forbidden to read prior review rounds, status files, or each other's outputs; each charged to recompute numbers from artefacts and source data rather than trusting the text. Charge: `_PANEL_BRIEF.md`.
**Editor:** every SEVERE finding and every number-bearing MAJOR finding was independently re-verified by the editor before consolidation (marked ✅ editor-verified below).

---

## 1. Independence statement — and the evidence it worked

Each reviewer received only the manuscript, the artefacts, the raw-data pointers, and the brief. None read `REVIEW_round1..5*`, `A1..A4_*.md`, `STATUS.md`, `NOTES_zh.md`, or the deposit SOP.

**The diagnostic signature is present:** several experts hit the same defects from different angles, and two editor-found defects were independently re-found:

| Defect | Found independently by |
|---|---|
| Limitations orphan fragment (lines 607–612, no header/number) | **A1 (M1)**, **A4 (F5)**, and the editor (git blame → introduced by Round-5 commit `4bf7803`) |
| "What this study adds — four elements" vs five listed items | **A1 (M2)**, **A4 (F5)**, editor |
| Anchor split 82.1%/17.9% should be 82.0%/18.0% | **A4 (F1)**, **A3 (minor #2)**; editor recomputed 82.047%/17.953% |
| Median imputation fitted on the full cohort before splitting | **A2 (M3)**, **A3 (minor #11)**; editor read `s3_models.py:79-81` |
| Calibration slope described as "log-odds scale" but computed on the probability scale | **A2 (M8)**, **A3 (minor #6)**; editor read `s3_models.py:215` |
| Audit trail `female_n = 8,506` wrong (Table 1's 8,502 correct) | **A4 (F2b)**, **A3 (minor #3)**; editor traced to `s4_report.py:370` merging 4 unknown-gender cases into female |
| External cohort contains density-driven features with no external support | **A2 (M6)**, **A3 (M3)** |

**No leakage of settled framing was observed:** reviewers contested points the author considered closed (e.g., A1-S1 challenging the frozen D1 outcome; A2-F2 challenging the negative-by-construction rule), which is exactly what a fresh panel is for.

---

## 2. Verdict table

| Expert | Focus | Verdict | Findings |
|---|---|---|---|
| A1 | Clinical / domain | **Major revisions** | 3 SEVERE, 7 MAJOR, 11 MINOR |
| A2 | Design / TRIPOD+AI | **Major revisions** | 3 SEVERE, 6 MAJOR, 19 MINOR |
| A3 | Statistics / provenance | **Major revisions** | 3 MAJOR, 11 MINOR |
| A4 | Venue / reporting | **Major revisions** | 1 SEVERE, 6 MAJOR, 8 MINOR |
| **Distribution** | | **unanimous Major revisions** | 7 SEVERE-class (after editor adjudication: 5), 19 MAJOR-class, 37 MINOR-class |

---

## 3. Cross-verification table (editor-verified rows marked ✔)

| # | Manuscript location | Manuscript claims | Independently recomputed | Who checked | Verdict |
|---|---|---|---|---|---|
| 1 | Abstract:22, Methods:120–121, Table 1, Fig 1, Limitations:587 | anchor split 82.1% / 17.9% | 13,834/16,861 = 82.047% → **82.0%**; 3,027/16,861 = 17.953% → **18.0%** (Figure 1 already prints 82.0/18.0) | A4, A3, **editor ✔** | **WRONG in text — 5 places** |
| 2 | Results:151 | 3,559,993 one-minute OR observations | 16,861-case OR-window rows = **3,379,173** (`s1_cohort.py:124` counts `vit_w` before the age/anchor filters; 19,106-case layer) | A3, **editor ✔** | **WRONG (−5.1%)** |
| 3 | Table 1 (surgery groups) | GI 5,172 … Other 339; rows sum to 17,330 | `s2_procedure_groups.csv` per-case recount: GI 4,916 … Other 348, **sum = 16,861** | **editor ✔** | **WRONG (stale table)** |
| 4 | Table 1 (age, BMI) | 51.3 (16.5); 25.7 (5.4) | `s2_features.csv`: age **52.9 (17.7)**; BMI **27.8 (7.0)** (n=16,699) | **editor ✔** | **WRONG (stale)** |
| 5 | Table 1 (female) | 8,502 (50.4%) | `s2_data_quality.json` gender_values F=8,502 ✔; audit trail's 8,506 merges 4 unknown into female | A4, A3, **editor ✔** | Table 1 right; **audit trail wrong** |
| 6 | Table 3 | Ventilation 20 / Laboratory 6 / Medication 51 predictors; coverage 28.8 / 0.45 / 98.3% | `s2_feature_dictionary.json` + `domain_coverage`: **47 / 12 / 26 (+2 derived)**; coverage column mixes case-level (labs 0.45, fluids 16.6, medication 98.3, invasive 14.8, ventilation 28.8) with feature-level means (others) | A2, A1, **editor ✔** | **WRONG counts; mixed metric** |
| 7 | Limitations + leakage audit | "zero residual horizon overlap (max interval 0.00 min)" | Feature window `[anchor−15, anchor]` **closed** (`s2_features.py:62/81`); label window `[anchor, OR_end]` **closed** (`s1_cohort.py:185`). MAP reading exactly at the anchor minute: **16,695 cases (99.0%)** enter both sides; 648 are <65; 2,602/2,622 D1+ (99.2%) include that minute in their own label; 260 D1+ have an anchor-minute MAP<65 in both. The audit checks only the feature side | A2, A3; **editor ✔ (raw recompute)** | **Claim needs precise restatement** |
| 8 | Limitations 7 | 1,496 (<10 post-anchor readings) "typically shorter or less-invasive cases" | 1,496 = **1,332 with 1–9 readings + 164 with no post-anchor MAP at all**; the 164 have median post-anchor window **216.5 min**; Surgery_start anchors are 42.9% of NBC vs 18.0% overall | A1, A2; **editor ✔** | **WRONG characterization (MNAR + proxy)** |
| 9 | Methods (imputation) | "median imputation with missingness indicators" | `SimpleImputer.fit_transform(X)` on the **full 16,861** before the split (`s3_models.py:79-81`); affects logistic rows only (trees use native NaN) | A2, A3; **editor ✔** | **Protocol defect** |
| 10 | Calibration | "slope 0.909 / intercept 0.008 (log-odds scale)" | `np.polyfit(p_cal, yte, 1)` = OLS on the **probability** scale; isotonic map is *not* identity (raw top decile 0.789→0.402; calibrated 0.436→0.405; Brier 0.1905→0.1190) | A2, A3; **editor ✔** | **Scale label wrong; calibration itself real** |
| 11 | Abstract / Table 4 | XGBoost AUPRC 0.347 (0.309–0.387), AUROC 0.722 (0.697–0.745); all 8 model rows | all 32 cells + 16 bootstrap CIs reproduce exactly from `s3_metrics.json`; bootstrap resamples y and p with the **same index vector** (no fit/eval mismatch); gate PASS 10/10 | A1, A2, A3, A4, **editor ✔** | **STANDS UP** |
| 12 | Table 2 | 14 definitions, D1 = 2,622 (15.55%) | all 14 counts reproduce from `s1_labels_postanchor.csv` (0/16,861 disagreements per case) | A1, A3, **editor ✔** | **STANDS UP** |
| 13 | Results (external) | AUPRC 0.160, AUROC 0.751, Brier 0.179, prevalence 5.73% | recomputed exactly from `vitaldb_predictions.csv` (AUROC 0.7512); "no refitting" true in code | A3, A1, **editor ✔** | **STANDS UP** |
| 14 | Title / Abstract / cover letter | "cumulative hypotension **burden**" | D1 = ≥30% of a case's own recorded readings <65 among ≥10 readings; required low readings runs **3 → 77** (median case: 9 of 30). Not a time-dose | A1; **editor ✔** | **OVER-CLAIM — reframe** |
| 15 | Methods:126 / Table 7 | external D1 "computed identically" | external median 4,356 samples/case → a positive label needs ≥30% = **≈1,307 samples ≈ 43.6 cumulative minutes** <65 vs 9 isolated readings internally; 214 zero-MAP cases silently labelled negative (and 214 is also the event count) | A1, A2; **editor ✔** | **MISLEADING — disclose + sensitivity** |
| 16 | Abstract:29 / Discussion | "higher in women and younger patients"; "performance fell with age" | stratum prevalence vs AUPRC: Spearman ρ = **0.50** (p = 0.17) on test-set prevalence (A1's 0.883 used cohort-level prevalence); AUPRC:prevalence ratios: women 2.11 = men 2.11 (sex ordering reverses), age <50 1.89 / 50–64 2.13 / ≥65 2.05 (no gradient), underweight 6.03 (outlier) | A1; **editor ✔ (own ratios)** | **PREVALENCE ARTEFACT — reframe** |
| 17 | Discussion (external) | "absolute probabilities did not transport" | the transported model is the **raw, uncalibrated** one; internally its mean prediction is 0.397/0.410 (full model, `core_benchmark.json`) vs prevalence 0.1555 — it over-predicts internally too | A1, A2; **editor ✔** | **FRAMING — not transport-specific** |
| 18 | Discussion / DCA | positive net benefit "up to ≈0.58"; temporal "0.46–0.74" | patient NB = **9.9×10⁻⁵** at 0.58 and **<0.01 from 0.36**; temporal last positive **0.45**, re-positive window **0.66–0.73** (manuscript says 0.46 / 0.66–0.74; audit trail says 0.73) | A1, A2, A4; **editor ✔** | **OVER-CLAIM — rewrite** |
| 19 | Cohort | 19,114 → 17,103 → 16,861 waterfall; all exclusion counts | reproduces exactly (8 + 1,632 + 371 + 242; 3,156,668 max OR minutes; anchors 13,834/3,027; OR median 167 min) | A1, A3, **editor ✔** | **STANDS UP** |
| 20 | "OR window shorter than 60 minutes" | duration-based exclusion | implementation is **<60 vital-sign records** (`obs_per_pid`, `s1_cohort.py:113`); 383 excluded cases actually have windows ≥60 min | A3 | **MISNOMER — reword** |
| 21 | "nMAP non-null in 19.89% of case-minutes" | case-minute rate | artefact computes a **whole-table row non-null rate**; true case-minute rate 19.78% | A3 | **REWORD** |
| 22 | "206 candidate predictors" | 206 | dictionary lists 206 features but `n_features` header says 207; **205 numeric columns** enter the model (after dropping 2 object columns); domain table must include `medication_derived` (2) | A2, A3, **editor ✔** | **RECONCILE to 205 numeric / 206 incl. categorical** |
| 23 | References | 18 refs, contiguous | refs **[9] and [13] never cited**; first-citation order 1,16,17,15,2,… non-sequential; [10–12] misattached to the audit-trail sentence; [15] Walsh 2013 cited as an ML external-validation study | A4 | **FIX** |
| 24 | Additional file 2 (TRIPOD+AI) | "completed reporting checklist" | shipped file is a **Chinese 24-item working draft** with ⚠️/⏳ flags and internal notes; item 11 (EPV) marked ✅ although the manuscript has no sample-size statement; item 4 claims a 2015-11~2018-10 period the manuscript never states | A4; **editor ✔** | **REWRITE in English, honest** |
| 25 | Data availability | release v1.0.0 + MANIFEST checksums | public tree ships `review/*`, `STATUS.md`, `NOTES_zh.md`, `GITHUB_DEPOSIT_SOP.md`, `author_verification_statement.md`, `external_validation_plan.md`, `results/_round1_subgroup_n.json`, and **`manuscript/irb_waiver_request_template.md` — which contradicts the no-waiver-letter ethics statement**; MANIFEST covers 21 results files only (no scripts, config, `results/ext/*`, fig6) | A4; **editor ✔ (gh api)** | **CLEAN + REBUILD MANIFEST + RE-RELEASE** |
| 26 | Table 7 (external prevalence) | 15.55% | temporal test-set prevalence is 291/1,818 = **16.01%** | A1, A2 | **WRONG cell** |
| 27 | Table 5 (BMI rows) | rows imply full coverage | BMI rows sum to **3,341**; 32 BMI-missing test cases dropped from the strata | A1, A2 | **DISCLOSE** |
| 28 | "12 keyword categories" vs 13 groups | — | `procedure_groups` has 13 groups incl. NO_SURGERY (6); Table 1 omits it | A1, A2 | **RECONCILE** |

Editor-verified numbers that were NOT in any reviewer's list (editor's own finds): Table 1 surgery-group counts (stale, sum 17,330), age 51.3 (16.5) → 52.9 (17.7), BMI 25.7 (5.4) → 27.8 (7.0), Table 3 domain counts stale (ventilation 20→47, labs 6→12, medication 51→26+2) and the "every domain ≥95% feature-level completeness" sentence contradicts derived-vitals 89.8%.

---

## 4. Graded consolidated issue list (deduplicated, editor-verified)

### Tier 0 — conclusion-framing / acceptance-blocking

| ID | Issue | Editor adjudication |
|---|---|---|
| T0-1 | **D1 is a reading-fraction, not cumulative time-dose** (3→77 low readings required; median 9 of 30). "Cumulative burden" over-claims in title/abstract/cover letter | **Keep D1** (frozen with author sign-off 2026-10-20); reframe everywhere as "≥30% of recorded post-anchor MAP readings below 65 mmHg" and drop unqualified "cumulative burden"; title to "…intraoperative hypotension **exposure**…" (author to confirm title change) |
| T0-2 | **External D1 is a different endpoint** (≈43.6 min <65 vs 9 isolated readings); "computed identically" misleading; 214 zero-MAP cases silently negative | Disclose with numbers; add absolute-time external sensitivity; report restricted external cohort (3,521 informative cases) |
| T0-3 | **Subgroup AUPRC ordering is a prevalence artefact** (sex ordering reverses on normalisation; age gradient attenuates; underweight 6.03 outlier) | Move Table 5 to supplement; report stratum prevalence + AUPRC:prevalence ratio; rewrite abstract claim |
| T0-4 | **Anchor-minute shared by feature and label windows** (99.0% of cases); "zero residual horizon overlap" invites a false disjointness reading | Restate precisely; add half-open-window sensitivity analysis |
| T0-5 | **NBC rule is MNAR with an anchor proxy** (42.9% Surgery_start among NBC vs 18.0% overall; `anchor_is_intubation` gain 72.2 = #3 feature; NBC cases scored lower 0.309 vs 0.406); 164 "negative" cases have no post-anchor MAP at all and 216.5-min windows | Add restricted-cohort (15,365) primary analysis; report the decomposition; fix Limitation 7 |
| T0-6 | **Anchor split 82.1/17.9 wrong in 5 places** (Figure 1 prints 82.0/18.0) | Correct to 82.0%/18.0% everywhere; add gate guard |
| T0-7 | **Observations count 3,559,993 wrong** (computed pre-filter; true 3,379,173 for 16,861) | Fix code + text; add to audit trail |
| T0-8 | **Public package ships an IRB-waiver template contradicting the ethics statement** + internal review files; MANIFEST covers 21 files only | Clean repo, rebuild MANIFEST, new release tag, update availability statement |

### Tier 1 — must-add analyses / must-fix methods

| ID | Issue | Action |
|---|---|---|
| T1-1 | Imputation fitted on full cohort before split (logistic rows) | Fit within training fold; re-run; update Table 4 |
| T1-2 | Calibration slope/intercept mislabeled (probability vs log-odds) | Fix label; keep numbers; describe method |
| T1-3 | Transported model carries density features with no external support (11/53 zero coverage; 72% of gain from untransportable features; `anchor_is_intubation`/`or_year` frozen constants; `anchor_minus_or_start` redefined) | Report external coverage table; add physiology-only subset transport sensitivity |
| T1-4 | External absolute calibration never demonstrated (top decile mean_p 0.804 vs observed 0.190) | Add external calibration slope/intercept + calibration-in-the-large internally |
| T1-5 | External funnel 6,388→3,735 not reported | Add funnel sentence |
| T1-6 | Temporal split not prospective in the claimed sense (2018 train cases fill 92% of the 180 min before the median 2018 anchor) | Cut "functions as a prospective check"; disclose |
| T1-7 | Subgroup multiplicity (9/4/8 post-hoc strata, no control) | Supplement + exploratory framing |
| T1-8 | Table 1 stale (surgery groups sum 17,330; age; BMI; female 8,502 vs trail 8,506) | Regenerate from artefacts |
| T1-9 | Table 3 stale domain counts + mixed coverage metric + "≥95% completeness" contradiction | Regenerate with dual columns |
| T1-10 | DCA over-claims (NB 9.9e-05 @0.58; <0.01 from 0.36; temporal 0.45/0.66–0.73) | Rewrite with verified values |
| T1-11 | Audit trail missing the external block + ~15 items; `female_n` 8,506; stale 13-min note | Rebuild audit trail |
| T1-12 | TRIPOD+AI checklist is a Chinese working draft | Rewrite in English, honest status |
| T1-13 | References [9]/[13] uncited; non-sequential order; misattachments | Fix citations |
| T1-14 | 34 cases with anchors 2–12.5 h after OR start (325 >60 min); clinically impossible pre-anchor events (Extubation×4, CPR×1, Mayfield×3, lag 2,853 min); nominal 15-min window extends before OR start for 46.2% of cases | Disclose in Limitations |
| T1-15 | Must-cite literature (PROBAST, Vickers, Van Calster, Hatib, Riley) | Add references |

### Tier 2 — wording / minor consistency
- Abstract: "1,000 bootstrap confidence intervals were secondary" misdescribes the method; 5.7% vs 5.73%; "fewer than 60 sustained cases (0.3%)" vs O1–O4 sum **98 (0.6%)**; keyword count.
- Methods: "<60 minutes" → "<60 vital-sign records"; "19.89% of case-minutes" → "19.78% of case-minutes" (or state the artefact's definition); 206 vs 205 numeric predictors; `medication_derived` domain omitted from Table 3; ABG 11.7% is of the 76 lab cases (0.11% of cohort); "12 categories" vs 13 groups; incomplete 53-feature description; undisclosed propofol mcg→mg drop (1,981/17,683 = 11.2%) and phenylephrine drops→mcg (6 rows); `map_slope`/`map_minutes_since_last` vs the sparsity limitation (internal tension); fuzzy-match description (substring, not token-based); crystalloid_in_ml always 0 / other_output_ml sign bug (verify + fix or disclose); 41 `*_15min` features computed over longer windows.
- Tables: Table 7 temporal prevalence 16.01%; Table 5 BMI rows sum 3,341 (32 missing).
- Duplicated DCA sentences (:385–389); abbreviation list omits SBP/DBP/HR/ASA but lists unused IOH/AKI/DUA; grammar nits.

### Tier 3 — format
- BMC Declarations subheads; figure legends vs PNGs (A4 verified they match); release-notes title ("sustained") stale.

---

## 5. Consensus / complementarity / disagreement

**Consensus (≥2 experts, editor-verified):** anchor split (A4+A3+editor); imputation pre-split (A2+A3+editor); calibration scale (A2+A3+editor); female_n (A4+A3+editor); Table 1/Table 3 staleness (A1+A2+editor); orphan fragment + four/five (A1+A4+editor); external density drift (A2+A3); limitations list broken (A1+A4).

**Complementarity:** A1 caught the clinical-semantic layer (what D1 means, endpoint commensurability, prevalence artefacts); A2 caught the design layer (label boundaries, MNAR, transport support, calibration protocol); A3 caught the arithmetic/provenance layer (denominators, audit-trail gaps, code bugs); A4 caught the venue layer (reporting checklist, package hygiene, citation mechanics). No single expert spans more than two layers — the panel composition paid off.

**Disagreements — editor adjudications:**
1. **A2-F3 (SEVERE: "isotonic regression is an identity map; the shipped model is uncalibrated") — DEMOTED to MINOR.** Editor re-ran the artefact check: the isotonic map is materially non-identity (raw top decile 0.789→0.402 observed; calibrated 0.436→0.405; Brier 0.1905→0.1190). A2's cited line (`ext_pipeline.py:398`) does not exist (file is 228 lines). The internal calibration claim **stands**; the valid kernel — the cover letter should say calibration was internal-only — is kept.
2. **A2-F5 (MAJOR: "184/291 = 63% of temporal-test positives overlap their own pre-anchor window") — DEMOTED to MINOR.** Editor recomputed: under a strict window-intersection criterion the overlap is the shared anchor minute only (already T0-4); under a length criterion 99.0% (not 63%). A2's "median 129 / max 450 min" figures equal the label-window lengths of temporal-test positives, not an overlap. The genuine temporal-split weakness is T1-6 (non-prospective density), retained.
3. **A1-S1 remedy (re-specify D1 as a time-anchored cumulative exposure) vs the frozen design decision.** Editor adjudication: D1 is frozen with author sign-off (2026-10-20); re-specification would invalidate every downstream artefact and re-open a signed decision. **Chosen path: keep D1, reframe honestly** (T0-1). Flagged to the author as a conscious trade-off: the alternative is a full outcome re-specification and re-run.
4. **A1's ρ = 0.883 vs editor's ρ = 0.50** for prevalence-vs-AUPRC: attributable to cohort-level vs test-set prevalence. Both support T0-3; the editor's test-set ratios are the ones reported.

---

## 6. Priority must-fix list (with desk-reject flags)

**DESK-REJECT / editor-blocking (must clear before any submission):**
1. T0-6 anchor split 82.0/18.0 (5 places + Figure 1 already correct) — a wrong headline number contradicts the paper's own figure.
2. T0-8 package hygiene: the public IRB-waiver template contradicts the Declarations; internal review files in a public DUA repo.
3. T1-12 TRIPOD+AI checklist shipped as a Chinese working draft while the cover letter calls it "completed".
4. T0-7 + T1-8 + T1-9 numbers that do not trace to artefacts (observations count, Table 1, Table 3).

**Must-add analysis (changes Results, not just wording):**
5. T0-4 anchor-minute sensitivity (half-open feature window).
6. T0-5 restricted-cohort (15,365) primary performance.
7. T0-2/T1-3/T1-4 external absolute-time label, restricted external cohort, external calibration slope/intercept, physiology-only transport.
8. T0-3 subgroup prevalence-normalised table.

**Must-reword:** T0-1, T1-2, T1-6, T1-10, T1-14, T1-15, Tier-2 list.

---

## 7. What stands up (do NOT change these)

- **Statistical kernel is sound.** A3 reproduced every headline number from artefacts and raw CSVs: cohort waterfall, all 14 outcome definitions (0/16,861 per-case disagreements), all 8 model rows × (AUPRC, AUROC, Brier, 16 bootstrap CIs), calibration, DCA, treat-all/MAP-only benchmarks, subgroup strata sizes, and the full external block (AUROC 0.7512 from `vitaldb_predictions.csv`). The bootstrap resamples y and predictions with the **same index vector** — no fit/eval mismatch (the bug class that sank a previous project). `s5_gate.py` PASS 10/10.
- **Leakage audit on the feature side is real**: all seven time-stamped domains truncated at the anchor, max interval 0.00 min, ALL_PASS.
- **No-refitting claim on the external step is true in code** (`ext_pipeline.py`: fit only on MOVER, `predict` on VitalDB).
- **Ethics statement** is internally consistent, names the exempting IRB, contains no waiver-letter language (but see T0-8 for the package-level contradiction).
- **Abstract structure** (≤350 words, four paragraphs, 7 keywords), Vancouver style, British spelling, figure legends match shipped PNGs, cover-letter headline numbers match the manuscript (except where listed).
- **The framing reframes are cheap**: nearly every Tier-0 item is a wording + disclosure + sensitivity-analysis fix, not a new study.

---

## 8. Recommended handling path

**A) Restructure and resubmit as the same article type (development + transportability check).** The paper's real contribution — an honest, auditable, leakage-checked development study on a sparse public OR resource with a quantified transportability check — survives every finding. The fixes are: reframe D1 (T0-1), disclose the external endpoint mismatch (T0-2), normalise the subgroup claims (T0-3), restate the leakage boundary (T0-4), add the restricted-cohort primary analysis (T0-5), and clean the package (T0-8). Downgrading the article type is not warranted; the strongest finding (auditability under sparsity) should be headlined more confidently, the weakest (subgroup ordering) demoted.

---

## 9. Process lessons — what the gates could not catch, and the new guards

The consistency gate passed 10/10 while the manuscript contained: a wrong anchor split repeated 5 times, a stale Table 1 (surgery groups summing to 17,330), a stale Table 3, an orphaned paragraph, a four-vs-five count contradiction, and a wrong observations count. The gate checks enumerated strings; **design-layer and second-occurrence defects are invisible to it.** New guards to add to `s5_gate.py`:

1. **Numbered-list integrity** — every indented continuation line in a `###` section must follow a `N. **Header.**` item; orphan fragments fail.
2. **Count-word vs item-count** — "contributes N elements" must equal the number of listed items; "N implications follow" must equal the ordinal words.
3. **Anchor-split guard** — assert 13,834/16,861 → 82.0 and 3,027/16,861 → 18.0 derived from `s1_cohort.json`.
4. **Observations-count guard** — recompute the OR-window row count for the analytic cohort and compare with the manuscript string.
5. **Table-traceability spot checks** — Table 1 surgery rows must sum to 16,861 and match `s2_procedure_groups.csv`; Table 3 domain counts must match `s2_feature_dictionary.json`.
6. **md↔docx sync probes** — the fixed defect strings must be absent from both, and every `###` heading must appear in the docx.
7. **Citation-order guard** — in-text citation numbers must be non-decreasing on first use and every reference must be cited.
8. **Audit-trail completeness** — every headline number in the manuscript must appear as a row in `s4_audit_trail.csv` (the external block currently has zero rows).

---

*Editor's certification: all Tier-0 items above were independently recomputed by the editor from artefacts or raw CSVs (rows marked ✔). Two reviewer findings were demoted after failed reproduction (§5). The consolidated report, the four expert files, and this report are the audit trail for the revision that follows.*
