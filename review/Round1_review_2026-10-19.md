# Round 1 审查报告 — 01 SIS 术中低血压预测

> 审查日期：2026-10-19 · 审查人：杨永新（Yongxin Yang）
> 审查范围：README / protocol / config / scripts(s1–s4) / results(s1 产物) **+ 源数据实测验证**
> 纪律声明：本次不只审包装与格式。所有结论均以 `scripts/audit/a1–a5.py` 在源数据上实算为准，
> 不采信 README/protocol 中的自述数字（凡自述与实算冲突者，一律标记）。

---

## 0. 结论（先结论）

**项目骨架工程质量高（config 中心化、协议预注册、口径纪律明确），但 s1 结局派生存在一个 P0 级算法错误，
导致 README §4 / protocol §3 / STATUS.md 中的六个患病率数字中，MAP 侧四个全部系统性错误（高估 3.9×–41×）。
在此 bug 修复之前，不得进入 s2 特征工程，更不得冻结 protocol。**

次要但同样影响可发表性的问题：主结局定义偏离文献主流、无术前基线导致无法做"相对下降"定义、
时间切分测试集仅 1,856 例、诱导锚点未定义、以及一个已存在的 MOVER IOH 预测 preprint 造成的新颖性风险。

---

## 1. 审查方法与可复现性

| 审计脚本 | 作用 | 关键输出 |
|---|---|---|
| `scripts/audit/a1_vitals_timeline.py` | 源数据列非空率、时间轴连续性、OR 窗口合理性 | 各列非空率、段长分布 |
| `scripts/audit/a2_outcome_definition_bug.py` | 复刻 s1 当前实现 vs 严格网格法，逐定义对比 | **偏差量化表（§2）** |
| `scripts/audit/a3_supported_definitions.py` | 枚举数据真正能支撑的定义族 | 新定义患病率表（§3） |
| `scripts/audit/a4_baseline_anchor.py` | 术前基线 MAP 可得性、OR_start→Surgery_start 差距、麻醉类型 | §5 / §6 依据 |
| `scripts/audit/a5_temporal_split_events.py` | 年份分布与 train/test 事件数 | §4 依据 |

运行环境：`C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python.exe`
（pandas 2.3.3 / numpy 2.4.6 / scikit-learn 1.9.0）。
每个脚本均可独立重跑，输出即上文表格数字。

---

## 2. P0-1（致命）：nMAP 是孤立点测，"连续分钟"逻辑与数据结构根本冲突

### 2.1 根因

`scripts/s1_cohort.py::pid_level_hypotension()` 的做法是：

```python
gdf = df.dropna(subset=[signal]).sort_values(["PID", "Obs_time"])
```

`patient_vitals.csv` 的缺失值是 MySQL 风格 `\N`。实测各列非空率：

| 列 | 非空率 |
|---|---|
| HRe | 94.79% |
| HRp | 95.90% |
| **nSBP** | **19.99%** |
| **nMAP** | **19.89%** |
| **nDBP** | **19.95%** |
| SP02 | 96.08% |

**README §3 声称 "1-min HR/SBP/MAP/DBP/SpO2, 100% non-null" 对 SBP/MAP/DBP 三列是错的。**

更关键的是连续非空 nMAP 段的结构（`a1` 实测）：

- 681,266 个连续非空段中，**长度 = 1 分钟的占 654,909 段（96.1%）**
- 中位段长 1.0 分钟，mean 1.05 分钟
- 每 PID nMAP 覆盖率：mean 22.6%、p50 22.2%、p95 35.1%

**即：数据集里几乎不存在"连续 5 分钟都有 MAP 记录"的序列。** nMAP 是 NIBP 循环点测
（每 PID 中位 33 次测量，平均每 4–5 分钟一个孤立分钟），不是连续 1-min 流。

`dropna` 把这 80% 的 NaN 分钟从序列里物理删除后，时间轴被压缩约 5 倍。于是
"5 个连续低值记录"在压缩数组里成立，在真实时钟上却跨越约 20–40 分钟。
**这不是精度问题，是语义问题：当前实现度量的是一个 protocol 没有定义的量。**

### 2.2 后果量化（分析队列 n=17,103）

| ID | 定义 | 当前 s1 实现 | 严格 1-min 网格法 | 偏差 |
|---|---|---|---|---|
| O1 | MAP<55 ≥5min (gap 0) | 161 (0.94%) | 16 (0.09%) | **高估 10.1×** |
| O2 | MAP<55 ≥5min (gap 1) | 234 (1.37%) | 60 (0.35%) | **高估 3.9×** |
| O3 | MAP<55 ≥10min | 29 (0.17%) | 2 (0.01%) | **高估 14.5×** |
| O4 | MAP<65 ≥10min | 1,320 (7.72%) | 32 (0.19%) | **高估 41.3×** |
| O5 | SpO2<90 ≥2min | 1,803 (10.54%) | 1,734 (10.14%) | +4.0%（可接受） |
| O6 | SpO2<92 ≥5min | 733 (4.29%) | 681 (3.98%) | +7.6%（可接受） |

> 注：当前 s1 报告的 161/234/29/1320 与我这里的"当前实现"复刻值一致（n=17,107 vs 17,103 的口径差见 P1-4），
> 证明 bug 已如实传导到 README §4、protocol §3、STATUS.md 三处。

**SpO2 侧因覆盖率 96%，偏差 <8%，数字基本可信** —— 这是唯一可以保留原有口径的维度。

### 2.3 反向验证：真实低血压暴露远高于当前数字

| 定义（数据可算） | 阳性 | 患病率 |
|---|---|---|
| 任一记录 MAP<55 | 4,105 | 24.00% |
| 任一记录 MAP<65 | 11,568 | 67.64% |
| 任一记录 MAP<70 | 14,251 | 83.32% |

24.0% 的 MAP<55 暴露率与文献报道的术中低血压发生率（常见 20–40%）高度吻合。
**当前 O2 = 1.4% 不是"事件稀疏"，而是漏检。**

### 2.4 处置

`pid_level_hypotension` 必须重写为"先重建 1-min 网格、再判 run"的两步实现，且需在 protocol 中
显式声明 NaN 分钟的语义（建议：NaN = 未测量，计为中断，同时报告"仅用已测量分钟"的敏感性版本）。
在修复并重跑 s1 之前，README §4 / protocol §3 / STATUS.md 的 MAP 侧数字应标记为"已知作废"。

---

## 3. P0-2：主结局 O2 事件数 234 严重低估，主指标 AUPRC 将不可用

连带后果（`a5` 实测）：

- 年份分布：2015 = 97 (0.6%)、2016 = 5,932 (34.7%)、2017 = 9,218 (53.9%)、**2018 = 1,856 (10.9%)**
- 时间切分后 train = 15,224 / **test = 1,856**
- 按当前 O2 口径（234 事件，患病率 1.37%），test 集事件数 ≈ 234 × 10.9% ≈ **25 例**
- 25 个事件做时间外验证的 AUPRC，置信区间会宽到没有任何判别力

**这不是靠"扩大 bootstrap 次数"能救的，是事件数本身不够。** 必须换用 §4 的高患病率定义。

---

## 4. P1-1：结局定义偏离文献主流，且无法做"相对基线下降"

### 4.1 偏离主流

文献标准（已联网核实，见 §8 引用）：

- **Walsh 2013, Anesthesiology**：MAP 与术后损伤关系的经验性定义
- **Salmasi 2017, Anesthesiology**：绝对阈值 **MAP <65 mmHg** 与相对基线下降 ≥20% 均与 MINS/AKI 相关；
  MAP–损伤曲线的转折点在 **65 mmHg**
- **POQI-3**：建议 MAP 60–70 mmHg 或 SBP <100 mmHg
- **BMC Anesthesiology 2022 系统综述**：最常报告的定义为 SBP<90、**MAP<60**、或较基线下降 20%

本项目主结局 **MAP <55** 是"重症级"阈值，比主流更严，且未给文献对照。
审稿人第一问必然是"为什么用 55 而不是 65？"。

### 4.2 结构性限制：无术前基线（必须诚实写入局限）

`a4` 实测：

- OR_start 前 30 min 内有 ≥1 次 nMAP 的 PID：**145 / 19,114（0.8%）**
- OR_start 前有 ≥5 min 记录的 PID：188
- 多数 PID 的首条生命体征出现在 OR_start 之后（`pre_min` 中位数 = −1 min，25% 分位 = −3 min）

**结论：SIS 无法实现 Salmasi/Hatib 式的"相对基线下降 ≥20%"定义。** 这是数据资产的结构性缺口，
不是工程量问题。必须在 protocol §9 与稿件 Limitations 中明确写出，不得用弱化措辞掩盖。

### 4.3 建议的新主结局（数据可算 + 文献可辩护）

| 候选定义 | 阳性 | 患病率 | train/test 事件 | 文献可辩护性 |
|---|---|---|---|---|
| **A. MAP<65，术中低值占比 ≥30%（≥10 次测量）** | **2,544** | **14.87%** | 2,255 / 287 | Salmasi 绝对阈值 + "持续暴露"量化 |
| B. ≥3 次 MAP<65 落在 30 min 内 | 7,634 | 44.64% | 6,791 / 832 | "反复低血压发作"口径 |
| C. ≥5 次 MAP<65 落在 60 min 内 | 5,554 | 32.47% | — | 同上，更严 |
| D. 任一记录 MAP<55 | 4,105 | 24.00% | 3,645 / 457 | 重症级暴露，事件充足 |
| E. ≥5 次 MAP<55 落在 60 min 内 | 534 | 3.12% | — | 严格持续，事件偏少 |

**推荐 A 为主结局**：与 Salmasi 绝对阈值一致、把"点测"数据结构转化为"暴露比例"临床量、
事件数 2,544（EPV 充足）、test 集仍有 287 事件（CI 可用）。D 作为敏感性/重症维度。
O5/O6（SpO2）保留为平行低氧维度，数字可信。

### 4.4 同时必须报告的指标纪律

- 主指标 AUPRC **必须与 prevalence 基线对比**，并报告 **AUPRC / prevalence（lift）**
  —— 文献已明确 AUROC 在不平衡数据上系统性高估性能
- 增加 **event-level recall**（事件级而非段级）与 **precision at fixed alert rate**
- DCA 净获益 + 校准曲线/斜率（已列入 protocol §7，保留）

---

## 5. P1-2：诱导锚点未定义，"前 15 min"目前不可实现

protocol §4 要求"诱导后前 15 min"，但 `s2_features.py` 的 TODO 承认"需先定位 induction 时刻"。
`a4` 实测：**SIS `patient_procedure_events` 没有 Induction 事件**（只有 Intubation 15,007 /
Extubation 15,258 / Sedation 2,343 / LMA 1,675 / Spinal 181 / CPBP On 197 / CSE 31 / Epidural 8）。

而 **OR_start → Surgery_start 中位 41 min（IQR 30–56）**。若以 OR_start 代理"诱导"，
"前 15 min"落在患者入室、摆体位、动静脉穿刺阶段，**不是麻醉诱导后**，特征语义完全错位。

**建议锚点优先级**：
1. **Intubation 事件时刻**（15,007 PID，78.5% 覆盖）—— 最接近"诱导完成"的可观测点
2. Surgery_start（缺失时代理，报告代理比例）
3. 首次 ETCO2 / TV 记录（`patient_ventilator`，反映机械通气开始）

---

## 6. P1-3：时间切分主次不清 + 测试集过小

README §5 把"患者级切分"与"时间切分"并列，未定主次。实测 test 仅 1,856 例（10.9%）。

**建议明确**：
- **主分析 = 患者级切分**（全 17,103，事件 2,544），保证 AUPRC 估计精度
- **次要 = 时间前向验证**（train 2015-11~2017-12 / test 2018-01~2018-10），诚实报告 CI 宽度，
  并明确其为"稳健性检验"而非"外部验证"
- 禁止把时间切分结果作为稿件的主结果表（会被质疑功效不足）

---

## 7. P1-4：阳性 PID 列表未落盘，s2/s3 无法拿到标签

`s1_outcomes.json` 中 `positive_pid_list_path: None`，注释说"由 s1b 负责"，但 **s1b 不存在**。
当前 s2/s3 没有任何途径取得结局标签 —— 这是骨架的硬阻塞。

**必须**：s1 直接落盘 `results/s1_labels.csv`（PID + 六定义 0/1 + 预测时点 + 事件首现时间），
并写入 MANIFEST。标签来源不可复现 = 审计链断裂。

---

## 8. P1-5：其他数据质量与工程问题

| # | 问题 | 实测/证据 | 建议 |
|---|---|---|---|
| P1-5a | OR 窗口无合理性校验 | or_min ≤0 或 >1440 的 **8/19,114**（max 3,156,668 min ≈ 6 年；Surgery_start−OR_start max 3,156,515 min） | 加 sanity check（0 < or_min ≤ 1440），剔除数入瀑布 |
| P1-5b | `excl_missing_or_window` 恒报 0 | 格式 `%m/%d/%y %H:%M` 的解析失败率从未验证 | 报告 `NaT` 数而非硬编码 0 |
| P1-5c | 口径不一致 | s1 报 17,107；加 OR 合理性过滤后为 **17,103** | 统一，差异 4 例即 P1-5a 的 ≤0 组 |
| P1-5d | `\N` 处理靠运气 | `read_csv` 未设 `na_values=["\\N"]`，靠 `to_numeric(coerce)` 兜底 | 显式 `na_values`，并加断言（非空率需落在预期区间，防静默全 NaN） |
| P1-5e | config 引用不存在的键 | `s2_features.py` 注释引用 `config: modeling.procedure_groups`，**config.yaml 中无此键** | 补键或删注释 |
| P1-5f | `or_window_observations` 语义含糊 | 3,561,196 是过滤到分析队列**之前**的口径 | 改名 `source_or_window_observations` 并加分析队列口径 |
| P1-5g | 无 EPV / 样本量论证 | protocol 无功效计算 | 按 Riley 或至少 EPV 计算，写入 §5 |
| P1-5h | 无 MANIFEST / 无 git tag / 无缓存 | s1 每次重读 200MB CSV | 加 MANIFEST 校验和 + parquet 缓存 + v1.0.0 tag |

---

## 9. P2-1：未开发的强预测因子（提高模型质量与可解释性的最大空间）

| 资产 | 规模/可得性 | 价值 |
|---|---|---|
| **麻醉技术类型** | Intubation 15,007 / LMA 1,675 / Sedation 2,343 / **Spinal 181 / CSE 31 / Epidural 8** / CPBP 197 / Mayfield 165 | **最强预测因子之一**。椎管内/区域麻醉→交感阻滞→低血压风险显著升高；且可解释、临床可信 |
| 吸入麻醉药 Fi/Et 浓度 | `patient_ventilator` 76MB | 直接血管扩张机制，浓度-效应关系 |
| 术中血气 12 项 | `patient_labs` 1.4MB | Na/K/Ca/Glu/HCO3/BE/Ph/PCO2/PO2/HgB |
| 液体入量 / 出血量 | `patient_input_output` 6MB | 低血容量直接机制 |
| 血管活性药给药 | `patient_medication` 20MB | 注意：**诱导后给药是泄漏**，须严格限定在预测窗前 |
| 特殊体位/操作 | Mayfield 165 / Aortic CC 99 / CPBP 197 | 强临床信号，事件少但可作指示变量 |

**建议 v1 至少纳入：麻醉技术类型 + 吸入麻醉药浓度 + 出血量/液体 + 血气关键项。**
当前 protocol §4 只列了人口学/手术/早期生理，把这些资产全部闲置，等于主动放弃模型上限。

---

## 10. P2-2：新颖性风险 —— 已存在 MOVER IOH 预测 preprint

已联网检索到：

> **"Predicting Intraoperative Hypotension Using Machine Learning: A Comprehensive Analysis of the MOVER Dataset"**
> Preprints.org 202603.1373（2026-03）· 声称 MOVER 上 XGBoost 5-min 预测 AUC-ROC 0.973、
> 10-min 0.942、15-min 0.908，accuracy 94.2%。

**必须正面处理**，三条路：

1. **在 Related Work 中明确引用并区分**：该 preprint 未同行评审、声称"first comprehensive comparison"，
   且其 "accuracy 94.2% / precision 93.8%" 在低患病率 IOH 任务上是典型的误导性指标
   （把多数类预测为阴性即可获得高 accuracy）—— 这正是本项目坚持 AUPRC + 校准 + DCA 的立论依据，
   可作为方法学对照点写进 Discussion。
2. **差异化定位**：该 preprint 面向高频/波形数据与"实时预警"；本项目面向**稀疏 NIBP 点测表格数据**
   的"术前+诱导早期一次性预测"，并坚持患者级 + 时间双重切分、校准、DCA。两者场景不同，可辩护。
3. **不得回避**：不引用会被审稿人直接点出。

另需注意：MOVER 官方论文（Samad et al., JAMIA Open 2023）明确 SIS 数据来自 2015–2017 EHR，
但实测数据含 2018 年（1,856 例）。README §5 已正确指出设计稿"2015–2017"不准确 —— 保持这个更正。

---

## 11. P2-3：两个结局维度混一篇

protocol §3 把 IOH（O1–O4）与低氧（O5–O6）作为"平行分析"。
一篇稿件同时报告两个不相关结局会引发多重比较与结局不清的质疑。

**建议**：主稿只做 **IOH（MAP）**；SpO2 维度移入补充材料，或明确声明为预设次要结局并做 multiplicity 说明。

---

## 12. 修订后的设计建议（汇总）

| 项 | 现状 | 建议 |
|---|---|---|
| 结局引擎 | `dropna` 压缩时间轴 | 重建 1-min 网格；NaN = 中断；加"仅已测分钟"敏感性版 |
| 主结局 | O2（MAP<55 ≥5min，234 例，已作废） | **A. MAP<65 占比 ≥30%（≥10 次测量），2,544 例** |
| 敏感性结局 | O1/O3/O4（数字已作废） | D（任一 MAP<55，4,105）+ B（≥3 低值<65/30min，7,634）+ 低氧 O5/O6 |
| 相对基线下降 | 未定义 | 明确声明"因 0.8% 覆盖率不可算"，写入局限 |
| 预测锚点 | 未定义（OR_start 代理错 41 min） | **Intubation 事件**为主锚，Surgery_start 为备 |
| 验证主次 | 患者级/时间级并列 | **主 = 患者级；次 = 时间前向**（test 1,856 例，诚实报 CI） |
| 基线模型 | age+sex+BMI | 保持，但明示无 ASA；**加麻醉技术类型**后作为"临床基线 v2" |
| 特征域 | 人口学/手术/早期生理 | + 麻醉技术类型 + 吸入麻醉药 + 出血/液体 + 血气 |
| 标签落盘 | 无 | `results/s1_labels.csv` + MANIFEST |
| 文献 | 未引用 MOVER IOH preprint | 必引并作方法学对照（§10） |
| 指标 | AUPRC 主 | + AUPRC/prevalence lift + event-level recall + precision@alert rate |

---

## 13. 行动清单（按优先级）

| # | 动作 | 优先级 | 阻塞 |
|---|---|---|---|
| 1 | 重写 `pid_level_hypotension`（网格法 + NaN 语义声明） | **P0** | 阻塞 s2/s3 |
| 2 | 重跑 s1，替换 README §4 / protocol §3 / STATUS.md 全部 MAP 侧数字 | **P0** | 阻塞 protocol 冻结 |
| 3 | 落盘 `results/s1_labels.csv`（PID 级六定义标签 + 事件首现时间） | **P0** | 阻塞 s2/s3 |
| 4 | 确定主结局（建议 A）+ 在 protocol §3 冻结 | **P0** | 阻塞 s2 特征定义 |
| 5 | 定义预测锚点（Intubation / Surgery_start 代理比例） | P1 | 阻塞 s2 |
| 6 | 补 OR 窗口 sanity check + 口径统一（17,103） | P1 | 阻塞 s1 |
| 7 | 补 `config.modeling.procedure_groups` 键 + 手术分组映射表 | P1 | 阻塞 s2 |
| 8 | 撰写 MOVER IOH preprint 的方法学对照段 | P1 | 阻塞 Discussion |
| 9 | 特征域扩展（麻醉类型/吸入药/血气/液体出血） | P1 | 提高模型上限 |
| 10 | 补 EPV/样本量论证；明确时间切分为次要验证 | P1 | 阻塞 §5 |
| 11 | 加 AUPRC lift / event-level recall / precision@alert rate | P2 | 阻塞 §7 |
| 12 | MANIFEST + parquet 缓存 + git v1.0.0 tag | P2 | 阻塞投稿包 |
| 13 | IOH 与 SpO2 分稿或降为补充材料 | P2 | 阻塞 §3 |

---

## 14. 本次审查明确肯定的既有设计

避免只报问题 —— 以下判断经审查确认是正确的，冻结时保留：

1. **AUPRC 作为主指标** —— 与文献对不平衡数据上 AUROC 高估的警示一致，正确。
2. **患者级 + 时间双重切分** —— 方向正确（仅主次需明确）。
3. **特征截停在预测时点前防双重 dipping** —— 正确，且 `patient_medication` 的泄漏风险已在 protocol §4 明示禁止。
4. **balanced class weights 而不重采样** —— 保持记录患病率，正确。
5. **OOF isotonic 校准** —— 防泄漏做法正确。
6. **SIS/EPIC 患者不重叠的划界论证** —— 方向正确（但新颖性论证需补 §10 的文献维度）。
7. **口径纪律**（画像 18,991 vs 分析队列 17,107 双向列示）—— 方法论意识好，问题只在数字本身错了。
8. **不投 PeerJ、不默认首投 Scientific Reports** —— 与既定纪律一致。

---

*本报告所有数字可由 `scripts/audit/a1–a5.py` 独立复现。修改 s1 后须重跑全部审计脚本并更新本报告 §2 表格。*
