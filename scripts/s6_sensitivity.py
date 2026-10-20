# -*- coding: utf-8 -*-
"""阶段 6：Round-6 敏感性分析集（review/REVIEW_round6_2026-10-20 必修清单）

S1 限定队列（≥10 次锚点后 MAP，15,365 例）
   —— 排除 negative-by-construction（NBC）MNAR 机制：164 例计数不确定 +
      1,332 例 1–9 次读数。主分析的全部指标在该队列上重算（A2-M4 评为
      "single most valuable missing analysis"）。
S2 半开特征窗 [anchor-15, anchor)
   —— 剔除锚点分钟读数，消标签-特征边界重叠（A2-M2）。依赖
      `python scripts/s2_features.py --half-open` 预生成的 s2_features_halfopen.csv。
S3 外部绝对时间结局（VitalDB 1-min 网格）
   —— 回应 A1-SEVERE-2：外部 "D1" 按原始采样比例计算（≈30 样本/min），
      与 MOVER 的点测比例不是同一终点。本分析在 VitalDB 上按 1-min 网格
      （镜像 s1_cohort.py _grid 约定：分钟值取该分钟最后样本，未测分钟=NaN=非低值）
      重算多档标签，并评估**已运输的既有预测**在各标签下的表现，量化患病率差距中
      有多少来自结局定义而非病例组合。
S4 外部校准（已运输模型）
   —— logit 尺度斜率/截距、calibration-in-the-large、十分位表（A1-SEVERE-4）。
S5 外部漏斗 6,388→3,735
   —— 各层排除原因与例数（A4-F2 审计链缺口）。
S6 生理学子集运输
   —— 剔除全部节律/密度特征（*_n、map_n_below_*、map_minutes_since_last、
      vitals_window_*、anchor_is_intubation、anchor_minus_or_start、or_year）后，
      无改动模型外运（A2-M6/A1-M3：这些特征在 VitalDB 支持度为 0 或分布外越）。
S7 锚点分钟重叠量化
   —— 特征窗闭区间导致的标签-特征边界重叠规模 + 标签侧改用 (anchor, OR_end]
      后的阳性翻转数（A2-M2 影响量化）。

输出：results/s6_sensitivity.json（s4_report.py 将其并入审计追踪表）
"""
import os
import sys
import json
import gzip
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log, save_json, parse_dt

import numpy as np
import pandas as pd
from sklearn.model_selection import (train_test_split, StratifiedKFold,
                                     cross_val_predict)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (average_precision_score, roc_auc_score,
                             brier_score_loss)
from sklearn.isotonic import IsotonicRegression
import xgboost as xgb

warnings.filterwarnings("ignore")
STAGE = "s6"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = load_config(); P = paths(cfg); RES = P["results_dir"]
EMR = P["sis_emr_dir"]
VDATA = os.path.join(ROOT, "data_vitaldb")
TRK = os.path.join(VDATA, "tracks")

seed = int(cfg["modeling"]["seed"])
n_boot = int(cfg["modeling"]["bootstrap_resamples"])
PRIMARY = cfg["outcomes"]["primary_id"]

# XGB 超参镜像 scripts/s3_models.py v1.0.0（Round-6 插补修复版）
XGB_KW = dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
              colsample_bytree=0.8, min_child_weight=10, reg_lambda=1.0,
              n_jobs=-1, random_state=seed, eval_metric="logloss")

OUT = {"stage": STAGE, "version": "v1.0.0-round6", "seed": seed,
       "note": "Round-6 敏感性分析集；S1/S2/S6b 复刻 s3 协议（同种子/同超参/同切分）"}


# ================================================================ 协议工具（镜像 s3）
def boot_ci(y_true, y_pred, fn, B=n_boot):
    rng = np.random.default_rng(seed)
    yt, yp = np.asarray(y_true), np.asarray(y_pred)
    n = len(yt); idx = np.arange(n); vals = []
    for _ in range(B):
        s = rng.choice(idx, size=n, replace=True)
        if yt[s].sum() == 0:
            continue
        vals.append(fn(yt[s], yp[s]))
    if not vals:
        return [None, None]
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return [float(lo), float(hi)]


def fit_eval(make_model, Xtr, ytr, Xte, yte, name, split):
    model = make_model()
    model.fit(Xtr, ytr)
    p = model.predict_proba(Xte)[:, 1]
    rec = dict(model=name, split=split, n_train=len(ytr), n_test=len(yte),
               n_pos_test=int(yte.sum()), auprc=round(average_precision_score(yte, p), 4),
               auprc_ci95=boot_ci(yte, p, average_precision_score),
               auroc=round(roc_auc_score(yte, p), 4),
               auroc_ci95=boot_ci(yte, p, roc_auc_score),
               brier=round(brier_score_loss(yte, p), 4),
               pred_mean=round(float(p.mean()), 4))
    return rec, model, p


def run_cohort(X, y, year, tag):
    """患者级（主）+ 时间（次）双切分，XGBoost（含 OOF isotonic 校准）与 logistic_full。"""
    out = {"tag": tag, "n": int(len(y)), "n_pos": int(y.sum()),
           "prevalence": round(float(y.mean()), 4), "results": []}
    ridx, teidx = train_test_split(X.index, test_size=0.2, random_state=seed, stratify=y)
    tr_mask = (year <= 2017).values
    te_mask = (year == 2018).values
    ridx_t, teidx_t = X.index[tr_mask], X.index[te_mask]
    for split, tr_i, te_i in [("patient", ridx, teidx), ("temporal", ridx_t, teidx_t)]:
        Xtr, Xte = X.loc[tr_i], X.loc[te_i]
        ytr, yte = y.loc[tr_i], y.loc[te_i]
        if ytr.sum() == 0 or yte.sum() == 0:
            log(STAGE, f"[{tag}/{split}] 训练或测试无阳性，跳过")
            continue
        spw = max(1.0, (ytr == 0).sum() / max(1, (ytr == 1).sum()))
        logit = Pipeline([
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])
        rec, _, _ = fit_eval(lambda: logit, Xtr, ytr, Xte, yte, "logistic_full", split)
        out["results"].append(rec)
        rec_x, xm, px = fit_eval(
            lambda: xgb.XGBClassifier(scale_pos_weight=spw, **XGB_KW),
            Xtr, ytr, Xte, yte, "xgboost", split)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        oof = cross_val_predict(xgb.XGBClassifier(scale_pos_weight=spw, **XGB_KW),
                                Xtr, ytr, cv=skf, method="predict_proba")[:, 1]
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(oof, ytr)
        pc = iso.predict(px)
        rec_x["auprc_cal"] = round(average_precision_score(yte, pc), 4)
        rec_x["auroc_cal"] = round(roc_auc_score(yte, pc), 4)
        rec_x["brier_cal"] = round(brier_score_loss(yte, pc), 4)
        rec_x["pred_mean_cal"] = round(float(pc.mean()), 4)
        out["results"].append(rec_x)
        log(STAGE, f"[{tag}/{split}] n={len(yte)} pos={int(yte.sum())} "
                   f"XGB AUPRC={rec_x['auprc']} AUROC={rec_x['auroc']} "
                   f"(cal {rec_x['auprc_cal']}/{rec_x['auroc_cal']})")
    return out


def load_matrix(path):
    feat = pd.read_csv(path).set_index("PID")
    obj = feat.select_dtypes(include="object").columns.tolist()
    return feat.drop(columns=obj), obj


# ================================================================ 0. 公共载入
log(STAGE, "载入主产物")
feat, obj_cols = load_matrix(os.path.join(RES, "s2_features.csv"))
lab = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")
anchor = pd.read_csv(os.path.join(RES, "s1_anchor.csv")).set_index("PID")
y_all = lab[PRIMARY].astype(int)
common = feat.index.intersection(lab.index)
feat, y_all = feat.loc[common], y_all.loc[common]
year = feat["or_year"].astype(int)
nmap = anchor["post_nmap_measurements"]

# ================================================================ S1 限定队列
log(STAGE, "S1 限定队列（≥10 次锚点后 MAP）")
elig = nmap.reindex(feat.index) >= 10
X1, y1 = feat[elig], y_all[elig]
log(STAGE, f"S1 队列 n={len(y1)} 阳性={int(y1.sum())} 患病率={y1.mean()*100:.2f}%")
OUT["S1_restricted_cohort"] = run_cohort(X1, y1, year[elig], "S1_evaluable")
OUT["S1_restricted_cohort"]["excluded_nbc_n"] = int((~elig).sum())
OUT["S1_restricted_cohort"]["excluded_nbc_breakdown"] = {
    "n_1_to_9_readings": int(((nmap.reindex(feat.index) >= 1) & (nmap.reindex(feat.index) < 10)).sum()),
    "n_indeterminate": int(nmap.reindex(feat.index).isna().sum()),
}

# ================================================================ S2 半开特征窗
ho_path = os.path.join(RES, "s2_features_halfopen.csv")
if os.path.exists(ho_path):
    log(STAGE, "S2 半开特征窗 [anchor-15, anchor)")
    feat_ho, obj_ho = load_matrix(ho_path)
    common_ho = feat_ho.index.intersection(lab.index)
    X2, y2 = feat_ho.loc[common_ho], y_all.loc[common_ho]
    year2 = X2["or_year"].astype(int)
    OUT["S2_half_open_window"] = run_cohort(X2, y2, year2, "S2_halfopen")
    OUT["S2_half_open_window"]["window"] = "[anchor-15min, anchor)"
else:
    log(STAGE, "S2 跳过：未找到 s2_features_halfopen.csv"
              "（请先运行 python scripts/s2_features.py --half-open）")
    OUT["S2_half_open_window"] = {"error": "s2_features_halfopen.csv not found"}

# ================================================================ S3 外部绝对时间结局
log(STAGE, "S3 外部绝对时间结局（VitalDB 1-min 网格）")
PHYS_MAP = (20.0, 250.0)          # 镜像 ext_build.PHYS['map']


def load_map_track(cid):
    p = os.path.join(TRK, "map", f"{cid}.csv.gz")
    if not os.path.exists(p) or os.path.getsize(p) < 50:
        return None
    try:
        with gzip.open(p, "rt") as f:
            df = pd.read_csv(f)
    except Exception:
        return None
    if df is None or df.shape[1] < 2 or df.shape[0] == 0:
        return None
    t = pd.to_numeric(df.iloc[:, 0], errors="coerce").values.astype(float)
    v = pd.to_numeric(df.iloc[:, 1], errors="coerce").values.astype(float)
    m = np.isfinite(v) & (v > 0) & (v >= PHYS_MAP[0]) & (v <= PHYS_MAP[1])
    return t[m], v[m]


def grid_labels(t, v, opstart, opend, thr=65.0):
    """1-min 网格（镜像 s1_cohort._grid：分钟值取该分钟最后样本；未测分钟=NaN=非低值）。

    返回 dict：n_valid_minutes, n_low_minutes, frac_low_minutes
    """
    m = (t >= opstart) & (t <= opend)
    t, v = t[m], v[m]
    if len(t) == 0:
        return {"n_valid": 0, "n_low": 0, "frac_low": 0.0}
    dur = opend - opstart
    n_min = int(np.floor(dur / 60.0)) + 1
    minute_idx = np.floor((t - opstart) / 60.0).astype(int)
    keep = (minute_idx >= 0) & (minute_idx < n_min)
    minute_idx, v_min = minute_idx[keep], v[keep]
    if len(minute_idx) == 0:
        return {"n_valid": 0, "n_low": 0, "frac_low": 0.0}
    # 最后样本胜出（与 s1 s.loc[times]=values 语义一致）
    last_val = pd.Series(v_min).groupby(minute_idx).last()
    n_valid = int(len(last_val))
    n_low = int((last_val < thr).sum())
    return {"n_valid": n_valid, "n_low": n_low,
            "frac_low": (n_low / n_valid) if n_valid else 0.0}


vl = pd.read_csv(os.path.join(RES, "ext", "vitaldb_labels.csv"))
vp = pd.read_csv(os.path.join(RES, "ext", "vitaldb_predictions.csv"))
vp = vp.set_index("caseid")
rows = []
for _, r in vl.iterrows():
    cid = int(r["caseid"]); opstart = float(r["opstart"]); opend = float(r["opend"])
    mv = load_map_track(cid)
    if mv is None:
        rows.append({"caseid": cid, "n_valid": 0, "n_low": 0, "frac_low": 0.0})
        continue
    rows.append({"caseid": cid, **grid_labels(mv[0], mv[1], opstart, opend)})
gl = pd.DataFrame(rows).set_index("caseid")
gl["D1_samples"] = vl.set_index("caseid")["D1"].reindex(gl.index).astype(int)
gl["n_post_map"] = vl.set_index("caseid")["n_post_map"].reindex(gl.index)
gl["p"] = vp["p"].reindex(gl.index)
# 标签变体（全部要求 ≥10 有效分钟，与 MOVER D1 的 ≥10 次读数门槛平行）
gl["D1_grid_30pct"] = ((gl.n_valid >= 10) & (gl.frac_low >= 0.30)).astype(int)
for k in (10, 20, 30, 60):
    gl[f"D1_abs{k}min"] = (gl.n_low >= k).astype(int)
# 既有预测在各标签下的表现（模型未改动，仅换结局）


def eval_pred(y_true, p):
    y_true = np.asarray(y_true).astype(int); p = np.asarray(p, dtype=float)
    ok = np.isfinite(p)
    y_true, p = y_true[ok], p[ok]
    if y_true.sum() == 0 or len(set(y_true.tolist())) < 2:
        return {"auroc": None, "auprc": None, "n": int(len(y_true)),
                "n_pos": int(y_true.sum())}
    return {"n": int(len(y_true)), "n_pos": int(y_true.sum()),
            "prevalence": round(float(y_true.mean()), 4),
            "auroc": round(roc_auc_score(y_true, p), 4),
            "auroc_ci95": boot_ci(y_true, p, roc_auc_score),
            "auprc": round(average_precision_score(y_true, p), 4),
            "auprc_ci95": boot_ci(y_true, p, average_precision_score),
            "brier": round(brier_score_loss(y_true, p), 4),
            "pred_mean": round(float(p.mean()), 4)}


label_variants = ["D1_samples", "D1_grid_30pct", "D1_abs10min",
                  "D1_abs20min", "D1_abs30min", "D1_abs60min"]
OUT["S3_external_time_labels"] = {
    "definition_note": ("D1_samples=已运输口径（≥10 个原始样本且 <65 样本占比≥30%，"
                        "VitalDB 约 30 样本/min）；网格变体在 [opstart,opend] 1-min 网格上"
                        "计算（分钟值=该分钟最后样本，未测分钟计非低值，镜像 s1_cohort._grid）；"
                        "abs 变体=累积低值分钟数绝对值门槛。预测为已运输的 53 特征模型，未改动。"),
    "n_zero_post_map_cases": int((gl.n_post_map == 0).sum()),
    "n_zero_valid_minutes": int((gl.n_valid == 0).sum()),
    "median_n_valid_minutes": float(gl.n_valid.median()),
    "median_post_window_minutes": float(
        (vl.set_index("caseid")["opend"] - vl.set_index("caseid")["opstart"]).median() / 60.0),
    "variants": {k: eval_pred(gl[k], gl["p"]) for k in label_variants},
}
gl.to_csv(os.path.join(RES, "s6_external_grid_labels.csv"))
log(STAGE, "S3 完成 -> results/s6_external_grid_labels.csv")

# ================================================================ S4 外部校准
log(STAGE, "S4 外部校准（已运输模型，未重校准）")
yv = vp["y"].astype(int).values
pv = vp["p"].astype(float).values
_p = np.clip(pv, 1e-6, 1 - 1e-6)
_lr = LogisticRegression(C=1e10, max_iter=2000)
_lr.fit(np.log(_p / (1 - _p)).reshape(-1, 1), yv)
slope_logit = float(_lr.coef_[0][0]); intercept_logit = float(_lr.intercept_[0])
sl_l, ic_l = np.polyfit(pv, yv, 1)
dec = pd.DataFrame({"p": pv, "y": yv})
dec["bin"] = pd.qcut(dec["p"], 10, duplicates="drop")
decile = dec.groupby("bin", observed=True).agg(
    n=("y", "size"), mean_pred=("p", "mean"), obs=("y", "mean")).reset_index(drop=True)
OUT["S4_external_calibration"] = {
    "model": " transported 53-feature XGBoost (unrefitted)",
    "n": int(len(yv)), "n_pos": int(yv.sum()),
    "prevalence": round(float(yv.mean()), 4),
    "pred_mean": round(float(pv.mean()), 4),
    "calibration_in_the_large": round(float(pv.mean() - yv.mean()), 4),
    "brier": round(brier_score_loss(yv, pv), 4),
    "calib_slope_logit": round(slope_logit, 4),
    "calib_intercept_logit": round(intercept_logit, 4),
    "calib_slope_probability_lpm": round(float(sl_l), 4),
    "calib_intercept_probability_lpm": round(float(ic_l), 4),
    "deciles": decile.round(4).to_dict("records"),
    "note": ("内部 isotonic 校准（Brier 0.1905→0.1190）从未被运输；外运的是未校准模型。"
             "slope<1 表示预测范围过宽（过分散），intercept 与 in-the-large 显示系统性高估。"),
}
log(STAGE, f"S4 slope_logit={slope_logit:.3f} itl={pv.mean()-yv.mean():+.3f}")

# ================================================================ S5 外部漏斗
log(STAGE, "S5 外部漏斗")
trks = pd.read_csv(os.path.join(VDATA, "trks.csv"))
art = trks[trks.tname.isin(["Solar8000/ART_MBP", "EV1000/ART_MBP"])]
n_art = int(art.caseid.nunique())
cases = pd.read_csv(os.path.join(VDATA, "cases.csv"))
n_all = int(len(cases))
OUT["S5_external_funnel"] = {
    "n_vitaldb_cases_with_vitals": n_all,
    "n_with_art_map_track": n_art,
    "n_without_art_map_track": n_all - n_art,
    "n_with_valid_op_timing": int(((cases.opstart > 0) & (cases.opend > cases.opstart)).sum()),
    "n_final_label_cohort": int(len(vl)),
    "n_zero_post_map": int((gl.n_post_map == 0).sum()),
    "n_d1_positive": int(vl.D1.sum()),
    "note": ("漏斗口径：VitalDB 全部病例 → 有创动脉 MAP 轨 → 有效 opstart/opend → "
             "标签队列。零 MAP 轨后读数者在 [opstart,opend] 内无 ART_MBP 样本，"
             "按构造为阴性（与 214 例阳性数纯属巧合，正文须并排披露）。"),
}

# ================================================================ S6 生理学子集运输
log(STAGE, "S6 生理学子集运输")
core = json.load(open(os.path.join(RES, "ext", "core_cols.json")))
DEMO = ["age", "male", "height_cm", "weight_kg", "bmi", "bmi_missing"]
STAT = [f"{s}_{st}" for s in ("sbp", "map", "dbp", "hr", "hrp", "spo2")
        for st in ("mean", "min", "max", "sd", "last")]
EXTRA = ["map_frac_below_65", "map_frac_below_55", "map_slope"]
PHYSIO = [c for c in (DEMO + STAT + EXTRA) if c in core]
DROPPED = [c for c in core if c not in PHYSIO]
Xp = feat[PHYSIO]
yp = y_all
spw_full = max(1.0, (yp == 0).sum() / max(1, (yp == 1).sum()))
xgb_full = xgb.XGBClassifier(scale_pos_weight=spw_full, **XGB_KW)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
oof = cross_val_predict(xgb.XGBClassifier(scale_pos_weight=spw_full, **XGB_KW),
                        Xp.values, yp.values, cv=skf, method="predict_proba")[:, 1]
iso_full = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(oof, yp.values)
xgb_full.fit(Xp.values, yp.values)
oof_auprc = average_precision_score(yp, oof); oof_auroc = roc_auc_score(yp, oof)
vf = pd.read_csv(os.path.join(RES, "ext", "vitaldb_features.csv")).set_index("caseid")
p_ext_raw = xgb_full.predict_proba(vf[PHYSIO].values)[:, 1]
p_ext_cal = iso_full.predict(p_ext_raw)
vpred = pd.DataFrame({"y": vp["y"].astype(int), "p": vp["p"]})
vpred["p_physio"] = pd.Series(p_ext_raw, index=vf.index).reindex(vpred.index)
vpred["p_physio_cal"] = pd.Series(p_ext_cal, index=vf.index).reindex(vpred.index)
s6_ext = eval_pred(vpred["y"], vpred["p_physio"])
s6_ext_cal = eval_pred(vpred["y"], vpred["p_physio_cal"])
# 内部患者级切分对照（同 S1/S2 协议）
s6_int = run_cohort(Xp, yp, year, "S6_physio_internal")
OUT["S6_physiological_subset"] = {
    "n_physio_features": len(PHYSIO),
    "dropped_features": DROPPED,
    "internal_full_cohort_oof": {"auprc": round(float(oof_auprc), 4),
                                 "auroc": round(float(oof_auroc), 4)},
    "internal_patient_split": s6_int,
    "external_unrefitted_raw": s6_ext,
    "external_unrefitted_calibrated": s6_ext_cal,
    "external_shipped_53feat_reference": eval_pred(vpred["y"], vpred["p"]),
    "note": ("生理学子集=六信号 mean/min/max/sd/last + map_frac_below_65/55 + map_slope + "
             "人口学（共 %d 个）。剔除的 %d 个特征为节律/密度/计时代理（*_n、map_n_below_*、"
             "map_minutes_since_last、vitals_window_*、anchor_is_intubation、"
             "anchor_minus_or_start、or_year）——这些特征在 VitalDB 的支持度为 0 或分布外越。"
             % (len(PHYSIO), len(DROPPED))),
}
log(STAGE, f"S6 physio n={len(PHYSIO)} ext AUROC={s6_ext.get('auroc')} "
           f"(53feat ref {OUT['S6_physiological_subset']['external_shipped_53feat_reference'].get('auroc')})")

# ================================================================ S7 锚点分钟重叠
log(STAGE, "S7 锚点分钟重叠量化")
vit = pd.read_csv(os.path.join(EMR, "patient_vitals.csv"),
                  usecols=lambda c: c in ("PID", "Obs_time", "nMAP"))
vit["Obs_time"] = pd.to_datetime(vit["Obs_time"], errors="coerce")
vit["nMAP"] = pd.to_numeric(vit["nMAP"], errors="coerce")
anc = anchor[["anchor_time", "anchor_minus_or_start"]].copy()
anc["anchor_time"] = pd.to_datetime(anc["anchor_time"], errors="coerce")
m = vit.merge(anc, left_on="PID", right_index=True, how="inner")
at_anchor = m[m.Obs_time == m.anchor_time]
n_cases_at_anchor = int(at_anchor.PID.nunique())
below_at_anchor = at_anchor[at_anchor.nMAP < 65]
n_cases_at_anchor_below = int(below_at_anchor.PID.nunique())
d1pos = set(y_all[y_all == 1].index)
n_d1pos_with_anchor_reading = int(at_anchor[at_anchor.PID.isin(d1pos)].PID.nunique())
n_d1pos_anchor_below = int(below_at_anchor[below_at_anchor.PID.isin(d1pos)].PID.nunique())
# 标签侧改用 (anchor, OR_end]（严格晚于锚点）后的阳性翻转
strict = m[m.Obs_time > m.anchor_time]
g = strict.dropna(subset=["nMAP"]).groupby("PID")
n_strict = g.size()
frac_strict = g["nMAP"].apply(lambda s: (s < 65).mean())
d1_strict = ((n_strict >= 10) & (frac_strict >= 0.30)).astype(int)
d1_strict = d1_strict.reindex(feat.index).fillna(0).astype(int)
flip_pos_to_neg = int(((y_all == 1) & (d1_strict == 0)).sum())
flip_neg_to_pos = int(((y_all == 0) & (d1_strict == 1)).sum())
n_d1_strict = int(d1_strict.sum())
OUT["S7_anchor_minute_overlap"] = {
    "n_cases_with_map_exactly_at_anchor": n_cases_at_anchor,
    "pct_cases_with_map_exactly_at_anchor": round(100 * n_cases_at_anchor / len(feat), 2),
    "n_cases_anchor_map_below_65": n_cases_at_anchor_below,
    "n_d1_positive_with_anchor_reading": n_d1pos_with_anchor_reading,
    "n_d1_positive_anchor_reading_below_65": n_d1pos_anchor_below,
    "label_window_strict_variant": {
        "window": "(anchor, OR_end]",
        "n_positive": n_d1_strict,
        "prevalence_pct": round(100 * n_d1_strict / len(feat), 2),
        "flip_positive_to_negative": flip_pos_to_neg,
        "flip_negative_to_positive": flip_neg_to_pos,
        "net_change": n_d1_strict - int(y_all.sum()),
    },
    "note": ("特征窗 [anchor-15, anchor] 与标签窗 [anchor, OR_end] 均为闭区间，"
             "锚点分钟读数同时进入两侧。S2 从特征侧剔除锚点分钟；此处量化标签侧"
             "改用严格开窗的影响（翻转数）。"),
}
log(STAGE, f"S7 anchor-minute cases={n_cases_at_anchor} "
           f"D1+ 含锚点读数={n_d1pos_with_anchor_reading}；"
           f"标签严格窗翻转 +→-={flip_pos_to_neg} -→+={flip_neg_to_pos}")

# ================================================================ S8 记录密度（病例分钟口径）
log(STAGE, "S8 记录密度（病例分钟口径，Round-6 A3-minor 订正稿件措辞）")
info = pd.read_csv(os.path.join(EMR, "patient_information.csv"))
info = info[info.PID.isin(feat.index)].copy()
for _c in ["OR_start", "OR_end"]:
    info[_c] = parse_dt(info[_c], fmt="%m/%d/%y %H:%M")
info["or_min"] = (info.OR_end - info.OR_start).dt.total_seconds() / 60
info = info[(info.or_min > 0) & (info.or_min <= 1440)]
vit2 = pd.read_csv(os.path.join(EMR, "patient_vitals.csv"),
                   usecols=lambda c: c in ("PID", "Obs_time", "nMAP"))
vit2["Obs_time"] = parse_dt(vit2["Obs_time"])
vit2["nMAP"] = pd.to_numeric(vit2["nMAP"], errors="coerce")
mw = vit2.merge(info[["PID", "OR_start", "OR_end"]], on="PID", how="inner")
mw = mw[(mw.Obs_time >= mw.OR_start) & (mw.Obs_time <= mw.OR_end)]
mw = mw[mw.nMAP.notna()].copy()
mw["minute"] = mw.Obs_time.dt.floor("min")
per_case = mw.groupby("PID")["minute"].nunique().rename("n_min_with_reading")
per_case = per_case.to_frame().join(info.set_index("PID")[["or_min"]])
per_case["case_minutes"] = np.ceil(per_case.or_min)
tot_case_minutes = float(per_case.case_minutes.sum())
tot_min_with_reading = float(per_case.n_min_with_reading.sum())
row_non_null = float(mw.shape[0] / vit2[vit2.PID.isin(info.PID)].shape[0])
OUT["S8_recording_density_case_minute"] = {
    "n_cases": int(len(per_case)),
    "total_case_minutes": int(tot_case_minutes),
    "minutes_with_at_least_one_map_reading": int(tot_min_with_reading),
    "case_minute_recording_rate": round(tot_min_with_reading / tot_case_minutes, 4),
    "all_rows_non_null_rate_nmap": round(row_non_null, 4),
    "per_case_mean_rate": round(float((per_case.n_min_with_reading /
                                       per_case.case_minutes).mean()), 4),
    "note": ("case_minute_recording_rate = 有 ≥1 次 nMAP 记录的 OR 窗分钟数 / OR 窗总分钟数"
             "（分钟按 Obs_time 向下取整去重）；all_rows_non_null_rate = patient_vitals 全表"
             "nMAP 非空行占比（= s1_data_quality.json column_non_null_rate.nMAP = 19.89%，"
             "稿件原文误标为 case-minute 率，Round-6 订正）。"),
}
log(STAGE, f"S8 case-minute rate={tot_min_with_reading/tot_case_minutes:.4f} "
           f"rows non-null={row_non_null:.4f}")

save_json(OUT, os.path.join(RES, "s6_sensitivity.json"))
log(STAGE, f"DONE — results/s6_sensitivity.json + s6_external_grid_labels.csv")