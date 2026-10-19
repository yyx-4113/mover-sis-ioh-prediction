# -*- coding: utf-8 -*-
"""审计：SIS patient_vitals 的真实时间轴结构 + s1 结局派生是否正确。"""
import pandas as pd, numpy as np

P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
# 只取前 400 万行已经全量；先读全量但只保留需要的列
vit = pd.read_csv(P+"patient_vitals.csv", dtype=str, na_values=["\\N"], keep_default_na=True)
print("rows:", len(vit), "pids:", vit.PID.nunique())
for c in ["HRe","HRp","nSBP","nMAP","nDBP","SP02"]:
    vit[c] = pd.to_numeric(vit[c], errors="coerce")
print("\n--- 各列非空率（全表） ---")
print(vit[["HRe","HRp","nSBP","nMAP","nDBP","SP02"]].notna().mean().round(4))

vit["Obs_time"] = pd.to_datetime(vit["Obs_time"], errors="coerce")
print("\nObs_time NaT:", vit.Obs_time.isna().sum())

# 每个 PID 的时间轴连续性
vit = vit.sort_values(["PID","Obs_time"])
g = vit.groupby("PID")["Obs_time"]
dt = g.diff().dt.total_seconds()/60.0
print("\n--- 同 PID 相邻记录间隔（分钟）分布 ---")
print(dt.value_counts().head(10))

# 每 PID 的记录数 vs OR 窗口分钟数
info = pd.read_csv(P+"patient_information.csv", dtype=str, na_values=["\\N"])
info["OR_start"] = pd.to_datetime(info["OR_start"], format="%m/%d/%y %H:%M", errors="coerce")
info["OR_end"]   = pd.to_datetime(info["OR_end"],   format="%m/%d/%y %H:%M", errors="coerce")
print("\nOR_start NaT:", info.OR_start.isna().sum(), "/", len(info))
info["or_min"] = (info.OR_end - info.OR_start).dt.total_seconds()/60
print("OR 时长(分钟) describe:")
print(info["or_min"].describe(percentiles=[.01,.05,.5,.95,.99]).round(1))
