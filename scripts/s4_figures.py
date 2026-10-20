"""生成 manuscript 图 1-5 独立 PNG（匹配图注）。所有数值现读现算自产物文件。"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans",
                     "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 130})

RES = "results"
FIG = os.path.join(RES, "figs")
os.makedirs(FIG, exist_ok=True)
MCOLOR = {"baseline_logit": "#9467bd", "logistic_full": "#8c564b",
          "xgboost": "#1f77b4", "lightgbm": "#2ca02c"}


def save(fig, name):
    p = os.path.join(FIG, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  wrote", p)


# ============================================================ Fig 1 队列构建瀑布
def fig1():
    c = json.load(open(os.path.join(RES, "s1_cohort.json")))
    src = c["source_pids"]
    steps = [
        (f"Screened records\n(n = {src:,})", None),
        ("Excluded: implausible OR window", c["excl_implausible_or_window"]),
        (f"Remaining\n(n = {src - c['excl_implausible_or_window']:,})", None),
        ("Excluded: OR window < 60 min", c["excl_short_or_window"]),
        (f"Remaining\n(n = {src - c['excl_implausible_or_window'] - c['excl_short_or_window']:,})", None),
        ("Excluded: age < 18 years", c["excl_underage"]),
        (f"Cohort after eligibility\n(n = {src - c['excl_implausible_or_window'] - c['excl_short_or_window'] - c['excl_underage']:,})", None),
        ("Excluded: absent / out-of-window anchor", c["excl_bad_anchor"]),
        (f"Analysed cohort\n(n = {c['analytic_pids']:,})", None),
    ]
    asc = c["anchor_source_counts"]
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    ax.axis("off")
    y = 0.96
    dy = 0.095
    for i, (label, excl) in enumerate(steps):
        if excl is None:
            ax.add_patch(plt.Rectangle((0.18, y - 0.06), 0.64, 0.075,
                         facecolor="#cfe2f3", edgecolor="#1f77b4", lw=1.2))
            ax.text(0.5, y - 0.0225, label, ha="center", va="center", fontsize=10.5)
        else:
            ax.text(0.84, y - 0.0225, f"– {excl:,}", ha="left", va="center",
                    fontsize=9, color="#c0392b")
            ax.text(0.5, y - 0.0225, label, ha="center", va="center", fontsize=9, color="#7f3b3b")
        if i < len(steps) - 1:
            ax.annotate("", xy=(0.5, y - dy + 0.01), xytext=(0.5, y - 0.06),
                        arrowprops=dict(arrowstyle="-|>", color="#444", lw=1.1))
        y -= dy
    ax.text(0.5, 0.02,
            f"Prediction anchor: Intubation {asc['Intubation']:,} ({asc['Intubation']/c['analytic_pids']*100:.1f}%)  |  "
            f"Surgery start {asc['Surgery_start']:,} ({asc['Surgery_start']/c['analytic_pids']*100:.1f}%)",
            ha="center", va="center", fontsize=9.5, style="italic",
            bbox=dict(boxstyle="round", fc="#fff3cd", ec="#e0a800", lw=1))
    ax.set_title("Figure 1. Cohort construction", fontsize=12, weight="bold")
    save(fig, "fig1_cohort.png")


# ============================================================ Fig 2 14 定义患病率
def fig2():
    d = json.load(open(os.path.join(RES, "s1_outcomes_postanchor.json")))
    rows = []
    for k, v in d.items():
        if isinstance(v, dict) and "definition" in v:
            rows.append((k, v["positive_pids"], v["prevalence"]))
    rows.sort(key=lambda r: r[2])
    ids = [r[0] for r in rows]
    prev = [r[2] * 100 for r in rows]
    colors = ["#c0392b" if r[0] == "D1" else "#1f77b4" for r in rows]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ypos = np.arange(len(ids))
    ax.barh(ypos, prev, color=colors)
    ax.set_yticks(ypos); ax.set_yticklabels(ids, fontsize=9)
    for i, p in enumerate(prev):
        ax.text(p + 0.3, i, f"{p:.1f}%", va="center", fontsize=8)
    ax.set_xlabel("Prevalence after prediction anchor (%)")
    ax.set_xlim(0, max(prev) * 1.15)
    ax.set_title("Figure 2. Prevalence of 14 candidate outcome definitions (D1 highlighted)",
                 fontsize=11, weight="bold")
    ax.grid(axis="y", alpha=0)
    save(fig, "fig2_definitions.png")


# ============================================================ Fig 3 PR + ROC（患者级）
def fig3():
    curves = json.load(open(os.path.join(RES, "s3_curves.json")))
    met = json.load(open(os.path.join(RES, "s3_metrics.json")))["results"]
    mmap = {(r["split"], r["model"]): r for r in met}
    pc = curves["patient"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4))
    for name in ["baseline_logit", "logistic_full", "xgboost", "lightgbm"]:
        pr = pc[name]["pr"]; roc = pc[name]["roc"]
        m = mmap[("patient", name)]
        ax1.plot(pr["recall"], pr["precision"], color=MCOLOR[name], lw=1.6,
                 label=f"{name} (AUPRC={m['auprc']:.3f})")
        ax2.plot(roc["fpr"], roc["tpr"], color=MCOLOR[name], lw=1.6,
                 label=f"{name} (AUROC={m['auroc']:.3f})")
    ax1.set_xlabel("Recall"); ax1.set_ylabel("Precision")
    ax1.set_ylim(0, 1.02); ax1.set_xlim(0, 1.02)
    ax1.set_title("Precision–recall (patient-level)", fontsize=10.5)
    ax1.legend(fontsize=7.5, loc="upper right")
    ax2.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6)
    ax2.set_xlabel("False positive rate"); ax2.set_ylabel("True positive rate")
    ax2.set_ylim(0, 1.02); ax2.set_xlim(0, 1.02)
    ax2.set_title("ROC (patient-level)", fontsize=10.5)
    ax2.legend(fontsize=7.5, loc="lower right")
    fig.suptitle("Figure 3. Model performance", fontsize=12, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, "fig3_pr_roc.png")


# ============================================================ Fig 4 校准 + DCA
def fig4():
    cd = json.load(open(os.path.join(RES, "s3_calib_dca.json")))["patient"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4))
    raw = cd["calibration_curve_raw"]; cal = cd["calibration_curve"]
    ax1.plot(raw["mean_pred"], raw["frac_pos"], "s--", color="#c0392b", lw=1.3,
             label="before recalibration")
    ax1.plot(cal["mean_pred"], cal["frac_pos"], "o-", color="#1f77b4", lw=1.6,
             label="after isotonic recalibration")
    ax1.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6, label="ideal")
    ax1.set_xlabel("Predicted probability"); ax1.set_ylabel("Observed fraction")
    ax1.set_title(f"Calibration (slope={cd['calib_slope']:.3f}, "
                  f"int={cd['calib_intercept']:.3f})", fontsize=10.5)
    ax1.legend(fontsize=8, loc="upper left")
    g = cd["dca"]["thresholds"]
    ax2.plot(g, cd["dca"]["net_benefit_model"], color="#1f77b4", lw=1.8, label="model (full)")
    ax2.plot(g, cd["dca"]["net_benefit_treat_all"], color="#c0392b", lw=1.3, label="treat all")
    ax2.plot(g, cd["dca"]["net_benefit_treat_none"], color="#7f7f7f", lw=1.3, label="treat none")
    bm = json.load(open(os.path.join(RES, "s3_calib_dca.json"))).get("map_only_benchmark")
    if bm:
        g2 = bm["dca"]["thresholds"]
        ax2.plot(g2, bm["dca"]["net_benefit_model"], color="#888888", lw=1.4, ls=":",
                 label="MAP-only logistic")
    ax2.set_xlabel("Threshold probability"); ax2.set_ylabel("Net benefit")
    ax2.set_title("Decision curve analysis", fontsize=10.5)
    ax2.legend(fontsize=7.5, loc="upper right")
    fig.suptitle("Figure 4. Calibration and decision curve analysis (XGBoost, patient-level)",
                 fontsize=12, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, "fig4_calib_dca.png")


# ============================================================ Fig 5 XGBoost 重要性
def fig5():
    imp = json.load(open(os.path.join(RES, "s3_feature_importance.json")))["xgboost_top25"]
    imp = sorted(imp, key=lambda r: r["gain"])
    names = [r["feature"] for r in imp]
    gains = [r["gain"] for r in imp]
    fig, ax = plt.subplots(figsize=(7.5, 8))
    ypos = np.arange(len(names))
    ax.barh(ypos, gains, color="#1f77b4")
    ax.set_yticks(ypos); ax.set_yticklabels(names, fontsize=8.5)
    ax.set_xlabel("Gain (XGBoost)")
    ax.set_title("Figure 5. Twenty-five highest-gain predictors (XGBoost)",
                 fontsize=11, weight="bold")
    ax.grid(axis="y", alpha=0)
    save(fig, "fig5_importance.png")


if __name__ == "__main__":
    print("Generating Fig 1-5 ...")
    fig1(); fig2(); fig3(); fig4(); fig5()
    print("DONE.")
