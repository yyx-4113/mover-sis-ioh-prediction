# -*- coding: utf-8 -*-
"""外部验证 Stage 1: 下载 VitalDB 开放数据集的所需生命体征轨（公开端点，免登录）。

只下载动脉 MAP 队列（Solar8000/ART_MBP 或 EV1000/ART_MBP）的 6 种生命体征轨：
  map (ART_MBP, 缺则 NIBP_MBP), sbp (ART_SBP, 缺则 NIBP_SBP), dbp (ART_DBP, 缺则 NIBP_DBP),
  hr (Solar8000/HR), hrp (Solar8000/PLETH_HR), spo2 (Solar8000/PLETH_SPO2)
轨端点: https://api.vitaldb.net/<tid> （gzip，公开）。结果缓存到 data_vitaldb/tracks/<signal>/<caseid>.csv.gz。

用法:
  python scripts/ext_download.py [--max-cases N] [--workers 12]
"""
import os, sys, json, argparse, subprocess
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data_vitaldb")
TRK = os.path.join(DATA, "tracks")
os.makedirs(TRK, exist_ok=True)

SIGNAL_TNAMES = {
    "map":  ["Solar8000/ART_MBP", "EV1000/ART_MBP", "Solar8000/NIBP_MBP"],
    "sbp":  ["Solar8000/ART_SBP", "Solar8000/NIBP_SBP"],
    "dbp":  ["Solar8000/ART_DBP", "Solar8000/NIBP_DBP"],
    "hr":   ["Solar8000/HR"],
    "hrp":  ["Solar8000/PLETH_HR"],
    "spo2": ["Solar8000/PLETH_SPO2"],
}


def build_case_signal_map(max_cases=None):
    trks = pd.read_csv(os.path.join(DATA, "trks.csv"))
    # arterial MAP cohort
    art = trks[trks.tname.isin(["Solar8000/ART_MBP", "EV1000/ART_MBP"])]
    cases = sorted(art.caseid.unique())
    if max_cases:
        cases = cases[:max_cases]
    # tid lookup: (tname, caseid) -> tid (prefer first occurrence if duplicates)
    tid_map = {}
    for _, r in trks.iterrows():
        tid_map.setdefault((r.tname, int(r.caseid)), r.tid)
    plan = []  # (caseid, signal, tid)
    for cid in cases:
        for sig, tnames in SIGNAL_TNAMES.items():
            chosen_tid = None
            for tn in tnames:
                tid = tid_map.get((tn, int(cid)))
                if tid is not None:
                    chosen_tid = tid
                    break
            if chosen_tid is not None:
                plan.append((int(cid), sig, str(chosen_tid)))
    return cases, plan


def cache_path(signal, caseid):
    d = os.path.join(TRK, signal)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{caseid}.csv.gz")


def download_one(args):
    caseid, signal, tid = args
    out = cache_path(signal, caseid)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return ("skip", caseid, signal)
    url = f"https://api.vitaldb.net/{tid}"
    for attempt in range(4):
        try:
            r = subprocess.run(
                ["curl", "-sS", "-m", "30", "--noproxy", "*", "-o", out, url],
                capture_output=True, timeout=40)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) >= 50:
                return ("ok", caseid, signal)
            # 残留空/小文件清理
            if os.path.exists(out):
                os.remove(out)
        except Exception:
            if os.path.exists(out):
                try: os.remove(out)
                except Exception: pass
    return ("fail", caseid, signal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-cases", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    cases, plan = build_case_signal_map(args.max_cases)
    print(f"[ext-download] arterial-MAP cohort: {len(cases)} cases; planned track downloads: {len(plan)}")

    from concurrent.futures import ThreadPoolExecutor
    stats = {"ok": 0, "skip": 0, "fail": 0}
    fails = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for status, cid, sig in ex.map(download_one, plan):
            stats[status] = stats.get(status, 0) + 1
            if status == "fail":
                fails.append((cid, sig))
    print(f"[ext-download] done: {stats}")
    if fails:
        print(f"[ext-download] FAILED {len(fails)} downloads (first 20):")
        for cid, sig in fails[:20]:
            print("   ", cid, sig)
    # manifest
    man = {"n_cases": len(cases), "n_planned": len(plan), "stats": stats, "fails": fails}
    with open(os.path.join(DATA, "download_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(f"[ext-download] manifest -> data_vitaldb/download_manifest.json")


if __name__ == "__main__":
    main()
