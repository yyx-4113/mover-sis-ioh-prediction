# A4 — Journal fit / reporting-compliance review (BMC Anesthesiology; TRIPOD+AI)

**Manuscript:** `manuscript/manuscript_v0.1.md` (v0.1) · **Cover letter:** `manuscript/cover_letter_bmc_anesthesiology.md`
**Reviewer role:** independent journal-fit and reporting-standard auditor, reviewing as a first submission. All numbers cited below were recomputed by me from the artefacts named in each finding.

---

## Executive summary

The manuscript is structurally close to BMC Anesthesiology requirements (five sections, four-paragraph structured abstract of 330 words — within the 350-word limit — seven keywords, all seven Declarations subheads in standard order plus authors' information and AI-use statements) and the cover letter's headline numbers match the manuscript exactly. The science-facing numbers I recomputed (cohort waterfall, anchor counts, all 16 Table 4 AUPRC/AUROC/Brier values with CIs, calibration, DCA, external metrics) trace correctly to the artefacts.

However, the submission is **not yet desk-edit clean**. There is one abstract-level numerical error repeated six times and contradicted by the paper's own Figure 1 (anchor split 82.1%/17.9% should be 82.0%/18.0%); Additional file 1 (the audit trail) does not deliver the "every number traceable" claim — it omits the entire external validation, contains a wrong sex count, cites a file that is not shipped, and reports a coverage metric that contradicts Table 3; Additional file 2 (TRIPOD+AI checklist) is a Chinese working draft with stale status flags that marks items complete whose content is absent from the manuscript, while the cover letter calls it "completed"; two references are never cited, first-citation numbering is not sequential, and two citations are attached to sentences they do not support; the Limitations list is visibly broken; and the public reproduction package that the availability statement points to ships internal review files, an IRB waiver-request template, and release notes quoting a different manuscript title. Verdict: **Major revisions**.

---

## Findings

### F1 — [SEVERE] Anchor-split percentages are wrong in six places and contradict Figure 1

【Problem】 The manuscript reports the intubation/surgery-start anchor split as 82.1% / 17.9% in six locations, but the correct rounded values are 82.0% / 18.0%, and the shipped Figure 1 already prints 82.0% / 18.0%.
【Evidence】 Recomputed from the counts the manuscript itself reports: 13,834 / 16,861 = **82.047%** → 82.0%; 3,027 / 16,861 = **17.953%** → 18.0% (confirmed against `results/s1_cohort.json` anchor_source_counts = 13,834 / 3,027). Wrong values at `manuscript/manuscript_v0.1.md:22` (abstract), `:120–121` (Methods), `:253–254` (Table 1, two rows), `:587` (Limitations item 5). Figure 1 (`results/figs/fig1_cohort.png`, bottom caption box) reads "Prediction anchor: Intubation 13,834 (82.0%) | Surgery start 3,027 (18.0%)" — the figure is right, the text is wrong.
【Why it matters】 A wrong number in the abstract, repeated in the body, a table and the limitations, that contradicts the paper's own figure, is the fastest way to lose a numbers-heavy paper's credibility; it also sits inside the reproducibility branding ("every number … traceable"). It will be caught at desk edit.
【Specific fix】 Replace all six occurrences. Paste-ready Methods replacement: "The prediction anchor was the first recorded Intubation event (n = 13,834; 82.0%). Where no intubation event existed, Surgery start was used as a proxy (n = 3,027; 18.0%)." Also fix abstract line 22 ("first intubation event, 82.0%; otherwise surgery start, 18.0%"), Table 1 rows ("13,834 (82.0)", "3,027 (18.0)") and Limitations line 587 ("In 18.0% of cases the anchor was Surgery start rather than intubation").

---

### F2 — [MAJOR] Additional file 1 (audit trail) does not deliver the "every number traceable" claim

【Problem】 The manuscript states that every reported number is traceable through the audit trail (Additional file 1), but the trail omits the entire external-validation section, contains at least one wrong value, reports a coverage metric that contradicts Table 3, references a file that is not shipped, and the anchor-timing IQR printed in the manuscript is produced by no script or artefact.
【Evidence】
(a) `results/s4_audit_trail.csv` (154 data rows) contains **no external-validation rows at all** — no n = 3,735, no 214 events, no AUROC 0.751, no AUPRC 0.160, no Brier 0.179, no mean predicted risk 0.37, no 53-feature internal 0.698/0.710/0.321/0.314 — although Table 7, Figure 6 and the Abstract/Discussion/Conclusions all report them (the values do exist in `results/ext/external_validation.json`, which the trail never cites).
(b) Trail row `cohort.female_n,8506` contradicts manuscript Table 1 "Female sex — n (%) | 8,502 (50.4)" and `results/s2_data_quality.json` gender_values F = 8,502 (8,355 + 8,502 + 4 = 16,861; with 8,506 the total would be 16,865 — impossible).
(c) Trail rows `features.coverage.labs.mean_non_null_pct,0.1695`, `ventilation,0.3283`, `medication,1.0`, `fluids,1.0`, `anesthesia_technique,1.0`, `vitals_nibp,0.9568` read as "coverage" but contradict manuscript Table 3 (0.45, 28.8, 98.3, 16.6, 98.2, 95.1); they are feature-level non-null means (`results/s2_data_quality.json` domain_coverage), a different metric that is never defined.
(d) ~25 of 154 trail rows cite `results/s2_features.csv` (matrix_rows, age_median, male_n, female_n, bmi_median, pre-anchor MAP median, all nine subgroup test-n rows, coverage case counts), but that file is in neither the tag-v1.0.0 repo tree nor MANIFEST.csv — broken source references.
(e) "median of 15 minutes (IQR 11–24)" (`manuscript_v0.1.md:122–123`) and Table 1 "Anchor after OR start, min — median (IQR) | 15 (11–24)" and "Pre-anchor MAP readings … 3 (2–4)": `scripts/s1_cohort.py:384–387` and `scripts/s2_features.py:115–118` compute only p05/p50/p95 (7 / 15 / 46); no p25/p75 exists in any artefact or script, so the IQR 11–24 is produced by nothing. The trail also has no row for OR duration 167 min or the surgical-group counts.
【Why it matters】 The audit trail is the paper's flagship reproducibility claim, repeated as a selling point in the cover letter ("a fully traceable audit trail (Additional file 1)"). A reader following it hits contradictions (female_n, coverage) and dead ends (external numbers, s2_features.csv, anchor IQR) — the claim is currently false in at least five verifiable ways, which converts an advertised strength into a review liability.
【Specific fix】 Regenerate `results/s4_audit_trail.csv` to (i) add external rows citing `results/ext/external_validation.json` for every Table 7 / Figure 6 number; (ii) correct `female_n` to 8502; (iii) relabel the feature-level rows as `…feature_non_null_pct` and add case-level `cases_with_data_pct` rows matching Table 3; (iv) ship `results/s2_features.csv` or repoint those rows to artefacts that exist; (v) add an anchor-timing quartile computation in `scripts/s1_cohort.py` (`"anchor_minus_or_start_min": {"p05":…, "p25":…, "p50":…, "p75":…, "p95":…}`) so the IQR is produced. Until that is done, amend the Methods sentence to: "Every number reported in this manuscript is generated from a result file by the analysis pipeline and is traceable through an audit trail (Additional file 1) that records, for each quantity, its value and the producing artefact." (dropping "and the command that reproduces it", which the trail does not provide for the external numbers).

---

### F3 — [MAJOR] TRIPOD+AI checklist (Additional file 2) is a Chinese working draft that overstates completeness; the cover letter calls it "completed"

【Problem】 Additional file 2 is a 24-item Chinese-language internal table with ⚠️/⏳ status markers and process notes, and it marks at least two items satisfied whose content is absent from the manuscript, while the cover letter advertises "a completed reporting checklist (Additional file 2)".
【Evidence】 `results/s4_tripod_ai.md`: title "TRIPOD+AI (2024) 清单 — 01 SIS 术中低血压预测"; item 11 marked ✅ "n=16861，事件 2622（EPV 充足）" — the manuscript contains **no sample-size or EPV statement anywhere** (no Methods subsection; 2,622 events / 206 predictors ≈ 12.7 EPV is nowhere stated); item 4 marked ✅ with dates "2015-11~2018-10" — the manuscript never states the study period (Methods "Study design and data source" gives no dates); items 21–24 carry ⚠️/⏳ ("须由作者确认", "待作者补充") although the manuscript's Declarations do contain ethics, availability, funding and competing-interest statements; the footer contains internal process language ("稿件已完成 Round-1 + Round-2 修订（v0.1 工作稿）", "三项设计决策已签字冻结（2026-10-20）"). Cover letter line 16: "is accompanied by a completed reporting checklist (Additional file 2)".
【Why it matters】 BMC requires the completed checklist as a submission file in the manuscript's language; a Chinese draft with stale flags fails the journal requirement and contradicts the cover letter, and the overstated items (4, 11) are exactly what a TRIPOD-literate reviewer checks first. The file is also shipped publicly inside the release package (it is in MANIFEST.csv).
【Specific fix】 Replace Additional file 2 with the official TRIPOD+AI (2024) 27-item checklist in English, each item marked "Reported — §x.y" or "Not applicable" against manuscript_v0.1.md; add to Methods a sample-size sentence (e.g., "With 2,622 events and 206 candidate predictors, the full logistic model has ≈12.7 events per predictor; tree ensembles, which do not require an events-per-predictor ratio, were the primary models.") and the data-collection window (e.g., "Cases were recorded between November 2015 and October 2018."); in the cover letter change to "a completed TRIPOD+AI (2024) reporting checklist (Additional file 2)".

---

### F4 — [MAJOR] Two references are never cited, first-citation numbering is not sequential, and two citations are misattached

【Problem】 References 9 and 13 appear in the list but are never cited; first-citation order is 1, 16, 17, 15, 2, 3, 4, 5, 6, 7, 8, 18, 10–12, 14, 15 — not sequential as Vancouver numbering requires; and the [10–12] and [14,15] citations are attached to sentences they do not support.
【Evidence】 Extraction of every in-text citation in `manuscript_v0.1.md` shows no `[9]` and no `[13]` anywhere; [16] is first cited at line 58, [17] at line 60, [15] at line 61 — all before [2,3] at line 65; line 229 cites [10–12] (the XGBoost paper, the LightGBM paper and the Oyarzun medRxiv preprint) for the audit-trail sentence, which none of the three supports; line 527 cites [14,15] for "machine-learning models for intraoperative risk from comparable operating-room resources, including external-validation studies", but [15] (Walsh 2013) is an observational MAP–outcome study, while [13] (Chiu, an ML model study) — the reference that would fit — is the uncited one. Reference list length is 18 entries; 16 distinct numbers are cited.
【Why it matters】 BMC copyeditors renumber, but non-sequential first-citation order plus two orphan entries signals careless reference management, and the misattached citations are accuracy errors a reviewer can check in minutes — especially [15] cited as an ML external-validation study and [10–12] cited for a sentence about the audit trail.
【Specific fix】 Renumber the list in order of first citation; cite scikit-learn in the Software paragraph ("Analyses used Python 3.13 with pandas 2.3.3, scikit-learn 1.9.0 [9], XGBoost 3.4.1 [10] and LightGBM 4.7.0 [11]."); delete the "[10–12]" at line 229; change line 527 to "…including external-validation studies [13,14]."

---

### F5 — [MAJOR] The Limitations list is broken by an orphaned fragment, and "What this study adds" says four but lists five

【Problem】 After Limitations item 10 the list continues with an unnumbered orphaned paragraph that begins mid-sentence, and the "What this study adds" section promises "four elements" but presents five numbered items.
【Evidence】 `manuscript_v0.1.md:606` ends item 10 ("…relative to the development cohort."); lines 607–612 are an indented continuation carrying **no list number** and opening mid-sentence: "pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg." Line 616 states "this study contributes four elements that are under-reported…", followed by items 1–5 (lines 619–643).
【Why it matters】 A visibly broken numbered list and a 4-vs-5 count mismatch in consecutive sections are returned for copy-editing before review, and the orphaned fragment suggests a deletion accident that may have removed the item's opening clause.
【Specific fix】 Insert the missing item at line 607: "11. **The model adds little beyond the current pressure.** The strongest predictor is the pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the fraction of pre-anchor readings already below 65 mmHg." And at line 616 change "contributes four elements" to "contributes five elements".

---

### F6 — [MAJOR] The public reproduction package ships internal review files and an IRB waiver-request template, and its release notes quote a different manuscript title

【Problem】 The GitHub release v1.0.0 that the availability statement points readers to contains internal working files and an unfilled IRB waiver-request template, and its release notes describe the manuscript under a different title ("sustained …") than the submitted one ("cumulative …").
【Evidence】 The tag-v1.0.0 repo tree (GitHub API) lists `review/REVIEW_round1_2026-10-20.md` … `review/A4_venue.md`, `STATUS.md`, `NOTES_zh.md`, `GITHUB_DEPOSIT_SOP.md`, `author_verification_statement.md`, `external_validation_plan.md`, `results/_round1_subgroup_n.json`, and `manuscript/irb_waiver_request_template.md`. The release body quotes the manuscript as *"Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: model development and internal and external validation"* — versus the actual title "Prediction of cumulative intraoperative hypotension burden … development and internal validation in MOVER/SIS with external validation in VitalDB". ("Sustained" is also substantively wrong for this paper: D1 is an exposure-fraction definition explicitly contrasted with sustained-grid definitions in Table 2.)
【Why it matters】 Editors and reviewers follow the availability link; finding internal review rounds, Chinese working notes and a waiver-request template in the public package contradicts the manuscript's exemption-based ethics framing and the first-submission posture, and the stale "sustained" title mislabels the work at the exact URL the paper advertises.
【Specific fix】 Cut a clean tag (e.g., v1.0.1) containing only `scripts/`, `config/`, `results/` (including `ext/` and `figs/`), `manuscript/` (md + docx), `MANIFEST.csv`, README and LICENSE; remove `manuscript/irb_waiver_request_template.md` and the `review/` directory from the public repository; correct the release-notes title to the exact submitted title; update the availability statement in the manuscript to the corrected tag URL.

---

### F7 — [MAJOR] The checksum manifest covers only 20 result files — not the code, config, external-validation artefacts or Figure 6

【Problem】 MANIFEST.csv (project root, and a byte-identical copy in the release) lists only 20 files under `results/`, omitting every script, the configuration files, all `results/ext/*` external-validation artefacts and `results/figs/fig6_external_validation.png`, although the availability statement advertises "a manifest of file checksums" for the package from which every number is generated.
【Evidence】 MANIFEST.csv = header + 20 rows (fig1–fig5, s1/s2/s3/s4 json/csv/html); no `scripts/*.py`, no `config/config.yaml`, no `results/ext/external_validation.json`, no `results/figs/fig6_external_validation.png`, no manuscript files. The tag-v1.0.0 tree confirms those files exist but are not manifested; the Table 7 / Figure 6 numbers trace to `results/ext/external_validation.json`, which is therefore not checksum-attested, and the code that "reproduces" the numbers is not attested either.
【Why it matters】 The manifest is the integrity mechanism behind the reproducibility claim; as shipped it attests neither the code nor the external-validation artefacts, so "together with a manifest of file checksums (MANIFEST.csv)" overstates what a reader can verify.
【Specific fix】 Regenerate MANIFEST.csv over every file in the release (scripts/, config/, results/ including ext/ and figs/, manuscript/, README) with sha256 and byte size, and amend the availability sentence to: "All analysis code, the configuration file, the audit trail, and the aggregate result files from which every number in this manuscript is generated are available at <corrected URL>, together with SHA-256 checksums for all shipped files (MANIFEST.csv)."

---

### F8 — [MINOR] The decision-curve paragraph states the same net-benefit numbers twice in consecutive sentences

【Problem】 Results "Calibration and clinical usefulness" repeats the DCA net-benefit values verbatim in back-to-back sentences.
【Evidence】 `manuscript_v0.1.md:385–389`: "The absolute net benefit at the decision-relevant thresholds was small (e.g., 0.050 and 0.058 at 0.15 on the two splits, and 0.079 and 0.085 at 0.10) … At a threshold of 0.15, close to the outcome prevalence, net benefit was 0.050 and 0.058 respectively; at a threshold of 0.10 it was 0.079 and 0.085."
【Why it matters】 Verbatim repetition in a results section reads as a copy-paste error at edit stage.
【Specific fix】 Delete the second pair of sentences and merge: "The absolute net benefit at the decision-relevant thresholds was small (0.079 and 0.085 at threshold 0.10, and 0.050 and 0.058 at 0.15 — close to the outcome prevalence — on the patient-level and temporal splits respectively), so the clinical usefulness demonstrated by the curve is modest."

---

### F9 — [MINOR] The abstract misdescribes the bootstrap ("1,000 bootstrap confidence intervals were secondary")

【Problem】 The abstract Methods sentence treats the bootstrap resamples as a secondary metric.
【Evidence】 `manuscript_v0.1.md:27–28`: "AUPRC was the primary metric; AUROC, Brier and 1,000 bootstrap confidence intervals were secondary…" The body (line 214) correctly says "Confidence intervals came from 1,000 bootstrap resamples of the test set."
【Why it matters】 Misstates the method in the most-read part of the paper.
【Specific fix】 "AUPRC was the primary metric; AUROC and Brier score were secondary, each with 95% confidence intervals from 1,000 bootstrap resamples; out-of-fold isotonic calibration and decision curve analysis were performed."

---

### F10 — [MINOR] DCA upper bound in text (0.74) disagrees with the audit trail (0.73)

【Problem】 The temporal-split net benefit is described as returning to positive "between approximately 0.66 and 0.74", but the audit trail records the positive-up-to threshold as 0.73.
【Evidence】 `manuscript_v0.1.md:383` and `:486` ("0.66–0.74"); `results/s4_audit_trail.csv` row `dca.temporal.net_benefit_positive_up_to_thr,0.73`.
【Why it matters】 A text-versus-artefact mismatch inside the paper's own traceability trail.
【Specific fix】 Change both places to "approximately 0.66 and 0.73".

---

### F11 — [MINOR] Grammar and awkward phrasing

【Problem】 Several sentences are ungrammatical or logically loose.
【Evidence】 `:129–130` "at least 10 MAP measurements after the anchor, of which at least 30% were below threshold"; `:190` "an arterial mean arterial pressure track (Solar8000/ART_MBP or EV1000/ART_MBP)"; `:88–90` "to report it under an explicit leakage audit"; `:487` "thresholds near to moderately above the outcome prevalence (roughly 0.10–0.30)" — 0.10 is *below* the 0.1555 prevalence.
【Why it matters】** Language quality is an explicit BMC acceptance criterion; these are the sentences a copyeditor will mark.
【Specific fix】** "…at least 10 MAP measurements after the anchor, at least 30% of which were below threshold"; "an arterial-line MAP track (Solar8000/ART_MBP or EV1000/ART_MBP)"; "and to report it with an explicit leakage audit"; "thresholds around and moderately above the outcome prevalence (roughly 0.15–0.30)".

---

### F12 — [MINOR] The abbreviations list does not match text usage

【Problem】 The list includes abbreviations never used in the text and omits abbreviations that are used.
【Evidence】** `manuscript_v0.1.md:665–670` lists IOH, AKI and DUA, none of which appears in the body; SBP, DBP and HR are used at `:193` ("MAP, SBP, DBP, HR, a heart-rate variability proxy and SpO₂") and ASA at `:584` ("ASA physical status was not available"), but none is in the list.
【Why it matters】** BMC requires the abbreviations list to reflect usage; mismatches are a standard desk edit.
【Specific fix】** Remove IOH, AKI and DUA from the list (or use them in the text) and add "ASA, American Society of Anesthesiologists; DBP, diastolic blood pressure; HR, heart rate; SBP, systolic blood pressure."

---

### F13 — [MINOR] The medication unit-mismatch filter silently drops 11.2% of propofol records and is undocumented

【Problem】 Medication dose features keep only rows in the expected unit, silently discarding 1,981 of 17,683 propofol records (and 6 phenylephrine records with a "drops" unit); the manuscript documents only the height/weight/BMI cleaning.
【Evidence】** `scripts/s2_features.py:359–361` (`su = s[s.Drug_units == unit]`); `results/s2_data_quality.json` medication_unit_mismatch.propofol: n_rows_all 17,683, n_rows_expected_unit 15,702, mcg 1,981; phenylephrine: 1,903 rows, 6 in "drops". Manuscript Methods (`:142–167`) mentions no medication-unit handling.
【Why it matters】** TRIPOD+AI expects predictor construction and data cleaning to be reported; dropped wrong-unit rows contribute zero dose rather than missing, a material and currently undisclosed data-handling decision in the medication domain (26 predictors).
【Specific fix】** Add to Methods: "Medication dose features were computed from records whose unit matched the expected unit for each drug; 1,981 of 17,683 propofol records (11.2%) were recorded in mcg rather than mg and were excluded from dose sums rather than converted, and 6 phenylephrine records carried a non-standard unit and were likewise excluded."

---

### F14 — [MINOR] Table 3 omits the "Derived medication indices" domain (204 of 206 predictors) and mixes dash counts with percentages

【Problem】 The leakage-audit/coverage table lists 12 of the 13 predictor domains, silently dropping "Derived medication indices" (2 predictors), and two rows show "—" for case counts beside numeric percentages.
【Evidence】** `manuscript_v0.1.md:145–148` lists 13 domains summing to 206 (3+6+14+12+36+6+2+32+47+26+2+12+8); Table 3 (`:326–339`) lists 12 rows summing to 204, with no derived-medication row, although `results/s2_data_quality.json` domain_coverage contains `medication_derived` (n_features 2, mean_non_null_pct 0.5625); rows at `:329` and `:334–335` show "—" with 99.7 / 89.8 / 99.6.
【Why it matters】** The leakage audit is one of the paper's self-advertised strengths; an incomplete audit table undercuts it and invites a query.
【Specific fix】** Add the row "| Derived medication indices | 2 | — | 56.3 | 0.00 |" to Table 3 (56.3% is the feature-level non-null rate; ideally compute and report the case-level count), and either fill the "—" cells or retitle the column "Cases with data (n) or feature-level non-null (%)" with a footnote defining the two metrics.

---

### F15 — [MINOR] Two small aggregate-claim inconsistencies

【Problem】 The abstract rounds the external prevalence differently from the body, and a collective claim about sustained definitions is arithmetically ambiguous.
【Evidence】** `:35` "Externally (VitalDB, prevalence 5.7%)" versus `:449` and Table 7 "5.73%"; `:545–546` (and `:626–627`) "sustained definitions at conventional thresholds identified fewer than 60 cases here" — Table 2's four sustained-grid definitions (O1–O4) sum to **98** cases (15+54+2+27), although each individually is ≤ 54.
【Why it matters】** Minor, but both are the kind of mismatch that makes a careful reviewer distrust other aggregates.
【Specific fix】** Use "5.73%" in the abstract; rephrase to "each sustained-grid definition identified fewer than 60 cases here (15 to 54 cases)".

---

## § Stands up (verified as correct)

1. **Abstract structure and length.** Four paragraphs (Background/Methods/Results/Conclusions), counted at **330 words including labels / 326 excluding** — inside BMC's 350-word limit; 7 keywords, inside the 3–10 range. (Counted programmatically from `manuscript_v0.1.md:14–44`.)
2. **Cohort and split arithmetic.** 19,114 − 8 − 1,632 − 371 = 17,103; 17,103 − 242 = 16,861; 13,834 + 3,027 = 16,861; 8,355 + 8,502 + 4 = 16,861; 13,488 + 3,373 = 15,043 + 1,818 = 16,861; 16,861 − 1,496 = 15,365; 3,735 − 214 = 3,521 — all recomputed and matching `results/s1_cohort.json` and `results/s2_data_quality.json`. Surgical-group counts sum to 16,861 and match `procedure_groups.counts` exactly.
3. **Every Table 4 performance number traces with correct rounding.** I recomputed all 16 AUPRC/AUROC pairs and both CIs against `results/s3_metrics.json` (e.g., XGBoost patient 0.3473 → 0.347, CI 0.3089–0.3875 → 0.309–0.387; LightGBM patient 0.3368 → 0.337, CI 0.6986–0.7453 → 0.699–0.745) plus all Brier values, the calibration chain (0.1905→0.191, 0.119, slope 0.909, intercept 0.008; temporal 0.1935→0.194, 0.1217→0.122, 0.9338→0.934, 0.0058→0.006), the DCA values (0.0787→0.079, 0.0503→0.050, 0.0848→0.085, 0.0579→0.058), the MAP-only benchmark (0.2842→0.284; increments 0.0132/0.0131→0.013), and all 18 subgroup AUPRCs in Table 5.
4. **External numbers match the artefact and the cover letter.** `results/ext/external_validation.json`: n 3,735; 214 events; prevalence 0.0573 → 5.73%; AUPRC 0.160 (0.1291–0.2021 → 0.129–0.202); AUROC 0.7507 → 0.751 (0.7133–0.7844 → 0.713–0.784); Brier 0.1789 → 0.179; pred_mean 0.365 → 0.37 — and the cover letter's "AUROC 0.751 … mean predicted risk 0.37 vs observed prevalence 0.057" matches exactly.
5. **Cover letter ↔ manuscript consistency (headline claims).** Title quoted verbatim; AUPRC 0.347 / AUROC 0.722; temporal 0.339; MAP-only 0.284 vs 0.347; incremental net benefit 0.013; NB thresholds 0.58 / 0.46; TRIPOD type 2b; the transportability framing; the ethics exemption statement; the availability statement — all consistent between letter and manuscript (the one exception, "completed reporting checklist", is finding F3).
6. **Ethics statement is internally consistent and BMC-conformable in form.** It names the exempting IRB, states the exemption basis (pre-existing de-identified data under a DUA), reports no approval number explicitly, and contains no waiver-letter language — I searched the manuscript and cover letter for "waiver"/"exemption letter" and found none (the waiver-request template exists only as a separate file in the repo; see F6). Declarations contain all seven BMC subheads in the standard order plus authors' information and an AI-use statement.
7. **Spelling and figure legends.** Body text is consistently British ("anaesthesia", "standardisation", "generalisability", "prioritise"); every American spelling found is inside a proper noun (Anesthesiology, journal titles) where it must be retained. Figure 1's waterfall numbers match the text; Figure 2 shows exactly the 14 definitions with D1 highlighted (1-dp labels consistent with Table 2); Figure 6 is the advertised three-panel external layout (ROC / PR / predicted-risk distribution) for n = 3,735 at 5.73%.
8. **The availability URL resolves and the core claims are plausible.** Release v1.0.0 exists (published 2026-10-20T09:58Z, not a draft); the tag tree contains `scripts/run_all.py`, `config/config.yaml`, `results/s4_audit_trail.csv`, `results/ext/external_validation.json` and `results/figs/fig6_external_validation.png`, and the release notes' key results (0.347/0.722 internal; 0.160/0.751 external) match the manuscript.

---

## § Questions for the authors

1. Where is the sample-size/EPV justification? The TRIPOD checklist marks it satisfied ("EPV 充足"), but no EPV statement appears in the manuscript; what is the intended events-per-predictor for the full logistic model (2,622/206 ≈ 12.7), and how was adequacy judged for the tree models?
2. What is the study period of the MOVER/SIS extraction? The checklist records 2015-11 to 2018-10, but the manuscript states no dates; please state the observation window in Methods (TRIPOD+AI item 4).
3. Which artefact produces the anchor-timing IQR "15 (11–24)" and the pre-anchor MAP "3 (2–4)"? Neither p25/p75 appears in any shipped artefact or script.
4. In VitalDB, exactly 214 cases are D1-positive and exactly 214 are negative-by-construction (<10 post-anchor measurements) — is that equality a coincidence, and was the same <10-measurement rule applied as in MOVER (1,496 cases)?
5. Do you intend to clean the public package (remove `review/`, `STATUS.md`, `NOTES_zh.md`, `GITHUB_DEPOSIT_SOP.md`, `author_verification_statement.md`, `external_validation_plan.md` and `manuscript/irb_waiver_request_template.md`) before peer review, given that the availability statement directs reviewers to it?
6. Were the excluded wrong-unit medication rows intended to be dropped rather than converted, and could this bias the medication features toward zero dose for affected cases?

---

## § What I actually checked

**Files read in full:** `manuscript/manuscript_v0.1.md` (794 lines), `manuscript/cover_letter_bmc_anesthesiology.md`, `results/s4_tripod_ai.md`, `MANIFEST.csv`, `results/s1_cohort.json`, `results/s3_metrics.json`, `results/s1_data_quality.json`, `results/s2_data_quality.json`, `results/s4_audit_trail.csv` (155 lines), `results/ext/external_validation.json`. Images inspected: `results/figs/fig1_cohort.png`, `fig2_definitions.png`, `fig6_external_validation.png`. Script excerpts read: `scripts/s1_cohort.py` (anchor quantile block), `scripts/s2_features.py` (unit-filter and anchor-quantile blocks).

**Web checks:** fetched the release page and API for `github.com/yyx-4113/mover-sis-ioh-prediction` tag v1.0.0 (exists; published 2026-10-20T09:58:22Z; one asset, `manuscript_v0.1.docx`, 433,909 bytes), the full recursive git tree at v1.0.0 (~90 entries), and the release's `MANIFEST.csv` (byte-identical to the project-root copy: 20 files).

**Counts performed by me:** abstract = 330 words with labels / 326 without, 4 paragraphs, 7 keywords; reference list = 18 entries, 16 distinct cited, [9] and [13] uncited; first-citation order = 1, 16, 17, 15, 2, 3, 4, 5, 6, 7, 8, 18, 10, 11, 12, 14, 15 (non-sequential); Table 3 predictor sum = 204 vs 206 claimed; O1–O4 sum = 98; audit-trail rows = 154, of which ~25 cite the unshipped `results/s2_features.csv` and 0 cover external validation.

**Values recomputed vs the manuscript:** anchor split 82.047% / 17.953% (manuscript 82.1 / 17.9 — **wrong**; Figure 1 shows 82.0 / 18.0 — right); D1 15.55% ✓; negative-by-construction 8.9% ✓; conditional prevalence 17.1% ✓; external prevalence 5.73% ✓ and 6.1% ✓; BMI computable 99.0% ✓; coverage 95.1 / 98.2 / 98.3 / 28.8 / 14.8 / 16.6 / 0.45% ✓; prevalence ratios 2.23× / 2.1× / 2.8× ✓; no-information Brier 0.131 ✓; gain ratio 2.33 ✓; all 16 Table 4 metric/CI triples ✓; calibration and DCA values ✓ (except the 0.74 vs 0.73 upper bound, F10); external 0.160 / 0.751 / 0.179 / 0.365 ✓; audit-trail `female_n` 8,506 vs manuscript 8,502 (**manuscript correct, trail wrong**); audit-trail labs coverage 0.1695 vs Table 3 0.45 (**Table 3 correct**, trail mislabels a feature-level mean).

**Not verified (outside this review's scope):** raw-EMR recomputation, the content of the shipped `.docx`, the 53-feature internal benchmark numbers beyond the audit-trail rows, and any figure content beyond the three PNGs inspected.

---

## Verdict

**Major revisions.**

The single change that would most improve the paper: **repair and re-ship Additional file 1 (the audit trail) so that it actually covers every number in the manuscript** — add the external-validation rows citing `results/ext/external_validation.json`, correct `female_n` to 8,502, relabel the coverage metric, add the anchor-timing quartile computation, and align the Methods sentence to what the trail delivers. The paper's central credibility claim is full traceability, and as shipped that claim fails in at least five independently checkable ways; the repair is mechanical and verifiable. (Runner-up: correct the anchor split to 82.0% / 18.0% in all six places, since the error currently sits in the abstract and contradicts Figure 1.)
