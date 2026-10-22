# PROJECT_HANDOFF — Cenomi Dashboard Intelligence Agent POC

| | |
|---|---|
| Handoff date | 22 October 2026 |
| Prepared by | Claude (Principal AI Architect role), for Swaroop Shivakumar |
| Phase | **Engineering specification planning.** The design baseline (DX1–DX6) is approved and frozen. The Engineering Specification Plan (ESP) is **proposed, awaiting approval**. |
| Code status | **Nothing implemented.** No application code, migrations, packages, CI or specifications exist in the repository. |
| Repository | `swa01wk/cenomi-dashboard-agent` (public). Verified 22 Oct 2026: branch `main` at commit `5bbd62a`, containing only `README.md` (`# cenomi-dashboard-agent`). Nothing from this handoff had been committed at that point. **Migration update (22 Oct 2026):** the handoff package is committed on branch `docs/cenomi-project-handoff` with a pull request open, pending the user's approval to merge; see `plans/STATUS.md`. |
| Companion files | `plans/STATUS.md` (live status), `docs/handoff/MIGRATION_MANIFEST.md` (every file and where it goes), `docs/handoff/HANDOFF_CONSISTENCY_REPORT.md`, `docs/handoff/MIGRATION_INSTRUCTIONS.md`, `docs/handoff/ONBOARDING_PROMPT.md` |

**How to use this document.** It gives a summary and points to the source for everything. Where a figure, rule or decision matters, the authoritative file is named; do not treat this summary as a replacement for it. Paths are the intended repository paths from `MIGRATION_MANIFEST.md`; until the package is committed they are paths inside the handoff package `repo/` folder.

**Labels used.** **[Approved]**: decided by the product owner. **[Proposed]**: a recommendation that has not been approved. **[Pending verification]**: approved, but a check on a real runtime is still outstanding. **[Open]**: needs a decision.

---

## 1. Product vision, business objectives, users and POC goals

**Vision.** This is a self-contained proof of concept. It recreates the Cenomi Admin and Tenant **V2** dashboards, with their KPIs and chart forms, on a realistic and reproducible synthetic PostgreSQL dataset. On top of the dashboards it adds a conversational analytics agent. The agent explains KPIs, retrieves verified values and records, derives comparisons, investigates across KPIs, and answers with validated generative UI delivered over AG-UI. Source: `docs/reference/Cenomi_Dashboard_Intelligence_Agent_PRD.md` §1.

**Central promise (PRD §1).** A user asks a business question in plain language. They get back an accurate, evidence-backed answer in the most useful presentation, without knowing the schema or setting dashboard filters by hand.

**Principles (PRD §1).**
- Charts and the agent share one set of metric definitions.
- All numerical computation is deterministic.
- No data is invented.
- Observation, hypothesis and causation are kept separate.
- When data is absent, the answer still helps.
- Access boundaries are secure.
- Follow-up questions keep their context.

**Target users (PRD §3).**
- Portfolio administrator
- Leasing manager
- Operations / service manager
- Fit-out manager
- Tenant
- Business analyst / executive

The design fixtures use four principals:
- Portfolio admin
- Central regional manager
- Tenant user on lease **T-31206** (Lumen Home, Sandstone Galleria)
- Tenant company user

**Original POC goals (PRD §2, §11).**
1. All 12 Admin V2 cards and the Tenant card groups, at parity.
2. Seeded multi-year synthetic data.
3. A canonical KPI registry.
4. An agent covering levels 3–5.
5. AG-UI with validated generative UI.
6. At least 150 benchmark questions.
7. 100% deterministic numeric checks.
8. Access isolation.
9. Measured latency (NFR-01).

**Out of scope (PRD §2):**
- Production data or writes
- Yardi/SAP/Appian integrations
- Payments data
- Autonomous actions
- Causal guarantees
- Model-written SQL, HTML or JS
- Mobile-native apps
- Production SLOs

Everything shown must be labelled **synthetic**.

## 2. Authoritative reference documents

Precedence when sources conflict, highest first [Approved; project instructions §14]:
1. Explicit current user instructions
2. Approved decisions (the GD register, plus later approved EDs and ADRs)
3. PRD
4. Technical Architecture & Implementation Plan (TA)
5. API Reference
6. Repository
7. Claude's recommendations

| # | Document | Exact file (intended repo path) | Version | Original location |
|---|---|---|---|---|
| 1 | Product Requirements Document | `docs/reference/Cenomi_Dashboard_Intelligence_Agent_PRD.md` | v1.0, 21 Oct 2026; sha256 `13ec1b69…3aa67c` | Claude Project file |
| 2 | Technical Architecture & Implementation Plan | `docs/reference/Cenomi_Dashboard_Intelligence_Agent_Technical_Architecture_and_Implementation_Plan.md` | v1.0, 21 Oct 2026; sha256 `dc26d235…7b4cb77436` | Claude Project file |
| 3 | Admin & Tenant Dashboard API, Chart and SQL Reference | `docs/reference/ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` | Generated 2026-10-13 (code trace of `cenomi-api-2` and `cenomi-frontend-2`); sha256 `e01113fc…2dcce7` | Claude Project file |
| 4 | DX1–DX6 design artifacts (31 boards) | `docs/design/baseline/boards/*.dc.html` (runnable), `docs/design/baseline/renders/*.png`, `docs/design/baseline/DESIGN_BOARDS_TEXT.md` | Canvas **version 27**, plus one local wording fix (OI-13) | Claude design canvas (link not transferable) |
| 5 | Consolidated Design Decision Register | `docs/reference/final-design-gate/03_DECISION_REGISTER.md` | 141 decisions plus the gate decisions of 22 Oct 2026 | Claude Docs artifact "Cenomi POC — Final Design Gate (GD)" |
| 6 | Final Design Gate review | `docs/reference/final-design-gate/01_…08_*.md` (8 tabs) | Outcome recorded 22 Oct 2026 | Same Docs artifact |
| 7 | KPI and synthetic data reconciliation | `docs/reference/final-design-gate/05_KPI_AND_DATA_RECONCILIATION.md` plus `docs/design/baseline/reference-models/dx6/` | Dataset `sd-2026.10.20-01`, 51/51 checks | Same Docs artifact plus local models |

Full hashes are in `docs/reference/README.md` and `SHA256SUMS`.

Supporting (non-authoritative) material:
- Planning history in `docs/reference/planning-history/`: Planning Assessment v0.1, v0.2 and v0.3 (G0), and the design decision notes DX4–DX5 and DX5R–DX6.
- The proposed ESP in `plans/proposed/engineering-specification-plan/`.

## 3. DX1–DX6 approved design summary

All six phases are approved. Together they form the frozen baseline (22 Oct 2026). Board index and what each board is normative for: `docs/design/baseline/README.md`.

| Phase | What it fixed | Evidence | GD status |
|---|---|---|---|
| DX1 Information architecture | 4 screens, a docked agent panel and 4 overlays (GDQ-08 later removed the notifications overlay). Visual direction A, "Ink & Violet". Synthetic banner and "data as of" treatment | Main (interactive shell), IA, Inventory, Direction A/B/C, DX1-Decisions | Approved |
| DX2 Dashboards | 12 Admin cards and the Tenant dashboard; card states; tablet and mobile layouts; parity notes | Admin and Tenant (interactive), States, Responsive, DX2-Notes; 64/64 browser checks | Approved |
| DX3 Chart parity | 15 V2 visuals; accessibility layer; selection contract `selection_ref.v1` | DX3-Gallery (interactive), DX3-Parity. Run only on a **test double**; real ECharts 5.6.0 has not run | Conditionally approved [Pending verification] |
| DX4 Agent workspace | Panel and workspace; 10 journeys J1–J10; evidence/inspector; history and resume; AG-UI handoff contracts | DX4-Workspace (interactive), Spec, Journeys, AGUI; 77/77 browser and 211 logic checks | Conditionally approved [AG-UI SDK check pending] |
| DX5 Generative UI | `analysis_result.v1`; `cenomi.presentation.v1`; a closed registry of **15 kinds**; composition policy P1–P6; validator; "View as" | DX5-GenUI (interactive), Contract, Verify; 3,778 logic and 45/45 browser checks | Approved with refinements |
| DX6 Proactive intelligence | Insight Inbox v2; detectors-1.1 (D1–D8); scoring; lifecycle; privacy; runner protocol; golden scenarios S1–S9 and N1–N11; 12 journeys K1–K12 | DX6-Inbox (interactive), Contract, Scenarios, Refinements, Verify; 44 browser, 81 logic, 387 data, 51 invariant and 13 runner checks | Conditionally approved, refinements done |

**Canonical screens (GD architecture tab):**
- Admin dashboard
- Tenant dashboard
- Analytical workspace
- Insight Inbox
- Agent panel (docked; an overlay below desktop width)
- Overlays:
  - Card focus (tabs: Chart, Table, Records, Definition)
  - Inspector (tabs: Evidence, Definition, Records, Execution)
  - Inline filter-change confirmation

The bell opens the inbox filtered to new notifications (GDQ-08); there is no separate notifications overlay.

**Canonical journeys:**
- DX4 **J1–J10**:
  - J1 ask from a selection
  - J2 investigate in the workspace
  - J3 dashboard filter proposal with confirm and undo
  - J4 partial result
  - J5 unavailable concept
  - J6 versions
  - J7 history and resume
  - J8 tenant isolation
  - J9 cancelled run
  - J10 isolation
- DX5 GenUI journeys (catalogue, validator, continuity, View as).
- DX6 **K1–K12**:
  - K1 scheduled run
  - K2 event-triggered Watch
  - K3 evidence and "why"
  - K4 investigate
  - K5 dismiss
  - K7 and K11 grants and privacy
  - K10 shared summary
  - K12 runner
  - Full list on DX6-Inbox and `DESIGN_BOARDS_TEXT.md`
- PRD §9 journeys 1–6. Journey 3, the fit-out cohort, is specified with existing components under GDQ-09.
- Slice demo journeys E2E-S1 to E2E-S3 (§15).

**Shared components** that consolidate six capabilities which earlier phases designed more than once (GD architecture tab):
- EvidencePanel
- RecordsTable
- StatementList (Observed / Derived / Hypothesis / Recommendation / Unavailable)
- One AccessScope service
- One append-only version pattern
- One freshness (stale) rule

## 4. Final Design Gate (GD) outcome

Source: `docs/reference/final-design-gate/01_DESIGN_REVIEW_REPORT.md` and `03_DECISION_REGISTER.md` §"Gate decisions recorded (22 Oct 2026)".

- **Recommendation accepted:** Conditional Go to engineering specification planning.
- **GDQ-01 to GDQ-12: all Option A** [Approved, 22 Oct 2026]:

  | ID | Decision |
  |---|---|
  | GDQ-01 | Five-day vertical slice, then the full scope (about 20 working days in total) |
  | GDQ-02 | PRD §7 catalogue parity through the DX5 registry, plus donut and stacked variants of `bar` and a progress variant of `kpi` |
  | GDQ-03 | Materialized as-of snapshots, generated by the seed and reconciled to parity at `as_of` |
  | GDQ-04 | S6/S7 corrections accepted; the tenant Watch path is tested with a labelled micro-fixture |
  | GDQ-05 | Deterministic per-user ordering within a priority band after repeated "not useful". It never hides a P1 and never changes thresholds |
  | GDQ-06 | Real ECharts verification is a **mandatory engineering gate** |
  | GDQ-07 | Custom squarified treemap preferred |
  | GDQ-08 | The bell opens the inbox filtered to new |
  | GDQ-09 | Fit-out cohort journey built from existing components plus a golden scenario |
  | GDQ-10 | The 17 defaults approved as a batch, with final definitions |
  | GDQ-11 | AG-UI verification spike in M0 |
  | GDQ-12 | Provider adapter with a primary and a fallback model. Model names and keys are configuration, set before agent integration |

- **DXD-80 to DXD-93 approved.** DX1–DX6 is the approved baseline, and **scope is frozen**.
- **Register after the gate:** 141 decisions:
  - 126 approved and ready
  - 7 verification pending
  - **1 needs a decision (DR-036, evaluation scoring)**
  - 2 deferred from five days
  - 5 superseded
- **Outstanding conditions and verification gates** (carried into the build gates):
  - Real ECharts 5.6.0 rendering of every chart (DR-007, DXD-21, DXD-61; OI-01, OI-03). Must pass before the M2 exit; the M0 harness runs first.
  - AG-UI SDK event names and semantics against the pinned release (DR-017, DXD-40; OI-12). Checked by the M0 spike and at the M4 exit.
  - axe-core and screen-reader checks on the real build (OI-02). Due at the M2 and M4 exits.
  - Model provider, model names and API key (GDQ-12). This is configuration, needed before slice day 3.
  - DR-036 evaluation scoring. Proposed as ED-11, needed before PR-M5.

Not ticked on the GD checklist and therefore not claimed as approved:
- Individual acceptance of the traceability tab and the KPI tab.
- The GD-doc specification inventory.

The user's approval message covered the gate decisions, DXD-80 to DXD-93, the baseline and the scope freeze.

## 5. Architectural principles, decisions and constraints

Source: `docs/reference/final-design-gate/02_ARCHITECTURE_AND_INTERACTION_MODEL.md` and `03_DECISION_REGISTER.md`.

- **One metric service** feeds every chart, every agent answer and every insight. The LLM plans and explains but **never computes a number** (DR-031: fact tokens plus a verifier).
- **Layers** (project instructions §2, as refined in GD):

  | Layer | Responsibility |
  |---|---|
  | State machine | Lifecycle, budgets, recovery, cancellation. Coverage is an outcome, not a state |
  | Task DAG | Bounded parallel execution; at most one re-plan |
  | Agent | Planner and synthesizer; writes fact tokens only |
  | Semantic layer | Metric YAML; kinds parity, corrected, derived, new; relationships; unavailable concepts |
  | Analytics execution | Parameterized SQL with a mandatory scope fragment; derivations; content-addressed datasets |
  | Context and evidence | Analytical state, facts, evidence envelopes, immutable versions, run ledger |
  | Presentation | Bounded policy; closed registry; server and client validation; deterministic table fallback |
  | AG-UI | Transport |
  | Proactive intelligence | Detectors and the insight lifecycle |
  | Authorization | AccessScope on every read, resume, import, deep link and delivery; uniform refusals |

- **Key rules:**
  - Parity policy DR-001/002: reproduce business definitions and visual forms; never reproduce defects. Where a quirk changes a number, keep the parity metric and add a named corrected metric.
  - Frozen `as_of` = 2026-10-20 (DR-003/004). `NOW()` is banned in metric SQL.
  - Asia/Riyadh bucketing; timestamps stored in UTC (DR-006).
  - Business data is read-only to the app (DR-013).
  - No row-level security; instead a mandatory scope fragment, a lint and a read-only role (DR-021).
  - Plain `@ag-ui/client`, no CopilotKit (DR-016).
  - In-app notifications only (DR-011).
  - Monitoring is historical replay, never live (DR-005).
  - Local Docker Compose only (DR-037).
  - English-first UI with no RTL; Arabic names stored (DR-024).
- **Stack** (DR-027 [Approved]; versions per ESP "Stack and runtime" [Proposed]):
  - Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy Core 2.0, psycopg 3, Alembic, uv
  - Web: Node 22, pnpm, Next.js 16 App Router, React 19, TypeScript strict, TanStack Query v5, zod 4
  - Database: PostgreSQL 16
  - Charts: ECharts **5.6.0 exactly** (DXD-61)
  - Tests: pytest, Vitest, Playwright, axe-core
  - Telemetry: OpenTelemetry with JSON logs
- **Contracts:** Pydantic is the source; JSON Schema 2020-12 is exported from it; TS and zod are generated; CI checks for drift (DR-028). Contracts are bootstrapped as hand-written JSON Schemas until code exists (ESP "Sources of truth").
- **Two run concepts, kept separate:** an *agent run* (threadId, runId, requestId, seq; DXD-40) and an *evaluation run* (run_key; DXD-86).
- **Banned wording:** "overdue" never appears for approvals (there is no SLA), and no causal verbs are used without a mechanism (C4/C5/C7, R-04).

## 6. Admin and Tenant dashboards, KPIs, charts and API references

- **Admin V2 cards (12):**
  - `properties` (stat tiles and occupancy meter, HTML)
  - `kpis` (3 tiles)
  - `leaseRequests` (donut)
  - `salesFunnel` (four-stage HTML flow)
  - `actionRequired` (list)
  - `pendingApprovals` (3 half gauges, bands 0–6 / 7–13 / 14–20 / 21–30 / 31+ days)
  - `pendingAmendments` (type × week heatmap, 4 wk+ includes future-dated)
  - `serviceRequests` (treemap plus permit strip; squarified HTML per GDQ-07)
  - `fitoutHandover` (4 rings; ring = reviewed ÷ (received + remaining + reviewed))
  - `fitoutDrawings` (horizontal stacked bars)
  - `documentStatus` (stacked A–D by mall plus table)
  - `unitDiscrepancy` (diverging bars)
  - Sources: PRD §4.1; API Reference §3a, §3b and §4; parity table in `05_KPI_AND_DATA_RECONCILIATION.md`.
- **Tenant (PRD §4.2):**
  - Overview tiles. Payments shows **Unavailable**.
  - Action required. Lease-scoped (DXD-93).
  - Reported-sales columns
  - Service requests: donut and treemap
  - Documents, events and opportunities
  - The prospective-tenant journey is deferred (DR-026, OI-15).
- **Parity rules:**
  - Every intentional difference is a security fix, a determinism fix or a time-zone normalization, and is shown on the card.
  - The eight PRD §5 caveats are each visible on a card.
  - Each caveat needs **named exposing rows** in the seed manifest (OI-05).
  - Drilldown totals must equal card totals (M2 acceptance).
- **Canonical KPI definitions:**
  - Today they live in the DX2 notes, the DX3 parity board, DXD-80 and the KPI tab.
  - They will be formalized as `specs/metrics/<metric_id>.yaml`, with `docs/contracts/KPI_CATALOG.md` generated from them (ESP items 14–15).
  - The metric YAML does not exist yet (OI-14).
- **New as-of metrics (DXD-80):**
  - `approvals.pending_by_delay.asof`
  - `amendments.pending_by_age_band.asof`
  - `units.vacant.asof`
  - Each must equal its parity metric at `as_of`.
- **Canonical figures:** see §7.

## 7. Database, entities, synthetic data, snapshots and golden invariants

- **Schemas:**
  - Taken from the GD architecture:
    - `core`: business data, read-only to the app
    - `meta`: data versions
    - `agent`
    - `insights`
    - `seed_meta`: labels, never granted to the agent
  - **`snap`** (as-of snapshots) is a **[Proposed]** addition from the ESP; the alternative is to put snapshots in `meta`. `DATABASE_SCHEMA.md` decides.
- **DB roles [Proposed, ESP]:**

  | Role | Access |
  |---|---|
  | `cenomi_owner` | DDL, used by migrations only |
  | `cenomi_seed` | Writes `core`, `meta`, `snap` and `seed_meta` |
  | `cenomi_reader` | SELECT on `core`, `meta` and `snap`. Used by the metric executor pool |
  | `cenomi_app` | Reads and writes `agent` and `insights`; no business reads |

- **Entities and lineage:**
  - Location hierarchy: region → mall → property → unit, with explicit `property_groups` (DR-047).
  - Lineage: enquiry → proposal → lease, and unit → inspection → drawing → handover through `fitout_projects` (DR-022).
  - `fitout_drawing_documents` is normalized: one row per document (DR-046).
  - The logical entity list is in Planning Assessment v0.3 §1.6.
- **Synthetic data:**
  - 3 regions and 25 fictional malls: Central 10, Eastern 7, Western 8 (DR-043).
  - PRD §8 volume targets.
  - Events run from 2024-01-01 to `as_of` 2026-10-20 (DR-004).
  - Process-based latent model.
  - Two fixture tiers (DR-033): hand-verified micro fixtures for metric truth, and a macro seed with property assertions.
  - The reference generator and replay are in `docs/design/baseline/reference-models/dx6/` (`gen_data.py`, `history.py`, `replay.py`, `recon.py`, `runner_model.py`).
  - **Reference hashes:**

    | Item | Value |
    |---|---|
    | Full insight replay hash | `82fde5250960761d` |
    | Runner reference_hash | `c1e36ced42cebecc` |
    | Runner tests | 13/13 |
    | Reconciliation | 51/51 |

- **Approved dataset:** `sd-2026.10.20-01`, `as_of` 2026-10-20. Canonical figures (KPI tab):

  | KPI and scope | Value |
  |---|---|
  | Pending approvals, all regions | 232 pending; 92 waiting 31+ days |
  | Pending approvals, Central | 130; 62 waiting 31+ |
  | Rawdah Point Mall | 71 pending (32 proposals / 23 contracts / 16 leases); 41 waiting 31+ (19/15/7) = **66.1%** of Central's 62 and 57.7% of its own pending |
  | Central amendments 4 wk+ | 25 (all types); renewals 18 (Rawdah 9, Sandstone 6, Qasr 3); oldest Rawdah renewal 171 days |
  | Unit discrepancy, September | 18 of 25 malls reported; 87 mismatched of 3,000 (2.9%); Gulf Gate 11 of 142 (7.7%), robust z 15.9 |
  | Vacancy | Central 408 of 3,420 (11.9%); all regions 1,026 of 8,140 (12.6%); Mirage Commons 58 of 299 (19.4%) |
  | Lease T-31206 | Reported sales Jan–Sep 2026 SAR 2,424,000; September SAR 241,800 (+7.5% on Sep 2025); 2 documents to upload; 0 requests in Action required (the company has 2) |

- **Historical snapshots (GDQ-03):**
  - The seed writes weekly and monthly as-of snapshots from its own lifecycle events.
  - A test proves each snapshot equals the parity metric at `as_of` for every mall and region.
- **Golden invariants:** GI-01 to GI-16, 51 checks; 21 cross-phase discrepancies (C1–C21) resolved. Required seed cohorts:
  - C11: 6 resolved Rawdah renewals in the window
  - Lease-scoped T-31206 drawings
  - S1, S2 and S4 cohorts
- **Golden scenarios** (`DX6-Scenarios`; `reference-models/dx6/insights.json`):

  | ID | Insight | Description |
  |---|---|---|
  | S1 | INS-107 | Cross-KPI cluster, P1 |
  | S2 | INS-104 | Mirage vacancy, P2 |
  | S3 | INS-105 / INS-105C | Late discrepancy data, P2 |
  | S4 | INS-106 | Gulf Gate jump, Watch |
  | S5 | INS-103 | Qasr improvement, P3 |
  | S6 | — | **Retired**; became N9, a seasonal pattern with no insight |
  | S7 | T-202 | Tenant drawings, P2 |
  | S8 | INS-090 | Auto-resolve |
  | S9 | INS-101 | Seven versions; merged into INS-107 when D6 runs |

  Quiet counterexamples N1–N11 must not fire.

## 8. Frontend, backend and integration boundaries

Source: ESP "Stack and runtime" and "5 · Repository structure" [Proposed]; topology ED-02 [Proposed].

| Process | Owns | Must never |
|---|---|---|
| `web` (:3000, Next.js 16) | Rendering, routing, client state, chart primitives, GenUI renderers, AG-UI client. Proxies `/api/*` and `/agui/*` | Query the database, compute a metric, call an LLM, decide authorization, render model-written HTML |
| `api` (:8000, FastAPI) | REST, AG-UI SSE endpoint, agent runtime in-process (ED-02 A), LLM adapter, AccessScope, metric executor, insight service | Let model output reach SQL; concatenate SQL; serve UI |
| `db` (:5432, PostgreSQL 16) | The schemas in §7 | Be reached by `web` |
| `migrate` and `seed` (one-shot) | Alembic as `cenomi_owner`; deterministic seed as `cenomi_seed` | Run implicitly at api start-up |
| Insight replay (command) | Checkpoint replay up to `as_of` | Run as a background scheduler |

**Module map** (backend `src/cenomi/`):
- `core`
- `contracts`
- `db`
- `auth`
- `semantic`
- `analytics`
- `api`
- `agent`
- `presentation`
- `agui`
- `insights`
- `seed`

Boundaries are enforced by import-linter; for example, `analytics` never imports `agent`. Web boundaries are enforced by ESLint.

## 9. Agent runtime, state, context, memory, tools and lifecycle

Sources: DX4 boards and the decision register (DR-031, DR-032, DXD-31–40); Planning Assessment v0.3 §4.3–4.6.

- **Lifecycle:**
  1. RECEIVED
  2. CONTEXT_RESOLVED (AccessScope)
  3. PLANNED (LLM call 1 produces an AnalysisPlan)
  4. PLAN_VALIDATED
  5. EXECUTED (DAG with budgets; at most one re-plan)
  6. FACTS_EXTRACTED
  7. SYNTHESIZED (LLM call 2 produces an AnswerDraft with fact tokens)
  8. EVIDENCE_VERIFIED (one retry, then a deterministic template)
  9. COMPOSED
  10. COMPLETE

  Coverage class (supported / derived / partial / related_only / unavailable / error) is an outcome attribute, not a state. Any state can go to ERROR or CANCELLED.
- **State and memory:**
  - Analytical state per thread is stored in PostgreSQL schema `agent`; there is no Redis (DR-029). It holds focus entities, active metrics, dataset refs, selections and decisions.
  - Answers are immutable versions; re-running creates a new version (DXD-33/37).
  - Resume re-checks authorization.
  - The run ledger serves as both audit and replay source.
- **Context from the dashboard:**
  - `selection_ref.v1` plus card filters, treated as a hint.
  - The server re-resolves scope; the client can only narrow it.
  - The panel shows card filters, agent scope and authorization boundaries as three separate rows (DX4 J1).
- **Tools** (DX4; Planning Assessment v0.3 §4.6):
  - Slice tools: `describe_metric`, `get_metric`, `compare`, `get_underlying_records`, `derive`
  - Full scope adds: `get_breakdown`, `get_trend`, `get_data_coverage`, `get_related_metrics`, `reuse_dataset`, `get_linked_cohort` (GDQ-09)
  - Insight tools (DX6)
  - Every tool wraps the metric executor; no tool has its own SQL.
- **Clarification:** only the state is designed. The policy and three golden dialogues are to be specified in `AGENT_ARCHITECTURE.md` (OI-07).
- **Business impact:** limited, because no revenue or rent metric exists. This is an unavailable-concept entry (OI-08).

## 10. AG-UI events and generative UI contracts

- **AG-UI (DR-016/017, DXD-40; DX4-AGUI board):**
  - RUN_* lifecycle
  - TEXT_MESSAGE_* containing verified text only
  - Sanitized TOOL_CALL_* (no rows, no SQL)
  - ACTIVITY_* for the plan
  - STATE_SNAPSHOT/DELTA for dashboard context
  - CUSTOM `cenomi.presentation.v1` for validated payloads
  - Frontend tool `propose_dashboard_filters` with confirm and undo (DR-025)
  - **No reasoning events** forwarded
  - Version pin **ED-10 [Proposed]**: AG-UI 1.0 (`ag-ui-protocol` 1.0.x, `@ag-ui/core` and `@ag-ui/client` 1.x). 1.0 adds `outcome: "cancelled"` and pending frontend tool calls, which match DXD-40 and DR-025. The M0 spike verifies this [Pending verification].
- **Generative UI (DX5; DXD-41–62; GDQ-02):**
  - `analysis_result.v1` (with calculation records and coverage) feeds `cenomi.presentation.v1`.
  - Closed registry of **15 kinds**:
    - `kpi`
    - `text`
    - `table`
    - `bar`
    - `trend`
    - `heatmap`
    - `funnel`
    - `treemap`
    - `compare`
    - `insight`
    - `notice`
    - `unavailable`
    - `evidence`
    - `method`
    - `records`
  - GDQ-02 variants: `bar` gets donut and stacked variants; `kpi` gets a progress variant.
  - Composition policy P1–P6.
  - Server and client (zod) validation.
  - An invalid presentation falls back to a **deterministic table**.
  - "View as" re-presents the same resultRef without re-querying.
  - No model-written HTML, URLs or code.
  - Treemap `minShare 0.08` controls labels only (DXD-22).

## 11. Proactive intelligence (DX6)

Sources: `DX6-Contract`, `DX6-Scenarios` and `DX6-Refinements` boards; DXD-63–93.

**Detectors (detectors-1.1):**

| ID | Name | Rule |
|---|---|---|
| D1 | Concentration | Share ≥ 50%, items ≥ 20, regional total ≥ 30, at least 3 malls; share denominator ≥ 10 |
| D2 | Sustained deterioration | Over 7 weekly or 6 monthly checkpoints: ≥ 4 increases, 0 decreases, net ≥ 5 (counts) or ≥ 2.0 pts (rates), and ≥ 10% |
| D3 | Sustained improvement | Detailed on the DX6-Contract board |
| D4a | Anomaly against own baseline | Rate ≥ 2.0× the trailing mean |
| D4b | Anomaly against peers | Robust z ≥ 3 with ≥ 15 peers |
| D5 | Coverage gap | Coverage < 90% |
| D6 | Cross-KPI co-movement on one entity | "Not concluded: no cause"; cross-entity correlation is never published |
| D7 | Lease trend | Uses the prior year; seasonal movements are not reported |
| D8 | Tenant action required | Lease-scoped (DXD-93) |

- **Thresholds** are configuration keys with versions, quoted in evidence. A change creates a new configuration version and a new run key.
- **Scoring (DXD-66, refined by DXD-90):**
  - Priority = impact × urgency. P1 ≥ 6, P2 3–5, P3 ≤ 2.
  - Low confidence goes to Watch; positive findings are P3.
  - Feedback ordering follows GDQ-05.
- **Lifecycle and runner:**
  - Checkpoint calendar: weekly, monthly on the 20th, plus events (DXD-75).
  - Deduplication and candidate log; silent updates below +10%; band rises re-notify.
  - Versions are append-only.
  - Runner protocol (DXD-86): run_key, claims, staging, atomic publish and outbox; tests R1–R13.
- **Inbox and notifications:**
  - In-app only. The bell opens the inbox filtered to new.
  - Detail with evidence.
  - Actions: acknowledge, dismiss, snooze and investigate (opens a private thread).
  - Shared summaries.
  - Digest.
  - Tenants get an own-lease inbox (DXD-79).
  - Privacy and role-change re-checks (K7, K11).
- **Five-day priority (DXD-92):** within the slice only D2 and D8 are built; the remainder is full scope.

## 12. Authorization, isolation, grounding, missing data, reliability and recovery

- **AccessScope** (DR-019/020; DXD-38, 56, 85):
  - Explicit scope kinds; deny by default; an empty scope gives an empty result, never global data and never a 500.
  - Each card and its endpoint share one permission.
  - The client can only narrow scope.
  - Refs are bound to the principal, the scope fingerprint and the data version.
  - Re-checked on every read, resume, import, deep link and delivery.
  - **Uniform refusals:** a refusal looks the same whether or not the item exists.
  - Tenant-audience detectors never benchmark against other tenants (N6).
- **Grounding:**
  - Every narrative number is a fact token; the verifier rejects any other number.
  - Every displayed value is bound from validated results.
  - Evidence envelope with calculation records.
  - Statement labels: Observed / Derived / Hypothesis / Recommendation / Unavailable.
- **Missing data:**
  - Coverage is a field of every result.
  - Unavailable concepts (payments, footfall, rent and so on) return an Unavailable card and never an estimate.
  - Regional evaluation needs at least 80% coverage (`coverage.min_for_regional_eval`); a D5 alert fires below 90%.
- **Reliability:**
  - Budgets per state; at most one re-plan.
  - Cancellation is an outcome.
  - Reconnect resumes by `seq` without duplicates.
  - Idempotent publish and outbox.
  - Stale evidence follows one freshness rule.

## 13. Testing, fixtures, expected results and acceptance

Source: ESP "Golden data and evaluation" and tab 3 [Proposed]; GD Open issues tab.

- **Fixture tiers:**
  - Micro fixtures per metric, hand-computed, at `tests/fixtures/metrics/<metric_id>/`.
  - Macro seed with canonical figures at `tests/fixtures/golden/canonical_figures.yaml`.
  - Replay goldens: the full hash and a separate slice hash.
  - Principals at `tests/fixtures/principals.yaml`.
- **Suites:**
  - Golden metric tests
  - GI invariants
  - Snapshot reconciliation
  - Isolation and scope-tampering tests
  - Adversarial verifier tests
  - Prompt-injection-as-data tests
  - AG-UI event fixtures validated against both SDKs
  - Per-kind GenUI fixtures and XSS tests
  - Detector micro-series tests
  - Runner crash-injection tests (R1–R13)
  - Playwright journeys J, K and E2E-S
  - axe-core
  - Benchmark of at least 150 cases (EVAL-01–06)
  - Latency (NFR-01: cached metric under 2 s p95; common question under 10 s; heavy investigation under 20 s with progress)
- **Determinism:**
  - ED-08 [Proposed]: a replay LLM provider in CI, with live runs as a manual workflow.
  - DR-036 / ED-11 [Open]: deterministic checks at 100%, an LLM judge for explanation quality, and at least 20% human spot-check.
- **Acceptance per milestone:** see §14 and `plans/proposed/engineering-specification-plan/03_FULL_SCOPE_ROADMAP.md`.

## 14. Implementation strategy, milestone dependencies and specification order

Source: `plans/proposed/engineering-specification-plan/` [Proposed, awaiting approval]. Structure preserved exactly.

**Milestones and hard dependencies.** Each arrow is passable only after the previous gate has passed and the named contract freeze is approved:

```
M0 Foundation ─CF-1→ M1 Data ─CF-2→ M2 Metrics & dashboards ─CF-3→ M3 Agent runtime ─CF-4→ M4 AG-UI & GenUI ─CF-6→ M5 Evaluation ─CF-5→ M6 Proactive intelligence
```

| Milestone | Gate (exit) |
|---|---|
| M0 | `make up` and CI green; contract drift check proven; AG-UI spike report; ECharts verification recorded |
| M1 | Seed reproducible by hash; GI 51/51; canonical figures exact; snapshots equal parity at `as_of` |
| M2 | Golden metric tests; card total = records total; 12 admin cards and tenant groups; ECharts gate passed or fallback applied; axe clean |
| M3 | Verifier rejects ungrounded numbers; J1–J10 pass on replay; budgets enforced |
| M4 | Event fixtures validate against the AG-UI 1.0 SDKs; every kind has a schema, fallback and fixture; DX5 journeys pass |
| M5 | 150+ cases scored; thresholds met; latency measured |
| M6 | Replay hash stable; S1–S9 fire; N1–N11 quiet; R1–R13 and K1–K12 pass |

**Contract freezes:**

| Freeze | Milestone | Covers |
|---|---|---|
| CF-0 | M0 | Toolchain |
| CF-1 | M1 | Data |
| CF-2 | M2 | Analytics |
| CF-3 | M3 | Agent, including evaluation case schema v1 |
| CF-4 | M4 | Presentation |
| CF-5 | M6 | Insights. Frozen **before** CF-6 |
| CF-6 | M5 | Evaluation; needs DR-036 |

**Specification-writing order is not implementation order.**

| | Order | Why |
|---|---|---|
| **Specification PRs** (writing order 1–43) | **M0 → M1 → M2 → M3 → M4 → M6 → M5** | The slice needs the M6 insight contract (CF-5) before day 1, but not the scoring rules. PR-M5 can follow during or after the slice. |
| **Implementation dependency** | **M0 → M1 → M2 → M3 → M4 → M5 → M6** | DR-010: the **complete M6 is implemented only after the M5 gate**, even though its specification is written earlier. Only the slice's thin M6 part (D2, D8, manual replay, inbox list/detail/acknowledge) is built early, because it depends only on M2 snapshots and M4 insight rendering. |

**Specification deliverables (ESP tab 4):**

- **17 documents:**
  - `AGENTS.md`
  - `docs/product/PRODUCT_SPEC.md`
  - `docs/architecture/`:
    - `ARCHITECTURE.md`
    - `DEVELOPMENT_ENVIRONMENT.md`
    - `DATABASE_SCHEMA.md`
    - `SYNTHETIC_DATA_STRATEGY.md`
    - `AGENT_ARCHITECTURE.md`
    - `AGUI_INTEGRATION.md`
    - `PROACTIVE_INTELLIGENCE.md`
    - `EVALUATION_PLAN.md`
  - `docs/design/`:
    - `DESIGN_BASELINE.md`
    - `DECISION_REGISTER.md`
    - `DESIGN_SYSTEM.md`
    - `GENERATIVE_UI.md`
  - `docs/contracts/`:
    - `API_CONTRACTS.md`
    - `AGENT_TOOLS.md`
    - `KPI_CATALOG.md`
- **10 plan files** in `plans/`:
  - `ROADMAP.md`
  - `SLICE_FIVE_DAY.md`
  - `M0_FOUNDATION.md`
  - `M1_DATA.md`
  - `M2_METRICS_AND_DASHBOARDS.md`
  - `M3_AGENT_RUNTIME.md`
  - `M4_AGUI_AND_GENUI.md`
  - `M5_EVALUATION.md`
  - `M6_PROACTIVE_INTELLIGENCE.md`
  - `STATUS.md`
- **Machine-readable specs** in `specs/`:
  - `metrics/`
  - `authorization/`
  - `scenarios/`
  - `detectors/`
  - `genui/`
  - `design/tokens.json`
  - `contracts/*.schema.json`
- **ADRs 0001–0014** in `docs/adr/`.
- **Seven milestone PRs:** PR-M0 (items 1–12), PR-M1 (13–21), PR-M2 (22–26), PR-M3 (27–31), PR-M4 (32–35), PR-M6 (36–40), PR-M5 (41–43).

**ADR process (ESP "ADR process and STATUS"):**
- An ADR is required for any change to a contract, the stack, a module boundary, DB roles, the security model or the agent lifecycle, and for any ED once decided.
- Lifecycle: Proposed → Accepted (the user merges) → Superseded or Rejected. Nothing is deleted.
- Change requests (CR-nnn) under the scope freeze are recorded in `plans/STATUS.md`.

**Source-of-truth rules (ESP "Sources of truth"):**
- One canonical home per concern.
- `specs/` is normative and machine-read.
- `docs/` explains and never restates.
- Generated files are committed and drift-checked.
- Expected values live only in `tests/fixtures/golden`.
- Progress lives only in `plans/STATUS.md`.

**Definition of "Cursor-ready" for every specification:**
- No TBD in normative sections.
- Every interface is typed and versioned.
- Every requirement has an acceptance test ID.
- Open questions are listed separately and are non-blocking.
- Design references point to frozen artifact versions.

## 15. Five-day vertical slice versus the complete POC

**The slice is a delivery cut, not the POC.** It is about 49 hours over 5 days and proves every architectural seam. The **complete approved scope is about 166.5 hours, roughly 20 working days, including the slice** (GDQ-01). Nothing approved is dropped.

| | Five-day slice (days 1–5) | Complete POC (days 1–20) |
|---|---|---|
| Data | Central region; S1, S2, S4 and T-31206 cohorts; weekly approval snapshots 21 Jul → 20 Oct | All 3 regions and 25 malls; S1–S9 and N1–N11; all snapshots |
| Metrics | 6:<br>`approvals.pending_by_delay` v1<br>`.asof` v1<br>`amendments.pending_by_age_band` v1<br>`unit_discrepancy.units` v1<br>`units.vacant` v1<br>`tenant_action_items.open` v1 | Full KPI catalogue |
| UI | 4 admin cards: Pending approvals, Pending amendments, Unit discrepancy, Properties. Tenant: Action required only | 12 admin cards; full tenant dashboard; workspace; inspector |
| Agent | Linear plans of up to 3 steps; 5 tools; fact tokens; verifier | DAG, re-plan, clarification, history and resume, all tools |
| GenUI | 5 kinds: `kpi`, `bar`, `table`, `insight`, `unavailable` | 15 kinds plus variants; View as |
| Proactive | D2 and D8; manual replay; inbox list, detail, acknowledge | D1–D8; event runs; outbox; badge; investigate; dismiss; snooze; digest; sharing; feedback ordering |
| Evaluation | 20 benchmark questions on replay; E2E-S1 to S3 | 150+ cases; live model; performance |
| Exit check | **INS-101** (standalone; the slice has no D6) and **T-202** with evidence | Full replay hash; INS-101 merges into INS-107 |

**Day plan:**

| Day | Hours | Work |
|---|---|---|
| 1 | 10 | Foundation, seed part 1, ECharts gate (GDQ-06) |
| 2 | 10 | Golden data, metrics, cards. Exit check: Central 130 / 62 |
| 3 | 10 | Tools and agent. Exit check: 62 taken from `get_metric` |
| 4 | 10 | AG-UI and GenUI |
| 5 | 9 | Proactive and E2E |

**After the slice:**

| Days | Work | Hours |
|---|---|---|
| 6–10 | M1/M2 complete | 43 |
| 11–12 | M3 | 15 |
| 12–14 | M4 | 20 |
| 15–16 | M5 | 13 |
| 17–19 | M6 | 24.5 |
| 20 | Hardening | 2 |

**Demo journeys:**
- **E2E-S1 (Rawdah):** answer 41, 66.1% of Central's 62, rendered as `kpi` plus `bar`; the word "overdue" does not appear.
- **E2E-S2:** inbox, INS-101, acknowledge (idempotent).
- **E2E-S3:** tenant on T-31206. Action required shows 2 items; T-202; cross-tenant question gets the uniform refusal; payments returns `unavailable`.

## 16. Current status, completed work, pending deliverables and next actions

See `plans/STATUS.md` for the live version.

**Completed and approved:**
- G0 planning (assessments v0.1–v0.3)
- DX1–DX6 design
- Final Design Gate
- GDQ-01 to GDQ-12 recorded as Option A
- DXD-80 to DXD-93
- Scope freeze (22 Oct 2026)

**Completed, not yet approved:** the Engineering Specification Plan (13 tabs, exported to `plans/proposed/engineering-specification-plan/`).

**Not started:**
- All 17 specification documents, 10 plan files, ADRs and machine-readable specs
- All implementation, CI and verification runs (ECharts, AG-UI spike, axe)

**Immediate next actions (in order):**
1. Migrate the package: upload to the new Claude Project and commit to the repository (`MIGRATION_INSTRUCTIONS.md`).
2. The user reviews and approves the ESP (approval checklist in ESP tab 7).
3. The user decides **ED-01, ED-02, ED-04, ED-05 and ED-06**; these block writing the M0 specifications. (ED-03 was approved on 22 Oct 2026, scoped; see §17.)
4. On approval, author PR-M0 (writing items 1–12) in sessions A–E (ESP tab 6), self-review it, and submit it for review.
5. ED-07 to ED-09 before any M0 build. Building also needs a separate explicit go-ahead (ED-06).

## 17. Open decisions, risks, unresolved questions and approvals

**Engineering decisions** (ESP tab 7). All are [Proposed] except **ED-03**, approved on 22 Oct 2026 with a limited scope:

| ID | Decision | Recommended | Needed before |
|---|---|---|---|
| ED-01 | How specs reach the repository: push access plus one PR per milestone, superseding DR-035; or the Project plus manual commit | A (PRs) | **M0 specs** |
| ED-02 | Backend topology: modular monolith with the agent in-process; or separate api and agent services (TA §11) | A | **M0 specs** |
| ED-03 | Frozen reference copies in `docs/reference/` | **Approved: Option A, 22 Oct 2026, scoped** to storing frozen copies of the authoritative reference documents and relevant design exports in the repository. It does not change product architecture, KPI calculations, implementation scope or any other ED | — |
| ED-04 | Slice cards tagged inside milestone plans, plus `SLICE_FIVE_DAY.md` | A | **M0 specs** |
| ED-05 | CI only, no deploy or image push | A | **M0 specs** |
| ED-06 | Build M0 as soon as PR-M0 is merged (still needs a go-ahead) | A | **M0 specs** |
| ED-07 | Dev sign-in with fixture principals and a signed httpOnly cookie | A | M0 build |
| ED-08 | Replay LLM provider in CI; live runs manual | A | M0 build |
| ED-09 | CSS Modules with token-generated CSS variables | A | M0 build |
| ED-10 | AG-UI 1.0 pin | A | PR-M4 |
| ED-11 | DR-036 scoring | A | PR-M5 |

**Open design-adjacent items** (not new design; to be settled in specifications):
- `snap` vs `meta` schema for snapshots
- TA §5.3 mapping to S/N scenarios (OI-06)
- Exposing rows for the eight caveats (OI-05)
- Seed-sourced drilldown records (OI-04)
- Clarification policy (OI-07)
- The 150-question benchmark (OI-09)
- Secret-scanning test (OI-10)
- Latency measurement (OI-11)
- KPI YAML (OI-14)

**Configuration (GDQ-12):** provider, primary and fallback model names, and API key. Needed before slice day 3. **Never commit the key.**

**Top risks** (GD Open issues tab):
- R-01: scope squeezed instead of sequenced
- R-02: seed or metric drift
- R-04: ungrounded numbers or causal wording
- R-14: a single developer is a single point of failure
- Full register R-01 to R-14 in `08_OPEN_ISSUES_AND_RISKS.md`

**Approvals required next:**
1. The ESP (tabs 1–6)
2. ED-01, ED-02, ED-04, ED-05 and ED-06
3. Permission to write PR-M0 to the repository

## 18. Instructions for continuing in the new Claude account

1. **Do not restart discovery or redesign.** DX1–DX6 and the GD register are frozen. A gap becomes an open question in the relevant specification, or a CR in STATUS.md, and never a silent decision.
2. **Read in this order:**
   1. This file
   2. `plans/STATUS.md`
   3. `docs/handoff/MIGRATION_MANIFEST.md`
   4. `docs/reference/final-design-gate/01` and `03`
   5. ESP `00`, `01`, `04`, `06`, `07`
   6. The PRD and TA
   7. The API Reference as needed
   8. Board text and renders as needed
3. **Verify** against `SHA256SUMS` that the reference files are intact.
4. **Confirm with the user** before any work:
   - ESP approval
   - The ED-01, ED-02, ED-04, ED-05 and ED-06 values (ED-03 is already approved, scoped)
   - Whether repository writing is authorized
5. **Then author PR-M0 exactly as ESP tab 6 describes:**
   - Sessions A–E
   - The self-review checklist
   - Writing items 1–12
   - ADRs 0001–0006
6. **Planning only.** Do not:
   - Write application code
   - Install packages
   - Create migrations
   - Create CI
   - Push without explicit authorization

   Implementation needs the user's explicit go-ahead.
7. **Keep `plans/STATUS.md` current** at every merge or decision. Never mark an unapproved specification or ED as complete.
8. **Respect the ordering:** specification PRs go M0, M1, M2, M3, M4, M6, M5; implementation goes M0→M6 with **M6 after M5**.
