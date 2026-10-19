# SIS Intraoperative Hypotension Prediction

> MOVER 数据库二次开发 · 方向 1 · 创建于 2026-10-19
> 作者：杨永新（Yongxin Yang），福建中医药大学附属第二医院麻醉科 · ORCID 0009-0004-9698-6552

## 1. Research question

Can **demographic + early intraoperative physiological** features (first 10–15 min after induction) predict subsequent **intraoperative hypotension (IOH)** / hypoxaemia in the MOVER SIS cohort, with performance exceeding a clinical baseline, under patient-level and temporal splitting?

## 2. Why this direction is defensible

- **Zero overlap with the JCMC manuscript** (EPIC-only preoperative → AQI complications): the data custodian confirmed SIS (2015-11 ~ 2018-10) and EPIC (2017-2022) are **patient-disjoint** with no cross-system key. No salami-slicing, no same-cohort duplication.
- SIS demographics (Age/Ht/Wt/Gender) are **100% complete**, so BMI is computable here (it was 100% missing in EPIC).
- SIS `patient_procedure_events` gives **timestamped anaesthetic-technique signals** (Intubation / LMA / Sedation / Spinal / CSE / Epidural / CPBP) — a strong, interpretable IOH predictor absent from the EPIC preoperative feature set.
- ⚠️ **v1.0.0 的勘误**：本文件曾声称 "SIS vitals 100% non-null at 1-min resolution — a rare completeness level"。
  该说法**只对 HR（94.8%/95.9%）与 SpO2（96.1%）大致成立**；**BP 三列（nSBP/nMAP/nDBP）非空率仅约 20%**，
  是 NIBP 循环点测。这不构成"数据完整性优势"，而是**决定了结局定义必须用点测口径**（见 §5bis）。
  把"稀疏点测"误当"连续 1-min 流"正是 v1.0.0 结局数字全部作废的根因。

## 3. Data assets (all under `data_raw/`, verified 2026-10-19)

| Source | Scale | Notes |
|---|---|---|
| `_sis_emr_x/EMR/patient_vitals.csv` | 200 MB, 19,023 PID | 1-min HR/SpO2 ~95–96% non-null; **BP (nSBP/nMAP/nDBP) only ~20% non-null — NIBP 循环点测，非连续流** |
| `_sis_emr_x/EMR/patient_information.csv` | 3.4 MB, 19,114 PID | Age/Ht/Wt/Gender + OR_start/OR_end/Surgery_start/Surgery_end (100%), Procedure text (99.9%) |
| `_sis_emr_x/EMR/patient_observations.csv` | 179 MB | SVV, PAP (pulmonary artery), CO, cerebral oximetry, TOF, ICPm, CVPm, ART/FEM pressures |
| `_sis_emr_x/EMR/patient_ventilator.csv` | 76 MB | Volatile-agent Fi/Et, ETCO2, TV, RR, PEEP, PIP, FiO2 |
| `_sis_emr_x/EMR/patient_medication.csv` | 20 MB | Intraoperative doses with start/end times |
| `_sis_emr_x/EMR/patient_labs.csv` | 1.4 MB | Intraoperative blood gases (12 analytes) |
| `_sis_emr_x/EMR/patient_input_output.csv` | 6 MB | Fluid in / blood loss |
| `_sis_emr_x/EMR/patient_procedure_events.csv` | 2.2 MB, 18 event types | Intubation 15,007 / Extubation 15,258 / Sedation 2,343 / LMA 1,675 / Spinal 181 / CPBP 197 / Mayfield 165 |
| `_sis_emr_x/EMR/patient_a_line.csv` | 2,989 rows, 2,951 PID | radial 885 / femoral 48 / brachial 32 |
| `sis_vitals.csv` | 3.6M rows | flat 1-min vitals (merged view of patient_vitals) |

> ⚠️ **v1.0.0 的勘误**：本文件曾声称 "1-min HR/SBP/MAP/DBP/SpO2, 100% non-null"。
> 实测（`scripts/audit/a1_vitals_timeline.py`）：HRe 94.79% / HRp 95.90% / SP02 96.08%，
> 而 **nSBP 19.99% / nMAP 19.89% / nDBP 19.95%**。BP 三列是 NIBP 循环点测：
> 643,466 个连续非空段中 **96.2% 是孤立单分钟**，中位段长 1.0 min。
> **数据集里几乎不存在"连续 5 分钟有 MAP 记录"的序列** —— 这直接决定了结局定义必须用
> 点测口径（`point_burst` / `exposure_fraction`），不能用"连续 N 分钟"口径。

## 4. Outcome prevalence (computed 2026-10-19, `scripts/s1_cohort.py`, **engine v1.1.0**)

> 🔴 **v1.0.0 数字已全部作废。** 旧引擎 `dropna(subset=[signal])` 把 80% 的 NaN 分钟物理删除，
> 时间轴被压缩约 5×，"连续 5 个低值记录"在压缩数组里成立，在真实时钟上却跨越 20–40 分钟。
> 实测偏差：O1 高估 **10.1×**、O2 **3.9×**、O3 **14.5×**、O4 **41.3×**。
> 修法与复现：`review/Round1_review_2026-10-19.md` §2 + `scripts/audit/a2_outcome_definition_bug.py`。

**Analytic cohort = 17,107 → 17,103 PID**（19,114 源 → 剔除 OR 窗口不合理 8 例 → OR 窗口观测 <60 min 1,632 例 → age <18 371 例；瀑布自洽校验通过）。
口径纪律：v1.0.0 的"筛查口径 / 分析口径"双分母展示已退役——稿件统一只报分析队列口径，全队列瀑布见 `results/s1_cohort.json`。

### 4.1 MAP 维度（14 个定义全量，engine v1.1.0）

| ID | 类型 | 定义 | 阳性 (n=17,103) | 患病率 |
|---|---|---|---|---|
| **D1** | **exposure_fraction** | **≥10 次测量且 MAP<65 占比 ≥30%** | **2,544** | **14.87%** |
| E1 | any_below | 任一记录 MAP<55 | 4,105 | 24.00% |
| B1 | point_burst | ≥3 次 MAP<65 落在 30 min 内 | 7,634 | 44.64% |
| B2 | point_burst | ≥5 次 MAP<65 落在 60 min 内 | 5,554 | 32.47% |
| E2 | any_below | 任一记录 MAP<65 | 11,568 | 67.64% |
| B3 | point_burst | ≥3 次 MAP<55 落在 30 min 内 | 1,272 | 7.44% |
| S1 | sustained_measured | MAP<65 ≥10min（仅已测分钟，**已知高估**） | 1,320 | 7.72% |
| O4 | sustained_grid | MAP<65 ≥10min（网格，NaN=中断） | 32 | 0.19% |
| O2 | sustained_grid | MAP<55 ≥5min（网格，允许 1 min 中断） | 60 | 0.35% |
| O1 | sustained_grid | MAP<55 ≥5min（网格，严格） | 16 | 0.09% |
| D2 | exposure_fraction | ≥10 次测量且 MAP<55 占比 ≥30% | 81 | 0.47% |
| O3 | sustained_grid | MAP<55 ≥10min（网格） | 2 | 0.01% |

### 4.2 SpO2 维度（覆盖率 96%，网格法与原口径一致，数字基本可信）

| ID | 定义 | 阳性 (n=17,103) | 患病率 |
|---|---|---|---|
| O5 | SpO2 <90% 持续 ≥2 min | 1,734 | 10.14% |
| O6 | SpO2 <92% 持续 ≥5 min | 681 | 3.98% |

**关键诊断**：S1（= 旧 O4 的算法）产出 1,320，与 v1.0.0 报的 1,320 **完全一致** ——
这反向证明旧引擎等价于"仅在已测量分钟上判 run"，诊断无误。

**主结局建议 = D1**（`config.outcomes.primary_id`，⚠️ 待 protocol 冻结确认）：
与 Salmasi 2017 的绝对阈值 65 mmHg 一致、把 NIBP 点测结构转化为"暴露比例"临床量、
事件数充足（train/test = 2,255/287）。全部 14 个定义的 PID 级标签与事件首现时刻
落盘于 `results/s1_labels.csv`。

## 5. Design (methodological discipline — non-negotiable)

1. **Patient-level split is PRIMARY** (each PID entirely in train or test). Temporal split is a secondary robustness check — see caveat below.
2. **Temporal split (secondary)**: train 2015-11 ~ 2017-12 / test 2018-01 ~ 2018-10 (measured range; note the project design draft's "2015–2017" is inaccurate — 2018 cases exist). Test is only **1,856 PID (10.9%)**; year distribution 2015=97 / 2016=5,932 / 2017=9,218 / 2018=1,856. Report CIs honestly and do not present the temporal result as the primary table.
3. **Primary metric AUPRC** (prevalence 14.9% under D1); must be reported against the prevalence baseline as **AUPRC / prevalence (lift)**. AUC, calibration, DCA secondary. Add **event-level recall** and **precision at fixed alert rate**.
4. **No double dipping**: features truncated at the prediction time point (e.g., first 15 min → next 60 min).
5. Baseline = age + sex + BMI (SIS has no ASA — must be stated as a limitation). **Anaesthetic technique type** (derived from `patient_procedure_events`: Intubation 15,007 / LMA 1,675 / Sedation 2,343 / Spinal 181 / CSE 31 / Epidural 8) is a strong, interpretable predictor and should be added as "clinical baseline v2".
6. TRIPOD-AI reporting; code + MANIFEST in a public named repository; data stay under DUA (not redistributed).

## 5bis. Outcome engine (v1.1.0) — why the definition family looks like this

SIS BP is NIBP point measurement (nMAP non-null 19.89%, 96.2% of non-null segments are isolated single minutes, median 33 measurements per case). Therefore:

- **"sustained ≥N consecutive minutes" is not identifiable** from point measurements — a real 5-minute hypotensive episode would usually be missed because BP simply isn't recorded. The `sustained_grid` family is retained for completeness and as a conservative floor (O1–O4 = 16/60/2/32).
- **`point_burst`** (≥k low measurements within a window) and **`exposure_fraction`** (fraction of measurements below threshold) are the identifiable, clinically interpretable quantities for NIBP data.
- **`sustained_measured`** (judging runs on measured minutes only) is retained *only* as a sensitivity analysis that deliberately overestimates, to quantify how far the old engine inflated the numbers.
- **No pre-operative baseline MAP**: only 145/19,114 PID (0.8%) have any nMAP within 30 min before OR_start → **Salmasi-style "relative drop ≥20% from baseline" is NOT computable in SIS**. This is a structural limitation and must be stated as such in the manuscript.

## 6. Known limitations to state honestly

- **No ASA** in SIS → clinical baseline is weaker than the EPIC manuscript's; cannot claim superiority over age+ASA.
- **No pre-operative baseline BP** (0.8% coverage) → cannot use relative-drop definitions; only absolute thresholds.
- **NIBP point measurement** (19.89% coverage, isolated minutes) → sustained-duration hypotension is not identifiable; event ascertainment is incomplete and biased toward cases with more frequent cuff cycling.
- **No postoperative outcome table in SIS** → no "IOH → postoperative outcome" link; outcomes are intraoperative events only.
- **Temporal test set is small** (1,856 PID) → generalisation estimates unstable; temporal split is secondary only.
- Waveform-level signals (arterial line morphology) not exploited in v1.
- Single centre (UCI).

## 7. Repo layout & commands

```
config/config.yaml      # single source of truth: paths, seeds, thresholds, outcome definitions
protocol/protocol.md    # pre-specified design (must be frozen before modelling)
scripts/s1_cohort.py    # stage 1: cohort construction + outcome derivation (engine v1.1.0, grid method)
scripts/s2_features.py  # stage 2: feature engineering (BMI, procedure grouping, early-window vitals)
scripts/s3_models.py    # stage 3: modelling + patient-level/temporal validation
scripts/s4_report.py    # stage 4: tables, figures, TRIPOD-AI checklist
scripts/run_all.py      # runs s1→s4 in order
scripts/audit/a1–a5.py  # Round 1 审查审计脚本（可独立复现本 README 全部数字）
results/                # all artefacts (traceable)
review/                 # review rounds
```

Key artefacts from stage 1:

| File | Content |
|---|---|
| `results/s1_cohort.json` | Cohort waterfall (self-consistency asserted) + OR-window sanity detail |
| `results/s1_outcomes.json` | 14 outcome definitions: positives / denominator / prevalence |
| `results/s1_labels.csv` | **PID-level labels + `{ID}_first_time` for all 14 definitions** (17,103 × 29) |
| `results/s1_data_quality.json` | nMAP coverage, segment-length distribution, measurement counts |

Run: `python scripts/run_all.py` (uses the managed venv; see `config/config.yaml` for interpreter paths).

## 8. Software

Python 3.13.12 (managed, WorkBuddy sandbox) · pandas 2.3.3 · numpy 2.4.6 · scikit-learn 1.9.0.

## 9. Status

See `STATUS.md`. Current: **s1 rebuilt with engine v1.1.0 (2026-10-19); all v1.0.0 MAP-side prevalence numbers retracted; s2 not started.**

## 10. Literature position

A preprint already exists on MOVER IOH prediction (Preprints.org 202603.1373, 2026-03) claiming XGBoost AUC-ROC 0.973 / accuracy 94.2%. It must be cited in Related Work and used as a methodological contrast — its accuracy/precision figures are the classic misleading metrics for a low-prevalence event, which is exactly why this project commits to AUPRC-vs-baseline, calibration and DCA. Differentiation: this project targets **sparse NIBP point-measurement tabular data** with **patient-level primary split + temporal secondary split + calibrated decision-curve analysis**, not high-frequency waveform real-time alerting.
