# -*- coding: utf-8 -*-
"""流水线入口：按序执行 s1 → s2 → s3 → s4。
任一阶段失败即中止（不打折扣：不静默跳过失败阶段）。"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
STAGES = ["s1_cohort.py", "s2_features.py", "s3_models.py", "s4_report.py"]

for s in STAGES:
    print(f"\n{'='*70}\n>>> {s}\n{'='*70}", flush=True)
    r = subprocess.run([PY, os.path.join(HERE, s)])
    if r.returncode != 0:
        print(f"[FAIL] {s} exit={r.returncode} — 流水线中止，后续阶段不执行", flush=True)
        sys.exit(r.returncode)
print("\n[OK] 全流水线完成。请更新 STATUS.md 并检查 results/ 产物。", flush=True)
