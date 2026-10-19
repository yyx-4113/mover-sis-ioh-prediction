# Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: model development and internal validation in the MOVER/SIS cohort

**Yongxin Yang**¹  ORCID 0009-0004-9698-6552

¹ Department of Anesthesiology, The Second Affiliated Hospital of Fujian University of
Traditional Chinese Medicine, Fuzhou, Fujian 350003, China

Correspondence: Yongxin Yang — 960856791@qq.com

---

## Abstract

**Background:** Intraoperative hypotension is associated with kidney and myocardial injury.
Reported performance of machine-learning models for anticipating it varies widely, and
near-perfect discrimination has been claimed on public datasets whose blood-pressure recordings
are sparse. We developed and internally validated a model predicting cumulative hypotension
burden over the remainder of surgery from data available at the anaesthesia induction anchor.

**Methods:** Retrospective cohort from MOVER/SIS (University of California Irvine; data use
agreement). Of 19,114 screened records, 16,861 adult cases had a valid anchor (first Intubation
event, 82.0%; otherwise surgery start, 18.0%). The primary outcome required ≥10 mean arterial
pressure (MAP) measurements after the anchor with ≥30% below 65 mmHg. All 206 predictors were
truncated at the anchor. Four models were fitted: baseline logistic (age, sex, body mass index),
full logistic, XGBoost and LightGBM. Validation used a patient-level 80/20 split (primary) and a
temporal split (secondary). The primary metric was area under the precision–recall curve (AUPRC);
AUROC and Brier score were secondary; 1,000 bootstrap resamples gave confidence intervals.
Out-of-fold isotonic calibration and decision curve analysis were performed.

**Results:** The outcome occurred in 2,622 of 16,861 cases (15.55%). XGBoost achieved AUPRC 0.347
(95% CI 0.309–0.387) and AUROC 0.722 (0.697–0.745) on the patient-level split, versus 0.234
(baseline), 0.301 (full logistic) and 0.337 (LightGBM); on the temporal split it achieved 0.339
(0.291–0.395) and 0.733 (0.703–0.762). Isotonic recalibration improved the Brier score from 0.191
to 0.119 (slope 0.909; intercept 0.008). Net benefit at a threshold of 0.15 was 0.050.
Performance was higher in women (0.357 vs 0.299), patients under 50 years (0.380 vs 0.186 at ≥65
years) and underweight patients (0.616). Pre-anchor mean MAP was the dominant predictor.

**Conclusions:** An anchor-based model using routinely recorded pre-induction data achieved modest
but non-null discrimination for cumulative hypotension burden and was well calibrated. Most
information resided in the pre-anchor arterial pressure level. External validation is required
before clinical application.

**Keywords:** intraoperative hypotension; machine learning; clinical prediction model; mean
arterial pressure; perioperative medicine; calibration; TRIPOD

---

## Background

Intraoperative hypotension is common and consistently associated with organ injury. Salmasi and
colleagues showed that MAP below an absolute threshold of 65 mmHg was progressively related to
both myocardial and kidney injury after non-cardiac surgery, that prolonged exposure increased
the odds at any given threshold, and that absolute thresholds discriminated as well as relative
thresholds derived from preoperative pressure [1]. These findings shifted attention from the
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

We therefore set out to develop and internally validate a model for the *cumulative burden* of
hypotension over the remainder of surgery, using only information available at the anaesthesia
induction anchor, and to report it under an explicit leakage audit, with calibration and
decision-analytic evaluation, and with an honest account of what the recording density of the
source data permits.

## Methods

### Study design and data source

This is a retrospective cohort study reported in accordance with TRIPOD+AI [7]; it corresponds to
TRIPOD type 2a (development with internal validation, no external validation). The data source was
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

The prediction anchor was the first recorded Intubation event (n = 13,834; 82.0%). Where no
intubation event existed, Surgery start was used as a proxy (n = 3,027; 18.0%). The anchor occurred
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
| neurosurgical | 2,530 (15.0) |
| orthopaedic | 2,407 (14.3) |
| urological | 1,541 (9.1) |
| plastic | 1,318 (7.8) |
| vascular | 1,049 (6.2) |
| gynaecological | 992 (5.9) |
| thoracic | 958 (5.7) |
| ear, nose and throat | 418 (2.5) |
| other | 348 (2.1) |
| ophthalmic | 201 (1.2) |
| cardiac | 177 (1.0) |
| no surgery recorded | 6 (<0.1) |
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

For XGBoost on the patient-level split, out-of-fold isotonic recalibration reduced the Brier score
from 0.191 to 0.119. The calibrated calibration slope was 0.909 and the intercept 0.008, indicating
predictions close to ideal on the log-odds scale with only mild over-fitting. On the temporal
split, the Brier score improved from 0.194 to 0.122 with slope 0.934 and intercept 0.006.

In decision curve analysis, net benefit for the calibrated model was positive across threshold
probabilities up to 0.58 on the patient-level split and up to 0.45 on the temporal split. At a
threshold of 0.15, close to the outcome prevalence, net benefit was 0.050 and 0.058 respectively;
at a threshold of 0.10 it was 0.079 and 0.085.

### Subgroup performance

Performance varied systematically (Table 5). AUPRC was higher in women than men, declined
monotonically with age, and was highest in underweight patients. These patterns were reproduced on
the temporal split for sex and age. The underweight subgroup was an exception: AUPRC was 0.616 on
the patient-level split but 0.382 on the temporal split, and with only 512 patients in that stratum
the estimate should be regarded as unstable.

**Table 5. AUPRC of XGBoost by subgroup.**

| Subgroup | n | Patient split | Temporal split |
|---|---|---|---|
| Men | 8,355 | 0.299 | 0.267 |
| Women | 8,502 | 0.357 | 0.370 |
| Age < 50 years | 6,915 | 0.380 | 0.377 |
| Age 50–64 years | 5,366 | 0.324 | 0.305 |
| Age ≥ 65 years | 4,580 | 0.186 | 0.194 |
| BMI < 18.5 kg/m² | 512 | 0.616 | 0.382 |
| BMI 18.5–24.9 kg/m² | — | 0.392 | 0.354 |
| BMI 25–29.9 kg/m² | — | 0.286 | 0.306 |
| BMI ≥ 30 kg/m² | — | 0.257 | 0.330 |

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

## Discussion

### Principal findings

In a cohort of 16,861 adult surgical cases, a gradient-boosted model using only information
available at the induction anchor achieved an AUPRC of 0.347 and an AUROC of 0.722 for the
cumulative burden of hypotension over the remainder of surgery, with closely similar performance
under temporal validation and good calibration after isotonic recalibration. Discrimination was
therefore approximately 2.2 times better than chance on the precision–recall scale — modest, but
clearly not null — and the predictions were clinically usable in a decision-analytic sense across
threshold probabilities up to about 0.20.

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
same public resource [4]. We do not question the authors' analysis directly, since the details
necessary to reproduce it are not available to us. We note only two facts that any reader can
weigh. First, in the component analysed here, non-invasive arterial pressure is recorded in fewer
than one in five case-minutes and almost all recorded segments are isolated single minutes, so the
physiological trajectory available to any model is extremely coarse. Second, an independent
pre-registered external evaluation on the same resource reported an AUROC of 0.696 for a
deliberately simple three-variable additive model [13], and a cross-centre evaluation attributed
inflated performance to selection effects rather than to genuine generalisability [5]. Our AUROC
of 0.722 is consistent in magnitude with the former. Performance of the order of 0.97 would require
near-separation of the classes, which in our judgement is more plausibly explained by the label
window overlapping the feature window, or by retaining as predictable events those cases already
below threshold at the prediction origin, than by physiological signal. We regard this as a
general methodological hazard in perioperative prediction rather than a criticism specific to one
report, and we note that our own estimate carries the same absence of external validation that we
identify as a limitation elsewhere [6].

### Implications

Three implications follow. First, the definition of the outcome should be stated with the same
prominence as the performance metric: across our 14 candidate definitions the prevalence ranged
from 0.01% to 65.8%, and no performance figure is interpretable without it. Second, cumulative-burden
outcomes are feasible on sparse data in a way that sustained-duration outcomes are not — sustained
definitions at conventional thresholds identified fewer than 60 cases here, which is an important
structural constraint on what can be modelled with non-invasive recordings. Third, anchor-based
prediction addresses a different clinical question from short-horizon prediction, and the two
should not be benchmarked against each other as though they were the same task.

### Limitations

1. **No external validation.** This is a single-centre development with internal validation only
   (TRIPOD type 2a). Discrimination and, in particular, calibration may not transfer.
2. **Severe sparsity of non-invasive blood pressure.** Median 3 readings in the 15-minute
   pre-anchor window; 96.2% of recording segments are single minutes. This caps achievable
   performance and makes any sustained-duration definition effectively unmeasurable.
3. **No preoperative baseline.** Fewer than 1% of cases had any MAP recording in the 30 minutes
   before OR start, so relative-threshold definitions could not be computed. This is a property of
   the source data, not a design choice.
4. **No physiological severity or outcome linkage.** ASA physical status was not available, and the
   database contains no postoperative outcomes, so the model could not be linked to acute kidney
   injury, myocardial injury or mortality. The endpoint is a surrogate.
5. **Anchor proxy.** In 18.0% of cases the anchor was Surgery start rather than intubation, because
   no intubation event was recorded. The direction of any resulting bias is uncertain.
6. **Unequal domain coverage.** Invasive monitoring, ventilation, laboratory and fluid domains were
   available for 14.8%, 28.8%, 0.45% and 16.6% of cases respectively, so the model is driven
   largely by demographics, surgical group, anaesthetic events and non-invasive pressure.
7. **Structural exclusions.** 1,496 cases (8.9%) had fewer than 10 post-anchor measurements and
   were classified as negative by construction; and anthropometric cleaning set 37 heights, 18
   weights and 6 BMI values to missing.
8. **Single author, no preregistration.** The analysis protocol was fixed before modelling but was
   not publicly registered. Predictor importance is descriptive and should not be read as inference.

## Conclusions

Using only data available at the anaesthesia induction anchor, a gradient-boosted model achieved
modest but non-null discrimination (AUPRC 0.347, AUROC 0.722) for cumulative intraoperative
hypotension burden, reproduced under temporal validation and well calibrated after isotonic
recalibration. Most of the predictive information resided in the pre-anchor arterial pressure
level, suggesting that such models primarily identify patients who are already relatively
hypotensive at induction rather than anticipating new events. We recommend that future work on
this and similar resources prioritise external validation, explicit reporting of the outcome
definition and its prevalence, and routine quantification of recording density, and that claims of
near-perfect discrimination on sparse non-invasive data be treated with corresponding caution.

---

## List of abbreviations

AKI, acute kidney injury; AUROC, area under the receiver operating characteristic curve; AUPRC,
area under the precision–recall curve; BMI, body mass index; DUA, data use agreement; IOH,
intraoperative hypotension; IQR, interquartile range; MAP, mean arterial pressure; MOVER, Medical
Informatics Operating Room Vitals and Events Repository; OR, operating room; SIS, surgical
information system; SpO₂, peripheral oxygen saturation; TRIPOD, Transparent Reporting of a
multivariable prediction model for Individual Prognosis Or Diagnosis.

## Declarations

**Ethics approval and consent to participate.** This study analysed a pre-existing, de-identified
database (MOVER, University of California Irvine) obtained under a signed data use agreement. No
patients were recruited, no intervention was performed, and no identifiable information was
accessed. In accordance with the policy of the Institutional Review Board of The Second Affiliated
Hospital of Fujian University of Traditional Chinese Medicine, research using exclusively
pre-existing de-identified data does not require prospective ethical approval; a formal
determination was therefore not sought, and no approval number is reported. All procedures were
conducted in accordance with the Declaration of Helsinki.

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
   Anesthesiology. 2017;126(1):47–65. doi:10.1097/ALN.0000000000001432. *(verified 2026-10-19)*
2. Wijnberge M, Geerts BF, Hol L, Lemmers N, Mulder MP, Berge P, et al. Effect of a machine
   learning-derived early warning system for intraoperative hypotension vs standard care on depth
   and duration of intraoperative hypotension during elective noncardiac surgery: the HYPE
   randomized clinical trial. JAMA. 2020;323(11):1052–1060. doi:10.1001/jama.2020.0592. *(verified 2026-10-20; PMID 32065827)*
3. Maheshwari K, Shimada T, Yang D, Khanna S, Cywinski JB, Irefin SA, et al. Hypotension prediction
   index for prevention of hypotension during moderate- to high-risk noncardiac surgery.
   Anesthesiology. 2020;133(6):1214–1222. doi:10.1097/ALN.0000000000003557. *(verified 2026-10-20)*
4. Alrantisi KMM. Predicting intraoperative hypotension using machine learning: a comprehensive analysis of the
   MOVER dataset. Preprints.org. 2026. doi:10.20944/preprints202603.1373.v1.
   *(unrefereed single-author preprint by Alrantisi KMM; posted 17 Mar 2026; verified 2026-10-20)*
5. Chaari N, Winski G, Hallbäck M, Lundström N, Björne H, Jacobsson M. Towards reliable prediction
   of intraoperative hypotension: a cross-center evaluation of deep learning-based and MAP-derived
   methods. J Clin Monit Comput. 2026;40(1):43–57. doi:10.1007/s10877-025-01357-0.
   *(verified 2026-10-19)*
6. Hernández Rincón EH, Salcedo Garrido G, Tovar Acosta N, Ramírez Urueña JA. Artificial
   intelligence for predicting perioperative anaesthetic complications and supporting clinical
   decision-making: a scoping review. J Clin Monit Comput. 2026. doi:10.1007/s10877-026-01449-5.
   *(verified 2026-10-19)*
7. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting
   clinical prediction models that use regression or machine learning methods. BMJ.
   2024;385:e078378. doi:10.1136/bmj-2023-078378. *(verified 2026-10-20)*
8. MOVER (Medical Informatics Operating Room Vitals and Events Repository). UCI Machine Learning
   Repository. doi:10.24432/C5VS5G. *(verified 2026-10-19)*
9. This manuscript, Table 2 (all 14 definitions computed for every case; see Additional file 1).
10. Pedregosa F, Varoquaux G, Gramfort A, et al. Scikit-learn: machine learning in Python. J Mach
    Learn Res. 2011;12:2825–2830. *(verified 2026-10-20; JMLR articles carry no DOI)*
11. Chen T, Guestrin C. XGBoost: a scalable tree boosting system. In: Proceedings of the 22nd ACM
    SIGKDD International Conference on Knowledge Discovery and Data Mining. 2016:785–794.
    doi:10.1145/2939672.2939785. *(verified 2026-10-20)*
12. Ke G, Meng Q, Finley T, et al. LightGBM: a highly efficient gradient boosting decision tree.
    In: Advances in Neural Information Processing Systems 30. 2017:3146–3154.
    *(verified 2026-10-20; NeurIPS proceedings carry no DOI)*
13. Oyarzun R. The dynamics of arterial pressure itself predict intraoperative hypotension beyond
    its current value: an interpretable additive model validated in 3,069 external patients under a
    selection-bias-resistant protocol. medRxiv. 2026. doi:10.1101/2026.08.26.26361468.
    *(unrefereed preprint; verified 2026-10-19)*
14. Chiu C, Braehler MR, Donovan AL, Butte AJ, Pirracchio R, Bishara AM. Development of a machine
    learning-derived model to predict unplanned ICU admissions after major non-cardiac surgery.
    BMC Anesthesiol. 2025;25:351. doi:10.1186/s12871-025-03195-8. *(verified 2026-10-20)*
15. Cheun H, Ahn JH, Park JW, et al. Development and external validation of a machine learning
    model for predicting severe immediate postoperative complications in adults undergoing cardiac
    surgery. BMC Anesthesiol. 2026;26:334. doi:10.1186/s12871-026-03841-9. *(verified 2026-10-20)*
16. Walsh M, Devereaux PJ, Garg AX, et al. Relationship between intraoperative mean arterial
    pressure and clinical outcomes after noncardiac surgery: toward an empirical definition of
    hypotension. Anesthesiology. 2013;119(3):507–515. *(verified 2026-10-19)*

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
isotonic recalibration, and net benefit across threshold probabilities, for XGBoost.

**Figure 5. Predictor importance.** Twenty-five highest-gain predictors from XGBoost.

## Additional files

**Additional file 1.** Audit trail: every number reported in this manuscript, its producing result
file, and the command that reproduces it (CSV).
