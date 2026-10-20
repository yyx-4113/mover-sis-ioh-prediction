# -*- coding: utf-8 -*-
"""外部验证 Stage 2-4: 特征/结局派生 + 复现 MOVER 核心模型 + 套用评估。

前置: scripts/ext_download.py 已把轨缓存到 data_vitaldb/tracks/<signal>/<caseid>.csv.gz
用法:
  python scripts/ext_build.py features   # 派生 VitalDB D1 + 53 核心特征
  python scripts/ext_build.py train      # 复现 MOVER 核心 XGB 并保存
  python scripts/ext_build.py apply      # 套用模型到 VitalDB，出指标+图
  python scripts/ext_build.py all        # features -> train -> apply
"""
import os, sys, json, gzip, argparse
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log

DATA = os.path.join(ROOT, "data_vitaldb")
TRK = os.path.join(DATA, "tracks")
RES = os.path.join(ROOT, "results", "ext")
os.makedirs(RES, exist_ok=True)

# 生理合理区间（过滤 VitalDB 哨兵 -8 及非生理值）
PHYS = {
    "map":  (20.0, 250.0),
    "sbp":  (40.0, 300.0),
    "dbp":  (10.0, 200.0),
    "hr":   (20.0, 250.0),
    "hrp":  (20.0, 250.0),
    "spo2": (50.0, 100.0),
}
SIGNALS = ["map", "sbp", "dbp", "hr", "hrp", "spo2"]
W_MIN = 15.0  # 与 config.yaml features.window_minutes 一致


def load_track(signal, caseid):
    p = os.path.join(TRK, signal, f"{caseid}.csv.gz")
    if not os.path.exists(p) or os.path.getsize(p) < 50:
        return None
    try:
        with gzip.open(p, "rt") as f:
            df = pd.read_csv(f)
    except Exception:
        return None
    if df is None or df.shape[1] < 2 or df.shape[0] == 0:
        return None
    cols = list(df.columns)
    tcol = cols[0]; vcol = cols[1]
    t = pd.to_numeric(df[tcol], errors="coerce").values.astype(float)
    v = pd.to_numeric(df[vcol], errors="coerce").values.astype(float)
    lo, hi = PHYS[signal]
    mask = np.isfinite(v) & (v > 0) & (v >= lo) & (v <= hi)
    return t[mask], v[mask]


def read_cases():
    return pd.read_csv(os.path.join(DATA, "cases.csv"))


# ----------------------------------------------------------------------
def stage_features():
    cases = read_cases()
    # 仅处理动脉 MAP 队列（与 ext_download 同口径）
    trks = pd.read_csv(os.path.join(DATA, "trks.csv"))
    art = trks[trks.tname.isin(["Solar8000/ART_MBP", "EV1000/ART_MBP"])]
    cohort = sorted(art.caseid.unique())
    cases = cases[cases.caseid.isin(cohort)].copy()
    cases = cases[(cases.opstart > 0) & (cases.opend > cases.opstart)]
    print(f"[features] cohort with valid opstart/opend: {len(cases)}")

    rows = []
    label_rows = []
    n_map_track_missing = 0
    n_post_lt10 = 0
    for _, r in cases.iterrows():
        cid = int(r.caseid); opstart = float(r.opstart); opend = float(r.opend)
        # ---- D1 结局（锚点后 [opstart, opend] MAP）----
        mv = load_track("map", cid)
        if mv is None:
            n_map_track_missing += 1
            continue
        t_map, v_map = mv
        post = (t_map >= opstart) & (t_map <= opend)
        v_post = v_map[post]
        n_post = int(len(v_post))
        frac65 = float((v_post < 65).mean()) if n_post > 0 else np.nan
        d1 = int((n_post >= 10) and (frac65 >= 0.30)) if n_post >= 10 else 0
        if n_post < 10:
            n_post_lt10 += 1
        # ---- 锚点前 15min 窗口生命体征统计 ----
        feat = {}
        for sig in SIGNALS:
            sv = load_track(sig, cid)
            if sv is None:
                for stat in ["mean", "min", "max", "sd", "n", "last"]:
                    feat[f"{sig}_{stat}"] = np.nan
                continue
            t_s, v_s = sv
            pre = (t_s >= opstart - W_MIN * 60.0) & (t_s <= opstart)
            vp = v_s[pre]
            if len(vp) == 0:
                for stat in ["mean", "min", "max", "sd", "n", "last"]:
                    feat[f"{sig}_{stat}"] = np.nan
                continue
            feat[f"{sig}_mean"] = float(np.mean(vp))
            feat[f"{sig}_min"] = float(np.min(vp))
            feat[f"{sig}_max"] = float(np.max(vp))
            feat[f"{sig}_sd"] = float(np.std(vp)) if len(vp) > 1 else np.nan
            feat[f"{sig}_n"] = int(len(vp))
            feat[f"{sig}_last"] = float(vp[-1])
        # MAP 派生量（锚点前窗）
        pre_map = (t_map >= opstart - W_MIN * 60.0) & (t_map <= opstart)
        vm = v_map[pre_map]
        if len(vm) > 0:
            feat["map_frac_below_65"] = float((vm < 65).mean())
            feat["map_frac_below_55"] = float((vm < 55).mean())
            feat["map_n_below_65"] = int((vm < 65).sum())
            feat["map_n_below_55"] = int((vm < 55).sum())
            # minutes_since_last: 距锚点最近的有效 MAP（分钟）
            t_pre = t_map[pre_map]
            feat["map_minutes_since_last"] = float(-(t_pre.max() - opstart) / 60.0)
            if len(vm) >= 3:
                x = (t_pre - t_pre.min()) / 60.0
                if x.max() > 0:
                    feat["map_slope"] = float(np.polyfit(x, vm.astype(float), 1)[0])
                else:
                    feat["map_slope"] = np.nan
            else:
                feat["map_slope"] = np.nan
            feat["vitals_window_actual_min"] = float((t_pre.max() - t_pre.min()) / 60.0)
            feat["vitals_window_n_records"] = int(len(vm))
        else:
            for k in ["map_frac_below_65", "map_frac_below_55", "map_n_below_65",
                      "map_n_below_55", "map_minutes_since_last", "map_slope",
                      "vitals_window_actual_min", "vitals_window_n_records"]:
                feat[k] = np.nan
        # 人口学
        feat["age"] = float(r.age) if pd.notna(r.age) else np.nan
        feat["male"] = 1 if str(r.sex).strip().upper() == "M" else 0
        feat["height_cm"] = float(r.height) if pd.notna(r.height) else np.nan
        feat["weight_kg"] = float(r.weight) if pd.notna(r.weight) else np.nan
        feat["bmi"] = float(r.bmi) if pd.notna(r.bmi) else np.nan
        feat["bmi_missing"] = 1 if pd.isna(r.bmi) else 0
        # MOVER 专属常量（VitalDB 不可得）
        feat["anchor_is_intubation"] = 0
        feat["anchor_minus_or_start"] = float(opstart) / 60.0  # 病例起始到手术开始的分钟
        feat["or_year"] = 0
        feat["caseid"] = cid
        rows.append(feat)
        label_rows.append({"caseid": cid, "D1": d1, "n_post_map": n_post,
                           "frac_below_65_post": frac65 if n_post > 0 else np.nan,
                           "opstart": opstart, "opend": opend})

    F = pd.DataFrame(rows)
    L = pd.DataFrame(label_rows)
    F.to_csv(os.path.join(RES, "vitaldb_features.csv"), index=False)
    L.to_csv(os.path.join(RES, "vitaldb_labels.csv"), index=False)
    # 质量报告
    n_lab = len(L)
    n_pos = int(L.D1.sum())
    n_excl = int((L.n_post_map < 10).sum())
    qa = {
        "n_cohort_valid": int(len(cases)),
        "n_map_track_missing": n_map_track_missing,
        "n_features_rows": n_lab,
        "n_d1_positive": n_pos,
        "prevalence_D1": round(n_pos / n_lab, 4) if n_lab else None,
        "n_excluded_lt10_post_map": n_excl,
        "feature_nonnull_median": {c: int(F[c].notna().sum()) for c in F.columns if c != "caseid"},
    }
    with open(os.path.join(RES, "vitaldb_features_qa.json"), "w") as f:
        json.dump(qa, f, indent=2)
    print(f"[features] DONE -> vitaldb_features.csv ({n_lab} rows, {n_pos} D1+), QA saved")


# ----------------------------------------------------------------------
def stage_train():
    cfg = load_config()
    feat = pd.read_csv(os.path.join(ROOT, "results", "s2_features.csv")).set_index("PID")
    lab = pd.read_csv(os.path.join(ROOT, "results", "s1_labels_postanchor.csv")).set_index("PID")
    cb = json.load(open(os.path.join(RES, "core_benchmark.json")))
    core_cols = cb["core_feature_list"]
    y = lab["D1"].astype(int)
    common = feat.index.intersection(lab.index)
    X = feat.loc[common, core_cols]
    y = y.loc[common]
    year = feat.loc[common, "or_year"].astype(int)
    from sklearn.model_selection import train_test_split
    import xgboost as xgb
    seed = cfg["modeling"]["seed"]
    spw = max(1.0, (y == 0).sum() / max(1, (y == 1).sum()))
    results = {"core_n_features": len(core_cols), "core_feature_list": core_cols}
    for split, (tr_i, te_i) in [
        ("patient", train_test_split(X.index, test_size=0.2, random_state=seed, stratify=y)),
        ("temporal", (X.index[year <= 2017], X.index[year == 2018])),
    ]:
        m = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
                              reg_lambda=1.0, scale_pos_weight=spw, n_jobs=-1,
                              random_state=seed, eval_metric="logloss")
        m.fit(X.loc[tr_i], y.loc[tr_i])
        p = m.predict_proba(X.loc[te_i])[:, 1]
        from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
        results[split] = dict(n_test=int(len(te_i)), n_pos_test=int(y.loc[te_i].sum()),
                              auprc=round(float(average_precision_score(y.loc[te_i], p)), 4),
                              auroc=round(float(roc_auc_score(y.loc[te_i], p)), 4),
                              brier=round(float(brier_score_loss(y.loc[te_i], p)), 4))
        log("ext-train", f"[MOVER-core/{split}] AUPRC={results[split]['auprc']} AUROC={results[split]['auroc']}")
    # 在全量上复现并最终保存用于外部验证的模型
    spw_all = max(1.0, (y == 0).sum() / max(1, (y == 1).sum()))
    mfinal = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                              subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
                              reg_lambda=1.0, scale_pos_weight=spw_all, n_jobs=-1,
                              random_state=seed, eval_metric="logloss")
    mfinal.fit(X, y)
    import joblib
    joblib.dump(mfinal, os.path.join(RES, "mover_core_model.joblib"))
    with open(os.path.join(RES, "core_cols.json"), "w") as f:
        json.dump(core_cols, f)
    with open(os.path.join(RES, "mover_core_train_metrics.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"[train] DONE -> mover_core_model.joblib + core_cols.json + metrics")


# ----------------------------------------------------------------------
def stage_apply():
    cfg = load_config()
    F = pd.read_csv(os.path.join(RES, "vitaldb_features.csv"))
    L = pd.read_csv(os.path.join(RES, "vitaldb_labels.csv"))
    core_cols = json.load(open(os.path.join(RES, "core_cols.json")))
    import joblib
    m = joblib.load(os.path.join(RES, "mover_core_model.joblib"))
    y = L.set_index("caseid").loc[F.caseid, "D1"].astype(int).values
    X = F[core_cols].copy()
    p = m.predict_proba(X)[:, 1]
    from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
    auprc = float(average_precision_score(y, p))
    auroc = float(roc_auc_score(y, p))
    brier = float(brier_score_loss(y, p))
    # bootstrap CI
    rng = np.random.default_rng(12345); n = len(y); idx = np.arange(n); vals_p = []; vals_r = []
    for _ in range(1000):
        s = rng.choice(idx, size=n, replace=True)
        if y[s].sum() == 0:
            continue
        vals_p.append(average_precision_score(y[s], p[s]))
        vals_r.append(roc_auc_score(y[s], p[s]))
    ci_p = [float(np.percentile(vals_p, 2.5)), float(np.percentile(vals_p, 97.5))]
    ci_r = [float(np.percentile(vals_r, 2.5)), float(np.percentile(vals_r, 97.5))]
    res = {
        "external_source": "VitalDB",
        "n_cases": int(n), "n_d1_positive": int(y.sum()),
        "prevalence_D1": round(float(y.mean()), 4),
        "auprc": round(auprc, 4), "auprc_ci95": [round(x, 4) for x in ci_p],
        "auroc": round(auroc, 4), "auroc_ci95": [round(x, 4) for x in ci_r],
        "brier": round(brier, 4), "pred_mean": round(float(p.mean()), 4),
        "note": ("MOVER 核心模型（53 列可移植子集，seed=12345）直接套用到 VitalDB 动脉 MAP 队列，"
                 "未用外部数据重拟合/重校准；anchor_is_intubation=0、or_year=0（VitalDB 不可得），"
                 "anchor_minus_or_start=手术开始距病例起始分钟。"),
    }
    with open(os.path.join(RES, "external_validation.json"), "w") as f:
        json.dump(res, f, indent=2)
    # 保存预测用于绘图
    pd.DataFrame({"caseid": F.caseid.values, "y": y, "p": p}).to_csv(
        os.path.join(RES, "vitaldb_predictions.csv"), index=False)
    print(f"[apply] DONE -> external_validation.json  AUPRC={auprc:.4f} AUROC={auroc:.4f} "
          f"(n={n}, pos={int(y.sum())}, prev={y.mean():.3f})")
    _figures(y, p)


def _figures(y, p):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve, precision_recall_curve
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    # ROC
    fpr, tpr, _ = roc_curve(y, p)
    ax[0].plot(fpr, tpr); ax[0].set_title("External ROC (VitalDB)"); ax[0].set_xlabel("FPR"); ax[0].set_ylabel("TPR")
    # PR
    prec, rec, _ = precision_recall_curve(y, p)
    ax[1].plot(rec, prec); ax[1].set_title("External PR (VitalDB)"); ax[1].set_xlabel("Recall"); ax[1].set_ylabel("Precision")
    # Predicted risk distribution
    ax[2].hist(p[y == 0], bins=40, alpha=0.6, label="D1-"); ax[2].hist(p[y == 1], bins=40, alpha=0.6, label="D1+")
    ax[2].set_title("Predicted risk"); ax[2].set_xlabel("P(D1+)"); ax[2].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "external_validation_fig.png"), dpi=130)
    print("[apply] figure -> external_validation_fig.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["features", "train", "apply", "all"])
    args = ap.parse_args()
    if args.stage == "features" or args.stage == "all":
        stage_features()
    if args.stage == "train" or args.stage == "all":
        if args.stage == "all":
            pass
        stage_train()
    if args.stage == "apply" or args.stage == "all":
        stage_apply()


if __name__ == "__main__":
    main()
