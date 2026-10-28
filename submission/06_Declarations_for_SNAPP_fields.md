# Declarations for the SNAPP submission fields

The system stores these separately from the manuscript file. Text entered in a
field **overrides** whatever the manuscript says, and the stored version is the
one that gets published.

Each block below carries the same wording and the same facts as the matching
declaration in `01_Manuscript.docx`. Two blocks are split rather than copied
verbatim, because the manuscript follows BMC style and prints one combined
heading, "Ethics approval and consent to participate", while the system asks for
the two separately:

- **Ethics approval** and **Consent to participate** together equal that one
  manuscript paragraph.

Every other block is verbatim. Copy the body text only, not the heading.

---

## Data availability

> The development cohort was drawn from MOVER (University of California Irvine), which is available to qualified researchers upon signature of a data use agreement (https://archive.ics.uci.edu/dataset/877/mover:+medical+informatics+operating+room+vitals+and+events+repository; UCI Machine Learning Repository, https://doi.org/10.24432/C5VS5G). The external cohort was drawn from VitalDB (https://vitaldb.net/), which is publicly accessible upon free registration and is described in Lee et al. (2022), doi:10.1038/s41597-022-01411-5. Patient-level data are not redistributed by the author, as the MOVER data use agreement does not permit this. All analysis code, the configuration file, the audit trail, and the aggregate result files from which every number in this manuscript is generated are available at https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.2 (v1.0.2 reproduction package), together with a manifest of file checksums (MANIFEST.csv). Patient-level derived files (per-case feature matrix and outcome labels) are regenerable from the MOVER source under the data use agreement by running the provided pipeline (scripts/run_all.py).

If the field also asks you to pick a category, choose the option closest to
"data available in a publicly accessible repository / via the code repository".
Never choose "available on request" or "available from the authors": the code,
configuration, audit trail and all aggregate result files are in a named public
repository with a release tag and checksums.

---

## Ethics approval

> This study analysed a pre-existing, de-identified database (MOVER, University of California Irvine) accessed under a signed data use agreement. No patients were recruited, no intervention was performed, and no identifiable information was accessed. Under the policy of the Institutional Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, retrospective research that uses exclusively pre-existing de-identified data obtained under a data use agreement is exempt from prospective ethical review and from individual consent; the study was conducted under this exemption and no approval number is reported. All procedures were conducted in accordance with the Declaration of Helsinki.

If the field demands an approval number or an approval date: **do not invent
one**. Use the free-text option and repeat the exemption wording above. The
project decision on record is "default exemption, no application for a waiver
letter, no approval number claimed".

---

## Consent to participate

> Not applicable. The study used exclusively pre-existing de-identified data accessed under a data use agreement; no patients were recruited and no identifiable information was accessed.

If the field only offers a checkbox for "consent obtained", leave it unchecked
and rely on the free text above, which states the individual-consent waiver.

---

## Consent for publication

> Not applicable.

---

## Clinical trial number

The technical check asked for this in the **manuscript**, not in a form field, so
it lives in `01_Manuscript.docx` under Declarations and is checked verbatim by
`s5_gate.py`. If the form also offers a field for it, enter:

> Clinical trial number: not applicable.

Keep the exact wording and punctuation. The journal's own submission-guidelines
page has not yet been updated to list this item; the requirement comes from the
Springer Nature system.

---

## Competing interests

> The author declares no competing interests.

---

## Funding

> This research received no grant or monetary support from any funding agency in the public, commercial or not-for-profit sectors.

If the system insists on at least one funder entry, leave the funder list empty
and keep this sentence in the free-text field. Do not name an employer as a
funder.

---

## Authors' contributions

> YY conceived the study, designed and implemented the data pipeline, performed all analyses, interpreted the results, and wrote and approved the manuscript. YY is the sole author.

---

## Acknowledgements

> The author thanks the University of California Irvine for making the MOVER resource available under a data use agreement.

---

## Use of artificial intelligence

BMC journals usually carry this as a separate question rather than a
declaration. If a field appears, use:

> A large-language-model assistant was used to support code writing, debugging and manuscript drafting. All study design decisions, all reported results, and the final text were reviewed and are the sole responsibility of the author. The assistant is not an author.

---

## Consistency rule going forward

Any future edit to a declaration must be made **twice**: once in
`manuscript/manuscript_v0.1.md` and once in this file (which is the source of the
text you paste into the fields). Otherwise the published statement and the
manuscript file will disagree.
