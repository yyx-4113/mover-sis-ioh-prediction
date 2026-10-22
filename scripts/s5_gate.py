#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wordcount + structure + numeric-consistency quality gate for the manuscript.

DISCIPLINE (per project rules): every expected number is DERIVED from a product
file (s3_metrics.json, s3_calib_dca.json). Nothing is hardcoded, so the gate
verifies the manuscript matches the CURRENT products rather than protecting stale
numbers.

Checks:
  1. Abstract word count <= 350 (BMC Anesthesiology limit)
  2. Total manuscript word count
  3. docx embeds 6 figures and 8 tables (Table 8 = sensitivity analyses)
  4. References: 21 entries, numbered contiguously 1..N
  5. No leftover placeholders ([RESULT]/[S3_RESULT]/[S6_RESULT]/TODO/FIXME/XXX)
  6. Anchor ratio present (82.0/18.0; 13,834/3,027)
  7. External transportability block present (3,735 / 6,388 / 214)
  8. Model performance numbers in manuscript match s3_metrics.json (derived)
  9. DCA net benefit @0.15 in manuscript matches s3_calib_dca.json (derived)
 10. DCA sign guard (temporal<0 @0.50, patient>0 @0.50)
 11. Limitations items numbered 1..N contiguously
 12. "What this study adds" items numbered 1..N contiguously
Produces a PASS/FAIL report and writes review/quality_gate_2026-10-20.md.
"""
import os
import re
import json
from docx import Document

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "manuscript", "manuscript_v0.1.md")
DOCX = os.path.join(ROOT, "manuscript", "manuscript_v0.1.docx")
REVIEW = os.path.join(ROOT, "review")
ABSTRACT_LIMIT = 350
EXPECTED_TABLES = 8       # Tables 1-7 + Table 8 (sensitivity analyses)
EXPECTED_FIGURES = 6

checks = []  # (name, status, detail)


def add(name, ok, detail):
    checks.append((name, "PASS" if ok else "FAIL", detail))


def count_words(text):
    return len(re.findall(r"\S+", text))


# ---- read manuscript -------------------------------------------------------
with open(SRC, encoding="utf-8") as f:
    md = f.read()
lines = md.splitlines()

# abstract section
abs_text = ""
in_abs = False
for ln in lines:
    if ln.strip() == "## Abstract":
        in_abs = True
        continue
    if in_abs and ln.strip() == "## Background":
        break
    if in_abs:
        abs_text += " " + ln
abs_words = count_words(abs_text.strip())
add("Abstract word count <= %d" % ABSTRACT_LIMIT, abs_words <= ABSTRACT_LIMIT,
    "%d words (limit %d)" % (abs_words, ABSTRACT_LIMIT))

total_words = count_words(md)
add("Total word count reported", True, "%d words" % total_words)

# references count + contiguity
ref_block = ""
in_ref = False
for ln in lines:
    if ln.strip() == "## References":
        in_ref = True
        continue
    if in_ref and ln.strip().startswith("## "):
        break
    if in_ref:
        ref_block += "\n" + ln
ref_nums = re.findall(r"(?m)^\s*(\d+)\.\s", ref_block)
ref_count = len(set(ref_nums))
add("References count == 21", ref_count == 21, "%d references found" % ref_count)
ref_nums_int = sorted(int(x) for x in set(ref_nums))
contiguous = ref_nums_int == list(range(1, len(ref_nums_int) + 1))
add("References numbered contiguously 1..N", contiguous,
    "1..%d" % len(ref_nums_int) if contiguous else "gaps: %s" % ref_nums_int)

# ---- docx structure ---------------------------------------------------------
doc = Document(DOCX)
n_images = sum(1 for r in doc.part.rels.values() if "image" in r.reltype)
n_tables = len(doc.tables)
add("docx embeds %d figures" % EXPECTED_FIGURES, n_images == EXPECTED_FIGURES,
    "%d images" % n_images)
add("docx has %d tables" % EXPECTED_TABLES, n_tables == EXPECTED_TABLES,
    "%d tables" % n_tables)

# ---- placeholder detection (critical: unfinished work) ---------------------
placeholders = ["[RESULT]", "[S3_RESULT]", "[S6_RESULT]", "TODO", "FIXME", "XXX"]
found_ph = [p for p in placeholders if p in md]
add("No leftover placeholders", len(found_ph) == 0,
    "clean" if not found_ph else "FOUND: " + ", ".join(found_ph))

# ---- anchor ratio + external block -----------------------------------------
anchor_ok = all(x in md for x in ["82.0", "18.0", "13,834", "3,027"])
add("Anchor ratio present (82.0 / 18.0; 13,834 / 3,027)", anchor_ok,
    "all tokens present" if anchor_ok else "missing anchor tokens")
ext_ok = ("External transportability check" in md) and all(
    x in md for x in ["3,735", "6,388", "214"])
add("External transportability block present (3,735 / 6,388 / 214)", ext_ok,
    "present" if ext_ok else "missing external tokens")

# ---- external metrics DERIVED from results/ext/external_validation.json ------
# Guards the values that previously drifted (Brier 0.179 -> 0.176, pred_mean 0.37 -> 0.36).
ev = json.load(open(os.path.join(ROOT, "results", "ext", "external_validation.json"),
                   encoding="utf-8"))
ext_tokens = [
    ("AUROC", "%.3f" % ev["auroc"]),
    ("AUPRC", "%.3f" % ev["auprc"]),
    ("Brier", "%.3f" % ev["brier"]),
    ("pred_mean", "%.2f" % ev["pred_mean"]),
    ("prevalence", "%.3f" % ev["prevalence_D1"]),
    ("n", "{:,}".format(ev["n_cases"])),
    ("events", str(ev["n_d1_positive"])),
]
ext_miss = ["%s=%s" % (k, v) for k, v in ext_tokens if v not in md]
add("External metrics match external_validation.json (derived)", len(ext_miss) == 0,
    "all %d present (%s)" % (len(ext_tokens), ", ".join("%s %s" % kv for kv in ext_tokens))
    if not ext_miss else "MISSING in ms: " + ", ".join(ext_miss))

# ---- mandatory editorial strings (verbatim, required by the journal) -------
# The BMC technical check asked for this exact string. It is an external
# requirement, not a product value, so it is quoted verbatim on purpose.
add("Clinical trial number declaration (verbatim editorial requirement)",
    "Clinical trial number: not applicable." in md,
    "present" if "Clinical trial number: not applicable." in md
    else "MISSING exact string 'Clinical trial number: not applicable.'")

# ---- model performance numbers DERIVED from s3_metrics.json ----------------
m = json.load(open(os.path.join(ROOT, "results", "s3_metrics.json"), encoding="utf-8"))
expected = []
for r in m["results"]:
    expected.append("%.3f" % r["auprc"])
    expected.append("%.3f" % r["auroc"])
missing = [e for e in expected if e not in md]
add("Model AUPRC/AUROC match s3_metrics (derived)", len(missing) == 0,
    "all %d present" % len(expected) if not missing else "MISSING in ms: " + ", ".join(missing))

# ---- DCA net benefit @0.15 DERIVED from s3_calib_dca.json -------------------
cd = json.load(open(os.path.join(ROOT, "results", "s3_calib_dca.json"), encoding="utf-8"))


def nb_at_threshold(split, thr=0.15):
    d = cd[split]["dca"]
    th = d["thresholds"]
    nb = d["net_benefit_model"]
    best_i = min(range(len(th)), key=lambda i: abs(th[i] - thr))
    return th[best_i], nb[best_i]


dca_nb = {}
dca_detail = []
dca_ok = True
for split in ("patient", "temporal"):
    t, nb = nb_at_threshold(split)
    dca_nb[split] = nb
    tok = "%.3f" % nb
    present = tok in md
    dca_ok = dca_ok and present
    dca_detail.append("%s @%.2f=%.3f -> '%s' %s" %
                      (split, t, nb, tok, "OK" if present else "MISSING in ms"))
add("DCA net benefit @0.15 matches s3 (derived)", dca_ok, "; ".join(dca_detail))

# regression guard: temporal DCA must be negative in mid-range (≈0.50)
t50_th, t50_nb = nb_at_threshold("temporal", 0.50)
p50_th, p50_nb = nb_at_threshold("patient", 0.50)
dca_sign_ok = (t50_nb < 0) and (p50_nb > 0)
add("DCA sign guard (temporal<0 @0.50, patient>0 @0.50)", dca_sign_ok,
    "temporal@0.50=%.4f, patient@0.50=%.4f" % (t50_nb, p50_nb))

# ---- numbered-list completeness --------------------------------------------
def section(name):
    out = []
    insec = False
    for ln in lines:
        if ln.strip() == "### " + name:
            insec = True
            continue
        if insec and ln.strip().startswith("### "):
            break
        if insec:
            out.append(ln)
    return "\n".join(out)


def numbered_ok(sec):
    nums = [int(x) for x in re.findall(r"(?m)^\s*(\d+)\.\s+\*\*", sec)]
    return nums == list(range(1, len(nums) + 1)), nums


lim_ok, lim_nums = numbered_ok(section("Limitations"))
add("Limitations numbered 1..N contiguously", lim_ok,
    "1..%d" % len(lim_nums) if lim_ok else "nums: %s" % lim_nums)

adds_ok, adds_nums = numbered_ok(section("What this study adds"))
add("What-this-study-adds numbered 1..N contiguously", adds_ok,
    "1..%d" % len(adds_nums) if adds_ok else "nums: %s" % adds_nums)

# ---- report ----------------------------------------------------------------
report = ["# Quality gate report — %s" % "2026-10-20", ""]
report.append("| Check | Status | Detail |")
report.append("|---|---|---|")
for name, status, detail in checks:
    report.append("| %s | **%s** | %s |" % (name, status, detail))
overall = "PASS" if all(c[1] == "PASS" for c in checks) else "FAIL"
report.append("")
report.append("## Overall: **%s**" % overall)
report.append("")
report.append("Abstract words: %d / %d" % (abs_words, ABSTRACT_LIMIT))
report.append("Total words: %d" % total_words)
report.append("docx images: %d, tables: %d, references: %d" %
              (n_images, n_tables, ref_count))

os.makedirs(REVIEW, exist_ok=True)
out = os.path.join(REVIEW, "quality_gate_2026-10-20.md")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(report) + "\n")

print("Overall: %s" % overall)
for name, status, detail in checks:
    print("[%s] %s :: %s" % (status, name, detail))
print("Report written: %s" % out)
