# -*- coding: utf-8 -*-
"""审计3：数据真正能支撑的 IOH 定义族 + SpO2 侧可靠性。"""
import pandas as pd, numpy as np
P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
vit = pd.read_csv(P+"patient_vitals.csv", dtype=str, na_values=["\\N"])
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"])
for c in ["nMAP","SP02"]: vit[c] = pd.to_numeric(vit[c], errors="coerce")
vit = vit.sort_values(["PID","Obs_time"])
info = pd.read_csv(P+"patient_information.csv", dtype=str, na_values=["\\N"])
info["OR_start"] = pd.to_datetime(info["OR_start"], format="%m/%d/%y %H:%M", errors="coerce")
info["OR_end"]   = pd.to_datetime(info["OR_end"],   format="%m/%d/%y %H:%M", errors="coerce")
info["or_min"] = (info.OR_end-info.OR_start).dt.total_seconds()/60
keep = info[(info.or_min>0)&(info.or_min<=1440)].dropna(subset=["OR_start","OR_end"])
obs = vit.merge(keep[["PID","OR_start","OR_end"]], on="PID", how="inner")
obs = obs[(obs.Obs_time>=obs.OR_start)&(obs.Obs_time<=obs.OR_end)]
nper = obs.groupby("PID").size()
keep = keep[keep.PID.isin(nper[nper>=60].index)]
age = pd.to_numeric(info.set_index("PID")["Age"], errors="coerce")
keep = keep[keep.PID.isin(age[age>=18].index)]
obs = obs[obs.PID.isin(keep.PID)]
N = keep.PID.nunique()
print(f"分析队列 n={N}, OR窗口观测={len(obs)}")

def any_below(df, sig, thr):
    """任一记录分钟 < thr。"""
    s = set(df.loc[df[sig]<thr, "PID"]); return s

def n_points_within(df, sig, thr, n_pts, window_min):
    """>=n_pts 个低值记录落在 window_min 分钟滚动窗内（NIBP 可计算口径）。"""
    pos=set()
    for pid,g in df.groupby("PID"):
        t = g.loc[g[sig]<thr, "Obs_time"].values
        if len(t)<n_pts: continue
        ts = pd.Series(pd.to_datetime(t))
        for i in range(len(ts)-n_pts+1):
            if (ts.iloc[i+n_pts-1]-ts.iloc[i]).total_seconds()/60 <= window_min:
                pos.add(pid); break
    return pos

def frac_min_below(df, sig, thr, frac, min_meas):
    """有 >=min_meas 次记录且低值占比 >= frac。"""
    pos=set()
    for pid,g in df.groupby("PID"):
        g=g.dropna(subset=[sig])
        if len(g)<min_meas: continue
        if (g[sig]<thr).mean()>=frac: pos.add(pid)
    return pos

print("\n=== MAP 侧：数据真正能支撑的定义族（n=%d）===" % N)
print(f"{'定义':44s} {'阳性':>5s} {'患病率':>8s}")
for lbl,fn in [
  ("任一记录 MAP<55", lambda d: any_below(d,"nMAP",55)),
  ("任一记录 MAP<65", lambda d: any_below(d,"nMAP",65)),
  ("任一记录 MAP<70", lambda d: any_below(d,"nMAP",70)),
  (">=3 低值(<55) 落在 30min 内", lambda d: n_points_within(d,"nMAP",55,3,30)),
  (">=5 低值(<55) 落在 60min 内", lambda d: n_points_within(d,"nMAP",55,5,60)),
  (">=3 低值(<65) 落在 30min 内", lambda d: n_points_within(d,"nMAP",65,3,30)),
  (">=5 低值(<65) 落在 60min 内", lambda d: n_points_within(d,"nMAP",65,5,60)),
  (">=10 次记录 且 <55 占比>=30%", lambda d: frac_min_below(d,"nMAP",55,0.30,10)),
  (">=10 次记录 且 <65 占比>=30%", lambda d: frac_min_below(d,"nMAP",65,0.30,10)),
]:
    s = fn(obs); print(f"{lbl:44s} {len(s):5d} {len(s)/N:8.2%}")

print("\n=== SpO2 侧（覆盖率 96%，原口径可靠）===")
print(f"{'定义':44s} {'阳性':>5s} {'患病率':>8s}")
for oid,(thr,mins,gap) in {"O5":(90,2,0),"O6":(92,5,0)}.items():
    pos=set()
    for pid,g in obs.groupby("PID"):
        t=g.Obs_time
        idx=pd.date_range(t.min(),t.max(),freq="1min")
        s=pd.Series(np.nan,index=idx); s.loc[t]=g["SP02"].values
        v=(s.values<thr); run=mx=0; gapn=0
        for x in v:
            if x: run+=1; gapn=0; mx=max(mx,run)
            else:
                gapn+=1
                if gapn>gap: run=0
        if mx>=mins: pos.add(pid)
    print(f"{oid} SpO2<{thr} >= {mins}min(gap{gap})  [网格法] {len(pos):5d} {len(pos)/N:8.2%}")
    # 复刻 s1 buggy 法对比
    bpos=set()
    for pid,g in obs.dropna(subset=["SP02"]).groupby("PID"):
        v=(g["SP02"].values<thr); run=mx=0; gapn=0
        for x in v:
            if x: run+=1; gapn=0; mx=max(mx,run)
            else:
                gapn+=1
                if gapn>gap: run=0
        if mx>=mins: bpos.add(pid)
    print(f"{'   └ s1 当前实现(dropna压缩)':44s} {len(bpos):5d} {len(bpos)/N:8.2%}")

# 每 PID MAP 测量次数分布（决定可用性子集）
m = obs.dropna(subset=["nMAP"]).groupby("PID").size()
print("\n=== 每 PID 的 nMAP 测量次数（OR窗口内）===")
print(m.describe(percentiles=[.05,.25,.5,.75,.95]).round(1))
print("测量次数 <5 的 PID:", (m<5).sum(), f"({(m<5).sum()/N:.1%})")
print("测量次数 >=10 的 PID:", (m>=10).sum(), f"({(m>=10).sum()/N:.1%})")
