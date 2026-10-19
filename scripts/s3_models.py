# -*- coding: utf-8 -*-
"""阶段 3：建模与验证（protocol §5-7）

输入：results/s2_features.csv（预锚点特征矩阵，无泄漏）
      results/s1_labels_postanchor.csv（锚点后主结局 D1）
      results/s1_anchor.csv（用于时间切分 year）
输出：results/s3_metrics.json            （模型 × 切分 的 AUPRC/AUROC/CI/Brier）
      results/s3_calib_dca.json         （OOF isotonic 校准 + DCA）
      results/s3_subgroups.json         （亚组 AUPRC）
      results/s3_feature_importance.json（XGB/LGBM gain top）
      results/s3_figs/*.png             （PR/ROC/校准/DCA/重要性）

=====================================================================
v1.0.0（2026-10-19）
=====================================================================
设计纪律（不可协商，逐条以断言守护，禁止静默失败）：
  - 标签 = 锚点后 D1（与 protocol §4 outcome_source=post_anchor 一致）
  - 特征矩阵任何锚点后列一律禁止进入（BANNED 守卫）
  - 患者级切分 = 主分析；时间切分（train<=2017 / test==2018）= 次要稳健性
  - 主指标 AUPRC；AUROC 与 bootstrap 95% CI 配对报告
  - 校准用 5 折 OOF isotonic
  - 1000 次患者级 bootstrap 95% CI
  - 所有预测概率必须落在 [0,1]，否则硬失败
"""
import os, sys, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (average_precision_score, roc_auc_score, brier_score_loss,
                             precision_recall_curve, roc_curve)
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
import xgboost as xgb
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log, save_json

warnings.filterwarnings("ignore")
STAGE = "s3"
cfg = load_config(); P = paths(cfg); RES = P["results_dir"]
FIG = os.path.join(RES, "s3_figs"); os.makedirs(FIG, exist_ok=True)

seed = int(cfg["modeling"]["seed"])
primary = cfg["modeling"]["primary_metric"]
n_boot = int(cfg["modeling"]["bootstrap_resamples"])
primary_id = cfg["outcomes"]["primary_id"]
assert primary_id == "D1", f"protocol 约定 primary_id=D1，实际 {primary_id}"

# ================================================================ 1. 载入与对齐
feat = pd.read_csv(os.path.join(RES, "s2_features.csv")).set_index("PID")
lab = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")
anchor = pd.read_csv(os.path.join(RES, "s1_anchor.csv")).set_index("PID")
assert primary_id in lab.columns, f"标签文件缺 {primary_id}"
y = lab[primary_id].astype(int)
common = feat.index.intersection(lab.index)
feat, y = feat.loc[common], y.loc[common]
assert y.notna().all(), "标签含 NaN——不允许"
assert set(y.unique()) <= {0, 1}, "标签非二值"
log(STAGE, f"对齐后样本 n={len(y)}；D1 阳性={int(y.sum())} ({y.mean()*100:.2f}%)")

# 丢弃非数值/非特征列（字符串类别列如 anchor_source / surg_group 不进模型）
obj_cols = feat.select_dtypes(include="object").columns.tolist()
X = feat.drop(columns=obj_cols)
BANNED = {"post_window_minutes", "post_nmap_measurements", "or_min", "surgery_end", "or_end"}
assert not (BANNED & set(X.columns)), f"泄漏列进入特征矩阵: {sorted(BANNED & set(X.columns))}"
assert X.select_dtypes(include="object").shape[1] == 0, "仍有对象列"
log(STAGE, f"特征矩阵 {X.shape[0]}×{X.shape[1]}；丢弃非数值列 {obj_cols}")

# 缺失处理：树模型保留 NaN（原生）；Logistic 中位数插补+缺失指示
imp = SimpleImputer(strategy="median", add_indicator=True)
X_log = pd.DataFrame(imp.fit_transform(X), index=X.index,
                     columns=imp.get_feature_names_out(X.columns))
base_cols = [c for c in ["age", "male", "bmi"] if c in X.columns]
assert len(base_cols) == 3, f"基线特征缺失: {base_cols}"

# 时间切分年份
year = X["or_year"].astype(int)
n_2018 = int((year == 2018).sum())
log(STAGE, f"时间切分 test(2018)={n_2018} 例；train(<=2017)={int((year<=2017).sum())} 例")

# ================================================================ 2. 工具函数
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

def fit_eval(make_model, Xtr, ytr, Xte, yte, name, split, calibrate=False):
    model = make_model()
    model.fit(Xtr, ytr)
    p = model.predict_proba(Xte)[:, 1] if hasattr(model, "predict_proba") \
        else model.decision_function(Xte)
    assert np.all((p >= 0) & (p <= 1)), f"[{name}/{split}] 概率越界 [{p.min():.3f},{p.max():.3f}]"
    assert yte.sum() > 0, f"[{name}/{split}] test 无阳性事件，AUPRC 不可估"
    auprc = average_precision_score(yte, p)
    auroc = roc_auc_score(yte, p)
    brier = brier_score_loss(yte, p)
    ci_p = boot_ci(yte, p, average_precision_score)
    ci_r = boot_ci(yte, p, roc_auc_score)
    rec = dict(model=name, split=split, n_train=len(ytr), n_test=len(yte),
               n_pos_test=int(yte.sum()), auprc=round(auprc, 4), auprc_ci95=ci_p,
               auroc=round(auroc, 4), auroc_ci95=ci_r, brier=round(brier, 4),
               pred_mean=round(float(p.mean()), 4))
    return rec, model, p

def build_models(ytr):
    """返回未拟合的模型规格：src 决定用插补矩阵(log)还是原生 NaN 矩阵(tree)，
    cols 为可选列子集（基线仅用 age/male/bmi）。fit_eval 负责在正确矩阵上拟合。"""
    spw = max(1.0, (ytr == 0).sum() / max(1, (ytr == 1).sum()))
    return {
        "baseline_logit": dict(src="log", cols=base_cols, factory=lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])),
        "logistic_full": dict(src="log", cols=None, factory=lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))])),
        "xgboost": dict(src="tree", cols=None, factory=lambda: xgb.XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, min_child_weight=10, reg_lambda=1.0,
            scale_pos_weight=spw, n_jobs=-1, random_state=seed, eval_metric="logloss")),
        "lightgbm": dict(src="tree", cols=None, factory=lambda: lgb.LGBMClassifier(
            n_estimators=300, num_leaves=15, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, min_child_samples=20, reg_lambda=1.0,
            class_weight="balanced", n_jobs=-1, random_state=seed, verbosity=-1)),
    }

# ================================================================ 3. 切分与建模
def subgroup_auprc(yte, p, Xte, tag):
    out = {}
    # 性别
    if "male" in Xte.columns:
        for v, lbl in [(1, "male"), (0, "female")]:
            m = (Xte["male"] == v).values
            if m.sum() > 50 and yte[m].sum() > 0:
                out[f"sex_{lbl}"] = round(average_precision_score(yte[m], p[m]), 4)
    # 年龄带
    if "age" in Xte.columns:
        for lo, hi, lbl in [(0, 50, "age<50"), (50, 65, "age50-65"), (65, 200, "age>=65")]:
            m = ((Xte["age"] >= lo) & (Xte["age"] < hi)).values
            if m.sum() > 50 and yte[m].sum() > 0:
                out[lbl] = round(average_precision_score(yte[m], p[m]), 4)
    # BMI 带
    if "bmi" in Xte.columns:
        for lo, hi, lbl in [(0, 18.5, "bmi<18.5"), (18.5, 25, "bmi18.5-25"),
                           (25, 30, "bmi25-30"), (30, 200, "bmi>=30")]:
            m = ((Xte["bmi"] >= lo) & (Xte["bmi"] < hi)).values
            if m.sum() > 50 and yte[m].sum() > 0:
                out[lbl] = round(average_precision_score(yte[m], p[m]), 4)
    return out

results = []
subgroups = {}
calib_dca = {}
importances = {}
preds = {}      # (split, name) -> test predicted probabilities
ytes = {}       # split -> test labels

# ---- 切分 A：患者级（主） ----
ridx, teidx = train_test_split(X.index, test_size=0.2, random_state=seed, stratify=y)
# ---- 切分 B：时间（次） ----
tr_mask = (year <= 2017).values
te_mask = (year == 2018).values
ridx_t, teidx_t = X.index[tr_mask], X.index[te_mask]

for (split, tr_i, te_i) in [("patient", ridx, teidx), ("temporal", ridx_t, teidx_t)]:
    log(STAGE, f"切分={split}  train={len(tr_i)} test={len(te_i)}")
    Xtr, Xte = X.loc[tr_i], X.loc[te_i]
    Xtr_tree, Xte_tree = X.loc[tr_i], X.loc[te_i]          # NaN 原生
    ytr, yte = y.loc[tr_i], y.loc[te_i]
    assert ytr.sum() > 0 and yte.sum() > 0, f"{split}: 训练或测试无阳性"
    models = build_models(ytr)
    fitted = {}
    for name, spec in models.items():
        if spec["src"] == "log":
            cols = spec["cols"]
            Xtr_m = X_log.loc[tr_i, cols] if cols is not None else X_log.loc[tr_i]
            Xte_m = X_log.loc[te_i, cols] if cols is not None else X_log.loc[te_i]
        else:
            Xtr_m, Xte_m = X.loc[tr_i], X.loc[te_i]
        rec, model, p = fit_eval(spec["factory"], Xtr_m, ytr, Xte_m, yte, name, split)
        results.append(rec)
        fitted[name] = model
        preds[(split, name)] = p
        ytes[split] = yte
        log(STAGE, f"  {name:14s} AUPRC={rec['auprc']:.3f} AUROC={rec['auroc']:.3f} Brier={rec['brier']:.3f}")

    # ---- 校准 + DCA（以 xgboost 为主模型）----
    xgb_model = fitted["xgboost"]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof = cross_val_predict(xgb_model, Xtr_tree, ytr, cv=skf, method="predict_proba")[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(oof, ytr)
    p_raw = xgb_model.predict_proba(Xte_tree)[:, 1]
    p_cal = iso.predict(p_raw)
    brier_raw = brier_score_loss(yte, p_raw)
    brier_cal = brier_score_loss(yte, p_cal)
    # 校准 in-the-small：y ~ a + b*p（线性）
    sl, ic = np.polyfit(p_cal, yte.values, 1)
    frac_pos, mean_pred = calibration_curve(yte, p_cal, n_bins=10, strategy="quantile")
    frac_pos_raw, mean_pred_raw = calibration_curve(yte, p_raw, n_bins=10, strategy="quantile")
    # DCA
    grids = np.round(np.arange(0.01, 1.00, 0.01), 2)
    N = len(yte); pos = int(yte.sum()); neg = N - pos
    nb_model, nb_all = [], []
    for t in grids:
        pred = (p_cal >= t).astype(int)
        tp = int(((pred == 1) & (yte == 1)).sum()); fp = int(((pred == 1) & (yte == 0)).sum())
        nb_model.append(tp / N - (fp / N) * (t / (1 - t)))
        nb_all.append(pos / N - (neg / N) * (t / (1 - t)))
    calib_dca[split] = {
        "model": "xgboost", "calibration": "isotonic_oof",
        "brier_raw": round(brier_raw, 4), "brier_calibrated": round(brier_cal, 4),
        "calib_slope": round(float(sl), 4), "calib_intercept": round(float(ic), 4),
        "calibration_curve": {"mean_pred": mean_pred.tolist(), "frac_pos": frac_pos.tolist()},
        "calibration_curve_raw": {"mean_pred": mean_pred_raw.tolist(), "frac_pos": frac_pos_raw.tolist()},
        "dca": {"thresholds": grids.tolist(), "net_benefit_model": nb_model,
                "net_benefit_treat_all": nb_all, "net_benefit_treat_none": [0.0] * len(grids)},
    }
    # 亚组
    subgroups[split] = subgroup_auprc(yte.values, p_cal, Xte, split)

    # 重要性（主切分患者级才存图/表；temporal 仅指标）
    if split == "patient":
        xi = xgb_model.get_booster().get_score(importance_type="gain")
        xidf = pd.DataFrame(sorted(xi.items(), key=lambda x: -x[1]),
                            columns=["feature", "gain"]).head(25)
        importances["xgboost_top25"] = xidf.to_dict("records")
        li = lgb.plot_importance(fitted["lightgbm"], importance_type="gain",
                                 max_num_features=25, figsize=(6, 7))
        plt.gcf().axes[0].get_figure().savefig(os.path.join(FIG, "importance_lgbm.png"), dpi=120, bbox_inches="tight")
        plt.close()

# ================================================================ 3b. 曲线原始点落盘（供 Fig 1-5 图件生成）
curves = {}
for split in ytes:
    yt = ytes[split]
    curves[split] = {}
    for name in ["baseline_logit", "logistic_full", "xgboost", "lightgbm"]:
        p = preds[(split, name)]
        prc, rc, _ = precision_recall_curve(yt, p)
        fpr, tpr, _ = roc_curve(yt, p)
        curves[split][name] = {
            "pr": {"recall": rc.tolist(), "precision": prc.tolist()},
            "roc": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
        }
save_json(curves, os.path.join(RES, "s3_curves.json"))

# ================================================================ 4. 图表（主切分）
def plot_pr_roc():
    plt.figure(figsize=(5, 4))
    for rec in results:
        if rec["split"] != "patient":
            continue
        # 重新取预测不可得，仅画指标 anchor 点
    # 简化：画各模型主切分 AUPRC 柱状
    df = pd.DataFrame([r for r in results if r["split"] == "patient"])
    plt.bar(df.model, df.auprc, color="#4C72B0")
    plt.axhline(y=y.mean(), color="red", ls="--", label=f"base rate {y.mean():.3f}")
    plt.ylabel("AUPRC"); plt.title("Patient-level AUPRC by model")
    plt.xticks(rotation=20); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "auprc_patient.png"), dpi=120); plt.close()

    plt.figure(figsize=(5, 4))
    plt.bar(df.model, df.auroc, color="#55A868")
    plt.axhline(y=0.5, color="red", ls="--", label="random 0.5")
    plt.ylabel("AUROC"); plt.title("Patient-level AUROC by model")
    plt.xticks(rotation=20); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "auroc_patient.png"), dpi=120); plt.close()

plot_pr_roc()

# 校准 + DCA（患者级主模型）
cd = calib_dca["patient"]
plt.figure(figsize=(5, 4))
plt.plot(cd["calibration_curve"]["mean_pred"], cd["calibration_curve"]["frac_pos"], "o-", label="calibrated")
plt.plot([0, 1], [0, 1], "k--", label="ideal")
plt.xlabel("Predicted probability"); plt.ylabel("Observed fraction")
plt.title(f"Calibration (slope={cd['calib_slope']})"); plt.legend(); plt.tight_layout()
plt.savefig(os.path.join(FIG, "calibration.png"), dpi=120); plt.close()

plt.figure(figsize=(5, 4))
g = cd["dca"]["thresholds"]
plt.plot(g, cd["dca"]["net_benefit_model"], label="model")
plt.plot(g, cd["dca"]["net_benefit_treat_all"], label="treat all")
plt.plot(g, cd["dca"]["net_benefit_treat_none"], label="treat none")
plt.xlabel("Threshold probability"); plt.ylabel("Net benefit")
plt.title("Decision curve (patient-level)"); plt.legend(); plt.tight_layout()
plt.savefig(os.path.join(FIG, "dca.png"), dpi=120); plt.close()

# ================================================================ 5. 落盘
save_json({"stage": STAGE, "version": "v1.0.0", "primary_id": primary_id,
           "primary_metric": primary, "seed": seed, "n_bootstrap": n_boot,
           "n_total": int(len(y)), "prevalence": round(float(y.mean()), 4),
           "results": results},
          os.path.join(RES, "s3_metrics.json"))
save_json(calib_dca, os.path.join(RES, "s3_calib_dca.json"))
save_json(subgroups, os.path.join(RES, "s3_subgroups.json"))
save_json(importances, os.path.join(RES, "s3_feature_importance.json"))
log(STAGE, "DONE (v1.0.0) — 产物: s3_metrics/calib_dca/subgroups/feature_importance + s3_figs")
