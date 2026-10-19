# -*- coding: utf-8 -*-
"""a6：手术文本关键词分组终版 + s2 各特征域可用性勘察。

背景：SIS `patient_information.Procedure` 是自由文本，19,098/19,114 非空但
17,120 种不同写法（16,446 种仅出现 1 次，含大小写/拼写变体）。
手工逐条映射不可行 → 关键词分组 + 受控模糊兜底（编辑距离<=1 的拼写错误）。

本脚本产出：
  1. 13 个手术分组的覆盖率（全量 19,114 与分析队列两个口径）
  2. 模糊兜底命中日志（每一例可审计：原文/命中 token/命中关键词/分组）
  3. 事件表锚点结构（Intubation/Surgery_start 偏移、越界比例）
  4. ventilator / medication / labs / input_output 四域可用性
"""
import json
import os
import sys

import numpy as np
import pandas as pd

P = "D:/2026.10/Mover数据库/data_raw/_sis_emr_x/EMR/"
NA = ["\\N"]

# ---------------------------------------------------------------- 手术分组（从 config 读取，单一事实来源）
# 关键词映射冻结在 config/config.yaml 的 features.procedure_group_keywords；
# 分组与模糊兜底实现见 _common.assign_procedure_group（与 s2 同一实现）。
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _common import load_config, assign_procedure_group, norm_procedure_text

_CFG = load_config()
GROUPS = _CFG["features"]["procedure_group_keywords"]


def main():
    info = pd.read_csv(P + "patient_information.csv", dtype=str, na_values=NA)
    for c in ["OR_start", "OR_end", "Surgery_start", "Surgery_end"]:
        info[c] = pd.to_datetime(info[c], format="%m/%d/%y %H:%M", errors="coerce")
    txt = info.Procedure.fillna("").str.lower()
    norm = txt.str.replace(r"[^a-z0-9 ]", " ", regex=True).str.replace(r"\s+", " ", regex=True)

    matched, fuzzy_log = assign_procedure_group(norm, GROUPS, fuzzy=True)
    info["surg_group"] = matched.values
    info["fuzzy_kw"] = ""
    for e in fuzzy_log:
        info.loc[info.PID == e["pid"], "fuzzy_kw"] = f"{e['token']}->{e['matched_kw']}({e['group']})"

    print("=" * 72)
    print("=== 1. 手术分组（全量 19,114）===")
    vc = info.surg_group.value_counts()
    print(vc.to_string())
    print(f"OTHER: {(info.surg_group=='OTHER').mean():.2%} ({(info.surg_group=='OTHER').sum()} 例)")
    print(f"模糊兜底命中: {len(fuzzy_log)} 例（详见 s2_fuzzy_match_log.csv）")
    print("\nOTHER 剩余 top20:")
    print(info.loc[info.surg_group == "OTHER", "Procedure"].value_counts().head(20).to_string())

    # 分析队列口径（复刻 s1 排除规则）
    info["or_min"] = (info.OR_end - info.OR_start).dt.total_seconds() / 60
    info["Age_n"] = pd.to_numeric(info.Age, errors="coerce")
    ana = info[(info.or_min > 0) & (info.or_min <= 1440) & (info.Age_n >= 18)]
    print(f"\n=== 分析队列口径（粗算，未含 OR 窗口观测<60 排除，n={len(ana)}）===")
    print(ana.surg_group.value_counts().to_string())

    # ---------------------------------------------------------------- 2. 事件表
    print("\n" + "=" * 72)
    print("=== 2. patient_procedure_events 锚点结构 ===")
    ev = pd.read_csv(P + "patient_procedure_events.csv", na_values=NA)
    ev["Event_time"] = pd.to_datetime(ev.Event_time, errors="coerce")
    print(f"rows={len(ev)} unique_pid={ev.PID.nunique()} Event_time_NaT={ev.Event_time.isna().sum()}")
    print(ev.Event_name.value_counts().to_string())

    j = ev.merge(info[["PID", "OR_start", "OR_end", "Surgery_start"]], on="PID", how="left")
    j["t_from_or"] = (j.Event_time - j.OR_start).dt.total_seconds() / 60
    j["t_to_surg"] = (j.Event_time - j.Surgery_start).dt.total_seconds() / 60
    print("\n-- 相对 OR_start 偏移(min) p05/p50/p95 --")
    print(j.groupby("Event_name")["t_from_or"].agg(
        lambda s: f"{s.quantile(.05):.0f}/{s.quantile(.5):.0f}/{s.quantile(.95):.0f}").to_string())
    print("\n-- 相对 Surgery_start 偏移(min) p05/p50/p95 --")
    print(j.groupby("Event_name")["t_to_surg"].agg(
        lambda s: f"{s.quantile(.05):.0f}/{s.quantile(.5):.0f}/{s.quantile(.95):.0f}").to_string())

    for pat, name in [("ntubation", "Intubation"), ("xtubation", "Extubation")]:
        sub = j[j.Event_name.str.contains(pat, case=False, na=False)]
        if sub.empty:
            continue
        first = sub.sort_values("Event_time").groupby("PID").first()
        inwin = ((first.Event_time >= first.OR_start) & (first.Event_time <= first.OR_end)).mean()
        print(f"\n[{name}] pid={len(first)} rows={len(sub)} 每PID事件数={sub.PID.value_counts().value_counts().to_dict()}")
        print(f"  在[OR_start,OR_end]内: {inwin:.2%} | 晚于Surgery_start: {(first.Event_time>first.Surgery_start).mean():.2%}"
              f" | 相对Surgery_start中位偏移: {first.t_to_surg.median():.0f}min")

    # ---------------------------------------------------------------- 3. 其他四域
    print("\n" + "=" * 72)
    print("=== 3. 其他特征域可用性 ===")

    ven = pd.read_csv(P + "patient_ventilator.csv", na_values=NA)
    ven["Obs_time"] = pd.to_datetime(ven.Obs_time, errors="coerce")
    print(f"\n[ventilator] rows={len(ven)} pid={ven.PID.nunique()}")
    print("  Agent:", ven.Agent.value_counts(dropna=False).head(10).to_dict())
    for c in ["Agent_Fi", "Agent_Et", "ETC02", "TV", "RR", "PEEP", "PIP", "FI02"]:
        v = pd.to_numeric(ven[c], errors="coerce")
        print(f"  {c:9s} 非空率={v.notna().mean():.1%} 中位={v.median():.2f}" if v.notna().any() else f"  {c:9s} 全空")

    med = pd.read_csv(P + "patient_medication.csv", na_values=NA)
    print(f"\n[medication] rows={len(med)} pid={med.PID.nunique()}")
    vc = med.Drug_name.value_counts()
    print(f"  药物种类={med.Drug_name.nunique()}  top25:")
    print(vc.head(25).to_string())

    labs = pd.read_csv(P + "patient_labs.csv", na_values=NA)
    labs["Obs_time"] = pd.to_datetime(labs.Obs_time, errors="coerce")
    print(f"\n[labs] rows={len(labs)} pid={labs.PID.nunique()}")
    analytes = ["Na", "K", "Ca", "Gluc", "Ph", "PCO2", "PO2", "BE", "HCO3", "HgB"]
    for c in analytes:
        v = pd.to_numeric(labs[c], errors="coerce")
        print(f"  {c:5s} 非空率={v.notna().mean():.1%}")

    io = pd.read_csv(P + "patient_input_output.csv", na_values=NA)
    io["IO_datetime"] = pd.to_datetime(io.IO_datetime, errors="coerce")
    print(f"\n[input_output] rows={len(io)} pid={io.PID.nunique()}")
    print("  Type:", io.Type.value_counts(dropna=False).to_string())
    io["Vol_n"] = pd.to_numeric(io.Volume, errors="coerce")
    print(io.groupby("Type", dropna=False)["Vol_n"].agg(["count", "median", "sum"]).round(1).to_string())

    obs = pd.read_csv(P + "patient_observations.csv", na_values=NA)
    print(f"\n[observations] rows={len(obs)} pid={obs.PID.nunique()}  (ART/MAP_ART/SVV/CO/TOF 等)")
    for c in ["MAP_ART", "SBP_ART", "DBP_ART", "SVV", "CO", "TOF", "Temp", "CVPm"]:
        v = pd.to_numeric(obs[c], errors="coerce")
        print(f"  {c:8s} 非空率={v.notna().mean():.2%}")

    # ---------------------------------------------------------------- 落盘
    # 注意：产物用 a6_ 前缀，避免覆盖 s2 的分析队列版本（s2_procedure_groups.csv 仅含 16,861 例）
    out = os.path.dirname(os.path.abspath(__file__)) + "/../results"
    os.makedirs(out, exist_ok=True)
    info[["PID", "Procedure", "surg_group", "fuzzy_kw"]].to_csv(
        os.path.join(out, "a6_procedure_groups_full19114.csv"), index=False)
    pd.DataFrame(fuzzy_log).to_csv(os.path.join(out, "a6_fuzzy_match_log_full19114.csv"), index=False)
    json.dump({k: v for k, v in GROUPS.items()},
              open(os.path.join(out, "a6_procedure_group_keywords_snapshot.json"), "w"),
              ensure_ascii=False, indent=1)
    print("\n落盘: results/a6_procedure_groups_full19114.csv / a6_fuzzy_match_log_full19114.csv / "
          "a6_procedure_group_keywords_snapshot.json")


if __name__ == "__main__":
    main()
