# Cover Letter

**To:** The Editor-in-Chief, *BMC Anesthesiology*
**Date:** 2026-10-20
**Manuscript type:** Original Article
**Corresponding author:** Yongxin Yang — 960856791@qq.com

Dear Editor-in-Chief,

Please consider our manuscript entitled **"Prediction of sustained intraoperative hypotension burden from data available at anaesthesia induction: model development and internal validation in the MOVER/SIS cohort"** for publication as an Original Article in *BMC Anesthesiology*.

**Summary of the work.** We developed and internally validated a gradient-boosted model that predicts the *cumulative burden* of intraoperative hypotension (≥10 post-anchor MAP measurements, ≥30% below 65 mmHg) over the remainder of surgery, using only data available at the anaesthesia-induction anchor. In 16,861 adult surgical cases from the MOVER/SIS cohort, the model achieved AUPRC 0.347 (AUROC 0.722) on a patient-level split and was reproduced under temporal validation, with well-calibrated probabilities after isotonic recalibration and positive net benefit up to decision thresholds of 0.58 (patient) and 0.73 (temporal). Most predictive information resided in the pre-anchor arterial pressure level; a MAP-only logistic benchmark reproduced most of the performance (AUPRC 0.284 vs 0.347; incremental net benefit 0.013).

**Why this manuscript fits *BMC Anesthesiology*.**
1. *Topic alignment.* Intraoperative hypotension and perioperative risk prediction are central to the journal's scope, and the clinical question (anticipation at induction rather than intraoperative monitoring) is directly relevant to anaesthesia practice.
2. *Methodological alignment.* The study is reported in accordance with TRIPOD+AI (2024), includes an explicit leakage audit, calibration assessment with recalibration, and decision-curve analysis, and is accompanied by a completed reporting checklist (Additional file 2) and a fully traceable audit trail (Additional file 1).
3. *Honest evidence level.* We deliberately present an internal-validation study (TRIPOD type 2a), explicitly state the absence of external validation, quantify the recording-density constraint of the source data, and benchmark the full model against a MAP-only baseline rather than overstating incremental value. We believe this candour about the limits of prediction on sparse public operating-room data is itself a contribution the journal's readership will value.

**Confirmations.**
- The manuscript is original, has not been published previously, and is not under consideration elsewhere.
- The sole author has approved the manuscript and agrees to its submission.
- Reporting follows TRIPOD+AI; the completed checklist is provided as Additional file 2.
- **Ethics.** This is a retrospective analysis of a pre-existing, de-identified database (MOVER, University of California Irvine) accessed under a signed data use agreement. Under the policy of the Institutional Review Board of The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, such research is exempt from prospective ethical review and individual consent; the study was conducted under this exemption, and a retrospective waiver letter documenting this basis is being obtained from the IRB. No approval number is reported because none was assigned.
- **Data availability.** Analysis code, the configuration file, the audit trail, and the aggregate result files from which every reported number is generated are available in the GitHub reproduction package (v1.0.0; https://github.com/yyx-4113/mover-sis-ioh-prediction) with a MANIFEST of file checksums. Patient-level derived files are regenerable from the MOVER source under the data use agreement by running the provided pipeline.
- **Competing interests.** The author declares no competing interests. **Funding.** No funding was received.
- **Use of artificial intelligence.** An LLM assistant supported code writing, debugging, and manuscript drafting; all design decisions, results, and the final text are the author's sole responsibility, and the assistant is not an author.

We would be grateful if the manuscript could be reviewed by editors and reviewers with expertise in perioperative prediction modelling and clinical calibration methodology. Suggested potential reviewers can be supplied on request and with their consent.

Thank you for your time and consideration.

Sincerely,

Yongxin Yang
Department of Anesthesiology, The Second Affiliated Hospital of Fujian University of Traditional Chinese Medicine, Fuzhou, Fujian 350003, China
ORCID: 0009-0004-9698-6552
Email: 960856791@qq.com
