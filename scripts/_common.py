# -*- coding: utf-8 -*-
"""共享工具：config 加载、路径解析、阶段日志、产物写入、手术分组。
所有阶段脚本从这里导入；禁止各脚本自行拼路径。"""
import json, os, sys, datetime

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)                      # directions/01_.../
CFG_PATH = os.path.join(PROJ, "config", "config.yaml")

# SIS 各表缺失值为 MySQL 风格 \N
SIS_NA = ["\\N"]

# SIS 时间字段有两种格式，按表固定（2026-10-19 实测）：
#   ISO  "%Y-%m-%d %H:%M:%S" —— vitals / observations / labs / input_output / procedure_events
#   美式 "%m/%d/%y %H:%M"     —— ventilator / medication
DT_ISO = "%Y-%m-%d %H:%M:%S"
DT_US = "%m/%d/%y %H:%M"


def parse_dt(series, fmt=DT_ISO):
    """双格式时间解析：先按主格式，剩余非空元素按美式格式重试。"""
    s = series.astype("string")
    t = pd.to_datetime(s, format=fmt, errors="coerce")
    m = t.isna() & s.notna() & (s.str.strip() != "")
    if m.any():
        t2 = pd.to_datetime(s[m], format=DT_US, errors="coerce")
        t.loc[m] = t2
    return t


def load_config():
    try:
        import yaml
    except ImportError:
        sys.exit("pyyaml missing: pip install pyyaml (into the managed venv)")
    with open(CFG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def paths(cfg):
    """把 config 里的相对路径解析为绝对路径。"""
    root = os.path.normpath(os.path.join(PROJ, cfg["paths"]["workspace_root"]))
    p = {k: (os.path.normpath(os.path.join(PROJ, v)) if not os.path.isabs(v) else v)
         for k, v in cfg["paths"].items()}
    p["workspace_root"] = root
    p["sis_emr_dir"] = os.path.normpath(os.path.join(PROJ, cfg["paths"]["sis_emr_dir"]))
    return p


def log(stage, msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] [{stage}] {msg}", flush=True)


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    log("io", f"saved -> {os.path.relpath(path, PROJ)}")


def require(path, what):
    if not os.path.exists(path):
        sys.exit(f"MISSING {what}: {path}\n请先确认数据已解压/下载到位。")
    return path


def norm_procedure_text(series):
    """Procedure 自由文本归一化：小写、非字母数字转空格、压缩连续空格。"""
    import re
    s = series.fillna("").astype(str).str.lower()
    return s.str.replace(r"[^a-z0-9 ]", " ", regex=True).str.replace(r"\s+", " ", regex=True)


def assign_procedure_group(text_series, keywords, fuzzy=True):
    """手术文本 → 分组。

    顺序即优先级：按 keywords 字典序逐个关键词匹配，首个命中的组生效。
    fuzzy=True 时对仍未命中的文本做受控模糊兜底（编辑距离<=1、首字符相同、
    词长>=7），用于吸收拼写变体（如 laparascopy/LAPARASCOPY）。

    返回 (groups: pd.Series, fuzzy_log: list[dict])。
    """
    import numpy as np
    from difflib import SequenceMatcher

    norm = norm_procedure_text(text_series)
    matched = pd.Series("OTHER", index=norm.index)
    for gname, kws in keywords.items():
        for kw in kws:
            m = (matched == "OTHER") & norm.str.contains(kw, regex=False)
            matched[m] = gname

    fuzzy_log = []
    if fuzzy:
        kwset = {}
        for g, kws in keywords.items():
            for kw in kws:
                kwset.setdefault(kw, g)
        for i in np.where(matched == "OTHER")[0]:
            t = norm.iloc[i]
            if not t.strip():
                continue
            for tok in t.split():
                if len(tok) < 7:
                    continue
                for kw, g in kwset.items():
                    if len(kw) < 7 or kw[0] != tok[0]:
                        continue
                    if abs(len(kw) - len(tok)) > 1:
                        continue
                    if SequenceMatcher(None, tok, kw).ratio() >= 0.90:
                        matched.iloc[i] = g
                        fuzzy_log.append({"pid": str(text_series.index[i]),
                                          "text": str(text_series.iloc[i]),
                                          "token": tok, "matched_kw": kw, "group": g})
                        break
                else:
                    continue
                break
    return matched, fuzzy_log
