# -*- coding: utf-8 -*-
"""Round-1 修订辅助：复现切分、计算测试集亚组 n、核对 1,496 与密度数字。
仅依赖 pandas/numpy，不重跑建模。
"""
import os, json, sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
feat = pd.read_csv(os.path.join(RES, "s2_features.csv")).set_index("PID")
lab = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")
anchor = pd.read_csv(os.path.join(RES, "s1_anchor.csv")).set_index("PID")
y = lab["D1"].astype(int)
year = feat["or_year"].astype(int)

# 复现患者级切分（与 s3_models.py 一致）
ridx, teidx = train_test_split(feat.index, test_size=0.2, random_state=12345, stratify=y)
tr_mask = (year <= 2017).values
te_mask = (year == 2018).values
splits = {"patient": pd.Index(teidx), "temporal": feat.index[te_mask]}

def subgroup_n(idx, tag):
    X = feat.loc[idx]; yy = y.loc[idx]
    out = {}
    for v, lbl in [(1, "male"), (0, "female")]:
        m = (X["male"] == v).values
        out[f"sex_{lbl}"] = int(m.sum())
    for lo, hi, lbl in [(0, 50, "age<50"), (50, 65, "age50-65"), (65, 200, "age>=65")]:
        m = ((X["age"] >= lo) & (X["age"] < hi)).values
        out[lbl] = int(m.sum())
    for lo, hi, lbl in [(0, 18.5, "bmi<18.5"), (18.5, 25, "bmi18.5-25"),
                       (25, 30, "bmi25-30"), (30, 200, "bmi>=30")]:
        m = ((X["bmi"] >= lo) & (X["bmi"] < hi)).values
        out[lbl] = int(m.sum())
    return out

print("=== TEST-SET subgroup n (held-out) ===")
test_n = {}
for sp, idx in splits.items():
    n = subgroup_n(idx, sp)
    test_n[sp] = n
    print(f"[{sp}] test N={len(idx)} events={int(y.loc[idx].sum())}")
    for k, v in n.items():
        print(f"   {k}: {v}")

print("\n=== FULL-COHORT subgroup n ===")
full = subgroup_n(feat.index, "full")
for k, v in full.items():
    print(f"   {k}: {v}")

# 核对 1,496
dq1 = json.load(open(os.path.join(RES, "s1_data_quality.json"), encoding="utf-8"))
n_lt10 = dq1["postanchor_nmap_measurements"]["n_ge_10"]
analytic = json.load(open(os.path.join(RES, "s1_cohort.json"), encoding="utf-8"))["analytic_pids"]
print(f"\n1,496 check: analytic={analytic} - postanchor_nmap>=10 ({n_lt10}) = {analytic - n_lt10}")

# 密度数字
print("\n=== recording density (from s1_data_quality.json) ===")
col = dq1["column_non_null_rate"]
seg = dq1["nmap_segment_length_distribution"]
pp = dq1["nmap_measurements_per_pid"]
print(f"  nMAP case-minute pct = {col['nMAP']*100:.2f}")
print(f"  SBP case-minute pct = {col['nSBP']*100:.2f}")
print(f"  DBP case-minute pct = {col['nDBP']*100:.2f}")
print(f"  HR case-minute pct  = {col['HRe']*100:.2f}")
print(f"  HRp case-minute pct = {col['HRp']*100:.2f}")
print(f"  SpO2 case-minute pct= {col['SP02']*100:.2f}")
print(f"  segments total = {seg['total_segments']}, length-1 share = {seg['length_1_share']*100:.2f}")
print(f"  MAP per case median = {pp['p50']:.0f} (p05 {pp['p05']:.0f}, p95 {pp['p95']:.0f})")

# 保存测试集亚组 n 供后续使用
out = {"test_subgroup_n": test_n, "full_subgroup_n": full,
       "n_lt10_excluded": analytic - n_lt10}
json.dump(out, open(os.path.join(RES, "_round1_subgroup_n.json"), "w"), indent=2)
print("\nsaved -> results/_round1_subgroup_n.json")
