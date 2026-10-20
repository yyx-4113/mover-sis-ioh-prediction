# -*- coding: utf-8 -*-
"""阶段 1：队列构建 + 结局派生（protocol §2-3）
输入：SIS EMR 表
输出：
  results/s1_cohort.json              队列瀑布
  results/s1_outcomes.json            全 OR 窗口结局患病率（描述性口径）
  results/s1_outcomes_postanchor.json 预测锚点后窗口结局患病率（建模口径，防泄漏）
  results/s1_labels.csv               全窗口 PID 级标签 + 首现时刻
  results/s1_labels_postanchor.csv    锚点后窗口标签（s3 建模用）
  results/s1_anchor.csv               每 PID 预测锚点时刻与来源
  results/s1_data_quality.json        点测结构诊断

=====================================================================
v1.1.0 修订（2026-10-19，Round 1 审查 P0 修复）
=====================================================================
【根因】v1.0.0 的 pid_level_hypotension() 用 dropna(subset=[signal]) 删除缺失分钟。
SIS 的 nMAP 是 NIBP 循环点测：全表非空率仅 19.89%，且 96.1% 的连续非空段是
"孤立单分钟"（中位段长 1.0 min）。dropna 把这 80% 的 NaN 分钟物理删除后，
时间轴被压缩约 5×，"连续 5 个低值记录"在压缩数组里成立，在真实时钟上却跨越
20-40 分钟。实测偏差：O1 高估 10.1×、O2 3.9×、O3 14.5×、O4 41.3×。

【修法】两段式：
  (1) 先按 PID 重建完整 1-min 时间网格（date_range(min..max, freq="1min")），
      把已测量分钟填回网格，NaN = 未测量；
  (2) 在网格上判 run。NaN 与 threshold 比较得 False，即"未测量分钟计为中断"，
      这是保守口径（宁可漏检，不虚报）。
      同时提供 sustained_measured 口径作为敏感性分析（仅在已测量分钟上判 run，
      会高估，仅用于量化"点测数据下持续事件不可判定"的程度）。

=====================================================================
v1.2.0 修订（2026-10-19，s2 开工前）
=====================================================================
【新增】预测锚点 + 锚点后标签通道：
  - SIS 无 Induction 事件；Intubation 事件中位位于 OR_start 后约 14 min
    （精确分位数见 results/s1_data_quality.json 的
     anchor_minus_or_start_min.intubation_only_p50），比 Surgery_start 早约 30 min，
    是"诱导结束"的天然锚点（82.0% 病例覆盖）。
    无 Intubation 的病例以 Surgery_start 兜底，anchor_source 逐例记录。
  - 建模标签必须来自锚点之后窗口：若用全 OR 窗口标签，则预测窗（锚点前）的
    低血压已被特征揭示，属目标泄漏。故新增 s1_labels_postanchor.csv。
  - 全窗口标签保留作队列描述（README §4 报的就是这个口径）。

【其他】显式 na_values、非空率守卫、OR 窗口校验、瀑布自洽校验（见 v1.1.0 注记）。
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log, save_json, require

import numpy as np
import pandas as pd

STAGE = "s1"
cfg = load_config(); P = paths(cfg)

# SIS 缺失值是 MySQL 风格 \N；显式声明，防止 "\N" 被当字符串读入
SIS_NA = ["\\N"]
SIGNAL_COL = {"MAP": "nMAP", "SpO2": "SP02"}

# ---------------------------------------------------------------- 读取
info = pd.read_csv(
    require(os.path.join(P["sis_emr_dir"], cfg["inputs"]["patient_information"]), "patient_information"),
    dtype=str, na_values=SIS_NA)
vit = pd.read_csv(
    require(os.path.join(P["sis_emr_dir"], cfg["inputs"]["patient_vitals"]), "patient_vitals"),
    dtype=str, na_values=SIS_NA)
log(STAGE, f"loaded patient_information rows={len(info)} unique_pid={info.PID.nunique()}")
log(STAGE, f"loaded patient_vitals      rows={len(vit)} unique_pid={vit.PID.nunique()}")

# ---------------------------------------------------------------- 时间解析
for c in ["OR_start", "OR_end"]:
    info[c] = pd.to_datetime(info[c], errors="coerce", format="%m/%d/%y %H:%M")
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"], errors="coerce")
for c in ["HRe", "HRp", "nSBP", "nMAP", "nDBP", "SP02"]:
    vit[c] = pd.to_numeric(vit[c], errors="coerce")

# ---------------------------------------------------------------- 数据质量守卫
# v1.1.0 新增：把"README 声称 100% non-null"这类自述变成可证伪的断言。
# 若上游数据被更换/重新导出，此处立即硬失败，而不是静默产出错误结局。
nn = vit[["HRe", "HRp", "nSBP", "nMAP", "nDBP", "SP02"]].notna().mean().round(4).to_dict()
log(STAGE, "列非空率: " + "  ".join(f"{k}={v:.2%}" for k, v in nn.items()))
GUARD = {"nMAP": (0.10, 0.35), "SP02": (0.80, 1.00)}
for col, (lo, hi) in GUARD.items():
    if not (lo <= nn[col] <= hi):
        sys.exit(f"[P0-GUARD] {col} 非空率 {nn[col]:.2%} 超出预期区间 [{lo:.0%}, {hi:.0%}]。"
                 f"这与 2026-10-19 Round 1 实测基线不符——数据可能已被更换或重新导出。"
                 f"请先运行 scripts/audit/a1_vitals_timeline.py 复核，再决定是否更新基线。")

# ---------------------------------------------------------------- 队列瀑布
flow = {"source_pids": int(info.PID.nunique())}
keep = info.dropna(subset=["OR_start", "OR_end"]).copy()
flow["excl_missing_or_window"] = int(info.PID.nunique() - keep.PID.nunique())
flow["or_start_nat"] = int(info.OR_start.isna().sum())
flow["or_end_nat"] = int(info.OR_end.isna().sum())

# v1.1.0 新增：OR 窗口合理性（v1.0.0 无此校验，8/19,114 例 or_min<=0 或 >1440，
# 最大 3,156,668 min ≈ 6 年，会被 OR 窗口过滤静默吞掉）
keep["or_min"] = (keep.OR_end - keep.OR_start).dt.total_seconds() / 60
_max_or = cfg["cohort"].get("max_or_window_minutes", 1440)
implausible = (keep.or_min <= 0) | (keep.or_min > _max_or)
flow["excl_implausible_or_window"] = int(implausible.sum())
flow["implausible_detail"] = {
    "or_min_le_0": int((keep.or_min <= 0).sum()),
    "or_min_gt_1440": int((keep.or_min > 1440).sum()),
    "or_min_max_observed": float(keep.or_min.max()),
}
if implausible.any():
    log(STAGE, f"排除 OR 窗口不合理: {implausible.sum()} 例 "
               f"(<=0min: {(keep.or_min<=0).sum()}, >1440min: {(keep.or_min>1440).sum()}, "
               f"max={keep.or_min.max():.0f}min)")
keep = keep[~implausible].copy()

vit_w = vit.merge(keep[["PID", "OR_start", "OR_end"]], on="PID", how="inner")
vit_w = vit_w[(vit_w.Obs_time >= vit_w.OR_start) & (vit_w.Obs_time <= vit_w.OR_end)]
obs_per_pid = vit_w.groupby("PID").size()
# Round-6 更正：该阈值为 OR 窗内生命体征"记录条数"下限，非分钟数
_pre_short = keep.PID.copy()
keep = keep[keep.PID.isin(obs_per_pid[obs_per_pid >= cfg["cohort"]["min_or_window_records"]].index)]
# Round-6 A3-minor 披露：被"记录条数<60"剔除者中，实际 OR 时长 >=60min（稀疏记录而非短手术）的例数
_excl_short_pids = set(_pre_short) - set(keep.PID)
flow["excl_short_or_window_ge60min_n"] = int(
    (keep.loc[keep.PID.isin(_excl_short_pids), "or_min"] >= 60).sum())
flow["excl_short_or_window"] = int(flow["source_pids"] - flow["excl_missing_or_window"]
                                   - flow["excl_implausible_or_window"] - keep.PID.nunique())

age = pd.to_numeric(info.set_index("PID")["Age"], errors="coerce")
keep = keep[keep.PID.isin(age[(age >= cfg["cohort"]["min_age"])].index)]
flow["excl_underage"] = int(flow["source_pids"] - flow["excl_missing_or_window"]
                            - flow["excl_implausible_or_window"]
                            - flow["excl_short_or_window"] - keep.PID.nunique())
flow["analytic_pids"] = int(keep.PID.nunique())
flow["or_min_median"] = float(keep.or_min.median())
# OR 窗观察数按当前 keep 层计算（此层为 17,103 队列层，尚未做锚点剔除）；
# 最终建模层（16,861）的观察数在锚点守卫后重算并覆写（Round-6 A3-M1 修复：
# 原实现在过滤前取 len(vit_w)，对应 19,106 例层，虚高 5.1%）。
flow["or_window_observations"] = int(vit_w[vit_w.PID.isin(keep.PID)].shape[0])
flow["or_window_observations_layer"] = "cohort_17103_pre_anchor"

# 瀑布自校验：各项之和必须等于源队列
_total = (flow["excl_missing_or_window"] + flow["excl_implausible_or_window"]
          + flow["excl_short_or_window"] + flow["excl_underage"] + flow["analytic_pids"])
if _total != flow["source_pids"]:
    sys.exit(f"[P0-GUARD] 队列瀑布不自洽: 各项之和 {_total} != source_pids {flow['source_pids']}")
log(STAGE, f"瀑布自洽: {flow['excl_missing_or_window']}+{flow['excl_implausible_or_window']}"
           f"+{flow['excl_short_or_window']}+{flow['excl_underage']}+{flow['analytic_pids']} = {_total}")
save_json(flow, os.path.join(P["results_dir"], "s1_cohort.json"))

vit_w = vit_w[vit_w.PID.isin(keep.PID)].copy()

# ---------------------------------------------------------------- 预测锚点（v1.2.0 新增）
# SIS 无 Induction 事件。Intubation 相对 OR_start 的分位数由本脚本计算并写入
# results/s1_data_quality.json（anchor_minus_or_start_min.intubation_only_*；
# Round-6 A3-minor 订正：旧注释"5/13/32"为 a6 审计的陈旧值，实测 6/14/32）。
#   → Intubation 是"诱导结束"的天然锚点；无 Intubation 者以 Surgery_start 兜底。
events = pd.read_csv(
    require(os.path.join(P["sis_emr_dir"], cfg["inputs"]["patient_procedure_events"]),
            "patient_procedure_events"),
    na_values=SIS_NA)
events["Event_time"] = pd.to_datetime(events["Event_time"], errors="coerce",
                                      format="%Y-%m-%d %H:%M:%S")
anchor_cfg = cfg["modeling"].get("anchor_event", "Intubation")
fallback_cfg = cfg["modeling"].get("anchor_fallback", "Surgery_start")

prim = events[events.Event_name.str.contains(anchor_cfg, case=False, na=False)]
prim_first = (prim.dropna(subset=["Event_time"]).sort_values(["PID", "Event_time"])
              .groupby("PID").first()[["Event_time"]].rename(columns={"Event_time": "anchor_event_time"}))

info["Surgery_start"] = pd.to_datetime(info.Surgery_start, errors="coerce", format="%m/%d/%y %H:%M")
anchor = keep[["PID", "OR_start", "OR_end"]].merge(
    info[["PID", "Surgery_start"]], on="PID", how="left").merge(
    prim_first, on="PID", how="left")
anchor["anchor_source"] = np.where(anchor.anchor_event_time.notna(), anchor_cfg, fallback_cfg)
anchor["anchor_time"] = anchor.anchor_event_time.fillna(anchor.Surgery_start)
anchor["anchor_minus_or_start"] = (anchor.anchor_time - anchor.OR_start).dt.total_seconds() / 60
anchor["post_window_minutes"] = (anchor.OR_end - anchor.anchor_time).dt.total_seconds() / 60

# 守卫：锚点必须严格落在 OR 窗口内，否则该病例无法定义预测窗
bad_anchor = (anchor.anchor_time <= anchor.OR_start) | (anchor.anchor_time >= anchor.OR_end) \
             | anchor.anchor_time.isna()
if bad_anchor.any():
    log(STAGE, f"[anchor-guard] {int(bad_anchor.sum())} 例锚点越界，剔除")
    keep = keep[~keep.PID.isin(anchor.PID[bad_anchor])]
    vit_w = vit_w[vit_w.PID.isin(keep.PID)]
    anchor = anchor[~bad_anchor].copy()
flow["excl_bad_anchor"] = int(flow["source_pids"] - flow["excl_missing_or_window"]
                              - flow["excl_implausible_or_window"] - flow["excl_short_or_window"]
                              - flow["excl_underage"] - keep.PID.nunique())
flow["analytic_pids"] = int(keep.PID.nunique())
# 建模层（最终分析队列）OR 窗观察数——锚点守卫后重算（A3-M1 修复）
flow["or_window_observations"] = int(len(vit_w))
flow["or_window_observations_layer"] = "analytic_16861_post_anchor"
flow["anchor_source_counts"] = anchor.anchor_source.value_counts().to_dict()
_total2 = (flow["excl_missing_or_window"] + flow["excl_implausible_or_window"]
           + flow["excl_short_or_window"] + flow["excl_underage"] + flow["excl_bad_anchor"]
           + flow["analytic_pids"])
if _total2 != flow["source_pids"]:
    sys.exit(f"[P0-GUARD] 队列瀑布不自洽(含锚点项): {_total2} != {flow['source_pids']}")
save_json(flow, os.path.join(P["results_dir"], "s1_cohort.json"))
log(STAGE, f"锚点来源: {anchor.anchor_source.value_counts().to_dict()}；分析队列 n={keep.PID.nunique()}")

# 锚点后观测窗（建模口径的生理数据范围）
post_w = vit_w.merge(anchor[["PID", "anchor_time"]], on="PID", how="inner")
post_w = post_w[(post_w.Obs_time >= post_w.anchor_time) & (post_w.Obs_time <= post_w.OR_end)]
log(STAGE, f"锚点后观测 {len(post_w)} 行 / {post_w.PID.nunique()} PID")

# ---------------------------------------------------------------- 结局引擎 v1.1.0
def _grid(values, times, thr):
    """把已测量分钟填回 1-min 网格；返回网格布尔低值数组。

    NaN 与 thr 比较得 False → 未测量分钟计为"非低血压"，即中断。保守口径。
    """
    idx = pd.date_range(times.min(), times.max(), freq="1min")
    s = pd.Series(np.nan, index=idx, dtype="float64")
    s.loc[times] = values
    return (s.values < thr)


def _max_run_with_gap(low, gap):
    """最长 run：连续低血压分钟数，允许至多 gap 个连续非低血压分钟插入。"""
    run = mx = gapn = 0
    for x in low:
        if x:
            run += 1; gapn = 0
            if run > mx: mx = run
        else:
            gapn += 1
            if gapn > gap: run = 0
    return mx


def _first_low_time(values, times, thr):
    """首个低于阈值的已测量分钟（供 s2/s3 做预测窗前泄漏过滤）。"""
    m = values < thr
    return pd.Timestamp(times[m].min()) if m.any() else pd.NaT


def _point_burst_time(values, times, thr, n_points, window_min):
    """满足 '>=n_points 个低值测量落在 window_min 内' 的最早窗口结束时刻。"""
    low_t = np.sort(times[values < thr])
    if len(low_t) < n_points:
        return pd.NaT
    for i in range(len(low_t) - n_points + 1):
        if (low_t[i + n_points - 1] - low_t[i]) / np.timedelta64(1, "m") <= window_min:
            return pd.Timestamp(low_t[i + n_points - 1])
    return pd.NaT


def evaluate(df, d):
    """按定义类型求阳性 PID 集合 + 主事件的首个可判定时刻。

    返回 (positive_pids:set, first_event_times:dict[pid -> Timestamp])
    first_event_times 供 s2/s3 在预测时点前剔除已发生事件（protocol §3 防泄漏）。
    """
    sig = SIGNAL_COL[d["signal"]]
    typ = d["type"]
    pos, first = set(), {}

    for pid, g in df.groupby("PID", sort=False):
        g = g.dropna(subset=[sig])
        if g.empty:
            continue
        vals = g[sig].values.astype(float)
        times = g.Obs_time.values

        if typ == "any_below":
            if (vals < d["threshold"]).any():
                pos.add(pid); first[pid] = _first_low_time(vals, times, d["threshold"])

        elif typ == "sustained_grid":
            # 网格法（v1.1.0 主口径）：NaN 计为中断
            if _max_run_with_gap(_grid(vals, times, d["threshold"]), d["gap_tolerance"]) >= d["minutes"]:
                pos.add(pid); first[pid] = _first_low_time(vals, times, d["threshold"])

        elif typ == "sustained_measured":
            # 敏感性口径：仅在已测量分钟上判 run（会高估，用于量化点测数据的不可判定性）
            if _max_run_with_gap(vals < d["threshold"], d["gap_tolerance"]) >= d["minutes"]:
                pos.add(pid); first[pid] = _first_low_time(vals, times, d["threshold"])

        elif typ == "point_burst":
            t = _point_burst_time(vals, times, d["threshold"], d["n_points"], d["window_minutes"])
            if pd.notna(t):
                pos.add(pid); first[pid] = t

        elif typ == "exposure_fraction":
            if len(g) >= d["min_measurements"] and (vals < d["threshold"]).mean() >= d["fraction"]:
                pos.add(pid); first[pid] = _first_low_time(vals, times, d["threshold"])

        else:
            sys.exit(f"[P0] 未知结局类型: {typ}")

    return pos, first


def _fmt_def(d):
    if d["type"] in ("sustained_grid", "sustained_measured"):
        return f"{d['signal']}<{d['threshold']} x>={d['minutes']}min(gap{d['gap_tolerance']})"
    if d["type"] == "point_burst":
        return f">={d['n_points']}x<{d['threshold']} in {d['window_minutes']}min"
    if d["type"] == "exposure_fraction":
        return f">={d['min_measurements']}meas & <{d['threshold']} >= {d['fraction']:.0%}"
    return f"any<{d['threshold']}"


def _seg_dist(df):
    """连续非空 nMAP 段长分布（诊断点测结构的核心指标）。"""
    v = df.dropna(subset=["nMAP"]).sort_values(["PID", "Obs_time"]).copy()
    if v.empty:
        return {}
    gapflag = v.groupby("PID")["Obs_time"].diff().dt.total_seconds().ne(60)
    v["_g"] = gapflag.cumsum()
    run = v.groupby(["PID", "_g"]).size()
    vc = run.value_counts().sort_index()
    return {"total_segments": int(len(run)),
            "length_1_share": round(float((run == 1).mean()), 4),
            "median_length": float(run.median()),
            "top_lengths": {int(k): int(vv) for k, vv in vc.head(8).items()}}


def _run_pass(df, tag, denom):
    """对一个观测窗跑全部定义，返回 (outcomes_dict, label_cols)。"""
    outcomes, label_cols = {}, {}
    for oid, d in DEFS.items():
        pos, first = evaluate(df, d)
        outcomes[oid] = {
            "definition": d,
            "positive_pids": len(pos),
            "denominator_pids": denom,
            "prevalence": round(len(pos) / max(denom, 1), 4),
            "first_event_times_recorded": len(first),
        }
        label_cols[oid] = (pos, first)
        log(STAGE, f"[{tag}] {oid:4s} {d['signal']:<4s} {d['type']:<19s} {_fmt_def(d):<34s} "
                   f"-> {len(pos):5d}/{denom} = {len(pos)/max(denom,1):6.2%}")
    return outcomes, label_cols


def _write_labels(lab_base, label_cols, path):
    lab = lab_base.copy()
    for oid, (pos, first) in label_cols.items():
        lab[oid] = lab.PID.isin(pos).astype(int)
        lab[f"{oid}_first_time"] = lab.PID.map(first)
    lab.to_csv(path, index=False)
    return lab


DEFS = cfg["outcomes"]["definitions"]
N = int(keep.PID.nunique())
log(STAGE, f"结局引擎 v1.1.0（网格法）开始，共 {len(DEFS)} 个定义，分析队列 n={N}")

# --- 通道 A：全 OR 窗口（描述性口径，README §4 报告用）---
outcomes_full, label_cols_full = _run_pass(vit_w, "full", N)
outcomes_full["primary_id"] = cfg["outcomes"]["primary_id"]
outcomes_full["engine_version"] = "v1.2.0-grid"
outcomes_full["note"] = ("v1.1.0 起 sustained_grid 类型在 1-min 网格上判定，NaN 计为中断。"
                         "v1.0.0 的 dropna 压缩时间轴缺陷已修复，其 MAP 侧数字全部作废。"
                         "本通道为全 OR 窗口口径，仅作队列描述；建模标签见 s1_outcomes_postanchor.json。")
save_json(outcomes_full, os.path.join(P["results_dir"], "s1_outcomes.json"))
_write_labels(keep[["PID"]].copy(), label_cols_full,
              os.path.join(P["results_dir"], "s1_labels.csv"))

# --- 通道 B：锚点后窗口（建模口径，防目标泄漏）---
outcomes_post, label_cols_post = _run_pass(post_w, "post", N)
outcomes_post["primary_id"] = cfg["outcomes"]["primary_id"]
outcomes_post["engine_version"] = "v1.2.0-grid-postanchor"
outcomes_post["anchor_source_counts"] = anchor.anchor_source.value_counts().to_dict()
_intub_med = float(anchor.loc[anchor.anchor_source == "Intubation",
                              "anchor_minus_or_start"].median())
outcomes_post["note"] = (f"标签窗口 = [anchor_time, OR_end]。anchor 默认取首个 Intubation 事件"
                         f"（Intubation 锚点中位 OR_start+{_intub_med:.0f}min），"
                         f"无 Intubation 者以 Surgery_start 兜底。"
                         f"若用全窗口标签，预测窗内的低血压已被特征揭示，属目标泄漏。")
save_json(outcomes_post, os.path.join(P["results_dir"], "s1_outcomes_postanchor.json"))
lab_post = _write_labels(keep[["PID"]].copy(), label_cols_post,
                         os.path.join(P["results_dir"], "s1_labels_postanchor.csv"))

# --- 锚点表 ---
pm = post_w.dropna(subset=["nMAP"]).groupby("PID").size().rename("post_nmap_measurements")
anchor = anchor.merge(pm, on="PID", how="left")
anchor[["PID", "anchor_time", "anchor_source", "anchor_minus_or_start", "post_window_minutes",
        "post_nmap_measurements"]].to_csv(os.path.join(P["results_dir"], "s1_anchor.csv"), index=False)
log(STAGE, "labels_post -> results/s1_labels_postanchor.csv；anchor -> results/s1_anchor.csv")

# ---------------------------------------------------------------- 数据质量诊断
# OR 起点前 30 min 窗口的 nMAP 覆盖（用原始 vitals 表，非 OR 窗过滤后的 vit_w）
_pre_or_map = (vit.merge(keep[["PID", "OR_start"]], on="PID", how="inner"))
_pre_or_map = _pre_or_map[(_pre_or_map.Obs_time >= _pre_or_map.OR_start - pd.Timedelta(minutes=30))
                          & (_pre_or_map.Obs_time < _pre_or_map.OR_start)]
_pre_or_map = _pre_or_map.dropna(subset=["nMAP"])
mcount = vit_w.dropna(subset=["nMAP"]).groupby("PID").size()
cov = vit_w.assign(_h=vit_w.nMAP.notna()).groupby("PID")["_h"].mean()
save_json({
    "column_non_null_rate": nn,
    "nmap_segment_length_distribution": _seg_dist(vit_w),
    "nmap_measurements_per_pid": {
        "mean": float(mcount.mean()), "p05": float(mcount.quantile(.05)),
        "p50": float(mcount.median()), "p95": float(mcount.quantile(.95)),
        "n_lt_5": int((mcount < 5).sum()), "n_ge_10": int((mcount >= 10).sum()),
    },
    "nmap_coverage_per_pid": {"mean": float(cov.mean()), "p50": float(cov.median())},
    "postanchor_nmap_measurements": {
        "mean": float(anchor.post_nmap_measurements.mean()),
        "p05": float(anchor.post_nmap_measurements.quantile(.05)),
        "p50": float(anchor.post_nmap_measurements.median()),
        "p95": float(anchor.post_nmap_measurements.quantile(.95)),
        "n_lt_5": int((anchor.post_nmap_measurements < 5).sum()),
        "n_ge_10": int((anchor.post_nmap_measurements >= 10).sum()),
    },
    "anchor_minus_or_start_min": {
        "p05": float(anchor.anchor_minus_or_start.quantile(.05)),
        "p25": float(anchor.anchor_minus_or_start.quantile(.25)),
        "p50": float(anchor.anchor_minus_or_start.median()),
        "p75": float(anchor.anchor_minus_or_start.quantile(.75)),
        "p95": float(anchor.anchor_minus_or_start.quantile(.95)),
        "intubation_only_p05": float(anchor.loc[anchor.anchor_source == "Intubation",
                                                "anchor_minus_or_start"].quantile(.05)),
        "intubation_only_p50": float(anchor.loc[anchor.anchor_source == "Intubation",
                                                "anchor_minus_or_start"].median()),
        "intubation_only_p95": float(anchor.loc[anchor.anchor_source == "Intubation",
                                                "anchor_minus_or_start"].quantile(.95)),
    },
    "post_window_minutes": {
        "p05": float(anchor.post_window_minutes.quantile(.05)),
        "p50": float(anchor.post_window_minutes.median()),
        "p95": float(anchor.post_window_minutes.quantile(.95)),
    },
    # OR 起点前 30 min 内有无 nMAP 记录（相对阈值定义不可计算的结构性缺口，稿件 Limitation 3）
    "pre_or_window_map_coverage": {
        "window": "[OR_start-30min, OR_start)",
        "n_cases_with_any_map": int(_pre_or_map.PID.nunique()),
        "pct_cases_with_any_map": round(100 * _pre_or_map.PID.nunique() / len(keep), 2),
    },
}, os.path.join(P["results_dir"], "s1_data_quality.json"))
log(STAGE, "DONE (v1.2.0)")
