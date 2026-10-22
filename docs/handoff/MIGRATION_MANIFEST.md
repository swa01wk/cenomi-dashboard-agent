# MIGRATION_MANIFEST — files the new Claude account needs

| | |
|---|---|
| Prepared | 22 October 2026 |
| Package | `cenomi-handoff-2026-10-22` (two zips: `…-docs.zip` and `…-design-baseline.zip`; see `MIGRATION_INSTRUCTIONS.md`) |
| Repository state (verified 22 Oct 2026) | `swa01wk/cenomi-dashboard-agent` @ `5bbd62a` on `main`: **only `README.md`**. The "Committed" column below records that state. |
| Migration update (22 Oct 2026) | All files in this manifest are committed on branch `docs/cenomi-project-handoff` (pull request pending merge; see `plans/STATUS.md`). They reach `main` only when the user merges. ED-03 Option A was approved on 22 Oct 2026, scoped to preserving the reference documents and design baseline |
| Integrity | Every file in the package is listed with its SHA-256 in `SHA256SUMS`. In the repository this file is `docs/handoff/SHA256SUMS`, with paths relative to the repository root: run `sha256sum -c docs/handoff/SHA256SUMS` from the root. Files edited at migration time are listed in `HANDOFF_CONSISTENCY_REPORT.md` § Post-package changes at migration |

## Where things live today, and what cannot be transferred

| Source in the original account | Transferable? | Preserved in the package by |
|---|---|---|
| Claude Project "Dashboard Agent": 3 uploaded reference docs and 5 `claude/` docs | Files can be copied | Byte copies in `docs/reference/` and `docs/reference/planning-history/` (sha256 recorded) |
| Claude Docs artifact "Cenomi POC — Final Design Gate (GD)" (`…/artifact/FR1f4Feb9ae8uvSgwjdtGv`) | **No.** The link is private to the original account | Markdown export of all 8 tabs plus a PNG of the embedded diagram → `docs/reference/final-design-gate/` |
| Claude Docs artifact "Cenomi POC — Engineering Specification Plan" (`…/artifact/DSDBfLnW8KosmeLTpGQvLk`) | **No** | Markdown export of all 13 tabs plus 3 diagram PNGs → `plans/proposed/engineering-specification-plan/` |
| Design canvas "Cenomi Dashboard Agent — POC Design" v27 (`…/artifact/WyJr2wZFCGVdBY2a13uGyM`) | **No.** Interactive canvas, private link | (a) Runnable HTML of all 31 boards plus `support.js` runtime, (b) 31 full-page PNG renders, (c) `DESIGN_BOARDS_TEXT.md` text extract, (d) reference models and test results → `docs/design/baseline/` |
| Claude memory for this Project | No | Not needed. Everything durable is in `PROJECT_HANDOFF.md` and `STATUS.md` |
| Conversation history | No | Not needed. Decisions are in the GD register and `STATUS.md` |

**Interactive artifacts and what replaces them.** The canvas and the two Docs artifacts cannot be opened from the new account. Their behaviour and decisions are preserved as follows:

| Interactive artifact | Behaviour preserved by | Decisions and content preserved by |
|---|---|---|
| DX1 shell prototype (Main) | `boards/Main.dc.html` (runs locally), `renders/Main.png` | `DESIGN_BOARDS_TEXT.md` § DX1; GD register DXD-01…20 |
| DX2 Admin and Tenant prototypes | `boards/Admin.dc.html`, `boards/Tenant.dc.html`, `boards/verify/card-*.png` | DX2-Notes, DX2-Decisions, DX2-Verify (HTML, PNG and text); GD KPI tab |
| DX3 chart parity gallery | `boards/DX3-Gallery.dc.html`. **Runs the GDQ-06 self-test on real ECharts 5.6.0 when online** | DX3-Parity, DX3-Decisions; GD KPI tab parity table |
| DX4 agent workspace | `boards/DX4-Workspace.dc.html`, `boards/dx4/*.png` (J1–J10 captures) | DX4-Spec, DX4-Journeys, DX4-AGUI, DX4-Decisions; `reference-models/dx4/` |
| DX5 GenUI lab | `boards/DX5-GenUI.dc.html` (includes the OI-13 wording fix), `boards/dx5/*.png` | DX5-Contract, DX5-Verify, DX5-Decisions; `reference-models/dx5/` |
| DX6 Insight Inbox | `boards/DX6-Inbox.dc.html`, `boards/dx6/*.png` (K-journey captures) | DX6-Contract, DX6-Scenarios, DX6-Refinements, DX6-Verify; `reference-models/dx6/` |
| GD and ESP Docs artifacts (checkbox and dropdown state) | Recorded as text in the exports. For example, GDQ answers appear as "Option A (recommended)" and the checklist as `[x]` | The exports themselves |

## Manifest

Legend:
- **A** = authoritative; **S** = supporting; **H** = handoff/control.
- "Committed" = present in the repository today.
- "Action": **Upload** = add to the new Claude Project knowledge; **Commit** = add to the repository; **Repo only** = too large or not useful as Project knowledge.

### Handoff and control files

| # | File | Purpose | Current location | Intended repo path | Version / date | A/S/H | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| H1 | `PROJECT_HANDOFF.md` | Complete project state and continuation instructions | Handoff package | `docs/handoff/PROJECT_HANDOFF.md` | 2026-10-22 | H | No | Upload + Commit | All A files |
| H2 | `STATUS.md` | Live status: phase, decisions, gates, blockers, next tasks | Handoff package | `plans/STATUS.md` | 2026-10-22 | H (becomes the canonical progress file; ESP item 12) | No | Upload + Commit | H1, ESP |
| H3 | `MIGRATION_MANIFEST.md` | This inventory | Handoff package | `docs/handoff/MIGRATION_MANIFEST.md` | 2026-10-22 | H | No | Upload + Commit | — |
| H4 | `ONBOARDING_PROMPT.md` | First prompt for the new Claude Project | Handoff package | `docs/handoff/ONBOARDING_PROMPT.md` | 2026-10-22 | H | No | Paste into new Project + Commit | H1–H3 |
| H5 | `HANDOFF_CONSISTENCY_REPORT.md` | Continuity verification (10 checks) | Handoff package | `docs/handoff/HANDOFF_CONSISTENCY_REPORT.md` | 2026-10-22 | H | No | Upload + Commit | H1–H3 |
| H6 | `MIGRATION_INSTRUCTIONS.md` | Exact steps for repository and Project migration | Handoff package | `docs/handoff/MIGRATION_INSTRUCTIONS.md` | 2026-10-22 | H | No | Commit (read once) | H3 |
| H7 | `SHA256SUMS` | Hashes of every migrated file (excluding itself and the pre-existing `README.md`) | Package root | `docs/handoff/SHA256SUMS` (added at migration on the user's instruction) | 2026-10-22 | H | No | Commit | All files |

### Authoritative reference documents (documents 1–3)

| # | File | Purpose | Current location | Intended repo path | Version / date | A/S | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| A1 | `Cenomi_Dashboard_Intelligence_Agent_PRD.md` | Product requirements | Claude Project file (original account); package copy | `docs/reference/Cenomi_Dashboard_Intelligence_Agent_PRD.md` | v1.0, 21 Oct 2026; sha256 13ec1b69… | A | No | Upload + Commit (ED-03 A) | — |
| A2 | `Cenomi_Dashboard_Intelligence_Agent_Technical_Architecture_and_Implementation_Plan.md` | Technical architecture and build plan | Claude Project file; package copy | `docs/reference/…Technical_Architecture_and_Implementation_Plan.md` | v1.0, 21 Oct 2026; sha256 dc26d235… | A | No | Upload + Commit (ED-03 A) | A1 |
| A3 | `ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` | V2 endpoints, chart mapping, SQL traces, risks (320 KB) | Claude Project file; package copy | `docs/reference/ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` | Generated 2026-10-13; sha256 e01113fc… | A | No | Upload + Commit (ED-03 A) | — |
| A4 | `docs/reference/README.md` | Versions and hashes of the reference set | Package | same | 2026-10-22 | S | No | Commit | A1–A3, GD1–GD9 |

### Final Design Gate exports (authoritative documents 5, 6 and 7)

| # | File | Purpose | Current location | Intended repo path | Version / date | A/S | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| GD1 | `01_DESIGN_REVIEW_REPORT.md` | **Complete Final Design Gate report**: outcome, findings, GDQ-01…12 answers, checklist | Docs artifact (not transferable) → exported | `docs/reference/final-design-gate/01_DESIGN_REVIEW_REPORT.md` | Gate outcome 22 Oct 2026 | A | No | Upload + Commit | GD3 |
| GD2 | `02_ARCHITECTURE_AND_INTERACTION_MODEL.md` | Consolidated architecture, screens, flows, consolidation | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 | A | No | Upload + Commit | GD9 |
| GD3 | `03_DECISION_REGISTER.md` | **Consolidated decision register**: 141 decisions, gate decisions, 17 final definitions | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 (126/7/1/2/5) | A | No | Upload + Commit | — |
| GD4 | `04_TRACEABILITY.md` | 70 requirements → design evidence → spec homes | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 | A | No | Upload + Commit | A1 |
| GD5 | `05_KPI_AND_DATA_RECONCILIATION.md` | **KPI parity, canonical figures, C1–C21, scenarios, invariants** | Exported | `docs/reference/final-design-gate/` | sd-2026.10.20-01; 51/51 | A | No | Upload + Commit | DB-RM |
| GD6 | `06_SPECIFICATION_INVENTORY_GD.md` | GD-time spec inventory (detail superseded by ESP4) | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 | S | No | Upload + Commit | — |
| GD7 | `07_FIVE_DAY_FEASIBILITY.md` | Effort basis for GDQ-01 | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 | A | No | Upload + Commit | — |
| GD8 | `08_OPEN_ISSUES_AND_RISKS.md` | OI-01…15, R-01…14 | Exported | `docs/reference/final-design-gate/` | 22 Oct 2026 | A | No | Upload + Commit | — |
| GD9 | `diagram_consolidated_architecture.png` | Architecture diagram from GD2 | Docs widget → screenshot | `docs/reference/final-design-gate/` | 22 Oct 2026 | S | No | Commit (repo only) | GD2 |

### DX1–DX6 design baseline (authoritative document 4)

| # | File(s) | Purpose | Current location | Intended repo path | Version / date | A/S | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| DB0 | `README.md` | Board index, normative-for map, how to run, OI-13 note | Package | `docs/design/baseline/README.md` | 2026-10-22 | S | No | Upload + Commit | DB1 |
| DB1 | 31 boards: `Main`, `IA`, `Inventory`, `Direction-A/B/C`, `DX1-Decisions`, `Admin`, `Tenant`, `States`, `DX2-Notes`, `Responsive`, `DX2-Decisions`, `DX2-Verify`, `DX3-Gallery`, `DX3-Parity`, `DX3-Decisions`, `DX4-Workspace`, `DX4-Spec`, `DX4-Journeys`, `DX4-Decisions`, `DX4-AGUI`, `DX5-GenUI`, `DX5-Contract`, `DX5-Verify`, `DX5-Decisions`, `DX6-Inbox`, `DX6-Contract`, `DX6-Scenarios`, `DX6-Refinements`, `DX6-Verify` (each `.dc.html`), plus `support.js` and `canvas.json` | **DX1–DX6 design exports and interaction specifications** (runnable) | Design canvas (not transferable) → exported | `docs/design/baseline/boards/` | Canvas v27 + OI-13 fix | A | No | Commit (repo only; about 22 MB with images) | — |
| DB2 | `boards/dx4/*.png` (13), `boards/dx5/*.png` (20), `boards/dx6/*.png` (20), `boards/verify/*.png` (34) | Journey and verification captures used by the boards | Canvas project files | `docs/design/baseline/boards/{dx4,dx5,dx6,verify}/` | v27 | S | No | Commit (repo only) | DB1 |
| DB3 | `renders/<Board>.png` (31) | Full-page render of every board | Generated 22 Oct 2026 | `docs/design/baseline/renders/` | v27 + OI-13 | S | No | Commit (repo only; about 26 MB). Optionally upload the 7 interactive-board renders | DB1 |
| DB4 | `DESIGN_BOARDS_TEXT.md` | Text of all 31 boards (205 KB): thresholds, scenarios, contracts, decisions | Generated 22 Oct 2026 | `docs/design/baseline/DESIGN_BOARDS_TEXT.md` | v27 + OI-13 | A (text form of DB1) | No | **Upload** + Commit | DB1 |
| DB5 | `render.js`, `text.js` | Regenerate DB3 and DB4 (Playwright) | Package | `docs/design/baseline/` | 2026-10-22 | S | No | Commit | DB1 |
| DB-RM | `reference-models/dx6/{gen_data.py, history.py, replay.py, recon.py, runner_model.py, insights.json, recon.json, runner_results.json, t6py.json, t6js.json}`; `dx5/{dump.json, t5_results.json}`; `dx4/{raw.json, logic_results.json}`; `dx3/data.json`; `gd/{register.json, register.md, trace.md, dx15_decisions.json}` | Reference generator, replay (hash 82fde5250960761d), reconciliation, runner model (c1e36ced42cebecc), test results; machine-readable register | Original session workspace | `docs/design/baseline/reference-models/` | 22 Oct 2026 | S (acceptance reference for figures and hashes) | No | Commit (repo only) | GD5 |

### Engineering Specification Plan exports (Proposed, not approved)

| # | File | Purpose | Current location | Intended repo path | Version / date | A/S | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| ESP0 | `00_OVERVIEW.md` | Summary, baseline and scope freeze, change control | Docs artifact (not transferable) → exported | `plans/proposed/engineering-specification-plan/` | 22 Oct 2026 draft | S (Proposed) | No | Upload + Commit | GD1, GD3 |
| ESP1 | `01_MILESTONE_DEPENDENCY_PLAN.md` | M0–M6 graph, gates, CF-0…CF-6, concurrency rules | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP0 |
| ESP2 | `02_FIVE_DAY_VERTICAL_SLICE.md` | Slice scope, day plan, E2E-S1…S3 | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP1 |
| ESP3 | `03_FULL_SCOPE_ROADMAP.md` | Per-milestone deliverables, interfaces, acceptance, tests, gates | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP1 |
| ESP4 | `04_SPECIFICATION_INVENTORY.md` | **17 docs, 10 plans, specs, ADRs; writing order 1–43; 7 PRs** | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP1 |
| ESP5 | `05_REPOSITORY_STRUCTURE.md` | Proposed tree and ownership rules | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP9 |
| ESP6 | `06_M0_AUTHORING_PLAN.md` | PR-M0 sessions A–E, self-review checklist, M0 task cards | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP4, ESP7 |
| ESP7 | `07_ENGINEERING_DECISIONS_FOR_APPROVAL.md` | ED-01…ED-11, configuration, approval checklist | Exported | same | draft (no ED approved) | S (Proposed) | No | Upload + Commit | — |
| ESP8 | `08_STACK_AND_RUNTIME.md` | Version lines, processes, DB roles | Exported | same | versions checked 22 Oct 2026 | S (Proposed) | No | Upload + Commit | GD3 (DR-027) |
| ESP9 | `09_SOURCES_OF_TRUTH.md` | Canonical source per concern, bootstrap rule, versioning | Exported | same | draft | S (Proposed) | No | Upload + Commit | — |
| ESP10 | `10_GOLDEN_DATA_AND_EVALUATION.md` | Fixture tiers, expected outputs, evaluation and E2E cases | Exported | same | draft | S (Proposed) | No | Upload + Commit | GD5 |
| ESP11 | `11_LOCAL_DEVELOPMENT_AND_CI.md` | Compose, environment, DB init, seeding, CI | Exported | same | draft | S (Proposed) | No | Upload + Commit | ESP8 |
| ESP12 | `12_ADR_PROCESS_AND_STATUS.md` | ADR process, initial ADRs 0001–0014, STATUS template | Exported | same | draft | S (Proposed) | No | Upload + Commit | — |
| ESP13 | `diagram_milestone_dependency.png`, `diagram_full_scope_roadmap.png`, `diagram_five_day_slice.png` | Diagrams for ESP1, ESP3 and ESP2 (the slice diagram was re-drawn with the corrected kind names) | Docs widgets → screenshots | same | 22 Oct 2026 | S | No | Commit (repo only) | ESP1–3 |

`plans/proposed/` is a staging location chosen so that unapproved plans are never mistaken for the approved `plans/` files. When the user approves the ESP, PR-M0 writes `plans/ROADMAP.md` (item 10) from it, and `plans/proposed/` stays as the record.

### Planning history (supporting)

| # | File | Purpose | Current location | Intended repo path | Version / date | A/S | Committed | Action | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| P1 | `PLANNING_ASSESSMENT_v0.1.md` | G0 assessment, first draft | Project `claude/PLANNING_ASSESSMENT_v0.1.md`; package copy | `docs/reference/planning-history/` | 21 Oct 2026 | S | No | Commit | A1–A3 |
| P2 | `PLANNING_ASSESSMENT_v0.2.md` | G0 assessment plus decision register v0.2 | Project `claude/…v0.2.md`; package copy | same | 21 Oct 2026 | S | No | Commit | P1 |
| P3 | `PLANNING_ASSESSMENT_v0.3.md` | G0 final; entity model §1.6, tool catalogue §4.6, lifecycle §4.3 | Project `claude/…v0.3.md`; package copy | same | 22 Oct 2026 | S | No | Upload (optional) + Commit | P2 |
| P4 | `DESIGN_DECISIONS_DX4_DX5.md` | Decision note | Project `claude/…`; package copy | same | 22 Oct 2026 | S | No | Commit | — |
| P5 | `DESIGN_DECISIONS_DX5R_DX6.md` | Decision note | Project `claude/…`; package copy | same | 22 Oct 2026 | S | No | Commit | P4 |

## Files that are missing or do not exist yet (by design)

| Expected file | Status |
|---|---|
| The 17 specification documents, 10 plan files (other than `STATUS.md`), ADRs 0001–0014, `specs/*`, `tests/fixtures/*` | **Not written.** They are deliverables of PR-M0…PR-M5 (ESP4) |
| `docs/design/DESIGN_BASELINE.md`, `docs/design/DECISION_REGISTER.md` | Not written (ESP items 3–4); inputs are DB0–DB4 and GD3 |
| AG-UI spike report, ECharts verification result | Not produced (M0-T08, M0-T09) |
| V2 UI design references cited by the API Reference (`ui-v2-dashboard-redesign.md`, `super-admin-dashboard.html`, etc.; DR-039) | **Never supplied.** DX2 and DX3 were designed from the API Reference text. Not required |
| Model provider configuration and API key (GDQ-12) | Not supplied. Must never be committed |

## Recommended Project knowledge set for the new account (text only)

H1, H2, H3, H5, A1, A2, A3, GD1–GD8, DB0, DB4, ESP0–ESP12, A4. Optionally P3. Keep images, HTML boards and reference models in the repository only. Then attach the GitHub repository to the new Project as a synced source.
