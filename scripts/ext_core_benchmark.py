# -*- coding: utf-8 -*-
"""外部验证前置基准：VitalDB 可移植核心特征子集在 MOVER 上的表现。

目的（protocol §外部验证）：
  直接竞品外部验证（VitalDB）可得的特征只有「人口学 + 锚点前动脉/无创血压/心率/SpO2
  + 锚点时序」；MOVER 的 sg_*（韩文手术名难映射）、ev_*（麻醉事件）、drug_*/lab_*/io_*/
  vent_*/art_* 等域在 VitalDB 不可得或 schema 差异过大。本脚本量化「仅用可移植子集」
  在 MOVER 上的 AUPRC/AUROC，作为 VitalDB 外部验证的**诚实预期下界**。

方法：完全复用 s3_models.py 的 XGB 规格（n_estimators=300, max_depth=4, lr=0.05,
  subsample=0.8, colsample=0.8, min_child_weight=10, reg_lambda=1.0, seed=12345），
  患者级 80/20 + 时间切分（<=2017 train / 2018 test），与 s3 一致。

输出：results/ext/core_benchmark.json
"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss

STAGE = "ext-core"
cfg = load_config(); P = paths(cfg); RES = P["results_dir"]
seed = cfg["modeling"]["seed"]
n_boot = cfg["modeling"]["bootstrap_resamples"]

# ---- 载入 MOVER 特征 + D1 标签（与 s3 完全一致）----
feat = pd.read_csv(os.path.join(RES, "s2_features.csv")).set_index("PID")
lab = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")
primary_id = cfg["outcomes"]["primary_id"]
y = lab[primary_id].astype(int)
common = feat.index.intersection(lab.index)
feat, y = feat.loc[common], y.loc[common]
obj_cols = feat.select_dtypes(include="object").columns.tolist()
X_all = feat.drop(columns=obj_cols)

# ---- 可移植核心子集：人口学 + 锚点前生命体征 + 锚点时序；剔除不可移植域 ----
KEEP_PREFIX = ("age", "male", "height_cm", "weight_kg", "bmi", "bmi_missing",
               "map_", "sbp_", "dbp_", "hr_", "hrp_", "spo2_",
               "vitals_window_", "anchor_is_intubation", "anchor_minus_or_start", "or_year")
DROP_PREFIX = ("sg_", "ev_", "n_events_pre_anchor", "art_", "agent_", "has_vent",
               "has_art_line", "drug_", "lab_", "has_lab", "io_", "has_io")
core_cols = [c for c in X_all.columns
             if c.startswith(KEEP_PREFIX) and not c.startswith(DROP_PREFIX)]
X_core = X_all[core_cols]
log(STAGE, f"全特征 {X_all.shape[1]} 列；核心可移植子集 {len(core_cols)} 列")
log(STAGE, f"被剔除的域前缀: {DROP_PREFIX}")

year = X_all["or_year"].astype(int)


def xgb_make(spw):
    return xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                             subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
                             reg_lambda=1.0, scale_pos_weight=spw, n_jobs=-1,
                             random_state=seed, eval_metric="logloss")


def boot_ci(yt, yp, fn, B=n_boot):
    rng = np.random.default_rng(seed); n = len(yt); idx = np.arange(n); vals = []
    for _ in range(B):
        s = rng.choice(idx, size=n, replace=True)
        if yt[s].sum() == 0:
            continue
        vals.append(fn(yt[s], yp[s]))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if vals else [None, None]


def eval_on(Xmat, tag):
    spw = max(1.0, (y.loc[Xmat.index] == 0).sum() / max(1, (y.loc[Xmat.index] == 1).sum()))
    out = {}
    for split, (tr_i, te_i) in [
        ("patient", train_test_split(Xmat.index, test_size=0.2, random_state=seed, stratify=y.loc[Xmat.index])),
        ("temporal", (Xmat.index[year <= 2017], Xmat.index[year == 2018])),
    ]:
        Xtr, Xte = Xmat.loc[tr_i], Xmat.loc[te_i]
        ytr, yte = y.loc[tr_i], y.loc[te_i]
        m = xgb_make(spw); m.fit(Xtr, ytr)
        p = m.predict_proba(Xte)[:, 1]
        auprc = average_precision_score(yte, p); auroc = roc_auc_score(yte, p)
        brier = brier_score_loss(yte, p)
        out[split] = dict(n_train=len(ytr), n_test=len(yte), n_pos_test=int(yte.sum()),
                          auprc=round(auprc, 4), auprc_ci95=boot_ci(yte.values, p, average_precision_score),
                          auroc=round(auroc, 4), auroc_ci95=boot_ci(yte.values, p, roc_auc_score),
                          brier=round(brier, 4), pred_mean=round(float(p.mean()), 4))
        log(STAGE, f"[{tag}/{split}] AUPRC={auprc:.3f} AUROC={auroc:.3f} (n_test={len(yte)}, pos={int(yte.sum())})")
    return out


results = {
    "primary_id": primary_id,
    "xgb_params": dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
                       colsample_bytree=0.8, min_child_weight=10, reg_lambda=1.0, seed=seed),
    "full_model": eval_on(X_all, "full"),          # 参照 s3（应≈0.347/0.339）
    "core_transportable_model": eval_on(X_core, "core"),
    "core_n_features": len(core_cols),
    "core_feature_list": core_cols,
    "note": ("core_transportable_model 用 VitalDB 可得的特征子集在 MOVER 上重拟合，"
             "代表外部验证的诚实预期（VitalDB 还将进一步丢失 anchor_is_intubation/ev_* "
             "等 MOVER 特有时序信号，故外部 AUPRC 可能更低）。"),
}
os.makedirs(os.path.join(RES, "ext"), exist_ok=True)
with open(os.path.join(RES, "ext", "core_benchmark.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
log(STAGE, "DONE -> results/ext/core_benchmark.json")
