# -*- coding: utf-8 -*-
"""外部验证管线（VitalDB）— SIS IOH 预测。

阶段：
  outcome   派生 VitalDB D1 标签（复用 s1 exposure_fraction 逻辑，按构造正确）
  features  对齐 VitalDB 特征矩阵到 MOVER 列（仅可移植核心子集）
  validate  复用 MOVER XGB 管线（seed=12345 重拟合 + OOF isotonic）套用外部特征，
            计算 AUPRC/AUROC/校准/DCA

用法：
  python scripts/ext_pipeline.py --selftest        # 离线验证 D1 派生逻辑（无需数据/包）
  python scripts/ext_pipeline.py --stage outcome   # 需已下载 VitalDB 数据 + vitaldb 包
  python scripts/ext_pipeline.py --stage features
  python scripts/ext_pipeline.py --stage validate
  python scripts/ext_pipeline.py --stage all

注意：本会话因 api.vitaldb.net 经代理 502 且需 VitalDB 账户，数据获取步无法执行；
      仅 --selftest 可在离线环境运行通过。作者须在已注册账户 + 可联网环境运行其余步骤。
"""
import os
import sys
import json
import argparse
import numpy as np
import pandas as pd

STAGE = "ext-pipeline"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


# ================================================================ 0. D1 派生（纯函数，复用 s1 逻辑）
def derive_D1(values, threshold=65, min_measurements=10, fraction=0.30):
    """暴露比例型结局（与 s1_cohort.py evaluate() exposure_fraction 分支一致）。

    输入：values = 锚点后窗口内 MAP 测量的数值数组（已剔除 NaN）
    返回：(is_positive:bool, n_measurements:int, frac_below:float)
    定义：n>=10 且 (值<threshold) 占比 >= fraction → 阳性。
    """
    values = np.asarray(values, dtype=float)
    n = int(len(values))
    if n < min_measurements:
        return False, n, (float((values < threshold).mean()) if n else 0.0)
    frac_below = float((values < threshold).mean())
    return (frac_below >= fraction), n, frac_below


# ================================================================ 1. VitalDB 加载（懒加载，受账户/网络约束）
class VitalDBLoader:
    """VitalDB 病例加载器。import 受网络/账户约束，仅在使用时触发。"""

    def __init__(self, cache_dir=None):
        try:
            import vitaldb
            self.vdb = vitaldb
        except Exception as e:  # pragma: no cover - 离线环境无包
            raise RuntimeError(
                "vitaldb 包不可用。请在已注册 VitalDB 账户 + 可联网环境执行：pip install vitaldb")
        self.cache_dir = cache_dir

    def load_case(self, caseid):
        """返回 (demographics:dict, df:DataFrame[time, ART_MAP, ...])。

        VitalDB 实际 API：
          vf = vitaldb.VitalFile(caseid)  →  df = vf.to_pandas()  （含 Time + 各轨）
          demo = vitaldb.get_case(caseid) →  dict(age, sex, height, weight, opname, opstart, opend, ...)
        此处仅描述契约；具体列名以实际下载为准（运行前用 1 例探查校准）。
        """
        vf = self.vdb.VitalFile(caseid) if self.cache_dir is None else \
            self.vdb.VitalFile(caseid, download_dir=self.cache_dir)
        df = vf.to_pandas()
        demo = self.vdb.get_case(caseid)
        return demo, df

    def list_cases(self, limit=None):
        """返回候选病例 ID 列表（按 external_source.case_filter 预筛）。"""
        cases = self.vdb.get_cases() if hasattr(self.vdb, "get_cases") else []
        if limit:
            cases = cases[:limit]
        return cases


# ================================================================ 2. 特征对齐（VitalDB → MOVER 列）
# 与 config_vitaldb.yaml features.keep_prefix / drop_prefix 及 ext_core_benchmark KEEP_PREFIX 一致。
KEEP_PREFIX = ("age", "male", "height_cm", "weight_kg", "bmi", "bmi_missing",
               "map_", "sbp_", "dbp_", "hr_", "hrp_", "spo2_",
               "vitals_window_", "anchor_is_intubation", "anchor_minus_or_start", "or_year")
DROP_PREFIX = ("sg_", "ev_", "n_events_pre_anchor", "art_", "agent_", "has_vent",
               "has_art_line", "drug_", "lab_", "has_lab", "io_", "has_io")


def select_core_columns(cols):
    return [c for c in cols if c.startswith(KEEP_PREFIX) and not c.startswith(DROP_PREFIX)]


def build_feature_row(demo, df, anchor_time, op_end, win=15):
    """由单例 VitalDB 数据构造 MOVER 风格特征行（仅可移植核心域）。

    锚点前窗口 = [anchor_time - win, anchor_time]；结局窗 = [anchor_time, op_end]。
    df 需含 time 列（datetime）与 ART_MAP（动脉 MAP）等轨。
    返回 dict（仅核心子集键）或 None（锚点/窗口无效）。
    """
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    if df["time"].isna().all():
        return None
    anchor_time = pd.to_datetime(anchor_time)
    op_end = pd.to_datetime(op_end)
    # ---- 锚点前窗口生命体征 ----
    m = (df["time"] >= anchor_time - pd.Timedelta(minutes=win)) & (df["time"] <= anchor_time)
    w = df[m]
    if w.empty or w["ART_MAP"].notna().sum() == 0:
        return None
    mapv = w["ART_MAP"].dropna().astype(float).values
    row = {}
    for name, arr in [("map", mapv)]:
        if len(arr):
            row[f"{name}_mean"] = float(arr.mean())
            row[f"{name}_max"] = float(arr.max())
            row[f"{name}_min"] = float(arr.min())
            row[f"{name}_sd"] = float(arr.std()) if len(arr) > 1 else 0.0
            row[f"{name}_last"] = float(arr[-1])
            row[f"{name}_n"] = int(len(arr))
            row[f"{name}_frac_below_65"] = float((arr < 65).mean())
            row[f"{name}_n_below_65"] = int((arr < 65).sum())
    # 人口学
    row["age"] = _to_float(demo.get("age"))
    row["male"] = 1 if str(demo.get("sex", "")).upper().startswith("M") else 0
    h = _to_float(demo.get("height")); wt = _to_float(demo.get("weight"))
    row["height_cm"] = h if (h and 100 <= h <= 220) else np.nan
    row["weight_kg"] = wt if (wt and 25 <= wt <= 300) else np.nan
    if row["height_cm"] and row["weight_kg"]:
        bmi = row["weight_kg"] / (row["height_cm"] / 100.0) ** 2
        row["bmi"] = bmi if 10 <= bmi <= 80 else np.nan
    else:
        row["bmi"] = np.nan
    row["bmi_missing"] = int(np.isnan(row["bmi"]))
    row["anchor_is_intubation"] = 0          # VitalDB 无此事件（恒 0，下游剔除）
    row["anchor_minus_or_start"] = 0.0       # 占位；实际以 anchor_minus_case_start 替代
    row["vitals_window_actual_min"] = float(
        (w["time"].max() - w["time"].min()).total_seconds() / 60.0) if len(w) else np.nan
    row["vitals_window_n_records"] = int(len(w))
    return row


def _to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


# ================================================================ 3. 模型复现 + 套用
def retrain_mover_xgb(mover_cfg_path, features_csv, labels_csv):
    """严格复用 s3 XGB 规格从 MOVER 数据重拟合；返回 (imputer, xgb_model, isotonic, feature_cols)。"""
    import yaml
    import xgboost as xgb
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    from sklearn.impute import SimpleImputer
    from sklearn.isotonic import IsotonicRegression

    with open(mover_cfg_path, encoding="utf-8") as f:
        mc = yaml.safe_load(f)
    X = pd.read_csv(features_csv).set_index("PID")
    y = pd.read_csv(labels_csv).set_index("PID")[mc["outcomes"]["primary_id"]].astype(int)
    common = X.index.intersection(y.index)
    X, y = X.loc[common], y.loc[common]
    X = X.select_dtypes(exclude="object")
    seed = mc["modeling"]["seed"]

    # 树模型用 NaN 原生矩阵；OOF isotonic 校准用同一 X
    xgb_model = xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                                  subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
                                  reg_lambda=1.0,
                                  scale_pos_weight=max(1.0, (y == 0).sum() / max(1, (y == 1).sum())),
                                  n_jobs=-1, random_state=seed, eval_metric="logloss")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof = cross_val_predict(xgb_model, X.values, y.values, cv=skf, method="predict_proba")[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip").fit(oof, y.values)
    xgb_model.fit(X.values, y.values)
    imp = SimpleImputer(strategy="median", add_indicator=True)  # 仅作缺失指示占位（树模型不强制需）
    imp.fit(X.values)
    return imp, xgb_model, iso, list(X.columns)


# ================================================================ 4. 命令行
def _selftest():
    """离线验证 D1 派生逻辑（无需 vitaldb 包/数据）。"""
    # 例1：12 次测量，恰好 4 次<65（8 个>=65 + 4 个<65）→ 4/12=0.333 >=0.30 → 阳性
    v1 = np.array([65, 70, 80, 90, 75, 72, 68, 66, 60, 64, 55, 62], dtype=float)
    pos, n, frac = derive_D1(v1, 65, 10, 0.30)
    assert pos and n == 12 and abs(frac - 4 / 12) < 1e-9, f"例1 失败: {pos,n,frac}"
    # 例2：12 次测量，恰好 3 次<65（9 个>=65 + 3 个<65）→ 3/12=0.25 <0.30 → 阴性
    v2 = np.array([65, 70, 80, 90, 75, 72, 68, 66, 71, 60, 64, 55], dtype=float)
    pos2, n2, frac2 = derive_D1(v2, 65, 10, 0.30)
    assert (not pos2) and n2 == 12 and abs(frac2 - 3 / 12) < 1e-9, f"例2 失败: {pos2,n2,frac2}"
    # 例3：仅 9 次测量 → 直接阴性（不足 min_measurements）
    v3 = np.array([50] * 9, dtype=float)
    pos3, n3, _ = derive_D1(v3, 65, 10, 0.30)
    assert (not pos3) and n3 == 9, f"例3 失败: {pos3,n3}"
    # 特征列选择
    cols = ["age", "male", "sg_CARDIAC", "ev_intubation", "map_mean", "drug_phenyl_n"]
    core = select_core_columns(cols)
    assert core == ["age", "male", "map_mean"], f"列选择失败: {core}"
    print("[selftest] D1 派生 + 特征列选择 全部通过 ✓")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["outcome", "features", "validate", "all"], default="all")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--config", default=os.path.join(HERE, "..", "config", "config_vitaldb.yaml"))
    ap.add_argument("--limit", type=int, default=None, help="调试：限下载 N 例")
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return

    cfg_path = os.path.abspath(args.config)
    # 数据获取与处理步骤需 vitaldb 包 + 账户 + 网络；本会话不可行，以下为契约实现骨架。
    raise SystemExit(
        "数据获取步需 VitalDB 账户 + 可联网环境：请 pip install vitaldb 后运行。\n"
        "离线可运行：python scripts/ext_pipeline.py --selftest")


if __name__ == "__main__":
    main()
