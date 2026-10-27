# -*- coding: utf-8 -*-
"""Build the BMC Medical Informatics and Decision Making submission bundle.

Assembles, into a single folder, everything the SNAPP submission
wizard (Springer Nature Article Processing Platform) asks for:

    submission/
      00_README_submission_checklist.md      what to upload, where, and the journal URL
      01_Manuscript.docx                     title page + abstract + main text + declarations
                                             + references + figure legends + tables
      02_Cover_letter.docx                   Times New Roman 12 pt
      03_Figures/Fig1..Fig6*.png             300 dpi, uploaded separately as well as embedded
      04_Additional_file_1_audit_trail.csv   every reported number -> product file -> command
      05_Additional_file_2_TRIPOD_AI.docx    TRIPOD+AI (2024) checklist, English

Idempotent: re-running overwrites the folder contents from the current products.
Never edits a source file; only reads and copies.
"""
import csv
import os
import re
import shutil

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "submission")
FIGDIR = os.path.join(OUT, "03_Figures")

JOURNAL = "BMC Medical Informatics and Decision Making"
# BMC MIDM is on SNAPP (Springer Nature Article Processing Platform), as are other
# BMC Series titles. 12911 is the Springer Nature journal ID.
SUBMIT_URL = "https://submission.springernature.com/new-submission/12911/3"
JOURNAL_URL = "https://link.springer.com/journal/12911"
ISSN = "1471-2253"


# --------------------------------------------------------------------------- #
# minimal markdown -> docx  (headings, bold, bullets, numbering, pipe tables)
# --------------------------------------------------------------------------- #
def set_base_style(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    rpr = st.element.get_or_add_rPr()
    rf = rpr.find(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rf is None:
        from docx.oxml.ns import qn
        rf = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rf)
    from docx.oxml.ns import qn
    rf.set(qn("w:eastAsia"), "Times New Roman")
    rf.set(qn("w:ascii"), "Times New Roman")
    rf.set(qn("w:hAnsi"), "Times New Roman")


def add_rich(p, text):
    """Add runs to paragraph p, rendering **bold** segments."""
    text = text.replace("\u2014", "\u2014")
    for i, seg in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not seg:
            continue
        r = p.add_run(seg)
        r.bold = (i % 2 == 1)
    return p


def md_to_docx(md_path, docx_path, title_center=False):
    doc = Document()
    set_base_style(doc)
    lines = open(md_path, encoding="utf-8").read().split("\n")

    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()

        # pipe table
        if s.startswith("|") and s.endswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = []
            for r in block:
                cells = [c.strip() for c in r.strip("|").split("|")]
                if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    continue  # separator row
                rows.append(cells)
            if rows:
                ncol = max(len(r) for r in rows)
                tbl = doc.add_table(rows=len(rows), cols=ncol)
                tbl.style = "Table Grid"
                for ri, r in enumerate(rows):
                    for ci in range(ncol):
                        val = r[ci] if ci < len(r) else ""
                        val = val.replace("**", "")
                        cell = tbl.cell(ri, ci)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        run = p.add_run(val)
                        run.bold = (ri == 0)
            continue

        if not s:
            i += 1
            continue

        # blockquote
        if s.startswith(">"):
            p = doc.add_paragraph()
            add_rich(p, s.lstrip("> ").strip())
            for r in p.runs:
                r.italic = True
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            p = doc.add_heading(level=min(lvl, 4))
            add_rich(p, m.group(2))
            if title_center and lvl == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.bold = True
            i += 1
            continue

        # bullets / numbering
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            add_rich(doc.add_paragraph(style="List Bullet"), m.group(1))
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            add_rich(doc.add_paragraph(style="List Number"), m.group(2))
            i += 1
            continue

        add_rich(doc.add_paragraph(), s)
        i += 1

    doc.save(docx_path)
    return docx_path


# --------------------------------------------------------------------------- #
def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(FIGDIR, exist_ok=True)

    made = []

    # 1. manuscript ---------------------------------------------------------
    src = os.path.join(ROOT, "manuscript", "manuscript_v0.1.docx")
    dst = os.path.join(OUT, "01_Manuscript.docx")
    shutil.copy2(src, dst)
    made.append((dst, "manuscript (title page, abstract, text, declarations, "
                      "references, figure legends, tables 1-8)"))

    # 2. cover letter -------------------------------------------------------
    cl_md = os.path.join(ROOT, "manuscript", "cover_letter_bmc_midm.md")
    dst = md_to_docx(cl_md, os.path.join(OUT, "02_Cover_letter.docx"),
                     title_center=True)
    made.append((dst, "cover letter (Times New Roman 12 pt)"))

    # 3. figures ------------------------------------------------------------
    fig_src = {
        "Fig1_cohort.png": "fig1_cohort.png",
        "Fig2_definitions.png": "fig2_definitions.png",
        "Fig3_pr_roc.png": "fig3_pr_roc.png",
        "Fig4_calib_dca.png": "fig4_calib_dca.png",
        "Fig5_importance.png": "fig5_importance.png",
        "Fig6_external_transportability.png": "fig6_external_validation.png",
    }
    figs = []
    for new, old in fig_src.items():
        s = os.path.join(ROOT, "results", "figs", old)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(FIGDIR, new))
            figs.append(new)
    made.append((FIGDIR, "6 figures at 300 dpi: " + ", ".join(figs)))

    # 4. additional file 1: audit trail -------------------------------------
    s = os.path.join(ROOT, "results", "s4_audit_trail.csv")
    dst = os.path.join(OUT, "04_Additional_file_1_audit_trail.csv")
    shutil.copy2(s, dst)
    n = sum(1 for _ in open(s, encoding="utf-8-sig")) - 1
    made.append((dst, "audit trail, %d rows (number -> product file -> command)" % n))

    # 5. additional file 2: TRIPOD+AI ---------------------------------------
    s = os.path.join(ROOT, "results", "s4_tripod_ai.md")
    dst = md_to_docx(s, os.path.join(OUT,
                                     "05_Additional_file_2_TRIPOD_AI.docx"))
    made.append((dst, "TRIPOD+AI (2024) reporting checklist, English"))

    # 6. declarations for the online fields ----------------------------------
    s = os.path.join(ROOT, "manuscript", "06_Declarations_for_SNAPP_fields.md")
    dst = os.path.join(OUT, "06_Declarations_for_SNAPP_fields.md")
    shutil.copy2(s, dst)
    made.append((dst, "field-by-field declarations to paste into the SNAPP form"))

    # 6b. point-by-point response to technical check -------------------------
    rl_md = os.path.join(ROOT, "manuscript", "07_Response_to_Technical_Check.md")
    if os.path.exists(rl_md):
        dst = md_to_docx(rl_md,
                         os.path.join(OUT, "07_Response_to_Technical_Check.docx"))
        made.append((dst, "point-by-point response to technical check"))

    # 7. README / checklist -------------------------------------------------
    readme = os.path.join(OUT, "00_README_submission_checklist.md")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(README.format(journal=JOURNAL, url=SUBMIT_URL,
                              jurl=JOURNAL_URL, issn=ISSN,
                              figs="\n".join("   - " + x for x in figs),
                              naudit=n))
    made.append((readme, "submission checklist and upload order"))

    print("Submission bundle -> %s" % OUT)
    for p, d in made:
        print("  %-58s %s" % (os.path.relpath(p, OUT), d))
    return made


README = """# Submission bundle - {journal}

**Submission site (SNAPP, Springer Nature Article Processing Platform):** {url}
**Journal home page:** {jurl}
**ISSN:** {issn}
**Springer Nature journal ID:** 12911

## How to reach the submission site

Open the journal home page and click **Submit your manuscript**; or paste the
direct link above. Either route lands on the Springer Nature sign-in page, which
states "continue with your submission to {journal}".

Sign in with **ORCID** (recommended, it links the submission to
0009-0004-9698-6552), or with a Springer Nature account, or with Google. The
account is created on first use.

Do **not** use an `editorialmanager.com` link for this journal. BMC titles have
moved off Editorial Manager onto SNAPP, and the old Editorial Manager address no
longer accepts new submissions.

Everything needed for the online submission is in this folder.
Upload order in the SNAPP submission wizard:

| Step in wizard | File in this folder |
|---|---|
| 1. Article type | Original Article (Research) |
| 2. Manuscript | `01_Manuscript.docx` |
| 3. Cover letter | `02_Cover_letter.docx` |
| 3b. Response to technical check | `07_Response_to_Technical_Check.docx` (point-by-point reply; upload in the cover-letter / query-response area) |
| 4. Figures (upload individually) | `03_Figures/` |
| 5. Additional files | `04_Additional_file_1_audit_trail.csv`, `05_Additional_file_2_TRIPOD_AI.docx` |

Figures included (300 dpi):
{figs}

Additional file 1 has {naudit} rows: every number reported in the manuscript,
the result file that produced it, and the command that reproduces it.

## Points to check before clicking Submit

- Author name carries **no academic title** (no MD/PhD); ORCID 0009-0004-9698-6552 is
  linked in the manuscript title page.
- Ethics statement: retrospective analysis of de-identified data under a signed data
  use agreement; exempt under the author institution's IRB policy; **no approval number
  is claimed** because none was assigned. Do not invent one.
- Data availability points at the public reproduction package release tag, not
  "available on request".
- Reporting checklist (TRIPOD+AI 2024) is attached as Additional file 2 and is in English.
- The cover letter and the manuscript report the same numbers (external AUROC 0.744,
  AUPRC 0.158, mean predicted risk 0.36, external Brier 0.176, n = 3,735, events 214).
- Declarations entered into the online fields are stored separately from the
  manuscript and are the version that gets published. Paste them from
  `06_Declarations_for_SNAPP_fields.md`, which matches the manuscript. Never type
  "available on request" into the data availability field, and never invent an
  ethics approval number.

## Reproducibility

Regenerate this bundle at any time with:

    python scripts/s7_submission_pack.py

It reads only from `manuscript/` and `results/` and never edits a source file.
"""


if __name__ == "__main__":
    build()
