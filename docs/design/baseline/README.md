# docs/design/baseline — DX1–DX6 approved design baseline (frozen)

This folder preserves the DX1–DX6 design canvas ("Cenomi Dashboard Agent — POC Design", **version 27**) so that no one depends on the original canvas link (`claude.ai/artifact/WyJr2wZFCGVdBY2a13uGyM`, private to the original account). It is the input for `docs/design/DESIGN_BASELINE.md` (ESP writing item 3, not yet written).

## What is here

| Path | Contents | Preserves |
|---|---|---|
| `boards/*.dc.html` + `boards/support.js` + `boards/canvas.json` | The 31 boards as runnable HTML (React runtime in `support.js`), with `canvas.json` (pages, titles, layout) | **Behaviour** of the 7 interactive prototypes and all specification boards |
| `boards/dx4/`, `boards/dx5/`, `boards/dx6/`, `boards/verify/` | Verified screenshots referenced by the journey and verification boards | Journey evidence |
| `renders/*.png` | Full-page render of every board (22 Oct 2026, no page errors) | Visual record if HTML cannot be run |
| `DESIGN_BOARDS_TEXT.md` | Extracted text of all 31 boards, in canvas order | Every decision, table, threshold and scenario as searchable text |
| `reference-models/` | DX3–DX6 data models, generators, replay and test results; GD register and trace sources | Reproducible numbers and hashes |
| `render.js`, `text.js` | Playwright scripts used to produce `renders/` and the text file | Re-generation |

## How to open the boards

```bash
cd docs/design/baseline/boards
python3 -m http.server 8766
# open http://localhost:8766/Main.dc.html  (or any other board)
```

Boards are self-contained except for Google Fonts (falls back to system fonts offline) and, in `DX3-Gallery.dc.html`, ECharts 5.6.0 from cdnjs. **With internet access, the DX3 gallery self-test runs on real ECharts 5.6.0 — this is GDQ-06 Option A**, the mandatory verification still outstanding. Record its result in `plans/STATUS.md`.

## Wording difference from canvas v27 (OI-13)

`DX5-GenUI.dc.html` here contains the DX6 refinement-1 fix (the rejection sample no longer says "overdue"). Canvas v27 was not republished with it. **These exported files are authoritative for that wording.**

## Board index (canvas order)

| Page | Board | Title | Interactive | Normative for |
|---|---|---|---|---|
| DX1 | `Main.dc.html` | DX1 · App shell prototype (interactive, mid-fidelity) | yes | App shell, rail, docked panel, synthetic banner, data-as-of treatment (DXD-01…20); canonical DX6 insights in the shell |
| DX1 | `IA.dc.html` | DX1 · Navigation map — core analytical loop |  | Navigation map and core analytical loop |
| DX1 | `Inventory.dc.html` | DX1 · Canonical screen inventory |  | Canonical screen and overlay inventory (notifications overlay later removed by GDQ-08; tenant inbox added by DXD-79) |
| DX1 | `Direction-A.dc.html` | Direction A · Ink & Violet (selected) |  | Selected visual direction: Ink & Violet (tokens, type, palette roles) |
| DX1 | `Direction-B.dc.html` | Direction B · Night Operations (optional dark theme later) |  | Not selected (optional dark theme later) — reference only |
| DX1 | `Direction-C.dc.html` | Direction C · Warm Editorial (not selected) |  | Not selected — reference only |
| DX1 | `DX1-Decisions.dc.html` | DX1 · Design decision register (approved) |  | DX1 decision register (superseded as a list by the GD register) |
| DX2 | `Admin.dc.html` | DX2 · Admin dashboard (interactive) | yes | 12 Admin cards: layout, filters, interactions, drilldowns, focus overlay |
| DX2 | `Tenant.dc.html` | DX2 · Tenant dashboard (interactive) | yes | Tenant dashboard card groups for lease T-31206 |
| DX2 | `States.dc.html` | DX2 · Card states |  | Loading, empty, error, unavailable, partial states per card |
| DX2 | `DX2-Notes.dc.html` | DX2 · Parity notes and intentional differences |  | Parity notes and intentional differences per card (basis for KPI_CATALOG caveats) |
| DX2 | `Responsive.dc.html` | DX2 · Tablet and mobile |  | Tablet and mobile layouts |
| DX2 | `DX2-Decisions.dc.html` | DX2 · Design decision register (approved) |  | DX2 decision register |
| DX2 | `DX2-Verify.dc.html` | DX2 · Verification record — 64/64 checks, all 12 Admin cards |  | 64/64 browser checks evidence |
| DX3 | `DX3-Gallery.dc.html` | DX3 · Chart parity gallery (interactive, live ECharts) | yes | 15 V2 visuals with selection contract and accessibility layer; contains the GDQ-06 self-test (loads ECharts 5.6.0 from cdnjs when online) |
| DX3 | `DX3-Parity.dc.html` | DX3 · Parity assessment, findings and decisions |  | Parity assessment, findings, fallbacks (DXD-21…30) |
| DX3 | `DX3-Decisions.dc.html` | DX3 · Design decision register (conditionally approved) |  | DX3 decision register |
| DX4 | `DX4-Workspace.dc.html` | DX4 · Agent workspace (interactive, 10 journeys) | yes | Agent panel and workspace, journeys J1–J10, evidence/inspector, history, cancel |
| DX4 | `DX4-Spec.dc.html` | DX4 · Interaction specification (revised after review) |  | Interaction specification (states, transitions, panel rows, filter proposals) |
| DX4 | `DX4-Journeys.dc.html` | DX4 · Journeys step by step (verified captures) |  | Step-by-step verified captures of J1–J10 |
| DX4 | `DX4-Decisions.dc.html` | DX4 · Decision register DXD-31…40 |  | DXD-31…40 |
| DX4 | `DX4-AGUI.dc.html` | DX4 · AG-UI handoff contracts |  | AG-UI handoff contracts: event mapping, run identity, state shape, CUSTOM payloads |
| DX5 | `DX5-GenUI.dc.html` | DX5 · Generative UI lab, catalogue and validator (interactive, refined) | yes | GenUI lab: 15-kind catalogue, validator, View as, continuity (contains OI-13 wording fix) |
| DX5 | `DX5-Contract.dc.html` | DX5 · Generative UI contract (revised) |  | analysis_result.v1, cenomi.presentation.v1, per-kind rules, composition policy P1–P6 |
| DX5 | `DX5-Decisions.dc.html` | DX5 · Decision register DXD-41…62 |  | DXD-41…62 |
| DX5 | `DX5-Verify.dc.html` | DX5 · Verification record |  | 3,778 logic + 45/45 browser checks |
| DX6 | `DX6-Inbox.dc.html` | DX6 · Insight Inbox v2 (interactive, 12 journeys, 3 roles, replayed detectors) | yes | Insight Inbox v2: 12 journeys K1–K12, 3 roles, replayed detectors |
| DX6 | `DX6-Contract.dc.html` | DX6 · Contract v2: detectors-1.1, privacy, API, tables, decisions DXD-63…93 |  | detectors-1.1 thresholds, scoring, privacy, insight API, tables, DXD-63…93 |
| DX6 | `DX6-Scenarios.dc.html` | DX6 · Golden scenarios v2 (S1–S9, N1–N11; S6 and S7 corrected) |  | Golden scenarios S1–S9 and counterexamples N1–N11 with expected outcomes |
| DX6 | `DX6-Refinements.dc.html` | DX6 · Review refinements: KPI reconciliation, privacy, idempotency, priorities |  | KPI reconciliation (C1–C21), privacy, idempotency, priorities (DXD-80…93) |
| DX6 | `DX6-Verify.dc.html` | DX6 · Verification record v2 |  | 44 browser, 81 logic, 387 data, 51 invariant, 13 runner checks |

## Reference models (`reference-models/`)

| Folder | Files | Use |
|---|---|---|
| `dx6/` | `gen_data.py`, `history.py`, `replay.py`, `recon.py`, `runner_model.py`, `insights.json`, `recon.json`, `runner_results.json`, `t6py.json`, `t6js.json` | Reference generator for sd-2026.10.20-01, declared weekly/monthly history, detector replay (`replay_hash` 82fde5250960761d), reconciliation 51/51, runner protocol model 13/13 (`reference_hash` c1e36ced42cebecc), DX6 test results 387/387 and 81/81 |
| `dx5/` | `dump.json`, `t5_results.json` | GenUI lab data and 3,778 logic-check results |
| `dx4/` | `raw.json`, `logic_results.json` | Agent workspace fixtures and 211 logic checks |
| `dx3/` | `data.json` | Chart gallery data |
| `gd/` | `register.json`, `register.md`, `trace.md`, `dx15_decisions.json` | Machine-readable decision register and traceability sources behind the GD doc |

These are **design-time reference models**, not application code. M1 re-implements the generator from `SYNTHETIC_DATA_STRATEGY.md`; the canonical figures and hashes here are the acceptance reference (DR-043).
