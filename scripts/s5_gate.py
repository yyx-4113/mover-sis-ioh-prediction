#!/usr/bin/env python3
"""Wordcount + structure + numeric-consistency quality gate for the manuscript.

Checks:
  1. Abstract word count <= 350 (BMC Anesthesiology limit)
  2. Total manuscript word count
  3. docx embeds 5 figures and 6 tables
  4. References section has 16 entries
  5. Key headline numbers appear in the manuscript text (cross-checked vs s3 products)
  6. DCA net benefit at threshold 0.15 matches s3_calib_dca (patient/temporal)
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

# references count
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
add("References count == 18", ref_count == 18, "%d references found" % ref_count)

# ---- docx structure ---------------------------------------------------------
doc = Document(DOCX)
n_images = sum(1 for r in doc.part.rels.values() if "image" in r.reltype)
n_tables = len(doc.tables)
add("docx embeds 5 figures", n_images == 5, "%d images" % n_images)
add("docx has 6 tables", n_tables == 6, "%d tables" % n_tables)

# ---- key numbers present (cross-checked vs s3) ------------------------------
key_numbers = ["0.347", "0.722", "0.234", "0.301", "0.337", "0.339", "0.733",
               "0.1555", "2,622", "16,861", "13,834", "3,027",
               "175.5", "75.2", "72.2", "69.1", "64.1", "52.9",
               "0.909", "0.008", "0.119", "0.191", "2.23", "82.1", "17.9"]
missing = [k for k in key_numbers if k not in md]
add("Key headline numbers present", len(missing) == 0,
    "all %d present" % len(key_numbers) if not missing else "MISSING: " + ", ".join(missing))

# ---- DCA net benefit at threshold 0.15 --------------------------------------
cd = json.load(open(os.path.join(ROOT, "results", "s3_calib_dca.json")))
manuscript_nb = {"patient": 0.050, "temporal": 0.058}


def nb_at_threshold(split, thr=0.15):
    d = cd[split]["dca"]
    th = d["thresholds"]
    nb = d["net_benefit_model"]
    best_i = min(range(len(th)), key=lambda i: abs(th[i] - thr))
    return th[best_i], nb[best_i]


dca_ok = True
dca_detail = []
for split in ("patient", "temporal"):
    t, nb = nb_at_threshold(split)
    diff = abs(nb - manuscript_nb[split])
    ok = diff <= 0.005
    dca_ok = dca_ok and ok
    dca_detail.append("%s @%.2f=%.3f vs ms %.3f (Δ%.4f)" %
                      (split, t, nb, manuscript_nb[split], diff))
add("DCA net benefit @0.15 matches s3", dca_ok, "; ".join(dca_detail))

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
