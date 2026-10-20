# Quality gate report — 2026-10-20

| Check | Status | Detail |
|---|---|---|
| Abstract word count <= 350 | **PASS** | 326 words (limit 350) |
| Total word count reported | **PASS** | 10167 words |
| References count == 18 | **PASS** | 18 references found |
| References numbered contiguously 1..N | **PASS** | 1..18 |
| docx embeds 6 figures | **PASS** | 6 images |
| docx has 8 tables | **PASS** | 8 tables |
| No leftover placeholders | **PASS** | clean |
| Anchor ratio present (82.0 / 18.0; 13,834 / 3,027) | **PASS** | all tokens present |
| External transportability block present (3,735 / 6,388 / 214) | **PASS** | present |
| Model AUPRC/AUROC match s3_metrics (derived) | **PASS** | all 16 present |
| DCA net benefit @0.15 matches s3 (derived) | **PASS** | patient @0.15=0.051 -> '0.051' OK; temporal @0.15=0.058 -> '0.058' OK |
| DCA sign guard (temporal<0 @0.50, patient>0 @0.50) | **PASS** | temporal@0.50=-0.0017, patient@0.50=0.0042 |
| Limitations numbered 1..N contiguously | **PASS** | 1..14 |
| What-this-study-adds numbered 1..N contiguously | **PASS** | 1..5 |

## Overall: **PASS**

Abstract words: 326 / 350
Total words: 10167
docx images: 6, tables: 8, references: 18
