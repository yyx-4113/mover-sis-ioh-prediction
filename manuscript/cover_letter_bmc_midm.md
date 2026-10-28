# Cover Letter

**To:** The Editor-in-Chief, *BMC Medical Informatics and Decision Making*
**Date:** 2026-10-27
**Manuscript type:** Original Article
**Corresponding author:** Yongxin Yang, 960856791@qq.com

Dear Editor-in-Chief,

Please consider our manuscript entitled **"Transparent, leakage-audited prediction of cumulative intraoperative hypotension burden from anaesthesia-induction data, with an external transportability check and quantification of sparse noninvasive blood pressure constraints"** for publication as an Original Article in *BMC Medical Informatics and Decision Making*.

**Disclosure of prior assessment.** This manuscript was previously assessed by *BMC Anesthesiology*, which declined publication on the grounds that the clinical validity of the outcome and the incremental value over a MAP-based approach were limited by the sparse, intermittently recorded noninvasive blood pressure in the source data. It has not been submitted elsewhere. In response we reframed the contribution to match the scope of *BMC Medical Informatics and Decision Making*: the paper's primary value is methodological — a transparent, leakage-audited clinical prediction pipeline and an honest, quantitative account of what sparse real-world vital-sign data can and cannot support — rather than a clinical claim of high discrimination. No new analyses were required; the repositioning is entirely in framing, and every reported number is unchanged.

**Summary of the work.** We developed and internally validated a gradient-boosted model that predicts intraoperative hypotensive exposure (≥10 post-anchor MAP measurements, ≥30% below 65 mmHg) over the remainder of surgery, using only data available at the anaesthesia-induction anchor. In 16,861 adult surgical cases from the MOVER/SIS cohort, the model achieved AUPRC 0.347 (AUROC 0.722) on a patient-level split and was reproduced under temporal validation, with well-calibrated probabilities after isotonic recalibration. Because the dominant predictor was the pre-anchor arterial pressure level, we benchmarked the full model against a MAP-only logistic baseline (incremental net benefit 0.013 at threshold 0.15) and report this honestly rather than overstating incremental value. We then applied the unchanged model to an independent public cohort (VitalDB, n = 3,735 arterial cases): discrimination transferred (external AUROC 0.744) but absolute probabilities did not (mean predicted risk 0.36 vs observed prevalence 0.057), identifying local recalibration as the concrete deployment requirement.

**Why this manuscript fits *BMC Medical Informatics and Decision Making*.**
1. *Scope alignment.* The journal publishes work on "the design, development, implementation, use, and evaluation of health information technologies and decision-making for human health," including machine learning and modelling. A transparent, calibration-first clinical prediction pipeline with an explicit leakage audit is squarely within this remit.
2. *Methodological contribution.* Beyond the modest absolute performance, the study contributes a quantitative leakage audit on a public operating-room resource, a 14-definition outcome sensitivity analysis that shows apparent performance to be largely an artefact of the chosen endpoint, a transparent accounting of spectrum bias from sparse monitoring, an honest MAP-only benchmark, and an external transportability check whose transferred and non-transferred components are isolated. These elements hold independently of the discrimination achieved and are under-reported in perioperative prediction.
3. *Validity over impact.* As a BMC Series journal, *BMC Medical Informatics and Decision Making* evaluates manuscripts on scientific validity rather than perceived interest or impact. Our study is methodologically sound, fully reported under TRIPOD+AI (2024) with the completed checklist (Additional file 2) and a traceable audit trail (Additional file 1), and candid about its constraints; we believe this honesty is itself a contribution the journal's readership will value.

**Confirmations.**
- The manuscript is original, has not been published previously, and is not under consideration elsewhere.
- The sole author has approved the manuscript and agrees to its submission.
- Reporting follows TRIPOD+AI; the completed checklist is provided as Additional file 2.
- **Ethics.** This is a retrospective analysis of a pre-existing, de-identified database (MOVER, University of California Irvine) accessed under a signed data use agreement. Under the policy of the Institutional Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, such research is exempt from prospective ethical review and individual consent; the study was conducted under this exemption. No approval number is reported because none was assigned.
- **Data availability.** Analysis code, the configuration file, the audit trail, and the aggregate result files from which every reported number is generated are available in the GitHub reproduction package (v1.0.2; https://github.com/yyx-4113/mover-sis-ioh-prediction/releases/tag/v1.0.2) with a MANIFEST of file checksums. Patient-level derived files are regenerable from the MOVER source under the data use agreement by running the provided pipeline.
- **Competing interests.** The author declares no competing interests. **Funding.** No funding was received.
- **Use of artificial intelligence.** An LLM assistant supported code writing, debugging, and manuscript drafting; all design decisions, results, and the final text are the author's sole responsibility, and the assistant is not an author.

We would be grateful if the manuscript could be reviewed by editors and reviewers with expertise in clinical prediction modelling, calibration methodology, and health-informatics evaluation. Suggested potential reviewers can be supplied on request and with their consent.

Thank you for your time and consideration.

Sincerely,

Yongxin Yang
Department of Anesthesiology, The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, Fuzhou, Fujian 350003, China
ORCID: 0009-0004-9698-6552
Email: 960856791@qq.com
