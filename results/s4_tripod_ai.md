# TRIPOD+AI (2024) 清单 — 01 SIS 术中低血压预测

> 状态图例：✅ 已满足 / 有产物支撑　⚠️ 部分满足 / 需补写　⏳ 待补（稿件阶段）
> 每项标注"正文段落 / 产物文件"，便于投稿前逐项核对。

| # | TRIPOD+AI 条目 | 状态 | 位置 / 证据 |
|---|---|---|---|
| 1 | **Title**：明确为预测模型研究（含 ML） | ⏳ | 稿件标题待定稿（protocol §1） |
| 2 | **Abstract**：结构化，含数据来源、模型、性能 | ⏳ | 待撰稿 |
| 3 | **Objectives**：明确临床问题与预测目标 | ✅ | protocol §1；锚点后 IOH |
| 4 | **Data sources**：数据来源、时间跨度、检索方式 | ✅ | `s1_cohort.json`；SIS EMR 九表，2015-11~2018-10 |
| 5 | **Eligibility**：纳入排除标准 | ✅ | protocol §2；`s1_cohort.json`（瀑布各项和自洽） |
| 6 | **Outcome**：结局定义与判定方式 | ✅ | protocol §3；14 定义敏感性矩阵 `s1_outcomes_postanchor.json` |
| 7 | **Predictors**：全部候选预测因子及定义、测量时点 | ✅ | `s2_feature_dictionary.json`（206 个特征逐条注域/来源表/窗口） |
| 8 | **Temporal/leakage**：预测因子须早于预测时点 | ✅ **强证据** | `s2_data_quality.json.leakage_audit`：各域 `max_used_time_minus_anchor ≤ 0`，ALL_PASS=True |
| 9 | **Missing data**：缺失处理方式 | ✅ | 树模型原生 NaN；Logistic 中位数插补+缺失指示（`s3_models.py`） |
| 10 | **Statistical / ML methods**：模型族、超参、软件版本 | ✅ | `s3_metrics.json`（seed/超参固定）；config `runtime` 记录版本 |
| 11 | **Sample size / EPV**：样本量与事件数论证 | ✅ | n=16861，事件 2622（EPV 充足）；见 `s1_outcomes_postanchor.json` |
| 12 | **Validation**：内部/外部验证策略 | ✅ | 患者级（主）+ 时间切分（次）；`s3_metrics.json` |
| 13 | **Performance measures**：主指标与不确定性 | ✅ | 主 AUPRC；1000 次 bootstrap 95% CI；`s3_metrics.json` |
| 14 | **Calibration**：校准评估与方法 | ✅ | OOF isotonic；`s3_calib_dca.json`（斜率 0.9092） |
| 15 | **Clinical utility**：决策曲线/净收益 | ✅ | DCA；`s3_calib_dca.json.dca` |
| 16 | **Participants**：描述参与者特征 | ✅ | `s2_data_quality.json`（人口学/BMI/手术分组分布） |
| 17 | **Model specification**：最终模型可获取 | ✅ | 脚本 + 产物完整可复现；建议附代码仓库 |
| 18 | **Subgroups**：亚组性能 | ✅ | `s3_subgroups.json`（性别/年龄/BMI） |
| 19 | **Limitations**：局限性（含偏倚来源） | ✅ | protocol §9；本报告 §8 |
| 20 | **Interpretation**：临床可解释性 | ✅ | `s3_feature_importance.json`（MAP 主导，逻辑自洽） |
| 21 | **Ethics / IRB**：伦理审批与知情同意 | ⚠️ | 回顾性去标识数据；**须由作者确认本单位伦理审批状态** |
| 22 | **Data availability**：数据与代码可获取 | ⚠️ | 产物齐备；**须落实公开仓库/DOI**（禁写 "available on request"） |
| 23 | **Funding / COI** | ⏳ | 待作者补充 |
| 24 | **Registration**：研究是否预注册 | ⚠️ | protocol 已版本化（v0.2-draft）；建议投稿前补注册号 |

## 待办（阻塞投稿的 3 项硬缺口）
1. **伦理/IRB 状态**须由作者书面确认（条目 21）。
2. **数据与代码公开**须落实真实仓库 URL（条目 22），不得写 "available on request"。
3. **三项设计决策待作者签字**：主结局 D1、预测锚点 Intubation、手术分组映射表
   （当前已按 config 在管线中暂固化执行，改动任一需重跑 s2→s3）。
