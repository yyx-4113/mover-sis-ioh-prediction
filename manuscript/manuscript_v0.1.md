# Prediction of cumulative intraoperative hypotension burden from data available at anaesthesia induction: development and internal validation in MOVER/SIS with an external transportability check in VitalDB

**Yongxin Yang**¹  ORCID 0009-0004-9698-6552

¹ Department of Anesthesiology, The Second Affiliated Hospital of Fujian University of
Traditional Chinese Medicine, Fuzhou, Fujian 350003, China

Correspondence: Yongxin Yang — 960856791@qq.com

---

## Abstract

**Background:** Intraoperative hypotension is associated with kidney and myocardial injury. Machine-learning performance estimates vary widely. We developed and internally validated a model predicting cumulative hypotension burden over the remainder of surgery from data available at the anaesthesia induction anchor, and examined its transportability in an external cohort.

**Methods:** Retrospective cohort from MOVER/SIS. Of 19,114 screened records, 16,861 adult cases had a valid anchor (first intubation event, 82.0%; otherwise surgery start, 18.0%). The primary outcome required ≥10 mean arterial pressure (MAP) measurements after the anchor with ≥30% below 65 mmHg. Predictors were truncated at the anchor; four models were fitted (baseline, full logistic, XGBoost, LightGBM). Validation used patient-level (primary) and temporal (secondary) splits; the unchanged MOVER core model was also applied to the VitalDB arterial cohort (n = 3,735; anchor adapted from intubation to operation start; no refitting) as a transportability check. AUPRC was the primary metric; AUROC and Brier score were secondary; 95% confidence intervals came from 1,000 bootstrap resamples; isotonic calibration and decision curve analysis were performed.

**Results:** The outcome occurred in 2,622 of 16,861 cases (15.55%). XGBoost achieved AUPRC 0.347 (95% CI 0.309–0.387) and AUROC 0.722 (0.697–0.745) on the patient-level split, versus 0.233 (baseline), 0.301 (full logistic) and 0.338 (LightGBM); on the temporal split it achieved 0.339 (0.291–0.395) and 0.733 (0.703–0.762). Isotonic recalibration improved the Brier score from 0.191 to 0.119. Subgroup AUPRC tracked stratum prevalence; pre-anchor mean MAP was the dominant predictor. Externally (VitalDB, prevalence 5.73%), the unchanged model retained discrimination (AUROC 0.744, 95% CI 0.705–0.778; AUPRC 0.158, 0.126–0.202) but probabilities were uncalibrated; the 53-feature internal AUROC was 0.698–0.710, confirming transportability rather than like-for-like validation.

**Conclusions:** An anchor-based model using routinely recorded pre-induction data achieved modest but non-null discrimination for cumulative hypotension burden and was well calibrated. An external transportability check in VitalDB supported transfer of ranking but not of absolute probabilities, requiring local recalibration before clinical use.

**Keywords:** intraoperative hypotension; machine learning; clinical prediction model; mean arterial pressure; perioperative medicine; calibration; TRIPOD

## Background

Intraoperative hypotension is common and consistently associated with organ injury. Salmasi and
colleagues showed that MAP below an absolute threshold of 65 mmHg was progressively related to
both myocardial and kidney injury after non-cardiac surgery, that prolonged exposure increased
the odds at any given threshold, and that absolute thresholds discriminated as well as relative
thresholds derived from preoperative pressure [1]. These conclusions have since been reinforced
by a systematic review of intraoperative hypotension and adverse postoperative outcomes [16] and
by a perioperative consensus that recommends keeping intraoperative mean arterial pressure at or
above 60 mmHg in at-risk patients [17], and by further work linking intraoperative mean arterial
pressure to outcomes [15]. These findings shifted attention from the
lowest recorded value towards the *cumulative burden* of hypotensive exposure.

That shift created a demand for anticipation. Commercial indices derived from arterial waveforms,
most notably the machine-learning Hypotension Prediction Index [19], have been evaluated in randomised trials [2,3],
and a growing literature applies machine learning to routinely recorded vital signs. Two features
of this literature motivate the present study.

First, reported performance is extremely heterogeneous, in part because the *prediction task*
differs between studies. Some predict whether hypotension will occur within the next 5–15 minutes
(a monitoring problem, addressed intraoperatively), whereas others stratify a patient's risk
before or at the start of the hypotensive exposure (a triage problem, addressed at induction).
These tasks are not interchangeable: the second admits fewer, coarser predictors and cannot
exploit the impending event's own precursors.

Second, some reported performances are difficult to reconcile with the information content of the
data. Applying gradient-boosted trees to the same public resource used here, a recent preprint
reported near-perfect discrimination for short-horizon prediction (AUROC 0.973, accuracy 0.942)
[4]. In the component of that resource analysed here, non-invasive MAP is recorded in 19.89% of
vital-sign rows (about one in five) and 96.2% of non-empty recording segments are isolated single
minutes. Under such
sparsity, discrimination of that magnitude is difficult to attribute to physiological signal.
A cross-centre evaluation reached a closely related conclusion, showing that apparent advantage
of deep-learning models over simple threshold rules largely disappears once cases already
hypotensive at the prediction origin are excluded and the grey zone is retained [5], and a
scoping review of perioperative artificial intelligence found external validation and
bias-resistant evaluation to be uncommon [6].

We therefore set out to develop and internally validate a model for the *cumulative burden* of
hypotension over the remainder of surgery, using only information available at the anaesthesia
induction anchor, to examine its transportability in an independent external cohort, and to report
it under an explicit leakage audit, with calibration and decision-analytic evaluation, and with an
honest account of what the recording density of the source data permits.

## Methods

### Study design and data source

This is a retrospective cohort study reported in accordance with TRIPOD+AI [7]; it corresponds to
TRIPOD type 2b (development with internal and external validation). The development data source was
MOVER (Medical Informatics Operating Room Vitals and Events Repository), University of California
Irvine, distributed through the UCI Machine Learning Repository [8]. The extraction analysed here
is the surgical information system (SIS) component, comprising nine linked tables: patient
information, procedure events, vitals, observations (invasive monitoring), ventilator settings,
medication, laboratories, intake/output, and a case-level procedure description. Access required a
signed data use agreement; all data were pre-existing and de-identified. No patients were
recruited and no intervention was performed.

### Cohort

Records were screened and excluded as follows (Figure 1): 8 records with implausible operating
room (OR) windows (4 with non-positive duration, 4 exceeding 1,440 minutes; maximum observed
3,156,668 minutes, indicating corrupt timestamps); 1,632 records with fewer than 60 vital-sign
observations inside the OR window; and 371 records of patients younger than 18 years. This left
17,103 cases. A further 242 cases were excluded because no valid prediction anchor could be
determined (anchor falling outside the OR window), yielding an analysis cohort of **16,861** cases
contributing 3,379,173 OR-window vital-sign observations. Median OR duration was 167 minutes.

### Prediction anchor

The prediction anchor was the first recorded Intubation event (n = 13,834; 82.0%). Where no
intubation event existed, Surgery start was used as a proxy (n = 3,027; 18.0%). The anchor occurred
a median of 15 minutes (IQR 11–24) after OR start. The observation window after the anchor had a
median duration of 147 minutes (5th–95th percentile 49–440).

### Outcome

The primary outcome (D1) adopts the absolute MAP threshold (<65 mmHg) of Salmasi et al. [1] but
operationalises burden as the proportion of *recorded* post-anchor MAP readings below threshold: at
least 10 readings, of which at least 30% below 65 mmHg. Because non-invasive pressure is recorded
intermittently rather than continuously, this is a proportion of recorded readings, not a
cumulative time below threshold; the number of low readings required for a positive label therefore
varies with recording density (3 to 77 readings across cases; median 9). The ≥10-measurement and
≥30%-below rule is our operational choice rather than a literal transcription of that report. Cases
with fewer than 10 post-anchor measurements were classified as negative by construction; this
applied to 1,496 cases (8.9%) — 1,332 with 1–9 readings and 164 with no post-anchor MAP recording
at all — because the definition deliberately requires a minimum amount of evidence before a burden
can be asserted. A sensitivity analysis restricted to the 15,365 evaluable cases is reported in the
Results.

Because the choice of hypotension definition materially changes apparent performance, 14 candidate
definitions were computed for every case and are reported in full (Table 2; their prevalence is shown in Figure 2). They comprise
sustained-grid definitions (consecutive minutes below threshold on a one-minute grid, with missing
minutes counted as interruption), point-burst definitions (a minimum number of low readings within
a rolling window), exposure-fraction definitions, any-below definitions, two SpO₂ desaturation
definitions included as a coverage comparison, and one measured-only definition retained solely to
quantify how much sustained-event definitions are inflated when gaps are ignored.

### Candidate predictors and leakage control

Two hundred and six candidate predictors were constructed across 13 domains: anchor
characteristics (3), demographics (6), surgical group (14), anaesthesia technique (12),
non-invasive blood pressure (36), derived non-invasive indices (6), quality-assurance counters
(2), invasive monitoring (32), ventilation and inhaled agents (47), medication (26), derived
medication indices (2), laboratories (12) and fluid/bleeding (8).

Every domain was truncated at the anchor such that no information dated after the prediction
origin could enter the model. Physiological and device domains were additionally restricted to the
15 minutes preceding the anchor; laboratories used the last value before the anchor; medication
and fluid records were restricted to those started before the anchor. The integrity of this
truncation was verified programmatically and reported as a leakage audit (Table 3): across all
seven time-stamped domains the maximum interval between any used observation and the anchor was
0.00 minutes, and no record had an unparseable timestamp. One boundary detail deserves statement:
the physiological windows are closed at the anchor ([anchor−15, anchor]), so a MAP reading recorded
exactly at the anchor minute belongs to both the feature window and the outcome window
([anchor, OR end]). Sensitivity analyses that exclude the anchor minute from the feature window,
and separately from the outcome window, are reported in the Results; neither changed the
conclusions.

Surgical group was assigned from the free-text procedure description by keyword mapping into 12
surgical categories plus a no-surgery category, with a controlled fuzzy fallback (edit distance ≤1,
identical initial, minimum length 7 characters). The residual "other" category contained 348 cases
(2.1%).

Anthropometric variables required cleaning. Height and weight in the source contained unit-entry
errors (observed height as low as 2 cm, weight as high as 839 kg), which propagated to body mass
index values as extreme as 2.2 × 10⁵ kg/m². Values outside adult plausible ranges (height
100–220 cm; weight 25–300 kg; BMI 10–80 kg/m²) were set to missing rather than imputed: 37
heights, 18 weights and 6 BMI values were affected, leaving BMI computable for 16,699 cases
(99.0%).

### Model development

Four models were pre-specified. A *baseline* logistic model used age, sex and BMI only, to
quantify how much the full predictor set adds. A *full* logistic model used all predictors after
median imputation with missingness indicators and standardisation, with balanced class weighting;
the imputer was fitted within each training fold only, so no test-set information entered
preprocessing. *XGBoost* (300 trees, depth 4, learning rate 0.05, subsample 0.8, column sampling
0.8, minimum child weight 10, L2 penalty 1.0, class-weight scaling) and *LightGBM* (300 trees, 15
leaves, learning rate 0.05, subsample 0.8, column sampling 0.8, minimum 20 samples per leaf, L2
penalty 1.0, balanced class weighting) used native handling of missing values and required no
imputation. Hyperparameters were fixed a priori on clinical-iterative grounds rather than by
external tuning; with 335 logistic parameters against 2,097 training events (events per variable
≈6.3, below the commonly cited 10-events-per-parameter heuristic [20]), the full logistic model is expected to be over-fitted and is reported as a comparator
rather than a deployable model.

### External validation cohort

As a transportability check rather than a like-for-like external validation, the MOVER core model was
applied unchanged to VitalDB [18], an independent public database of high-fidelity vital signs from
surgical patients at a single tertiary centre (Seoul National University Hospital, Republic of
Korea), accessed through its public application programming interface without authentication. A
transparency limitation must be stated at the outset: VitalDB records no intubation event, so the
prediction anchor was adapted from the MOVER intubation (induction) anchor to the operation start
time (opstart), which occurs *after* induction and intubation. The external "pre-anchor" 15-minute
window therefore captures early-intraoperative rather than pre-induction physiology, a different
phase from the development window. The outcome D1 was computed by the same rule over
[opstart, opend]; because VitalDB samples arterial pressure far more densely than the intermittent
non-invasive readings in MOVER, the same proportion-based rule implies a much larger absolute
hypotensive exposure for a positive external label (at the median recording density, about 1,300
hypotensive samples, or some 44 cumulative minutes below 65 mmHg, versus 9 readings in MOVER), so
the external endpoint is not equivalent to the development endpoint and part of the prevalence gap
between cohorts is definitional rather than case-mix; a sensitivity analysis on a common
one-minute-grid, absolute-time definition is reported in the Results. Of 6,388 VitalDB cases with
recorded vital signs, 3,735 had an arterial MAP track (Solar8000/ART_MBP or EV1000/ART_MBP) together
with valid operation timing and formed the external cohort. Predictors were
restricted to the 53-feature transportable subset: demographic and anthropometric variables;
pre-anchor 15-minute summary statistics of six vital signs (MAP, SBP, DBP, HR, a heart-rate
variability proxy and SpO₂); the fraction of pre-anchor MAP readings below 65 and 55 mmHg; and three
MOVER-specific contextual features — the anchor-to-OR-start interval, an indicator that the anchor
was an intubation event, and a calendar-year indicator. The latter two are not derivable from
VitalDB and were set to zero; the anchor-to-OR-start interval was re-derived under the opstart anchor
(opstart minus case start, in minutes), so its meaning necessarily differs from the development
cohort, where it is the OR-start-to-intubation interval — a residual source of transportability
error. For transparency we note that the transported model was fitted on the full MOVER cohort
(all 16,861 cases), whereas the internal comparators in Table 7 were fitted on the 80% training
split of the patient-level split; the external model is therefore not disadvantaged by a smaller
training set, but neither is it directly comparable to the held-out internal estimates. The MOVER
core model (53 features, seed 12,345) was applied without any external refitting or
recalibration; performance was summarised by AUPRC (primary), AUROC and Brier score, with 95%
confidence intervals from 1,000 bootstrap resamples. Calibration was assessed descriptively and was
not updated on the external data.

### Validation and performance

The primary validation was a patient-level split: a randomly selected 80% (n = 13,488) for
training and 20% (n = 3,373; 525 outcome-positive) for testing, with no patient appearing in both.
A secondary temporal split used cases before 2018 for training (n = 15,043) and cases from 2018
for testing (n = 1,818; 291 outcome-positive), to detect calendar-time drift.

Because the outcome is moderately imbalanced (15.55%), AUPRC was the primary metric; a model with
no skill attains AUPRC equal to the prevalence. AUROC and Brier score were secondary. Confidence
intervals came from 1,000 bootstrap resamples of the test set. Calibration was assessed and, for
the primary model, improved by isotonic regression fitted on out-of-fold predictions from a
5-fold cross-validation within the training data, then applied unchanged to the test set.
Calibration slope and intercept were reported on both the probability scale (linear-probability
model) and the log-odds scale (logistic recalibration), in keeping with current guidance on calibration assessment [21]. Decision curve analysis quantified net
benefit across threshold probabilities.

Predictor importance was reported as XGBoost gain. Because gain reflects the fitted model rather
than an inferential quantity, it is presented descriptively.

### Software and reproducibility

Analyses used Python 3.13 with pandas 2.3.3, scikit-learn 1.9.0 [9], XGBoost 3.4.1 [10] and
LightGBM 4.7.0 [11]. The random seed was fixed at 12,345. Every headline number reported in this
manuscript is generated from a result file by the analysis pipeline and is traceable through an
audit trail (Additional file 1) that records, for each quantity, its value, the producing artefact
and the command that reproduces it; a small number of descriptive statistics (for example the
interquartile ranges of recording density) are produced by the same scripts and are listed in the
trail with their source artefact but without a dedicated reproduce command.

## Results

### Cohort

The 16,861 analysed cases had a median age of 54 years (IQR 39–66) and were almost evenly split by
sex (Table 1). Median BMI was 26.6 kg/m² (IQR 23.1–30.9). The most common surgical groups were
gastrointestinal (29.2%), neurosurgical (15.0%) and orthopaedic (14.3%). The primary outcome
occurred in 2,622 cases (15.55%). Compared with outcome-negative cases, outcome-positive cases
were younger (median 48 vs 55 years), had lower BMI (25.4 vs 26.8 kg/m²) and, most prominently,
lower pre-anchor mean MAP (79.5 vs 89.0 mmHg) and lower pre-anchor minimum MAP (72 vs 81 mmHg).

**Table 1. Characteristics of the analysis cohort (n = 16,861).**

| Characteristic | Value |
|---|---|
| Age, years — median (IQR) | 54 (39–66) |
| Male sex — n (%) | 8,355 (49.6) |
| Female sex — n (%) | 8,502 (50.4) |
| Sex unknown — n (%) | 4 (<0.1) |
| Height, cm — median (IQR) | 167 (160–175) |
| Weight, kg — median (IQR) | 76 (63–90) |
| Body mass index, kg/m² — median (IQR) | 26.6 (23.1–30.9) |
| Anchor = Intubation — n (%) | 13,834 (82.0) |
| Anchor = Surgery start (proxy) — n (%) | 3,027 (18.0) |
| Anchor after OR start, min — median (IQR) | 15 (11–24) |
| Post-anchor window, min — median (5th–95th) | 147 (49–440) |
| Pre-anchor MAP readings in 15-min window — median (IQR) | 3 (2–4) |
| Pre-anchor mean MAP, mmHg — median (IQR) | 87.7 (77.7–98.5) |
| Invasive arterial monitoring available — n (%) | 2,503 (14.8) |
| Ventilation data available — n (%) | 4,852 (28.8) |
| Pre-anchor laboratory results — n (%) | 76 (0.45) |
| Pre-anchor fluid/intake-output records — n (%) | 2,794 (16.6) |
| Surgical group: gastrointestinal — n (%) | 4,916 (29.2) |
| Surgical group: neurosurgical | 2,530 (15.0) |
| Surgical group: orthopaedic | 2,407 (14.3) |
| Surgical group: urological | 1,541 (9.1) |
| Surgical group: plastic | 1,318 (7.8) |
| Surgical group: vascular | 1,049 (6.2) |
| Surgical group: gynaecological | 992 (5.9) |
| Surgical group: thoracic | 958 (5.7) |
| Surgical group: ear, nose and throat | 418 (2.5) |
| Surgical group: other | 348 (2.1) |
| Surgical group: ophthalmic | 201 (1.2) |
| Surgical group: cardiac | 177 (1.0) |
| Surgical group: no surgery recorded | 6 (<0.1) |
| **Primary outcome D1 — n (%)** | **2,622 (15.55)** |

### Outcome definition sensitivity

The 14 candidate definitions span a very wide prevalence range (Table 2), which is the principal
reason that performances reported across studies are not comparable. Strict sustained-grid
definitions at 55 mmHg identified 15 to 54 cases (0.09–0.32%), far too few for modelling, whereas
any-below definitions identified up to 11,091 cases (65.8%). The primary definition D1 occupies an
intermediate position with adequate event count for model development.

**Table 2. Prevalence of 14 candidate outcome definitions (n = 16,861), post-anchor window.**

| ID | Type | Signal | Threshold | Parameters | n | % |
|---|---|---|---|---|---|---|
| O1 | sustained grid | MAP | 55 | 5 min, no gaps | 15 | 0.09 |
| O2 | sustained grid | MAP | 55 | 5 min, 1-min gaps allowed | 54 | 0.32 |
| O3 | sustained grid | MAP | 55 | 10 min, 1-min gaps allowed | 2 | 0.01 |
| O4 | sustained grid | MAP | 65 | 10 min, 1-min gaps allowed | 27 | 0.16 |
| S1 | measured-only grid | MAP | 65 | 10 min (known to overestimate) | 1,214 | 7.20 |
| B1 | point burst | MAP | 65 | ≥3 readings within 30 min | 7,240 | 42.94 |
| B2 | point burst | MAP | 65 | ≥5 readings within 60 min | 5,192 | 30.79 |
| B3 | point burst | MAP | 55 | ≥3 readings within 30 min | 1,159 | 6.87 |
| **D1** | **exposure fraction** | **MAP** | **65** | **≥10 readings and ≥30% below** | **2,622** | **15.55** |
| D2 | exposure fraction | MAP | 55 | ≥10 readings and ≥30% below | 91 | 0.54 |
| E1 | any below | MAP | 55 | — | 3,770 | 22.36 |
| E2 | any below | MAP | 65 | — | 11,091 | 65.78 |
| O5 | sustained grid | SpO₂ | 90 | 2 min, no gaps | 1,292 | 7.66 |
| O6 | sustained grid | SpO₂ | 92 | 5 min, no gaps | 572 | 3.39 |

S1 is retained solely to demonstrate the magnitude of inflation produced by ignoring recording
gaps; O5 and O6 are desaturation outcomes shown for coverage comparison and are not hypotension
definitions.

### Predictor availability and recording density

Predictor availability was markedly unequal across domains (Table 3). Demographic, surgical,
anchor and medication domains were essentially complete. By contrast, invasive arterial monitoring
was available for 2,503 cases (14.8%), ventilation data for 4,852 (28.8%), fluid records for 2,794
(16.6%) and pre-anchor laboratory results for 76 (0.45%). Within the non-invasive blood pressure
domain, 16,036 cases (95.1%) had at least one reading in the 15-minute pre-anchor window, but the
median number of MAP readings in that window was 3 (IQR 2–4).

Across the whole cohort, non-invasive MAP was recorded in 19.89% of case-minutes (systolic 19.99%,
diastolic 19.95%), whereas heart rate and pulse rate were recorded in 94.8% and 95.9% and
oxygen saturation in 96.1%. Of 637,188 non-empty MAP recording segments, 96.2% consisted of a
single minute; the median segment length was 1 minute. Per case, the median number of MAP
measurements over the OR window was 33 (5th–95th percentile 12–90).

**Table 3. Leakage audit and coverage by predictor domain.**

| Domain | Predictors | Cases with data | Coverage (%) | Max interval to anchor (min) |
|---|---|---|---|---|
| Anchor characteristics | 3 | 16,861 | 100.0 | 0.00 |
| Demographics | 6 | — | 99.7 | n/a (static) |
| Surgical group | 14 | 16,861 | 100.0 | n/a (static) |
| Anaesthesia technique | 12 | 16,563 | 98.2 | 0.00 |
| Medication (pre-anchor) | 26 | 16,573 | 98.3 | 0.00 |
| Non-invasive blood pressure | 36 | 16,036 | 95.1 | 0.00 |
| Derived non-invasive indices | 6 | — | 89.8 | 0.00 |
| Quality-assurance counters | 2 | — | 99.6 | 0.00 |
| Ventilation and inhaled agents | 47 | 4,852 | 28.8 | 0.00 |
| Invasive monitoring | 32 | 2,503 | 14.8 | 0.00 |
| Fluid and bleeding | 8 | 2,794 | 16.6 | 0.00 |
| Laboratories | 12 | 76 | 0.45 | 0.00 |

All seven time-stamped domains passed the audit (maximum interval 0.00 minutes; zero records with
unparseable timestamps).

### Model performance

On the primary patient-level split, XGBoost gave the highest AUPRC at 0.347 (95% CI 0.309–0.387),
which is 2.23 times the prevalence of 0.1555 expected under no skill (Table 4). LightGBM was
similar on AUROC (0.721 vs 0.722) but slightly lower on AUPRC. The full logistic model reached
AUPRC 0.301, and the age/sex/BMI baseline 0.233, indicating that the additional predictors
contribute meaningfully beyond basic demographics while the absolute gain remains moderate. Figure 3 shows the precision–recall and receiver operating characteristic curves for all four models.

Results on the temporal split were closely similar (XGBoost AUPRC 0.339, AUROC 0.733), indicating
no material calendar-time drift.

**Table 4. Model performance on the patient-level (primary) and temporal (secondary) splits.**

| Split | Model | n train | n test | Events in test | AUPRC (95% CI) | AUROC (95% CI) | Brier |
|---|---|---|---|---|---|---|---|
| Patient | Baseline logistic (age, sex, BMI) | 13,488 | 3,373 | 525 | 0.233 (0.205–0.267) | 0.624 (0.596–0.650) | 0.239 |
| Patient | Full logistic | 13,488 | 3,373 | 525 | 0.301 (0.269–0.339) | 0.706 (0.681–0.728) | 0.216 |
| Patient | **XGBoost** | 13,488 | 3,373 | 525 | **0.347 (0.309–0.387)** | **0.722 (0.697–0.745)** | 0.191 |
| Patient | LightGBM | 13,488 | 3,373 | 525 | 0.338 (0.299–0.377) | 0.721 (0.697–0.743) | 0.183 |
| Temporal | Baseline logistic | 15,043 | 1,818 | 291 | 0.243 (0.209–0.288) | 0.609 (0.574–0.646) | 0.239 |
| Temporal | Full logistic | 15,043 | 1,818 | 291 | 0.336 (0.289–0.394) | 0.726 (0.694–0.758) | 0.226 |
| Temporal | **XGBoost** | 15,043 | 1,818 | 291 | **0.339 (0.291–0.395)** | **0.733 (0.703–0.762)** | 0.194 |
| Temporal | LightGBM | 15,043 | 1,818 | 291 | 0.336 (0.289–0.390) | 0.731 (0.702–0.761) | 0.188 |

AUPRC under no skill equals the prevalence (0.1555). Brier scores are for uncalibrated predictions.

### Calibration and clinical usefulness

For XGBoost on the patient-level split, the uncalibrated Brier score was 0.191, which exceeds the
no-information Brier score of 0.131 (prevalence × (1 − prevalence)); this confirms meaningful
miscalibration for which recalibration was required rather than cosmetic. Out-of-fold isotonic
recalibration reduced the Brier score to 0.119, with a calibration slope of 0.909 and an intercept
of 0.008 on the probability scale (linear-probability model); the logit-scale recalibration slope
and intercept are reported alongside. On the temporal split the Brier score
improved from 0.194 to 0.122, with slope 0.934 and intercept 0.006 on the probability scale. In
both cases the probability-scale slope below 1 indicates that the uncalibrated predictions were
slightly over-dispersed, which isotonic recalibration corrected.

In decision curve analysis, the calibrated model's net benefit exceeded that of the "treat none"
strategy from the lowest evaluated threshold up to 0.58 on the patient-level split and up to 0.45
on the temporal split; on the temporal split it then turned negative between 0.46 and 0.65 and
returned briefly to positive only between 0.66 and 0.73, where the net benefit was nonetheless
negligible (≤0.0006), as it was at the top of the patient-level range (0.0001 at 0.58). The "treat
all" strategy had a small positive net benefit at the lowest evaluated thresholds (≈0.06 at
threshold 0.10) but became strongly negative at higher thresholds (≈−2.1 at 0.73), so it offers no
advantage over the model. The absolute net benefit at the decision-relevant thresholds was small
(0.078 and 0.085 at threshold 0.10; 0.051 and 0.058 at threshold 0.15, close to the outcome
prevalence), so the clinical usefulness demonstrated by the curve is modest. In a benchmark
against a logistic model using the pre-anchor mean MAP alone, the full model's incremental net
benefit was 0.013 at both thresholds 0.10 and 0.15 (Figure 4).

### Subgroup performance

Raw subgroup AUPRC varied across strata (Table 5): it was higher in women than men, declined with
age, and was highest in underweight patients. However, subgroup AUPRC tracks stratum outcome
prevalence closely: across the nine strata the rank correlation between full-cohort stratum
prevalence and patient-level subgroup AUPRC was strong (Spearman ρ = 0.88, p = 0.002). Normalising
AUPRC by stratum prevalence (the no-skill AUPRC for that stratum) compressed the age gradient to
ratios of 1.89, 2.28 and 1.82 across increasing age bands and reversed the sex ordering (men 2.17
vs women 2.07); on the temporal split the normalised ratios were similarly uniform (1.88–2.14 by
age band; women 2.14 vs men 1.93). The raw subgroup differences therefore largely reflect stratum
base rates rather than differential model skill, and no subgroup-specific claim is made. The
underweight stratum is the clearest exception and is explicitly unstable: its raw AUPRC of 0.616
rests on 10 outcome events among 98 patient-level test-set cases (512 cases, 95 events in the full
cohort), and the corresponding ratio of 3.32 is inflated by the same small numbers; on the temporal
split the AUPRC fell to 0.382.

**Table 5. AUPRC of XGBoost by subgroup (held-out test set), with stratum prevalence and the
AUPRC-to-prevalence ratio (lift over the no-skill baseline).**

| Subgroup | n (test) | Stratum prevalence, % (full cohort) | Patient AUPRC | AUPRC / prevalence | Temporal AUPRC | AUPRC / prevalence |
|---|---|---|---|---|---|---|
| Men | 1,689 | 13.80 | 0.299 | 2.17 | 0.267 | 1.93 |
| Women | 1,684 | 17.27 | 0.357 | 2.07 | 0.370 | 2.14 |
| Age < 50 years | 1,402 | 20.09 | 0.380 | 1.89 | 0.377 | 1.88 |
| Age 50–64 years | 1,044 | 14.26 | 0.324 | 2.28 | 0.305 | 2.14 |
| Age ≥ 65 years | 927 | 10.22 | 0.186 | 1.82 | 0.194 | 1.90 |
| BMI < 18.5 kg/m² | 98 | 18.55 | 0.616 | 3.32 | 0.382 | 2.06 |
| BMI 18.5–24.9 kg/m² | 1,202 | 18.76 | 0.392 | 2.09 | 0.354 | 1.89 |
| BMI 25–29.9 kg/m² | 1,064 | 14.55 | 0.286 | 1.96 | 0.306 | 2.10 |
| BMI ≥ 30 kg/m² | 977 | 12.45 | 0.257 | 2.07 | 0.330 | 2.65 |

n denotes the number of cases in the held-out test set on which each subgroup AUPRC was computed
(patient-level split: 3,373; temporal split: 1,818). Stratum prevalence is the D1 prevalence of the
stratum in the full analysis cohort (n = 16,861), which estimates the stratum base rate more
stably than the smaller held-out sets; under no skill the AUPRC of a stratum equals its prevalence,
so the ratio is the lift over that baseline. Subgroup AUPRCs are exploratory given the reduced
event counts within strata: for example, the underweight stratum comprised 98 patient-level
test-set cases with 10 events (512 cases with 95 events in the full cohort). Thirty-two test-set
cases had missing BMI and contribute to no BMI stratum.

### Predictor importance

Pre-anchor arterial pressure dominated (Table 6). Mean MAP had a gain roughly 2.3 times that of the
next predictor. The remaining informative predictors were the maximum pre-anchor MAP, whether the
anchor was an intubation event, the elapsed time from OR start to the anchor, the fraction of
pre-anchor readings already below 65 mmHg, surgical group, and diastolic and invasive arterial
pressure summaries. Figure 5 shows the 25 highest-gain predictors.

**Table 6. Ten highest-gain predictors, XGBoost (patient-level split).**

| Rank | Predictor | Domain | Gain |
|---|---|---|---|
| 1 | Mean pre-anchor MAP | Non-invasive blood pressure | 175.5 |
| 2 | Maximum pre-anchor MAP | Non-invasive blood pressure | 75.2 |
| 3 | Anchor is intubation | Anchor | 72.2 |
| 4 | Intubation event recorded | Anaesthesia technique | 69.1 |
| 5 | Interval from OR start to anchor | Anchor | 64.1 |
| 6 | Fraction of pre-anchor readings below 65 mmHg | Non-invasive blood pressure | 52.9 |
| 7 | Gastrointestinal surgical group | Surgical group | 48.6 |
| 8 | Mean pre-anchor diastolic pressure | Non-invasive blood pressure | 45.0 |
| 9 | Minimum invasive diastolic pressure | Invasive monitoring | 44.7 |
| 10 | Mean invasive MAP | Invasive monitoring | 43.2 |

### External transportability check

The MOVER core model was applied without refitting to the VitalDB arterial cohort of 3,735 eligible
cases (of 6,388 VitalDB cases with recorded vital signs, those with valid operation timing and an
arterial MAP track), of which 214 (5.73%) met the D1 outcome (Table 7); a further 214 cases with
fewer than 10 post-anchor MAP measurements were classified D1-negative by construction under the
same rule as the development cohort, so the conditional prevalence among adequately monitored
external cases was 6.1% (214 of 3,521). Discrimination transferred: the external AUROC was 0.744
(95% CI 0.705–0.778), numerically above the internal patient-level value of 0.698 and the temporal
value of 0.710 for the same 53-feature model, although the confidence intervals overlap
(0.705–0.778 vs 0.673–0.723 and 0.679–0.740), so the difference should be read as consistency
rather than superiority. The external AUPRC of 0.158 (0.126–0.202) exceeded the external prevalence
by a factor of 2.8, a larger relative lift than the 2.1-fold internal value for that model. The
lower absolute AUPRC reflects the much lower external prevalence (5.73% vs 15.55%) rather than a
loss of ranking ability. Absolute probabilities did not transfer: the mean predicted risk was 0.37
against an observed prevalence of 0.057 (external Brier score 0.179), indicating that the model
would require local recalibration before the predicted probabilities could be used directly. These
results are summarised in Figure 6 and Table 7.

**Table 7. External transportability check of the MOVER core model (53 features) in VitalDB versus
internal performance of the same model in MOVER/SIS.**

| Dataset | Split | n | Events | Prevalence (%) | AUPRC (95% CI) | AUROC (95% CI) | Brier |
|---|---|---|---|---|---|---|---|
| MOVER/SIS (development) | Patient | 3,373 | 525 | 15.55 | 0.321 (0.284–0.362) | 0.698 (0.673–0.723) | 0.198 |
| MOVER/SIS (development) | Temporal | 1,818 | 291 | 16.01 | 0.314 (0.269–0.365) | 0.710 (0.679–0.740) | 0.199 |
| VitalDB (external) | — | 3,735 | 214 | 5.73 | 0.158 (0.126–0.202) | 0.744 (0.705–0.778) | 0.179 |

Internal values are for the identical 53-feature transportable model; the development manuscript
headline (AUPRC 0.347, AUROC 0.722) is for the full 206-feature model. The external cohort had no
refitting or recalibration.

### Sensitivity analyses

We examined the robustness of the main findings to eight perturbations; the key results are in Table 8.

**S1 – Restricted evaluable cohort.** Excluding the 1,496 negative-by-construction (NBC) cases left 15,365 cases with at least 10 post-anchor MAP measurements (conditional prevalence 17.06%). On this subset XGBoost reached AUPRC 0.401 (95% CI 0.358–0.444) and AUROC 0.735 (0.710–0.757) on the patient-level split and AUPRC 0.367 (0.318–0.425) and AUROC 0.739 (0.709–0.769) on the temporal split – higher than the full-cohort values, confirming that the apparent precision gain reflects removal of the NBC cases rather than stronger physiological signal.

**S2 – Half-open anchor window.** Repeating the main analysis with the anchor minute excluded from the feature window (strict `<anchor`) gave patient-level AUPRC 0.342 (0.302–0.380) and AUROC 0.715 (0.690–0.737) and temporal AUPRC 0.334 (0.286–0.388) and AUROC 0.723 (0.693–0.753), essentially unchanged from the closed-window main results, so inclusion of the anchor minute does not drive the findings.

**S3 – Externally re-derived time-based labels.** Recomputing the external D1 outcome on VitalDB on a common one-minute grid with absolute-time thresholds (already-transported 53-feature model, unrefitted) yielded AUROC 0.744 (0.705–0.778) and AUPRC 0.158 (0.126–0.202) under the sampling-based definition (D1_samples, prevalence 5.73%) – numerically consistent with the development-label external value, confirming the transportability signal is not an artefact of the development label rule.

**S4 – External recalibration.** Fitting a logistic recalibration to the transported predictions on VitalDB (logit-scale slope 0.77, intercept -2.61; calibration-in-the-large 0.30) shifted the mean predicted risk from 0.36 towards the observed prevalence of 0.057 and improved the Brier score, demonstrating that local recalibration restores probability accuracy.

**S5 – External funnel.** Of 6,388 VitalDB cases with recorded vitals, 3,735 had a valid arterial MAP track and operation timing; 214 had zero post-anchor MAP and were negative by construction, coinciding exactly with the 214 D1-positive cases (disclosed for transparency).

**S6 – Physiological-feature subset.** Restricting the transported model to the 39 physiological value-domain features (dropping cadence counters and the frozen context features) gave external AUROC 0.713 (0.670–0.750) and AUPRC 0.151 (0.119–0.196) – only marginally below the 53-feature value, so the dropped features contributed little.

**S7 – Anchor-minute label overlap.** In the primary design both windows are closed at the anchor (the feature window `[anchor-15, anchor]` and the label window `[anchor, OR_end]` share the anchor minute); 99.0% of cases have a MAP reading exactly at the anchor. Re-deriving labels with the strictly open label window `(anchor, OR_end]` flipped only 62 positive to negative and 35 negative to positive (net -27; prevalence 15.39% vs 15.55%), confirming the anchor minute belongs to the feature side and its shared inclusion does not materially affect labels.

**S8 – Case-minute recording rate.** The fraction of surgical minutes with at least one recorded MAP (case-minute recording rate) was 19.6%, corroborating the 19.89% row-level MAP density and the sparse-sampling limitation in Limitation 9.

**Table 8. Sensitivity analyses of the MOVER/SIS hypotension model (XGBoost unless noted).**

| Analysis | Split | n | Prevalence (%) | AUPRC (95% CI) | AUROC (95% CI) |
|---|---|---:|---:|---:|---:|
| S1 Restricted cohort | Patient | 15,365 | 17.06 | 0.401 (0.358–0.444) | 0.735 (0.710–0.757) |
| S1 Restricted cohort | Temporal | 15,365 | 17.06 | 0.367 (0.318–0.425) | 0.739 (0.709–0.769) |
| S2 Half-open window | Patient | 16,861 | 15.55 | 0.342 (0.302–0.380) | 0.715 (0.690–0.737) |
| S2 Half-open window | Temporal | 16,861 | 15.55 | 0.334 (0.286–0.388) | 0.723 (0.693–0.753) |
| S3 External labels (D1_samples) | - | 3,735 | 5.73 | 0.158 (0.126–0.202) | 0.744 (0.705–0.778) |
| S6 Physiological subset (external) | - | 3,735 | 5.73 | 0.151 (0.119–0.196) | 0.713 (0.670–0.750) |

## Discussion

### Principal findings

In a cohort of 16,861 adult surgical cases, a gradient-boosted model using only information
available at the induction anchor achieved an AUPRC of 0.347 and an AUROC of 0.722 for the
cumulative burden of hypotension over the remainder of surgery, with closely similar performance
under temporal validation and good calibration after isotonic recalibration. Discrimination was
therefore approximately 2.2-fold (2.23×) better than the no-skill baseline on the precision–recall
scale — modest, but clearly not null — and the decision curve showed the model yielded positive net
benefit relative to both default strategies across threshold probabilities up to approximately 0.58
(patient-level) and 0.45 (temporal); on the temporal split the net benefit turns negative beyond
0.45 except for a narrow positive interval between 0.66 and 0.73, where its magnitude is negligible.
The decision-relevant region is therefore thresholds near to moderately above the outcome
prevalence (roughly 0.10–0.30), where the calibrated probabilities
could support a vasopressor-readiness or enhanced-monitoring decision; the specific operating point
remains a clinical judgement to be informed by external validation rather than settled here.

### Interpretation

The dominance of pre-anchor mean MAP is the single most informative result, and it should be read
carefully. Its most straightforward interpretation is that patients who are already relatively
hypotensive at induction are likely to remain so, which is clinically sensible and actionable:
it identifies a group in whom vigilance, arterial cannulation and vasopressor readiness are
justified early. Its more cautionary interpretation is that the model is, to a substantial degree,
an extrapolation of the current pressure rather than a discovery of new physiology. That
distinction matters, because a model whose information content is largely the present blood
pressure adds little to what an anaesthetist already sees, and it is precisely the setting in which
selection bias can inflate apparent performance [5].

This interpretation is consistent with the stratified findings. Raw AUPRC declined with age and was
higher in women, but both patterns tracked stratum outcome prevalence rather than differential
model skill: normalising by stratum prevalence reversed the sex ordering and compressed the age
gradient (Table 5). The patterns remain compatible with the model tracking pre-anchor pressure
levels, whose distribution and prognostic weight differ across these strata, rather than with the
model identifying age- or sex-specific vulnerability.

### Relation to previous work

Our results stand in marked contrast to the near-perfect discrimination recently reported on the
same public resource [4]. We do not question that analysis directly, since the details necessary to
reproduce it are not available to us; we raise it as a methodological hazard rather than a claim
about any specific report. Two facts are open to any reader. First, in the component analysed here,
non-invasive arterial pressure is recorded in fewer than one in five case-minutes and almost all
recorded segments are isolated single minutes, so the physiological trajectory available to any
model is extremely coarse. Second, an independent external evaluation on the same resource reported
an AUROC of 0.696 for a deliberately simple three-variable additive model under a
selection-bias-resistant protocol [12], and a cross-centre evaluation attributed inflated
performance to selection effects rather than to genuine generalisability [5]; our AUROC of 0.722
is consistent in magnitude with the former. We note that the same external analysis reported that
the *dynamics* of arterial pressure, not only its current value, carry incremental predictive
information for hypotension [12]. Our recording density (median 3 MAP readings in the 15-minute
pre-anchor window) is too sparse to characterise such dynamics, so our model necessarily leans on
the static pre-anchor level; this is a limitation of the source data rather than evidence against
the dynamics signal. Other investigators have developed machine-learning models for intraoperative
risk from comparable operating-room resources, including models developed on MOVER itself [13] and
external-validation studies in related surgical populations [14]. We now
provide such an external transportability check ourselves, in VitalDB, an independent resource
with a different recording architecture; the model's ranking ability transferred (external AUROC
0.744, in the same range as and overlapping the confidence interval of the internal 0.698–0.710 for
the same 53-feature model) while absolute probabilities did not and would
require local recalibration — a finding that strengthens rather than weakens the caution above.
Performance of the order of 0.97 would still require near-separation of the classes, which is
difficult to reconcile with the recording density reported here, and we flag the possibility of
label–feature window overlap or of counting as predictable those cases already below threshold at
the prediction origin. We regard these as general methodological hazards in perioperative prediction
rather than criticisms specific to one report, and we note that external validation and
bias-resistant evaluation remain uncommon in this literature [6].

### Implications

Four implications follow. First, the definition of the outcome should be stated with the same
prominence as the performance metric: across our 14 candidate definitions the prevalence ranged
from 0.01% to 65.8%, and no performance figure is interpretable without it. Second, cumulative-burden
outcomes are feasible on sparse data in a way that sustained-duration outcomes are not — sustained
definitions at conventional thresholds identified fewer than 60 cases here, which is an important
structural constraint on what can be modelled with non-invasive recordings. Third, anchor-based
prediction addresses a different clinical question from short-horizon prediction, and the two
should not be benchmarked against each other as though they were the same task. Fourth, the model's
information content is dominated by the pre-anchor arterial pressure: in a decision-curve benchmark
against a logistic model using the pre-anchor mean MAP alone, the full model added only 0.013 net
benefit at threshold 0.15, and the MAP-only model alone achieved an AUPRC of 0.284 versus 0.347 for
the full model. The incremental value of the full model is therefore modest; its contribution lies
in calibrated risk stratification and in pooling the pre-anchor MAP with a small number of ancillary
signals, rather than in revealing hidden physiology.

### Limitations

1. **External validation was performed as a transportability check with necessary adaptations and
   shows transfer of discrimination but not of calibration.** The model was validated externally in
   VitalDB without refitting or recalibrating, but three adaptations limit how the result should be
   read. First, because VitalDB records no intubation event, the anchor was adapted from induction
   (intubation) to operation start (opstart), which occurs after induction; the external pre-anchor
   window therefore captures early-intraoperative rather than pre-induction physiology, a different
   phase from the development window. Second, the one MOVER-specific timing feature that could be
   re-derived under the opstart anchor — the interval from operation start to the prediction anchor —
   necessarily changes meaning between cohorts (OR-start-to-intubation in MOVER, case-start-to
   -operation-start in VitalDB) and is a residual source of transportability error. Third, the
   external cohort was restricted to 3,735 of 6,388 VitalDB cases with valid operation timing and an
   arterial MAP track, introducing selection we could not characterise fully, and a further 214
   external cases were classified D1-negative by construction for having fewer than 10 post-anchor
   MAP measurements. The external cohort also had a substantially lower outcome prevalence (5.73% vs
   15.55%) and a different recording architecture (continuous arterial pressure rather than
   intermittent non-invasive measurement), so the external AUPRC cannot be compared directly with the
   internal value; the external AUROC (0.744) indicates that ranking transferred, although its
   confidence interval overlaps the internal interval. Predicted probabilities were not calibrated to
   the external cohort (mean predicted risk 0.37 vs observed 0.057), so the external result supports
   deployment readiness of the *discrimination* but not of the *probabilities*.
2. **Severe sparsity of non-invasive blood pressure.** Median 3 readings in the 15-minute
   pre-anchor window; 96.2% of recording segments are single minutes. This caps achievable
   performance and makes any sustained-duration definition effectively unmeasurable.
3. **No preoperative baseline.** Fewer than 1% of cases had any MAP recording in the 30 minutes
   before OR start, so relative-threshold definitions could not be computed. This is a property of
   the source data, not a design choice.
4. **No physiological severity or outcome linkage.** ASA physical status was not available, and the
   database contains no postoperative outcomes, so the model could not be linked to acute kidney
   injury, myocardial injury or mortality. The endpoint is a surrogate.
5. **Anchor proxy and spectrum bias.** In 18.0% of cases the anchor was Surgery start rather than
   intubation, because no intubation event was recorded. This is not merely a labelling nuisance:
   the anchor source was among the strongest predictors (anchor is intubation ranked third by gain),
   so the proxy cohort — cases without a recorded intubation, which may systematically differ, for
   example monitored anaesthesia care or non-intubated procedures — introduces spectrum bias that
   the model can exploit but that may not transfer.
6. **Unequal domain coverage.** Invasive monitoring, ventilation, laboratory and fluid domains were
   available for 14.8%, 28.8%, 0.45% and 16.6% of cases respectively, so the model is driven
   largely by demographics, surgical group, anaesthetic events and non-invasive pressure.
7. **Structural exclusions and spectrum bias.** 1,496 cases (8.9%) had fewer than 10 post-anchor
   measurements and were classified as negative by construction — 1,332 with 1–9 readings and 164
   with no post-anchor MAP recording at all. This is a spectrum effect: the
   excluded cases are exactly those with the sparsest monitoring, and they are therefore not missing
   at random. A visible proxy confirms the mechanism: 42.9% of the excluded cases had a
   Surgery-start anchor versus 18.0% overall, and the anchor-source indicator is among the
   strongest predictors, so the model can score these cases low for reasons unrelated to
   physiology. The conditional prevalence among cases with at least 10 measurements was 17.1%
   (2,622 of 15,365); a sensitivity analysis restricted to those 15,365 evaluable cases is reported
   in the Results and shows that XGBoost discrimination improved to AUPRC 0.401 (95% CI 0.358–0.444) and AUROC 0.735 (0.710–0.757) – an apparent gain driven by removal of the negative-by-construction cases rather than by added physiological signal. Anthropometric cleaning set 37 heights, 18 weights and 6 BMI
   values to missing.
8. **Single author, no preregistration.** The analysis protocol was fixed before modelling but was
   not publicly registered. Predictor importance is descriptive and should not be read as inference.
9. **Outcome-label validity under sparse sampling.** D1 is an exposure-fraction definition that treats each recorded MAP as representative of the true intraoperative pressure; under the observed 19.89% row-level recording density (case-minute MAP recording rate 19.6%), with 96.2% of non-null segments consisting of isolated single minutes, recorded MAP is not a random sample of the surgical period. Cases monitored only during stable intervals could be under-counted as burden-free, so the reported prevalence and performance may be sensitive to which minutes were recorded. We state this as a structural limitation of deriving burden from intermittent non-invasive measurement rather than continuous arterial pressure.
10. **External discrimination may be inflated by recording density.** VitalDB records continuous arterial pressure, which both defines the outcome and supplies the MAP predictors far more densely and cleanly than the intermittent non-invasive measurement in MOVER/SIS; blood-pressure autocorrelation under dense sampling can inflate apparent ranking discrimination relative to the development cohort. The external AUROC of 0.744 should therefore be read as evidence that ranking transferred under a denser measurement regime, not as evidence of intrinsically better discrimination than the development cohort.
11. **The model largely reflects the present blood pressure.** The dominant predictor is the
    pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the
    fraction of pre-anchor readings already below 65 mmHg. The model therefore largely extrapolates
    the patient's current pressure rather than discovering independent risk, and adds limited
    information beyond what a clinician reading the bedside monitor already has; a decision-curve
    benchmark against a MAP-only logistic model showed the full model's incremental net benefit was
    only 0.013 at threshold 0.15 (Figure 4).
12. **Anchor placement is imprecise for a minority of cases.** The Intubation anchor occurred a
    median of 15 minutes after OR start, but the distribution has a long right tail: 325 cases had
    an anchor more than 60 minutes after OR start (maximum 751 minutes, about 12.5 hours), so for
    those cases the "pre-anchor" window describes mid- or post-operative physiology rather than
    induction. In addition, a small number of clinically implausible events were recorded before
    the anchor (four extubations, one cardiopulmonary resuscitation and three head-frame
    applications, at lags up to 2,853 minutes), which we retained rather than silently deleted;
    they affect the pre-anchor event counters only.
13. **The transported feature set includes features with no external support.** Four of the 53
    transported features are recording-cadence counters whose VitalDB values lie far outside the
    MOVER range (median MAP-reading count 450 versus 3; minutes since last MAP reading 0.02 versus
    1.0), and one contextual feature (anchor is intubation) is frozen at zero in VitalDB. A
    sensitivity analysis restricting the transported model to the 39 physiological value-domain
    features is reported in the Results; the external discrimination under that restriction was
    AUROC 0.713 (95% CI 0.670–0.750) and AUPRC 0.151 (0.119–0.196) – only marginally below the 53-feature shipped value (0.744/0.158), confirming the dropped recording-cadence and context features contributed little.
14. **The external outcome is not the development outcome.** Because VitalDB samples arterial
    pressure far more densely, the same proportion-based rule implies a much larger absolute
    exposure for a positive external label (about 44 cumulative minutes below 65 mmHg at the median
    recording density versus 9 readings in MOVER), so the external prevalence of 5.73% is not
    directly comparable with the internal 15.55%. A sensitivity analysis re-deriving the external
    labels on a common one-minute grid with absolute-time thresholds is reported in the Results
    and showed the transported model still discriminated comparably (D1_samples: AUROC 0.744, AUPRC 0.158), confirming the transportability signal is not an artefact of the development label definition.

### What this study adds

Beyond the modest absolute performance, this study contributes five elements that are under-reported
in perioperative hypotension prediction and that hold independently of the discrimination achieved.

1. **A quantitative leakage audit on a public operating-room resource.** All seven time-stamped
   predictor domains were truncated at the prediction origin with no used record postdating its
   anchor (maximum interval 0.00 minutes; no unparseable timestamps), and the one residual boundary
   overlap — a MAP reading recorded exactly at the anchor minute, which belongs to both the feature
   and the outcome window — is quantified and shown not to change the conclusions. Such audits are
   uncommon yet essential wherever near-perfect discrimination has been claimed on sparse data,
   and they convert an unverifiable "cannot be reproduced" concern into a reported, auditable fact.
2. **A 14-definition outcome sensitivity analysis.** Apparent performance is shown to be largely an
   artefact of the chosen hypotension definition (prevalence spanning 0.01%–65.8%), and
   sustained-duration definitions are demonstrated to be effectively unmeasurable under the observed
   recording density (median 3 MAP readings in the pre-anchor window; 96.2% of segments a single
   minute). This gives future work on the same and similar resources a principled basis for choosing
   an evaluable endpoint.
3. **A transparent accounting of spectrum bias.** The 1,496 cases (8.9%) excluded by construction
   because of sparse monitoring are reported alongside the conditional prevalence among evaluable
   cases (17.1%, 2,622 of 15,365), quantifying how monitoring density shapes both the endpoint and
   the apparent signal rather than hiding it behind a single cohort prevalence.
4. **An honest MAP-only benchmark.** Against a logistic model using the pre-anchor mean MAP alone,
   the full model's incremental net benefit was only 0.013 at decision thresholds 0.10–0.15; this
   reframes the result as a calibrated risk-stratification aid anchored on the pre-induction pressure
   rather than a discovery of new physiology, and supplies future work with a realistic baseline on
   this resource.
5. **An honest external transportability check on an independent resource.** In VitalDB the model
   was applied unchanged with its anchor adapted to operation start; discrimination transferred
   (AUROC 0.744, in the same range as and overlapping the confidence interval of the internal
   0.698–0.710 for the same feature set) while calibration did not, isolating exactly what does and
   does not generalise and supplying a concrete deployment requirement (local recalibration on the
   deployment cohort's own anchor and recording regime) rather than an abstract "needs external
   validation" caveat. The differing endpoint definitions, recording densities and feature-space
   support between the two cohorts are quantified rather than glossed over.

## Conclusions

Using only data available at the anaesthesia induction anchor, a gradient-boosted model achieved
modest but non-null discrimination (AUPRC 0.347, AUROC 0.722) for cumulative intraoperative
hypotension burden, reproduced under temporal validation and well calibrated after isotonic
recalibration. In an independent external cohort (VitalDB, n = 3,735) the same model retained
discrimination (AUROC 0.744) without refitting — a transportability check rather than a like-for-like
validation, because the external anchor (operation start) postdates induction and the external
outcome is defined on denser arterial sampling — although absolute probabilities were not
calibrated to that cohort and would require local updating. Most of the predictive information
resided in the pre-anchor arterial pressure level, suggesting that such models primarily identify
patients who are already relatively hypotensive at induction rather than anticipating new events. We
recommend that future work on this and similar resources prioritise local recalibration on the
deployment cohort's own anchor and recording regime, explicit reporting of the outcome definition
and its prevalence, and routine quantification of recording density, and that claims of
near-perfect discrimination on sparse non-invasive data be treated with corresponding caution.

---

## List of abbreviations

ASA, American Society of Anesthesiologists; AUROC, area under the receiver operating
characteristic curve; AUPRC, area under the precision–recall curve; BMI, body mass index; IQR,
interquartile range; MAP, mean arterial pressure; MOVER, Medical Informatics Operating Room Vitals
and Events Repository; OR, operating room; SIS, surgical information system; SpO₂, peripheral
oxygen saturation; TRIPOD, Transparent Reporting of a multivariable prediction model for
Individual Prognosis Or Diagnosis; VitalDB, Vital Signs Database.

## Declarations

**Ethics approval and consent to participate.** This study analysed a pre-existing, de-identified
database (MOVER, University of California Irvine) accessed under a signed data use agreement. No
patients were recruited, no intervention was performed, and no identifiable information was
accessed. Under the policy of the Institutional Review Board of The Second Affiliated Hospital of
Fujian University of Traditional Chinese Medicine, retrospective research that uses exclusively
pre-existing de-identified data obtained under a data use agreement is exempt from prospective
ethical review and from individual consent; the study was conducted under this exemption and no
approval number is reported. All procedures were conducted in accordance with the Declaration of Helsinki.

**Consent for publication.** Not applicable.

**Availability of data and materials.** The analysis used MOVER (University of California Irvine),
which is available to qualified researchers upon signature of a data use agreement
(https://mover.ics.uci.edu/; UCI Machine Learning Repository, https://doi.org/10.24432/C5VS5G).
Patient-level data are not redistributed by the author, as the data use agreement does not permit
this. All analysis code, the configuration file, the audit trail, and the aggregate result files
from which every number in this manuscript is generated are available at
https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.0 (v1.0.0 reproduction package), together with a manifest of
file checksums (MANIFEST.csv). Patient-level derived files (per-case feature matrix and outcome
labels) are regenerable from the MOVER source under the data use agreement by running the provided
pipeline (scripts/run_all.py).

**Competing interests.** The author declares no competing interests.

**Funding.** This research received no grant or monetary support from any funding agency in the
public, commercial or not-for-profit sectors.

**Authors' contributions.** YY conceived the study, designed and implemented the data pipeline,
performed all analyses, interpreted the results, and wrote and approved the manuscript. YY is the
sole author.

**Acknowledgements.** The author thanks the University of California Irvine for making the MOVER
resource available under a data use agreement.

**Authors' information.** Yongxin Yang, Department of Anesthesiology, The Second Affiliated
Hospital of Fujian University of Traditional Chinese Medicine, Fuzhou, China. ORCID
0009-0004-9698-6552.

**Use of artificial intelligence.** A large-language-model assistant was used to support code
writing, debugging and manuscript drafting. All study design decisions, all reported results, and
the final text were reviewed and are the sole responsibility of the author. The assistant is not
an author.

## References

1. Salmasi V, Maheshwari K, Yang D, Mascha EJ, Singh A, Sessler DI, et al. Relationship between
   intraoperative hypotension, defined by either reduction from baseline or absolute thresholds, and
   acute kidney and myocardial injury after noncardiac surgery: a retrospective cohort analysis.
   Anesthesiology. 2017;126(1):47–65. doi:10.1097/ALN.0000000000001432.
2. Wijnberge M, Geerts BF, Hol L, Lemmers N, Mulder MP, Berge P, et al. Effect of a machine
   learning-derived early warning system for intraoperative hypotension vs standard care on depth
   and duration of intraoperative hypotension during elective noncardiac surgery: the HYPE
   randomized clinical trial. JAMA. 2020;323(11):1052–1060. doi:10.1001/jama.2020.0592.
3. Maheshwari K, Shimada T, Yang D, Khanna S, Cywinski JB, Irefin SA, et al. Hypotension prediction
   index for prevention of hypotension during moderate- to high-risk noncardiac surgery.
   Anesthesiology. 2020;133(6):1214–1222. doi:10.1097/ALN.0000000000003557.
4. Alrantisi KMM. Predicting intraoperative hypotension using machine learning: a comprehensive analysis of the
   MOVER dataset. Preprints.org. 2026. doi:10.20944/preprints202603.1373.v1.
5. Chaari N, Winski G, Hallbäck M, Lundström N, Björne H, Jacobsson M. Towards reliable prediction
   of intraoperative hypotension: a cross-center evaluation of deep learning-based and MAP-derived
   methods. J Clin Monit Comput. 2026;40(1):43–57. doi:10.1007/s10877-025-01357-0.
6. Hernández Rincón EH, Salcedo Garrido G, Tovar Acosta N, Ramírez Urueña JA. Artificial
   intelligence for predicting perioperative anaesthetic complications and supporting clinical
   decision-making: a scoping review. J Clin Monit Comput. 2026. doi:10.1007/s10877-026-01449-5.
7. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting
   clinical prediction models that use regression or machine learning methods. BMJ.
   2024;385:e078378. doi:10.1136/bmj-2023-078378.
8. MOVER (Medical Informatics Operating Room Vitals and Events Repository). UCI Machine Learning
   Repository. doi:10.24432/C5VS5G.
9. Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. J Mach
    Learn Res. 2011;12:2825–2830.
10. Chen T, Guestrin C. XGBoost: a scalable tree boosting system. In: Proceedings of the 22nd ACM
    SIGKDD International Conference on Knowledge Discovery and Data Mining. 2016:785–794.
    doi:10.1145/2939672.2939785.
11. Ke G, Meng Q, Finley T, et al. LightGBM: a highly efficient gradient boosting decision tree.
    In: Advances in Neural Information Processing Systems 30. 2017:3146–3154.
12. Oyarzun R. The dynamics of arterial pressure itself predict intraoperative hypotension beyond
    its current value: an interpretable additive model validated in 3,069 external patients under a
    selection-bias-resistant protocol. medRxiv. 2026. doi:10.1101/2026.08.26.26361468.
13. Chiu C, Braehler MR, Donovan AL, Butte AJ, Pirracchio R, Bishara AM. Development of a machine
    learning-derived model to predict unplanned ICU admissions after major non-cardiac surgery.
    BMC Anesthesiol. 2025;25:351. doi:10.1186/s12871-025-03195-8.
14. Cheun H, Ahn JH, Park JW, et al. Development and external validation of a machine learning
    model for predicting severe immediate postoperative complications in adults undergoing cardiac
    surgery. BMC Anesthesiol. 2026;26:334. doi:10.1186/s12871-026-03841-9.
15. Walsh M, Devereaux PJ, Garg AX, et al. Relationship between intraoperative mean arterial
    pressure and clinical outcomes after noncardiac surgery: toward an empirical definition of
    hypotension. Anesthesiology. 2013;119(3):507–515. doi:10.1097/ALN.0b013e3182a10e26.
16. Sun LY, Wijeysundera DN, Tait GA, Beattie WS. Association of intraoperative hypotension with acute kidney injury after elective noncardiac surgery. Anesthesiology. 2015;123(3):515–523. doi:10.1097/ALN.0000000000000765.
17. Saugel B, Fletcher N, Gan TJ, Grocott MPW, Myles PS, Sessler DI, et al. PeriOperative Quality Initiative (POQI) international consensus statement on perioperative arterial pressure management. Br J Anaesth. 2024;133(2):264–276. doi:10.1016/j.bja.2024.04.046.
18. Lee HC, Park Y, Yoon SB, Yang SM, Park D, Jung CW. VitalDB, a high-fidelity multi-parameter vital signs database in surgical patients. Sci Data. 2022 Jun 8;9(1):279. doi:10.1038/s41597-022-01411-5. PMID: 35676300; PMCID: PMC9178032.
19. Hatib F, Jian Z, Buddi S, Lee C, Settels J, Sibert K, et al. Machine-learning algorithm to predict hypotension based on high-fidelity arterial pressure waveform analysis. Anesthesiology. 2018;129(4):663–674. doi:10.1097/ALN.0000000000002300. PMID: 29894315.
20. Riley RD, Ensor J, Snell KIE, Harrell FE Jr, Martin GP, Reitsma JB, et al. Calculating the sample size required for developing a clinical prediction model. BMJ. 2020 Mar 18;368:m441. doi:10.1136/bmj.m441. PMID: 32184264.
21. Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW; Topic Group 'Evaluating diagnostic tests and prediction models' of the STRATOS initiative. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019 Dec 16;17(1):230. doi:10.1186/s12916-019-1466-7. PMID: 31842878; PMCID: PMC6912996.

## Figure legends

**Figure 1. Cohort construction.** Flow from 19,114 screened records to the 16,861 analysed cases,
showing exclusions for implausible operating room window (n = 8), fewer than 60 recorded
vital-sign observations within the operating-room window (n = 1,632), age below 18 years (n = 371)
and absent or out-of-window prediction anchor (n = 242).

**Figure 2. Prevalence of the 14 candidate outcome definitions.** Definitions ordered by prevalence,
with the primary definition D1 highlighted.

**Figure 3. Model performance.** Precision–recall and receiver operating characteristic curves for
all four models on the patient-level split.

**Figure 4. Calibration and decision curve analysis.** Calibration plot before and after out-of-fold
isotonic recalibration, and net benefit across threshold probabilities for XGBoost, a MAP-only
logistic benchmark, treat all and treat none.

**Figure 5. Predictor importance.** Twenty-five highest-gain predictors from XGBoost.

**Figure 6. External transportability check in VitalDB.** Receiver operating characteristic
(left), precision–recall (centre) and predicted-risk distribution (right) for the MOVER core model
applied unchanged to the VitalDB arterial cohort (n = 3,735; outcome prevalence 5.73%).

## Additional files

**Additional file 1.** Audit trail: every number reported in this manuscript, its producing result
file, and the command that reproduces it (CSV).

**Additional file 2.** TRIPOD+AI (2024) reporting checklist, with each item mapped to the relevant
manuscript section or result file.
