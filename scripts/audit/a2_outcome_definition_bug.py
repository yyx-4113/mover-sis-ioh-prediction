# -*- coding: utf-8 -*-
"""审计2：nMAP 采样模式 + dropna 时间轴压缩对结局患病率的影响。"""
import pandas as pd, numpy as np
P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
vit = pd.read_csv(P+"patient_vitals.csv", dtype=str, na_values=["\\N"])
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"])
for c in ["nMAP","SP02"]: vit[c] = pd.to_numeric(vit[c], errors="coerce")
vit = vit.sort_values(["PID","Obs_time"])

# 每 PID：连续非空 nMAP 段长度分布（用 shift 分组）
v = vit.dropna(subset=["nMAP"])
v["grp"] = (v.groupby("PID")["Obs_time"].diff().dt.total_seconds()/60 != 1).cumsum()
run = v.groupby(["PID","grp"]).size()
print("--- 连续非空 nMAP 段长度分布（分钟）---")
print(run.value_counts().sort_index().head(15))
print("总段数:", len(run), " 中位段长:", run.median(), " mean:", round(run.mean(),2))

# 每 PID 有 MAP 的分钟数 vs 总记录分钟数
tot = vit.groupby("PID").size()
hasm = vit.dropna(subset=["nMAP"]).groupby("PID").size()
cov = (hasm / tot).dropna()
print("\n--- 每 PID 的 nMAP 覆盖率 ---")
print(cov.describe(percentiles=[.05,.25,.5,.75,.95]).round(3))
print("覆盖率<=0.05 的 PID 数:", (cov<=0.05).sum(), "/", len(cov))

# ==== 核心：用正确方式重算 O2，与 s1 当前实现对比 ====
info = pd.read_csv(P+"patient_information.csv", dtype=str, na_values=["\\N"])
info["OR_start"] = pd.to_datetime(info["OR_start"], format="%m/%d/%y %H:%M", errors="coerce")
info["OR_end"]   = pd.to_datetime(info["OR_end"],   format="%m/%d/%y %H:%M", errors="coerce")
info["or_min"] = (info.OR_end - info.OR_start).dt.total_seconds()/60
implaus = (info.or_min <= 0) | (info.or_min > 1440)
print("\n--- OR 窗口合理性 ---")
print("or_min<=0 或 >1440min 的 PID:", implaus.sum(), "/", len(info))
print("or_min<=0:", (info.or_min<=0).sum(), " or_min>1440:", (info.or_min>1440).sum())

keep = info[~implaus].dropna(subset=["OR_start","OR_end"]).copy()
obs = vit.merge(keep[["PID","OR_start","OR_end"]], on="PID", how="inner")
obs = obs[(obs.Obs_time>=obs.OR_start)&(obs.Obs_time<=obs.OR_end)]
# 排除短窗口 + 未成年（复刻 s1 口径）
n_per = obs.groupby("PID").size()
keep = keep[keep.PID.isin(n_per[n_per>=60].index)]
age = pd.to_numeric(info.set_index("PID")["Age"], errors="coerce")
keep = keep[keep.PID.isin(age[age>=18].index)]
obs = obs[obs.PID.isin(keep.PID)]
print("\n分析队列 PID:", keep.PID.nunique(), " OR窗口观测:", len(obs))

def pid_pos_BUGGY(df, sig, thr, minutes, gap):
    """复刻 s1_cohort.py 当前实现（dropna 压缩时间轴）。"""
    gdf = df.dropna(subset=[sig]).sort_values(["PID","Obs_time"])
    pos=set()
    for pid,g in gdf.groupby("PID"):
        v=(g[sig].values<thr); run=mx=0; gapn=0
        for x in v:
            if x: run+=1; gapn=0; mx=max(mx,run)
            else:
                gapn+=1
                if gapn>gap: run=0
        if mx>=minutes: pos.add(pid)
    return pos

def pid_pos_CORRECT(df, sig, thr, minutes, gap):
    """正确实现：重建 1-min 网格，NaN 计为中断（保守）。"""
    pos=set()
    for pid,g in df.groupby("PID"):
        t=g.Obs_time
        idx=pd.date_range(t.min(), t.max(), freq="1min")
        s=pd.Series(np.nan, index=idx)
        s.loc[t]=g[sig].values
        v=(s.values<thr)  # NaN 比较 -> False
        run=mx=0; gapn=0
        for x in v:
            if x: run+=1; gapn=0; mx=max(mx,run)
            else:
                gapn+=1
                if gapn>gap: run=0
        if mx>=minutes: pos.add(pid)
    return pos

print("\n=== O1/O2/O3/O4: 当前实现 vs 正确实现（分析队列 n=%d）===" % keep.PID.nunique())
for oid,(thr,mins,gap) in {"O1":(55,5,0),"O2":(55,5,1),"O3":(55,10,1),"O4":(65,10,1)}.items():
    b=pid_pos_BUGGY(obs,"nMAP",thr,mins,gap)
    c=pid_pos_CORRECT(obs,"nMAP",thr,mins,gap)
    n=keep.PID.nunique()
    print(f"{oid} MAP<{thr} >= {mins}min(gap{gap}): BUGGY={len(b):4d} ({len(b)/n:.2%})  CORRECT={len(c):4d} ({len(c)/n:.2%})  差={len(b)-len(c):+d}")
