# 参考文献著录核实记录（2026-10-20）

本文档记录 `manuscript/manuscript_v0.1.md` 参考文献逐篇联网核实结果与来源。
核实方法：WebSearch + 出版方/PubMed/出版社官方页交叉比对。所有卷期、页码、DOI 均来自
可访问的出版方或索引页面，**非凭记忆**。

| # | 引用 | 核实结论 | 来源 |
|---|---|---|---|
| 1 | Salmasi 2017, Anesthesiology 126(1):47–65 | ✅ 已核实(2026-10-19) | Anesthesiology / PubMed |
| 2 | Wijnberge 2020, JAMA 323(11):1052–1060 | ✅ **补 DOI 10.1001/jama.2020.0592**；卷期页码无误；PMID 32065827 | JAMA Network / PubMed |
| 3 | Maheshwari 2020, Anesthesiology 133(6):1214–1222 | ✅ **补 DOI 10.1097/ALN.0000000000003557**；卷期页码无误 | PubMed / WeChat secondary (DOI confirmed) |
| 4 | Alrantisi KMM 2026, Preprints 202603.1373 | ✅ **补作者名 Alrantisi KMM**；doi 10.20944/preprints202603.1373.v1 正确；单作者预印本，发布 2026-03-17；声明 AUC-ROC 0.973（5-min） | Preprints.org 官方页 / Scilit / Google Scholar |
| 5 | Chaari 2026, J Clin Monit Comput 40(1):43–57 | ✅ 已核实(2026-10-19)；DOI 10.1007/s10877-025-01357-0 | Springer |
| 6 | Hernández 2026, J Clin Monit Comput | ✅ 已核实(2026-10-19)；DOI 10.1007/s10877-026-01449-5 | Springer |
| 7 | Collins 2024, BMJ 385:e078378 | ✅ **补 DOI 10.1136/bmj-2023-078378**；注意 DOI 编号含 2023，正式出版 2024-04-16（已接受 2024-01-17） | BMJ 官方 PDF / Birmingham repo |
| 8 | MOVER, UCI, doi:10.24432/C5VS5G | ✅ 已核实(2026-10-19) | UCI ML Repository |
| 9 | This manuscript, Table 2 | — 自引 | — |
| 10 | Pedregosa 2011, JMLR 12:2825–2830 | ✅ **卷期页码无误；JMLR 文章本身不分配 DOI**（已注明） | scikit-learn 官方 about/citing 页 |
| 11 | Chen & Guestrin 2016, KDD:785–794 | ✅ **补 DOI 10.1145/2939672.2939785**；卷期页码无误 | ACM DL / BibSLEIGH |
| 12 | Ke 2017, NeurIPS 30:3146–3154 | ✅ **卷期页码无误；NeurIPS 会议录不分配 DOI**（已注明） | NeurIPS proceedings / arxiv-vanity |
| 13 | Oyarzun 2026, medRxiv 2026.08.26.26361468 | ✅ 已核实(2026-10-19)；VitalDB→MOVER 外部验证 3,069 例 AUROC 0.696 | medRxiv |
| 14 | **Chiu 2025, BMC Anesthesiol 25:351** | ✅ **补 DOI 10.1186/s12871-025-03195-8**；XGBoost + 10折内部验证、无外部验证、AUROC 0.80（95%CI 0.74–0.86）。**与本稿证据级别一致，支撑期刊锁定论证** | Springer / PMC / PubMed |
| 15 | **Cheun 2026, BMC Anesthesiol 26:334** | ✅ **补 DOI 10.1186/s12871-026-03841-9**；XGBoost 内部 0.804 / 外部 0.735 / 0.712。**与本稿证据级别一致，支撑期刊锁定论证** | Springer / Yonsei IR / SNU Pure |
| 16 | Walsh 2013, Anesthesiology 119(3):507–515 | ✅ 已核实(2026-10-19) | Anesthesiology |

## 关键判定

1. **#2/#3/#7/#11 原缺 DOI** → 已补录，现 16 篇中 12 篇带 DOI（#9 自引、#10/#12 期刊本身无 DOI）。
2. **#4 Preprints 批判对象的作者与数值均确证**：单作者 Khaled M.M. Alrantisi，发布于 Preprints.org（2026-03-17），
   自称 XGBoost AUC-ROC **0.973**（5-min 预测窗）。该数值在 MOVER/SIS nMAP 非空率仅 19.89%、
   96.1% 非空段为孤立单分钟的数据上高度可疑——正文 Discussion 的批判据此展开。
3. **#14/#15 是 BMC Anesthesiology 已发表的同级别稿**（单中心回顾 + XGBoost + 仅内部/外部验证，
   AUROC 0.80 / 0.804），确证本稿 0.722–0.723 落在期刊已接受区间内 → 首投 BMC Anesthesiology 的
   实证依据成立。
4. 全部 `⚠️ *citation details to verify*` 标记已清零（0 处残留）。

## 仍需作者注意（非著录问题）

- 数据可用性声明中的仓库 URL 目前为占位符（`manuscript_v0.1.md` 第 521 行 `⚠️ TODO`），
  投稿前须替换为真实创建并打 tag 的 GitHub 仓库地址（禁写 "available on request"）。
- 伦理声明（路线 B）已按"既有去标识数据 + 已签 DUA"如实撰写，无批准号、无批准日期，未虚构。
