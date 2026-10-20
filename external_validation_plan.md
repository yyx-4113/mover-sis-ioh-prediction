# 外部验证实施方案（VitalDB）— SIS 术中低血压（IOH）预测

> 项目：01_SIS术中低血压预测 ｜ 主结局 D1 ｜ 首投 BMC Anesthesiology
> 状态：方案已定，数据获取与运行**待作者在「已注册 VitalDB 账户 + 可联网」环境执行**（本会话因 `api.vitaldb.net` 经代理 502 且无账户，无法下载）
> 已离线完成：可移植核心子集在 MOVER 上的基准（`results/ext/core_benchmark.json`）

---

## 0. 目的与科学价值

1. **补齐 TRIPOD 2a 短板**：稿件目前诚实声明 "no external validation"；外部验证是审稿人最易追问的项。
2. **对冲 novelty / clinical-utility 退稿风险**：本稿核心论点之一是"模型主要反映当下血压 + 锚点时序"。外部验证直接检验该信号是否跨库泛化。
3. **量化 MOVER 性能的来源**：MOVER 模型 top 特征含 `anchor_is_intubation`(gain 72.2)、`ev_intubation`(69.1)、`anchor_minus_or_start`(64.1) 等**锚点/事件时序类**因子，这些在 VitalDB 不可得。外部验证将揭示"多少性能来自可泛化的血流动力学信号、多少来自 MOVER 特有的记录结构"。

---

## 1. 数据获取（硬门槛 — 本会话不可行）

| 步骤 | 说明 | 本会话状态 |
|---|---|---|
| 注册 VitalDB 账户 | vitaldb.net → 提交申请，通常需人工审批（数日） | ⛔ 需作者操作 |
| 安装包 | `pip install vitaldb`（PyPI 可达；本会话代理太慢超时） | ⚠️ 待稳定网络 |
| 下载病例 | `VitalFile(caseid)` 逐例拉取高频波形（动脉麻醉病例，~50–200 MB/例） | ⛔ 需账户+网络 |
| 筛选 | 取≥18岁、有动脉 MAP 轨、手术时长 60–1440 min、锚点前 15 min 有 MAP 的病例 | — |

**预期样本量**：与 MOVER 建模层（16,861）量级相当即可，建议 ≥1,500 例（与 MOVER 测试集 3,373/1,818 可比）。
**网络注意**：VitalDB 数据走 `api.vitaldb.net`；本环境该端点经代理返回 502，**必须在可联网环境运行 `scripts/ext_pipeline.py`**。

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

### 诚实预期（来自 `core_benchmark.json`，MOVER 上已测）
| 模型 | patient AUPRC | temporal AUPRC | AUROC |
|---|---|---|---|
| 全模型（205 列，MOVER） | 0.347 | 0.340 | 0.722/0.733 |
| **核心子集（53 列，MOVER）** | **0.321** | **0.313** | 0.698/0.710 |

→ VitalDB 因再失 `anchor_is_intubation` 等 MOVER 特有时序信号，**外部 AUPRC 预期 ~0.25–0.32、AUROC ~0.69–0.72**。对照先例 medRxiv 2026.08.26.26361468（VitalDB+MOVER 外部 AUROC 0.696）量级一致，可信。即便落在 0.25 附近，相对 15.5% 患病率仍约 1.6–2.1× lift，**与外部验证前结论自洽、不夸大**。

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
| `external_validation_plan.md` | ✅ 本文件 |
| `config/config_vitaldb.yaml` | ✅ 已建 |
| `scripts/ext_pipeline.py`（D1 派生 + VitalDB 加载 + 特征对齐 + 模型套用 + selftest） | ✅ 脚手架（数据获取步待账户+网络） |
| `results/ext/vitaldb_labels_postanchor.csv` | ⏳ 待数据 |
| `results/ext/vitaldb_features.csv` | ⏳ 待数据 |
| `results/ext/vitaldb_validation.json` | ⏳ 待数据 |
| 稿件 "External validation" 节 + 图 | ⏳ 待数据 |

---

## 9. 作者待办（非科学内容阻塞项）

1. 在 vitaldb.net 注册并取得下载权限；
2. 在可联网环境 `pip install vitaldb`；
3. 运行 `python scripts/ext_pipeline.py --stage all`（或分步 outcome → features → validate）；
4. 取得结果后，把稿件 "External validation" 节与图补入，并将正文 "no external validation" 改为已验证陈述。
