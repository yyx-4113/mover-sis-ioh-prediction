# -*- coding: utf-8 -*-
"""Round-1 补充：MAP-only 逻辑回归 DCA 基准（检验全模型相对"床旁 MAP"的增量价值）

方法学依据：A1 §7 / A2 §7 要求给出"模型相对单纯预锚点 MAP 的增量决策价值"。
本脚本在患者级主切分上，用 *仅* 预锚点平均 MAP 拟合逻辑回归（与 s3 全模型同款
中位数插补+缺失指示+标准化+类别均衡），以相同 5 折 OOF isotonic 校准，
计算 DCA 净收益，写入 results/s3_calib_dca.json["map_only_benchmark"]，
并重绘 results/s3_figs/dca.png（叠加基准曲线），供 Figure 4 使用。

纪律：从 s2_features.csv / s1_labels_postanchor.csv 现读现算；复现 s3 的患者级切分
（train_test_split, test_size=0.2, random_state=seed, stratify=D1）。
"""
import os, json
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
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(RES, "s3_figs")

seed = 12345
feat = pd.read_csv(os.path.join(RES, "s2_features.csv")).set_index("PID")
lab = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")
y = lab["D1"].astype(int)
common = feat.index.intersection(lab.index)
feat, y = feat.loc[common], y.loc[common]

ridx, teidx = train_test_split(feat.index, test_size=0.2, random_state=seed, stratify=y)
Xtr, Xte = feat.loc[ridx], feat.loc[teidx]
ytr, yte = y.loc[ridx], y.loc[teidx]

def make_map_only():
    imp = SimpleImputer(strategy="median", add_indicator=True)
    Xtr_m = pd.DataFrame(imp.fit_transform(Xtr[["map_mean"]]), index=Xtr.index,
                         columns=imp.get_feature_names_out(["map_mean"]))
    Xte_m = pd.DataFrame(imp.transform(Xte[["map_mean"]]), index=Xte.index,
                         columns=imp.get_feature_names_out(["map_mean"]))
    sc = StandardScaler().fit(Xtr_m)
    Xtr_s, Xte_s = sc.transform(Xtr_m), sc.transform(Xte_m)
    clf = LogisticRegression(max_iter=3000, class_weight="balanced")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof = cross_val_predict(clf, Xtr_s, ytr, cv=skf, method="predict_proba")[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(oof, ytr)
    clf.fit(Xtr_s, ytr)
    p_raw = clf.predict_proba(Xte_s)[:, 1]
    p_cal = iso.predict(p_raw)
    return p_cal, p_raw

p_cal, p_raw = make_map_only()
auprc_map_only = round(float(average_precision_score(yte.values, p_cal)), 4)
auprc_map_only_raw = round(float(average_precision_score(yte.values, p_raw)), 4)

# DCA（与 s3 同网格/同公式）
grids = np.round(np.arange(0.01, 1.00, 0.01), 2)
N = len(yte); pos = int(yte.sum()); neg = N - pos
nb_model, nb_all = [], []
for t in grids:
    pred = (p_cal >= t).astype(int)
    tp = int(((pred == 1) & (yte == 1)).sum()); fp = int(((pred == 1) & (yte == 0)).sum())
    nb_model.append(tp / N - (fp / N) * (t / (1 - t)))
    nb_all.append(pos / N - (neg / N) * (t / (1 - t)))

# 载入现有 dca 文件，叠加基准
cd = json.load(open(os.path.join(RES, "s3_calib_dca.json"), encoding="utf-8"))
# 增量净收益关键阈值
def nb_at(d, thr):
    i = min(range(len(d["thresholds"])), key=lambda k: abs(d["thresholds"][k] - thr))
    return d["net_benefit_model"][i]
incr_010 = round(nb_at(cd["patient"]["dca"], 0.10) - nb_at({"thresholds": grids.tolist(),
            "net_benefit_model": nb_model}, 0.10), 4)
incr_015 = round(nb_at(cd["patient"]["dca"], 0.15) - nb_at({"thresholds": grids.tolist(),
            "net_benefit_model": nb_model}, 0.15), 4)
cd["map_only_benchmark"] = {
    "model": "logistic_map_mean_only",
    "calibration": "isotonic_oof",
    "auprc_patient_test": auprc_map_only,
    "auprc_patient_test_raw": auprc_map_only_raw,
    "nb_increment_at_0.10": incr_010,
    "nb_increment_at_0.15": incr_015,
    "dca": {
        "thresholds": grids.tolist(),
        "net_benefit_model": nb_model,
        "net_benefit_treat_all": nb_all,
        "net_benefit_treat_none": [0.0] * len(grids),
    },
}
json.dump(cd, open(os.path.join(RES, "s3_calib_dca.json"), "w", encoding="utf-8"), indent=1)
print("[benchmark] map-only logistic DCA written; test n=%d pos=%d auprc=%.4f" %
      (N, pos, auprc_map_only))

# 增量净收益（全模型 vs MAP-only）关键阈值
full = cd["patient"]["dca"]
def nb_at(d, thr):
    i = min(range(len(d["thresholds"])), key=lambda k: abs(d["thresholds"][k] - thr))
    return d["thresholds"][i], d["net_benefit_model"][i]
for thr in (0.10, 0.15):
    tf, nbf = nb_at(full, thr)
    tb, nbb = nb_at(cd["map_only_benchmark"]["dca"], thr)
    print("[benchmark] @%.2f  full=%.4f  map_only=%.4f  incr=%.4f" %
          (thr, nbf, nbb, nbf - nbb))

# 重绘 dca.png（叠加基准）
plt.figure(figsize=(5.4, 4.2))
g = full["thresholds"]
plt.plot(g, full["net_benefit_model"], lw=2, label="XGBoost (full model)")
plt.plot(g, cd["map_only_benchmark"]["dca"]["net_benefit_model"], lw=2, ls="--",
         label="MAP-only logistic")
plt.plot(g, full["net_benefit_treat_all"], lw=1.5, color="gray", label="treat all")
plt.plot(g, full["net_benefit_treat_none"], lw=1.5, color="black", label="treat none")
plt.xlabel("Threshold probability")
plt.ylabel("Net benefit")
plt.title("Decision curve (patient-level)")
plt.legend(loc="upper right", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "dca.png"), dpi=120)
plt.close()
print("[benchmark] dca.png regenerated with MAP-only benchmark overlay")
