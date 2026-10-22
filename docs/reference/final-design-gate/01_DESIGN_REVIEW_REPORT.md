# Cenomi POC — Final Design Gate (GD)

Oct 22, 2026 · @Swaroop Shivakumar

**Recommendation: Conditional Go.** The DX1–DX6 design is coherent and traceable enough to start the engineering specifications (M0), once you decide GDQ-01 to GDQ-05 below. It is not a Go for building the complete POC in five working days: the approved scope is about 165 focused hours against 40–50 available.

**Gate outcome (22 Oct 2026):** Conditional Go to engineering specification planning accepted. GDQ-01 to GDQ-12 recorded as Option A; DXD-80 to DXD-93 approved; DX1–DX6 is the approved design baseline and scope is frozen. Still open: the real ECharts verification (GDQ-06, a mandatory engineering gate), the exact model names and credentials (GDQ-12, configuration), and evaluation scoring (DR-036). Next: the Engineering Specification Plan.

## Recommendation and conditions

Of 141 consolidated decisions, 104 are approved and ready to specify, 7 are approved but still need engineering verification, 23 need your decision (17 of them are proposed defaults you can approve as one batch), 2 are deferred from the first five days and 5 are superseded. Of 70 traced requirements, 46 are fully designed, 13 are designed but await verification, 7 are partial, 3 are left to the specifications and 1 is deferred.

| Condition | Kind | Blocks |
| --- | --- | --- |
| Decide the five-day scope (GDQ-01): a vertical slice in five days, or about 20 working days for the full scope | Decision | Writing the milestone plans |
| Decide how the GenUI registry covers the PRD §7 catalogue (GDQ-02) | Decision | GENERATIVE\_UI.md |
| Decide the route for as-of history (GDQ-03) and confirm the S6/S7 scenario corrections (GDQ-04) | Decision | DATABASE\_SCHEMA.md, SYNTHETIC\_DATA\_STRATEGY.md |
| Reconcile feedback re-ranking (DR-012 with DXD-72, GDQ-05) | Decision | Proactive specification |
| Validate the charts on the real ECharts 5.6.0 runtime (DR-007, DXD-21, DXD-61) | Verification | Final DR-007; the dashboard build (M2), not the specifications |
| Run axe-core and a screen reader on the real build; check AG-UI SDK assumptions | Verification | M2 and M4 exit gates |

**Why not a full Go:** the ECharts runtime could not be loaded from this workspace (the network refused cdnjs and npm), so DR-007 cannot be finalized by me. The verification is a five-minute self-test you can run in the DX3 gallery.

**Why not No-Go:** no contradiction remains that blocks writing specifications. Every cross-phase inconsistency found was either fixed in the design (21 KPI discrepancies, two golden scenarios) or turned into one of the decisions below.

## What was reviewed

The review covered all 31 boards on the design canvas (six interactive prototypes, 25 specification and evidence boards), the G0 planning assessment v0.3, the PRD, the Technical Architecture plan and the Admin/Tenant API Reference. Every figure in this report was recomputed from the prototype data, not copied from earlier boards.

| Phase | What it fixed | Verification evidence | Status |
| --- | --- | --- | --- |
| DX1 | Information architecture: 4 screens, docked panel, 4 overlays; Ink and Violet | Navigation map, screen inventory | Approved |
| DX2 | 12 Admin cards and the Tenant dashboard, states, responsive layouts | 64 of 64 browser checks on all 12 Admin cards | Approved |
| DX3 | Chart parity for 15 V2 visuals; accessibility layer; selection contract | Gallery runs on a test double only; real ECharts 5.6.0 not yet run | Conditionally approved |
| DX4 | Agent workspace, 10 journeys, evidence, history, AG-UI contracts | 77 of 77 browser checks, 211 logic checks | Conditionally approved |
| DX5 | Generative UI: analysis\_result.v1, cenomi.presentation.v1, 15-kind registry, validator | 3,778 logic checks, 45 of 45 browser checks (re-run today) | Approved with refinements |
| DX6 | Proactive intelligence and Insight Inbox, 12 journeys | 44 browser, 81 logic, 387 data, 51 invariant and 13 runner-protocol checks | Conditionally approved, refinements done |

Two small corrections were made during this gate: the DX1 shell now shows the canonical DX6 insights, and the DX5 rejection sample no longer says “overdue”. The DX5 tests were re-run after the change and still pass.

## Findings

Fourteen findings. Five are major, and each now has either a fix in the design or a decision for you; none needs another design phase.

| ID | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| F-01 | Major | KPI values differed between phases: the DX1 shell dated “41 of 71” to 30 Sep, used a share where DX6 used a count, and quoted a Central median of 19% (recomputed: 45.0%). | Fixed. Canonical definition DXD-80; 21 discrepancies resolved; 51 invariant checks pass (KPI tab). |
| F-02 | Major | Two golden scenarios were wrong. S6 assumed no prior-year sales, but the dataset has 2024–2025 and shows the same seasonal dip. S7 counted the company’s 2 service requests for a lease that has none. | Corrected in DX6 v2 (S6 is now a quiet decision, S7 counts the lease’s 2 drawings). Confirm with GDQ-04. |
| F-03 | Major | The DX5 registry (15 kinds) is not the PRD §7 catalogue (15 types). Donut, stacked bar, progress ring, status badge, metric group and drilldown action have no explicit kind. The PRD’s “Distribution → donut or stacked bars” has no composition rule. | GDQ-02. |
| F-04 | Major | The approved scope is about 165 hours; five days give 40–50. | GDQ-01 (Five-day feasibility tab). |
| F-05 | Major · verification | No chart has run on the real ECharts 5.6.0 runtime. Every DX3 and DX5 chart result comes from a test double or HTML stand-ins. | GDQ-06; treemap route GDQ-07. Does not block specifications. |
| F-06 | Medium | DR-012 (G0) says feedback drives deterministic re-ranking; DXD-72 says feedback is only logged for review. | GDQ-05. |
| F-07 | Medium | PRD journey 3 and TA demonstration 3 (do fit-out inspections delay handover?) have no designed journey, although DR-022 lineage supports them. | GDQ-09: specify with existing components. |
| F-08 | Medium | Weekly history for approvals, amendments and vacancy is not a V2 metric; V2 computes these live. | Three new as-of metrics (DXD-80); route GDQ-03. |
| F-09 | Medium | Six capabilities are designed more than once: evidence display, drilldown records, labelled statements, authorization re-checks, version history and stale handling. | One shared component or service each (Architecture tab). |
| F-10 | Low | DXD-02 has a notifications overlay; DX6 sends the bell straight to the inbox. | GDQ-08. |
| F-11 | Low | The DX1 screen inventory lists the inbox for admins only; DX6 gives tenants an own-lease inbox (DXQ-16 A). | Superseded by DXD-79; PRODUCT\_SPEC records it. |
| F-12 | Low | DX2 drilldown records are generated fixtures with random ages and malls, not the seeded population. | M2 builds records from the seed (DXD-49, discrepancy C21). |
| F-13 | Low | Clarification (L4-CLAR) and business-impact reasoning (L4-BIZ) are only partly designed. | Specified in AGENT\_ARCHITECTURE; no new screens. |
| F-14 | Verification | axe-core and screen-reader runs, and the AG-UI SDK assumptions in DXD-40, are still unverified. | M2 and M4 exit gates; optional spike GDQ-11. |

## Decisions needed from you

Twelve decisions. GDQ-01 to GDQ-05 change what the specifications contain and are needed before M0 writing starts; the rest can follow during M0. Pick a value in the last column, or comment on a row.

| ID | Decision | Options | Recommendation and reason | Needed before | Your decision |
| --- | --- | --- | --- | --- | --- |
| GDQ-01 | Five-day scope | A: five days deliver an end-to-end vertical slice; full scope follows in phases (about 20 working days in total). B: keep five days and cut to the slice permanently. C: two developers in parallel (about 10–12 working days for full scope). | A. The slice proves every architectural seam; nothing approved is dropped. | Milestone plans | Option A (recommended) |
| GDQ-02 | PRD §7 catalogue vs DX5 registry | A: map each PRD type to a DX5 kind, and add donut and stacked-bar variants to bar and a progress variant to KPI, reusing the DX3 primitives (about 2 h). B: keep the DX5 registry and record the deviation. | A. Restores PRD parity and the “Distribution” composition at little cost. | GENERATIVE\_UI.md | Option A (recommended) |
| GDQ-03 | As-of history route | A: the seed generator writes a metric\_snapshot table from its own lifecycle events, plus a test that it equals the parity metric at as\_of. B: generic as-of SQL over status-history tables. | A. Far less SQL; the invariants still prove consistency. | DATABASE\_SCHEMA.md | Option A (recommended) |
| GDQ-04 | Scenario corrections and tenant Watch | A: accept the S6/S7 corrections; test the tenant Watch path with a labelled micro-fixture. B: seed a genuine own-lease anomaly for T-31206 in the macro data. | A. Keeps the seasonal counterexample honest. | SYNTHETIC\_DATA\_STRATEGY.md | Option A (recommended) |
| GDQ-05 | Feedback re-ranking | A: deterministic per-user ordering within a band after repeated “not useful”; never hides a P1, never changes thresholds; secondary in five days. B: drop re-ranking; feedback is for review only. | A. Satisfies DR-012 without automatic tuning. | Proactive specification | Option A (recommended) |
| GDQ-06 | ECharts verification | A: you run the DX3 gallery self-test in Play and paste the result. B: allow cdnjs.cloudflare.com and registry.npmjs.org for my sessions. C: attach echarts 5.6.0 and axe-core files. | A now, B for repeatable runs. | Final DR-007 (before M2) | Option A (recommended) |
| GDQ-07 | Treemap implementation | A: the custom squarified HTML treemap for both treemaps. B: ECharts treemap if the self-test meets the thresholds. | A. Removes the one medium-risk chart from the five-day path. | M2 plan | Option A (recommended) |
| GDQ-08 | Notifications surface | A: the bell opens the inbox filtered to new; no separate overlay. B: keep the DXD-02 overlay. | A. One surface fewer. | PRODUCT\_SPEC.md | Option A (recommended) |
| GDQ-09 | Linked fit-out cohort journey | A: specify it with existing kinds (comparison, table, trend) and the fitout\_handover\_delay scenario; no design addendum. B: a short design addendum first. | A. No new component is needed. | AGENT\_TOOLS.md | Option A (recommended) |
| GDQ-10 | Proposed defaults | A: approve all 17 proposed defaults as one batch (DR-004, 008, 018b, 021, 023, 024 Arabic storage, 027–030, 037, 042–044, 046, 047, DXD-22). B: review one by one. | A. Every design already assumes them. | M0 start | Option A (recommended) |
| GDQ-11 | AG-UI spike (DR-038) | A: a throwaway 2–3 h spike in M0 against the pinned SDK. B: no spike; verify in M4. | A. Protocol drift is cheaper to find before M4. | AGUI\_INTEGRATION.md | Option A (recommended) |
| GDQ-12 | Model provider and API key (DR-015) | A: name the provider and two candidate models; key available for M3. B: decide in M3. | A. Agent latency and grounding depend on it. | Agent runtime plan | Option A (recommended) |

## Final Design Gate approval checklist

Tick each item when you accept it. The gate is approved when every “before M0” item is ticked; verification items are carried into the build gates.

**Before M0 specifications start**

- [ ] Recommendation accepted: Conditional Go to M0 specifications
- [ ] Consolidated register accepted: 104 ready, 7 verification pending, 2 deferred, 5 superseded (Decision register tab)
- [ ] DX6 refinement records DXD-80…93 confirmed (privacy, run identity, recovery, detector quality, priorities)
- [x] GDQ-01 five-day scope decided
- [x] GDQ-02 GenUI catalogue mapping decided
- [x] GDQ-03 as-of history route decided
- [x] GDQ-04 S6/S7 corrections confirmed
- [x] GDQ-05 feedback re-ranking decided
- [x] GDQ-10 proposed defaults approved as a batch
- [ ] Traceability accepted: 46 designed, 13 verification pending, 7 partial, 3 specification-only, 1 deferred (Traceability tab)
- [ ] KPI and data reconciliation accepted: canonical figures, 21 discrepancies resolved, invariants GI-01…16 (KPI tab)
- [ ] Specification inventory and writing order accepted (Specification inventory tab)

**During M0 (not blocking its start)**

- [ ] GDQ-06 ECharts self-test result pasted, or egress allowed; DR-007 finalized
- [x] GDQ-07, GDQ-08, GDQ-09 decided
- [ ] GDQ-11 spike approved or declined; GDQ-12 provider and key named
- [ ] Open issues I-01…I-12 assigned to their gates (Open issues tab)

**Carried into build gates**

- [ ] M2 exit: all charts on ECharts 5.6.0 (or the treemap fallback), axe-core clean, screen-reader pass on the Admin dashboard
- [ ] M4 exit: AG-UI events verified on the pinned SDK; GenUI charts on the real runtime
- [ ] M5 and M6 exits: golden scenarios S1–S9 and N1–N11, invariants and replay hash reproduced on the seeded database
