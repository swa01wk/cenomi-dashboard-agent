# HANDOFF_CONSISTENCY_REPORT

| | |
|---|---|
| Date | 22 October 2026 |
| Scope | The handoff package `cenomi-handoff-2026-10-22`: 214 files under `repo/`, plus `SHA256SUMS` |
| Method | Scripted checks over the package (file existence, ID completeness, figure cross-checks, string searches), then a manual read of every handoff file against its sources |
| Result | **All 10 checks pass.** There are 6 findings to carry forward (F-1 to F-6). None blocks migration |

## Results

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | No approved DX1–DX6 capability is missing | **Pass** | All 31 boards in `canvas.json` order exist as runnable HTML and as PNG renders. `DESIGN_BOARDS_TEXT.md` has 31 sections. All image references inside the boards resolve (0 broken). The identifiers J1–J10, K1–K12, S1–S9, N1–N11, D1–D8, R1–R13, INS-107 and T-202 are all present. Every DX phase is summarized in PROJECT_HANDOFF §3 and §9–§11, with the 15 DX5 kind names, the 6 shared components and the 8 core flows |
| 2 | Canonical KPI definitions and the approved dataset are preserved | **Pass** | All 17 canonical figure strings in PROJECT_HANDOFF §7 match `05_KPI_AND_DATA_RECONCILIATION.md` or the DX6 board text. Examples: 232/92, 130/62, 71 (32/23/16), 41 = 66.1% / 57.7%, 171 days, 87/3,000, 11/142, z 15.9, 408/3,420, 1,026/8,140, 58/299, SAR 2,424,000, SAR 241,800 (+7.5%). The dataset ID, `as_of`, replay hash `82fde5250960761d` and runner hash `c1e36ced42cebecc` are recorded, and the reference models that produce them are included. Metric definitions are in the KPI tab, the DX2-Notes and DX3-Parity boards, and DXD-80. The YAML form does not exist yet (F-5) |
| 3 | The approved decision register is complete | **Pass, see F-1** | `03_DECISION_REGISTER.md` contains exactly 141 decision rows: DR-001 to DR-047 plus DR-018b (48), and DXD-01 to DXD-93 (93). None is missing and there are no extras. The gate section records GDQ-01 to GDQ-12 and the final definitions of the 17 defaults. The machine-readable copy is in `reference-models/gd/register.json` |
| 4 | The five-day slice is not mistaken for the full POC | **Pass** | PROJECT_HANDOFF §15 opens with "The slice is a delivery cut, not the POC" and compares the two side by side (49 h vs 166.5 h, about 20 days). The same rule appears in STATUS, in the onboarding continuity rules and in the "good first reply" checklist. Every item the slice leaves out is listed under the full scope |
| 5 | The milestone sequence is correctly documented | **Pass** | Chain M0→M6 with gates and CF-0 to CF-6 (PROJECT_HANDOFF §14, STATUS). Specification PR order is **M0, M1, M2, M3, M4, M6, M5** and implementation order is **M0→…→M5→M6**, stated as distinct in four places. DR-010 is cited for the complete M6 following the M5 gate. The slice's thin M6 part is explained (it depends only on M2 snapshots and M4 rendering) |
| 6 | Outstanding engineering decisions are not silently resolved | **Pass** | When the package was prepared, ED-01 to ED-11 appeared only as Proposed, with recommendations. A scripted search for "ED-0x … approved" found none, and the six M0-blocking EDs were named. *(Migration update, 22 Oct 2026: the user approved ED-03 Option A with a limited scope. The other ten EDs remain Proposed, and five still block the M0 specifications.)* DR-036 is open. The `snap` vs `meta` choice is open. GDQ-12 configuration is not supplied |
| 7 | Pending ECharts and AG-UI verification stays visible | **Pass** | STATUS § Verification gates lists ECharts 5.6.0 (GDQ-06), the AG-UI spike (GDQ-11), axe and screen reader, and latency, all as Pending. PROJECT_HANDOFF §4 lists them as outstanding conditions. The DX3 status reads "Conditionally approved [Pending verification]". The onboarding prompt asks the new account to list them |
| 8 | No implementation work is marked complete | **Pass** | Every spec, plan, build and gate row in STATUS is "Not started" or "Pending". The one exception is `plans/STATUS.md` itself, marked as the handoff version. The repository is reported as README-only at `5bbd62a`, verified 22 Oct 2026. No file claims anything is committed |
| 9 | Every referenced authoritative file exists or is listed as missing | **Pass** | 40 referenced paths resolve. The paths that do not resolve are all future deliverables (`docs/product/PRODUCT_SPEC.md`, `docs/contracts/KPI_CATALOG.md`, `specs/*`, `tests/fixtures/*`, `plans/ROADMAP.md`, `docs/design/DESIGN_BASELINE.md`, `DECISION_REGISTER.md`), and each is listed in MIGRATION_MANIFEST § "Files that are missing or do not exist yet". The V2 UI references (DR-039) were never supplied, and this is also listed |
| 10 | The new account can find the exact next action without earlier conversations | **Pass** | STATUS § "Next tasks" and § "Completion criteria"; PROJECT_HANDOFF §16 and §18; the onboarding prompt step 6. The next action is: migrate, then the user approves the ESP and decides ED-01, ED-02, ED-04, ED-05 and ED-06 (ED-03 is approved, scoped), then PR-M0 is authored in sessions A–E (ESP tab 6) |

## Findings to carry forward

| ID | Finding | Effect | Resolution |
|---|---|---|---|
| F-1 | The per-row "GD status" column in `03_DECISION_REGISTER.md` still shows the **pre-gate** statuses: 104 ready, 23 "Decision required". The section "Gate decisions recorded (22 Oct 2026)" at the end of the same file settles 22 of those 23. Those 22 are the 17 GDQ-10 defaults, DR-012 and DXD-72 (GDQ-05), DR-015 (GDQ-12), DR-038 (GDQ-11) and DXD-80 (GDQ-03, plus the DXD-80 to DXD-93 approval). Only **DR-036** remains open. The post-gate count is 126 / 7 / 1 / 2 / 5 | A reader of the table alone could think 23 decisions are open | The gate section is authoritative; PROJECT_HANDOFF §4 and STATUS state this. When `docs/design/DECISION_REGISTER.md` (ESP item 4) is written, apply the post-gate status to each row. The export is left unchanged so that it matches the source document |
| F-2 | The 7 verification-pending decisions are DR-007, DR-017, DXD-21, DXD-24, DXD-39, DXD-40 and DXD-61. DXD-24 and DXD-39 (accessibility and inspector checks on the real build) are covered by the axe and screen-reader gate rather than named individually in STATUS | Minor traceability gap | Cite all seven in the M2 and M4 gate wording when PR-M2 and PR-M4 are written |
| F-3 | OI-13: the DX5-GenUI "overdue" wording fix is in the exported board (verified: no "overdue" in `DX5-GenUI.dc.html`) but not on canvas v27 | None for the new account; the canvas is not transferable | The exported boards are authoritative for this wording (baseline README) |
| F-4 | ED-03 (reference copies in the repository) was unapproved when the package was prepared | — | **Resolved 22 Oct 2026:** the user approved ED-03 Option A, scoped to preserving the reference documents and design baseline. This is recorded in `plans/STATUS.md` and PROJECT_HANDOFF §17 |
| F-5 | Metric YAML, `KPI_CATALOG.md`, the TA §5.3 to S/N scenario mapping, the exposing rows for the eight caveats, the clarification policy and the 150-question benchmark do not exist (OI-04, 05, 06, 07, 09, 14) | Expected. They are specification work | Already assigned to PR-M1, PR-M3 and PR-M5 in ESP tab 4 |
| F-6 | The GD-doc "Specification inventory" tab (GD6) and the original project instructions §10 list older document names (for example `M1_DATABASE_AND_SEEDING.md`). ESP tab 4 and tab 5 supersede them (`M1_DATA.md`, and the `docs/` sub-folders) | Two lists of file names | Treat ESP tab 4 and tab 5 as the proposed structure. MIGRATION_INSTRUCTIONS §3 tells the user to update the project instructions §10 pointer. GD6 is marked "superseded in detail" in `docs/reference/README.md` |

## Corrections made while preparing the package

- The ESP five-day slice diagram was re-drawn because the original screenshot pre-dated the kind-name fix (it showed `kpi_card` and `limitation`). It now shows the DX5 names `kpi` and `unavailable`.
- Embedded-diagram placeholders in five exported tabs were replaced with links to the PNG exports. The GD "Five-day feasibility" tab's old slice widget now points to the ESP slice diagram.
- No other content in the exports was changed. The exports otherwise match the Docs artifacts as of 22 Oct 2026.

## Re-running the checks

The scripted checks use only Python 3 standard-library code over the package. To repeat check 3:

```bash
cd repo
python3 -c "import re;r=open('docs/reference/final-design-gate/03_DECISION_REGISTER.md').read();print(len(set(re.findall(r'^\| (DR-\d{3}b?|DXD-\d{2}) \|',r,re.M))))"   # expect 141
```

## Post-package changes at migration (22 Oct 2026)

When the user authorized the documentation migration, all 214 package files were extracted from the two archives and checked against the package `SHA256SUMS`. **214 of 214 matched.** The archives were also scanned for unsafe entries (absolute paths, `..` traversal, symlinks), and none were found.

| Item | SHA-256 |
|---|---|
| `cenomi-handoff-2026-10-22-docs.zip` | `56a3a7226ccc2fba221787845d30a3865f25ad6a3ef7748442ab6626807b5f9c` |
| `cenomi-handoff-2026-10-22-design-baseline.zip` | `73dadf8a9467a0763740cdc65d4d2426e6c0a61d27ba29e3ea7e47892c669d7a` |
| Package `SHA256SUMS` (as delivered) | `f63c0b42253825cd47117cde7cf517224989830b3e3079e32696453e6f739eb4` |

Seven control and status files were then edited, and only for two reasons:
- To record the user's scoped approval of **ED-03 Option A**.
- To record that the migration is **pending merge**.

No reference document, design export, board, render, reference model or ESP tab was changed. `docs/handoff/SHA256SUMS` holds the hashes of the committed files. The package-time hashes of the seven edited files are:

| File | Package-time SHA-256 | Reason |
|---|---|---|
| `plans/STATUS.md` | `936b3ad817a445c3a9d4fe8e02cea170ab0a62a2154d4c3c5111319101303746` | ED-03 recorded as approved (scoped); migration pending merge; next approvals updated |
| `docs/handoff/PROJECT_HANDOFF.md` | `2e9a397c415f86770f83ffca7fac1ec4c177677c086a488c137155c74424f50d` | ED-03 approval (scoped) and migration status |
| `docs/handoff/MIGRATION_MANIFEST.md` | `05f8bd4452d8f5336fd557944f7cf6d766b050b6422ac7edf379b91a04d7c15c` | Migration status line; `SHA256SUMS` committed at `docs/handoff/SHA256SUMS` |
| `docs/handoff/MIGRATION_INSTRUCTIONS.md` | `773b9e1297aad04b9958941db076e7bb78990d397a759c766858d9b1e1c11f35` | ED-03 approval (scoped) and migration status |
| `docs/handoff/ONBOARDING_PROMPT.md` | `0e4c3302b0dfb290d304ec4ea06244bd99e14bc510fd86d28759e6bea60822b5` | ED-03 approval (scoped) and migration status |
| `docs/handoff/HANDOFF_CONSISTENCY_REPORT.md` | `7f1d600923855bb1aa757e093046d02f29ea92334962c4a0c42039b21cb7d841` | F-4 resolved; check 6 note; this section |
| `docs/reference/README.md` | `831b462fa3e78709572bdbdf9f4f5ae4106990b2c821add6d527699fe648a76e` | ED-03 approval stated |
