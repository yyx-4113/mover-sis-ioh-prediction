# Protocol — SIS 术中低血压预测（草案 **v0.3**，未冻结）

> 起草 2026-10-19 · v0.2 = Round 1 审查 P0 修复（结局引擎重写）
> **v0.3 = 2026-10-19 s1 v1.2.0 + s2 v1.0.0 实跑回填**（预测锚点、锚点后标签通道、特征域冻结）
> 冻结前禁止运行 s3 建模脚本 · 冻结后任何改动须记入 `review/protocol_amendments.md`

## §1 研究问题

利用 SIS 队列的术前人口学 + 术中早期生理（预测锚点前 15 min），预测其后是否发生术中低血压（IOH），性能须超越人口学基线，采用患者级 + 时间双重切分（患者级为主，时间级为次要稳健性检验）。

## §2 数据与队列

- 数据源：`data_raw/_sis_emr_x/EMR/*`（SIS EMR 九表）+ `data_raw/sis_vitals.csv`。
- 队列：SIS `patient_information` 全部 19,114 PID。
- 排除（预定义，按序执行并报告瀑布）：
  1. 缺 OR_start 或 OR_end（实算 0 例，仍写规则）；
  2. **OR 窗口不合理：`or_min <= 0` 或 `> max_or_window_minutes(1440)`（实算剔除 8 例，最大 3,156,668 min ≈ 6 年）**；
  3. OR 窗口内 1-min 观测 <60（实算剔除 1,632 例）；
  4. Age <18 岁（实算剔除 371 例）；
  5. **预测锚点越界（v0.3 新增）：锚点不在 (OR_start, OR_end) 开区间内（实算剔除 242 例）**。
- 报告：纳入/排除瀑布、各排除步骤例数，全部写入 `results/s1_cohort.json`；瀑布自洽校验（各项之和 == source_pids）由脚本断言。
- **实跑口径：分析队列 16,861 PID**（19,114 − 0 − 8 − 1,632 − 371 − 242）。稿件只报分析队列口径。

## §3 结局定义（v0.2 重写 —— 因数据结构而改，非任意更改）

### 3.1 为什么必须重写（v0.1 → v0.2 的唯一实质原因）

SIS 的 nMAP 是 **NIBP 循环点测**，不是连续 1-min 流：

- nMAP 全表非空率 **19.89%**（nSBP 19.99% / nDBP 19.95%）—— v0.1 依赖的"100% non-null"前提不成立；
- 643,466 个连续非空段中 **96.2% 是孤立单分钟**，中位段长 1.0 min；
- 每台手术中位 33 次 MAP 测量（p05 = 12，p95 = 90）。

因此 **"MAP <thr 持续 ≥N 连续分钟"在点测数据上不可识别**：一次真实的 5 分钟低血压发作，
大概率因血压根本没被测到而被漏掉。v0.1 的引擎用 `dropna` 删除缺失分钟后，把"5 个连续低值记录"
当成"5 分钟持续低压"，而真实时钟上跨越 20–40 分钟 —— 实测高估 O1 **10.1×**、O2 **3.9×**、
O3 **14.5×**、O4 **41.3×**（`review/Round1_review_2026-10-19.md` §2，`scripts/audit/a2`）。

### 3.2 定义族（14 个全部计算，主指标单列）

**全 OR 窗口口径（描述性，n = 16,861）**：

| ID | 类型 | 定义 | 阳性 | 患病率 |
|---|---|---|---|---|
| **D1** | **exposure_fraction** | **≥10 次测量且 MAP<65 占比 ≥30%** | **2,506** | **14.86%** |
| E1 | any_below | 任一记录 MAP<55 | 4,050 | 24.02% |
| B1 | point_burst | ≥3 次 MAP<65 落在 30 min 内 | 7,555 | 44.81% |
| B2 | point_burst | ≥5 次 MAP<65 落在 60 min 内 | 5,491 | 32.57% |
| E2 | any_below | 任一记录 MAP<65 | 11,444 | 67.87% |
| B3 | point_burst | ≥3 次 MAP<55 落在 30 min 内 | 1,252 | 7.43% |
| S1 | sustained_measured | MAP<65 ≥10min（仅已测分钟，**已知高估**） | 1,308 | 7.76% |
| O4 | sustained_grid | MAP<65 ≥10min（网格，NaN=中断） | 32 | 0.19% |
| O2 | sustained_grid | MAP<55 ≥5min（网格，允许 1 min 中断） | 60 | 0.36% |
| O1 | sustained_grid | MAP<55 ≥5min（网格，严格） | 16 | 0.09% |
| D2 | exposure_fraction | ≥10 次测量且 MAP<55 占比 ≥30% | 77 | 0.46% |
| O3 | sustained_grid | MAP<55 ≥10min（网格） | 2 | 0.01% |
| O5 | sustained_grid | SpO2 <90% 持续 ≥2 min | 1,697 | 10.06% |
| O6 | sustained_grid | SpO2 <92% 持续 ≥5 min | 663 | 3.93% |

**锚点后窗口口径（建模标签，n = 16,861）** —— 见 §3.4：

| ID | 阳性 | 患病率 |
|---|---|---|
| **D1（主结局）** | **2,622** | **15.55%** |
| E1 | 3,770 | 22.36% |
| B1 | 7,240 | 42.94% |
| B2 | 5,192 | 30.79% |
| B3 | 1,159 | 6.87% |
| O5 / O6 | 1,292 / 572 | 7.66% / 3.39% |

**语义约定（v0.2 新增，必须写进稿件方法）**：

1. `sustained_grid`：先按 PID 重建完整 1-min 网格（`date_range(min..max, freq="1min")`），
   已测量分钟填回网格；**NaN（未测量）与阈值比较得 False，即计为中断**。保守口径，宁可漏检不虚报。
2. `point_burst` / `exposure_fraction`：**NIBP 点测数据下真正可识别的口径**，主结局所在族。
3. `sustained_measured`：仅在已测量分钟上判 run，**必然高估**；只作敏感性分析，
   用于量化"点测数据下持续事件不可判定"的程度，不得用于主结果。
4. `any_below`：任一记录分钟低于阈值，用作暴露上限参照。

**主结局 = D1**（≥10 次测量且 MAP<65 占比 ≥30%）。理由：
与 Salmasi 2017 的绝对阈值 65 mmHg 一致；把点测结构转化为"暴露比例"这一可解释临床量；
锚点后口径事件数 2,622（15.55%），EPV 充足；阈值取自文献而非事后挑数。

**主稿只报 IOH（MAP）维度**；SpO2（O5/O6）移入补充材料，避免一篇稿件两个不相关结局引发多重比较质疑。

### 3.3 无法实现的定义（结构性缺口，必须诚实声明）

- **相对基线下降（MAP 较术前基线降 ≥20%）**：SIS 无术前基线。实测 OR_start 前 30 min 内有
  ≥1 次 nMAP 的仅 **145/19,114 PID（0.8%）**；多数 PID 的首条生命体征出现在 OR_start 之后。
  → Salmasi/Hatib 式相对下降定义在本数据集**不可计算**，写入 §9 局限，不得用弱化措辞掩盖。

### 3.4 建模标签必须来自锚点后窗口（v0.3 新增，防目标泄漏）

若用全 OR 窗口标签，则预测窗（锚点前 15 min）内已经发生的低血压会被特征直接揭示
（如 `map_frac_below_65`），模型学到的是"复述已知"而非"预测未知"，性能虚高。

因此：

- 标签窗口 = **[anchor_time, OR_end]**；产物 `results/s1_labels_postanchor.csv`。
- 全窗口标签（`results/s1_labels.csv`）仅作队列描述（README §4 / §3.2 上表）。
- 事件首现时刻同样按锚点后窗口计算（`{ID}_first_time`），供 s3 做 prevalence 敏感性分析。

## §4 预测因子（全部可术前或预测窗前获得）

| 域 | 变量 | 来源 |
|---|---|---|
| 人口学 | Age, Sex, **BMI（由 Ht/Wt 实算）** | patient_information |
| **麻醉技术类型** | **18 类 procedure_events 的锚点前指示变量**（Intubation / LMA / Sedation / Spinal / CSE / Epidural / Mayfield / CPBP / Aortic CC / MD Handoff / TQ Up 等）+ `n_events_pre_anchor` | patient_procedure_events（仅 `Event_time <= anchor_time`） |
| 手术 | Procedure 文本 → **13 组关键词分组（v0.3 已冻结）** | patient_information + `config.features.procedure_group_keywords` |
| 早期生理 | 锚点前 15 min 的 MAP/HR/SBP/DBP/SpO2 的 mean/min/max/SD/last/n、MAP 低于 65/55 的占比与次数、MAP 斜率、距上次 MAP 测量的时长、窗口实际覆盖分钟数 | patient_vitals |
| **有创监测（v0.3 新增）** | 锚点前 15 min 的 MAP_ART/SBP_ART/DBP_ART 统计量 + `has_art_line`（约 20% 病例有 1-min 有创 MAP，中位 238 次/例）+ Temp + CVPm | patient_observations |
| 早期通气 | 锚点前 15 min PEEP/FiO2/ETCO2/TV/RR/PIP 均值 + `has_vent_record` | patient_ventilator（约 29% 病例有记录） |
| **吸入麻醉药（v0.2 新增）** | 挥发性麻醉药种类指示（sevo/des/iso/N₂O）+ Fi 浓度 | patient_ventilator |
| **液体与出血（v0.2 新增）** | 晶体/胶体/血制品输入量、尿量、EBL、其他输出 | patient_input_output（仅 `IO_datetime <= anchor_time`） |
| **血气（v0.2 新增）** | 锚点前最后一次 Na/K/Ca/Glu/Ph/PCO2/PO2/BE/HCO3/**HgB** + `has_lab` | patient_labs（约 18% 病例有记录） |
| 早期用药 | 16 类药物的锚点前给药次数与累计量：**phenylephrine(mcg)/ephedrine(mg)/norepi/epi/vasopressin/dopamine**（血管活性）、fentanyl(mcg)/sufentanil/hydromorphone（阿片）、propofol(mg)/midazolam/dexmedetomidine/ketamine（镇静）、NMB、neostigmine；派生 `vasoactive_n_doses`、`minutes_to_first_vasoactive` | patient_medication（仅 `Start_time <= anchor_time`） |

**手术分组（v0.3 冻结）**：Procedure 为自由文本（19,098/19,114 非空，17,120 种写法，
16,446 种仅出现 1 次），逐条手工映射不可行 → **关键词分组 + 受控模糊兜底**：

- 13 组：NO_SURGERY / CARDIAC / NEURO（含脊柱）/ THORACIC / VASCULAR / GI / UROLOGY / GYN / ORTHO / ENT / OPHTHO / PLASTIC / OTHER；
- 匹配规则：文本小写、非字母数字转空格，按 config 顺序"首个命中"生效；未命中者走模糊兜底
  （编辑距离 ≤1、首字符相同、词长 ≥7），命中日志逐例落盘 `results/s2_fuzzy_match_log.csv`；
- **实测 OTHER 仅 2.48%（474/19,114）**，模糊兜底命中 60 例；
- 冻结位置：`config/config.yaml → features.procedure_group_keywords`；实现：`_common.assign_procedure_group`（a6 与 s2 共用）。

**预测锚点（v0.3 冻结）**：SIS `patient_procedure_events` **无 Induction 事件**；
实测 Intubation 中位位于 **OR_start+13 min**、比 Surgery_start 早 **30 min**
（p05/p50/p95 相对 Surgery_start = −78/−30/−7 min），99.07% 落在 OR 窗口内
→ 是"诱导结束"的天然锚点。

1. **Intubation 事件时刻**（分析队列内 13,834 PID，82.1%）；
2. **Surgery_start 兜底**（3,027 PID，17.9%；须报告代理比例，并以 `anchor_is_intubation` 作特征）；
3. 锚点越界者剔除（242 例，见 §2 排除 5）。

**禁止**：任何预测窗之后的信息（后续生命体征、后续用药、血气、液体、出血量、
OR_end/Surgery_end 及其派生量如 `or_min`、`post_window_minutes`）。s2 落盘前有
`BANNED` 列守卫 + 每域泄漏审计（`s2_data_quality.json → leakage_audit`，
`max_used_time_minus_anchor <= 0` 断言）。

**基线模型 v1** = Age + Sex + BMI（SIS 无 ASA，须在摘要与局限明示）。
**基线模型 v2** = Age + Sex + BMI + 麻醉技术类型（作为"临床基线"报告）。

## §5 验证设计

1. **患者级切分（主分析）**：同一 PID 全部观测归同一侧（SIS 为 PID 级单记录，天然满足，仍写规则）。
   主指标 AUPRC 的患者级估计以此为准。
2. **时间切分（次要稳健性检验）**：train = 2015-11-01 ~ 2017-12-31；test = 2018-01-01 ~ 2018-10-03。
   实测 test 仅 **1,856 PID（10.9%）**；年份分布 2015 = 97 / 2016 = 5,932 / 2017 = 9,218 / 2018 = 1,856。
   **不得**把时间切分结果作为稿件主结果表（功效不足会被直接质疑）；须诚实报告 CI 宽度。
3. 开发集内 5 折患者级 StratifiedGroupKFold，仅用于超参/校准拟合。

## §6 模型

- Logistic（L2）、XGBoost、LightGBM；同一插补设计矩阵 + 缺失指示变量。
- 类别不平衡：balanced class weights（不重采样，保持记录患病率）。
- 校准：out-of-fold isotonic（防泄漏）。

## §7 指标

- **主指标：AUPRC**（D1 锚点后患病率 15.55%），**必须与 prevalence 基线对比，报告 AUPRC / prevalence（lift）** ——
  文献已明确 AUROC 在不平衡数据上系统性高估性能。
- 次要：AUROC（与基线配对 DeLong）、Brier、校准曲线/斜率、DCA 净获益。
- **event-level recall**（事件级而非段级）与 **precision at fixed alert rate**。
- 区间：1000 次患者级 clustered bootstrap 95% CI（SIS 为 PID 级单记录，预期无聚集，仍按患者级报告以保持纪律一致）。
- 子组：性别、年龄带、BMI 带、手术分组、麻醉技术类型、`anchor_is_intubation`。

## §8 报告与合规

- TRIPOD-AI 清单（沿用 `modeling/results/TRIPOD_AI_checklist.md` 结构，逐项适配）。
- 每个报告数字可追溯到 `results/` 产物文件（审计追踪表）。
- DUA：数据不公开分发；公开代码 + protocol + MANIFEST；仓库实名（yyx-4113）+ 版本 tag。
- 作者身份：单作者，不带 MD/PhD 头衔（本科学历）。
- **Related Work 必须引用** MOVER IOH 预测 preprint（Preprints.org 202603.1373, 2026-03），
  并作为方法学对照点：其报告的 accuracy 94.2% / precision 93.8% 在低患病率 IOH 任务上是
  典型误导性指标，本项目以 AUPRC-vs-baseline + 校准 + DCA 相对照。

## §9 已知局限（须写入稿件）

1. 单中心（UCI）。
2. SIS 无 ASA → 基线弱于 EPIC 稿件。
3. **SIS 无术前基线血压（OR_start 前 30 min 内有 MAP 的仅 0.8%）→ 无法实现"相对基线下降"定义**，
   只能用绝对阈值。
4. **nMAP 为 NIBP 点测（非空率 19.89%，96.2% 非空段为孤立单分钟）→ "持续 N 分钟"型低血压不可识别**，
   事件检出不完整，且偏向血压测量更频繁的病例。
5. SIS 无术后结局表 → 不能建立 IOH 与术后并发症的关联。
6. 2018 年样本量小（时间测试集 1,856 例），泛化估计不稳；时间切分仅作次要稳健性检验。
7. 未利用波形级信号（动脉压形态）。
8. **锚点异质性（v0.3 新增）**：17.9% 病例以 Surgery_start 代理 Intubation，其预测窗覆盖的
   生理阶段不同（GA 病例窗口=诱导期；非插管病例窗口=椎管内/镇静起效后、切皮前）；
   以 `anchor_is_intubation` 作特征并做分层分析，但残余混杂无法完全排除。
9. **通气/血气/有创监测覆盖不全（v0.3 新增）**：ventilator 29%、labs 18%、ART 20%，
   这些域的缺失非随机（与病例复杂度相关），以缺失指示变量缓解但残余混杂存在。

## §10 冻结检查单

- [x] §2 排除例数已实算回填（0 / 8 / 1,632 / 371 / **242** / 16,861）
- [x] §3 结局定义族已实算回填（v0.2 定义族 + v0.3 锚点后口径）
- [ ] **主结局 D1 最终确认（⚠️ 待作者签字）**
- [x] §4 手术分组规则已冻结（config.features.procedure_group_keywords，OTHER 2.48%）
- [x] §4 预测锚点已冻结（Intubation 13,834 / Surgery_start 3,027）
- [x] §5 时间边界已按数据实际范围校准
- [ ] §7 指标（含 lift / event-level recall）最终确认
- [ ] §9 局限清单逐条确认写入稿件
- [ ] 作者签字（日期）
