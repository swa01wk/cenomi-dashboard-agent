# DECISION_REGISTER — approved design and engineering decisions

| | |
|---|---|
| Document code | DREG (requirement IDs `DREG-Rnnn`) |
| Version | 1.0 · 2026-10-22 · PR-M0 |
| Source | Frozen GD export `docs/reference/final-design-gate/03_DECISION_REGISTER.md` (141 decisions) plus the gate decisions of 22 Oct 2026 and the engineering decisions approved on 22 Oct 2026 |
| Generated | The §2 table was rendered from the frozen export with exactly the status changes listed in §1 (one-time render, checked in this PR). M0-T10 adds the renderer `scripts/docs/render_register.py` and a drift check; from then on a row changes only through an ADR or CR followed by a re-render |

**DREG-R001** This register is the single living list of DR and DXD decisions. Specifications cite decisions by ID and never restate their rules. The frozen export stays unchanged as the record of the gate.

**DREG-R002** A decision changes status only through: a gate decision (GDQ), an approved engineering decision recorded in an ADR, or an approved change request (CR) in `plans/STATUS.md`. The row's Note names which.

## 1. Status after the gate and after 22 Oct 2026 approvals

The export's per-row status column shows the **pre-gate** statuses. Its closing section records that GDQ-01…12 (all Option A) settled 22 of the 23 “Decision required” rows (consistency finding F-1). This register applies those settlements to each row, and also records DR-035 as superseded by ADR-0001 (ED-01 A, approved 22 Oct 2026).

| Status | Pre-gate (export column) | Now |
|---|---|---|
| Approved · ready | 104 | 125 |
| Verification pending | 7 | 7 |
| Decision required | 23 | 1 |
| Deferred from five days | 2 | 2 |
| Superseded | 5 | 6 |
| **Total** | **141** | **141** |

Rows whose status changed:

- GDQ-10 batch (17): DR-004, DR-008, DR-018b, DR-021, DR-023, DR-024, DR-027, DR-028, DR-029, DR-030, DR-037, DR-042, DR-043, DR-044, DR-046, DR-047, DXD-22.
- GDQ-05: DR-012, DXD-72. GDQ-12: DR-015. GDQ-11: DR-038. GDQ-03: DXD-80.
- ADR-0001 (ED-01 A): DR-035 → Superseded.
- Still open: **DR-036** (evaluation scoring), proposed resolution ED-11 A, needed before PR-M5.
- Verification pending (7): DR-007, DR-017, DXD-21, DXD-24, DXD-39, DXD-40, DXD-61 — cited individually by the M2 and M4 gates (consistency finding F-2).

## 2. Register

| ID | Decision | Rule | Origin | Status (pre-gate) | Status (now) | Note |
| --- | --- | --- | --- | --- | --- | --- |
| DR-001 | Parity policy | Reproduce business definitions and visual forms; never security defects; fix nondeterminism; quirks that change a number → parity metric + named corrected metric. | G0 | Approved · ready | Approved · ready |  |
| DR-002 | Parity classification of REF findings | §3.4 rulings; soft-deleted fit-out rows only in parity cards, never in insights or recommendations. | G0 | Approved · ready | Approved · ready | Per-metric confirmation in M0 KPI batches. |
| DR-003 | Frozen as\_of per data version | One as\_of used by seed, SQL, APIs, agent, insights and fixtures; NOW() banned in metric SQL. | G0 | Approved · ready | Approved · ready |  |
| DR-004 | as\_of value and data window | as\_of 2026-10-20; transactional events 2024-01-01 → as\_of. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. All designs already use these values. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-005 | Monitoring is synthetic historical replay | Detectors replayed at checkpoints ≤ as\_of; never live monitoring. | G0 | Approved · ready | Approved · ready | Calendar fixed by DXD-75 (weekly, monthly on the 20th, events). |
| DR-006 | Time zones | Store UTC; bucket every calendar filter and age band in Asia/Riyadh. | G0 | Approved · ready | Approved · ready |  |
| DR-007 | Apache ECharts for dashboard and GenUI charts | Conditional on faithful V2 reproduction, treemap fidelity and chart accessibility. | G0 (conditional) | Verification pending | Verification pending | Real-runtime validation still outstanding (DXD-21, DXD-61); fallback DXD-23. GDQ-06 A: real ECharts 5.6.0 verification is a mandatory engineering gate (M0-T08 harness; pass or fallback by M2 exit). |
| DR-008 | Non-chart visuals as HTML | Stage flow approved; stat tiles, occupancy meter, permit strip, captions proposed. | G0 · partly proposed | Decision required | Approved · ready | Batch approval: freeze the remaining HTML visuals at GD (built and verified in DX2/DX3). GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-009 | Level 5 in scope after the core agent | Insight discovery, monitoring, notifications, lifecycle and feedback. | G0 | Approved · ready | Approved · ready |  |
| DR-010 | Sequencing M3c → M6 after M5 | Core agent evaluated without Level 5; proactive work after. | G0 | Approved · ready | Approved · ready | The five-day plan reorders delivery; the dependency stays. |
| DR-011 | In-app notifications only | Inbox, badge, per-user list; no email, SMS or push. | G0 | Approved · ready | Approved · ready | Confirmed by DXD-77. |
| DR-012 | Meaning of feedback | Stored; drives deterministic re-ranking, suppression and evaluation reports. | G0 | Decision required | Approved · ready | Conflicts with DXD-72 (logged for review only). GDQ-05. Reconciled by GDQ-05 A (22 Oct 2026): deterministic per-user ordering within a priority band after repeated “not useful”; never hides a P1; never changes thresholds. |
| DR-013 | Read-only business data | Application state in separate schemas written by a separate DB role. | G0 | Approved · ready | Approved · ready |  |
| DR-014 | Provider-agnostic LLM adapter | Model is configuration; structured output and tool calling required. | G0 | Approved · ready | Approved · ready |  |
| DR-015 | Model roles and selection | planner / synthesizer / fast keys; benchmark two candidates. | G0 · open | Decision required | Approved · ready | Provider and API key needed before agent work starts (GDQ-12). GDQ-12 A (22 Oct 2026): provider adapter with one primary and one fallback model. Model names and credentials are configuration, still to be supplied before agent integration. |
| DR-016 | Plain @ag-ui/client | Own React hooks and the GenUI registry; no CopilotKit. | G0 | Approved · ready | Approved · ready |  |
| DR-017 | AG-UI event mapping | CUSTOM cenomi.presentation.v1, ACTIVITY\_\* plan, sanitized TOOL\_CALL\_*, STATE\_* context; no reasoning events. | G0 · proposed | Verification pending | Verification pending | Design contract DXD-40; SDK assumptions checked against the pinned version (GDQ-11). SDK assumptions checked by the M0 spike (M0-T09) and at M4 exit; ED-10 (AG-UI pin) still proposed. |
| DR-018 | Synthetic sales\_funnel\_snapshot | Live card counts; snapshot divergence explained. | G0 | Approved · ready | Approved · ready |  |
| DR-018b | No approvals filter-list snapshot table | Filter options from live data. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-019 | Simplified, backend-enforced roles and permissions | Final role list in M0. | G0 | Approved · ready | Approved · ready | Design fixture roles: portfolio admin, Central manager, tenant (one lease, company). |
| DR-020 | Scope semantics | Explicit scope kinds; empty scope = empty result; card and endpoint share a permission; client can only narrow; refs bound to principal, scope, data version. | G0 · accepted | Approved · ready | Approved · ready | Extended by DXD-38, 56, 85. |
| DR-021 | Row-level security not in baseline | Mandatory scope fragment + lint + read-only role. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-022 | Explicit lineage | enquiry → proposal → lease; unit → inspection → drawing → handover via fitout\_projects. | G0 | Approved · ready | Approved · ready | No designed journey uses it yet (PRD journey 3); GDQ-09. GDQ-09 A: the fit-out cohort journey is specified with existing components and a golden scenario. |
| DR-023 | Lineage metrics labelled new | Cohort conversion, inspection → handover lag. | G0 · accepted (M0) | Decision required | Approved · ready | Batch approval with the KPI catalog. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-024 | English-first UI | Arabic names stored for fidelity (proposed); no RTL. | G0 · partly proposed | Decision required | Approved · ready | English-first approved at G0; Arabic storage in the batch. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-025 | Agent proposes dashboard filter changes; user confirms | Frontend tool propose\_dashboard\_filters. | G0 | Approved · ready | Approved · ready | Designed in DX4 J3. |
| DR-026 | Prospective-tenant journey | Stretch goal. | G0 · proposed (M5) | Deferred from five days | Deferred from five days |  |
| DR-027 | Tech stack | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy Core, psycopg 3, Alembic, uv; Node 22, pnpm, Next.js, TS, TanStack Query, zod; PostgreSQL 16; pytest, Vitest, Playwright; OpenTelemetry. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval; versions pinned in M0. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-028 | Pydantic → JSON Schema → TS + zod | CI drift check. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-029 | Conversation and run state in PostgreSQL schema agent | No Redis. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. Insight tables in schema insights (DX6). GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-030 | Metric registry as YAML; SQL templates as files | Startup validation and scope lint. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-031 | Narrative numbers only from fact tokens | Verifier rejects other numbers; one retry; deterministic template. | G0 · accepted | Approved · ready | Approved · ready | Designed DX4/DX5 (DXD-41, 55) and DX6 (DXD-63). |
| DR-032 | Lifecycle with bounded re-plan | plan → validate → DAG → ≤ 1 re-plan → facts → synthesis → verify → compose. | G0 · accepted | Approved · ready | Approved · ready | Designed DX4 (J6 budget, J9 interruption). |
| DR-033 | Two-tier fixtures | Micro hand-verified fixtures; process-based macro seed with property assertions. | G0 · accepted | Approved · ready | Approved · ready | DX6 adds golden cohorts and invariants (DXD-81). |
| DR-034 | Repository naming | Project-instruction docs/ and plans/ names; TA §11 code layout. | G0 | Approved · ready | Approved · ready | Docs part superseded by ADR-0002 (approved ESP structure); the rest stands. |
| DR-035 | Planning documents committed manually | Option A. | G0 | Approved · ready | Superseded | Superseded by ADR-0001 (ED-01 Option A, approved 22 Oct 2026): specifications are delivered by milestone pull requests. |
| DR-036 | Evaluation scoring | Deterministic checks; LLM judge for explanation quality; ≥ 20% human spot-check. | G0 · proposed (M5) | Decision required | Decision required | Needed before the evaluation spec. Only open register decision. Proposed resolution ED-11 Option A; needed before PR-M5. |
| DR-037 | Local Docker Compose | No cloud deployment. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-038 | Optional technical spike | Throwaway AG-UI round trip and model latency. | G0 · open | Decision required | Approved · ready | Recommended now (GDQ-11). GDQ-11 A (22 Oct 2026): AG-UI verification spike in M0 (M0-T09). |
| DR-039 | Design references | Design from the API Reference. | G0 · resolved | Approved · ready | Approved · ready |  |
| DR-040 | Brand treatment | Cenomi-inspired, fictional data, synthetic indicator, no brand assets. | G0 | Approved · ready | Approved · ready |  |
| DR-041 | Design before specifications | Gate GD before M0 specifications. | G0 | Approved · ready | Approved · ready | This gate. |
| DR-042 | New and corrected metrics only via the KPI catalog | No silent scope expansion. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. Adds three as-of metrics (DXD-80). GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-043 | Scale and geography | 3 regions, 25 fictional malls, PRD §8 targets. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval; used by every design. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-044 | Units and numeric policy | SAR, m², 1-decimal %, integers, — with a reason. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval; implemented by DXD-44. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-045 | Detector set and priority formula | Robust z, peer outlier, trend break, co-movement; impact × severity × confidence. | G0 · proposed | Superseded | Superseded | Superseded by DXD-63, 64, 66, 89, 90. |
| DR-046 | Normalized fitout\_drawing\_documents | Not parsed from JSON. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DR-047 | Simplified location hierarchy | region → mall → property → unit; explicit property\_groups. | G0 · proposed (M0) | Decision required | Approved · ready | Batch approval. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DXD-01 | Visual direction | Ink and Violet is the primary design system; Night Operations optional later; Warm Editorial not pursued. | DX1 | Approved · ready | Approved · ready |  |
| DXD-02 | Screen architecture | Four screens plus the docked agent panel and four overlays: card focus, inspector, notifications, filter-change confirmation. | DX1 | Approved · ready | Approved · ready | GDQ-08 proposes the bell opens the inbox instead of a notifications overlay. GDQ-08 A (22 Oct 2026): the notifications overlay is removed; the bell opens the Insight Inbox filtered to new. |
| DXD-03 | Agent UX | Docked panel for quick questions; expandable workspace for investigations; entry points on every card and data point. | DX1 | Approved · ready | Approved · ready |  |
| DXD-04 | Shared inspector | Evidence, Definition, Records and Execution tabs for metrics, generated components and insights alike. | DX1 | Approved · ready | Approved · ready | Insight detail must reuse the inspector’s evidence components. |
| DXD-05 | Three kinds of context | Card filters, the agent’s query scope, and proposed filter changes that apply only after confirmation, shown separately. | DX1 | Approved · ready | Approved · ready |  |
| DXD-06 | State preservation | Dashboard ↔ workspace keeps conversation, selections, card filters, pins and scroll. | DX1 | Approved · ready | Approved · ready |  |
| DXD-07 | Responsive behaviour | Desktop, tablet, mobile; below desktop the agent is an overlay or full screen. | DX1 | Approved · ready | Approved · ready |  |
| DXD-08 | Statement labels | Observed, Derived, Hypothesis, Recommendation, Unavailable as text; colour never the only signal. | DX1 | Approved · ready | Approved · ready |  |
| DXD-09 | Synthetic data | Reference date and synthetic designation on every screen and card footer. | DX1 | Approved · ready | Approved · ready |  |
| DXD-10 | Expanded cards | Centred overlay plus Open in workspace with filters, selection and tab intact. | DX2 | Approved · ready | Approved · ready |  |
| DXD-11 | Records vs Inspector | Drilldowns in the card’s Records tab; inspector for evidence, definitions, provenance, execution; shared table components. | DX2 | Approved · ready | Approved · ready |  |
| DXD-12 | Selection model | One active selection globally; per-card memory; explicit pinning. | DX2 | Superseded | Superseded | Superseded for analytical context by DXD-29 → DXD-32; per-card memory kept. |
| DXD-13 | Mall map | Out of the baseline; mall cards and available units kept. | DX2 | Approved · ready | Approved · ready |  |
| DXD-14 | Partial coverage everywhere | Same Partial label and a sentence naming what is missing; coverage is a result field. | DX2 | Approved · ready | Approved · ready |  |
| DXD-15 | Filters vs boundaries | Removable filter chips; locked Boundaries row for access and reference date. | DX2 | Approved · ready | Approved · ready |  |
| DXD-16 | One state vocabulary | loading, zero, empty, unavailable, error, outside\_access, partial, undefined\_ratio for cards and components. | DX2 | Approved · ready | Approved · ready |  |
| DXD-17 | Context and scroll preservation | Overlays keep scroll, filters, selection and tab. | DX2 | Approved · ready | Approved · ready |  |
| DXD-18 | Chart and table share one dataset | Same authorized result; finer table rows must reconcile with chart totals. | DX2 | Approved · ready | Approved · ready |  |
| DXD-19 | Phone navigation | Below 820 px the rail becomes a bottom tab bar. | DX2 | Approved · ready | Approved · ready |  |
| DXD-20 | Value labels on narrow charts | Value on the selected mark and tooltip; Table lists all. | DX2 | Approved · ready | Approved · ready |  |
| DXD-21 | How DR-007 is verified | Gallery self-test with real ECharts, or a local version-pinned asset; test doubles never count. | DX3 | Verification pending | Verification pending | ECharts could not be loaded from this workspace (egress refused); GDQ-06. GDQ-06 A: mandatory engineering gate; harness M0-T08. |
| DXD-22 | minShare 0.08 | Option A provisionally: every tile stays with its drilldown; the threshold only hides labels. | DX3 | Decision required | Approved · ready | No ui-kit source available; batch approval makes it final. GDQ-10 A (22 Oct 2026); final definition in §4. |
| DXD-23 | Treemap fallback | Custom squarified component if ECharts misses the thresholds. | DX3 | Approved · ready | Approved · ready | GDQ-07 A: the custom squarified treemap is preferred, subject to the real-library findings. |
| DXD-24 | V2 palette with verified accessibility | Keep V2 hues with labels, focus, text alternatives and non-colour selection; WCAG verified, not assumed. | DX3 | Verification pending | Verification pending | axe-core and screen reader on the real build. |
| DXD-25 | One selection contract | Every selectable element emits selection\_ref.v1. | DX3 | Approved · ready | Approved · ready |  |
| DXD-26 | What a selection carries | Metric id, version and kind, grain, dimensions, value, unit, filters, scope, dataset reference. | DX3 | Approved · ready | Approved · ready |  |
| DXD-27 | Chart ↔ table keeps the definition | Same result reference; finer rows must reconcile. | DX3 | Approved · ready | Approved · ready |  |
| DXD-28 | Same semantics everywhere | Same states, actions and payload on every surface. | DX3 | Approved · ready | Approved · ready |  |
| DXD-29 | Active, kept and pinned | One active selection globally; kept selections never sent automatically. | DX3 | Superseded | Superseded | Superseded by DXD-32. |
| DXD-30 | Grounded numbers | Every displayed number comes from the dataset; the model never types a number. | DX3 | Approved · ready | Approved · ready |  |
| DXD-31 | Composite rankings only on request | Multi-KPI comparison with leaders by default; a combined score only when asked. | DX4 | Approved · ready | Approved · ready |  |
| DXD-32 | Analytical selections are thread-local | Each investigation has its own selections; imports are explicit. | DX4 | Approved · ready | Approved · ready |  |
| DXD-33 | History is immutable | Stored answers never change; re-run creates a new run. | DX4 | Approved · ready | Approved · ready |  |
| DXD-34 | KPI reconciliation (finding) | Rawdah 41 (all types, 1m+) and 32 (proposals, all ages) are different populations; both reconcile. | DX4 | Approved · ready | Approved · ready | Extended by the DX6 reconciliation (DXD-80). |
| DXD-35 | Coverage semantics | Observed subset labelled with coverage; full total Unavailable, never estimated. | DX4 | Approved · ready | Approved · ready |  |
| DXD-36 | Evidence envelope on every statement and visual | Class, metric ids and versions, filters, scope, freshness, dataset version, coverage. | DX4 | Approved · ready | Approved · ready |  |
| DXD-37 | Versioned recovery | A successful retry creates v2; v1 kept unchanged. | DX4 | Approved · ready | Approved · ready |  |
| DXD-38 | Context isolation rules | Threads, roles, chips and resume never widen authorization; re-checked. | DX4 | Approved · ready | Approved · ready |  |
| DXD-39 | Accessibility of evidence, activity and selection | Text states, aria-pressed, focus-managed inspector, one polite live region. | DX4 | Verification pending | Verification pending | axe-core and screen reader on the real build. |
| DXD-40 | AG-UI handoff contracts | Event-to-state mapping, run identity, cancellation, reconnection, retries, idempotency. | DX4 | Verification pending | Verification pending | SDK assumptions checked against the pinned version (GDQ-11). SDK assumptions checked by the M0 spike (M0-T09) and at M4 exit. |
| DXD-41 | The result is authoritative | Components render only from the validated resultRef; text uses fact tokens. | DX5 | Approved · ready | Approved · ready |  |
| DXD-42 | Closed component registry | Fifteen kinds; no model-generated code. | DX5 | Approved · ready | Approved · ready | Mapping to the PRD §7 list: GDQ-02. GDQ-02 A: PRD §7 catalogue parity through the registry plus donut and stacked variants of bar and a progress variant of kpi. |
| DXD-43 | Representation alternates | View as without re-query. | DX5 | Approved · ready | Approved · ready |  |
| DXD-44 | One formatting module | Counts, rates, SAR, missing, zero, undefined formatted once. | DX5 | Approved · ready | Approved · ready |  |
| DXD-45 | State vocabulary | Never conflated. | DX5 | Approved · ready | Approved · ready |  |
| DXD-46 | Size classes | Workspace 760, panel 420, canvas 360, phone 358, expanded 1000. | DX5 | Approved · ready | Approved · ready |  |
| DXD-47 | Validation and fallback | Server validation plus client re-validation. | DX5 | Approved · ready | Approved · ready | Amended by DXD-57. |
| DXD-48 | Envelope per component | A disagreeing payload envelope is rejected. | DX5 | Approved · ready | Approved · ready |  |
| DXD-49 | Drilldown and selection | Accessible marks; selection\_ref.v1; records from the same population. | DX5 | Approved · ready | Approved · ready |  |
| DXD-50 | Fixtures are labelled | Production never renders fixtures. | DX5 | Approved · ready | Approved · ready |  |
| DXD-51 | Bounded representation policy | Intent, shape, dimensions, accessibility, space (P1–P6); user switches with View as. | DX5 | Approved · ready | Approved · ready |  |
| DXD-52 | Deterministic table fallback | From the verified, authorized result. | DX5 | Approved · ready | Approved · ready |  |
| DXD-53 | Treemap below 400 px | Ranked list, same keys and selection. | DX5 | Approved · ready | Approved · ready |  |
| DXD-54 | Component budget | 3 in the panel, 6 in the workspace. | DX5 | Approved · ready | Approved · ready |  |
| DXD-55 | Verified calculations | Calc records recomputed by the verifier; neither LLM nor renderer derives KPI values. | DX5 | Approved · ready | Approved · ready |  |
| DXD-56 | Authorization by grants | Current grants vs scope, dimensions, records; withhold, never filter; never name out-of-grant entities. | DX5 | Approved · ready | Approved · ready |  |
| DXD-57 | Failure taxonomy | Presentation, calculation, authorization, unknown result, stale, partial are distinct. | DX5 | Approved · ready | Approved · ready |  |
| DXD-58 | Fallback preserves boundaries | Rows, paging, evidence, coverage, formatting, authorization. | DX5 | Approved · ready | Approved · ready |  |
| DXD-59 | Subset disclosure | Declared and disclosed; the renderer never aggregates. | DX5 | Approved · ready | Approved · ready |  |
| DXD-60 | Continuity | Envelope and selection kept across View as, moves, expand, resume. | DX5 | Approved · ready | Approved · ready |  |
| DXD-61 | ECharts at the Design Gate | GenUI charts validated on ECharts 5.6.0. | DX5 | Verification pending | Verification pending | Same pending verification as DXD-21. GDQ-06 A: mandatory engineering gate; GenUI charts re-verified at M4 exit. |
| DXD-62 | Implementation priority | Ten core kinds first; specialized kinds use the table fallback until built. | DX5 | Approved · ready | Approved · ready |  |
| DXD-63 | Detection is deterministic | Rules in the analytics layer; templated text with fact tokens. | DX6 | Approved · ready | Approved · ready |  |
| DXD-64 | Detector catalogue | D1–D8 as detectors-1.1. | DX6 | Approved · ready | Approved · ready | Refined by DXD-89. |
| DXD-65 | Audience-scoped instances, three checks | Generation, delivery, every read, against current grants. | DX6 | Approved · ready | Approved · ready |  |
| DXD-66 | Transparent scoring | impact × urgency; P1 ≥ 6, P2 3–5, P3 ≤ 2; Low → Watch; positive → P3. | DX6 | Approved · ready | Approved · ready | Rules in DXD-90. |
| DXD-67 | Shared lifecycle, personal triage | Shared and per-user states. | DX6 | Approved · ready | Approved · ready | Thread content private (DXD-83). |
| DXD-68 | Deduplicate, merge, re-notify, suppress | Band rise or ≥ 10% worse than the last notified version. | DX6 | Approved · ready | Approved · ready |  |
| DXD-69 | Quiet by default | Logged decisions with reasons. | DX6 | Approved · ready | Approved · ready |  |
| DXD-70 | Delivery | P1 in app; P2/P3 digest; Watch inbox only. | DX6 | Approved · ready | Approved · ready | Digest scheduling deferrable (DXD-92). |
| DXD-71 | Investigation handoff | Insight imported and labelled into a private thread. | DX6 | Approved · ready | Approved · ready |  |
| DXD-72 | Feedback | Logged for review; no automatic threshold change; per-user mute. | DX6 | Decision required | Approved · ready | Reconcile with DR-012 (GDQ-05). As amended by GDQ-05 A (22 Oct 2026); see DR-012. |
| DXD-73 | Scenario history | Declared history extension. | DX6 | Superseded | Superseded | Amended by DXD-81. |
| DXD-74 | Five-day priority (DX6) | Original core list. | DX6 | Superseded | Superseded | Amended by DXD-92. |
| DXD-75 | Evaluation cadence (DXQ-12 A) | Weekly, monthly on the as-of day, calendar months, events; all replay. | DX6 | Approved · ready | Approved · ready |  |
| DXD-76 | Instances per authorized scope (DXQ-13 A) | Regional instances within each authorized region; operator and tenant never share. | DX6 | Approved · ready | Approved · ready |  |
| DXD-77 | In-app digest only (DXQ-14 A) | No email in the POC. | DX6 | Approved · ready | Approved · ready |  |
| DXD-78 | Positive findings (DXQ-15 A) | P3 Opportunity insights. | DX6 | Approved · ready | Approved · ready |  |
| DXD-79 | Tenant proactive insights (DXQ-16 A) | Own-lease Watch and Action needed. | DX6 | Approved · ready | Approved · ready | No tenant Watch in the current data after the S6 correction (GDQ-04). Supersedes the DX1 inventory statement that only admins have an inbox. |
| DXD-80 | Canonical approval-age metric and as-of history | Parity live card; three new as-of metrics equal to parity at as\_of; “waiting 31+ days”; no “overdue”. | DX6 | Decision required | Approved · ready | New metrics need KPI-catalog approval (DR-042); route GDQ-03. GDQ-03 A (22 Oct 2026): materialized as-of snapshots; enters the KPI catalogue under DR-042. Snapshot schema `snap` (D-01, ADR-0006). |
| DXD-81 | Reconstructible scenario history | Series reproduced from record lifecycles; invariants GI-01…16. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-82 | Replay oracle | Insights, versions, notifications and candidates only from replay. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-83 | Private investigation threads | Owner only, re-authorized each read; others see status and role only. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-84 | Explicit shared summaries | Owner-selected verified statements inside the instance scope. | DX6 | Deferred from five days | Deferred from five days | Designed and tested; secondary. |
| DXD-85 | Uniform refusals | Same response for unauthorized and non-existent. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-86 | Run identity and triggers | run\_key over trigger, checkpoint, dataset, configuration, partition; event dedupe; one worker. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-87 | Atomic publication and idempotent delivery | Staging; one transaction; optimistic version check; outbox keys. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-88 | Restart, late and corrected data | Restart discards staging; ingested\_at; corrections = new dataset version; stale label. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-89 | Detector quality rules (detectors-1.1) | Versioned thresholds, minimum history, missing data, coverage, denominators, consecutive periods, no cross-entity associations. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-90 | Scoring rules | Impact and urgency rules explicit. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-91 | Watch promotion and clearing | Two periods → Medium Risk; else clears. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |
| DXD-92 | Five-day priority for proactive work | Core incl. D8 and E2E tests; D3, D4, full D7, snooze, digest, feedback analytics secondary. | DX6 | Approved · ready | Approved · ready | Overall five-day scope is GDQ-01. |
| DXD-93 | Lease-scoped tenant actions | Never company-wide counts for a lease audience. | DX6 | Approved · ready | Approved · ready | Refinement record; confirm at GD. |

## 3. Gate decisions recorded (22 Oct 2026)

Copied unchanged from the frozen export.


GDQ-01 to GDQ-12 were decided as Option A. That settles 22 of the 23 decisions above that were marked “Decision required”. Only DR-036, evaluation scoring, is still open. The register now reads 126 approved and ready, 7 approved with verification pending, 1 needing a decision, 2 deferred from five days and 5 superseded.

| Gate decision | Settles | Recorded definition |
| --- | --- | --- |
| GDQ-01 A | Five-day scope | An integrated end-to-end vertical slice in five working days. The complete DX1–DX6 scope is kept for the later milestones |
| GDQ-02 A | GUI-01, GUI-02 | PRD §7 catalogue parity through the DX5 registry plus approved variants: donut and stacked variants of bar, and a progress variant of kpi (DX5 registry kind names) |
| GDQ-03 A | DXD-80 route | Materialized as-of snapshots generated from seeded lifecycle records, reconciled deterministically against the canonical KPI definitions and the reference snapshot |
| GDQ-04 A | S6/S7, tenant Watch | Corrected S6/S7 accepted; the tenant Watch path is tested with a labelled micro-fixture |
| GDQ-05 A | DR-012, DXD-72 | Deterministic per-user ordering within a priority band after repeated “not useful”; never hides a P1; never changes detector thresholds |
| GDQ-06 A | DR-007, DXD-21, DXD-61 | Real ECharts verification stays a mandatory engineering gate (status stays Verification pending until it runs) |
| GDQ-07 A | Treemaps | The custom squarified treemap is preferred, subject to the real-library findings |
| GDQ-08 A | DXD-02 overlay | The bell opens the Insight Inbox filtered to new notifications; there is no separate overlay |
| GDQ-09 A | MET-07, DR-022 | The fit-out inspection-to-handover investigation is specified with existing components and a golden evaluation scenario |
| GDQ-10 A | 17 defaults | Approved as one batch with the final definitions in the next table |
| GDQ-11 A | DR-038 | A short AG-UI protocol verification spike in M0 |
| GDQ-12 A | DR-015 | A configurable provider adapter with one primary and one fallback model. Exact model names and credentials are configuration decisions, finalized before agent integration |

## 4. Final definitions of the 17 batch-approved defaults (GDQ-10)

Copied unchanged from the frozen export.


| ID | Final definition | Specification home |
| --- | --- | --- |
| DR-004 | Dataset as\_of = 2026-10-20 (Asia/Riyadh). Transactional events run from 2024-01-01 to as\_of. Every “now”-relative calculation takes the dataset’s as\_of as a bound parameter; metric SQL never calls NOW() | KPI\_CATALOG, SYNTHETIC\_DATA\_STRATEGY |
| DR-008 | Stage flow, stat tiles, occupancy meter, permit strip and chart captions are HTML/CSS components, not ECharts | DESIGN\_SYSTEM, GENERATIVE\_UI |
| DR-018b | No approvals filter-list snapshot table; filter options come from live data under the caller’s scope | KPI\_CATALOG, API\_CONTRACTS |
| DR-021 | No row-level security in the baseline. Every metric SQL file carries the mandatory scope fragment bound from AccessScope; CI rejects a file without it; the API reads business data through a read-only role | ARCHITECTURE, DATABASE\_SCHEMA |
| DR-023 | Lineage metrics (enquiry → proposal → lease conversion, inspection → handover lag, drawing approval → handover lag) have kind “new” and are never shown as parity | KPI\_CATALOG |
| DR-024 | English-first UI with no RTL; Arabic names are stored in name\_ar columns for fidelity and not displayed | DATABASE\_SCHEMA, PRODUCT\_SPEC |
| DR-027 | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy Core, psycopg 3, Alembic, uv; Node 22 LTS, pnpm, Next.js (App Router), TypeScript strict, TanStack Query, zod; PostgreSQL 16; pytest, Vitest, Playwright; OpenTelemetry with structured JSON logs. Exact versions pinned by lockfiles in M0 and recorded in ADR-0003 | ARCHITECTURE, ADR-0003 |
| DR-028 | Pydantic models are the source of every contract; JSON Schema (2020-12) is exported from them; TypeScript types and zod schemas are generated; CI regenerates and fails on any diff | API\_CONTRACTS, ADR-0004 |
| DR-029 | Conversation, run, answer and dataset state lives in PostgreSQL schema agent; insight state in schema insights; no Redis | DATABASE\_SCHEMA |
| DR-030 | One YAML file per metric plus one SQL template file per query; validated at startup and in CI, including the scope lint | KPI\_CATALOG |
| DR-037 | Local Docker Compose only; no cloud deployment | ARCHITECTURE, plans/M0 |
| DR-042 | New and corrected metrics, including the three as-of metrics of DXD-80, enter only through KPI\_CATALOG with their kind and decision reference | KPI\_CATALOG |
| DR-043 | 3 regions and 25 fictional malls at the PRD §8 volume targets; the canonical figures (dataset sd-2026.10.20-01) are the acceptance reference | SYNTHETIC\_DATA\_STRATEGY |
| DR-044 | Currency SAR, area m², percentages to 1 decimal, counts as integers, a missing value shown as “—” with a reason | DESIGN\_SYSTEM, KPI\_CATALOG |
| DR-046 | Drawing grades live in a normalized fitout\_drawing\_documents table, one row per document, not parsed from JSON | DATABASE\_SCHEMA |
| DR-047 | Location hierarchy region → mall → property → unit, with an explicit property\_groups table for discrepancy roll-up and no hard-coded ID joins | DATABASE\_SCHEMA |
| DXD-22 | Treemap minShare 0.08 controls label visibility only; every category and sub-category stays a tile with its drilldown | GENERATIVE\_UI, DESIGN\_SYSTEM |

## 5. Engineering decisions (ED, D)

Engineering decisions fix how the approved design is built. They never reopen a DR or DXD decision. Approved ones are recorded in ADRs.

| ID | Decision | Status | Option | Recorded in | Needed before |
|---|---|---|---|---|---|
| ED-01 | How specifications reach the repository | **Approved 2026-10-22** | A: branches and milestone PRs; owner merges; supersedes DR-035 | ADR-0001 | M0 specs |
| ED-02 | Backend topology | **Approved 2026-10-22** | A: modular monolith, agent in-process | ADR-0005 | M0 specs |
| ED-03 | Reference documents in the repository | **Approved 2026-10-22 (scoped)** | A: frozen copies; scope limited to preserving the reference documents and design baseline | ADR-0002 §3; STATUS | — |
| ED-04 | How the slice is planned | **Approved 2026-10-22** | A: slice cards tagged in milestone plans plus `SLICE_FIVE_DAY.md`; delivery class slice / full / deferred | ADR-0002 §4 | M0 specs |
| ED-05 | CI/CD scope | **Approved 2026-10-22** | A: GitHub Actions CI; images built, not pushed; no deploy | ADR-0015 §2 | M0 specs |
| ED-06 | When M0 is built | **Approved 2026-10-22** | A: after PR-M0 is approved and merged, subject to explicit build authorization | ADR-0015 §3 | M0 specs |
| D-01 | Snapshot schema | **Approved 2026-10-22** | A: dedicated `snap` schema | ADR-0006 §2 | M0 specs |
| ED-07 | POC sign-in | **Approved 2026-10-22** | A: fixture-user sign-in with a signed httpOnly session cookie, limited to `dev`, `test` and `ci`; any other environment fails closed; authorization and grants always enforced on the backend | ADR-0016 | M0 build |
| ED-08 | Model determinism in tests | **Approved 2026-10-22** | A: scripted mock for unit tests, recorded replay in CI, separate controlled live evaluations; a missing recording fails, never a live call | ADR-0017 (adapter detail: ADR-0009, PR-M3) | M0 build |
| ED-09 | Styling approach | **Approved 2026-10-22** | A: CSS Modules with shared design tokens and generated colour and spacing variables; preserves the approved Ink & Violet design | ADR-0018 (token set: DESIGN_SYSTEM, PR-M2) | M0 build |
| ED-10 | AG-UI version pin | Proposed | A recommended: AG-UI 1.0; B: last 0.x | — (ADR-0010) | PR-M4 |
| ED-11 | Evaluation scoring (resolves DR-036) | Proposed | A recommended: deterministic 100% + LLM judge + ≥ 20% human spot-check; B: deterministic + human only | — (ADR-0014) | PR-M5 |

### 5.1 Approved Option A definitions for ED-07, ED-08 and ED-09

**Status: Approved 2026-10-22 by the project owner (Option A for all three).** These are the decision texts recorded in ADR-0016, ADR-0017 and ADR-0018. The M0 sections written to them are now normative. The owner's approval wording is quoted under each decision; where it adds a requirement, the requirement is numbered into the decision text. The Option B paragraphs are kept as the record of the rejected alternative.

#### ED-07 — POC sign-in

**Option A (approved decision text)**

1. The POC has no passwords, no user table and no identity provider. A principal signs in by choosing a fixture principal on `/sign-in`. The fixture principals are defined in `tests/fixtures/principals.yaml` and validated against `principal.v1` at startup.
2. `POST /api/v1/auth/dev/sign-in {principalId}` issues a session cookie named `cenomi_session`:
   - the payload is `{principalId, issuedAt, expiresAt}`;
   - it is signed with HMAC-SHA256 (Python standard library) using `SESSION_SECRET` (at least 32 bytes) and verified in constant time;
   - the time-to-live is `SESSION_TTL_MINUTES` (default 480);
   - attributes are `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure` when served over HTTPS.
3. `GET /api/v1/me` returns the principal. `POST /api/v1/auth/sign-out` clears the cookie. An unknown principal, or a tampered or expired cookie, is refused: `404 NOT_AVAILABLE` at sign-in, `401 UNAUTHENTICATED` elsewhere.
4. The sign-in routes are mounted only when `AUTH_MODE=dev_fixture` and `CENOMI_ENV` is `dev`, `test` or `ci`. Any other combination refuses to start (ARCH-R026).
5. Roles and permissions remain backend-enforced (DR-019). The browser never reads the cookie. The demo persona switch is sign-out followed by sign-in.
6. Out of scope: real authentication, multi-factor authentication, account management, single sign-on.
7. **Production fails closed.** The POC defines no production environment. Any `CENOMI_ENV` other than `dev`, `test` or `ci`, including any attempt to run the POC as production, refuses to start (ARCH-R026 cases b and e). The dev sign-in routes are never mounted outside those three environments.
8. **Authorization and grants are always enforced and validated on the backend.** The cookie carries only `principalId`, `issuedAt` and `expiresAt`. Role, grants and scope are resolved on the server from the fixture principal on every request and are never accepted from the cookie, a header, a query parameter or a request body. Every data access goes through AccessScope (ARCH-R077–R082).

> Owner's approval (2026-10-22): "ED-07 — Option A: Fixture-user authentication with signed HTTP-only session cookies, limited to development, test, and CI. Production must fail closed. Authorization and grants must always be enforced and validated on the backend."

**Affects:** ARCHITECTURE §5.4 (auth routes), §6.6; M0-T06; M0-T04 (`/sign-in`); `.env.example`.

**Option B (not chosen)** (username and password table):
- M0-T06 is rewritten: an `app_users` table with password hashes, a hashing dependency, a login form, and password policy and lockout rules;
- ARCHITECTURE §6.6 and the sign-in route change;
- the cookie boundary stays.

#### ED-08 — Model determinism in tests

**Option A (approved decision text)**

1. There are three model-provider kinds behind one adapter (ARCHITECTURE §8.2):

   | Kind | Behaviour | Where used |
   |---|---|---|
   | `mock` | Scripted responses declared inside a test | Always allowed |
   | `replay` | Recorded live responses | CI and E2E |
   | `live` | The configured provider and models (GDQ-12) | Manual runs only |

2. Replay recordings are keyed by the SHA-256 of a normalized request: model role, prompt template ID and version, structured-output schema ID, messages, tool list and decoding parameters. Provider-specific transport fields are excluded.
3. Each recording is stored as one JSON file under `LLM_REPLAY_DIR` (default `tests/fixtures/llm-replay/`). The file carries the response, provider, model, recording time and the commit it was recorded at.
4. **A replay miss is an error, never a fallback to a live call.** Changing a prompt template version therefore forces an explicit re-recording.
5. Recordings are produced only by `make agent-test-live RECORD=1`, which is manual, budget-limited and uses separate credentials. They are committed only through a reviewed PR.
6. CI (`ci/agent`, `ci/e2e`) runs with `LLM_MODE=replay` and has no model credential. The live model is measured only through `eval-live.yml` or `make agent-test-live`, and is never a required check.
7. **Missing recordings fail.** A replay miss, an unreadable recording or a recording for a different request hash fails the test with an explicit replay-miss error (its error code is registered with ADR-0009 in PR-M3); it never triggers an unplanned live-model call. The `replay` provider has no code path to a live provider.

> Owner's approval (2026-10-22): "ED-08 — Option A: Scripted mock model for deterministic unit tests, recorded replay responses for CI, and separate controlled live-model evaluations. Missing recordings must fail rather than trigger unplanned live-model calls."

**Affects:** ARCHITECTURE §8.2, §10.2 (areas F and G), §10.5; `ci_checks.yaml` (`LLM_MODE=replay`); `make_targets.yaml` (`agent-test-replay`, `agent-test-live RECORD`); ADR-0009 (PR-M3); M0-T07 (`eval-live.yml` skeleton); M0-T11 (markers).

**Option B (not chosen)** (CI calls the live model):
- CI needs a model secret, which conflicts with DEVENV-R027 for PR workflows unless they are restricted to non-fork branches;
- results become non-deterministic and cost money per run;
- the replay rows above are removed.

Note: the approved testing requirements (mock and replay tests must not depend on live APIs, and live tests must be opt-in) already require the substance of Option A.

#### ED-09 — Styling approach

**Option A (approved decision text)**

1. Component styles are CSS Modules (`*.module.css`), co-located with their component.
2. Global CSS is limited to a reset, base typography and the token variables.
3. Design tokens are defined once, in `specs/design/tokens.json` (PR-M2, Ink & Violet, DXD-01). `make codegen` generates:
   - `apps/web/src/styles/tokens.css` (CSS custom properties);
   - `packages/viz/src/tokens.ts` (TypeScript constants for ECharts colours and sizes);

   both are GENERATED and drift-checked.
4. There is no UI kit, no Tailwind and no runtime CSS-in-JS. Theming, including the optional later Night Operations theme, swaps variable sets only.
5. In M0, the shell uses a minimal provisional stylesheet `apps/web/src/styles/shell.css` with neutral variables, replaced by the generated tokens in M2.
6. **The approved Ink & Violet visual design is preserved** (DXD-01). The generated variables cover at least colour and spacing; values come only from `tokens.json`, never hard-coded in a CSS Module once the tokens exist (M2). The provisional M0 stylesheet introduces no new visual language.

> Owner's approval (2026-10-22): "ED-09 — Option A: CSS Modules with shared design tokens and generated colour/spacing variables, preserving the approved Ink and Violet visual design."

**Affects:** ARCHITECTURE §6.1 (`styles/`); ADR-0003 (styling row); M0-T04; DESIGN_SYSTEM (PR-M2).

**Option B (not chosen)** (Tailwind):
- Tailwind and PostCSS dependencies are added, with a Tailwind theme generated from `tokens.json`;
- utility classes replace CSS Modules;
- M0-T04 and ADR-0003 change.

Configuration (not a decision): GDQ-12 provider, primary and fallback model names and the API key — before slice day 3 and before the M0-T09 latency sample can be taken; never committed.

