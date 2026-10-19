# -*- coding: utf-8 -*-
"""审计5：时间切分下 train/test 的事件数（用真实可支撑的定义）。"""
import pandas as pd, numpy as np
P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
vit = pd.read_csv(P+"patient_vitals.csv", dtype=str, na_values=["\\N"])
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"]); vit["nMAP"]=pd.to_numeric(vit["nMAP"],errors="coerce")
info = pd.read_csv(P+"patient_information.csv", dtype=str, na_values=["\\N"])
for c in ["OR_start","OR_end"]:
    info[c]=pd.to_datetime(info[c],format="%m/%d/%y %H:%M",errors="coerce")
info["or_min"]=(info.OR_end-info.OR_start).dt.total_seconds()/60
keep=info[(info.or_min>0)&(info.or_min<=1440)].dropna(subset=["OR_start","OR_end"])
obs=vit.merge(keep[["PID","OR_start","OR_end"]],on="PID").query("OR_start<=Obs_time<=OR_end")
nper=obs.groupby("PID").size(); keep=keep[keep.PID.isin(nper[nper>=60].index)]
age=pd.to_numeric(info.set_index("PID")["Age"],errors="coerce")
keep=keep[keep.PID.isin(age[age>=18].index)]
obs=obs[obs.PID.isin(keep.PID)]
keep["year"]=keep.OR_start.dt.year
print("=== 按 OR_start 年份的 PID 分布（分析队列 n=%d）===" % keep.PID.nunique())
print(keep.year.value_counts().sort_index())
print("\n占比:")
print((keep.year.value_counts(normalize=True).sort_index()*100).round(1))

def def_any55(df):
    return set(df.loc[df.nMAP<55,"PID"])
def def_frac65(df):
    pos=set()
    for pid,g in df.dropna(subset=["nMAP"]).groupby("PID"):
        if len(g)>=10 and (g.nMAP<65).mean()>=0.30: pos.add(pid)
    return pos
def def_n3_65_30(df):
    pos=set()
    for pid,g in df.groupby("PID"):
        t=g.loc[g.nMAP<65,"Obs_time"]
        if len(t)<3: continue
        ts=pd.Series(pd.to_datetime(t).values)
        for i in range(len(ts)-2):
            if (ts.iloc[i+2]-ts.iloc[i]).total_seconds()/60<=30: pos.add(pid); break
    return pos

keep_idx = keep.set_index("PID")
print("\n=== 时间切分 train(<=2017-12-31) / test(>=2018-01-01) 事件数 ===")
tr_pids=set(keep_idx.index[keep_idx.OR_start<="2017-12-31"])
te_pids=set(keep_idx.index[keep_idx.OR_start>="2018-01-01"])
print(f"train n={len(tr_pids)}, test n={len(te_pids)}")
for nm,fn in [("任一记录MAP<55",def_any55),("MAP<65占比>=30%(>=10次)",def_frac65),(">=3低值<65/30min",def_n3_65_30)]:
    s=fn(obs)
    a=len(s&tr_pids); b=len(s&te_pids)
    print(f"{nm:26s} train={a:5d}  test={b:4d}   test事件率={b/len(te_pids):.2%}")
    # 粗略 AUPRC CI 宽度示意：b 个事件的 bootstrap
    print(f"{'':26s}   test 事件数 {b} → AUPRC 95%CI 半宽约 ±{1.96*np.sqrt(max(b,1))/max(len(te_pids),1)*100:.2f} 个百分点(患病率尺度)")
