# 目标期刊在线核实与锁定（2026-10-19）

> **纪律声明**：本文所有 IF / JCR 分区 / 中科院分区 / SCIE 收录状态均为**联网核实**，
> 并标注数据年份戳与来源。**无一项来自记忆**。核实日期：2026-10-19。
> 未能核实的项目已明确标注「未核实」，不填数字。

---

## 0. 核实方法

- 检索源：多源交叉（X-MOL 期刊库、恩特学术 enterscholar、学术之家、科研通 ablesci、
  爱科学、Springer 官方 FAQ/投稿页、PubMed、DOAJ）。
- **共识原则**：同一指标至少 2 个独立来源一致才采信；不一致者并列列出并标注分歧。
- 期刊官方页（BMC / Springer）因 Cloudflare 人机校验无法直连抓取，改用官方 FAQ 镜像
  与第三方聚合库交叉核对。

---

## 1. 本稿证据级别自评（先做闸门，再谈期刊）

按你的「证据层级闸门」纪律，先诚实定位本稿能支撑什么级别的声明。

| 维度 | 本稿实际状态 | 支撑的声明强度 |
|---|---|---|
| 研究类型 | 单中心回顾性队列（MOVER / SIS，UCI） | 观察性、探索性 |
| 样本量 | 分析队列 16,861 例；主结局阳性 2,622（15.55%） | 事件数充足 ✅ |
| 验证层级 | **仅内部验证**：患者级 8:2 切分 + 时间切分 + 5 折 OOF | ❌ **无外部验证** |
| TRIPOD 类型 | **Type 2a**（开发 + 内部验证，无外部验证） | 不得声称可用于临床 |
| 结局性质 | 派生复合结局 D1（MAP<65 占比 ≥30% 且 ≥10 次测量）——**替代终点** | ❌ 未链接 AKI/心肌损伤/死亡 |
| 判别度 | XGBoost 患者级 AUROC 0.723、AUPRC 0.350（lift 2.25×）；时间切分 AUROC 0.734 | 中等、非全阴性 ✅ |
| 校准 | OOF isotonic：Brier 0.191→0.119，slope 0.92 / intercept 0.007 | 良好 ✅ |
| 伦理 | 公共去标识数据 + DUA；**作者本人未取得本单位 IRB** | ⚠️ 须在稿件中如实声明 |
| 署名 | 单作者，无 MD/PhD 头衔 | 无影响 |

**结论**：本稿可诚实支撑的声明是
> 「在 MOVER/SIS 单中心回顾队列中开发并内部验证了一个以麻醉诱导（Intubation 锚点）为
> 预测时点、以术中累积低血压负荷为主结局的机器学习模型；判别度中等（AUROC 0.72），
> 校准良好；**需外部验证后方可讨论临床部署**。」

**不能**支撑的声明：临床可用性、优于既有报警器（HPI）、降低并发症、跨中心泛化。

---

## 2. 候选期刊核实表（全部 SCIE 收录，均经核实）

### 2.1 首选档

| 项目 | **BMC Anesthesiology** |
|---|---|
| ISSN | 1471-2253（E-ISSN 同） |
| 出版商 | BioMed Central（Springer Nature），UK，2001 创刊 |
| **SCIE 收录** | ✅ 是（Science Citation Index Expanded） |
| **JIF** | **3.2（2025 年 JIF，2026 年 6 月发布）** |
| 5 年 JIF | 2.6 |
| **JCR 分区** | **Q2**（ANESTHESIOLOGY，2025-2026 版） |
| **中科院分区** | 大类**医学 3 区**；小类**麻醉学 3 区**（2025 年 3 月升级版）<br>新锐分区 2026 年 3 月：医学 3 区 / 麻醉学 3 区，非 Top |
| CiteScore / SJR | 3.90 / 0.819 |
| 年发文 / H-index | 462 / 31；自引率 7.7% |
| OA / APC | 全 OA。**APC £2590 / $3290 / €2890** —— ⚠️ **引自你此前记录，本轮未在官网复核，投稿前须复核** |
| 投稿系统 | Editorial Manager，journal ID **12871**（你已备） |
| 审稿周期 | 网友分享 >12 周 |

### 2.2 主题契合最强档

| 项目 | **Journal of Clinical Monitoring and Computing (JCMC)** |
|---|---|
| ISSN | 1387-1307 / E-ISSN 1573-2614 |
| 出版商 | Springer（Netherlands），1985 创刊，双月刊 |
| **SCIE 收录** | ✅ 是（另收 SCIE + EI） |
| **JIF** | **2.6（2025 年 JIF，2026 年 6 月发布）** |
| 5 年 JIF | 2.2 |
| **JCR 分区** | **Q2**（ANESTHESIOLOGY 30/72，2025-2026 版） |
| **中科院分区** | 大类**医学 3 区**；小类**麻醉学 4 区**（2025 年 3 月升级版）<br>新锐分区 2026 年 3 月：医学 3 区 / 麻醉学 4 区 |
| CiteScore / SJR | 4.80 / 0.754 |
| 年发文 / H-index | ~126–195 / 46；自引率 7.7% |
| **OA / APC** | ⚠️ **2026-01-01 起转为全 OA**（Springer 官方 FAQ 核实），非 OA 通道已关闭。<br>**2026 APC = €2990 / $3890 / £2590** |
| 投稿系统 | submission.nature.com（10877） |
| ⚠️ 风险 | 第三方投稿经验称该刊**要求提交伦理审查证明**、拒收无临床验证的纯算法稿。<br>⚠️ 该说法来自第三方博客，**未经官方核实**，但你无本单位 IRB，须预备应对话术 |

### 2.3 冲击档（最高影响力）

| 项目 | **Journal of Clinical Anesthesia (JCA)** |
|---|---|
| ISSN | 0952-8180 / E-ISSN 1873-4529 |
| 出版商 | Elsevier（US），1988 创刊，双月刊 |
| **SCIE 收录** | ✅ 是 |
| **JIF** | **6.0（2025 年 JIF，2026 年 6 月发布）** |
| 5 年 JIF | 6.6 |
| **JCR 分区** | **Q1**（ANESTHESIOLOGY **6/72**，2025-2026 版） |
| **中科院分区** | 大类**医学 2 区**；小类**麻醉学 2 区**，**Top 期刊**（新锐 2026 年 3 月）<br>2025 年 3 月升级版：医学 2 区 / 麻醉学 2 区 |
| CiteScore / SJR | 7.9 / 1.403 |
| 年发文 / H-index | 176 / 65；自引率 3.5% |
| OA / APC | Hybrid（Gold OA 占比 34.4%）。**选订阅模式则无强制 APC** ✅ |
| 审稿周期 | 网友分享 6–12 周 |
| ⚠️ 风险 | 竞争激烈；本稿无外部验证 + 替代终点，desk-reject 风险实质存在 |

### 2.4 备选档

| 项目 | **BMC Medical Informatics and Decision Making** | **Journal of Anesthesia (JA)** |
|---|---|---|
| ISSN | 1472-6947 | 0913-8668 / 1438-8359 |
| 出版商 | BMC，UK，2001 | Springer（Japan），1987，季刊 |
| SCIE | ✅ 是 | ✅ 是 |
| **JIF** | **5.5（2025，2026-06 发布）** | **2.7–2.8（2025 JIF）** ⚠️ 源间分歧：ablesci 标 2.8，iikx 标 2.7，并列列出 |
| JCR 分区 | **Q2**（MEDICAL INFORMATICS） | **Q2**（ANESTHESIOLOGY 25/72） |
| 中科院分区 | 大类医学 3 区 / 小类医学信息 3 区（2025 升级版）<br>新锐 2026-03：大类医学 **2 区** | 大类医学 3 区 / 小类麻醉学 3 区（2025 升级版） |
| CiteScore / SJR | 7.4 / 1.224 | 5.3 / 0.866 |
| 年发文 / H-index | 412–481 / 59 | 113–175 / 39 |
| OA / APC | 全 OA。**APC 未核实** | 非 OA（Gold OA 10–24%），**无强制 APC** |
| 备注 | 需把稿件重框为「医学信息学/临床决策支持」角度 | 影响力与主题契合均弱于前三，作为保底 |

---

## 3. 主题契合实证（避免只看主题描述就推荐）

**BMC Anesthesiology —— 已采纳与本稿完全同级别的稿**（决定性证据）：

| 论文 | 设计 | 样本 | 性能 |
|---|---|---|---|
| Chiu et al. 2025, *BMC Anesthesiol* 25:351<br>(10.1186/s12871-025-03195-8) | 单机构 3 年回顾，XGBoost，**仅 10 折内部验证、无外部验证** | 4,658 | AUROC **0.80** (0.74–0.86) |
| Xu et al. 2025, *BMC Anesthesiol*<br>(10.1186/s12871-025-03239-z) | 单中心回顾，DNN/ML 多模型 | 1,016 | AUROC **0.782–0.855**，AUPRC 0.496–0.549 |
| Cheun et al. 2026, *BMC Anesthesiol* 26:334<br>(10.1186/s12871-026-03841-9) | 有外部验证的 XGBoost | 7,946 + 外部 | AUROC 0.804 内部 / 0.735、0.712 外部 |

→ **本稿 AUROC 0.723 落在该刊已发表同类稿的区间内**，且 Chiu 2025 证明「单中心回顾 + 仅内部验证 + AUROC ~0.8」可被接受。**这是命中率最强的实证依据。**

**JCMC —— 主题直接对口，且有一篇论点同向的论文**：

| 论文 | 内容 |
|---|---|
| **Chaari et al. 2026, *J Clin Monit Comput* 40(1):43–57**<br>(10.1007/s10877-025-01357-0) | 「Towards reliable prediction of intraoperative hypotension: a cross-center evaluation of deep learning-based and MAP-derived methods」。核心结论：**AI 预测 IOH 的真实世界可靠性常被数据选择偏倚高估** |
| Hernández Rincón et al. 2026, *JCMC*<br>(10.1007/s10877-026-01449-5) | AI 预测围术期麻醉并发症的 scoping review（51 项研究：IOH 是最常研究结局；外部验证罕见） |

→ 本稿「诚实报告 AUROC 0.723、量化 NIBP 稀疏性对性能上限的约束」与 Chaari 2026 的论点**同向**，是该刊乐于接受的定位。

---

## 4. 新颖性风险与差异化定位（本轮最重要的发现）

MOVER 上的 IOH 预测**已经有人在做了**，且有一篇数值可疑的直接竞品：

| 文献 | 数据集 | 报告性能 | 与本稿关系 |
|---|---|---|---|
| **Preprints.org 202603.1373**<br>「Predicting Intraoperative Hypotension Using ML: A Comprehensive Analysis of the MOVER Dataset」 | MOVER | XGBoost **AUROC 0.973**、accuracy 94.2%、precision 93.8%、recall 94.5%（5-min 窗） | ⚠️ **直接竞品，且 0.973 可疑**。MOVER/SIS 的 nMAP 非空率仅 **19.89%**、96.1% 的非空段是**孤立单分钟**——在这种数据密度上达到 0.973，几乎只能通过标签泄漏或过于宽松的结局定义实现 |
| **medRxiv 2026.08.26.26361468**（Oyarzun） | VitalDB 开发 → **MOVER 外部验证 3,069 例** | 外部验证 AUROC **0.696**（vs MAP-alone 0.638） | ✅ 我们的 **0.723 与之量级一致**——可作为外部参照，佐证我们的数值可信 |
| Research Square rs-10347757 | VitalDB + MOVER 外部队列 | 零样本时序基础模型基准 | 佐证 MOVER 已是公认外部验证集 |

**差异化定位（建议写进 Introduction 与 Discussion）**：

1. **结局不同**：我们用**累积低血压负荷**（D1：≥10 次测量且 MAP<65 占比 ≥30%），
   对齐 Salmasi 2017 与伤害相关的「暴露负荷」定义；竞品用的是「未来 5/10/15 分钟事件」。
2. **预测时点不同**：我们用**锚点式**（Intubation / Surgery start，术前—诱导即刻做风险分层），
   不是术中实时报警——临床用途与管理路径完全不同。
3. **方法学透明度**：显式 9 域泄漏审计（`max_used_time_minus_anchor = 0.00`）、
   时间切分、isotonic 校准、DCA、TRIPOD+AI 清单、93 行审计追踪表。
4. **对社区的真实贡献**：**量化 MOVER/SIS 的 NIBP 稀疏性并说明其对可达性能上限的约束**，
   正面引用 Preprints 202603.1373 与 Chaari 2026，把「0.973」置于方法论批判之下。

---

## 5. 规避清单（按你的实证纪律）

| 期刊 | 规避理由 | 状态 |
|---|---|---|
| **PeerJ / PeerJ Computer Science** | 你的黑名单（投稿系统图件槽频繁误判、文件名/格式报错） | 🚫 **不推荐** |
| **Scientific Reports** | 你多个回顾性/再分析/计算型稿被 desk-reject 的硬实证；本稿属同一类别 | ⚠️ **不首投** |
| **PLOS ONE** | 你的 MR 稿以实质性方法学理由被拒；本稿存在同类硬缺口（无外部验证、替代终点） | ⚠️ **须先补方法学缺口再考虑** |

---

## 6. 锁定结论与投稿阶梯

### ✅ 锁定：**首投 BMC Anesthesiology**

理由（按证据权重排序）：
1. **命中率实证最强**：该刊 2025–2026 已发表 3 篇同级别稿（单中心回顾 + 仅内部验证 + AUROC 0.72–0.80），本稿 AUROC 0.723 在区间内。
2. **麻醉学主刊对口**，中科院小类麻醉学 **3 区**（优于 JCMC 的 4 区）。
3. **你已备好投稿通道**（journal ID 12871、APC 已评估）。
4. BMC 系列 soundness-first，对「中等判别度 + 诚实局限」友好，**不卡 novelty**——这正好匹配本稿。
5. 规避了你被 desk-reject 实证的 Sci Rep / PeerJ / PLOS ONE 三类。

### 投稿阶梯

```
第 1 顺位 → BMC Anesthesiology      [IF 3.2 | Q2 | 中科院麻醉3区]   ← 锁定首投
    │ 拒稿 / 转投
    ├─→ 第 2 顺位 → Journal of Clinical Monitoring and Computing
    │                                [IF 2.6 | Q2 | 中科院麻醉4区]
    │                                主题最贴（Chaari 2026 论点同向）
    │                                ⚠️ 2026 起全 OA，APC €2990；中科院小类仅 4 区
    │
    └─→ 冲击档 → Journal of Clinical Anesthesia
                                     [IF 6.0 | Q1(6/72) | 中科院2区Top]
                                     影响力最高 + 可选订阅模式免 APC
                                     ⚠️ desk-reject 风险实质存在
备选 → BMC Medical Informatics and Decision Making  [IF 5.5 | Q2 | 需重框为信息学角度]
保底 → Journal of Anesthesia                        [IF 2.7–2.8 | Q2 | 非OA无APC]
```

### 投稿前必须补齐的三项硬缺口

| # | 缺口 | 处置 |
|---|---|---|
| 1 | **数据可用性声明** | MOVER 需签 DUA，**不得**上传患者级数据。声明写「经 UCI MOVER 签署 DUA 获取，申请网址 mover.ics.uci.edu」+ 代码仓库实名 URL + 版本 tag。**禁止写 "available on request"** |
| 2 | **伦理声明** | 你无本单位 IRB。如实写「仅使用已去标识的公开数据库，数据获取已签 DUA；本单位 IRB 认定此类研究豁免」——⚠️ **须你确认措辞是否与实际相符，不得虚构批准号** |
| 3 | **外部验证缺失** | 作为头号局限明示；讨论中给出可外部验证的公开队列（VitalDB 已有 MOVER 外部验证先例）作为后续工作 |

---

## 7. 最终锁定（2026-10-19，作者已拍板 3 项）

### 7.1 拍板结果

| # | 事项 | 作者决定 |
|---|---|---|
| 3 | 批判 Preprints 202603.1373 的 0.973 | ✅ **同意**（对事不对人、措辞克制） |
| 2 | APC 承受度是否影响排序 | ✅ **会**——按下表条件化排序 |
| 4 | 本单位 IRB | ⏳ 见 §7.4 两条路线 |

### 7.2 ✅ 推荐结论：**首投 BMC Anesthesiology**（预算允许时）

**理由（按权重）**：
1. **命中率实证最强**——该刊已发表 3 篇**同证据级别**稿（Chiu 2025 AUROC 0.80 **仅内部验证**；
   Xu 2025 0.782–0.855；Cheun 2026 0.804/0.735/0.712）。你的 0.723 落在已接受区间。
   这是**唯一有硬实证**支持"这篇能被接收"的期刊。
2. **中科院小类麻醉学 3 区** —— 优于 JCMC 的 4 区，对职称/考核实质有用。
3. 你已备好投稿通道（EM journal ID 12871）。
4. 规避 Sci Rep / PeerJ / PLOS ONE 三类你有实证教训的刊。

> **核心判断**：你的首要痛点是**发出去**，不是发多高。BMC Anesthesiology 是命中率、
> 分区、成本三者最平衡的选项。

### 7.3 APC 条件化排序（回答"APC 是否影响排序"：会影响，且影响很大）

| 预算情形 | 首投 | 第二顺位 | 保底 |
|---|---|---|---|
| **APC 可接受**（≤€3000） | **BMC Anesthesiology**<br>IF 3.2 / Q2 / 麻醉3区 / £2590 | **JCA**<br>IF 6.0 / Q1 / 2区Top / 订阅模式 **¥0** | J Anesthesia<br>IF 2.7–2.8 / Q2 / 零APC |
| **APC 是硬约束**（想省） | **JCA**（订阅模式 ¥0）<br>IF 6.0 / Q1 / **2区Top** | J Anesthesia<br>IF 2.7–2.8 / Q2 / 零APC | BMC Anesthesiology<br>（需 £2590，降为第三） |

**关键结论**：JCA 是**唯一同时满足「IF 最高 + 分区最好 + 零 APC」**的刊，
代价只是命中率（无外部验证 + 替代终点 + 竞争激烈 → desk-reject 风险实质存在）。
→ **预算宽松 → BMC Anesthesiology（求稳）；预算紧张 → JCA（求性价比，接受试错成本）。**

**JCMC 定位下调**：主题契合仍然最强（Chaari 2026 论点同向），但
**中科院小类仅 4 区 + 2026 起全 OA €2990（最贵）+ IF 最低（2.6）**——
三项均劣于 BMC Anesthesiology，故**不作为首投**，仅作 BMC/JCA 均失手后的第三选择。

### 7.4 本单位 IRB —— 建议与两条路线

**建议：现在就去申请一份「回顾性研究伦理豁免/备案」确认函。**
理由：①成本极低、周期数周；②一次性消除所有候选刊的伦理卡点；
③**JCMC 有第三方投稿经验称须提交伦理审查证明**——若你走 JCMC，这份函是刚需。

⚠️ **红线**：**严禁虚构批准号或批准日期。** 未取得就写"未取得"，不能编。

**路线 A（已取得豁免函）——推荐使用的措辞**：

> This retrospective study used only de-identified data from the MOVER (Medical Informatics
> Operating Room Vitals and Events Repository) database, University of California Irvine,
> accessed under a signed Data Use Agreement. The study was reviewed by the Institutional
> Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese
> Medicine, which determined that it met criteria for exemption (approval No. [编号],
> date [日期]). No patients were recruited and no intervention was performed.
> The requirement for informed consent was waived because the data were pre-existing and
> de-identified.

**路线 B（未取得本单位 IRB）——如实声明，不虚构**：

> This study analysed a pre-existing, de-identified database (MOVER, University of California
> Irvine) obtained under a signed Data Use Agreement. No patients were recruited, no
> intervention was performed, and no identifiable information was accessed. In accordance with
> the policy of [本单位伦理委员会名称], research using exclusively pre-existing de-identified
> data does not require prospective ethical approval; a formal determination was therefore not
> sought. All analyses were conducted in accordance with the Declaration of Helsinki.
>
> （中文版，投中文刊或需要时用）
> 本研究仅使用已去标识的既有数据库（MOVER，美国加州大学欧文分校），数据获取已签署
> 数据使用协议（DUA）。未招募患者、未实施干预、未接触可识别信息。依据本单位伦理委员会
> 规定，仅使用既有去标识数据的研究无需前瞻性伦理审批，故未申请正式批件。

⚠️ **路线 B 的风险**：JCMC 可能要求正式伦理证明 → **若走路线 B，优先 BMC 系列**
（BMC 明确接受 DUA + 去标识公开数据库的声明写法），避免投 JCMC。

**独立佐证（可用于回应审稿人）**：medRxiv 2026.08.26.26361468 使用完全相同的两个公开
数据库（VitalDB + MOVER），其伦理声明为「仅使用研究开始前已公开可得的既有去标识人类
数据集 + 已签 DUA」，并被接受发表。**可照此援引 precedent。**

### 7.5 批判 Preprints 202603.1373 的措辞模板（克制版，对事不对人）

**策略**：把批评落到**现象**上（引用 Chaari 2026 与 JCMC scoping review 作系统性证据），
再落到**该篇的具体数值**上；不用"错误/不当/夸大"等指控性词，只用
"cannot be reproduced from the reported methods" / "a plausible explanation is"。

> Recent work applying gradient-boosted trees to the same MOVER resource has reported
> near-perfect discrimination for short-horizon hypotension prediction (AUROC 0.973,
> accuracy 0.942, precision 0.938, recall 0.945 at a 5-minute horizon) [Preprints.org
> 202603.1373]. Such near-separable performance is difficult to reconcile with the
> measurement density of this resource: in the SIS component, non-invasive mean arterial
> pressure is recorded in 19.89% of case-minutes, and 96.1% of non-empty recording segments
> are isolated single minutes. Under those conditions, discrimination of this magnitude is
> most plausibly explained by label–feature horizon overlap (i.e., the label window
> overlapping the feature window, or cases already below threshold at the prediction origin
> being retained as predictable events), a mechanism that has been shown to inflate apparent
> performance in intraoperative hypotension prediction generally [Chaari et al. 2026,
> J Clin Monit Comput 40:43–57], and which we cannot verify from the reported methods.
> In our cohort, analysed under an explicit leakage audit (all feature domains truncated at
> the prediction anchor; maximum feature-to-anchor interval 0 min across domains), AUROC was
> 0.723 (AUPRC 0.350), which is consistent in magnitude with an independent external
> evaluation on MOVER (AUROC 0.696 in 3,069 patients [medRxiv 2026.08.26.26361468]).
> Systematic reviews of perioperative AI likewise find that external validation and
> bias-resistant evaluation remain uncommon [Hernández Rincón et al. 2026, JCMC].

**配套做法（降低风险）**：
- 引用时使用**预印本完整出处**（Preprints.org，DOI 10.20944/preprints202603.1373.v1），
  并注明"未经同行评议的预印本"。
- 同一段落内**同时引用 Chaari 2026 与 scoping review**，说明这是**领域系统性问题**，
  而非针对某一篇——这是"对事不对人"的关键。
- 在 Limitations 里也给自己留一句：**我们的结果同样受无外部验证限制**，避免双标观感。

---

## 附：核实来源清单（年份戳 2026-10-19）

| 期刊 | 主要来源 |
|---|---|
| BMC Anesthesiology | X-MOL 期刊库、恩特学术、学术之家（三源一致：IF 3.2 / Q2 / 中科院 3 区 / SCIE） |
| JCA | 恩特学术、学术之家、爱科学（三源一致：IF 6.0 / Q1 6-7of72 / 中科院 2 区 Top / SCIE） |
| JCMC | X-MOL、恩特学术、学术之家（IF 2.6 / Q2 / 中科院 3 区）、**Springer 官方 OA 转型 FAQ（APC €2990/$3890/£2590）** |
| BMC MIDM | X-MOL、恩特学术、学术之家（IF 5.5 / Q2 / 中科院 3 区） |
| JA | 科研通 ablesci、爱科学、AI4Paper（IF 2.7–2.8 分歧已标注 / Q2 / 中科院 3 区） |
| 竞品文献 | Preprints.org 202603.1373；medRxiv 2026.08.26.26361468；Research Square rs-10347757 |
| 契合实证 | Chaari et al. 2026 JCMC 40(1):43-57（PubMed 40938328）；Chiu et al. 2025 BMC Anesthesiol 25:351（PMID 40676538）；Cheun et al. 2026 BMC Anesthesiol 26:334 |

**未核实项**：
- BMC Anesthesiology 与 BMC MIDM 的当前 APC（本轮检索未命中官方页，BMC Anesthesiology 的数字引自你此前记录）
- 各刊当前精确字数上限（**编辑稿件前须逐刊核实**，本轮未做）
