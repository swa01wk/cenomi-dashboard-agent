# DESIGN_BASELINE — index of the frozen DX1–DX6 design

| | |
|---|---|
| Document code | DBASE (requirement IDs `DBASE-Rnnn`) |
| Version | 1.0 · 2026-10-22 · PR-M0 |
| Frozen baseline | Design canvas "Cenomi Dashboard Agent — POC Design" **version 27**, plus the OI-13 wording fix present only in the exported `DX5-GenUI.dc.html` |
| Repository copy | `docs/design/baseline/` (committed in PR #1 under ED-03; integrity in `docs/handoff/SHA256SUMS`) |
| Decision register | `docs/design/DECISION_REGISTER.md` |

**DBASE-R001** Specifications cite design evidence by **board file name** (for example `DX4-AGUI`) and, where useful, by decision or journey ID. They never cite the original canvas link, which is private to the original account. The files under `docs/design/baseline/` are never edited (ADR-0002 §3); `make specs-check` verifies their hashes.

**DBASE-R002** Precedence inside the design baseline, highest first:
1. Decision register status (post-gate);
2. contract and specification boards (DX4-Spec, DX4-AGUI, DX5-Contract, DX6-Contract, DX6-Scenarios, DX6-Refinements);
3. interactive prototypes;
4. verification records;
5. superseded phase registers.

The exported boards win over canvas v27 for the OI-13 wording.

**DBASE-R003** Design test doubles are not runtime evidence. In particular, DX3 and DX5 chart results ran on a test double, and real ECharts 5.6.0 verification is a mandatory gate (GDQ-06, DXD-21).

---

## 1. How to open the boards

```bash
cd docs/design/baseline/boards
python3 -m http.server 8766
# open http://localhost:8766/Main.dc.html  (or any other board)
```

Boards are self-contained except for Google Fonts (they fall back to system fonts offline). `DX3-Gallery.dc.html` loads ECharts 5.6.0 from cdnjs; `make echarts-gate` (M0-T08) serves it a pinned local copy instead. A full-page PNG of every board is in `renders/`, and the text of every board is in `DESIGN_BOARDS_TEXT.md`.

---

## 2. Board index and what each is normative for

| Phase | Board file | Interactive | Normative for | Consumed by |
|---|---|---|---|---|
| DX1 | `Main.dc.html` | yes | App shell, rail, docked panel, synthetic banner, data-as-of treatment; canonical DX6 insights in the shell | ARCHITECTURE §6, PRODUCT_SPEC §3 |
| DX1 | `IA.dc.html` | | Navigation map and the core analytical loop | ARCHITECTURE §6.2 |
| DX1 | `Inventory.dc.html` | | Screen and overlay inventory. The notifications overlay was later removed by GDQ-08; the tenant inbox was added by DXD-79 | PRODUCT_SPEC §3 |
| DX1 | `Direction-A.dc.html` | | Selected visual direction, Ink & Violet: type, palette roles | DESIGN_SYSTEM (PR-M2) |
| DX1 | `Direction-B.dc.html`, `Direction-C.dc.html` | | Not selected; reference only | — |
| DX1 | `DX1-Decisions.dc.html` | | DXD-01…09 (superseded as a list by the register) | — |
| DX2 | `Admin.dc.html` | yes | 12 Admin cards: layout, filters, interactions, drilldowns, focus overlay | Card specs (PR-M2) |
| DX2 | `Tenant.dc.html` | yes | Tenant card groups for lease T-31206 | Card specs (PR-M2) |
| DX2 | `States.dc.html` | | The card state vocabulary | PRODUCT_SPEC §4, DESIGN_SYSTEM |
| DX2 | `DX2-Notes.dc.html` | | Parity notes and intentional differences per card | KPI_CATALOG, card specs |
| DX2 | `Responsive.dc.html` | | Tablet and mobile layouts; breakpoints 1280 and 820 px | ARCHITECTURE §6.10 |
| DX2 | `DX2-Decisions.dc.html`, `DX2-Verify.dc.html` | | DXD-10…20; 64/64 checks | — |
| DX3 | `DX3-Gallery.dc.html` | yes | 15 V2 visuals, selection contract, accessibility layer; **contains the GDQ-06 self-test** | M0-T08, viz primitives (PR-M2) |
| DX3 | `DX3-Parity.dc.html`, `DX3-Decisions.dc.html` | | Parity assessment, treemap thresholds (area CV ≤ 5 %, order ≥ 90 %, aspect ≤ 1.25 × reference), fallbacks (DXD-21…30) | ADR-0011 (PR-M2) |
| DX4 | `DX4-Workspace.dc.html` | yes | Agent panel and workspace; journeys J1–J10; inspector; history; cancel | AGENT_ARCHITECTURE, AGUI_INTEGRATION |
| DX4 | `DX4-Spec.dc.html` | | Lifecycle states shown to users, answer order, errors and gaps, selection semantics, history and resume | ARCHITECTURE §8.1, AGENT_ARCHITECTURE |
| DX4 | `DX4-Journeys.dc.html` | | Verified step captures of J1–J10 | Playwright J suites |
| DX4 | `DX4-AGUI.dc.html` | | Run identity, event → client-state reducer, retry kinds, idempotency, reconnection; assumptions A1–A8 | ARCHITECTURE §8.4 (spike), AGUI_INTEGRATION |
| DX4 | `DX4-Decisions.dc.html` | | DXD-31…40 | — |
| DX5 | `DX5-GenUI.dc.html` | yes | Catalogue of 15 kinds, validator, View as, continuity (includes the OI-13 fix) | GENERATIVE_UI (PR-M4) |
| DX5 | `DX5-Contract.dc.html` | | `analysis_result.v1`, `cenomi.presentation.v1`, per-kind rules, composition policy P1–P6, calculation records | API_CONTRACTS, GENERATIVE_UI |
| DX5 | `DX5-Verify.dc.html`, `DX5-Decisions.dc.html` | | 3,778 logic + 45/45 browser checks; DXD-41…62 | — |
| DX6 | `DX6-Inbox.dc.html` | yes | Insight Inbox v2: K1–K12, three roles, replayed detectors | PROACTIVE_INTELLIGENCE (PR-M6) |
| DX6 | `DX6-Contract.dc.html` | | detectors-1.1 thresholds, scoring, privacy, insight API, tables, DXD-63…93 | PROACTIVE_INTELLIGENCE, ADR-0013 |
| DX6 | `DX6-Scenarios.dc.html` | | S1–S9, N1–N11 with expected outcomes (S6 retired, S7 corrected) | SYNTHETIC_DATA_STRATEGY, fixtures |
| DX6 | `DX6-Refinements.dc.html` | | KPI reconciliation C1–C21, privacy, idempotency, priorities (DXD-80…93) | KPI_CATALOG, PROACTIVE_INTELLIGENCE |
| DX6 | `DX6-Verify.dc.html` | | 44 browser, 81 logic, 387 data, 51 invariant, 13 runner checks | — |

---

## 3. Reference models (acceptance references, not application code)

| Folder | Provides | Used as |
|---|---|---|
| `reference-models/dx6/` | Reference generator for `sd-2026.10.20-01`, declared history, replay (`replay_hash` `82fde5250960761d`), reconciliation (51/51), runner model (`reference_hash` `c1e36ced42cebecc`) | The independent source of the canonical figures and hashes (ARCH-R084). M1 re-implements the generator from SYNTHETIC_DATA_STRATEGY; it does not import these files |
| `reference-models/dx5/`, `dx4/`, `dx3/` | Lab data and logic-check results | Evidence of the design checks |
| `reference-models/gd/` | Machine-readable register and traceability sources | Inputs to DECISION_REGISTER |

**DBASE-R004** Code under `backend/`, `apps/` or `packages/` never imports or executes files from `docs/design/baseline/`. The one exception is the `echarts-gate` harness, which serves the DX3 gallery board read-only for verification.
