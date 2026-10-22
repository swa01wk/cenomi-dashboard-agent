# docs/reference — frozen reference documents

These files are **frozen copies** for Cursor and for the new Claude account. They are stored here under **ED-03 Option A, approved by the user on 22 Oct 2026**. That approval covers only preserving the existing reference documents and design baseline. It does not change product architecture, KPI calculations, implementation scope or any other engineering decision.

Rules: never edit these files. A changed source document is added as a new file with a new version, recorded as a CR in `plans/STATUS.md`. Specifications cite these files by path and section.

## Authoritative documents

| # | File | Version | Original location | SHA-256 |
|---|---|---|---|---|
| 1 | `Cenomi_Dashboard_Intelligence_Agent_PRD.md` | v1.0, 21 Oct 2026 | Claude Project file | `13ec1b6975dfb491d9b28496dd236164fa9880adda7b92bd0f7a8bb8963aa67c` |
| 2 | `Cenomi_Dashboard_Intelligence_Agent_Technical_Architecture_and_Implementation_Plan.md` | v1.0, 21 Oct 2026 | Claude Project file | `dc26d23585e2d47424bef6aa3ad408a3327cecd9b6279284931bde7f4cb77436` |
| 3 | `ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` | Generated 2026-10-13 (code trace) | Claude Project file | `e01113fc48f2d354c63df6b12ede8bdf5c742044563ad76fcbb83d6b3e2dcce7` |

## Final Design Gate exports (authoritative documents 5, 6 and 7)

Exported on 22 Oct 2026 from the Claude Docs artifact "Cenomi POC — Final Design Gate (GD)", one Markdown file per tab, after the gate decisions were recorded. The original link (`claude.ai/artifact/FR1f4Feb9ae8uvSgwjdtGv`) is private to the original account and must not be assumed accessible. Embedded diagram widgets are replaced by PNG exports or links (marked in each file). Document 4 (DX1–DX6 boards) lives in `docs/design/baseline/`.

| File | Tab | Holds | SHA-256 |
|---|---|---|---|
| `final-design-gate/01_DESIGN_REVIEW_REPORT.md` | Design review report | Recommendation, gate outcome, phases reviewed, findings F-01…F-14, GDQ-01…12 with recorded answers, approval checklist | `ba987829b5f98a9848f4b20767590bcb343d8937560a1213079785a0d5f6af9e` |
| `final-design-gate/02_ARCHITECTURE_AND_INTERACTION_MODEL.md` | Architecture and interaction model | Consolidated layers, screens and overlays, 8 core flows, consolidation of duplicated capabilities | `6cc160079454bf42d52b0a0d3e83b10dc8d3ae8bef39e5b6bcea8add9afde90e` |
| `final-design-gate/03_DECISION_REGISTER.md` | Decision register | All 141 decisions (DR-001…047 + DR-018b, DXD-01…93) with GD status; § Gate decisions recorded (22 Oct 2026); final definitions of the 17 batch defaults | `fec5418c5cce49358e2e4f72b8ce8084eae901754e986ac4a650c68801f69895` |
| `final-design-gate/04_TRACEABILITY.md` | Traceability | 70 requirements traced to design evidence and spec homes | `1cd7a505344a55691b7da020ebbdcb9ae82afc586ca6b98973ca31fbe9fceffb` |
| `final-design-gate/05_KPI_AND_DATA_RECONCILIATION.md` | KPI and data reconciliation | Parity table per card, canonical figures for sd-2026.10.20-01, discrepancies C1–C21, data model, golden scenarios, invariants | `bc177156bfbe827f2afbd4e02dee5c5a0280db568e807bd6c7daa72753c3f057` |
| `final-design-gate/06_SPECIFICATION_INVENTORY_GD.md` | Specification inventory | GD-time spec inventory (superseded in detail by ESP tab 4; kept for record) | `580be9e0e1fd4c30ad82c4ce31ab2d9bf6f58e9faaed6916cdda1afceb1d1ed3` |
| `final-design-gate/07_FIVE_DAY_FEASIBILITY.md` | Five-day feasibility | Effort table (~165 h) and options behind GDQ-01 | `220c36e46b62f3a62e2d2428080b24497ff865ad894fccb01e8c64345cdbe5d4` |
| `final-design-gate/08_OPEN_ISSUES_AND_RISKS.md` | Open issues and risks | OI-01…OI-15 and R-01…R-14 | `00d6e11399c1d6b484b687bd6c66809c75b3df442f1d32d7a5754faaaad185e5` |
| `final-design-gate/diagram_consolidated_architecture.png` | (diagram) | Architecture diagram embedded in tab 02 | `e8e8f796cae248ab0dd236aed79fc896a58f0fc69b9ebf3c755b4b5d2c282432` |

## Planning history (supporting, not authoritative)

| File | What it is | SHA-256 |
|---|---|---|
| `planning-history/PLANNING_ASSESSMENT_v0.1.md` | G0 planning assessment, first draft (21 Oct 2026) | `6abc8b22e8882ea81dc4178f692e89d4cfb9b4626a25c8e760ef08cb0f857011` |
| `planning-history/PLANNING_ASSESSMENT_v0.2.md` | G0 assessment with decisions incorporated; decision register DR-001…047 | `374ad43057a60350c8ec29e0f4db16d500950cbf6e365f09b569701d9a497c36` |
| `planning-history/PLANNING_ASSESSMENT_v0.3.md` | G0 assessment, final version referenced by GD | `588732b7b9c19bd3b5f2cd11f7e44267983270c7bf01207dbe7f2b31c842ab73` |
| `planning-history/DESIGN_DECISIONS_DX4_DX5.md` | Decision note: DX4 corrections and DX5 (22 Oct 2026) | `7e6da7639568395820570173dad479c89816327f17532ce011fb128dd4368f63` |
| `planning-history/DESIGN_DECISIONS_DX5R_DX6.md` | Decision note: DX5 refinements and DX6 (22 Oct 2026) | `f887753990df75a9525e51179e10e006c18585e8ef821bb16b7d457319bc6e9b` |

Where planning history disagrees with the GD register, the GD register wins (it is later and approved).
