# -*- coding: utf-8 -*-
"""阶段 2：特征工程（protocol §4）

输入：SIS EMR 九表 + results/s1_anchor.csv（s1 v1.2.0 产出的每 PID 预测锚点）
输出：
  results/s2_features.csv            PID × 特征矩阵（分析队列 16,861 行）
  results/s2_feature_dictionary.json 每个特征的域/来源表/窗口/定义
  results/s2_data_quality.json       各域覆盖率 + 泄漏审计 + 单位异常
  results/s2_procedure_groups.csv    手术分组明细
  results/s2_fuzzy_match_log.csv     模糊兜底命中日志（逐例可审计）

=====================================================================
v1.0.0（2026-10-19）
=====================================================================
【设计纪律】
1. 全部特征必须早于预测锚点 anchor_time。锚点 = 首个 Intubation 事件
   （中位 OR_start 后约 14 min，精确分位数见 s1_data_quality.json
   anchor_minus_or_start_min.intubation_only_p50），无 Intubation 者以
   Surgery_start 兜底。
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
# Round-6 A2-M2：特征窗默认 [anchor-W, anchor] 闭（含锚点分钟）。
# --half-open 生成半开变体 [anchor-W, anchor)（剔除锚点分钟）用于敏感性分析；
# 该变体的全部产物加 _halfopen 后缀，不覆盖主口径文件。
import sys as _sys
HALF_OPEN = "--half-open" in _sys.argv
ANCHOR_INCLUSIVE = not HALF_OPEN
SUFFIX = "_halfopen" if HALF_OPEN else ""
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
    """截断到锚点前 W 分钟窗口；返回 (窗口内 df, 审计 dict)。

    主口径窗为 [anchor-W, anchor]（闭，ANCHOR_INCLUSIVE=True）；
    --half-open 变体为 [anchor-W, anchor)（剔除锚点分钟）。
    audit 记录 n_rows_at_anchor_minute：恰好落在锚点时刻的记录数——
    这些记录同时出现在特征窗与标签窗 [anchor, OR_end] 内（Round-6 披露项）。
    """
    used, audit = _leak_filter(df, time_col, anchor_df, label)
    used["_pre_min"] = -used._tma
    lo = 0 if ANCHOR_INCLUSIVE else np.nextafter(0, 1)   # 半开：严格 >0（即 < anchor）
    win = used[(used._pre_min >= lo) & (used._pre_min <= W)].copy()
    audit["window_minutes"] = W
    audit["window_closed_at_anchor"] = ANCHOR_INCLUSIVE
    audit["n_rows_at_anchor_minute"] = int((used._pre_min == 0).sum())
    audit["n_pids_at_anchor_minute"] = int(used.loc[used._pre_min == 0, "PID"].nunique())
    audit["n_rows_in_window"] = int(len(win))
    audit["n_pids_in_window"] = int(win.PID.nunique())
    # ---- 窗口边界守卫（Round-6 回归教训：'>=' 误写为 '>' 会使主口径静默退化为半开窗，
    #      并让 S2 敏感性分析空跑；此断言两类错误都会立即失败）----
    if ANCHOR_INCLUSIVE:
        if audit["n_rows_at_anchor_minute"] > 0:
            assert float(win._pre_min.min()) == 0.0, \
                f"[P0-WINDOW] {label}: 闭窗未包含锚点分钟（窗内最小 _pre_min=" \
                f"{win._pre_min.min()}）——窗口边界回归，终止。"
    else:
        assert (win._pre_min > 0).all(), f"[P0-WINDOW] {label}: 半开窗包含了锚点分钟，终止。"
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
# Round-6 修复：原实现 `Gender.startswith("M")` 把 4 例 " Unknown" 一律编码为 0（女性），
# 造成 Table 1 女性数（8,502）与特征列 male==0 计数（8,506）矛盾。现按 F/M/未知三态编码，
# 未知留 NaN（树模型原生处理、logistic 由 pipeline 插补），不再静默并入女性。
_g = demo.Gender.fillna("").str.strip().str.upper()
feat["male"] = np.where(_g.str.startswith("M"), 1.0,
                        np.where(_g.str.startswith("F"), 0.0, np.nan))
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
    "male_n": int((feat.male == 1).sum()),
    "female_n": int((feat.male == 0).sum()),
    "sex_unknown_n": int(feat.male.isna().sum()),
    "age_mean": round(float(feat.age.mean()), 2),
    "age_sd": round(float(feat.age.std()), 2),
    "age_median": float(feat.age.median()),
    "age_q1": float(feat.age.quantile(0.25)),
    "age_q3": float(feat.age.quantile(0.75)),
    "age_min": float(feat.age.min()),
    "age_max": float(feat.age.max()),
    "bmi_mean": round(float(feat.bmi.mean()), 2),
    "bmi_sd": round(float(feat.bmi.std()), 2),
    "bmi_median": float(feat.bmi.median()),
    "bmi_q1": float(feat.bmi.quantile(0.25)),
    "bmi_q3": float(feat.bmi.quantile(0.75)),
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
    """IO 记录分类（Round-6 修复）。

    原实现从不返回 "crystalloid"：Plasmalyte/LR/NS/D5W 等晶体液全部落入
    "other_out" 兜底，导致 crystalloid_in_ml 恒为 0，且 other_output_ml
    混入输入容量后被取负（符号反转）。现按 Volume 符号语义 + 关键词分类：
      输出（Volume<0）：urine / ebl / other_out（胃肠引流、胸腔引流、腹水等）
      输入（Volume>0）：blood（血制品）/ colloid（白蛋白、羟乙基淀粉、右旋糖酐）/
                       crystalloid（晶体与糖液）/ tpn_in / medication_iv
    tpn_in 与 medication_iv 为营养/药物类输入，不计入六类液体容量特征，
    仅在 s2_data_quality.json 的 io_classification 披露条数。
    """
    tl = str(t).lower()
    # ---- 输出类 ----
    if "urine" in tl:
        return "urine"
    if "ebl" in tl or "blood loss" in tl:
        return "ebl"
    if any(k in tl for k in ["gastric", "ng tube", "chest tube", "ascites", "drain",
                             "ventriculostomy", "jp drain", "csf", "liposuction"]):
        return "other_out"
    # ---- 输入：血液制品 ----
    if any(k in tl for k in ["prbc", "packed red", "plasma", "platelet", "cryo",
                             "cell saver", "blood"]):
        return "blood"
    # ---- 输入：胶体 ----
    if any(k in tl for k in ["albumin", "hetastarch", "dextran"]):
        return "colloid"
    # ---- 输入：晶体/糖液 ----
    if any(k in tl for k in ["saline", "nacl", "sodium chloride", "ringer", "plasmalyte",
                             "dextrose", "d5", "d10", "ns", "glucose", "mannitol"]):
        return "crystalloid"
    # ---- 输入：营养/药物（不进六类液体容量特征）----
    if "tpn" in tl:
        return "tpn_in"
    return "medication_iv"


io_used["_cls"] = io_used.Type.map(_io_class)
FLUID_OUT = {"urine", "ebl", "other_out"}          # 输出类：求和后取负转正
if not io_used.empty:
    piv = io_used.pivot_table(index="PID", columns="_cls", values="vol",
                              aggfunc="sum").fillna(0.0)
    rename = {"crystalloid": "crystalloid_in_ml", "colloid": "colloid_in_ml",
              "blood": "blood_products_ml", "urine": "urine_out_ml",
              "ebl": "ebl_ml", "other_out": "other_output_ml"}
    sign_violations = {}
    for src, dst in rename.items():
        v = piv[src].reindex(feat.index).fillna(0.0) if src in piv.columns else 0.0
        # 符号守卫：输出类净量应为负、输入类净量应为正；违例条数进 DQ 披露
        if src in piv.columns:
            s = piv[src]
            n_bad = int((s > 0).sum()) if src in FLUID_OUT else int((s < 0).sum())
            if n_bad:
                sign_violations[src] = n_bad
        feat[dst] = -v if src in FLUID_OUT else v
        FEATS.append({"feature": dst, "domain": "fluids", "source": f"patient_input_output[{src}]",
                      "window": "<= anchor"})
    DQ["io_classification"] = {
        "n_records_by_class": {str(k): int(v) for k, v in
                               io_used["_cls"].value_counts().items()},
        "sign_violation_pids": sign_violations,
        "note": ("tpn_in/medication_iv 为营养与药物类输入，不计入六类液体容量特征；"
                 "符号违例 PID 数按类披露（净量与输入/输出语义相反者）。"),
    }
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
out_csv = os.path.join(RES, f"s2_features{SUFFIX}.csv")
feat.to_csv(out_csv)
log(STAGE, f"features -> {out_csv}  ({feat.shape[0]} rows x {feat.shape[1]} cols)")

# 守卫：禁止把锚点之后信息带进矩阵
BANNED = {"post_window_minutes", "post_nmap_measurements", "or_min", "surgery_end", "or_end"}
bad = BANNED & set(feat.columns)
if bad:
    sys.exit(f"[P0-LEAK] 特征矩阵含锚点后信息列: {sorted(bad)}")

save_json({"n_features": int(feat.shape[1]), "n_rows": int(feat.shape[0]),
           "window_minutes": W, "features": FEATS,
           "window_closed_at_anchor": ANCHOR_INCLUSIVE},
          os.path.join(RES, f"s2_feature_dictionary{SUFFIX}.json"))

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
save_json(DQ, os.path.join(RES, f"s2_data_quality{SUFFIX}.json"))
log(STAGE, f"DONE (v1.0.0{'; half-open anchor variant' if HALF_OPEN else ''})")
