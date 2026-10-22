# Cenomi Dashboard Intelligence Agent — Product Requirements Document

**Version:** 1.0 · **Date:** 21 October 2026 · **Status:** POC specification

## 1. Executive summary

Build a self-contained proof of concept that recreates the Cenomi Admin and Tenant dashboard V2 KPIs and chart forms using a realistic relational synthetic dataset, then adds a conversational intelligence agent. The agent must understand KPI business definitions, retrieve verified values and supporting records, derive comparisons and cross-KPI insights, and return context-appropriate generative UI: KPI cards, tables, charts, heatmaps, explanations, limitations and interactive drilldowns.

**Central product promise:** Ask a business question in natural language and receive an accurate, evidence-backed answer in the most useful presentation format, without knowing the schema or composing dashboard filters manually.

**Principles:** chart and agent share metric definitions; deterministic numerical computation; no invented data; distinction between observation, hypothesis and causation; usable absence-of-data responses; secure access boundaries; interactive follow-up context.

## 2. Scope and constraints

### In scope

1. Replicate all **12 Admin V2 cards** and Tenant dashboard card groups documented in `ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` (code review dated 13 October 2026), including matching chart families, status categories and relevant local filters.
2. PostgreSQL relational schema sufficient to reproduce the KPIs; seeded, reproducible, multi-year synthetic records with coherent foreign keys and lifecycle transitions.
3. Canonical KPI semantic registry, deterministic queries, read-only analytics tool API and chart/detail reconciliation.
4. Conversation agent with metric discovery, direct answers, derivations, comparisons, trending, ranking, investigation, prioritization and explanation of unsupported queries.
5. AG-UI bidirectional event stream, declarative validated UI components, dashboard-context synchronization, data-point drilldowns and follow-up prompts.
6. Evaluation suite covering metric accuracy, grounding, uncertainty, UI selection, access scope and latency.

### Out of scope for initial POC

Production Cenomi database connection or writes; Yardi/SAP/Appian integrations; actual tenant financial payments; autonomous approvals or operational changes; causal inference guarantees; unrestricted agent SQL or arbitrary HTML/JavaScript; mobile-native rendering; production-scale multi-tenancy and infrastructure SLOs.

The POC's records, amounts, organizations and mall names must be labelled **synthetic**. The original reference is static source analysis, not verified live data. Any current-code discrepancies are hypotheses to reproduce and classify, not production findings to assert as confirmed.

## 3. Users and jobs to be done

| Persona | Primary question | Needed result |
|---|---|---|
| Portfolio administrator | Which malls have rising vacancy or expiring leases? | Comparable occupancy, area and leasing exposure |
| Leasing manager | Where are leads or proposals stalling? | Funnel stage, trend, approval ageing and associated records |
| Operations / service manager | Which request categories are accumulating backlog? | Ranked backlog, status distribution, timeline and drilldown |
| Fit-out manager | Which units or malls are behind on inspection, drawings or handover? | Stage progress and pending work, with status caveats |
| Tenant | What do I need to do next? | Documents, requests, sales submissions and relevant actions |
| Business analyst / executive | What changed and what deserves investigation? | Evidence-backed patterns, limitations and priorities |

## 4. Dashboard parity requirements

### 4.1 Admin V2 cards

| ID | KPI / data | Required visual | Filters |
|---|---|---|---|
| `properties` | Property count, total units, occupied/vacant units and GLA | Stat tiles + unit occupancy meter | None |
| `kpis` | Expiring leases, active leases, pending sales submissions | 3 stat tiles | None |
| `leaseRequests` | Lease requests by unit type or registration source | Donut with switch | Year |
| `salesFunnel` | Requests → leads → proposals → contracts, signed/unsigned splits | Four-stage flow | Year, month, region, mall |
| `actionRequired` | Unread actionable notifications | List | None |
| `pendingApprovals` | Proposals/contracts/leases by age band | Half gauges | Region, mall |
| `pendingAmendments` | Amendment type × delay week | Heatmap | Year, month, region, mall |
| `serviceRequests` | Inquiries, work permits, complaints, status breakdown | Treemap + permit strip | Year, month, region, mall |
| `fitoutHandover` | Four inspection groups, pending handovers | Progress rings + callout | Year, month, region, mall |
| `fitoutDrawings` | MEP/architectural/electrical drawing progress | Horizontal stacked bars | Year, month, region, mall |
| `documentStatus` | Drawing grades A/B/C/D by mall and discipline | Stacked columns + table | Year, region, discipline |
| `unitDiscrepancy` | Matches/mismatches by month or mall | Diverging bars | Year, month, mall-wise/month-wise |

### 4.2 Tenant view

Keep lease/unit/brand KPIs; pending documents; open/total service requests; pending and approved sales submissions; pending/approved inquiries; tenant profile; payments placeholder (explicitly unavailable); action-required notifications; monthly reported-sales chart; requests by status/category; announcements/events; leasing opportunities; prospective tenant journey where feasible.

All charts must show empty, loading and error states. All applicable filters must be propagated to data retrieval and the agent context. A chart tooltip/drilldown should resolve the same metric population as its parent visual or clearly disclose documented differences.

## 5. Metric truth and compatibility

The initial dashboard-parity definitions follow the supplied reference, including: service-request treemap sizes excluding pending/closed; fit-out ring `reviewed/(received+remaining+reviewed)`; sales chart including submitted/approved; stage totals fetched from separate live-like sources. They must be labelled correctly and **must not be misrepresented** as SLA compliance, fit-out approval, realized revenue or cohort conversion.

The semantic registry stores formula, data grain, entity relationships, valid filters and date dimension, timezone, status inclusion/exclusion, authorization scope, unit, refresh timestamp, version, drilldown query, and analytical caveats. Optional improved/derived metrics receive different IDs and explicit labels rather than replacing parity KPIs silently.

### Known caveats requiring POC tests

- Live-like funnel aggregates versus batch snapshot are not identical sources; signed + unsigned may not equal all statuses.
- Admin active/expiring lease definitions can overlap or include grace-period records.
- Summary-data and sales endpoint use different pending status sets.
- Service request overview, list and tenant open-request count have different filtering/pagination semantics.
- Fit-out summary and list may count different statuses or deleted records.
- Approvals and amendments use different ageing cutoffs and future-date handling.
- Timestamp, region and property filtering vary among endpoints.
- Payment count is not implemented in the reference.

These become explicit contract tests and documented limitations. POC data must contain rows that expose them.

## 6. Conversational intelligence requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| AI-01 | Define/explain any dashboard KPI | Correct formula, source, scope and caveat |
| AI-02 | Retrieve current metric with inherited filters | Exact match against canonical query |
| AI-03 | Rank, aggregate, calculate percentages and deltas | Deterministic correct math |
| AI-04 | Compare periods, malls, regions or categories | Comparable time windows and denominators |
| AI-05 | Investigate across related KPIs | Explicit relationship and evidence; no unverified causal claim |
| AI-06 | Support contextual pronouns and selected visual values | Resolves “this”, “that mall”, “why so high?” correctly |
| AI-07 | Distinguish observed facts, hypotheses, actions | Every recommendation traces to measurements |
| AI-08 | Handle partial coverage and absent data | States exactly what is missing; related proxy is never passed off as answer |
| AI-09 | Produce inspectable provenance | Metric IDs, time scope, filter set, query/dataset reference |
| AI-10 | Prevent cross-user or cross-tenant data leakage | Server-enforced scope; denied request test |

Response coverage classes: `supported`, `derived`, `partial`, `related_only`, `unavailable`, and `error`. Numerical confidence is not fabricated: report coverage, sample size, period and derivation. If data are missing, stale or insufficient, the answer must say so.

## 7. Generative UI requirements

The agent chooses a renderer from an allowlisted catalog based on user intent and result shape. AG-UI is the transport/event protocol; declarative payloads are an application contract, not arbitrary executable code. A2UI compatibility is an extension, not a prerequisite.

| User question | Default composition |
|---|---|
| How many? | Metric card, short text, scope |
| Show details | Paginated/sortable table |
| Compare malls | Ranked bar chart + exact-values table |
| Trend | Line/column chart + change summary |
| Distribution | Donut or stacked bars |
| Where are delays? | Heatmap + summary cards |
| Why / what should we prioritize? | Evidence cards, comparable table, observations and caveats |
| Unsupported metric | Limitation card, explanation, available related metrics |

Catalog: `metric_card`, `metric_group`, `data_table`, `line_chart`, `bar_chart`, `stacked_bar`, `donut_chart`, `funnel`, `heatmap`, `progress_ring`, `status_badge`, `insight_card`, `warning_card`, `limitation_card`, `drilldown_action`.

Interactions: select a chart segment; ask about current selection; click row for detail; change compatible dimensions; switch table/chart when valid; trigger a question through approved actions. Every returned component binds to validated data or a server dataset reference, never model-authored numerical facts. Renderers accept only schema-valid props. Empty/unavailable states do not force fabricated charts.

## 8. Synthetic data product requirements

Baseline target: about **25 malls, 3 calendar years, 8k units, 6k leases, 60k service requests and 120k sales records**, plus related proposals, enquiries, amendments, drawing documents, inspections, notifications and discrepancies. These are configuration targets, not requirements for exact cardinality.

Use deterministic seed (`seed_version`, `random_seed`) and enforce referential integrity. Generate credible seasonality, multi-region access, vacant/occupied states, future/expired leases, stage conversion and dropoff, request status transitions, realistic turnaround times and document/sales reporting frequency.

Inject named scenarios with truth fixtures: seasonal sales; one mall with severe ageing; another with high volume but quick resolution; handover delays; long-running complaints; missing sales months; mismatched unit records; sparse-data periods; cancelled/reopened workflows; incomplete funnel statuses; permission-limited tenants. Expected insights must be verifiable from records. Never feed scenario labels directly to the agent.

## 9. Core journeys

1. **Ask from dashboard:** User views October 2026 Central region service-request treemap, asks “Which mall is worst?” → agent retrieves breakdown under identical scope → ranked chart/table + explicit prioritization criterion.
2. **Select-and-investigate:** User clicks a delayed approval heatmap cell, asks “What caused this?” → selected type and age band carried to agent → linked records and timing analysis → hypothesis with evidence and caveat.
3. **Cross-metric:** User asks whether delayed fit-out inspections accompany late handovers → linked unit cohorts and time windows → supported association or insufficient-linkage response.
4. **Tenant next action:** Tenant asks which documents are outstanding → permitted documents only → grouped table and navigation actions.
5. **Unavailable:** User asks for yesterday's mall footfall → no footfall table → clear refusal to provide a number, optional sales/occupancy proxies labelled as different metrics.
6. **Follow-up:** “Show that as a table” → reuse prior approved dataset, with no recalculation or fabricated values.

## 10. Non-functional requirements

- Deterministic numeric precision; explicit currencies SAR, percentage units, timezones and rounding.
- All agent reads are authenticated, read-only, time-bounded, row-limited, audited and access-scoped.
- POC latency objectives (to validate): cached single metric <2 seconds p95; common analytics question <10 seconds p95; heavier multi-tool investigation <20 seconds p95 with progress events.
- UI accessible by keyboard and screen readers; responsive desktop/tablet; legend labels and chart values available in text/table alternative.
- No production identifiers or sensitive records in fixtures; synthetic-only branding/disclaimer.
- Request IDs, tool trace, metric/query version, error classification and selected data evidence logged safely.

## 11. Definition of done

- Every scoped dashboard V2 card renders using seeded API data and parity-tested metrics.
- At least 150 benchmark questions across direct, derived, comparative, investigative, partial, unavailable and adversarial categories.
- 100% deterministic numerical checks pass on golden fixtures; no unsupported numeric assertions on unavailable-data tests.
- Interactive text + validated generative components render correctly across all allowlisted types.
- Chart selection and follow-up query preserve context and backend access control.
- Drilldown counts reconcile where semantic definitions match; unavoidable differences visibly documented.
- Seed regeneration reproduces expected outputs; zero production data dependencies.

## 12. Delivery and decision gates

M0 metric definition/sign-off; M1 schema + seed generator; M2 APIs + dashboard parity; M3 agent/semantic tools; M4 AG-UI + declarative renderer; M5 evaluation and demonstration. Admin dashboard is implemented and assessed first, followed by the Tenant role with permission-scoped reuse. Production deployment and source integration require separate approval.

**Source baseline:** `ADMIN_TENANT_DASHBOARD_API_REFERENCE.md` (October 13, 2026), including endpoint inventory, frontend chart mapping, SQL traces and consolidated risks. Source-code and database behaviour must be revalidated if the implementation branches have changed.

---

## Appendix A. Additional Agent Capabilities — Levels 3–5

The following is an additive capability checklist. Existing PRD requirements remain authoritative; overlapping items should be mapped to those requirements rather than interpreted as replacements. POC priorities are specified in Appendix C.

### A.1 Level 3 — Intent-Aware Analytical Execution

1. Natural-language intent understanding
2. KPI semantic understanding and discovery
3. Business entity and dimension resolution
4. Intelligent analytical query planning
5. Multi-metric extraction from user queries
6. Deterministic KPI computation
7. Aggregation, ranking, filtering and sorting
8. Period-over-period comparisons
9. Percentage, variance and growth calculations
10. Contextual follow-up question handling
11. Dashboard filter and selection awareness
12. Structured conversation-state persistence
13. Analytical query validation
14. Read-only tool execution and error recovery
15. Role-based and tenant-scoped data access
16. Data availability and coverage detection
17. Graceful handling of unsupported questions
18. Metric provenance and calculation traceability

### A.2 Level 4 — Context-Aware Analytical Intelligence

1. Structured analytical context assembly
2. Cross-KPI reasoning and correlation analysis
3. Multi-step analytical investigation planning
4. Context-aware root-cause investigation (evidence-based hypotheses, not unsupported causal conclusions)
5. Historical trend interpretation
6. Comparative business performance analysis
7. Adaptive analytical clarification
8. Business-context-aware reasoning
9. Multi-turn analytical memory and continuity
10. Dynamic drilldown and investigation
11. Contextual KPI relationship discovery
12. Data quality and consistency assessment
13. Confidence, uncertainty and coverage awareness
14. Evidence-backed insight generation
15. Business impact assessment
16. Explainable analytical reasoning
17. Alternative hypothesis exploration
18. Context-preserving analytical follow-ups
19. Generative UI composition using AG-UI
20. Dynamic selection of KPI cards, charts, tables and heatmaps
21. Interactive chart-to-conversation synchronization
22. User-role-aware analytical explanations
23. Relevant next-question suggestions
24. Analytical result reuse and caching

### A.3 Level 5 — Proactive Decision Intelligence

1. Automated insight discovery
2. Statistical anomaly detection
3. Proactive KPI monitoring
4. Emerging trend identification
5. Early-warning signal detection
6. Cross-KPI anomaly investigation
7. Intelligent business issue prioritization
8. Impact-based insight ranking
9. Next-best-investigation recommendations
10. Evidence-backed business action recommendations
11. Opportunity and risk identification
12. Historical baseline deviation detection
13. Multi-dimensional performance monitoring
14. Proactive executive insight summaries
15. Automated business performance narratives
16. Insight freshness and relevance validation
17. Duplicate insight detection and suppression
18. Context-aware insight notifications (optional)
19. Insight lifecycle management (new, acknowledged, dismissed, resolved)
20. User feedback-driven insight improvement
21. Recommendation evidence and audit trails
22. Human-governed decision support

## Appendix B. Additional Shared Architectural Capabilities

These requirements apply across intelligence levels rather than representing a separate agent maturity level.

### B.1 Analytics and semantic foundation

1. Centralized KPI semantic registry
2. Metric dependency and relationship graph
3. Deterministic analytics execution engine
4. Read-only analytics tool registry
5. Metric lineage and provenance tracking
6. Query and dataset versioning
7. Data-quality validation
8. Historical baseline management

### B.2 Agent orchestration and intelligence

1. Analytics orchestrator
2. Intent classification and routing
3. Multi-step investigation planner
4. Tool selection and execution governance
5. Structured analytical context management
6. Persistent conversation and investigation state
7. Bounded reasoning and execution
8. Evidence verification before response generation

### B.3 Generative UI and AG-UI

1. AG-UI event-stream integration
2. Declarative UI component registry
3. Dynamic component selection
4. KPI cards and metric groups
5. Interactive tables and charts
6. Evidence and insight cards
7. Warnings and limitation cards
8. Contextual drilldown actions
9. Chart-to-agent context synchronization
10. Agent-to-dashboard filter synchronization
11. Progressive response rendering
12. UI schema validation and safe rendering

### B.4 Reliability, governance and evaluation

1. Role-based and tenant-scoped authorization
2. Read-only data access
3. Deterministic numerical verification
4. Hallucination and unsupported-claim prevention
5. Observation-versus-hypothesis classification
6. Source freshness and coverage checks
7. Tool execution tracing
8. Analytical reasoning observability
9. Golden-dataset evaluation
10. Insight accuracy and relevance evaluation
11. Generative UI correctness testing
12. Latency and performance monitoring

## Appendix C. Recommended POC Priorities

| Priority | Capabilities | Implementation target |
|---|---|---|
| P0 | Level 3 capabilities | Complete |
| P0 | Level 4: context, cross-KPI reasoning, investigation, evidence and generative UI | Complete |
| P1 | Level 4: advanced investigation, alternative hypotheses, business impact and analytical continuity | Complete |
| P1 | Level 5: anomaly detection, insight discovery, prioritization and recommendations | Implement |
| P2 | Level 5: continuous monitoring, notifications, insight lifecycle and feedback-driven improvement | Optional / later phase |

**Target maturity:** Full Level 3, comprehensive Level 4 and selected Level 5 capabilities. The agent should progress from answering KPI questions to investigating business patterns to proactively identifying actionable, evidence-backed insights. All numerical claims must remain grounded in verified data, and operational actions and approvals remain outside this read-only POC.
