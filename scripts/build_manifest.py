#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild MANIFEST.csv (SHA-256 checksums) for the published reproduction package.

Policy (release-notes contract): the public tree ships **aggregate artefacts only**.
Per-case derived CSVs (feature matrices, outcome labels, test-set predictions,
external per-case tables) are regenerable from the source databases under the
DUA and are excluded, as are internal working files (review/, STATUS.md, ...).

Usage:  python scripts/build_manifest.py          # writes MANIFEST.csv
        python scripts/build_manifest.py --check  # verify existing MANIFEST
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "MANIFEST.csv")

# Included: (label, absolute path) — explicit list, no surprise inclusion.
INCLUDE_GLOBS = [
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "author_verification_statement.md",
    "GITHUB_DEPOSIT_SOP.md",
    "release_notes_v1.0.1.md",
    "workflows/release.yml",
    "config/config.yaml",
    "config/config_vitaldb.yaml",
    "protocol/protocol.md",
    "scripts/*.py",
    "scripts/audit/*.py",
    "scripts/build_manifest.py",
    "manuscript/manuscript_v0.1.md",
    "results/*.json",
    "results/figs/*.png",
    "results/s3_figs/*.png",
    "results/ext/*.json",
    "results/ext/*.joblib",
    "results/ext/external_validation_fig.png",
]

# Excluded even if a glob matches (per-case / internal / derived-data files).
EXCLUDE = {
    "results/_round1_subgroup_n.json",     # intermediate profiling artefact
    "results/s2_feature_dict.json",        # superseded by s2_feature_dictionary.json
    "results/s4_report_manifest.json",     # stale internal marker
    "results/ext/mover_core_train_metrics.json",
}
EXCLUDE_PATTERNS = (
    "results/s2_features",                 # per-case feature matrices (incl. _halfopen)
    "results/s1_labels",                   # per-case outcome labels
    "results/s1_anchor.csv",               # per-case anchor table
    "results/s3_test_predictions_",        # per-case test-set predictions
    "results/s6_external_grid_labels.csv", # external per-case labels
    "results/s2_procedure_groups.csv",
    "results/s2_fuzzy_match_log.csv",
)


def _excluded(rel):
    if rel in EXCLUDE:
        return True
    return any(pat in rel for pat in EXCLUDE_PATTERNS)


def collect():
    import glob
    files = set()
    for pattern in INCLUDE_GLOBS:
        for path in glob.glob(os.path.join(ROOT, pattern)):
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            if _excluded(rel):
                continue
            files.add(rel)
    return sorted(files)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    rows = []
    for rel in collect():
        ap = os.path.join(ROOT, rel)
        rows.append((rel, sha256(ap), os.path.getsize(ap)))
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write("file,sha256,bytes\n")
        for rel, digest, size in rows:
            fh.write(f"{rel},{digest},{size}\n")
    print(f"MANIFEST.csv written: {len(rows)} files")
    return rows


def check():
    if not os.path.exists(OUT):
        print("MANIFEST.csv missing — run without --check first")
        return 1
    ok = True
    with open(OUT, encoding="utf-8") as fh:
        lines = fh.read().splitlines()[1:]
    for line in lines:
        rel, digest, _size = line.split(",")
        ap = os.path.join(ROOT, rel)
        if not os.path.exists(ap):
            print(f"MISSING  {rel}")
            ok = False
        elif sha256(ap) != digest:
            print(f"CHANGED  {rel}")
            ok = False
    print("MANIFEST check: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else (build() and 0))
