# Round-2 复审 — MOVER/SIS IOH 预测稿件（manuscript_v0.1.md）

> 编辑：AI 期刊编辑（整合 4 位独立评审 + 独立复算）
> 日期：2026-10-20
> 输入：Round-1 修订稿 + Round-1 评审动作闭环记录（`REVIEW_round1_2026-10-20.md`）

---

## 1. Round-1 修订的确认（四组评审复验）

| 评审 | 原判定 | Round-1 后复验结论 |
|---|---|---|
| **A1 领域** | Minor revision | **Accept (minor)** — 模型≈现有血压的局限已写入 Limitations #9 与第 4 条启示；[14][15][16] 已引用；Sun 2015 / POQI 2024 已作为 [17][18] 补入并引用；MAP-only DCA 基准已落地。 |
| **A2 设计-生物统计** | Minor revision | **Accept (minor)** — 校准表述已改为"必须重校准而非装饰"（无信息 Brier 0.131 为锚）；表 5 已改为测试集口径并加探索性脚注；DCA 时间切分上界 0.45→**0.73** 已修正；MAP-only 基准已补。 |
| **A3 溯源-复算** | Major revision | **Accept** — 审计追踪已扩至 154 行（时间校准、全部 DCA 净收益、时间亚组、病例计数覆盖率、密度、1,496、亚组测试集 n、条件患病率口径）。所有关键数字现已可追溯到 `s3_*/s1_*/s2_*` 产物。 |
| **A4 期刊-报告** | Minor revision | **Accept (minor)** — TRIPOD+AI 已作为 Additional file 2；参考文献泄露的 "(verified)/(unrefereed)" 注记已剥离；18 篇参考文献计数正确；伦理声明已改为路线 B（DUA 豁免，未虚构编号）。 |

**交叉结论：四组对 Round-1 修订均给出 "Accept / Minor"，编辑综合判定 = Minor revision（小修后接收）**——对 *BMC Anesthesiology* 口径而言已达投稿就绪。

---

## 2. Round-2 新发现（独立复算暴露的算术 bug）⚠️

在对稿件做"逐项核对"时，编辑独立复算了条件患病率口径，发现一个**未被 Round-1 捕获的真实错误**：

### 2.1 问题
- 稿件 Limitations #7 原文写："the conditional prevalence among cases with at least 10 measurements was **17.5% (2,622 of 14,965)**"。
- 但建模层 n = 16,861，其中 **1,496** 例因 <10 次锚点后 MAP 被"按构造判阴性"（`s1_data_quality.json`：`postanchor_nmap_measurements.n_ge_10 = 15,365` → 16,861 − 15,365 = 1,496，已核实）。
- 因此**可评估分母应为 15,365，而非 14,965**；条件患病率 = 2,622 / 15,365 = **17.06% ≈ 17.1%**。
- 14,965 与 15,365 相差 400，系稿件笔误（分母写错），且 17.5% 由此派生错误。

### 2.2 更深的同源 bug（审计追踪公式）
- `scripts/s4_report.py` 原第 343 行计算：
  `conditional_prevalence = positive_pids / (N − n_ge10)`，即 2,622 / **1,496** = **1.7527**（患病率 > 1，无意义）。
- 正确应为除以 **n_ge10 = 15,365**：2,622 / 15,365 = **0.1706**。
- 即：审计追踪本身也写过错误值（1.7527），与稿件笔误同源但独立——两者都源于"分母取了被排除例数而非可评估例数"。

### 2.3 修复（已落地，含回归保护）
- 稿件 Limitations #7：17.5% (2,622 of 14,965) → **17.1% (2,622 of 15,365)**。
- `s4_report.py`：分母改为 `_n_ge10`，新增 `outcome.D1.n_eligible_ge10_postanchor_map = 15365` 行；重跑后审计追踪 = `conditional_prevalence_ge10meas = 0.1706`（原 1.7527）。
- 质量门 `s5_gate.py`：key_numbers 新增 **"15,365"**，防回归。
- 重跑门禁：**PASS**（摘要 325/350 词、18 篇文献、5 图 6 表、26 项关键数字、DCA@0.15 与 s3 一致）。

> **审计纪律注记**：此错误再次印证用户铁律——"gate 全绿 ≠ 审核完成"。Round-1 门禁只校验固定关键数字清单，未覆盖条件患病率分母；若非 Round-2 独立复算，该笔误会随稿件直投。现审计追踪与稿件已互相自洽（0.1706 ↔ 17.1%/15,365）。

---

## 3. 其余 Round-2 一致性扫描（全部通过）

编辑对稿件其余"易错数字"逐一比对 `s1_data_quality.json` / `s3_metrics.json` / 审计追踪：

| 稿件陈述 | 数据核实 | 结论 |
|---|---|---|
| 19.89% 病例-分钟 MAP 记录密度；收缩/舒张 19.99%/19.95% | `column_non_null_rate`: nMAP 0.1989 / nSBP 0.1999 / nDBP 0.1995 | ✅ |
| HR/PR 94.8%/95.9%；SpO₂ 96.1% | HRe 0.9479 / HRp 0.959 / SP02 0.9608 | ✅ |
| 637,188 段 MAP；96.2% 为单分钟；中位段长 1 min | `nmap_segment_length_distribution` | ✅ |
| 每例中位 MAP 33（P5–P95: 12–90） | `nmap_measurements_per_pid` | ✅ |
| 16,036 例 (95.1%) 有 ≥1 次 NIBP | 审计 `coverage.case_count.non_invasive_bp = 16036`（16,036/16,861=95.1%） | ✅ |
| DCA 净收益 @0.15 = 0.050/0.058；@0.10 = 0.079/0.085 | `s3_calib_dca.json`（0.0503/0.0579；0.0787/0.0848） | ✅ |
| MAP-only AUPRC 0.284 vs XGBoost 0.347；净收益 +0.013 | `map_only_benchmark`（raw 0.2842；nb_increment 0.0132/0.0131） | ✅ |
| 时间切分上界 0.73、患者级 0.58 | `s3_calib_dca.json` 末位正值阈值 | ✅ |

**无其余笔误。**

---

## 4. 综合编辑裁定

- **四组评审共识**：Round-1 修订已化解全部 Major/Minor 关切 → **Minor revision（小修后接收）**。
- **Round-2 新修**：条件患病率笔误 + 审计追踪公式 bug 已修复并加回归保护，门禁 PASS。
- **稿件当前状态**：对 *BMC Anesthesiology* 已达"投稿就绪（accept after minor revision）"级别。**仍未满足的硬门槛均为作者侧行政事项，非稿件科学内容问题。**

---

## 5. 仍遗留给作者的阻塞项（非编辑可代劳）

1. **正式 IRB 豁免/备案函**（TRIPOD 条目 21）：路线 B 已在正文如实声明（DUA 豁免、无编号无日期）；投稿前须补具本单位伦理委员会函件。
2. **复现包推送与 release tag**：本地已提交 2 个 commit（`4a5f490` Round-1 + 待提交 Round-2）；远程 `origin/main` 当前领先本地（含他处提交），且本环境出站 TLS/代理 502 不稳，**须在网络通畅环境 `git fetch && git rebase && git push` 并补 `gh release create v1.0.0`**。正文数据可用性声明已用实名仓库 URL，无"available on request"。
3. **外部验证（推荐但不阻塞投稿）**：单中心内部验证；若能在第二轮补一个外部队列（如 VitalDB/MIMIC 子集）将显著提升接收概率，但非 BMC Anesthesiology 首投硬性要求。

---

## 6. Round-2 动作日志

| # | 修复 | 文件 | 状态 |
|---|---|---|---|
| 1 | 条件患病率分母 14,965→15,365；17.5%→17.1% | `manuscript_v0.1.md` | DONE |
| 2 | 审计追踪条件患病率公式（÷被排除→÷可评估）；新增 n_eligible 行 | `scripts/s4_report.py` → 重跑 | DONE |
| 3 | 质量门 key_numbers 加 "15,365" 防回归 | `scripts/s5_gate.py` | DONE |
| 4 | TRIPOD 模板固化（条目 1/2 ✅、v0.1 引用、设计决策冻结、修订状态） | `scripts/s4_report.py` → 重跑 | DONE |
| 5 | 重生成 docx + 重跑门禁 | `scripts/s5_docx.py` / `s5_gate.py` | DONE（PASS） |
| 6 | 提交 Round-2 修复至本地 git | git | DONE（待 push） |
