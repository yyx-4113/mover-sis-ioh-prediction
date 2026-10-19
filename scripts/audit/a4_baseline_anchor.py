# -*- coding: utf-8 -*-
"""审计4：术前基线 MAP 可用性 + OR_start/Surgery_start 锚点差距 + 麻醉类型可得性。"""
import pandas as pd, numpy as np
P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
vit = pd.read_csv(P+"patient_vitals.csv", dtype=str, na_values=["\\N"])
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"])
vit["nMAP"] = pd.to_numeric(vit["nMAP"], errors="coerce")
info = pd.read_csv(P+"patient_information.csv", dtype=str, na_values=["\\N"])
for c in ["OR_start","OR_end","Surgery_start","Surgery_end"]:
    info[c] = pd.to_datetime(info[c], format="%m/%d/%y %H:%M", errors="coerce")

# 1) OR_start 之前是否有 vitals 记录（术前基线）
first = vit.groupby("PID")["Obs_time"].min()
j = info.set_index("PID").join(first.rename("first_obs"))
j["pre_min"] = (j["OR_start"] - j["first_obs"]).dt.total_seconds()/60
print("=== OR_start 之前可用作基线的分钟数 ===")
print(j["pre_min"].describe(percentiles=[.25,.5,.75,.95]).round(1))
print("OR_start 前 >=5min 记录的 PID:", (j.pre_min>=5).sum(), "/", j.pre_min.notna().sum())
print("OR_start 前 >=30min 记录的 PID:", (j.pre_min>=30).sum())

# OR_start 前 5-15min 内能否拿到 >=1 次 MAP 测量
pre = vit.merge(info[["PID","OR_start"]], on="PID")
pre = pre[(pre.Obs_time < pre.OR_start) & (pre.Obs_time >= pre.OR_start - pd.Timedelta(minutes=30))]
pre_m = pre.dropna(subset=["nMAP"])
cnt = pre_m.groupby("PID").size()
print("OR_start 前 30min 内有 >=1 次 nMAP 的 PID:", len(cnt), f"({len(cnt)/info.PID.nunique():.1%})")

# 2) OR_start -> Surgery_start 差距
g = (info["Surgery_start"] - info["OR_start"]).dt.total_seconds()/60
print("\n=== OR_start -> Surgery_start 差距（分钟）===")
print(g.describe(percentiles=[.05,.25,.5,.75,.95]).round(1))

# 3) 麻醉类型可得性
pe = pd.read_csv(P+"patient_procedure_events.csv", na_values=["\\N"])
print("\n=== patient_procedure_events 事件计数 ===")
print(pe.Event_name.value_counts().head(25))
