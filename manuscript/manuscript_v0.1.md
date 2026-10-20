# Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: development and internal validation in MOVER/SIS with external validation in VitalDB

**Yongxin Yang**¹  ORCID 0009-0004-9698-6552

¹ Department of Anesthesiology, The Second Affiliated Hospital of Fujian University of
Traditional Chinese Medicine, Fuzhou, Fujian 350003, China

Correspondence: Yongxin Yang — 960856791@qq.com

---

## Abstract

**Background:** Intraoperative hypotension is associated with kidney and myocardial injury.
Reported machine-learning performance varies widely, and near-perfect discrimination has been claimed
on public datasets with sparse blood-pressure recordings. We developed and validated (internally and
externally) a model predicting cumulative hypotension burden over the remainder of surgery from data
available at the anaesthesia induction anchor.

**Methods:** Retrospective cohort from MOVER/SIS (University of California Irvine; data use
agreement). Of 19,114 screened records, 16,861 adult cases had a valid anchor (first intubation
event, 82.1%; otherwise surgery start, 17.9%). The primary outcome required ≥10 mean arterial
pressure (MAP) measurements after the anchor with ≥30% below 65 mmHg. Predictors were truncated at
the anchor; four models were fitted (baseline, full logistic, XGBoost, LightGBM). Validation used
patient-level (primary) and temporal (secondary) splits; the unchanged MOVER core model was also
applied to the VitalDB arterial cohort (n = 3,735; anchor adapted from intubation to operation
start; no refitting). AUPRC was the primary metric; AUROC, Brier and 1,000 bootstrap confidence
intervals were secondary; out-of-fold isotonic calibration and decision curve analysis were performed.

**Results:** The outcome occurred in 2,622 of 16,861 cases (15.55%). XGBoost achieved AUPRC 0.347
(95% CI 0.309–0.387) and AUROC 0.722 (0.697–0.745) on the patient-level split, versus 0.234
(baseline), 0.301 (full logistic) and 0.337 (LightGBM); on the temporal split it achieved 0.339
(0.291–0.395) and 0.733 (0.703–0.762). Isotonic recalibration improved the Brier score from 0.191
to 0.119. Performance was higher in women and younger patients; pre-anchor mean MAP was the dominant
predictor. Externally (VitalDB, prevalence 5.7%), the unchanged model retained discrimination
(AUROC 0.751, 95% CI 0.713–0.784; AUPRC 0.160, 0.129–0.202) but probabilities were uncalibrated.

**Conclusions:** An anchor-based model using routinely recorded pre-induction data achieved modest
but non-null discrimination for cumulative hypotension burden and was well calibrated. External
validation confirmed transfer of discrimination but not of absolute probabilities, which would
require local recalibration before clinical use.

**Keywords:** intraoperative hypotension; machine learning; clinical prediction model; mean
arterial pressure; perioperative medicine; calibration; TRIPOD

---

## Background

Intraoperative hypotension is common and consistently associated with organ injury. Salmasi and
colleagues showed that MAP below an absolute threshold of 65 mmHg was progressively related to
both myocardial and kidney injury after non-cardiac surgery, that prolonged exposure increased
the odds at any given threshold, and that absolute thresholds discriminated as well as relative
thresholds derived from preoperative pressure [1]. These conclusions have since been reinforced
by a systematic review of intraoperative hypotension and adverse postoperative outcomes [17] and
by a perioperative consensus that recommends keeping intraoperative mean arterial pressure at or
above 60 mmHg in at-risk patients [18], and by further work linking intraoperative mean arterial
pressure to outcomes [16]. These findings shifted attention from the
lowest recorded value towards the *cumulative burden* of hypotensive exposure.

That shift created a demand for anticipation. Commercial indices derived from arterial waveforms,
most notably the Hypotension Prediction Index, have been evaluated in randomised trials [2,3],
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
case-minutes and 96.2% of non-empty recording segments are isolated single minutes. Under such
sparsity, discrimination of that magnitude is difficult to attribute to physiological signal.
A cross-centre evaluation reached a closely related conclusion, showing that apparent advantage
of deep-learning models over simple threshold rules largely disappears once cases already
hypotensive at the prediction origin are excluded and the grey zone is retained [5], and a
scoping review of perioperative artificial intelligence found external validation and
bias-resistant evaluation to be uncommon [6].

We therefore set out to develop and validate (internally and externally) a model for the *cumulative burden* of
hypotension over the remainder of surgery, using only information available at the anaesthesia
induction anchor, and to report it under an explicit leakage audit, with calibration and
decision-analytic evaluation, and with an honest account of what the recording density of the
source data permits.

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
3,156,668 minutes, indicating corrupt timestamps); 1,632 records with an OR window shorter than
60 minutes; and 371 records of patients younger than 18 years. This left 17,103 cases. A further
242 cases were excluded because no valid prediction anchor could be determined (anchor falling
outside the OR window), yielding an analysis cohort of **16,861** cases contributing 3,559,993
one-minute OR observations. Median OR duration was 167 minutes.

### Prediction anchor

The prediction anchor was the first recorded Intubation event (n = 13,834; 82.1%). Where no
intubation event existed, Surgery start was used as a proxy (n = 3,027; 17.9%). The anchor occurred
a median of 15 minutes (IQR 11–24) after OR start. The observation window after the anchor had a
median duration of 147 minutes (5th–95th percentile 49–440).

### Outcome

The primary outcome (D1) was a cumulative-burden definition aligned with the absolute-threshold
framework of Salmasi et al. [1]: at least 10 MAP measurements after the anchor, of which at least
30% were below 65 mmHg. Cases with fewer than 10 post-anchor measurements were classified as
negative by construction; this applied to 1,496 cases (8.9%), because the definition deliberately
requires a minimum amount of evidence before a burden can be asserted.

Because the choice of hypotension definition materially changes apparent performance, 14 candidate
definitions were computed for every case and are reported in full (Table 2) [9]. They comprise
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
0.00 minutes, and no record had an unparseable timestamp.

Surgical group was assigned from the free-text procedure description by keyword mapping into 12
categories with a controlled fuzzy fallback (edit distance ≤1, identical initial, minimum length
7 characters). The residual "other" category contained 348 cases (2.1%).

Anthropometric variables required cleaning. Height and weight in the source contained unit-entry
errors (observed height as low as 2 cm, weight as high as 839 kg), which propagated to body mass
index values as extreme as 2.2 × 10⁵ kg/m². Values outside adult plausible ranges (height
100–220 cm; weight 25–300 kg; BMI 10–80 kg/m²) were set to missing rather than imputed: 37
heights, 18 weights and 6 BMI values were affected, leaving BMI computable for 16,699 cases
(99.0%).

### Model development

Four models were pre-specified. A *baseline* logistic model used age, sex and BMI only, to
quantify how much the full predictor set adds. A *full* logistic model used all predictors after
median imputation with missingness indicators and standardisation, with balanced class weighting.
*XGBoost* (300 trees, depth 4, learning rate 0.05, subsample 0.8, column sampling 0.8, minimum
child weight 10, L2 penalty 1.0, class-weight scaling) and *LightGBM* (300 trees, 15 leaves,
learning rate 0.05, subsample 0.8, column sampling 0.8, minimum 20 samples per leaf, L2 penalty
1.0, balanced class weighting) used native handling of missing values and required no imputation.

### External validation cohort

To test generalisability beyond the development site, the MOVER core model was applied unchanged to
VitalDB [19], an independent public database of high-fidelity vital signs from surgical patients at
a single tertiary centre (Seoul National University Hospital, Republic of Korea), accessed through
its public application programming interface without authentication. Because VitalDB records no
intubation event, the prediction anchor was adapted from the MOVER intubation anchor to the
operation start time (opstart), the closest available analogue, and the outcome D1 was computed
identically over the window [opstart, opend]. The external cohort comprised cases with an arterial
mean arterial pressure track (Solar8000/ART_MBP or EV1000/ART_MBP) and valid opstart/opend times
(n = 3,735). Predictors were restricted to the 53-feature transportable subset (demographics and
pre-anchor 15-minute vital-sign statistics) available in both resources; MOVER-specific timing
signals (anchor is intubation, intubation event recorded) and the calendar-year indicator, which are
not derivable from VitalDB, were set to zero. The MOVER core model (53 features, seed 12,345) was
applied without any external refitting or recalibration; performance was summarised by AUPRC
(primary), AUROC and Brier score, with 95% confidence intervals from 1,000 bootstrap resamples.
Calibration was assessed descriptively and was not updated on the external data.

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
Calibration slope and intercept were reported. Decision curve analysis quantified net benefit
across threshold probabilities.

Predictor importance was reported as XGBoost gain. Because gain reflects the fitted model rather
than an inferential quantity, it is presented descriptively.

### Software and reproducibility

Analyses used Python 3.13 with pandas 2.3.3, scikit-learn 1.9.0, XGBoost 3.4.1 and LightGBM 4.7.0.
The random seed was fixed at 12,345. Every number reported in this manuscript is generated from a
result file by the analysis pipeline and is traceable through an audit trail (Additional file 1)
that records, for each quantity, its value, the producing artefact and the command that
reproduces it [10–12].

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
| Anchor = Intubation — n (%) | 13,834 (82.1) |
| Anchor = Surgery start (proxy) — n (%) | 3,027 (17.9) |
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
| Demographics | 6 | — | 99.8 | n/a (static) |
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
similar on AUROC (0.724 vs 0.722) but slightly lower on AUPRC. The full logistic model reached
AUPRC 0.301, and the age/sex/BMI baseline 0.234, indicating that the additional predictors
contribute meaningfully beyond basic demographics while the absolute gain remains moderate.

Results on the temporal split were closely similar (XGBoost AUPRC 0.339, AUROC 0.733), indicating
no material calendar-time drift.

**Table 4. Model performance on the patient-level (primary) and temporal (secondary) splits.**

| Split | Model | n train | n test | Events in test | AUPRC (95% CI) | AUROC (95% CI) | Brier |
|---|---|---|---|---|---|---|---|
| Patient | Baseline logistic (age, sex, BMI) | 13,488 | 3,373 | 525 | 0.234 (0.207–0.268) | 0.626 (0.597–0.653) | 0.239 |
| Patient | Full logistic | 13,488 | 3,373 | 525 | 0.301 (0.268–0.340) | 0.707 (0.682–0.729) | 0.216 |
| Patient | **XGBoost** | 13,488 | 3,373 | 525 | **0.347 (0.309–0.387)** | **0.722 (0.697–0.745)** | 0.191 |
| Patient | LightGBM | 13,488 | 3,373 | 525 | 0.337 (0.301–0.375) | 0.724 (0.699–0.745) | 0.183 |
| Temporal | Baseline logistic | 15,043 | 1,818 | 291 | 0.243 (0.209–0.288) | 0.609 (0.574–0.646) | 0.240 |
| Temporal | Full logistic | 15,043 | 1,818 | 291 | 0.336 (0.289–0.394) | 0.725 (0.693–0.757) | 0.227 |
| Temporal | **XGBoost** | 15,043 | 1,818 | 291 | **0.339 (0.291–0.395)** | **0.733 (0.703–0.762)** | 0.194 |
| Temporal | LightGBM | 15,043 | 1,818 | 291 | 0.337 (0.290–0.392) | 0.732 (0.703–0.761) | 0.188 |

AUPRC under no skill equals the prevalence (0.1555). Brier scores are for uncalibrated predictions.

### Calibration and clinical usefulness

For XGBoost on the patient-level split, the uncalibrated Brier score was 0.191, which exceeds the
no-information Brier score of 0.131 (prevalence × (1 − prevalence)); this confirms meaningful
miscalibration for which recalibration was required rather than cosmetic. Out-of-fold isotonic
recalibration reduced the Brier score to 0.119, with a calibration slope of 0.909 and an intercept
of 0.008, indicating well-calibrated probabilities on the log-odds scale. On the temporal split the
Brier score improved from 0.194 to 0.122, with slope 0.934 and intercept 0.006.

In decision curve analysis, the calibrated model's net benefit exceeded that of both default
strategies (treat all, treat none) across the evaluated threshold range, remaining positive up to a
threshold of 0.58 on the patient-level split and 0.73 on the temporal split (with a transient dip
near 0.67 on the temporal split). At a threshold of 0.15, close to the outcome prevalence, net
benefit was 0.050 and 0.058 respectively; at a threshold of 0.10 it was 0.079 and 0.085. In a
benchmark against a logistic model using the pre-anchor mean MAP alone, the full model's incremental
net benefit was 0.013 at both thresholds 0.10 and 0.15 (Figure 4).

### Subgroup performance

Performance varied systematically (Table 5). AUPRC was higher in women than men, declined
monotonically with age, and was highest in underweight patients. These patterns were reproduced on
the temporal split for sex and age. The underweight subgroup was an exception: AUPRC was 0.616 on
the patient-level split but 0.382 on the temporal split, and with only 98 cases in the patient-level test-set stratum (512 in the full cohort)
the estimate should be regarded as unstable.

**Table 5. AUPRC of XGBoost by subgroup (held-out test set).**

| Subgroup | n (test) | Patient split | Temporal split |
|---|---|---|---|
| Men | 1,689 | 0.299 | 0.267 |
| Women | 1,684 | 0.357 | 0.370 |
| Age < 50 years | 1,402 | 0.380 | 0.377 |
| Age 50–64 years | 1,044 | 0.324 | 0.305 |
| Age ≥ 65 years | 927 | 0.186 | 0.194 |
| BMI < 18.5 kg/m² | 98 | 0.616 | 0.382 |
| BMI 18.5–24.9 kg/m² | 1,202 | 0.392 | 0.354 |
| BMI 25–29.9 kg/m² | 1,064 | 0.286 | 0.306 |
| BMI ≥ 30 kg/m² | 977 | 0.257 | 0.330 |

n denotes the number of cases in the held-out test set on which each subgroup AUPRC was computed
(patient-level split: 3,373; temporal split: 1,818). Subgroup AUPRCs are exploratory given the
reduced event counts within strata; for example, the underweight stratum comprised 98
patient-level test-set cases (512 in the full cohort).

### Predictor importance

Pre-anchor arterial pressure dominated (Table 6). Mean MAP had a gain roughly 2.3 times that of the
next predictor. The remaining informative predictors were the maximum pre-anchor MAP, whether the
anchor was an intubation event, the elapsed time from OR start to the anchor, the fraction of
pre-anchor readings already below 65 mmHg, surgical group, and diastolic and invasive arterial
pressure summaries.

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

### External validation

The MOVER core model was applied without refitting to the VitalDB arterial cohort of 3,735 cases, of
which 214 (5.73%) met the D1 outcome (Table 7). Discrimination transferred: the external AUROC was
0.751 (95% CI 0.713–0.784), numerically above the internal patient-level value of 0.698 and the
temporal value of 0.710 for the same 53-feature model, and the external AUPRC of 0.160
(0.129–0.202) exceeded the external prevalence by a factor of 2.8, a larger relative lift than the
2.1-fold internal value for that model. The lower absolute AUPRC reflects the much lower external
prevalence (5.73% vs 15.55%) rather than a loss of ranking ability. Absolute probabilities did not
transfer: the mean predicted risk was 0.37 against an observed prevalence of 0.057 (external Brier
score 0.179), indicating that the model would require local recalibration before the predicted
probabilities could be used directly. These results are summarised in Figure 6 and Table 7.

**Table 7. External validation of the MOVER core model (53 features) in VitalDB versus internal
performance of the same model in MOVER/SIS.**

| Dataset | Split | n | Events | Prevalence (%) | AUPRC (95% CI) | AUROC (95% CI) | Brier |
|---|---|---|---|---|---|---|---|
| MOVER/SIS (development) | Patient | 3,373 | 525 | 15.55 | 0.321 (0.284–0.362) | 0.698 (0.673–0.723) | 0.198 |
| MOVER/SIS (development) | Temporal | 1,818 | 291 | 15.55 | 0.314 (0.269–0.365) | 0.710 (0.679–0.740) | 0.199 |
| VitalDB (external) | — | 3,735 | 214 | 5.73 | 0.160 (0.129–0.202) | 0.751 (0.713–0.784) | 0.179 |

Internal values are for the identical 53-feature transportable model; the development manuscript
headline (AUPRC 0.347, AUROC 0.722) is for the full 206-feature model. The external cohort had no
refitting or recalibration.

## Discussion

### Principal findings

In a cohort of 16,861 adult surgical cases, a gradient-boosted model using only information
available at the induction anchor achieved an AUPRC of 0.347 and an AUROC of 0.722 for the
cumulative burden of hypotension over the remainder of surgery, with closely similar performance
under temporal validation and good calibration after isotonic recalibration. Discrimination was
therefore approximately 2.2-fold (2.23×) better than the no-skill baseline on the precision–recall
scale — modest, but clearly not null — and the decision curve showed the model yielded positive net
benefit relative to both default strategies across threshold probabilities up to 0.58
(patient-level) and 0.73 (temporal). The decision-relevant region is therefore thresholds near to
moderately above the outcome prevalence (roughly 0.10–0.30), where the calibrated probabilities
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

This interpretation is consistent with the stratified findings. Performance declined sharply with
age, which is the opposite of what a purely risk-factor-based model would predict, and was higher
in women. Both patterns are compatible with the model tracking pre-anchor pressure levels, whose
distribution and prognostic weight differ across these strata, rather than with the model
identifying age- or sex-specific vulnerability.

### Relation to previous work

Our results stand in marked contrast to the near-perfect discrimination recently reported on the
same public resource [4]. We do not question that analysis directly, since the details necessary to
reproduce it are not available to us; we raise it as a methodological hazard rather than a claim
about any specific report. Two facts are open to any reader. First, in the component analysed here,
non-invasive arterial pressure is recorded in fewer than one in five case-minutes and almost all
recorded segments are isolated single minutes, so the physiological trajectory available to any
model is extremely coarse. Second, an independent external evaluation on the same resource reported
an AUROC of 0.696 for a deliberately simple three-variable additive model under a
selection-bias-resistant protocol [13], and a cross-centre evaluation attributed inflated
performance to selection effects rather than to genuine generalisability [5]; our AUROC of 0.722
is consistent in magnitude with the former. We note that the same external analysis reported that
the *dynamics* of arterial pressure, not only its current value, carry incremental predictive
information for hypotension [13]. Our recording density (median 3 MAP readings in the 15-minute
pre-anchor window) is too sparse to characterise such dynamics, so our model necessarily leans on
the static pre-anchor level; this is a limitation of the source data rather than evidence against
the dynamics signal. Other investigators have developed machine-learning models for intraoperative
risk from comparable operating-room resources, including external-validation studies [14,15]. We now
provide such an external validation ourselves, in VitalDB, an independent resource with a different
recording architecture; the model's ranking ability transferred (external AUROC 0.751, above the
internal 0.698–0.710 for the same 53-feature model) while absolute probabilities did not and would
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

1. **External validation was performed with necessary adaptations and shows transfer of
   discrimination but not of calibration.** The model was validated externally in VitalDB without
   refitting or recalibrating; the anchor was adapted from intubation to operation start (VitalDB
   records no intubation event) and MOVER-specific timing signals were set to zero. The external
   cohort had a substantially lower outcome prevalence (5.73% vs 15.55%) and a different
   recording architecture (continuous arterial pressure rather than intermittent non-invasive
   measurement), so the external AUPRC cannot be compared directly with the internal value; the
   external AUROC (0.751) indicates that ranking transferred. Predicted probabilities were not
   calibrated to the external cohort (mean predicted risk 0.37 vs observed 0.057), so the external
   result supports deployment readiness of the *discrimination* but not of the *probabilities*.
2. **Severe sparsity of non-invasive blood pressure.** Median 3 readings in the 15-minute
   pre-anchor window; 96.2% of recording segments are single minutes. This caps achievable
   performance and makes any sustained-duration definition effectively unmeasurable.
3. **No preoperative baseline.** Fewer than 1% of cases had any MAP recording in the 30 minutes
   before OR start, so relative-threshold definitions could not be computed. This is a property of
   the source data, not a design choice.
4. **No physiological severity or outcome linkage.** ASA physical status was not available, and the
   database contains no postoperative outcomes, so the model could not be linked to acute kidney
   injury, myocardial injury or mortality. The endpoint is a surrogate.
5. **Anchor proxy and spectrum bias.** In 17.9% of cases the anchor was Surgery start rather than
   intubation, because no intubation event was recorded. This is not merely a labelling nuisance:
   the anchor source was among the strongest predictors (anchor is intubation ranked third by gain),
   so the proxy cohort — cases without a recorded intubation, which may systematically differ, for
   example monitored anaesthesia care or non-intubated procedures — introduces spectrum bias that
   the model can exploit but that may not transfer.
6. **Unequal domain coverage.** Invasive monitoring, ventilation, laboratory and fluid domains were
   available for 14.8%, 28.8%, 0.45% and 16.6% of cases respectively, so the model is driven
   largely by demographics, surgical group, anaesthetic events and non-invasive pressure.
7. **Structural exclusions and spectrum bias.** 1,496 cases (8.9%) had fewer than 10 post-anchor
   measurements and were classified as negative by construction. This is a spectrum effect: the
   excluded cases are exactly those with the sparsest monitoring (typically shorter or less-invasive
   cases) and are therefore not missing at random. The conditional prevalence among cases with at
   least 10 measurements was 17.1% (2,622 of 15,365), and excluding the sparse-monitoring cases may
   attenuate apparent performance. Anthropometric cleaning set 37 heights, 18 weights and 6 BMI
   values to missing.
8. **Single author, no preregistration.** The analysis protocol was fixed before modelling but was
   not publicly registered. Predictor importance is descriptive and should not be read as inference.
9. **The model largely reflects the present blood pressure.** The dominant predictor is the
   pre-anchor MAP level, and the next strongest predictors are the maximum pre-anchor MAP and the
   fraction of pre-anchor readings already below 65 mmHg. The model therefore largely extrapolates
   the patient's current pressure rather than discovering independent risk, and adds limited
   information beyond what a clinician reading the bedside monitor already has; a decision-curve
   benchmark against a MAP-only logistic model showed the full model's incremental net benefit was
   only 0.013 at threshold 0.15 (Figure 4).

### What this study adds

Beyond the modest absolute performance, this study contributes four elements that are under-reported
in perioperative hypotension prediction and that hold independently of the discrimination achieved.

1. **A quantitative leakage audit on a public operating-room resource.** All seven time-stamped
   predictor domains were truncated at the prediction origin with zero residual horizon overlap
   (maximum interval 0.00 minutes; no unparseable timestamps). Such audits are uncommon yet
   essential wherever near-perfect discrimination has been claimed on sparse data, and they
   convert an unverifiable "cannot be reproduced" concern into a reported, auditable fact.
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
5. **An honest external validation on an independent resource.** In VitalDB the model was applied
   unchanged; discrimination transferred (AUROC 0.751, exceeding the internal 0.698–0.710 for the
   same feature set) while calibration did not, isolating exactly what does and does not generalise
   and supplying a concrete deployment requirement (local recalibration) rather than an abstract
   "needs external validation" caveat.

## Conclusions

Using only data available at the anaesthesia induction anchor, a gradient-boosted model achieved
modest but non-null discrimination (AUPRC 0.347, AUROC 0.722) for cumulative intraoperative
hypotension burden, reproduced under temporal validation and well calibrated after isotonic
recalibration. In an independent external cohort (VitalDB, n = 3,735) the same model retained
discrimination (AUROC 0.751) without refitting, although absolute probabilities were not calibrated
to that cohort and would require local updating. Most of the predictive information resided in the
pre-anchor arterial pressure level, suggesting that such models primarily identify patients who are
already relatively hypotensive at induction rather than anticipating new events. We recommend that
future work on this and similar resources prioritise local recalibration at deployment, explicit
reporting of the outcome definition and its prevalence, and routine quantification of recording
density, and that claims of near-perfect discrimination on sparse non-invasive data be treated with
corresponding caution.

---

## List of abbreviations

AKI, acute kidney injury; AUROC, area under the receiver operating characteristic curve; AUPRC,
area under the precision–recall curve; BMI, body mass index; DUA, data use agreement; IOH,
intraoperative hypotension; IQR, interquartile range; MAP, mean arterial pressure; MOVER, Medical
Informatics Operating Room Vitals and Events Repository; OR, operating room; SIS, surgical
information system; SpO₂, peripheral oxygen saturation; TRIPOD, Transparent Reporting of a
multivariable prediction model for Individual Prognosis Or Diagnosis; VitalDB, Vital Signs Database.

## Declarations

**Ethics approval and consent to participate.** This study analysed a pre-existing, de-identified
database (MOVER, University of California Irvine) accessed under a signed data use agreement. No
patients were recruited, no intervention was performed, and no identifiable information was
accessed. Under the policy of the Institutional Review Board of The Second Affiliated Hospital of
Fujian University of Traditional Chinese Medicine, retrospective research that uses exclusively
pre-existing de-identified data obtained under a data use agreement is exempt from prospective
ethical review and from individual consent; the study was conducted under this exemption and no
approval number is reported. A retrospective waiver letter documenting this basis is being obtained
from the IRB. All procedures were conducted in accordance with the Declaration of Helsinki.

**Consent for publication.** Not applicable.

**Availability of data and materials.** The analysis used MOVER (University of California Irvine),
which is available to qualified researchers upon signature of a data use agreement
(https://mover.ics.uci.edu/; UCI Machine Learning Repository, https://doi.org/10.24432/C5VS5G).
Patient-level data are not redistributed by the author, as the data use agreement does not permit
this. All analysis code, the configuration file, the audit trail, and the aggregate result files
from which every number in this manuscript is generated are available at
https://github.com/yyx-4113/mover-sis-ioh-prediction (v1.0.0 reproduction package), together with a manifest of
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
9. This manuscript, Table 2 (all 14 definitions computed for every case; see Additional file 1).
10. Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. J Mach
    Learn Res. 2011;12:2825–2830.
11. Chen T, Guestrin C. XGBoost: a scalable tree boosting system. In: Proceedings of the 22nd ACM
    SIGKDD International Conference on Knowledge Discovery and Data Mining. 2016:785–794.
    doi:10.1145/2939672.2939785.
12. Ke G, Meng Q, Finley T, et al. LightGBM: a highly efficient gradient boosting decision tree.
    In: Advances in Neural Information Processing Systems 30. 2017:3146–3154.
13. Oyarzun R. The dynamics of arterial pressure itself predict intraoperative hypotension beyond
    its current value: an interpretable additive model validated in 3,069 external patients under a
    selection-bias-resistant protocol. medRxiv. 2026. doi:10.1101/2026.08.26.26361468.
14. Chiu C, Braehler MR, Donovan AL, Butte AJ, Pirracchio R, Bishara AM. Development of a machine
    learning-derived model to predict unplanned ICU admissions after major non-cardiac surgery.
    BMC Anesthesiol. 2025;25:351. doi:10.1186/s12871-025-03195-8.
15. Cheun H, Ahn JH, Park JW, et al. Development and external validation of a machine learning
    model for predicting severe immediate postoperative complications in adults undergoing cardiac
    surgery. BMC Anesthesiol. 2026;26:334. doi:10.1186/s12871-026-03841-9.
16. Walsh M, Devereaux PJ, Garg AX, et al. Relationship between intraoperative mean arterial
    pressure and clinical outcomes after noncardiac surgery: toward an empirical definition of
    hypotension. Anesthesiology. 2013;119(3):507–515.
17. Sun LY, Wijeysundera DN, Tait GA, Beattie WS. Association of intraoperative hypotension with acute kidney injury after elective noncardiac surgery. Anesthesiology. 2015;123(3):515–523. doi:10.1097/ALN.0000000000000765.
18. Saugel B, Fletcher N, Gan TJ, Grocott MPW, Myles PS, Sessler DI, et al. PeriOperative Quality Initiative (POQI) international consensus statement on perioperative arterial pressure management. Br J Anaesth. 2024;133(2):264–276. doi:10.1016/j.bja.2024.04.046.
19. Lee S, Park J, Lee S, Park Y, Kim S, Kim T, et al. VitalDB, a high-fidelity vital signs database in surgical patients. Sci Data. 2022;9:279. doi:10.1038/s41597-022-01794-9.

## Figure legends

**Figure 1. Cohort construction.** Flow from 19,114 screened records to the 16,861 analysed cases,
showing exclusions for implausible operating room window (n = 8), operating room window shorter
than 60 minutes (n = 1,632), age below 18 years (n = 371) and absent or out-of-window prediction
anchor (n = 242).

**Figure 2. Prevalence of the 14 candidate outcome definitions.** Definitions ordered by prevalence,
with the primary definition D1 highlighted.

**Figure 3. Model performance.** Precision–recall and receiver operating characteristic curves for
all four models on the patient-level split.

**Figure 4. Calibration and decision curve analysis.** Calibration plot before and after out-of-fold
isotonic recalibration, and net benefit across threshold probabilities for XGBoost, a MAP-only
logistic benchmark, treat all and treat none.

**Figure 5. Predictor importance.** Twenty-five highest-gain predictors from XGBoost.

**Figure 6. External validation in VitalDB.** Receiver operating characteristic (left), precision–recall (centre) and predicted-risk distribution (right) for the MOVER core model applied unchanged to the VitalDB arterial cohort (n = 3,735; outcome prevalence 5.73%).

## Additional files

**Additional file 1.** Audit trail: every number reported in this manuscript, its producing result
file, and the command that reproduces it (CSV).

**Additional file 2.** TRIPOD+AI (2024) reporting checklist, with each item mapped to the relevant
manuscript section or result file.
