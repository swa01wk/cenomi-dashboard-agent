# Approved design decision register

The register holds 141 decisions: the 48 G0 entries (DR-001…047 with DR-018b) and DXD-01…93 from the six design phases. 104 are approved and ready, 7 await engineering verification, 23 need a decision, 2 are deferred from the first five days and 5 are superseded. It replaces the separate phase registers as the single authoritative list for the M0 specifications.

Status meanings: **Approved · ready** = can be specified as written. **Verification pending** = approved, but a real-runtime check is still owed. **Decision required** = needs your answer (most are batchable defaults, GDQ-10). **Deferred from five days** = in the full scope, outside the first delivery. **Superseded** = kept for history; its successor is named.

| ID | Decision | Rule | Origin | GD status | Note |
| --- | --- | --- | --- | --- | --- |
| DR-001 | Parity policy | Reproduce business definitions and visual forms; never security defects; fix nondeterminism; quirks that change a number → parity metric + named corrected metric. | G0 | Approved · ready |  |
| DR-002 | Parity classification of REF findings | §3.4 rulings; soft-deleted fit-out rows only in parity cards, never in insights or recommendations. | G0 | Approved · ready | Per-metric confirmation in M0 KPI batches. |
| DR-003 | Frozen as\_of per data version | One as\_of used by seed, SQL, APIs, agent, insights and fixtures; NOW() banned in metric SQL. | G0 | Approved · ready |  |
| DR-004 | as\_of value and data window | as\_of 2026-10-20; transactional events 2024-01-01 → as\_of. | G0 · proposed (M0) | Decision required | Batch approval. All designs already use these values. |
| DR-005 | Monitoring is synthetic historical replay | Detectors replayed at checkpoints ≤ as\_of; never live monitoring. | G0 | Approved · ready | Calendar fixed by DXD-75 (weekly, monthly on the 20th, events). |
| DR-006 | Time zones | Store UTC; bucket every calendar filter and age band in Asia/Riyadh. | G0 | Approved · ready |  |
| DR-007 | Apache ECharts for dashboard and GenUI charts | Conditional on faithful V2 reproduction, treemap fidelity and chart accessibility. | G0 (conditional) | Verification pending | Real-runtime validation still outstanding (DXD-21, DXD-61); fallback DXD-23. |
| DR-008 | Non-chart visuals as HTML | Stage flow approved; stat tiles, occupancy meter, permit strip, captions proposed. | G0 · partly proposed | Decision required | Batch approval: freeze the remaining HTML visuals at GD (built and verified in DX2/DX3). |
| DR-009 | Level 5 in scope after the core agent | Insight discovery, monitoring, notifications, lifecycle and feedback. | G0 | Approved · ready |  |
| DR-010 | Sequencing M3c → M6 after M5 | Core agent evaluated without Level 5; proactive work after. | G0 | Approved · ready | The five-day plan reorders delivery; the dependency stays. |
| DR-011 | In-app notifications only | Inbox, badge, per-user list; no email, SMS or push. | G0 | Approved · ready | Confirmed by DXD-77. |
| DR-012 | Meaning of feedback | Stored; drives deterministic re-ranking, suppression and evaluation reports. | G0 | Decision required | Conflicts with DXD-72 (logged for review only). GDQ-05. |
| DR-013 | Read-only business data | Application state in separate schemas written by a separate DB role. | G0 | Approved · ready |  |
| DR-014 | Provider-agnostic LLM adapter | Model is configuration; structured output and tool calling required. | G0 | Approved · ready |  |
| DR-015 | Model roles and selection | planner / synthesizer / fast keys; benchmark two candidates. | G0 · open | Decision required | Provider and API key needed before agent work starts (GDQ-12). |
| DR-016 | Plain @ag-ui/client | Own React hooks and the GenUI registry; no CopilotKit. | G0 | Approved · ready |  |
| DR-017 | AG-UI event mapping | CUSTOM cenomi.presentation.v1, ACTIVITY\_\* plan, sanitized TOOL\_CALL\_*, STATE\_* context; no reasoning events. | G0 · proposed | Verification pending | Design contract DXD-40; SDK assumptions checked against the pinned version (GDQ-11). |
| DR-018 | Synthetic sales\_funnel\_snapshot | Live card counts; snapshot divergence explained. | G0 | Approved · ready |  |
| DR-018b | No approvals filter-list snapshot table | Filter options from live data. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-019 | Simplified, backend-enforced roles and permissions | Final role list in M0. | G0 | Approved · ready | Design fixture roles: portfolio admin, Central manager, tenant (one lease, company). |
| DR-020 | Scope semantics | Explicit scope kinds; empty scope = empty result; card and endpoint share a permission; client can only narrow; refs bound to principal, scope, data version. | G0 · accepted | Approved · ready | Extended by DXD-38, 56, 85. |
| DR-021 | Row-level security not in baseline | Mandatory scope fragment + lint + read-only role. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-022 | Explicit lineage | enquiry → proposal → lease; unit → inspection → drawing → handover via fitout\_projects. | G0 | Approved · ready | No designed journey uses it yet (PRD journey 3); GDQ-09. |
| DR-023 | Lineage metrics labelled new | Cohort conversion, inspection → handover lag. | G0 · accepted (M0) | Decision required | Batch approval with the KPI catalog. |
| DR-024 | English-first UI | Arabic names stored for fidelity (proposed); no RTL. | G0 · partly proposed | Decision required | English-first approved at G0; Arabic storage in the batch. |
| DR-025 | Agent proposes dashboard filter changes; user confirms | Frontend tool propose\_dashboard\_filters. | G0 | Approved · ready | Designed in DX4 J3. |
| DR-026 | Prospective-tenant journey | Stretch goal. | G0 · proposed (M5) | Deferred from five days |  |
| DR-027 | Tech stack | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy Core, psycopg 3, Alembic, uv; Node 22, pnpm, Next.js, TS, TanStack Query, zod; PostgreSQL 16; pytest, Vitest, Playwright; OpenTelemetry. | G0 · proposed (M0) | Decision required | Batch approval; versions pinned in M0. |
| DR-028 | Pydantic → JSON Schema → TS + zod | CI drift check. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-029 | Conversation and run state in PostgreSQL schema agent | No Redis. | G0 · proposed (M0) | Decision required | Batch approval. Insight tables in schema insights (DX6). |
| DR-030 | Metric registry as YAML; SQL templates as files | Startup validation and scope lint. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-031 | Narrative numbers only from fact tokens | Verifier rejects other numbers; one retry; deterministic template. | G0 · accepted | Approved · ready | Designed DX4/DX5 (DXD-41, 55) and DX6 (DXD-63). |
| DR-032 | Lifecycle with bounded re-plan | plan → validate → DAG → ≤ 1 re-plan → facts → synthesis → verify → compose. | G0 · accepted | Approved · ready | Designed DX4 (J6 budget, J9 interruption). |
| DR-033 | Two-tier fixtures | Micro hand-verified fixtures; process-based macro seed with property assertions. | G0 · accepted | Approved · ready | DX6 adds golden cohorts and invariants (DXD-81). |
| DR-034 | Repository naming | Project-instruction docs/ and plans/ names; TA §11 code layout. | G0 | Approved · ready |  |
| DR-035 | Planning documents committed manually | Option A. | G0 | Approved · ready |  |
| DR-036 | Evaluation scoring | Deterministic checks; LLM judge for explanation quality; ≥ 20% human spot-check. | G0 · proposed (M5) | Decision required | Needed before the evaluation spec. |
| DR-037 | Local Docker Compose | No cloud deployment. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-038 | Optional technical spike | Throwaway AG-UI round trip and model latency. | G0 · open | Decision required | Recommended now (GDQ-11). |
| DR-039 | Design references | Design from the API Reference. | G0 · resolved | Approved · ready |  |
| DR-040 | Brand treatment | Cenomi-inspired, fictional data, synthetic indicator, no brand assets. | G0 | Approved · ready |  |
| DR-041 | Design before specifications | Gate GD before M0 specifications. | G0 | Approved · ready | This gate. |
| DR-042 | New and corrected metrics only via the KPI catalog | No silent scope expansion. | G0 · proposed (M0) | Decision required | Batch approval. Adds three as-of metrics (DXD-80). |
| DR-043 | Scale and geography | 3 regions, 25 fictional malls, PRD §8 targets. | G0 · proposed (M0) | Decision required | Batch approval; used by every design. |
| DR-044 | Units and numeric policy | SAR, m², 1-decimal %, integers, — with a reason. | G0 · proposed (M0) | Decision required | Batch approval; implemented by DXD-44. |
| DR-045 | Detector set and priority formula | Robust z, peer outlier, trend break, co-movement; impact × severity × confidence. | G0 · proposed | Superseded | Superseded by DXD-63, 64, 66, 89, 90. |
| DR-046 | Normalized fitout\_drawing\_documents | Not parsed from JSON. | G0 · proposed (M0) | Decision required | Batch approval. |
| DR-047 | Simplified location hierarchy | region → mall → property → unit; explicit property\_groups. | G0 · proposed (M0) | Decision required | Batch approval. |
| DXD-01 | Visual direction | Ink and Violet is the primary design system; Night Operations optional later; Warm Editorial not pursued. | DX1 | Approved · ready |  |
| DXD-02 | Screen architecture | Four screens plus the docked agent panel and four overlays: card focus, inspector, notifications, filter-change confirmation. | DX1 | Approved · ready | GDQ-08 proposes the bell opens the inbox instead of a notifications overlay. |
| DXD-03 | Agent UX | Docked panel for quick questions; expandable workspace for investigations; entry points on every card and data point. | DX1 | Approved · ready |  |
| DXD-04 | Shared inspector | Evidence, Definition, Records and Execution tabs for metrics, generated components and insights alike. | DX1 | Approved · ready | Insight detail must reuse the inspector’s evidence components. |
| DXD-05 | Three kinds of context | Card filters, the agent’s query scope, and proposed filter changes that apply only after confirmation, shown separately. | DX1 | Approved · ready |  |
| DXD-06 | State preservation | Dashboard ↔ workspace keeps conversation, selections, card filters, pins and scroll. | DX1 | Approved · ready |  |
| DXD-07 | Responsive behaviour | Desktop, tablet, mobile; below desktop the agent is an overlay or full screen. | DX1 | Approved · ready |  |
| DXD-08 | Statement labels | Observed, Derived, Hypothesis, Recommendation, Unavailable as text; colour never the only signal. | DX1 | Approved · ready |  |
| DXD-09 | Synthetic data | Reference date and synthetic designation on every screen and card footer. | DX1 | Approved · ready |  |
| DXD-10 | Expanded cards | Centred overlay plus Open in workspace with filters, selection and tab intact. | DX2 | Approved · ready |  |
| DXD-11 | Records vs Inspector | Drilldowns in the card’s Records tab; inspector for evidence, definitions, provenance, execution; shared table components. | DX2 | Approved · ready |  |
| DXD-12 | Selection model | One active selection globally; per-card memory; explicit pinning. | DX2 | Superseded | Superseded for analytical context by DXD-29 → DXD-32; per-card memory kept. |
| DXD-13 | Mall map | Out of the baseline; mall cards and available units kept. | DX2 | Approved · ready |  |
| DXD-14 | Partial coverage everywhere | Same Partial label and a sentence naming what is missing; coverage is a result field. | DX2 | Approved · ready |  |
| DXD-15 | Filters vs boundaries | Removable filter chips; locked Boundaries row for access and reference date. | DX2 | Approved · ready |  |
| DXD-16 | One state vocabulary | loading, zero, empty, unavailable, error, outside\_access, partial, undefined\_ratio for cards and components. | DX2 | Approved · ready |  |
| DXD-17 | Context and scroll preservation | Overlays keep scroll, filters, selection and tab. | DX2 | Approved · ready |  |
| DXD-18 | Chart and table share one dataset | Same authorized result; finer table rows must reconcile with chart totals. | DX2 | Approved · ready |  |
| DXD-19 | Phone navigation | Below 820 px the rail becomes a bottom tab bar. | DX2 | Approved · ready |  |
| DXD-20 | Value labels on narrow charts | Value on the selected mark and tooltip; Table lists all. | DX2 | Approved · ready |  |
| DXD-21 | How DR-007 is verified | Gallery self-test with real ECharts, or a local version-pinned asset; test doubles never count. | DX3 | Verification pending | ECharts could not be loaded from this workspace (egress refused); GDQ-06. |
| DXD-22 | minShare 0.08 | Option A provisionally: every tile stays with its drilldown; the threshold only hides labels. | DX3 | Decision required | No ui-kit source available; batch approval makes it final. |
| DXD-23 | Treemap fallback | Custom squarified component if ECharts misses the thresholds. | DX3 | Approved · ready |  |
| DXD-24 | V2 palette with verified accessibility | Keep V2 hues with labels, focus, text alternatives and non-colour selection; WCAG verified, not assumed. | DX3 | Verification pending | axe-core and screen reader on the real build. |
| DXD-25 | One selection contract | Every selectable element emits selection\_ref.v1. | DX3 | Approved · ready |  |
| DXD-26 | What a selection carries | Metric id, version and kind, grain, dimensions, value, unit, filters, scope, dataset reference. | DX3 | Approved · ready |  |
| DXD-27 | Chart ↔ table keeps the definition | Same result reference; finer rows must reconcile. | DX3 | Approved · ready |  |
| DXD-28 | Same semantics everywhere | Same states, actions and payload on every surface. | DX3 | Approved · ready |  |
| DXD-29 | Active, kept and pinned | One active selection globally; kept selections never sent automatically. | DX3 | Superseded | Superseded by DXD-32. |
| DXD-30 | Grounded numbers | Every displayed number comes from the dataset; the model never types a number. | DX3 | Approved · ready |  |
| DXD-31 | Composite rankings only on request | Multi-KPI comparison with leaders by default; a combined score only when asked. | DX4 | Approved · ready |  |
| DXD-32 | Analytical selections are thread-local | Each investigation has its own selections; imports are explicit. | DX4 | Approved · ready |  |
| DXD-33 | History is immutable | Stored answers never change; re-run creates a new run. | DX4 | Approved · ready |  |
| DXD-34 | KPI reconciliation (finding) | Rawdah 41 (all types, 1m+) and 32 (proposals, all ages) are different populations; both reconcile. | DX4 | Approved · ready | Extended by the DX6 reconciliation (DXD-80). |
| DXD-35 | Coverage semantics | Observed subset labelled with coverage; full total Unavailable, never estimated. | DX4 | Approved · ready |  |
| DXD-36 | Evidence envelope on every statement and visual | Class, metric ids and versions, filters, scope, freshness, dataset version, coverage. | DX4 | Approved · ready |  |
| DXD-37 | Versioned recovery | A successful retry creates v2; v1 kept unchanged. | DX4 | Approved · ready |  |
| DXD-38 | Context isolation rules | Threads, roles, chips and resume never widen authorization; re-checked. | DX4 | Approved · ready |  |
| DXD-39 | Accessibility of evidence, activity and selection | Text states, aria-pressed, focus-managed inspector, one polite live region. | DX4 | Verification pending | axe-core and screen reader on the real build. |
| DXD-40 | AG-UI handoff contracts | Event-to-state mapping, run identity, cancellation, reconnection, retries, idempotency. | DX4 | Verification pending | SDK assumptions checked against the pinned version (GDQ-11). |
| DXD-41 | The result is authoritative | Components render only from the validated resultRef; text uses fact tokens. | DX5 | Approved · ready |  |
| DXD-42 | Closed component registry | Fifteen kinds; no model-generated code. | DX5 | Approved · ready | Mapping to the PRD §7 list: GDQ-02. |
| DXD-43 | Representation alternates | View as without re-query. | DX5 | Approved · ready |  |
| DXD-44 | One formatting module | Counts, rates, SAR, missing, zero, undefined formatted once. | DX5 | Approved · ready |  |
| DXD-45 | State vocabulary | Never conflated. | DX5 | Approved · ready |  |
| DXD-46 | Size classes | Workspace 760, panel 420, canvas 360, phone 358, expanded 1000. | DX5 | Approved · ready |  |
| DXD-47 | Validation and fallback | Server validation plus client re-validation. | DX5 | Approved · ready | Amended by DXD-57. |
| DXD-48 | Envelope per component | A disagreeing payload envelope is rejected. | DX5 | Approved · ready |  |
| DXD-49 | Drilldown and selection | Accessible marks; selection\_ref.v1; records from the same population. | DX5 | Approved · ready |  |
| DXD-50 | Fixtures are labelled | Production never renders fixtures. | DX5 | Approved · ready |  |
| DXD-51 | Bounded representation policy | Intent, shape, dimensions, accessibility, space (P1–P6); user switches with View as. | DX5 | Approved · ready |  |
| DXD-52 | Deterministic table fallback | From the verified, authorized result. | DX5 | Approved · ready |  |
| DXD-53 | Treemap below 400 px | Ranked list, same keys and selection. | DX5 | Approved · ready |  |
| DXD-54 | Component budget | 3 in the panel, 6 in the workspace. | DX5 | Approved · ready |  |
| DXD-55 | Verified calculations | Calc records recomputed by the verifier; neither LLM nor renderer derives KPI values. | DX5 | Approved · ready |  |
| DXD-56 | Authorization by grants | Current grants vs scope, dimensions, records; withhold, never filter; never name out-of-grant entities. | DX5 | Approved · ready |  |
| DXD-57 | Failure taxonomy | Presentation, calculation, authorization, unknown result, stale, partial are distinct. | DX5 | Approved · ready |  |
| DXD-58 | Fallback preserves boundaries | Rows, paging, evidence, coverage, formatting, authorization. | DX5 | Approved · ready |  |
| DXD-59 | Subset disclosure | Declared and disclosed; the renderer never aggregates. | DX5 | Approved · ready |  |
| DXD-60 | Continuity | Envelope and selection kept across View as, moves, expand, resume. | DX5 | Approved · ready |  |
| DXD-61 | ECharts at the Design Gate | GenUI charts validated on ECharts 5.6.0. | DX5 | Verification pending | Same pending verification as DXD-21. |
| DXD-62 | Implementation priority | Ten core kinds first; specialized kinds use the table fallback until built. | DX5 | Approved · ready |  |
| DXD-63 | Detection is deterministic | Rules in the analytics layer; templated text with fact tokens. | DX6 | Approved · ready |  |
| DXD-64 | Detector catalogue | D1–D8 as detectors-1.1. | DX6 | Approved · ready | Refined by DXD-89. |
| DXD-65 | Audience-scoped instances, three checks | Generation, delivery, every read, against current grants. | DX6 | Approved · ready |  |
| DXD-66 | Transparent scoring | impact × urgency; P1 ≥ 6, P2 3–5, P3 ≤ 2; Low → Watch; positive → P3. | DX6 | Approved · ready | Rules in DXD-90. |
| DXD-67 | Shared lifecycle, personal triage | Shared and per-user states. | DX6 | Approved · ready | Thread content private (DXD-83). |
| DXD-68 | Deduplicate, merge, re-notify, suppress | Band rise or ≥ 10% worse than the last notified version. | DX6 | Approved · ready |  |
| DXD-69 | Quiet by default | Logged decisions with reasons. | DX6 | Approved · ready |  |
| DXD-70 | Delivery | P1 in app; P2/P3 digest; Watch inbox only. | DX6 | Approved · ready | Digest scheduling deferrable (DXD-92). |
| DXD-71 | Investigation handoff | Insight imported and labelled into a private thread. | DX6 | Approved · ready |  |
| DXD-72 | Feedback | Logged for review; no automatic threshold change; per-user mute. | DX6 | Decision required | Reconcile with DR-012 (GDQ-05). |
| DXD-73 | Scenario history | Declared history extension. | DX6 | Superseded | Amended by DXD-81. |
| DXD-74 | Five-day priority (DX6) | Original core list. | DX6 | Superseded | Amended by DXD-92. |
| DXD-75 | Evaluation cadence (DXQ-12 A) | Weekly, monthly on the as-of day, calendar months, events; all replay. | DX6 | Approved · ready |  |
| DXD-76 | Instances per authorized scope (DXQ-13 A) | Regional instances within each authorized region; operator and tenant never share. | DX6 | Approved · ready |  |
| DXD-77 | In-app digest only (DXQ-14 A) | No email in the POC. | DX6 | Approved · ready |  |
| DXD-78 | Positive findings (DXQ-15 A) | P3 Opportunity insights. | DX6 | Approved · ready |  |
| DXD-79 | Tenant proactive insights (DXQ-16 A) | Own-lease Watch and Action needed. | DX6 | Approved · ready | No tenant Watch in the current data after the S6 correction (GDQ-04). |
| DXD-80 | Canonical approval-age metric and as-of history | Parity live card; three new as-of metrics equal to parity at as\_of; “waiting 31+ days”; no “overdue”. | DX6 | Decision required | New metrics need KPI-catalog approval (DR-042); route GDQ-03. |
| DXD-81 | Reconstructible scenario history | Series reproduced from record lifecycles; invariants GI-01…16. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-82 | Replay oracle | Insights, versions, notifications and candidates only from replay. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-83 | Private investigation threads | Owner only, re-authorized each read; others see status and role only. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-84 | Explicit shared summaries | Owner-selected verified statements inside the instance scope. | DX6 | Deferred from five days | Designed and tested; secondary. |
| DXD-85 | Uniform refusals | Same response for unauthorized and non-existent. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-86 | Run identity and triggers | run\_key over trigger, checkpoint, dataset, configuration, partition; event dedupe; one worker. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-87 | Atomic publication and idempotent delivery | Staging; one transaction; optimistic version check; outbox keys. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-88 | Restart, late and corrected data | Restart discards staging; ingested\_at; corrections = new dataset version; stale label. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-89 | Detector quality rules (detectors-1.1) | Versioned thresholds, minimum history, missing data, coverage, denominators, consecutive periods, no cross-entity associations. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-90 | Scoring rules | Impact and urgency rules explicit. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-91 | Watch promotion and clearing | Two periods → Medium Risk; else clears. | DX6 | Approved · ready | Refinement record; confirm at GD. |
| DXD-92 | Five-day priority for proactive work | Core incl. D8 and E2E tests; D3, D4, full D7, snooze, digest, feedback analytics secondary. | DX6 | Approved · ready | Overall five-day scope is GDQ-01. |
| DXD-93 | Lease-scoped tenant actions | Never company-wide counts for a lease audience. | DX6 | Approved · ready | Refinement record; confirm at GD. |

## Gate decisions recorded (22 Oct 2026)

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

### Final definitions of the 17 batch-approved defaults (GDQ-10)

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
