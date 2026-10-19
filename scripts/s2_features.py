# -*- coding: utf-8 -*-
"""阶段 2：特征工程（protocol §4）

输入：SIS EMR 九表 + results/s1_anchor.csv（s1 v1.2.0 产出的每 PID 预测锚点）
输出：
  results/s2_features.csv            PID × 特征矩阵（分析队列 17,103 行）
  results/s2_feature_dictionary.json 每个特征的域/来源表/窗口/定义
  results/s2_data_quality.json       各域覆盖率 + 泄漏审计 + 单位异常
  results/s2_procedure_groups.csv    手术分组明细
  results/s2_fuzzy_match_log.csv     模糊兜底命中日志（逐例可审计）

=====================================================================
v1.0.0（2026-10-19）
=====================================================================
【设计纪律】
1. 全部特征必须早于预测锚点 anchor_time。锚点 = 首个 Intubation 事件
   （中位 OR_start+13 min），无 Intubation 者以 Surgery_start 兜底。
   每个域读入后第一件事就是按 `time <= anchor_time` 截断，截断结果写入
   s2_data_quality.json 的 leakage_audit（max_used_time_minus_anchor 必须 <= 0）。
2. 禁止使用任何锚点之后的信息：后续生命体征、后续用药、血气、液体、出血量、
   OR_end/Surgery_end 及其派生量（如 or_min、post_window_minutes）一律不进特征矩阵。
3. 缺失不插补：保留 NaN + 显式缺失指示变量，由 s3 统一插补设计。
4. 手术分组关键词冻结在 config.features.procedure_group_keywords，分组函数在
   _common.assign_procedure_group（与审计脚本 a6 同一实现，单一事实来源）。
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (load_config, paths, log, save_json, require,
                     parse_dt, SIS_NA, DT_ISO, DT_US,
                     assign_procedure_group)

import numpy as np
import pandas as pd

STAGE = "s2"
cfg = load_config(); P = paths(cfg)
RES = P["results_dir"]
EMR = P["sis_emr_dir"]
W = int(cfg["features"]["window_minutes"])          # 预测窗长度（min）
FEATS = []                                           # 特征字典累积
DQ = {}                                              # 数据质量累积


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def _read(name):
    return pd.read_csv(require(os.path.join(EMR, cfg["inputs"][name]), name),
                       na_values=SIS_NA)


def _leak_filter(df, time_col, anchor_df, label):
    """按 time_col <= anchor_time 截断；返回 (截断后 df, 泄漏审计 dict)。

    审计字段 max_used_time_minus_anchor 必须 <= 0，否则说明截断逻辑失效。
    """
    m = df.merge(anchor_df[["PID", "anchor_time"]], on="PID", how="inner")
    m[time_col] = parse_dt(m[time_col])
    m["_tma"] = (m[time_col] - m.anchor_time).dt.total_seconds() / 60.0
    used = m[m._tma <= 0].copy()
    audit = {
        "domain": label,
        "n_rows_merged": int(len(m)),
        "n_rows_after_leak_filter": int(len(used)),
        "n_pids": int(used.PID.nunique()),
        "max_used_time_minus_anchor": (float(used._tma.max()) if len(used) else 0.0),
        "n_time_nat": int(m[time_col].isna().sum()),
    }
    if audit["max_used_time_minus_anchor"] > 0:
        sys.exit(f"[P0-LEAK] {label}: 截断后仍有 {audit['max_used_time_minus_anchor']:.1f} min "
                 f"超出锚点的记录——截断逻辑失效，终止。")
    return used, audit


def _window_slice(df, time_col, anchor_df, label):
    """截断到锚点前 W 分钟窗口 [anchor-W, anchor]；返回 (窗口内 df, 审计 dict)。"""
    used, audit = _leak_filter(df, time_col, anchor_df, label)
    used["_pre_min"] = -used._tma
    win = used[(used._pre_min >= 0) & (used._pre_min <= W)].copy()
    audit["window_minutes"] = W
    audit["n_rows_in_window"] = int(len(win))
    audit["n_pids_in_window"] = int(win.PID.nunique())
    return win, audit


def _stats(win, col, prefix, label, index):
    """窗口内某数值列的 mean/min/max/sd/last/n 六个统计量（按 PID）。"""
    sub = win.dropna(subset=[col])
    if sub.empty:
        return pd.DataFrame(index=index)
    g = sub.groupby("PID")[col]
    out = {
        f"{prefix}_mean": g.mean(), f"{prefix}_min": g.min(),
        f"{prefix}_max": g.max(), f"{prefix}_sd": g.std(), f"{prefix}_n": g.size(),
        f"{prefix}_last": sub.sort_values("Obs_time").groupby("PID")[col].last(),
    }
    for k in out:
        FEATS.append({"feature": k, "domain": label, "source": col,
                      "window": f"[anchor-{W}min, anchor]"})
    return pd.DataFrame({k: v.reindex(index) for k, v in out.items()})


# ================================================================ 0. 锚点与队列
log(STAGE, "读取 s1 锚点产物")
anchor = pd.read_csv(require(os.path.join(RES, "s1_anchor.csv"), "s1_anchor.csv"))
anchor["anchor_time"] = parse_dt(anchor.anchor_time)
anchor = anchor[["PID", "anchor_time", "anchor_source", "anchor_minus_or_start"]].copy()
PIDS = anchor.PID.tolist()
N = len(anchor)
log(STAGE, f"分析队列 n={N}；锚点来源 {anchor.anchor_source.value_counts().to_dict()}")
DQ["cohort"] = {"n_pids": N,
                "anchor_source_counts": anchor.anchor_source.value_counts().to_dict(),
                "anchor_minus_or_start_min": {
                    "p05": float(anchor.anchor_minus_or_start.quantile(.05)),
                    "p50": float(anchor.anchor_minus_or_start.median()),
                    "p95": float(anchor.anchor_minus_or_start.quantile(.95))}}

info = _read("patient_information")
info = info[info.PID.isin(PIDS)].copy()
for c in ["OR_start", "Surgery_start"]:
    info[c] = parse_dt(info[c], fmt=DT_US)
info["or_year"] = info.OR_start.dt.year

feat = anchor.set_index("PID")[["anchor_source", "anchor_minus_or_start"]].copy()
feat["anchor_is_intubation"] = (feat.anchor_source == "Intubation").astype(int)
feat["or_year"] = info.set_index("PID").or_year
FEATS.append({"feature": "anchor_is_intubation", "domain": "anchor",
              "source": "s1_anchor.anchor_source", "window": "at anchor"})
FEATS.append({"feature": "anchor_minus_or_start", "domain": "anchor",
              "source": "anchor_time - OR_start", "window": "at anchor"})
FEATS.append({"feature": "or_year", "domain": "anchor", "source": "OR_start",
              "window": "at anchor"})

# ================================================================ 1. 人口学
log(STAGE, "[1/9] 人口学")
demo = info.set_index("PID")
feat["age"] = _num(demo.Age)
feat["male"] = demo.Gender.fillna("").str.upper().str.startswith("M").astype(int)
# --- 单位错误防护：MOVER 源表的 Ht/Wt 存在单位/录入错误（实测 height 低至 2 cm、
#     weight 高达 839 kg），直接派生会产生 BMI 高达 2.2e5 的荒谬值并污染模型与亚组。
#    成年人合理区间外的取值一律置为缺失（保守，不做臆断填补）。
HT_RANGE, WT_RANGE, BMI_RANGE = (100.0, 220.0), (25.0, 300.0), (10.0, 80.0)
_raw_h = _num(demo.Ht)
_raw_w = _num(demo.Wt)
feat["height_cm"] = _raw_h.where((_raw_h >= HT_RANGE[0]) & (_raw_h <= HT_RANGE[1]))
feat["weight_kg"] = _raw_w.where((_raw_w >= WT_RANGE[0]) & (_raw_w <= WT_RANGE[1]))
_raw_bmi = feat["weight_kg"] / (feat["height_cm"] / 100.0) ** 2
feat["bmi"] = _raw_bmi.where((_raw_bmi >= BMI_RANGE[0]) & (_raw_bmi <= BMI_RANGE[1]))
feat["bmi_missing"] = feat.bmi.isna().astype(int)
for k in ["age", "male", "height_cm", "weight_kg", "bmi"]:
    FEATS.append({"feature": k, "domain": "demographics", "source": "patient_information",
                  "window": "static"})
FEATS.append({"feature": "bmi_missing", "domain": "demographics",
              "source": "derived: bmi isna", "window": "static"})
_n_h_bad = int(((_raw_h < HT_RANGE[0]) | (_raw_h > HT_RANGE[1])).sum())
_n_w_bad = int(((_raw_w < WT_RANGE[0]) | (_raw_w > WT_RANGE[1])).sum())
_n_b_bad = int(((_raw_bmi < BMI_RANGE[0]) | (_raw_bmi > BMI_RANGE[1])).sum())
DQ["demographics"] = {
    "gender_values": {str(k): int(v) for k, v in demo.Gender.value_counts(dropna=False).items()},
    "bmi_computable": int(feat.bmi.notna().sum()),
    "bmi_computable_pct": round(float(feat.bmi.notna().mean()), 4),
    "ht_missing": int(feat.height_cm.isna().sum()),
    "wt_missing": int(feat.weight_kg.isna().sum()),
    "age_missing": int(feat.age.isna().sum()),
    "bmi_implausible_n": _n_b_bad,
    "ht_implausible_n": _n_h_bad,
    "wt_implausible_n": _n_w_bad,
    "plausibility_ranges": {"height_cm": list(HT_RANGE), "weight_kg": list(WT_RANGE),
                            "bmi": list(BMI_RANGE)},
    "note": "Implausible height/weight/BMI (unit-entry errors) set to missing, not imputed.",
}
assert feat["bmi"].dropna().between(*BMI_RANGE).all(), "BMI plausibility filter failed"
assert feat["height_cm"].dropna().between(*HT_RANGE).all(), "height plausibility filter failed"
assert feat["weight_kg"].dropna().between(*WT_RANGE).all(), "weight plausibility filter failed"
log(STAGE, f"  人口学合理性过滤：height 剔除 {_n_h_bad}、weight 剔除 {_n_w_bad}、"
           f"bmi 剔除 {_n_b_bad}（置为缺失，不填补）")

# ================================================================ 2. 手术分组
log(STAGE, "[2/9] 手术分组")
kw = cfg["features"]["procedure_group_keywords"]
groups, fuzzy_log = assign_procedure_group(demo.Procedure, kw, fuzzy=True)
feat["surg_group"] = groups.reindex(feat.index)
for g in list(kw.keys()) + ["OTHER"]:
    feat[f"sg_{g}"] = (feat.surg_group == g).astype(int)
    FEATS.append({"feature": f"sg_{g}", "domain": "surgery", "source": "Procedure keywords",
                  "window": "static"})
FEATS.append({"feature": "surg_group", "domain": "surgery", "source": "Procedure (string)",
              "window": "static"})
DQ["procedure_groups"] = {
    "counts": {str(k): int(v) for k, v in feat.surg_group.value_counts().items()},
    "other_pct": round(float((feat.surg_group == "OTHER").mean()), 4),
    "fuzzy_matched_n": len(fuzzy_log),
}
pd.DataFrame({"PID": feat.index, "surg_group": feat.surg_group.values}).to_csv(
    os.path.join(RES, "s2_procedure_groups.csv"), index=False)
pd.DataFrame(fuzzy_log).to_csv(os.path.join(RES, "s2_fuzzy_match_log.csv"), index=False)

# ================================================================ 3. 麻醉技术事件（仅锚点前）
log(STAGE, "[3/9] 麻醉技术事件（仅锚点前）")
ev = _read("patient_procedure_events")
ev["Event_time"] = parse_dt(ev.Event_time)
ev_used, ev_audit = _leak_filter(ev, "Event_time", anchor, "procedure_events")
DQ["leakage_audit"] = [ev_audit]
ev_names = sorted(ev_used.Event_name.dropna().unique())
for name in ev_names:
    col = "ev_" + "".join(ch if ch.isalnum() else "_" for ch in name).strip("_").lower()
    feat[col] = feat.index.isin(ev_used.loc[ev_used.Event_name == name, "PID"]).astype(int)
    FEATS.append({"feature": col, "domain": "anesthesia_technique",
                  "source": f"patient_procedure_events[{name}]", "window": "<= anchor"})
feat["n_events_pre_anchor"] = feat.index.map(ev_used.groupby("PID").size()).fillna(0).astype(int)
FEATS.append({"feature": "n_events_pre_anchor", "domain": "anesthesia_technique",
              "source": "patient_procedure_events", "window": "<= anchor"})
DQ["anesthesia_technique"] = {
    "n_events_pre_anchor_pids": int(ev_used.PID.nunique()),
    "event_counts_pre_anchor": {str(k): int(v) for k, v in
                                ev_used.Event_name.value_counts().items()},
    "n_pids_without_any_event": int(N - ev_used.PID.nunique()),
}

# ================================================================ 4. NIBP 生命体征（锚点前窗口）
log(STAGE, f"[4/9] NIBP 生命体征（锚点前 {W} min）")
vit = _read("patient_vitals")
vit["Obs_time"] = parse_dt(vit.Obs_time)
for c in ["HRe", "HRp", "nSBP", "nMAP", "nDBP", "SP02"]:
    vit[c] = _num(vit[c])
vit_win, vit_audit = _window_slice(vit, "Obs_time", anchor, "patient_vitals")
DQ["leakage_audit"].append(vit_audit)
SIGMAP = {"nSBP": "sbp", "nMAP": "map", "nDBP": "dbp", "HRe": "hr", "HRp": "hrp", "SP02": "spo2"}
for col, short in SIGMAP.items():
    feat = feat.join(_stats(vit_win, col, short, "vitals_nibp", feat.index))

sub = vit_win.dropna(subset=["nMAP"])
if not sub.empty:
    g = sub.groupby("PID")["nMAP"]
    feat["map_frac_below_65"] = g.apply(lambda s: (s < 65).mean()).reindex(feat.index)
    feat["map_frac_below_55"] = g.apply(lambda s: (s < 55).mean()).reindex(feat.index)
    feat["map_n_below_65"] = g.apply(lambda s: int((s < 65).sum())).reindex(feat.index)
    feat["map_n_below_55"] = g.apply(lambda s: int((s < 55).sum())).reindex(feat.index)
    feat["map_minutes_since_last"] = (-sub.groupby("PID")._tma.max()).reindex(feat.index)

    def _slope(gg):
        gg = gg.dropna(subset=["nMAP"]).sort_values("Obs_time")
        if len(gg) < 3:
            return np.nan
        x = (gg.Obs_time - gg.Obs_time.min()).dt.total_seconds().values / 60.0
        if x.max() <= 0:
            return np.nan
        return float(np.polyfit(x, gg.nMAP.values.astype(float), 1)[0])

    feat["map_slope"] = vit_win.groupby("PID")[["Obs_time", "nMAP"]].apply(_slope).reindex(feat.index)
    for k in ["map_frac_below_65", "map_frac_below_55", "map_n_below_65", "map_n_below_55",
              "map_minutes_since_last", "map_slope"]:
        FEATS.append({"feature": k, "domain": "vitals_nibp_derived", "source": "patient_vitals",
                      "window": f"[anchor-{W}min, anchor]"})
cov = vit_win.groupby("PID").agg(_first=("Obs_time", "min"), _last=("Obs_time", "max"),
                                 _n=("Obs_time", "size"))
feat["vitals_window_actual_min"] = ((cov._last - cov._first).dt.total_seconds() / 60).reindex(feat.index)
feat["vitals_window_n_records"] = cov._n.reindex(feat.index).fillna(0).astype(int)
for k in ["vitals_window_actual_min", "vitals_window_n_records"]:
    FEATS.append({"feature": k, "domain": "qa", "source": "patient_vitals",
                  "window": f"[anchor-{W}min, anchor]"})
DQ["vitals_window"] = {
    "n_pids_with_any_vital": int(vit_win.PID.nunique()),
    "n_pids_no_vital_in_window": int(N - vit_win.PID.nunique()),
    "window_actual_min_p50": float(feat.vitals_window_actual_min.median()),
    "n_records_p50": float(feat.vitals_window_n_records.median()),
    "map_measurements_in_window_p50": float(sub.groupby("PID").size().median()),
    "map_measurements_in_window_p05": float(sub.groupby("PID").size().quantile(.05)),
}

# ================================================================ 5. 有创监测（锚点前窗口）
log(STAGE, f"[5/9] 有创监测（锚点前 {W} min）")
obs = _read("patient_observations")
obs["Obs_time"] = parse_dt(obs.Obs_time)
for c in ["MAP_ART", "SBP_ART", "DBP_ART", "Temp", "CVPm"]:
    obs[c] = _num(obs[c])
obs_win, obs_audit = _window_slice(obs, "Obs_time", anchor, "patient_observations")
DQ["leakage_audit"].append(obs_audit)
feat["has_art_line"] = feat.index.isin(obs_win.loc[obs_win.MAP_ART.notna(), "PID"]).astype(int)
FEATS.append({"feature": "has_art_line", "domain": "invasive_monitoring",
              "source": "patient_observations[MAP_ART]", "window": f"[anchor-{W}min, anchor]"})
for col, short in [("MAP_ART", "art_map"), ("SBP_ART", "art_sbp"), ("DBP_ART", "art_dbp"),
                   ("Temp", "temp"), ("CVPm", "cvp")]:
    feat = feat.join(_stats(obs_win, col, short, "invasive_monitoring", feat.index))
a = obs_win.dropna(subset=["MAP_ART"])
if not a.empty:
    feat["art_map_frac_below_65"] = a.groupby("PID").MAP_ART.apply(
        lambda s: (s < 65).mean()).reindex(feat.index)
    FEATS.append({"feature": "art_map_frac_below_65", "domain": "invasive_monitoring",
                  "source": "patient_observations[MAP_ART]", "window": f"[anchor-{W}min, anchor]"})
DQ["invasive_monitoring"] = {
    "n_pids_with_art_in_window": int(a.PID.nunique()) if not a.empty else 0,
    "art_map_measurements_p50": float(a.groupby("PID").size().median()) if not a.empty else 0.0,
    "temp_coverage_pct": round(float(obs_win.Temp.notna().mean()), 4),
    "cvp_coverage_pct": round(float(obs_win.CVPm.notna().mean()), 4),
}

# ================================================================ 6. 通气与吸入麻醉药（锚点前窗口）
log(STAGE, f"[6/9] 通气与吸入麻醉药（锚点前 {W} min）")
ven = _read("patient_ventilator")
ven["Obs_time"] = parse_dt(ven.Obs_time, fmt=DT_US)
for c in ["Agent_Fi", "Agent_Et", "ETC02", "TV", "RR", "PEEP", "PIP", "FI02"]:
    ven[c] = _num(ven[c])
ven_win, ven_audit = _window_slice(ven, "Obs_time", anchor, "patient_ventilator")
DQ["leakage_audit"].append(ven_audit)
feat["has_vent_record"] = feat.index.isin(ven_win.PID).astype(int)
FEATS.append({"feature": "has_vent_record", "domain": "ventilation",
              "source": "patient_ventilator", "window": f"[anchor-{W}min, anchor]"})
for code, name in [("S", "sevoflurane"), ("N", "nitrous"), ("D", "desflurane"), ("I", "isoflurane")]:
    feat[f"agent_{name}"] = feat.index.isin(ven_win.loc[ven_win.Agent == code, "PID"]).astype(int)
    FEATS.append({"feature": f"agent_{name}", "domain": "ventilation",
                  "source": f"patient_ventilator[Agent={code}]", "window": f"[anchor-{W}min, anchor]"})
for col, short in [("Agent_Fi", "agent_fi"), ("PEEP", "peep"), ("FI02", "fio2"),
                   ("ETC02", "etco2"), ("TV", "tv"), ("RR", "rr"), ("PIP", "pip")]:
    feat = feat.join(_stats(ven_win, col, short, "ventilation", feat.index))
DQ["ventilation"] = {
    "n_pids_with_vent_in_window": int(ven_win.PID.nunique()),
    "agent_counts_in_window": {str(k): int(v) for k, v in
                               ven_win.Agent.value_counts(dropna=False).items()},
    "agent_fi_p50": float(ven_win.Agent_Fi.median()),
}

# ================================================================ 7. 术中用药（仅锚点前）
log(STAGE, "[7/9] 术中用药（仅锚点前）")
med = _read("patient_medication")
med["Start_time"] = parse_dt(med.Start_time, fmt=DT_US)
med["Dose_n"] = _num(med.Dose)
med_used, med_audit = _leak_filter(med, "Start_time", anchor, "patient_medication")
DQ["leakage_audit"].append(med_audit)
med_used["_name"] = med_used.Drug_name.fillna("").str.lower()

DRUGS = [
    ("phenyl",    "phenylephrine",   "mcg"),
    ("ephedrine", "ephedrine",       "mg"),
    ("norepi",    "norepinephrine",  "mcg"),
    ("epi",       "epinephrine",     "mcg"),
    ("vaso",      "vasopressin",     "units"),
    ("dopa",      "dopamine",        None),
    ("atropine",  "atropine",        None),
    ("fentanyl",  "fentanyl",        "mcg"),
    ("sufent",    "sufentanil",      "mcg"),
    ("hydro",     "hydromorphone",   None),
    ("propofol",  "propofol",        "mg"),
    ("midazolam", "midazolam",       "mg"),
    ("dexmed",    "dexmedetomidine", "mcg"),
    ("ketamine",  "ketamine",        None),
    ("nmb",       "rocuronium|vecuronium|cisatracurium|succinylcholine", None),
    ("neostig",   "neostigmine",     None),
]
for key, pat, unit in DRUGS:
    s = med_used[med_used["_name"].str.contains(pat, regex=True, na=False)]
    if s.empty:
        continue
    feat[f"drug_{key}_n"] = feat.index.map(s.groupby("PID").size()).fillna(0).astype(int)
    FEATS.append({"feature": f"drug_{key}_n", "domain": "medication",
                  "source": f"patient_medication[{pat}]", "window": "<= anchor"})
    if unit:
        su = s[s.Drug_units == unit]
        feat[f"drug_{key}_total_{unit}"] = feat.index.map(
            su.groupby("PID").Dose_n.sum()).fillna(0.0)
        FEATS.append({"feature": f"drug_{key}_total_{unit}", "domain": "medication",
                      "source": f"patient_medication[{pat},{unit}]", "window": "<= anchor"})
        if len(su) < len(s):
            DQ.setdefault("medication_unit_mismatch", {})[key] = {
                "pattern": pat, "expected_unit": unit,
                "n_rows_all": int(len(s)), "n_rows_expected_unit": int(len(su)),
                "units_seen": {str(k): int(v) for k, v in s.Drug_units.value_counts().items()}}
vaso_keys = ["phenyl", "ephedrine", "norepi", "epi", "vaso", "dopa"]
feat["vasoactive_n_doses"] = feat[[f"drug_{k}_n" for k in vaso_keys
                                   if f"drug_{k}_n" in feat.columns]].sum(axis=1).astype(int)
FEATS.append({"feature": "vasoactive_n_doses", "domain": "medication_derived",
              "source": "sum of vasoactive n", "window": "<= anchor"})
vs = med_used[med_used["_name"].str.contains(
    "phenylephrine|ephedrine|norepinephrine|epinephrine|vasopressin|dopamine",
    regex=True, na=False)]
if not vs.empty:
    first_vaso = vs.groupby("PID").Start_time.min()
    feat["minutes_to_first_vasoactive"] = (
        (first_vaso - info.set_index("PID").OR_start).dt.total_seconds() / 60).reindex(feat.index)
    FEATS.append({"feature": "minutes_to_first_vasoactive", "domain": "medication_derived",
                  "source": "first vasoactive Start_time - OR_start", "window": "<= anchor"})
DQ["medication"] = {
    "n_pids_with_drug_pre_anchor": int(med_used.PID.nunique()),
    "n_records_pre_anchor": int(len(med_used)),
    "end_time_missing_pct": round(float(_read("patient_medication").End_time.isna().mean()), 4),
    "vasoactive_n_doses_p50": float(feat.vasoactive_n_doses.median()),
}

# ================================================================ 8. 血气（锚点前最后一次）
log(STAGE, "[8/9] 血气（锚点前最后值）")
labs = _read("patient_labs")
labs["Obs_time"] = parse_dt(labs.Obs_time)
ANALYTES = ["Na", "K", "Ca", "Gluc", "Ph", "PCO2", "PO2", "BE", "HCO3", "HgB"]
for c in ANALYTES:
    labs[c] = _num(labs[c])
lab_used, lab_audit = _leak_filter(labs, "Obs_time", anchor, "patient_labs")
DQ["leakage_audit"].append(lab_audit)
if not lab_used.empty:
    last = lab_used.sort_values("Obs_time").groupby("PID").last()
    for c in ANALYTES:
        feat[f"lab_{c.lower()}"] = last[c].reindex(feat.index)
        FEATS.append({"feature": f"lab_{c.lower()}", "domain": "labs",
                      "source": f"patient_labs[{c}] last <= anchor", "window": "<= anchor"})
    feat["has_lab"] = feat.index.isin(lab_used.PID).astype(int)
    feat["lab_n_pre_anchor"] = feat.index.map(lab_used.groupby("PID").size()).fillna(0).astype(int)
    for k in ["has_lab", "lab_n_pre_anchor"]:
        FEATS.append({"feature": k, "domain": "labs", "source": "patient_labs", "window": "<= anchor"})
DQ["labs"] = {
    "n_pids_with_lab_pre_anchor": int(lab_used.PID.nunique()),
    "coverage_pct": round(float(lab_used.PID.nunique() / N), 4),
    "analyte_non_null_in_used": {c: round(float(lab_used[c].notna().mean()), 4) for c in ANALYTES},
}

# ================================================================ 9. 液体与出血（锚点前）
log(STAGE, "[9/9] 液体与出血（锚点前）")
io = _read("patient_input_output")
io["IO_datetime"] = parse_dt(io.IO_datetime)
io["vol"] = _num(io.Volume)
io_used, io_audit = _leak_filter(io, "IO_datetime", anchor, "patient_input_output")
DQ["leakage_audit"].append(io_audit)


def _io_class(t):
    """IO 记录分类。Volume 为负 = 输出（尿液/EBL/引流），为正 = 输入。"""
    tl = str(t).lower()
    if "urine" in tl:
        return "urine"
    if "ebl" in tl or "blood loss" in tl:
        return "ebl"
    if any(k in tl for k in ["prbc", "packed red", "plasma", "platelet", "cryo",
                             "cell saver", "blood"]):
        return "blood"
    if any(k in tl for k in ["albumin", "hetastarch", "dextran"]):
        return "colloid"
    return "other_out"


io_used["_cls"] = io_used.Type.map(_io_class)
if not io_used.empty:
    piv = io_used.pivot_table(index="PID", columns="_cls", values="vol",
                              aggfunc="sum").fillna(0.0)
    rename = {"crystalloid": "crystalloid_in_ml", "colloid": "colloid_in_ml",
              "blood": "blood_products_ml", "urine": "urine_out_ml",
              "ebl": "ebl_ml", "other_out": "other_output_ml"}
    for src, dst in rename.items():
        v = piv[src].reindex(feat.index).fillna(0.0) if src in piv.columns else 0.0
        feat[dst] = -v if dst in ("urine_out_ml", "ebl_ml", "other_output_ml") else v
        FEATS.append({"feature": dst, "domain": "fluids", "source": f"patient_input_output[{src}]",
                      "window": "<= anchor"})
    feat["has_io_record"] = feat.index.isin(io_used.PID).astype(int)
    feat["io_n_records_pre_anchor"] = feat.index.map(
        io_used.groupby("PID").size()).fillna(0).astype(int)
    for k in ["has_io_record", "io_n_records_pre_anchor"]:
        FEATS.append({"feature": k, "domain": "fluids", "source": "patient_input_output",
                      "window": "<= anchor"})
DQ["fluids"] = {
    "n_pids_with_io_pre_anchor": int(io_used.PID.nunique()),
    "coverage_pct": round(float(io_used.PID.nunique() / N), 4),
    "type_counts_pre_anchor": {str(k): int(v) for k, v in
                               io_used.Type.value_counts().head(25).items()},
}

# ================================================================ 落盘
log(STAGE, "组装特征矩阵")
feat = feat.reindex(PIDS)
feat.index.name = "PID"
out_csv = os.path.join(RES, "s2_features.csv")
feat.to_csv(out_csv)
log(STAGE, f"features -> {out_csv}  ({feat.shape[0]} rows x {feat.shape[1]} cols)")

# 守卫：禁止把锚点之后信息带进矩阵
BANNED = {"post_window_minutes", "post_nmap_measurements", "or_min", "surgery_end", "or_end"}
bad = BANNED & set(feat.columns)
if bad:
    sys.exit(f"[P0-LEAK] 特征矩阵含锚点后信息列: {sorted(bad)}")

save_json({"n_features": int(feat.shape[1]), "n_rows": int(feat.shape[0]),
           "window_minutes": W, "features": FEATS},
          os.path.join(RES, "s2_feature_dictionary.json"))

cov_summary = {}
for f in FEATS:
    d = f["domain"]
    if f["feature"] in feat.columns:
        s = feat[f["feature"]]
        cov_summary.setdefault(d, {"n_features": 0, "non_null_pct": []})
        cov_summary[d]["n_features"] += 1
        cov_summary[d]["non_null_pct"].append(round(float(s.notna().mean()), 4))
for d, v in cov_summary.items():
    v["mean_non_null_pct"] = round(float(np.mean(v["non_null_pct"])), 4)
    del v["non_null_pct"]
DQ["domain_coverage"] = cov_summary
DQ["leakage_audit_all_pass"] = all(a["max_used_time_minus_anchor"] <= 0
                                   for a in DQ["leakage_audit"])
save_json(DQ, os.path.join(RES, "s2_data_quality.json"))
log(STAGE, "DONE (v1.0.0)")
