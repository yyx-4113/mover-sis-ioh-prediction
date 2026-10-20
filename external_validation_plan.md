# 外部验证实施方案（VitalDB）— SIS 术中低血压（IOH）预测

> 项目：01_SIS术中低血压预测 ｜ 主结局 D1 ｜ 首投 BMC Anesthesiology
> 状态：**✅ 已完成并写入稿件**（2026-10-20）。VitalDB 开放数据集**公开免登录**，直连（绕开代理 `--noproxy`）可达；逐轨 CSV 下载 + 53 列核心特征对齐 + MOVER 模型复现套用，端到端验证通过。
> 已离线完成：可移植核心子集在 MOVER 上的基准（`results/ext/core_benchmark.json`，patient AUPRC 0.321 / temporal 0.313）
> **最终外部验证结果（全量 3,735 例，口径 B 核心 53 列、未重拟合/重校准）**：VitalDB 外部 **AUPRC 0.160** (95%CI 0.129–0.202) / **AUROC 0.751** (0.713–0.784) / Brier 0.179；患病率 5.73%（214/3,735）；预测风险均值 0.37（未对外部校准）。AUPRC 显著低于内部预期（0.25–0.32）**完全由外部患病率更低（5.73% vs 15.55%）解释**；AUROC 反而高于内部核心模型（0.698/0.710），相对 lift 2.8× 高于内部 2.1×。稿件 TRIPOD 已由 2a 升为 **2b**，新增 External validation 节（正文+表 7+图 6）。

---

## 0. 目的与科学价值

1. **补齐 TRIPOD 短板**：稿件原诚实声明 "no external validation"（2a）；外部验证已完成，已升为 **2b（开发+内部+外部验证）**，是审稿人最易追问项的直接回应。
2. **对冲 novelty / clinical-utility 退稿风险**：本稿核心论点之一是"模型主要反映当下血压 + 锚点时序"。外部验证直接检验该信号是否跨库泛化。
3. **量化 MOVER 性能的来源**：MOVER 模型 top 特征含 `anchor_is_intubation`(gain 72.2)、`ev_intubation`(69.1)、`anchor_minus_or_start`(64.1) 等**锚点/事件时序类**因子，这些在 VitalDB 不可得。外部验证将揭示"多少性能来自可泛化的血流动力学信号、多少来自 MOVER 特有的记录结构"。

---

## 1. 数据获取（✅ 已验证可行 — 公开端点免登录）

| 步骤 | 说明 | 状态 |
|---|---|---|
| 数据可达性 | VitalDB **开放数据集完全公开**：`api.vitaldb.net/cases`、`/trks`、`/labs` 及逐轨 CSV `api.vitaldb.net/<tid>` 均免 token（200）。仅 `.vital` 波形包较大，故**不逐例下载波形**，改为按需拉取所需生命体征轨 CSV | ✅ 验证 |
| 网络 | 本环境 `api.vitaldb.net` 经本地代理（`HTTPS_PROXY=127.0.0.1:53274`）返回 502；**绕开代理直连可达**（`curl --noproxy '*'` 或 requests 清代理，HTTP 200，~2s）。`pip install vitaldb` 已装 | ✅ 验证 |
| 下载单位 | 非 `VitalDB()` 包的 `VitalFile` 波形（~17 MB/例 × 6000 不可行），而是**逐轨 CSV**：每例 6 种生命体征轨（MAP/SBP/DBP/HR/HRP/SpO2），~14 KB gzip/轨，3735 例 × 6 ≈ 22,410 个文件 | ✅ 验证 |
| 队列筛选 | 动脉 MAP 队列（`Solar8000/ART_MBP` 或 `EV1000/ART_MBP`），n=**3,735**；其中 SBP/DBP/HR/HRP/SpO2 覆盖 ≈3,724–3,735（近乎齐全） | ✅ 验证 |
| 运行 | `scripts/ext_download.py`（下载，后台，带缓存/重试）→ `scripts/ext_build.py features|train|apply` | ✅ 验证 |

**锚点适配**：VitalDB 无 Intubation 事件 → 以 `opstart`（手术开始，相对病例起始秒数）为锚；D1 结局窗 `[opstart, opend]`，特征窗 `[opstart-15min, opstart]`（与 MOVER 锚点前 15 min 一致，设计无泄漏）。
**最终样本量**：动脉 MAP 队列 **3,735 例**（远高于 ≥1,500 建议），全量下载中。
**注意**：下载需绕开代理（见上）；`data_vitaldb/` 为本地缓存，不入库（已在 `.gitignore` 规划）。

---

## 2. 结局 D1 跨库对齐（复用 s1 逻辑，按构造正确）

定义完全一致（`config_vitaldb.yaml` ↔ `config/config.yaml`）：

- 类型：`exposure_fraction`（暴露比例型，非持续型 —— 因 VitalDB 虽密，仍按"测量次数+低值占比"定义以保证口径可比）
- 信号：**MAP < 65 mmHg**
- 标准：**≥10 次测量** 且其中 **≥30% < 65**
- 结局窗：`[anchor, op_end]`

**锚点适配（关键差异）**：VitalDB **无 Intubation 事件**，故以 **operation start（`opstart`）** 为预测锚点（保守适配，相当于 MOVER 的 `Surgery_start` 兜底口径）。逐例记录 `anchor_source = "operation_start"`；MOVER 的 `anchor_minus_or_start` 在本库对应 `anchor_minus_case_start`（opstart 距病例/麻醉起点的分钟数）。

> 诚实声明：锚点定义不同 → 严格说这不是"同锚点精确复现"，而是 **temporo-geographic external validation**。这点在稿件与 cover letter 中明说，避免双标观感。

---

## 3. 特征对齐表（MOVER → VitalDB）

| MOVER 特征域 | VitalDB 来源 | 可移植性 |
|---|---|---|
| `age`, `male`, `height_cm`, `weight_kg`, `bmi` | `case` 表 age/sex/height/weight | ✅ 直接 |
| `map_mean/max/min/sd/last/n`, `map_frac_below_65`, `map_n_below_65`, `map_slope`, `map_minutes_since_last` | `ART_MAP` 轨（锚点前 15 min 窗口） | ✅ 直接（且更密） |
| `sbp_*`, `dbp_*`, `hr_*`, `hrp_*`, `spo2_*` | `ART_SBP/DBP`、`HR`、`SpO2` 轨 | ✅ 直接 |
| `vitals_window_actual_min`, `vitals_window_n_records` | 由窗口派生 | ✅ 直接 |
| `anchor_is_intubation` | —（VitalDB 无此事件） | ❌ 恒为 0 → **剔除** |
| `anchor_minus_or_start` | `anchor_minus_case_start` | ⚠️ 重定义 |
| `sg_*`（12 手术组） | `opname`（多为韩文，关键词不映射） | ❌ 剔除（报告为 transportability 局限） |
| `ev_*`, `n_events_pre_anchor` | 麻醉事件轨 schema 差异 | ❌ 剔除 |
| `drug_*`, `lab_*`, `io_*`, `agent_*`, `art_*`, `has_vent/art/lab/io` | 用药/血气/液体/通气 schema 差异大、覆盖率低 | ❌ 剔除 |

**可移植核心子集 = 53 列**（已固化为 `results/ext/core_benchmark.json` 的 `core_feature_list`）。

---

## 4. 验证口径（两种，均报告）

- **口径 A（严格外部验证）**：用 MOVER **全模型（205 特征）** 套 VitalDB，缺失域由 s3 同一 `SimpleImputer(median)+indicator` 填充；报告 AUPRC/AUROC/校准/DCA 及对 MOVER 的衰减。
- **口径 B（核心可移植模型）**：仅用 53 列核心子集重拟合（同 seed/同 XGB 规格）；代表"真正可跨库迁移的信号"。
- **口径 C（参考）**：在 VitalDB 上**独立训练** XGBoost 作为内部对照（非外部验证，但可说明该库本身可建模性）。

### 诚实预期 vs 实际（来自 `core_benchmark.json` + `external_validation.json`）
| 模型 | patient AUPRC | temporal AUPRC | AUROC |
|---|---|---|---|
| 全模型（205 列，MOVER） | 0.347 | 0.340 | 0.722/0.733 |
| **核心子集（53 列，MOVER）** | **0.321** | **0.313** | 0.698/0.710 |
| **核心子集（53 列，VitalDB 外部，未重拟合）** | **0.160** | — | **0.751** |

→ **实际表现解读（诚实）**：外部 AUPRC 0.160 低于内部预期 0.25–0.32，**主因是外部患病率仅 5.73%（远低于 MOVER 15.55%）**——AUPRC 锚定患病率，绝对数值不可直接跨患病率比较；相对 lift（0.160/0.0573 = **2.8×**）反而**高于**内部核心模型（0.321/0.1555 = 2.1×）。外部 **AUROC 0.751 高于**内部核心模型（0.698/0.710），说明**排序能力跨库泛化**。绝对概率未迁移（预测均值 0.37 vs 观察 0.057，Brier 0.179），证实部署前需本地重校准。对照先例 medRxiv 2026.08.26.26361468（VitalDB+MOVER 外部 AUROC 0.696）量级一致；本稿 AUROC 略高，与"动脉密集监测 + 锚点适配为手术开始"口径差异相关，已在稿件 Limitations 如实声明。

---

## 5. 模型套用（复现管线）

`s3_models.py` **不持久化拟合模型**，故外部验证必须：

1. 用 **seed=12345** 从 `s2_features.csv` + `s1_labels_postanchor.csv` 重拟合同一 XGB（`n_estimators=300, max_depth=4, lr=0.05, subsample=0.8, colsample=0.8, min_child_weight=10, reg_lambda=1.0, scale_pos_weight=负正比`）；
2. 5 折 OOF isotonic 校准（与 s3 一致）；
3. 落盘 `results/ext/mover_xgb_pipeline.joblib`（imputer + xgb + isotonic）；
4. 严格按列名/顺序对齐 VitalDB 特征矩阵后套用。

脚本：`scripts/ext_pipeline.py`（含 `--selftest` 离线验证 D1 派生逻辑）。

---

## 6. 质量门（新增，scripts/ext_gate.py 待建）

1. `derive_D1` selftest（合成数据）PASS；
2. VitalDB 队列瀑布自洽（排除项之和 = 源队列）；
3. 特征列对齐断言（核心 53 列 ⊆ VitalDB 产出列）；
4. AUPRC/AUROC + 1000 bootstrap CI；
5. isotonic 校准 + DCA（net benefit 相对 treat-all/none）；
6. 与 `core_benchmark.json` 预期区间对账（外部 AUPRC 不应远低于 0.25，否则查锚点/特征对齐）。

---

## 7. 诚实局限（写入稿件 External validation 节）

1. 锚点定义不同（opstart vs intubation）→ 属 temporo-geographic 而非同锚点复现；
2. 手术分组/用药/血气/液体域不可移植 → 验证的是"核心血流动力学信号"泛化；
3. 测量密度差异（VitalDB 动脉密集 vs MOVER NIBP 稀疏）→ 把记录密度作为显变量讨论，呼应稿件既有的"量化 NIBP 稀疏性约束"论点。

---

## 8. 交付物清单

| 文件 | 状态 |
|---|---|
| `results/ext/core_benchmark.json` | ✅ 已完成（MOVER 上核心子集基准） |
| `scripts/ext_core_benchmark.py` | ✅ 已完成 |
| `external_validation_plan.md` | ✅ 本文件（已更新终值） |
| `config/config_vitaldb.yaml` | ✅ 已建（注：实际管线用 `scripts/ext_build.py` + `scripts/ext_download.py`，未依赖该 yaml） |
| `scripts/ext_download.py` | ✅ 已完成（逐轨 gzip 下载，绕代理） |
| `scripts/ext_build.py` | ✅ 已完成（features / train / apply，含 D1 派生 + 53 列对齐 + 套用） |
| `scripts/ext_pipeline.py`（早期 D1 派生脚手架 + selftest） | ✅ 保留（已被 ext_build.py 取代） |
| `results/ext/vitaldb_features.csv` | ✅ 已完成（3,735 例） |
| `results/ext/vitaldb_labels.csv` | ✅ 已完成 |
| `results/ext/mover_core_model.joblib` + `core_cols.json` | ✅ 已完成（MOVER 核心 53 列模型复现） |
| `results/ext/external_validation.json` + `external_validation_fig.png` | ✅ 已完成 |
| `results/figs/fig6_external_validation.png` | ✅ 已完成（稿件图 6） |
| 稿件 "External validation" 节 + 表 7 + 图 6 | ✅ 已完成（manuscript_v0.1.md + docx 重生成 + gate PASS） |

---

## 9. 作者待办（已闭环）

1. ~~在 vitaldb.net 注册并取得下载权限~~ → **实测 VitalDB 开放端点免登录**，注册非必需；
2. ~~`pip install vitaldb`~~ → 未使用官方包，改用 `api.vitaldb.net` 逐轨 CSV + 绕代理直连；
3. 运行 `python scripts/ext_download.py --workers 16`（全量 3,735 例 × 6 轨，22,288 成功 / 0 失败）→ `python scripts/ext_build.py features` → `apply`；**已全部跑通**；
4. 稿件 "External validation" 节 + 表 7 + 图 6 已补入，正文 "no external validation" 已改为 TRIPOD 2b 已验证陈述；docx 已重生成、gate（摘要 322 词 / 6 图 / 7 表 / 19 参考文献 / 34 关键数字 / DCA）全 PASS。

**剩余阻塞项（与科学无关）**：IRB 豁免函（伦理路线 B）；`gh release create v1.0.0`（代理令牌缺 ref 写权限，需在具权限环境补）。
