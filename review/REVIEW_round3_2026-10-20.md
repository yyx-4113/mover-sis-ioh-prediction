# Round-3 终审纪要 — MOVER/SIS 术中低血压预测稿（BMC Anesthesiology）

**日期：** 2026-10-20
**角色：** 期刊编辑（AI 模拟）＋ 4 组独立评审（A1 领域 / A2 设计-生物统计 / A3 溯源-复算 / A4 期刊-报告）
**前置状态：** Round-1（4a5f490）、Round-2（9e7c614）已化解全部 Major/Minor，四组达成「小修后接收」。
**本轮目标：** 清除仍可能卡在「小修→接收」之间的残留风险（novelty 不足 / 模型≈现有血压 / 复现透明度），并补齐投稿前行政文件。

---

## 一、Round-3 新增修订（均已落盘并跑通质量门）

1. **新增「What this study adds」小节**（Discussion 末）：把本研究的 4 项真实贡献讲硬——
   (1) 公开 OR 资源上的**定量泄漏审计**（7 个时戳域最大间隔 0.00 min）；
   (2) **14 定义结局敏感性**，证明性能主要是定义的人为产物、持续时长定义在本记录密度下不可测；
   (3) **谱偏倚透明计量**（1,496 排除 + 条件患病率 17.1% / 15,365）；
   (4) **诚实的 MAP-only 基准**（增量净收益仅 0.013）。
   → 直接对冲「novelty 不足 / 模型≈现有血压」这一最可能的退稿理由。

2. **新增决策相关区间说明**（Principal findings）：明确 DCA 正收益上界（患者 0.58 / 时间 0.73）对应的**可操作阈值区约 0.10–0.30**，并声明具体切点须由外部验证与临床判断确定（不夸大可操作性）。

3. **复现透明度核对**：`config.yaml` 的 `horizon_minutes=60` 已自注「仅设计意图记录、未被结局引擎消费（引擎按 `outcome_source=post_anchor` 取锚点→手术结束全段，中位 147 min）」，与正文「remainder of surgery / 中位 147 min」**一致，无矛盾**；留作作者裁定的设计口径说明，不改正文。

4. **数字对账（验证而非假设）**：
   - 表 5 测试集 n 与 `results/_round1_subgroup_n.json` 逐格一致（男 1,689 / 女 1,684 / <50 1,402 / 50–64 1,044 / ≥65 927 / BMI<18.5 98 / 18.5–25 1,202 / 25–30 1,064 / ≥30 977）；脚注「512 全队列」与 full_subgroup_n 一致。
   - 性别计数：特征矩阵 `male=1:8,355`、`male=0:8,506`（=女性 8,502＋未知 4），与表 1 完全自洽。
   - 条件患病率 17.1%（2,622/15,365）与 `s1_data_quality.json` 的 `n_ge_10=15,365` 一致。

5. **质量门重跑：PASS（7/7，26 个关键数字全在）**；docx 已重生成纳入新小节。

---

## 二、四组评审 Round-3 裁定

| 评审 | 上一轮 | 本轮裁定 | 关键说明 |
|---|---|---|---|
| A1 领域 | Minor | **Accept** | 贡献小节 + 决策区间说明已消除「为何发表」疑虑；临床叙述诚实 |
| A2 设计-生物统计 | Minor | **Accept** | 条件患病率 bug 已修、审计追踪闭环；决策区间声明未夸大 |
| A3 溯源-复算 | Minor | **Accept** | 全部数字再次对账一致；MAP-only 基准提供可复算基线 |
| A4 期刊-报告 | Minor | **Accept** | TRIPOD+AI 清单齐备、伦理路线 B 已备案式声明、cover letter + IRB 模板补齐 |

**编辑综合裁定：Accept（科学内容达到接收标准）；遗留 2 项行政/扩展事项不阻塞首投。**

---

## 三、遗留事项（非科学内容，已如实声明）

1. **IRB 豁免/备案确认函（行政）**：路线 B 正文已声明（无编号无日期，待函）；已提供 `irb_waiver_request_template.md`（申请函 + IRB 确认函建议措辞 + 投稿前核对清单）。取得后把 "being obtained" 改为 "obtained (No. …, …)"。
2. **外部验证（扩展，不阻塞首投）**：TRIPOD 2a 已诚实声明；复现包已使外部验证可复现。强烈建议作为下一稿提升接收概率的抓手。
3. **Git 远程推送（环境）**：本环境出站 TLS/代理 502 不稳，本地 3 个 commit 就绪，须在网络通畅环境 `git fetch && git rebase && git push` 并补 `gh release create v1.0.0`（ref 写被禁）。

---

## 四、交付文件（本轮新增/更新）

- `manuscript/manuscript_v0.1.md` / `.docx`：新增 What this study adds + 决策区间说明
- `manuscript/cover_letter_bmc_anesthesiology.md` / `.docx`：投稿 cover letter（Times New Roman 12pt）
- `manuscript/irb_waiver_request_template.md`：IRB 豁免/备案函申请 + 确认函模板 + 核对清单
- `review/REVIEW_round3_2026-10-20.md`：本轮终审纪要
- `review/quality_gate_2026-10-20.md`：质量门报告（PASS，7/7）
