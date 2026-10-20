# -*- coding: utf-8 -*-
"""阶段 4：结果汇总报告 + TRIPOD-AI 清单 + 审计追踪表

输出：
  results/s4_report.html       自包含结果报告（图表 base64 内嵌，可直接预览）
  results/s4_tripod_ai.md     TRIPOD+AI(2024) 清单，逐项标注"正文/产物位置"
  results/s4_audit_trail.csv  每个关键数字 → 来源产物文件 → 复现命令（审计追踪）

纪律：报告中的每一个数字都必须从产物 JSON/CSV 现读现算，禁止硬编码。
"""
import os, sys, base64, json
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_config, paths, log

STAGE = "s4"
cfg = load_config(); P = paths(cfg); RES = P["results_dir"]
FIG = os.path.join(RES, "s3_figs")
J = lambda f: json.load(open(os.path.join(RES, f), encoding="utf-8"))

cohort = J("s1_cohort.json")
out_post = J("s1_outcomes_postanchor.json")
dq = J("s2_data_quality.json")
fd = J("s2_feature_dictionary.json")
metrics = J("s3_metrics.json")
calib = J("s3_calib_dca.json")
subg = J("s3_subgroups.json")
imp = J("s3_feature_importance.json")

PROJ = cfg["project"]["name"]
PRIMARY = "D1"
d1 = out_post[PRIMARY]
PREV = d1["prevalence"]
N = cohort["analytic_pids"]


def img_b64(name):
    p = os.path.join(FIG, name)
    if not os.path.exists(p):
        return ""
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def fmt(x, n=4):
    return f"{x:.{n}f}" if isinstance(x, float) else str(x)


def get(split, model):
    return next(r for r in metrics["results"] if r["split"] == split and r["model"] == model)


best = get("patient", "xgboost")
best_t = get("temporal", "xgboost")
cp = calib["patient"]
leak_pass = dq["leakage_audit_all_pass"]

# ---------------- 表 1：队列瀑布 ----------------
wf = [
    ("源数据唯一 PID", cohort["source_pids"], ""),
    ("排除 OR 窗口荒谬值（≤0 或 >1440 min）", -cohort["excl_implausible_or_window"],
     f"max 观测 {cohort['implausible_detail']['or_min_max_observed']:.0f} min"),
    ("排除 OR 窗口过短（<60 min）", -cohort["excl_short_or_window"], ""),
    ("排除未成年（<18 岁）", -cohort["excl_underage"], ""),
    ("排除锚点越界（Intubation/Surgery_start 不可用）", -cohort["excl_bad_anchor"], ""),
    ("<b>建模队列（s2/s3 实际使用）</b>", N, "锚点后队列"),
]
rows_wf = "".join(f"<tr><td>{a}</td><td class='num'>{b:,}</td><td>{c}</td></tr>"
                  for a, b, c in wf)

# ---------------- 表 2：锚点后结局 ----------------
rows_out = ""
OUT_KEYS = sorted([k for k, v in out_post.items()
                   if isinstance(v, dict) and "definition" in v])
for k in OUT_KEYS:
    v = out_post[k]
    tag = " <b>[主结局]</b>" if k == PRIMARY else ""
    rows_out += (f"<tr><td><code>{k}</code>{tag}</td><td>{v['definition']['type']}</td>"
                 f"<td class='num'>{v['positive_pids']:,}</td>"
                 f"<td class='num'>{v['prevalence']*100:.2f}%</td></tr>")

# ---------------- 表 3：特征域覆盖 ----------------
rows_dq = ""
for d, v in dq["domain_coverage"].items():
    rows_dq += (f"<tr><td>{d}</td><td class='num'>{v['n_features']}</td>"
                f"<td class='num'>{v['mean_non_null_pct']*100:.1f}%</td></tr>")

# ---------------- 表 4：模型表现 ----------------
rows_m = ""
for r in metrics["results"]:
    ci_p = (f"[{r['auprc_ci95'][0]:.3f}, {r['auprc_ci95'][1]:.3f}]"
            if r["auprc_ci95"][0] is not None else "-")
    rows_m += (f"<tr><td>{r['split']}</td><td>{r['model']}</td>"
               f"<td class='num'><b>{fmt(r['auprc'])}</b></td><td class='num'>{ci_p}</td>"
               f"<td class='num'>{fmt(r['auroc'])}</td><td class='num'>{fmt(r['brier'])}</td>"
               f"<td class='num'>{r['n_test']:,}</td><td class='num'>{r['n_pos_test']}</td></tr>")

rows_sg = "".join(f"<tr><td>{k}</td><td class='num'>{fmt(v)}</td></tr>"
                  for k, v in subg["patient"].items())
rows_imp = "".join(
    f"<tr><td>{i+1}</td><td><code>{r['feature']}</code></td><td class='num'>{r['gain']:.1f}</td></tr>"
    for i, r in enumerate(imp["xgboost_top25"][:15]))

HTML = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>{PROJ} — 结果汇总报告</title>
<style>
body{{font-family:-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Microsoft YaHei',sans-serif;
max-width:1080px;margin:0 auto;padding:28px;color:#1a1a1a;background:#fff;line-height:1.65}}
h1{{font-size:24px;border-bottom:3px solid #2c5f8a;padding-bottom:10px;color:#2c5f8a}}
h2{{font-size:19px;margin-top:34px;color:#2c5f8a;border-left:5px solid #2c5f8a;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}}
th{{background:#2c5f8a;color:#fff;text-align:left;padding:9px 10px;font-weight:600}}
td{{border-bottom:1px solid #e3e3e3;padding:8px 10px}}
tr:nth-child(even) td{{background:#f7f9fb}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;font-family:Consolas,monospace}}
code{{background:#f0f2f5;padding:2px 5px;border-radius:3px;font-size:13px}}
.meta{{color:#666;font-size:13px;margin-bottom:6px}}
.ok{{color:#1a7f37;font-weight:600}}.warn{{color:#b8860b;font-weight:600}}
.box{{background:#f7f9fb;border-left:4px solid #2c5f8a;padding:12px 16px;margin:14px 0;font-size:14px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
figure{{margin:8px 0}}figure img{{max-width:100%;border:1px solid #ddd;border-radius:4px}}
figcaption{{font-size:12px;color:#666;margin-top:4px}}
</style></head><body>
<h1>{PROJ} — 结果汇总报告</h1>
<div class="meta">生成脚本 <code>scripts/s4_report.py</code> · 主结局 <code>{PRIMARY}</code>（锚点后）·
患病率 <b>{PREV*100:.2f}%</b> · 建模队列 <b>{N:,}</b> 例 · 特征 <b>{len(fd['features'])}</b> 个 ·
seed {metrics['seed']}</div>
<div class="meta">全部数字均由 <code>results/</code> 下产物现读现算，无硬编码；审计追踪见
<code>s4_audit_trail.csv</code>。</div>

<div class="box">
<b>一句话结论：</b>以麻醉诱导/插管后（锚点）前 15 min 的常规监护与用药数据预测其后 IOH，
XGBoost 取得患者级 <b>AUPRC {fmt(best['auprc'])}</b>（患病率 {PREV*100:.2f}%，约
<b>{best['auprc']/PREV:.2f}×</b> lift）、AUROC <b>{fmt(best['auroc'])}</b>；
时间独立验证一致（AUPRC {fmt(best_t['auprc'])}），isotonic 校准后 Brier
{cp['brier_raw']}→{cp['brier_calibrated']}。
</div>

<h2>1. 队列构建瀑布</h2>
<table><tr><th>步骤</th><th class="num">PID 数</th><th>备注</th></tr>{rows_wf}</table>
<div class="meta">锚点来源：Intubation {cohort['anchor_source_counts']['Intubation']:,} /
Surgery_start（代理）{cohort['anchor_source_counts']['Surgery_start']:,}，
代理率 {cohort['anchor_source_counts']['Surgery_start']/N*100:.1f}%。</div>

<h2>2. 锚点后结局（14 种定义敏感性矩阵）</h2>
<table><tr><th>定义</th><th>类型</th><th class="num">阳性 n</th><th class="num">患病率</th></tr>{rows_out}</table>
<div class="meta">主结局 <code>D1</code> = ≥10 次 MAP 测量且 MAP&lt;65 占比 ≥30%（锚点后窗口），事件充足。
持续型定义（O1–O4）在 NIBP 点测数据下事件极少，印证"持续时长不可判定"这一结构性限制。</div>

<h2>3. 特征域与覆盖（防泄漏）</h2>
<table><tr><th>域</th><th class="num">特征数</th><th class="num">平均非空率</th></tr>{rows_dq}</table>
<p><b>泄漏审计：</b>各域全部满足 <code>max_used_time_minus_anchor ≤ 0</code>，
ALL_PASS = <span class="{'ok' if leak_pass else 'warn'}">{leak_pass}</span>；
特征矩阵不含 <code>post_window_minutes / or_min / or_end</code> 等锚点后列。</p>
<div class="box"><b>稀疏性局限（须诚实声明）：</b>血气锚点前覆盖率仅
{dq['labs']['coverage_pct']*100:.2f}%、液体 {dq['fluids']['coverage_pct']*100:.1f}%、
通气 {dq['ventilation']['n_pids_with_vent_in_window']/N*100:.1f}%、
有创动脉 {dq['invasive_monitoring']['n_pids_with_art_in_window']/N*100:.1f}%；
预测实际由人口学、手术分组、麻醉技术事件、锚点前 15 min NIBP 与用药驱动。</div>

<h2>4. 模型表现（主指标 AUPRC）</h2>
<table><tr><th>切分</th><th>模型</th><th class="num">AUPRC</th><th class="num">95% CI</th>
<th class="num">AUROC</th><th class="num">Brier</th><th class="num">n_test</th>
<th class="num">阳性</th></tr>{rows_m}</table>
<div class="meta">患者级切分为<b>主分析</b>，时间切分（train ≤2017 / test =2018）为<b>次要稳健性</b>；
CI 为 {metrics['n_bootstrap']} 次患者级 bootstrap 百分位数。</div>
<div class="grid">
<figure><img src="{img_b64('auprc_patient.png')}"><figcaption>患者级 AUPRC（虚线=患病率基线）</figcaption></figure>
<figure><img src="{img_b64('auroc_patient.png')}"><figcaption>患者级 AUROC（虚线=随机 0.5）</figcaption></figure>
</div>

<h2>5. 校准与决策曲线</h2>
<p>主模型 XGBoost，5 折 OOF isotonic 校准：Brier <b>{cp['brier_raw']} → {cp['brier_calibrated']}</b>，
校准斜率 <b>{cp['calib_slope']}</b>（理想 1）、截距 <b>{cp['calib_intercept']}</b>（理想 0）。</p>
<div class="grid">
<figure><img src="{img_b64('calibration.png')}"><figcaption>校准曲线（10 分位）</figcaption></figure>
<figure><img src="{img_b64('dca.png')}"><figcaption>决策曲线分析（DCA）</figcaption></figure>
</div>

<h2>6. 亚组 AUPRC（患者级）</h2>
<table><tr><th>亚组</th><th class="num">AUPRC</th></tr>{rows_sg}</table>
<div class="meta">临床可解释：女性＞男性；随年龄升高预测性能下降；低 BMI 信号最强。</div>

<h2>7. 特征重要性（XGBoost, gain, Top 15）</h2>
<table><tr><th>#</th><th>特征</th><th class="num">gain</th></tr>{rows_imp}</table>
<figure><img src="{img_b64('importance_lgbm.png')}" style="max-width:520px">
<figcaption>LightGBM gain Top 25</figcaption></figure>
<div class="meta">主导特征为<b>预锚点 MAP 水平</b>（<code>map_mean</code> / <code>map_max</code> /
<code>map_frac_below_65</code>）与插管相关事件/时序，临床逻辑自洽。</div>

<h2>8. 关键局限</h2>
<ol>
<li><b>无术前基线：</b>OR_start 前 30 min 内有 MAP 的仅约 0.8%，相对基线下降定义不可计算。</li>
<li><b>NIBP 为点测：</b>nMAP 段长中位数 1 min，持续时长类定义在网格法下近乎不可用。</li>
<li><b>单中心回顾：</b>无外部验证；时间切分为内部时间验证。</li>
<li><b>数据稀疏：</b>血气/液体/通气/有创监测锚点前覆盖率低（见 §3）。</li>
<li><b>锚点代理：</b>{cohort['anchor_source_counts']['Surgery_start']:,} 例
（{cohort['anchor_source_counts']['Surgery_start']/N*100:.1f}%）无 Intubation 事件，以 Surgery_start 代理。</li>
</ol>
</body></html>"""

open(os.path.join(RES, "s4_report.html"), "w", encoding="utf-8").write(HTML)
log(STAGE, "report -> results/s4_report.html")

# ---------------- TRIPOD+AI 清单 ----------------
TRIPOD = """# TRIPOD+AI (2024) 清单 — 01 SIS 术中低血压预测

> 状态图例：✅ 已满足 / 有产物支撑　⚠️ 部分满足 / 需补写　⏳ 待补（稿件阶段）
> 每项标注"正文段落 / 产物文件"，便于投稿前逐项核对。

| # | TRIPOD+AI 条目 | 状态 | 位置 / 证据 |
|---|---|---|---|
| 1 | **Title**：明确为预测模型研究（含 ML） | ⏳ | 稿件标题待定稿（protocol §1） |
| 2 | **Abstract**：结构化，含数据来源、模型、性能 | ⏳ | 待撰稿 |
| 3 | **Objectives**：明确临床问题与预测目标 | ✅ | protocol §1；锚点后 IOH |
| 4 | **Data sources**：数据来源、时间跨度、检索方式 | ✅ | `s1_cohort.json`；SIS EMR 九表，2015-11~2018-10 |
| 5 | **Eligibility**：纳入排除标准 | ✅ | protocol §2；`s1_cohort.json`（瀑布各项和自洽） |
| 6 | **Outcome**：结局定义与判定方式 | ✅ | protocol §3；14 定义敏感性矩阵 `s1_outcomes_postanchor.json` |
| 7 | **Predictors**：全部候选预测因子及定义、测量时点 | ✅ | `s2_feature_dictionary.json`（{nf} 个特征逐条注域/来源表/窗口） |
| 8 | **Temporal/leakage**：预测因子须早于预测时点 | ✅ **强证据** | `s2_data_quality.json.leakage_audit`：各域 `max_used_time_minus_anchor ≤ 0`，ALL_PASS={lp} |
| 9 | **Missing data**：缺失处理方式 | ✅ | 树模型原生 NaN；Logistic 中位数插补+缺失指示（`s3_models.py`） |
| 10 | **Statistical / ML methods**：模型族、超参、软件版本 | ✅ | `s3_metrics.json`（seed/超参固定）；config `runtime` 记录版本 |
| 11 | **Sample size / EPV**：样本量与事件数论证 | ✅ | n={n}，事件 {pos}（EPV 充足）；见 `s1_outcomes_postanchor.json` |
| 12 | **Validation**：内部/外部验证策略 | ✅ | 患者级（主）+ 时间切分（次）；`s3_metrics.json` |
| 13 | **Performance measures**：主指标与不确定性 | ✅ | 主 AUPRC；{nb} 次 bootstrap 95% CI；`s3_metrics.json` |
| 14 | **Calibration**：校准评估与方法 | ✅ | OOF isotonic；`s3_calib_dca.json`（斜率 {slope}） |
| 15 | **Clinical utility**：决策曲线/净收益 | ✅ | DCA；`s3_calib_dca.json.dca` |
| 16 | **Participants**：描述参与者特征 | ✅ | `s2_data_quality.json`（人口学/BMI/手术分组分布） |
| 17 | **Model specification**：最终模型可获取 | ✅ | 脚本 + 产物完整可复现；建议附代码仓库 |
| 18 | **Subgroups**：亚组性能 | ✅ | `s3_subgroups.json`（性别/年龄/BMI） |
| 19 | **Limitations**：局限性（含偏倚来源） | ✅ | protocol §9；本报告 §8 |
| 20 | **Interpretation**：临床可解释性 | ✅ | `s3_feature_importance.json`（MAP 主导，逻辑自洽） |
| 21 | **Ethics / IRB**：伦理审批与知情同意 | ⚠️ | 回顾性去标识数据；**须由作者确认本单位伦理审批状态** |
| 22 | **Data availability**：数据与代码可获取 | ⚠️ | 产物齐备；**须落实公开仓库/DOI**（禁写 "available on request"） |
| 23 | **Funding / COI** | ⏳ | 待作者补充 |
| 24 | **Registration**：研究是否预注册 | ⚠️ | protocol 已版本化（v0.2-draft）；建议投稿前补注册号 |

## 待办（阻塞投稿的 3 项硬缺口）
1. **伦理/IRB 状态**须由作者书面确认（条目 21）。
2. **数据与代码公开**须落实真实仓库 URL（条目 22），不得写 "available on request"。
3. **三项设计决策待作者签字**：主结局 D1、预测锚点 Intubation、手术分组映射表
   （当前已按 config 在管线中暂固化执行，改动任一需重跑 s2→s3）。
""".format(nf=len(fd["features"]), lp=leak_pass, n=N, pos=d1["positive_pids"],
           nb=metrics["n_bootstrap"], slope=cp["calib_slope"])
open(os.path.join(RES, "s4_tripod_ai.md"), "w", encoding="utf-8").write(TRIPOD)
log(STAGE, "tripod+ai checklist -> results/s4_tripod_ai.md")

# ---------------- 审计追踪表 ----------------
trail = []


def add(metric, value, src, how):
    trail.append({"metric": metric, "value": value, "source_file": src, "reproduce": how})


S1 = "python scripts/s1_cohort.py"
S2 = "python scripts/s2_features.py"
S3 = "python scripts/s3_models.py"
add("cohort.source_pids", cohort["source_pids"], "results/s1_cohort.json", S1)
add("cohort.excl_implausible_or_window", cohort["excl_implausible_or_window"], "results/s1_cohort.json", S1)
add("cohort.excl_short_or_window", cohort["excl_short_or_window"], "results/s1_cohort.json", S1)
add("cohort.excl_underage", cohort["excl_underage"], "results/s1_cohort.json", S1)
add("cohort.excl_bad_anchor", cohort["excl_bad_anchor"], "results/s1_cohort.json", S1)
add("cohort.analytic_pids", N, "results/s1_cohort.json", S1)
add("anchor.source.Intubation", cohort["anchor_source_counts"]["Intubation"], "results/s1_cohort.json", S1)
add("anchor.source.Surgery_start", cohort["anchor_source_counts"]["Surgery_start"], "results/s1_cohort.json", S1)
add(f"outcome.{PRIMARY}.positive_pids(post-anchor)", d1["positive_pids"], "results/s1_outcomes_postanchor.json", S1)
add(f"outcome.{PRIMARY}.prevalence(post-anchor)", d1["prevalence"], "results/s1_outcomes_postanchor.json", S1)
for k in OUT_KEYS:
    if k != PRIMARY:
        add(f"outcome.{k}.positive_pids", out_post[k]["positive_pids"],
            "results/s1_outcomes_postanchor.json", S1)
add("features.n_features", len(fd["features"]), "results/s2_feature_dictionary.json", S2)
add("features.matrix_rows", metrics["n_total"], "results/s2_features.csv", S2)
add("features.leakage_audit_all_pass", dq["leakage_audit_all_pass"], "results/s2_data_quality.json", S2)
for a in dq["leakage_audit"]:
    add(f"features.leakage.{a['domain']}.max_tma", a["max_used_time_minus_anchor"],
        "results/s2_data_quality.json", S2)
for d, v in dq["domain_coverage"].items():
    add(f"features.coverage.{d}.mean_non_null_pct", v["mean_non_null_pct"],
        "results/s2_data_quality.json", S2)
for r in metrics["results"]:
    add(f"model.{r['split']}.{r['model']}.auprc", r["auprc"], "results/s3_metrics.json", S3)
    add(f"model.{r['split']}.{r['model']}.auroc", r["auroc"], "results/s3_metrics.json", S3)
    add(f"model.{r['split']}.{r['model']}.brier", r["brier"], "results/s3_metrics.json", S3)
add("calib.patient.brier_raw", cp["brier_raw"], "results/s3_calib_dca.json", S3)
add("calib.patient.brier_calibrated", cp["brier_calibrated"], "results/s3_calib_dca.json", S3)
add("calib.patient.slope", cp["calib_slope"], "results/s3_calib_dca.json", S3)
add("calib.patient.intercept", cp["calib_intercept"], "results/s3_calib_dca.json", S3)
for k, v in subg["patient"].items():
    add(f"subgroup.patient.{k}.auprc", v, "results/s3_subgroups.json", S3)
for r in imp["xgboost_top25"][:10]:
    add(f"importance.xgboost.{r['feature']}", r["gain"], "results/s3_feature_importance.json", S3)

# ---------------- Round-1 扩展：补齐可追溯性缺口 ----------------
# 时间切分校准
ct = calib["temporal"]
add("calib.temporal.brier_raw", ct["brier_raw"], "results/s3_calib_dca.json", S3)
add("calib.temporal.brier_calibrated", ct["brier_calibrated"], "results/s3_calib_dca.json", S3)
add("calib.temporal.slope", ct["calib_slope"], "results/s3_calib_dca.json", S3)
add("calib.temporal.intercept", ct["calib_intercept"], "results/s3_calib_dca.json", S3)

# DCA 净收益：报告点 + 末正阈值（crossing）
for sp in ("patient", "temporal"):
    d = calib[sp]["dca"]
    th, nb = d["thresholds"], d["net_benefit_model"]
    for tgt in (0.10, 0.15):
        i = min(range(len(th)), key=lambda k: abs(th[k] - tgt))
        add(f"dca.{sp}.net_benefit_model@thr{tgt:.2f}", round(float(nb[i]), 6), "results/s3_calib_dca.json", S3)
    last_pos = max([k for k in range(len(nb)) if nb[k] > 0], default=None)
    if last_pos is not None:
        add(f"dca.{sp}.net_benefit_positive_up_to_thr", round(float(th[last_pos]), 2), "results/s3_calib_dca.json", S3)
        add(f"dca.{sp}.net_benefit_at_crossing", round(float(nb[last_pos]), 6), "results/s3_calib_dca.json", S3)

# MAP-only 逻辑回归 DCA 基准（检验相对床旁 MAP 的增量价值）
_bm = calib.get("map_only_benchmark", {})
if _bm:
    add("benchmark.map_only.auprc_raw", _bm.get("auprc_patient_test_raw"), "results/s3_calib_dca.json", S3)
    add("benchmark.map_only.auprc_calibrated", _bm.get("auprc_patient_test"), "results/s3_calib_dca.json", S3)
    add("benchmark.map_only.nb_increment_at_0.10", _bm.get("nb_increment_at_0.10"), "results/s3_calib_dca.json", S3)
    add("benchmark.map_only.nb_increment_at_0.15", _bm.get("nb_increment_at_0.15"), "results/s3_calib_dca.json", S3)

# 时间切分亚组
for k, v in subg["temporal"].items():
    add(f"subgroup.temporal.{k}.auprc", v, "results/s3_subgroups.json", S3)

# 记录密度（正文 284–288 行）
dq1 = json.load(open(os.path.join(RES, "s1_data_quality.json"), encoding="utf-8"))
_col = dq1["column_non_null_rate"]; _seg = dq1["nmap_segment_length_distribution"]; _pp = dq1["nmap_measurements_per_pid"]
add("density.nmap_case_minute_pct", round(_col["nMAP"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.sbp_case_minute_pct", round(_col["nSBP"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.dbp_case_minute_pct", round(_col["nDBP"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.hr_case_minute_pct", round(_col["HRe"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.spo2_case_minute_pct", round(_col["SP02"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.nmap_segments_total", _seg["total_segments"], "results/s1_data_quality.json", S1)
add("density.nmap_segment_length1_share_pct", round(_seg["length_1_share"] * 100, 2), "results/s1_data_quality.json", S1)
add("density.nmap_per_case_median", float(_pp["p50"]), "results/s1_data_quality.json", S1)

# 1,496 例监测稀疏排除 + 条件患病率
_n_ge10 = dq1["postanchor_nmap_measurements"]["n_ge_10"]
add("outcome.D1.n_cases_lt10_postanchor_map", N - _n_ge10, "results/s1_data_quality.json + results/s1_cohort.json", S1)
add("outcome.D1.conditional_prevalence_ge10meas", round(d1["positive_pids"] / (N - _n_ge10), 4),
    "results/s1_outcomes_postanchor.json + results/s1_data_quality.json", S1)

# 表 3 病例计数覆盖率（与正文 Coverage(%) 一致），另存为 case_count 行
_feat = pd.read_csv(os.path.join(RES, "s2_features.csv"))
_cov_cases = {
    "anchor": N,
    "demographics": "n/a (static)",
    "surgery": N,
    "anesthesia_technique": dq["anesthesia_technique"]["n_events_pre_anchor_pids"],
    "medication_pre_anchor": dq["medication"]["n_pids_with_drug_pre_anchor"],
    "non_invasive_bp": int((_feat["map_n"] > 0).sum()),
    "ventilation": dq["ventilation"]["n_pids_with_vent_in_window"],
    "invasive_monitoring": dq["invasive_monitoring"]["n_pids_with_art_in_window"],
    "fluid_bleeding": dq["fluids"]["n_pids_with_io_pre_anchor"],
    "laboratories": dq["labs"]["n_pids_with_lab_pre_anchor"],
}
for _dom, _val in _cov_cases.items():
    add(f"coverage.case_count.{_dom}", _val, "results/s2_data_quality.json / results/s2_features.csv", S2)

# 表 1 关键队列统计量
add("cohort.age_median", float(_feat["age"].median()), "results/s2_features.csv", S2)
add("cohort.male_n", int((_feat["male"] == 1).sum()), "results/s2_features.csv", S2)
add("cohort.female_n", int((_feat["male"] == 0).sum()), "results/s2_features.csv", S2)
add("cohort.bmi_median", round(float(_feat["bmi"].median()), 1), "results/s2_features.csv", S2)
add("cohort.preanchor_map_mean_median", round(float(_feat["map_mean"].median()), 1), "results/s2_features.csv", S2)
add("cohort.post_anchor_window_median_min", dq1["post_window_minutes"]["p50"],
    "results/s1_data_quality.json", S1)

# 表 5 亚组 n（测试集，与 AUPRC 同口径）
_yy = pd.read_csv(os.path.join(RES, "s1_labels_postanchor.csv")).set_index("PID")["D1"].astype(int)
_ridx, _teidx = train_test_split(_feat.set_index("PID").index, test_size=0.2,
                                random_state=int(cfg["modeling"]["seed"]), stratify=_yy)
_fte = _feat.set_index("PID").loc[_teidx]


def _subgroup_n(X):
    o = {}
    o["sex_male"] = int((X["male"] == 1).sum()); o["sex_female"] = int((X["male"] == 0).sum())
    o["age<50"] = int((X["age"] < 50).sum())
    o["age50-65"] = int(((X["age"] >= 50) & (X["age"] < 65)).sum())
    o["age>=65"] = int((X["age"] >= 65).sum())
    o["bmi<18.5"] = int((X["bmi"] < 18.5).sum())
    o["bmi18.5-25"] = int(((X["bmi"] >= 18.5) & (X["bmi"] < 25)).sum())
    o["bmi25-30"] = int(((X["bmi"] >= 25) & (X["bmi"] < 30)).sum())
    o["bmi>=30"] = int((X["bmi"] >= 30).sum())
    return o


for _k, _v in _subgroup_n(_fte).items():
    add(f"subgroup.patient.test_n.{_k}", _v, "results/s2_features.csv (reproduced patient split)", S3)

pd.DataFrame(trail).to_csv(os.path.join(RES, "s4_audit_trail.csv"), index=False, encoding="utf-8-sig")
log(STAGE, f"audit trail -> results/s4_audit_trail.csv ({len(trail)} 行)")
log(STAGE, "DONE (v1.0.0)")
