# PRODUCT_SPEC — scope, users, screens, cards and journeys

| | |
|---|---|
| Document code | PSPEC (requirement IDs `PSPEC-Rnnn`) |
| Version | 1.0 · 2026-10-22 · PR-M0 |
| Status | Proposed in PR-M0; normative when merged |
| Sources | PRD v1.0 (`docs/reference/Cenomi_Dashboard_Intelligence_Agent_PRD.md`); TA v1.0; API Reference (2026-10-13); DX1–DX6 boards (canvas v27 + OI-13 fix, `docs/design/baseline/`); GD register (`docs/design/DECISION_REGISTER.md`); GD tabs 02, 04, 05 |
| Extended by | PR-M2 (Appendix A: per-card specifications); PR-M4 and PR-M6 (journey step detail in their plans) |

**This document adds no capability.** Every statement traces to the PRD, a DX board or a decision ID (scope freeze, 22 Oct 2026). A gap found while writing a later specification becomes an open question or a CR, never a silent addition.

---

## 1. Product and scope freeze

**What the POC is.** A self-contained proof of concept with three parts:
1. It recreates the Cenomi Admin and Tenant **V2** dashboards (KPIs and chart forms) on a reproducible synthetic PostgreSQL dataset.
2. It adds a conversational analytics agent. The agent explains KPIs, retrieves verified values and records, derives comparisons, and investigates across KPIs. It answers with validated generative UI delivered over AG-UI.
3. It adds deterministic proactive insights in an Insight Inbox.

**Central promise.** A user asks a business question in plain language and gets an accurate, evidence-backed answer in the most useful presentation, without knowing the schema or setting dashboard filters by hand.

**PSPEC-R001** The approved scope is the frozen DX1–DX6 baseline of 22 Oct 2026, including all approved amendments (GDQ-01…12, DXD-80…93). Scope changes require a CR in `plans/STATUS.md` that cites a PRD requirement or carries the owner's approval.

**PSPEC-R002** Every screen, card and number shown is labelled synthetic. The reference date "As of 20 Oct 2026" is visible on every screen and in every card footer, with the wording "As of 20 Oct 2026 · synthetic data" (DXD-09, DATA-07).

**PSPEC-R003** The five-day vertical slice is a delivery cut of this scope (GDQ-01, ED-04). It is never described as the complete POC. Every card and journey below carries one delivery class.

| Class | Meaning |
|---|---|
| `slice` | Delivered in the five-day slice |
| `full` | Delivered by the full-scope milestones |
| `deferred` | Inside the approved scope; scheduled after the full-scope milestones |

---

## 2. Users, personas and roles

### 2.1 Personas (PRD §3)

| Persona | Primary question | Needed result |
|---|---|---|
| Portfolio administrator | Which malls have rising vacancy or expiring leases? | Comparable occupancy, area and leasing exposure |
| Leasing manager | Where are leads or proposals stalling? | Funnel stage, trend, approval ageing and associated records |
| Operations / service manager | Which request categories are accumulating backlog? | Ranked backlog, status distribution, timeline and drilldown |
| Fit-out manager | Which units or malls are behind on inspection, drawings or handover? | Stage progress and pending work, with status caveats |
| Tenant | What do I need to do next? | Documents, requests, sales submissions and relevant actions |
| Business analyst / executive | What changed and what deserves investigation? | Evidence-backed patterns, limitations and priorities |

### 2.2 Roles and design fixtures

The roles are the seven fixture roles of ARCHITECTURE §9.1 (DR-019). The design fixtures, carried into `tests/fixtures/principals.yaml`, are:

| Fixture | Role | Scope |
|---|---|---|
| Portfolio admin | `PORTFOLIO_ADMIN` | ALL |
| Central regional manager | `REGIONAL_ADMIN` | Central region |
| Tenant user on lease T-31206 (Lumen Home, Sandstone Galleria) | `TENANT_LEASE_CONTACT` | That lease only |
| Tenant company user | `TENANT_COMPANY_ADMIN` | The company's leases |

**PSPEC-R004** One permission controls both a card's visibility and its data (DR-019, DX2-Notes). Cards the role cannot use are hidden, and the page header shows how many are hidden. The persona switch in the top bar is demo-only (DX1 Inventory) and exists only in dev-fixture sign-in mode (ARCH-R040).

---

## 3. Screens and surfaces

| Surface | Kind | Who | Reached from | Main actions | Decisions | Delivered |
|---|---|---|---|---|---|---|
| Admin dashboard | Screen (`/admin`) | Admin roles by permission | Sign-in, rail | 12 cards, card filters, select a data point, Ask, Expand | DXD-02, 10–20 | M2 (`slice`: 4 cards) |
| Tenant dashboard | Screen (`/tenant`) | Tenant users (one lease or a company) | Sign-in, rail | Next actions, documents, requests, sales; change sales year or lease | DXD-02, 13, 16, 93 | M2 (`slice`: Action required) |
| Analytical workspace | Screen (`/workspace`, `/workspace/{threadId}`) | All | Open in workspace, Investigate, rail | Multi-step investigations, pins, history, private threads; rename or delete a thread; switch chart ↔ table | DXD-03, 31–38, 83 | M4 (`full`) |
| Insight Inbox | Screen (`/insights`, `/insights/{insightId}`) | Admin roles; tenants for their own lease (DXD-79) | Bell (opens filtered to new, GDQ-08), rail, card indicators | Triage, evidence, versions, investigate, dismiss, snooze, share summary, feedback | DXD-65–93 | M6 (`slice`: list, detail, acknowledge) |
| Agent panel | Docked at ≥ 1280 px; overlay sheet below; full screen on phone | All | Ask on a card, a selection, top-bar search, `/` | Ask, follow up, confirm or dismiss a filter proposal, remove a context chip | DXD-03, 05, 07 | M4 (`slice`) |
| Card focus | Overlay | All | Expand | Chart, Table, Records, Definition tabs; Ask about this card; Open in workspace | DXD-10, 11, 27 | M2 |
| Inspector | Overlay | All | Evidence or Records on any answer, chart, card or insight | Evidence, Definition, Records, Execution tabs | DXD-04, 36, 39 | M4 |
| Filter-change confirmation | Inline in the conversation | All | An answer that proposes a filter | Apply, dismiss; Undo from the card's "changed" flag | DR-025, DXD-05 | M4 (`full`) |

**PSPEC-R005** There is no notifications overlay. The bell opens the Insight Inbox filtered to new (GDQ-08 supersedes that part of DXD-02).

**PSPEC-R006** Monitoring has no screen of its own. It is synthetic historical replay, and its output appears as insights. The replay checkpoint timeline sits in the inbox header (DX1 Inventory; DR-005).

**PSPEC-R007** Shell rules:
- The rail shows Dashboard, Workspace and Insights. Below 820 px it becomes a bottom tab bar (DXD-19).
- Below 1280 px the agent opens over the dashboard instead of narrowing it (DXD-07, DX2 Responsive).
- Moving between dashboard and workspace keeps the conversation, selections, card filters, pins and scroll position (DXD-06).
- Opening or closing any overlay keeps scroll, filters, selection and the active tab (DXD-17).

---

## 4. Product-wide rules

| ID | Rule | Basis |
|---|---|---|
| **PSPEC-R008** | One state vocabulary for cards and generated components: `loading`, `zero` (shown as 0), `empty` (no match · before the dataset starts · after the reference date), `unavailable`, `error` (with reference and Retry), `outside_access`, `partial`, `undefined_ratio` (dash and "0 of 0"). A state never shows a fabricated chart | DXD-16, DXD-45; DX2 States |
| **PSPEC-R009** | Statement labels: Observed, Derived, Hypothesis (also with a dashed outline), Recommendation, Unavailable. Colour is never the only signal | DXD-08 |
| **PSPEC-R010** | Units and numbers: currency SAR; area m²; percentages to 1 decimal; counts as integers; a missing value is "—" with a reason. Formatting comes from one module | DR-044, DXD-44 |
| **PSPEC-R011** | Every number the user sees comes from the dataset through the shared metric service. The model never types a number | DXD-30, DR-031 |
| **PSPEC-R012** | Unavailable concepts (payments, footfall, rent and others listed in the unavailable-concepts catalogue, PR-M1) produce an Unavailable card and never an estimate. A related metric is offered only as a clearly different metric, never as a proxy answer | AI-08, DXD-35; DX4 J5 |
| **PSPEC-R013** | Wording: "waiting 31+ days (1m+)" for approval age; the word "overdue" is never used for approvals; no causal verb without a supporting mechanism | C4, C5, C7; R-04 |
| **PSPEC-R014** | English-first UI with no right-to-left layout. Arabic names are stored (`name_ar`) and not displayed | DR-024 |
| **PSPEC-R015** | Access boundaries are shown, never hidden: a locked Boundaries row (role access, lease restriction, reference date) that neither the user nor the agent can remove or widen | DXD-15 |
| **PSPEC-R016** | Refusals look the same whether or not the item exists | DXD-85 |
| **PSPEC-R017** | Card filters stay per card (V2 parity); there is no global filter bar | DXD-05; DX2-Notes |

---

## 5. Card inventory

The parity table and intentional differences are those of GD tab 05 and the DX2-Notes board, frozen. Per-card specifications (metrics, filters, chart primitive, interactions, states, drilldown, parity test) are written in **Appendix A by PR-M2**. Metric IDs are fixed by the KPI catalogue in PR-M1.

### 5.1 Admin V2 cards (PRD §4.1)

| Card id | Requirement | V2 visual (implementation) | Filters | Delivery | E2E suite |
|---|---|---|---|---|---|
| `properties` | PAR-A01 | Stat tiles (malls, units, occupied, vacant, GLA) + unit occupancy meter (HTML) | None | `slice` (with all values, ROADMAP A-09) | E2E-CARD-properties |
| `kpis` | PAR-A02 | 3 stat tiles: expiring leases, active leases, pending sales submissions (HTML) | None | `full` | E2E-CARD-kpis |
| `leaseRequests` | PAR-A03 | Donut with unit-type / source switch, top 4 + Other (ECharts) | Year | `full` | E2E-CARD-leaseRequests |
| `salesFunnel` | PAR-A04 | Four-stage flow with signed/unsigned splits (HTML) | Year, month, region, mall | `full` | E2E-CARD-salesFunnel |
| `actionRequired` | PAR-A05 | List of the latest three unread items with badge and type pills (HTML) | None | `full` | E2E-CARD-actionRequired |
| `pendingApprovals` | PAR-A06 | 3 half gauges, bands 0–6 / 7–13 / 14–20 / 21–30 / 31+ days, with band counts printed (ECharts) | Region, mall | `slice` | E2E-CARD-pendingApprovals |
| `pendingAmendments` | PAR-A07 | Type × delay-week heatmap; future-dated rows in 4 wk+ (ECharts) | Year, month, region, mall | `slice` | E2E-CARD-pendingAmendments |
| `serviceRequests` | PAR-A08 | Squarified treemap (GDQ-07) + work-permit strip | Year, month, region, mall | `full` | E2E-CARD-serviceRequests |
| `fitoutHandover` | PAR-A09 | 4 rings, ring = reviewed ÷ (received + remaining + reviewed), pending-handover callout (ECharts) | Year, month, region, mall | `full` | E2E-CARD-fitoutHandover |
| `fitoutDrawings` | PAR-A10 | Horizontal stacked bars by discipline (ECharts) | Year, month, region, mall | `full` | E2E-CARD-fitoutDrawings |
| `documentStatus` | PAR-A11 | Stacked A–D columns by mall, discipline switch, chart ↔ table (ECharts) | Year, region, discipline | `full` | E2E-CARD-documentStatus |
| `unitDiscrepancy` | PAR-A12 | Diverging bars, mall-wise / month-wise (ECharts) | Year, month, mall-wise/month-wise | `slice` | E2E-CARD-unitDiscrepancy |

### 5.2 Tenant card groups (PRD §4.2)

| Card group id | Requirement | Content | Delivery | E2E suite |
|---|---|---|---|---|
| `overview` | PAR-T01, PAR-T05 | Leases, units, brands; pending documents; open and total service requests; sales pending and approved; lease requests pending and approved; profile; payments shown as **Unavailable**, never 0 | `full` | E2E-TCARD-overview |
| `actionRequired` | PAR-T02 | Lease-scoped action items, never company-wide counts for a lease audience (DXD-93). For lease T-31206: the lease's 2 items (fit-out drawings to upload) and 0 service requests (the company has 2; ROADMAP A-10) | `slice` | E2E-TCARD-actionRequired |
| `reportedSales` | PAR-T03 | Monthly columns, submitted + approved, month of period end, year and lease selects | `full` | E2E-TCARD-reportedSales |
| `serviceRequests` | PAR-T04 | Donut by status and treemap by category; same population as the open-requests tile | `full` | E2E-TCARD-serviceRequests |
| `documents` | PAR-T05 | Grouped document links, deep links for single items | `full` | E2E-TCARD-documents |
| `events` | PAR-T06 | Merged announcements and events feed, duplicates removed on the server | `full` | E2E-TCARD-events |
| `opportunities` | PAR-T07 | Leasing opportunities: mall list with available units; no mall map (DXD-13) | `full` | E2E-TCARD-opportunities |
| Prospective-tenant journey | PAR-T08 | Stretch goal | `deferred` (DR-026, OI-15) | — |

### 5.3 Acceptance criteria common to every card (detailed per card in Appendix A, PR-M2)

| ID | Criterion |
|---|---|
| **PSPEC-R018** | The card renders its V2 visual family from seeded API data, with no dashboard mocks |
| **PSPEC-R019** | The card total equals the Records total under the same filters, and a finer table reconciles with the chart (DXD-18, PAR-X03) |
| **PSPEC-R020** | Each of the eight PRD §5 caveats is visible on its card, with named exposing rows in the seed (MET-04) |
| **PSPEC-R021** | Every state in PSPEC-R008 that can occur for the card renders as specified |
| **PSPEC-R022** | Every selectable element emits `selection_ref.v1` and supports keyboard selection, with an accessible table alternative (DXD-25, GUI-06) |
| **PSPEC-R023** | Every intentional difference from V2 is visible on the card and traces to DR-001, DR-002 or DR-006 |

---

## 6. Journey index

Each journey has a test suite ID (`specs/traceability/id_conventions.yaml`). Step-level acceptance lives in the board named and in the milestone plan that delivers the journey.

### 6.1 PRD journeys and TA demonstrations

| ID | Journey | Designed in | Delivery | Tested by |
|---|---|---|---|---|
| PRD-J1 | Ask from the dashboard: "Which mall is worst?" | DX4 J1, J2 pattern | `full` (M4; the SR-treemap version is an M5 benchmark case) | DX4-J1, DX4-J2; benchmark |
| PRD-J2 | Select a heatmap cell and investigate | DX4 J1 (amendments heatmap) | `full` | DX4-J1 |
| PRD-J3 | Do delayed inspections accompany late handovers? | Specified with existing components plus a golden scenario (GDQ-09) | `full` | PRD-J3 E2E (M4) and golden case (M5) |
| PRD-J4 | Tenant: which documents are outstanding? | DX6 T-202 thread; DX4 J8 boundary | `slice` (E2E-S3), `full` | E2E-S3, DX4-J8 |
| PRD-J5 | Yesterday's footfall | DX4 J5 | `full` | DX4-J5 |
| PRD-J6 | "Show that as a table" | DX5 View as, no re-query | `full` | E2E-DX5-VIEWAS |
| TA-D1 | Backlog priority | DX4 J2 | `full` | DX4-J2 |
| TA-D2 | Where are opportunities dropping? | DX5 funnel result and caveat | `full` | E2E-DX5-CAT |
| TA-D3 | Are inspections delaying handover? | GDQ-09 | `full` | As PRD-J3 |
| TA-D4 | Select a cell, ask "why this?" | DX4 J1 | `full` | DX4-J1 |
| TA-D5 | Underlying records, switch to table, cursor pagination | DX5 records and paging | `full` | E2E-DX5-VIEWAS |
| TA-D6 | Unknown data | DX4 J5 | `full` | DX4-J5 |
| TA-D7 | Tenant A cannot reach tenant B | DX4 J8, J10; DX6 K7, K11 | `slice` (E2E-S3), `full` | DX4-J8, DX4-J10, DX6-K7, DX6-K11 |

### 6.2 Design journeys

| ID | Journey (board) | Delivery |
|---|---|---|
| DX4-J1 | Ask from a chart selection (DX4-Workspace) | `slice` (via E2E-S1), `full` |
| DX4-J2 | Multi-step investigation | `full` |
| DX4-J3 | Confirmed dashboard filter change | `full` |
| DX4-J4 | Partial information | `full` |
| DX4-J5 | Unavailable data | `slice` (payments in E2E-S3), `full` |
| DX4-J6 | Budget limit, failure and versioned retry | `full` |
| DX4-J7 | History and resume | `full` |
| DX4-J8 | Tenant access boundary | `slice` (E2E-S3), `full` |
| DX4-J9 | Interruption, reconnection and Stop | `full` |
| DX4-J10 | Context isolation checks | `full` |
| E2E-DX5-CAT | Component catalogue, all 15 kinds plus variants (DX5-GenUI) | `slice` (5 kinds), `full` |
| E2E-DX5-VAL | Validator outcomes and table fallback | `slice`, `full` |
| E2E-DX5-CONT | Continuity across View as, moves, expand, resume | `full` |
| E2E-DX5-VIEWAS | View as without re-query | `full` |
| DX6-K1 | Scheduled evaluation (DX6-Inbox) | `full` (slice: manual replay only) |
| DX6-K2 | Event-triggered evaluation | `full` |
| DX6-K3 | Triage the inbox | `slice` (list, detail, acknowledge), `full` |
| DX6-K4 | Investigate privately | `full` |
| DX6-K5 | Dismiss, feedback and suppression | `full` |
| DX6-K6 | Dashboard notifications | `full` |
| DX6-K7 | Role visibility and tenant isolation | `slice` (T-202 lease scope), `full` |
| DX6-K8 | When the agent stays quiet | `full` |
| DX6-K9 | Insight lifecycle and versions | `full` |
| DX6-K10 | Private investigation and shared summary | `full` (shared summaries deferred from five days, DXD-84) |
| DX6-K11 | Stale evidence and a grant change | `full` |
| DX6-K12 | Duplicates, re-runs and recovery | `full` |

### 6.3 Slice demonstration journeys (ESP tab 2)

| ID | Persona | Expected result | Delivery |
|---|---|---|---|
| E2E-S1 | Central manager | Card shows Central 130 pending and 62 waiting 31+. The answer gives 41 waiting 31+, 66.1% of Central's 62, rendered as `kpi` + `bar`. Evidence shows the `get_metric` calls and the `derive` calculation. Inherited filters are Central and Rawdah Point Mall. "Overdue" does not appear | `slice` |
| E2E-S2 | Central manager | After the slice replay to 20 Oct, INS-101 (D2) is listed with its weekly series and threshold facts. Acknowledge is stored once, even if repeated | `slice` |
| E2E-S3 | Tenant on T-31206 | Action required shows 2 items. T-202 (D8, P2) is visible to this lease only. Answers are lease-scoped. A cross-tenant question gets the uniform refusal. Payments return `unavailable` | `slice` |

Expected values for these journeys live only in `tests/fixtures/golden/` (PR-M1).

### 6.4 Platform journeys (no design ID)

| ID | Journey | Milestone |
|---|---|---|
| E2E-SHELL-01 | Signed-out visit redirects to `/sign-in`; banner and as-of date visible | M0 |
| E2E-SHELL-02 | Sign in as each fixture principal; land on the persona's dashboard route; rail shows Dashboard, Workspace, Insights | M0 |
| E2E-SHELL-03 | Sign out clears client state and returns to `/sign-in` | M0 |
| E2E-NAV-01 | Every route in ARCHITECTURE §6.2 renders (placeholders in M0) and keeps the shell | M0 |
| E2E-RESP-01…03 | Shell at 1440 × 900, 1024 × 768 and 390 × 844: rail ↔ bottom tab bar; banner visible | M0 |

---

## 7. Out of scope, deferred and limits

**Out of scope (PRD §2):**
- production data or writes;
- Yardi, SAP and Appian integrations;
- actual tenant financial payments;
- autonomous approvals or operational changes;
- causal-inference guarantees;
- model-written SQL, HTML or JS;
- mobile-native apps;
- production-scale multi-tenancy and SLOs;
- the mall map (DXD-13);
- email, SMS and push notifications (DR-011, DXD-77).

**Deferred within scope:** the prospective-tenant journey (DR-026, PAR-T08).

**Deferred from the five days but in full scope:**
- DXD-84 shared summaries;
- per DXD-92: D3, D4, full D7, snooze, digest and feedback analytics.

**Known limit:** business-impact answers are limited because there is no revenue or rent metric. This is recorded as an unavailable-concept entry (OI-08, L4-BIZ).

---

## 8. Glossary

| Term | Meaning |
|---|---|
| `as_of` | The frozen reference date of a dataset, 2026-10-20 for `sd-2026.10.20-01`. Nothing is computed beyond it |
| Dataset | One generated data version: ID, `as_of`, seed hash |
| Parity metric | Reproduces a V2 business definition (DR-001) |
| Corrected metric | A separately named metric that fixes a V2 quirk that changes a number |
| Derived metric | Computed deterministically from other metrics by `derive`; carries a calculation record |
| New metric | A metric V2 does not have (as-of history, lineage metrics); kind `new` (DR-023, DXD-80) |
| Coverage | A field of every result: `supported`, `derived`, `partial`, `related_only`, `unavailable`, `error` |
| Fact token | A placeholder in model-written text that the server fills from a verified fact (DR-031) |
| Evidence envelope | Class, metric IDs and versions, filters, scope, freshness, dataset version and coverage attached to every statement and visual (DXD-36) |
| `selection_ref.v1` | The payload a selectable chart element emits (DXD-25, 26) |
| `resultRef` | Reference to a validated analytical result that components render from (DXD-41) |
| Thread | One investigation: selections, pins, scope and runs |
| Run | One agent execution (`threadId`, `runId`, `requestId`, `seq`) |
| Evaluation run | One detector evaluation, identified by `run_key` (DXD-86). Distinct from an agent run |
| Insight / instance | A published detector finding, and its audience-scoped instance (DXD-65, 76) |
| Watch, P1, P2, P3 | Insight priority bands (DXD-66, 90, 91) |
| Scope, grant, AccessScope | What a principal may see; enforced server-side on every read (ARCHITECTURE §9) |
| Uniform refusal | The same response for unauthorized and non-existent (DXD-85) |
| Slice / full scope | The five-day delivery cut / the complete approved POC (GDQ-01) |

---

## 9. Open questions (non-blocking)

| ID | Question | Default until decided | Decide in | Owner |
|---|---|---|---|---|
| OQ-PSPEC-01 | Does the tenant persona see the bell? DX1 IA showed no bell for tenants; DXD-79 later gave tenants an own-lease inbox | The tenant reaches the inbox from the rail; bell visibility for tenants is fixed in PR-M6 | PR-M6 | Architect, owner approval if it changes a design |

---

## 10. Acceptance mapping

| Requirements | Verified by |
|---|---|
| PSPEC-R002, R004 (persona routing), R007 (shell parts) | M0-T04, M0-T06: E2E-SHELL-01…03, E2E-NAV-01, E2E-RESP-01…03 |
| PSPEC-R008–R023 | The card and journey suites above, in their delivering milestones (M2, M4, M6) |
| PSPEC-R001, R003 | `make specs-check` (delivery class on every task card) and gate reviews |
