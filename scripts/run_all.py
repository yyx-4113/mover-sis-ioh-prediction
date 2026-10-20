# -*- coding: utf-8 -*-
"""流水线入口：按序执行 s1 → s2 → s3 → DCA 基准 → 外部链 → s6 敏感性 → s4 图件 → s4 报告。

Round-6 起的规范顺序（2026-10-20，v1.0.0-round6）：
  1. s1_cohort.py               队列 + 锚点 + 14 结局标签
  2. s2_features.py             特征矩阵（主口径，特征窗 [anchor-15, anchor] 闭）
  3. s2_features.py --half-open 半开窗变体（S2 敏感性用，产物加 _halfopen 后缀）
  4. s3_models.py               四模型 × 双切分 + OOF isotonic 校准 + DCA
  5. _dca_map_benchmark.py      MAP-only DCA 基准（写回 s3_calib_dca.json）
  6. ext_core_benchmark.py      53 特征可移植子集在 MOVER 上的基准（用新 s2 特征）
  7. ext_build.py train         全队列复训核心模型（必须在 s2 之后，否则外运模型与特征不同代）
  8. ext_build.py apply         套用到 VitalDB，出 external_validation.json + 预测（s6 S3/S4/S6 依赖）
  9. s6_sensitivity.py          Round-6 敏感性分析集（S1-S8）
 10. s4_figures.py              图 1-6
 11. s4_report.py               HTML 报告 + 审计追踪表（并入 s6 行）

注：ext_build.py features 阶段需 vitaldb 包 + 联网（VitalDB 账户），不在本流水线内；
    其产物 vitaldb_features.csv / vitaldb_labels.csv 由特征定义派生、与 MOVER 侧无关，可缓存复用。

任一阶段失败即中止（不打折扣：不静默跳过失败阶段）。
质量门 s5_gate.py 单独跑（稿件 ↔ 产物一致性），失败须人工处理后再提交。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

STAGES = [
    ["s1_cohort.py"],
    ["s2_features.py"],
    ["s2_features.py", "--half-open"],
    ["s3_models.py"],
    ["_dca_map_benchmark.py"],
    ["ext_core_benchmark.py"],
    ["ext_build.py", "train"],
    ["ext_build.py", "apply"],
    ["s6_sensitivity.py"],
    ["s4_figures.py"],
    ["s4_report.py"],
]

for argv in STAGES:
    print(f"\n{'='*70}\n>>> {' '.join(argv)}\n{'='*70}", flush=True)
    r = subprocess.run([PY, os.path.join(HERE, argv[0])] + argv[1:])
    if r.returncode != 0:
        print(f"[FAIL] {' '.join(argv)} exit={r.returncode} — 流水线中止，后续阶段不执行",
              flush=True)
        sys.exit(r.returncode)
print("\n[OK] 全流水线完成。请跑 scripts/s5_gate.py 并更新 STATUS.md。", flush=True)
