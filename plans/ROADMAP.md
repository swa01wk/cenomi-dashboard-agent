# ROADMAP — approved Engineering Specification Plan

| | |
|---|---|
| Document code | RMAP (requirement IDs `RMAP-Rnnn`) |
| Version | **1.0 · approved 2026-10-22** · introduced by PR-M0 |
| Approved from | Engineering Specification Plan draft of 22 Oct 2026 (13 tabs), preserved unchanged in `plans/proposed/engineering-specification-plan/` |
| Approval | Project owner, 2026-10-22, "subject to the refinements" of the approval message. The refinements are recorded as amendments A-01 to A-18 (§2). The owner's review of PR #2 (2026-10-22, 21:04 IST) added refinements A-19 to A-24 |
| Holds | Scope and structure of the engineering programme: milestones, dependencies, contract freezes, deliverables, feature-card standard, exit-gate framework, slice classification, specification inventory, timeline |
| Does not hold | Progress (only `plans/STATUS.md`); decisions (only `docs/adr/` and `docs/design/DECISION_REGISTER.md`); task cards (milestone plans) |

---

## 1. Approval record and provenance

**RMAP-R001** The 22 Oct 2026 ESP draft is approved. Where this document and the draft differ, this document wins and the difference is listed in §2. The draft is never edited; it is the provenance record.

**RMAP-R002** The approval preserves:
- the complete DX1–DX6 scope;
- the Final Design Gate decisions;
- the canonical KPI semantic architecture and the single metric service shared by dashboards, the agent and detectors;
- deterministic calculation;
- evidence-grounded answers;
- AG-UI transport with declarative generative UI;
- deterministic proactive intelligence;
- milestones M0–M6;
- the five-day integrated vertical slice;
- the full-scope roadmap;
- the 17 specification documents, the 10 plan files, the ADRs, the machine-readable contracts and the milestone gates.

**Decisions approved on 2026-10-22 together with this plan:**

| Decision | Option approved |
|---|---|
| ED-01 | A (ADR-0001) |
| ED-02 | A (ADR-0005) |
| ED-04 | A (ADR-0002) |
| ED-05 | A (ADR-0015) |
| ED-06 | A (ADR-0015) |
| D-01 | A (ADR-0006) |
| ED-03 | A, approved earlier the same day; scope unchanged |
| DR-035 | Superseded by ADR-0001 |
| ED-07 | A, approved later on 2026-10-22 (ADR-0016) |
| ED-08 | A, approved later on 2026-10-22 (ADR-0017) |
| ED-09 | A, approved later on 2026-10-22 (ADR-0018) |

**Not approved, and not decided by this plan:**

| Item | Needed before |
|---|---|
| ED-10 | PR-M4 |
| ED-11 / DR-036 | PR-M5 |
| GDQ-12 configuration | Slice day 3; the M0-T09 latency sample |

Their current status lives only in `plans/STATUS.md`.

---

## 2. Amendments to the proposed plan

| ID | Amendment | Source | Where it lives now |
|---|---|---|---|
| A-01 | **Delivery model.** Specification → feature branch → implementation → local checks → PR → CI → review → merge → integrated verification → milestone exit gate. A feature is done only when its acceptance tests pass; a milestone only when its gate passes on the merged commit and the owner approves the report | Approval Part 4 | ADR-0015; §6, §7 |
| A-02 | **Makefile contract.** The root Makefile is the single developer and CI interface. The approved target list replaces the ESP tab 11 command table, mapped in DEVELOPMENT_ENVIRONMENT §5.4 | Approval Part 6 | `specs/engineering/make_targets.yaml`; DEVENV §5 |
| A-03 | **CI architecture.** Three workflows (`ci.yml`, `milestone-gate.yml`, `eval-live.yml`). One aggregating required check `ci/summary`. Path-aware jobs that never skip shared-contract consumers. Replaces the ESP tab 11 CI table | Approval Part 8 | `specs/engineering/ci_checks.yaml`; DEVENV §7 |
| A-04 | **Testing strategy and traceability defined in M0.** The ESP gave the test taxonomy to `EVALUATION_PLAN.md` (PR-M5); it moves to ARCHITECTURE §10 and §12, because every M0 card needs test IDs. EVALUATION_PLAN keeps benchmark composition, scoring, thresholds and the performance method (gap G-2) | Approval Parts 7, 11; restoration G-2 | ARCHITECTURE §10, §12; `specs/traceability/id_conventions.yaml` |
| A-05 | **Web application architecture** (routes, layouts, data fetching, client state ownership, authentication boundary, deep links, inspector integration, responsive structure) defined in ARCHITECTURE (gap G-3) | Restoration G-3 | ARCHITECTURE §6 |
| A-06 | **Snapshot schema decided in M0, not PR-M1.** `snap` (D-01), because M0-T02 creates the schemas and grants (gap G-1) | D-01; restoration G-1 | ADR-0006 |
| A-07 | **`agent` and `insights` tables are no longer M1 deliverables.** M0 creates the empty schemas; PR-M3 and PR-M6 specify their tables and amend DATABASE_SCHEMA; M3 and the M6 slice part migrate them. Amends the ESP tab 3 M1 deliverable "migrations for … agent and insights schemas" (gap G-4) | Restoration G-4 | ADR-0006 §1 |
| A-08 | **Ownership of the thread, history, run and runtime-limit contracts** made explicit (gap G-5); see the table after this one | Restoration G-5 | This section (table below); seams in ARCHITECTURE §8.1–§8.2 |
| A-09 | **Properties card values in the slice.** The slice keeps the Properties card. PR-M1 must define every value the V2 card shows: mall count, unit count, occupied and vacant units, occupied and vacant GLA, and the unit occupancy share (PRD §4.1; PA v0.3 §7.6). The slice metric list therefore reads "the six named metrics plus the Properties card's portfolio metrics". Effort +1 h on slice day 2. No value is dropped (gap G-6) | Restoration G-6 | §8; PR-M1 |
| A-10 | **Tenant action terminology.** PR-M1 fixes `tenant_action_items.open` so that T-202's "2 fit-out drawings to upload" (Lighting layout since 12 Oct; Shopfront details re-upload since 17 Oct) is the same population as the tenant card's "2 documents to upload" for lease T-31206, with 0 service requests in Action required (the company has 2). Corrected S7 and DXD-93 are preserved (gap G-7) | Restoration G-7 | PR-M1 (KPI YAML, scenario manifest) |
| A-11 | **ADR-0015** added for the delivery workflow, ED-05 and ED-06. Numbered after the reserved 0007–0014 range | Approval Part 3 | `docs/adr/` |
| A-12 | **Two machine-readable folders** added: `specs/engineering/` (make targets, CI checks, specification-set version) and `specs/traceability/` (ID conventions) | Approval Parts 6, 8, 11 | ADR-0002 |
| A-13 | **AG-UI 1.0 correction.** ESP tab 8 claims 1.0 adds `outcome: "cancelled"`. The 1.0 documentation checked on 2026-10-22 lists only `success` and `interrupt` outcomes. The DX4 mapping of Stop to `RUN_ERROR` code `CANCELLED` is unaffected. The spike adds checks A9–A14 | ADR-0003 §3 | ARCHITECTURE §8.4; M0-T09 |
| A-14 | **M0 task cards revised.** M0-T01 includes the full Makefile contract. M0-T10 adds `specs-check`, `trace-report` and the register renderer. **M0-T11 is new** (test harness and CI reporting). M0 build estimate rises from about 9 h to about 14 h | Approval Parts 6–11 | `plans/M0_FOUNDATION.md`; §10 |
| A-15 | **Feature (task card) standard** of 20 fields applies to every milestone plan | Approval Part 4 | §6 |
| A-16 | **Delivery class** on every card: `slice`, `full` or `deferred` | ED-04 A; approval Part 3 | ADR-0002 §4; §8 |
| A-17 | **CF-0 contents** made exact: error envelope, error code registry, principal, scope decision, health report, dataset descriptor, the engineering specs and the ID conventions | M0 authoring | §3.2 |
| A-18 | **Universal exit-gate criteria UG-01 to UG-20** with a per-milestone applicability matrix | Approval Part 10 | §7 |
| A-19 | **CI fails closed.** Only `success` passes. Timeouts, cancellations and missing results fail. A skip is accepted only for a job that is not applicable, as recomputed independently. Unclassified files and any shared-contract change run every job | PR #2 review, item 1 | `ci_checks.yaml` (`ci/changes`, `ci/summary` rules); DEVENV-R020, R047–R050 |
| A-20 | **Result vocabulary** PASSED, FAILED, NOT_APPLICABLE, NOT_IMPLEMENTED, SKIPPED, with three applicability rules, a build window for NOT_IMPLEMENTED, card completion by `trace-report CARD=…`, and gate enforcement of the whole completed scope including regression. Replaces the single "N/A" status | PR #2 review, item 2 | ARCHITECTURE §10.8 (ARCH-R101–R105); DEVENV-R013; `make_targets.yaml` conventions |
| A-21 | **Branch protection is an M0 implementation requirement.** It is applied in two stages: P1 before the first implementation PR merges, P2 (`ci/summary` required) once M0-T07 merges. Exceptions are recorded as `EXC-nnn`; EXC-001 (pre-CI bootstrap cards) was proposed here and approved conditionally (A-26). Required approving reviews are set to 0 because PRs are authored under the owner's account; the owner's merge is the approval | PR #2 review, item 3 | DEVENV §8.4, R039, R051; ADR-0015 §5; `plans/M0_FOUNDATION.md` §3, §8 |
| A-22 | **Milestone evidence** is a machine-checked report validated against the `gateReport` schema. It holds the merged SHA, the approved spec-set version, dataset and fixture versions, required CI results, results per suite, blocking defects, approved exceptions, deferred items and the owner's approval | PR #2 review, item 4 | RMAP-R010; `specs/engineering/engineering.schema.json` (`gateReport`) |
| A-23 | **Run outcomes versus transport events.** The application lifecycle is separated from AG-UI transport, with normative semantics for completion, cancellation, approval interruption, disconnection, tool failure, retry and resume. The spike gates every dependent CF-3 and CF-4 freeze | PR #2 review, item 5 | ARCHITECTURE §8.6 (ARCH-R106, R107), ARCH-R108; RMAP-R015 |
| A-24 | **Exact proposed Option A definitions** for ED-07, ED-08 and ED-09, for owner approval. Their status stays Proposed (superseded by A-25) | PR #2 review, item 6 | DECISION_REGISTER §5.1 |
| A-25 | **ED-07, ED-08 and ED-09 approved (Option A)** with the owner's added requirements: production fails closed and grants are always enforced on the backend (ED-07); a missing recording fails and never triggers a live call (ED-08); the Ink & Violet design is preserved (ED-09). AT-M0-T06-02 and AT-M0-T07-05 are extended to verify them | Owner approval, 2026-10-22 | DECISION_REGISTER §5.1; ADR-0016, ADR-0017, ADR-0018; `plans/M0_FOUNDATION.md` |
| A-26 | **P1/P2 protection policy approved** with 0 required approving reviews; **EXC-001 approved conditionally** with conditions C1–C7, including retroactive GitHub Actions verification before the M0 exit gate. The condition C4 investigation is recorded | Owner approval, 2026-10-22 | DEVENV §8.4; `plans/M0_FOUNDATION.md` §3, GATE-M0-10; STATUS (EXC-001 log) |

**Ownership established by A-08 (gap G-5):**

| Contract or behaviour | Normative home | Specified in | Built in |
|---|---|---|---|
| Thread and conversation REST (list, open, rename, delete, history, resume, re-run with current data) | AGENT_ARCHITECTURE.md (semantics) + `specs/contracts/thread*.v1` + API_CONTRACTS.md route table | PR-M3 | M3 (API), M4 (UI) |
| Run management: start (AG-UI endpoint), cancel, event replay `GET …/events?after=` | AGUI_INTEGRATION.md + `specs/contracts/run*.v1` (paths in DX4-AGUI are proposals) | PR-M4; run lifecycle semantics in PR-M3 | M3 runtime, M4 transport |
| Tool execution budgets, plan limits, deadlines | AGENT_ARCHITECTURE.md (values) + `.env.example` names in DEVENV (no values restated) | PR-M3 | M3 |
| Cancellation, retry kinds, recovery, versioned answers | AGENT_ARCHITECTURE.md (runtime) + AGUI_INTEGRATION.md (wire) | PR-M3 + PR-M4 | M3, M4 |
| Agent-to-frontend state synchronization (STATE_*, frontend tool `propose_dashboard_filters`) | AGUI_INTEGRATION.md | PR-M4 | M4 |
| REST conventions, error envelope, pagination, idempotency keys | ARCHITECTURE.md §5.4 + `specs/contracts/error_*` | **PR-M0** | M0 |

---

## 3. Milestones, dependencies and contract freezes

### 3.1 Dependency graph (unchanged from ESP tab 1)

```
M0 Foundation ─CF-1→ M1 Data ─CF-2→ M2 Metrics & dashboards ─CF-3→ M3 Agent runtime ─CF-4→ M4 AG-UI & GenUI ─CF-6→ M5 Evaluation ─CF-5→ M6 Proactive intelligence
```

**RMAP-R003** Each arrow is passable only when both hold:
- the previous milestone's exit gate has passed and the owner has approved its report;
- the named contract freeze is approved.

**RMAP-R004** Specification-writing order is **M0 → M1 → M2 → M3 → M4 → M6 → M5**. Implementation dependency is **M0 → M1 → M2 → M3 → M4 → M5 → M6**. The **complete M6 is implemented only after the M5 gate** (DR-010).

The thin M6 slice part may be built earlier because it depends only on the M2 snapshots and M4 insight rendering:
- D2 and D8;
- manual replay;
- inbox list, detail and acknowledge;
- the `insights` tables it needs.

**RMAP-R005** Specification readiness never authorizes implementation. Each milestone's build needs the owner's explicit authorization after its specification PR merges (ADR-0015 §3).

### 3.2 Contract freezes

| Freeze | Frozen by | Contracts |
|---|---|---|
| CF-0 Toolchain | PR-M0 | Repository layout; `error_envelope.v1` and `error_codes.v1`; `principal.v1`; `scope_decision.v1` (AccessScope interface, deny by default); `health_report.v1`; `dataset_descriptor.v1`; codegen pipeline and JSON Schema subset (ADR-0004); `specs/engineering/*`; `specs/traceability/id_conventions.yaml`; CI check names |
| CF-1 Data | PR-M1 | Tables, enums, roles' table grants for `core`, `meta`, `snap`, `seed_meta`; metric YAML; permissions matrix; scenario manifest; canonical figures |
| CF-2 Analytics | PR-M2 | Metric query, `analysis_result.v1`, card view-models, records paging, `selection_ref.v1`, design tokens |
| CF-3 Agent | PR-M3 | AnalysisPlan, tool schemas, AnswerDraft, fact tokens, evidence envelope, LLM adapter interface, thread and run identity contracts, `agent` tables, evaluation case schema v1. Elements that depend on the AG-UI spike freeze only after its report (RMAP-R015) |
| CF-4 Presentation | PR-M4 | `cenomi.presentation.v1` and per-kind schemas, composition policy, AG-UI event mapping and state shape, run-management endpoints. Requires the merged spike report (RMAP-R015) |
| CF-5 Insights | PR-M6 | `insight.v1`, detector configuration schema, runner protocol, inbox API, `insights` tables |
| CF-6 Evaluation | PR-M5 | Benchmark composition and scoring (needs DR-036) |

CF-5 is frozen before CF-6; the reason is unchanged from the ESP.

### 3.3 What may run concurrently

ESP tab 1 "Concurrency and contract blocking" stands unchanged. One addition: after CF-0, the M0 build (if authorized) may run while PR-M1 is being written.

---

## 4. Repository structure

**RMAP-R006** The approved structure is the ESP tab 5 tree with these additions and clarifications:

```text
.github/
  workflows/ci.yml · milestone-gate.yml · eval-live.yml      (M0-T07; ADR-0015)
  actions/setup/action.yml                                    (shared toolchain setup)
  pull_request_template.md · ISSUE_TEMPLATE/defect.yml        (M0-T10)
specs/
  engineering/ make_targets.yaml · ci_checks.yaml · spec_set.yaml · engineering.schema.json
  traceability/ id_conventions.yaml
  contracts/   error_envelope.v1 · error_codes.v1.yaml · principal.v1 · scope_decision.v1 ·
               health_report.v1 · dataset_descriptor.v1  (.schema.json)
infra/postgres/bootstrap/roles.sql                           (roles only; schemas are Alembic)
backend/migrations/                                          (Alembic, linear history)
tests/reports/                                               (git-ignored; CI artefacts)
```

Ownership rules (ESP tab 5) stand.

---

## 5. Milestone deliverables matrix (M0–M6)

Each cell names deliverables, not task cards; cards are written in each milestone plan. "—" means nothing in that area for that milestone. The **slice** marker shows what the five-day slice needs from the milestone.

### M0 — Foundation

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | Role bootstrap; Alembic framework; baseline migration creating six empty schemas with grants and default privileges; DB safety guards | slice |
| Backend services and APIs | `cenomi` package with 12 module skeletons and import-linter contracts; settings; JSON logging; OpenTelemetry; request references; error envelope; `/api/v1/health`, `/api/v1/health/live`, `/api/v1/me`, `/api/v1/dataset`, dev sign-in/out (ED-07 pending) | slice |
| Frontend application | Next.js shell: rail, top bar, synthetic banner with as-of, persona-aware navigation, route skeletons per ARCHITECTURE §6, `/api` and `/agui` rewrites, TanStack Query client | slice |
| Agent runtime and analytical tools | Interface boundaries only (ARCHITECTURE §8). No agent code | — |
| AG-UI and generative UI | Throwaway AG-UI spike and report (A1–A14). No product code | full (pre-slice) |
| Proactive intelligence | — | — |
| Automated testing | pytest, Vitest and Playwright harnesses; trace markers; JUnit and trace reports; shell smoke E2E; DB grant tests; contract tests | slice |
| Developer tooling | Root Makefile (full target contract); uv and pnpm workspaces; lockfiles; `make doctor`; `.env.example`; Compose | slice |
| CI/CD | `ci.yml` with all jobs and fail-closed `ci/summary` (targets not yet due report NOT_APPLICABLE or NOT_IMPLEMENTED per ARCHITECTURE §10.8); `milestone-gate.yml`; `eval-live.yml` skeleton; security scans; image builds without push; ECharts gate harness | slice |
| Documentation and contracts | PR-M0 items 1–12; CF-0 schemas; AGENTS.md; Cursor rules; PR and defect templates | slice |

### M1 — Database and synthetic data

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | `core`, `meta`, `snap`, `seed_meta` tables, enums, constraints and indexes; migration ordering; deterministic generator (latent model, lifecycles, S1–S9, N1–N11, TA §5.3 mapping, cohorts, exposing rows for the eight caveats); frozen clock (`as_of`); snapshots; `ingested_at`; seed hash; reconciliation | slice (Central, S1/S2/S4, T-31206, weekly approval snapshots) |
| Backend services and APIs | Data-access layer (engines per role); `meta` dataset descriptor replaces the config source; read-only reader sessions | slice |
| Frontend application | — | — |
| Agent runtime and analytical tools | Analytical data contracts later milestones depend on: entity identifiers, lineage keys (DR-022), coverage inputs, `ingested_at` | slice |
| AG-UI and generative UI | — | — |
| Proactive intelligence | Snapshot series consumed by D2 (weekly approvals) and the D8 lease-scoped action items | slice |
| Automated testing | Fresh-migration test; FK and constraint tests; determinism (two resets, same hash); GI-01…16 (51 checks); canonical figures; snapshot = parity at `as_of`; grant tests; frozen-clock and timezone boundary tests; property tests for generators | slice (Central subset) |
| Developer tooling | `make seed`, `seed-reset`, `seed-verify` active; `make seed SCOPE=slice` | slice |
| CI/CD | `ci/database` job active with Postgres service, seed and verify | slice |
| Documentation and contracts | PR-M1: DATABASE_SCHEMA, metric YAML (including the Properties set, A-09), KPI_CATALOG, permissions.yaml, SYNTHETIC_DATA_STRATEGY, scenarios, canonical figures, micro-fixture specs, ADR-0007/0008/0012, M1 plan | slice |

### M2 — KPI semantic layer and dashboards

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | Indexes justified by metric queries (EXPLAIN evidence) | slice (slice metrics) |
| Backend services and APIs | Registry loader and validator; SQL templates with scope fragment and `as_of`; executor (coverage, calculation records, content-addressed datasets, result cache by scope and data version); metric query, card view-model, filter-option and records endpoints | slice (6 metrics + Properties set) |
| Frontend application | Admin dashboard (12 cards); tenant dashboard groups; card focus (Chart, Table, Records, Definition); viz primitives; squarified treemap (GDQ-07); state vocabulary; responsive layouts | slice (4 admin cards, tenant Action required) |
| Agent runtime and analytical tools | — (tools consume the executor in M3) | — |
| AG-UI and generative UI | `selection_ref.v1` emitted by every selectable chart | slice |
| Proactive intelligence | — | — |
| Automated testing | Golden metric tests (T0/T1); card total = records total; parity caveat tests; scope-tampering; empty scope = empty result; component tests per state; Playwright card journeys E2E-CARD-*; axe-core | slice (slice cards) |
| Developer tooling | `make backend-test` covers KPI golden tests | slice |
| CI/CD | `ci/echarts-gate` becomes blocking; frontend build and E2E jobs active | slice |
| Documentation and contracts | PR-M2: API_CONTRACTS, DESIGN_SYSTEM + tokens (ED-09), card specs, ADR-0011, M2 plan | slice |

### M3 — Agent runtime and analytics

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | `agent` schema tables (threads, runs, run events, answer versions, facts, datasets, analytical state) | slice (subset needed by linear runs) |
| Backend services and APIs | Thread and history REST (A-08); run lifecycle service; cancellation | slice (no history and resume) |
| Frontend application | — (agent UI in M4) | — |
| Agent runtime and analytical tools | LLM adapter (primary, fallback, mock, replay); state machine; planner; plan validator; DAG executor with budgets and ≤ 1 re-plan; all tools including `get_linked_cohort` (GDQ-09); fact extraction; synthesizer; verifier; clarification policy (OI-07); unavailable concepts; analytical state; immutable versions; run ledger | slice (linear ≤ 3 steps, 5 tools, verifier) |
| AG-UI and generative UI | Internal run events for M4 | slice |
| Proactive intelligence | Evidence envelope and verifier reused by M6 | slice |
| Automated testing | Transition table tests; tool golden examples; mock-model tests (E); replay tests J1–J10 at API level; adversarial verifier; prompt-injection-as-data; secret-scan of logs and events (OI-10); 20 slice cases | slice (20 cases) |
| Developer tooling | `agent-test-mock`, `agent-test-replay` active; `agent-test-live` guarded | slice |
| CI/CD | `ci/agent` active; `eval-live.yml` usable (needs GDQ-12 config and the protected environment) | slice |
| Documentation and contracts | PR-M3: AGENT_ARCHITECTURE, AGENT_TOOLS, evaluation case schema v1 + 20 questions, ADR-0009, DATABASE_SCHEMA amendment, M3 plan | slice |

### M4 — AG-UI and generative UI

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | — | — |
| Backend services and APIs | AG-UI run endpoint (ED-10 pin), event mapping, cancel, replay endpoint; presentation composer; server validator | slice |
| Frontend application | Agent panel; analytical workspace; inspector (Evidence, Definition, Records, Execution); EvidencePanel, StatementList, RecordsTable; View as; filter-proposal confirm and undo; reconnect | slice (panel, 5 kinds, no workspace) |
| Agent runtime and analytical tools | Frontend tool `propose_dashboard_filters` | full |
| AG-UI and generative UI | Registry of 15 kinds + GDQ-02 variants; composition policy P1–P6; client zod validation; table fallback | slice (kpi, bar, table, insight, unavailable) |
| Proactive intelligence | `insight` kind rendering | slice |
| Automated testing | Event-fixture contract tests against both SDKs; reducer, dedupe, cancel, reconnect, retry, idempotent submit; per-kind renderer and XSS tests; Playwright J1–J10 and DX5 journeys; axe-core | slice (E2E-S1) |
| Developer tooling | `integration-test` covers AG-UI | slice |
| CI/CD | `ci/integration` and `ci/e2e` cover AG-UI and GenUI | slice |
| Documentation and contracts | PR-M4: AGUI_INTEGRATION, GENERATIVE_UI, ADR-0010, M4 plan | slice |

### M5 — Evaluation and reliability

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | Invariants and replay hash re-run as regression | — |
| Backend services and APIs | Performance instrumentation for NFR-01 | — |
| Frontend application | Accessibility remediation from axe and screen-reader runs | — |
| Agent runtime and analytical tools | Benchmark harness (replay and live); scoring per DR-036; cost and token accounting | slice (20 cases on replay only) |
| AG-UI and generative UI | Protocol and GenUI regression suites | — |
| Proactive intelligence | — (M6 after this gate) | — |
| Automated testing | ≥ 150 cases (EVAL-01–06); KPI accuracy; grounding; cross-KPI; authorization; missing data; AG-UI protocol; GenUI validation; performance and reliability; recovery; Playwright regression suite | — |
| Developer tooling | Evaluation reports; `make agent-test-live` with budgets | — |
| CI/CD | Replay benchmark as a regression job; CI evaluation report; live workflow reporting | — |
| Documentation and contracts | PR-M5: EVALUATION_PLAN, benchmark, ADR-0014 + M5 plan | — |

### M6 — Proactive intelligence

| Area | Deliverables | Slice |
|---|---|---|
| Database and data engineering | `insights` schema tables | slice (subset for D2/D8) |
| Backend services and APIs | Evaluation runner (run_key, claims, staging, atomic publish, outbox); event triggers; inbox API; notification badge; investigate handoff; shared summaries; feedback; snooze; digest | slice (manual replay, list, detail, acknowledge) |
| Frontend application | Insight Inbox (bell opens it filtered to new, GDQ-08); detail with evidence; lifecycle actions; tenant own-lease inbox; card indicators | slice (list, detail, acknowledge) |
| Agent runtime and analytical tools | Insight tools; investigation into a private thread | full |
| AG-UI and generative UI | Insight kind in threads | slice |
| Proactive intelligence | D1–D8 (detectors-1.1); scoring; dedup and suppression; Watch promotion; lifecycle; privacy re-checks; feedback ordering (GDQ-05) | slice (D2, D8) |
| Automated testing | Detector micro-series; slice and full replay goldens; S1–S9 fire, N1–N11 quiet; runner tests R1–R13; K1–K12; privacy and role-change; concurrency and idempotency | slice (INS-101, T-202, slice hash) |
| Developer tooling | `make replay` | slice |
| CI/CD | Replay golden in `ci/integration`; full replay in the milestone gate | slice |
| Documentation and contracts | PR-M6: PROACTIVE_INTELLIGENCE, detectors-1.1 + insight.v1, fixtures, ADR-0013, M6 plan + SLICE_FIVE_DAY | slice |

---

## 6. Feature (task card) standard

**RMAP-R007** Every task card in every milestone plan has these 20 fields, in this order. A field that does not apply says **N/A** with a one-line reason; nothing is invented to fill it.

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | `M<n>-T<nn>` (the task card ID) |
| 2 | Requirement references | Product requirement IDs, spec requirement IDs (`XXX-Rnnn`), decision IDs, design journey IDs |
| 3 | Owning milestone | M0–M6 |
| 4 | Objective | Business or technical outcome, one or two sentences |
| 5 | Scope and exclusions | In scope; explicitly out of scope |
| 6 | Dependencies | Cards, contract freezes, decisions and configuration it needs |
| 7 | Backend deliverables | Modules, routes, commands |
| 8 | Frontend deliverables | Routes, components |
| 9 | Agent deliverables | Runtime, tools, prompts |
| 10 | Database and data requirements | Schemas, tables, migrations, fixtures |
| 11 | Interfaces and contracts | `specs/contracts/*` and spec sections it implements |
| 12 | Implementation tasks | Ordered steps |
| 13 | File and module ownership | Paths it creates or changes; anything outside requires stopping and reporting |
| 14 | Test cases | Test files and the AT IDs they carry |
| 15 | Acceptance criteria | `AT-M<n>-T<nn>-<kk>` statements, each verifiable by an automated test unless marked *manual* with a reason |
| 16 | Failure and recovery scenarios | What can fail and the required behaviour |
| 17 | Security requirements | Authorization, secrets, input handling |
| 18 | Observability requirements | Logs, metrics, traces it must emit |
| 19 | Delivery class | `slice`, `full` or `deferred` (ADR-0002 §4) |
| 20 | Completion gate | The checklist that marks the card done |

**RMAP-R008** A card fits one Composer session and one PR. If implementation reveals the card cannot be completed within its file ownership and scope, Composer stops and reports; it never widens the card (ESP tab 12; R-09).

---

## 7. Milestone exit-gate framework

### 7.1 Universal criteria

**RMAP-R009** A milestone is complete only when all three hold:
- its required task cards are merged;
- its gate checks pass on the **integrated merged commit** of `main`;
- the owner approves its milestone verification report.

A PR passing CI is never sufficient on its own.

| ID | Universal criterion |
|---|---|
| UG-01 | Required task cards implemented and merged; each traceable to its PR |
| UG-02 | Approved contracts for the milestone are satisfied (schemas equal, drift check clean) |
| UG-03 | Backend checks pass |
| UG-04 | Frontend checks pass |
| UG-05 | Agent checks pass |
| UG-06 | Relevant Playwright journeys pass |
| UG-07 | Database invariants pass |
| UG-08 | KPI parity maintained |
| UG-09 | Authorization requirements pass |
| UG-10 | Security checks pass (secrets, dependency audit, licences) |
| UG-11 | Evidence verification requirements pass |
| UG-12 | Reliability and recovery tests pass |
| UG-13 | Required observability is available (fields, correlation, traces) |
| UG-14 | No unresolved blocking defect (`DEF-` issue labelled `blocking`) |
| UG-15 | Documentation and ADRs current |
| UG-16 | `plans/STATUS.md` reflects the actual state |
| UG-17 | Every acceptance test ID of the cards of M0…M<n> is `PASSED` (`make trace-report GATE=M<n>`). An AT that is FAILED, NOT_IMPLEMENTED or SKIPPED fails the gate (ARCH-R105) |
| UG-18 | Required CI evidence archived (milestone-gate workflow artefacts) |
| UG-19 | Deferred items explicitly listed with their target milestone |
| UG-20 | Milestone verification report approved by the owner |

### 7.2 Applicability

A = applies. — = not applicable because the subsystem does not exist yet; the check is then not required.

| | M0 | M1 | M2 | M3 | M4 | M5 | M6 |
|---|---|---|---|---|---|---|---|
| UG-01, 02, 03, 10, 13–20 | A | A | A | A | A | A | A |
| UG-04 Frontend | A (shell) | — | A | — | A | A | A |
| UG-05 Agent | — | — | — | A | A | A | A |
| UG-06 Playwright | A (shell smoke) | — | A | — | A | A | A |
| UG-07 DB invariants | A (grants) | A | A | A | A | A | A |
| UG-08 KPI parity | — | A (canonical figures) | A | A | A | A | A |
| UG-09 Authorization | A (deny by default) | A (grants) | A | A | A | A | A |
| UG-11 Evidence | — | — | — | A | A | A | A |
| UG-12 Reliability | — | — | — | A | A | A | A |

### 7.3 Milestone-specific acceptance (exact checks in each milestone plan)

| Milestone | Acceptance |
|---|---|
| M0 | Environment reproducibility from a clean clone; architecture contracts (CF-0) frozen; toolchain consistency (`make doctor`); Makefile behaviour per contract; CI baseline green with stable check names; module boundaries enforced; AG-UI spike report reviewed; ECharts run recorded |
| M1 | Migrations from empty; schema integrity; deterministic seed (same hash twice); frozen clock; snapshots = parity at `as_of`; GI-01…16 (51 checks); canonical figures exact |
| M2 | All required KPI contracts; dashboard API parity; chart interactions; card total = records total; authorization and empty-scope behaviour; dashboard E2E; ECharts gate passed or DXD-23 fallback applied; axe clean (DR-007, DXD-21, DXD-24 cited) |
| M3 | State machine transitions; tools; bounded execution and budgets; mock tests; golden replay J1–J10 (API level); verifier rejects ungrounded numbers; recovery and versioned retry |
| M4 | AG-UI streaming and SDK fixture validation (DR-017, DXD-40, DXD-39, DXD-61 cited); generated UI contracts; context preservation; evidence rendering; drilldowns; integration E2E |
| M5 | Evaluation coverage ≥ 150; numerical accuracy 100%; grounding; security; reliability; performance (NFR-01 measured); accessibility; regression suite |
| M6 | Detector correctness; S1–S9 and N1–N11; lifecycle; notification authorization; dedup and idempotency; full replay hash `82fde5250960761d`; runner tests R1–R13; K1–K12 |

### 7.4 Integration rules and the milestone verification report

**RMAP-R010** The gate runs `milestone-gate.yml` on a specific merged `main` commit and produces two files:
- `tests/reports/gate/M<n>/report.json`, which **must validate against the `gateReport` definition** in `specs/engineering/engineering.schema.json` (`make specs-check GATE=M<n>` validates it);
- `report.md`, rendered from the JSON.

Both are archived as workflow artefacts for 90 days and linked from STATUS.md. The report records:

| Evidence | Field | Source |
|---|---|---|
| Merged commit SHA (40 hex) | `mergedCommitSha` | The gate run input |
| Approved specification-set version, and the PR that approved it | `specSet.version`, `specSet.approvedInPr` | `spec_set.yaml` at that commit |
| Dataset ID, `as_of`, seed hash, seeded state | `dataset` | `meta` (from M1); "not seeded" before |
| Fixture-set version: SHA-256 over the sorted paths and contents of `tests/fixtures/**`, plus the canonical-figures file hash | `fixtures` | Computed by the gate workflow |
| Required CI results: the `ci/summary` conclusion and every job's applicability, conclusion and run URL | `ci` | The reused `ci.yml` run |
| Results per suite, in the ARCH §10.8 vocabulary, with counts. Suites: backend unit, backend integration, frontend unit and component, integration (API, auth, AG-UI), Playwright E2E, agent mock, agent replay, database invariants, contracts, specs, security, ECharts gate, accessibility, replay golden, performance. `NOT_APPLICABLE` must cite its rule | `suites` | JUnit and `status.jsonl` |
| Every `GATE-M<n>-nn` check and every universal criterion, with its result | `gateChecks`, `universalCriteria` | Gate run |
| Trace summary: AT total, passed, failed, not implemented, skipped | `trace` | `trace-report GATE=M<n>` |
| Defects: open `blocking` defects (must be empty for approval) and other open defects | `defects` | GitHub issues `DEF-nnnn` |
| Approved exceptions in force or used during the milestone | `exceptions` | STATUS.md `EXC-nnn` |
| Deferred items with their target milestone | `deferred` | Milestone plan |
| The owner's decision, with date and reference | `approval` | Filled after review; `pending` until then |

**RMAP-R014** The gate enforces everything applicable to the milestone's completed scope (ARCH-R105). That includes regression: the acceptance tests of every earlier milestone must still pass at M<n>'s gate. A gate is never passed on PR-level CI evidence alone.

**RMAP-R015** No CF-3 or CF-4 contract element that depends on AG-UI SDK behaviour (spike items A1–A14) is frozen before the M0-T09 spike report is merged and reviewed (ARCH-R108).

**RMAP-R011** No milestone is marked complete in STATUS.md before the owner approves its report.

---

## 8. Five-day slice classification

**RMAP-R012** The slice is a delivery cut through M0–M4 and M6, not a milestone, and never the POC. Its scope is ESP tab 2, with amendment A-09 (Properties card metrics). Its exit is E2E-S1 to E2E-S3, INS-101 (standalone) and T-202 with evidence.

**RMAP-R013** Every task card carries a delivery class (A-16). `plans/SLICE_FIVE_DAY.md` (PR-M6) orders the `slice` cards into days. With ED-06 A, M0 is built before slice day 1, so day 1's foundation allocation becomes verification buffer.

---

## 9. Specification inventory and writing order

ESP tab 4 stands (items 1–43, seven PRs, Cursor-ready criteria), with these ownership updates:

| Item | Update |
|---|---|
| 1 | ADRs 0001–0006 **and 0015** |
| 2 | `docs/reference/` already committed (PR #1). PR-M0 adds only the hash check, via `make specs-check` |
| 6 | ARCHITECTURE additionally owns: web application architecture (§6), agent and AG-UI seams (§8), data ownership and migration rules (§7), testing architecture (§10), source-of-truth table (§11), traceability (§12) |
| 7 | DEVELOPMENT_ENVIRONMENT additionally owns: Makefile contract, dependency and locking strategy, CI architecture, branch and PR policy, repository settings, CI reporting, failure triage |
| 8 | Bootstrap contracts: the six files listed in CF-0 |
| 10 | This file |
| 13 | DATABASE_SCHEMA covers `core`, `meta`, `snap`, `seed_meta`; amended in PR-M3 and PR-M6 (A-07) |
| 14 | Metric YAML includes the Properties set (A-09) and the T-31206 action-item population (A-10) |
| 27, 32 | Own the G-5 contracts (A-08) |
| 41 | EVALUATION_PLAN no longer owns the general test taxonomy (A-04) |

**Cursor-ready criteria (unchanged):**
- no TBD in a normative section;
- every interface typed and versioned;
- every requirement has an acceptance test ID;
- open questions listed separately and non-blocking;
- design references point to frozen artefact versions.

---

## 10. Timeline (focused hours)

| Change | Hours | Note |
|---|---|---|
| ESP full-scope estimate | about 166.5 | Includes the slice (about 49) and the ESP's M0 (about 9: 6 build + 3 spike and harness) |
| A-14: approved delivery framework in M0 | +5 | M0 becomes about 14 h; built before slice day 1 under ED-06 A |
| A-09: Properties card metrics in the slice | +1 | Slice day 2 |
| **Revised full-scope estimate** | **about 172.5** | Roughly 21 working days for one developer, including the pre-slice M0 build |

**Effect on the slice.** It stays five working days (about 50 h). Because M0 is built beforehand, day 1's foundation allocation becomes verification buffer.

Specification writing is outside this timeline (ESP tab 4).
