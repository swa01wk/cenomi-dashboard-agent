# STATUS — Cenomi Dashboard Intelligence Agent POC

Updated: 2026-10-22 (repository migration, pending merge) · Baseline: DX1–DX6 (canvas v27 + OI-13 local wording fix), Final Design Gate 2026-10-22 · Dataset: `sd-2026.10.20-01` (as_of 2026-10-20; insight replay hash `82fde5250960761d`, runner reference_hash `c1e36ced42cebecc`)

> Status vocabulary: **Approved** (decided by the product owner) · **Proposed** (drafted, awaiting approval) · **Not started** · **Pending verification** (approved, real-runtime check owed) · **Open** (needs a decision). Nothing below is marked complete unless it was approved.

## Current phase and milestone

| | |
|---|---|
| Phase | **Specification planning** (pre-M0). Design phase closed. **Documentation migration to the repository: pending merge.** |
| Current milestone | **M0 Foundation — specifications not started** |
| State | Engineering Specification Plan (ESP) **Proposed**, awaiting approval |
| Migration | Handoff package (214 files + `docs/handoff/SHA256SUMS`) committed on branch `docs/cenomi-project-handoff` from `main` @ `5bbd62a`; pull request open, **pending user approval to merge**. Until merged, `main` remains README-only |
| Next gate | Merge the migration PR → ESP approval + ED-01, ED-02, ED-04, ED-05, ED-06 decided → author PR-M0 |
| Implementation | **Not started.** No application code, migrations, packages, CI or engineering specifications exist |

## Completed and approved work

| Item | Date | Evidence |
|---|---|---|
| G0 planning assessment (v0.1 → v0.3) and decision register DR-001…047 | 21–22 Oct 2026 | `docs/reference/planning-history/PLANNING_ASSESSMENT_v0.3.md` |
| DX1 information architecture | Oct 2026 | Boards Main, IA, Inventory, Direction A–C, DX1-Decisions |
| DX2 Admin and Tenant dashboards (64/64 checks) | Oct 2026 | Boards Admin, Tenant, States, Responsive, DX2-Notes, DX2-Verify |
| DX3 chart parity (conditionally approved — real ECharts pending) | Oct 2026 | DX3-Gallery, DX3-Parity |
| DX4 agent workspace (77/77, 211 logic; conditionally approved) | 22 Oct 2026 | DX4 boards |
| DX5 generative UI (3,778 logic, 45/45; approved with refinements) | 22 Oct 2026 | DX5 boards |
| DX6 proactive intelligence (44/81/387/51/13 checks; refinements done) | 22 Oct 2026 | DX6 boards; reference models |
| Final Design Gate: Conditional Go to specification planning | 22 Oct 2026 | `docs/reference/final-design-gate/01_DESIGN_REVIEW_REPORT.md` |
| GDQ-01…GDQ-12 = Option A; DXD-80…93 approved; scope frozen | 22 Oct 2026 | `03_DECISION_REGISTER.md` § Gate decisions recorded |
| Register: 141 decisions = 126 ready, 7 verification pending, 1 decision (DR-036), 2 deferred, 5 superseded | 22 Oct 2026 | Same |
| **ED-03 Option A approved (scoped)**: frozen copies of the authoritative reference documents and relevant design exports stored in the repository under their documentation paths. Scope: preserving the existing reference and design baseline only; it does not change product architecture, KPI calculations, implementation scope or any other engineering decision | 22 Oct 2026 | User authorization for the documentation migration; `docs/reference/`, `docs/design/baseline/` |

## Milestones

| Milestone | Specs PR | Spec state | Build state | Slice cards | Gate | Blocked by |
|---|---|---|---|---|---|---|
| M0 Foundation | PR-M0 (items 1–12) | Not started | Not started | Day 1 | `make up` + CI green; drift check; AG-UI spike report; ECharts run recorded | Migration PR merge; ESP approval; ED-01, ED-02, ED-04, ED-05, ED-06 |
| M1 Data | PR-M1 (13–21) | Not started | Not started | Days 1–2 | Seed hash reproducible; GI 51/51; canonical figures; snapshots = parity | PR-M0 merged (CF-0) |
| M2 Metrics and dashboards | PR-M2 (22–26) | Not started | Not started | Days 2–3 | Golden tests; card = records totals; ECharts gate | PR-M1 (CF-1) |
| M3 Agent runtime | PR-M3 (27–31) | Not started | Not started | Day 3 | Verifier; J1–J10 on replay; budgets | PR-M2 (CF-2); GDQ-12 config |
| M4 AG-UI and GenUI | PR-M4 (32–35) | Not started | Not started | Day 4 | AG-UI 1.0 fixtures; every kind schema/fallback/fixture | PR-M3 (CF-3); ED-10; spike report |
| M6 Proactive intelligence (spec written 6th) | PR-M6 (36–40) | Not started | Not started (full build after M5) | Day 5 | Replay hash; S1–S9 / N1–N11; R1–R13; K1–K12 | PR-M4 (CF-4); **full build: M5 gate (DR-010)** |
| M5 Evaluation (spec written 7th) | PR-M5 (41–43) | Not started | Not started | Day 5 (20 questions) | 150+ scored; thresholds; latency | PR-M6 (CF-5); ED-11 / DR-036 |

Specification-writing order: **M0, M1, M2, M3, M4, M6, M5**. Implementation dependency: **M0 → M1 → M2 → M3 → M4 → M5 → M6** (complete M6 only after the M5 gate).

## Contract freezes

| CF | Contracts | Frozen in | Date | Version |
|---|---|---|---|---|
| CF-0 Toolchain | Repo layout, error envelope, AccessScope interface, codegen, CI | PR-M0 | — | — |
| CF-1 Data | Tables, enums, roles, schemas; metric YAML; permissions; scenarios; canonical figures | PR-M1 | — | — |
| CF-2 Analytics | metric query, analysis_result.v1, card view-models, records, selection_ref.v1, tokens | PR-M2 | — | — |
| CF-3 Agent | AnalysisPlan, tool schemas, AnswerDraft, fact tokens, evidence envelope, LLM adapter, evaluation case schema v1 | PR-M3 | — | — |
| CF-4 Presentation | cenomi.presentation.v1, per-kind schemas, composition policy, AG-UI mapping, state shape | PR-M4 | — | — |
| CF-5 Insights | insight.v1, detector config schema, runner protocol, inbox API | PR-M6 | — | — |
| CF-6 Evaluation | Benchmark composition, scoring (needs DR-036) | PR-M5 | — | — |

## Specifications (17 documents, 10 plan files, ADRs, machine-readable specs)

All **Not started**. Writing order and Cursor-ready criteria: `plans/proposed/engineering-specification-plan/04_SPECIFICATION_INVENTORY.md`.

| # | Path | State | PR | Open questions |
|---|---|---|---|---|
| 1 | docs/adr/0001–0006 | Not started (ADR-0002 records the approved ED-03) | M0 | ED-01, ED-02 |
| 2 | docs/reference/ (frozen copies) | Committed on branch `docs/cenomi-project-handoff` (migration PR, **pending merge**) under ED-03 A (scoped approval 2026-10-22). PR-M0 still adds the README/version check described in ESP tab 4 | Migration PR | — |
| 3 | docs/design/DESIGN_BASELINE.md | Not started (inputs in docs/design/baseline/) | M0 | — |
| 4 | docs/design/DECISION_REGISTER.md | Not started (source: GD export 03) | M0 | — |
| 5 | docs/product/PRODUCT_SPEC.md | Not started | M0 | — |
| 6 | docs/architecture/ARCHITECTURE.md | Not started | M0 | ED-02 |
| 7 | docs/architecture/DEVELOPMENT_ENVIRONMENT.md | Not started | M0 | ED-05, 07–09 |
| 8 | specs/contracts bootstrap | Not started | M0 | — |
| 9 | AGENTS.md, .cursor/rules | Not started | M0 | — |
| 10 | plans/ROADMAP.md | Not started | M0 | — |
| 11 | plans/M0_FOUNDATION.md | Not started | M0 | — |
| 12 | plans/STATUS.md | **This file (migration version, pending merge)** | Migration PR, then M0 | — |
| 13–21 | DATABASE_SCHEMA, metric YAML, KPI_CATALOG, permissions, SYNTHETIC_DATA_STRATEGY, scenarios, golden fixtures, ADR 0007/0008/0012, M1 plan | Not started | M1 | snap vs meta; OI-04/05/06/14 |
| 22–26 | API_CONTRACTS, DESIGN_SYSTEM + tokens, card specs, ADR-0011, M2 plan | Not started | M2 | ECharts result |
| 27–31 | AGENT_ARCHITECTURE, AGENT_TOOLS, eval case schema + 20 questions, ADR-0009, M3 plan | Not started | M3 | OI-07, OI-10 |
| 32–35 | AGUI_INTEGRATION, GENERATIVE_UI, ADR-0010, M4 plan | Not started | M4 | ED-10; spike |
| 36–40 | PROACTIVE_INTELLIGENCE, detectors-1.1 + insight.v1, insight fixtures, ADR-0013, M6 plan + SLICE_FIVE_DAY | Not started | M6 | — |
| 41–43 | EVALUATION_PLAN, benchmark, ADR-0014 + M5 plan | Not started | M5 | DR-036 / ED-11; OI-09 |

## Decisions

**Approved this phase:** GDQ-01…GDQ-12 (Option A, 2026-10-22) · DXD-80…93 · the 17 batch defaults with final definitions (GDQ-10) · scope freeze · **ED-03 Option A (2026-10-22), scoped** to storing frozen copies of the authoritative reference documents and relevant design exports in the repository; it does not alter product architecture, KPI calculations, implementation scope or any other engineering decision.

**Remaining proposals (not approved):**

| ID | Decision | Recommended | Needed before | Owner |
|---|---|---|---|---|
| ESP | Engineering Specification Plan (tabs 1–6, supporting tabs) | Approve | Any spec writing | User |
| **ED-01** | Delivery via PRs with push access (supersedes DR-035) | A | **M0 specs** | User |
| **ED-02** | Modular monolith, agent in-process | A | **M0 specs** | User |
| **ED-04** | Slice cards tagged in milestone plans | A | **M0 specs** | User |
| **ED-05** | CI only, no deploy | A | **M0 specs** | User |
| **ED-06** | Build M0 right after PR-M0 merges (with explicit go-ahead) | A | **M0 specs** | User |
| ED-07 | Dev fixture sign-in, signed httpOnly cookie | A | M0 build | User |
| ED-08 | Replay LLM provider in CI | A | M0 build | User |
| ED-09 | CSS Modules + token CSS variables | A | M0 build | User |
| ED-10 | AG-UI 1.0 pin | A | PR-M4 | User |
| ED-11 | DR-036 evaluation scoring | A | PR-M5 | User |
| DR-036 | Evaluation scoring (register's only open decision) | via ED-11 | PR-M5 | User |
| — | `snap` schema vs snapshots in `meta` | Decide in DATABASE_SCHEMA.md | PR-M1 | Architect |

**Configuration (not decisions):** GDQ-12 provider, primary and fallback model names, API key — before slice day 3 (stored as a secret, never committed) · repository push access if ED-01 = A.

## Verification gates

| Gate | Status | Evidence |
|---|---|---|
| ECharts 5.6.0 real-runtime verification (GDQ-06; DR-007, DXD-21, DXD-61) | **Pending verification** — mandatory; harness M0-T08, gate before M2 exit | DX3 gallery ran on a test double only |
| AG-UI spike against pinned SDK (GDQ-11; DR-017, DXD-40) | **Pending verification** — M0-T09 | Not run |
| Model configuration (GDQ-12) | **Open (configuration)** | Not supplied |
| axe-core + screen reader on real build (GUI-06, NFR-02; OI-02) | Pending — M2/M4 exits | Structural smoke only |
| Latency NFR-01 (OI-11) | Pending — M5 | Not measured |

## Change requests

| CR | Date | Summary | Cites | Decision |
|---|---|---|---|---|
| — | — | None raised | — | — |

## Blockers and risks

| ID | Blocker or risk | Owner | Since | Next action |
|---|---|---|---|---|
| B-01 | ESP not approved | User | 2026-10-22 | Review ESP tabs 1–7 |
| B-02 | ED-01, ED-02, ED-04, ED-05, ED-06 undecided (block M0 specs; ED-03 approved 2026-10-22) | User | 2026-10-22 | Pick values |
| B-03 | Migration PR open, not merged (documentation-only push was authorized 2026-10-22; ED-01 for specification PRs is still undecided) | User | 2026-10-22 | Review and merge the migration PR |
| B-04 | OI-13: DX5-GenUI "overdue" wording fix exists in exported boards but not on canvas v27 | Architect | 2026-10-22 | Exported boards are authoritative for this wording; no action blocks specs |
| R-01 | Scope squeezed into five days | User/Architect | GD | Keep slice vs full scope separate |
| R-02 | Seed/metric drift from canonical figures | Developer | GD | GI invariants + replay hash in CI |
| R-04 | Ungrounded numbers / causal wording | Developer | GD | Fact tokens, verifier, banned-term lint |
| R-14 | Single developer | User | GD | Specs complete before day 1 |

Full risk register: `docs/reference/final-design-gate/08_OPEN_ISSUES_AND_RISKS.md`.

## Next tasks (dependency order)

1. Migrate: user reviews and merges the migration PR (branch `docs/cenomi-project-handoff`); then set up the new Claude Project and attach the repository — `docs/handoff/MIGRATION_INSTRUCTIONS.md` §3.
2. New account verifies understanding (onboarding prompt) and reports gaps.
3. User approves ESP and decides ED-01, ED-02, ED-04, ED-05, ED-06 (ED-03 already approved, scoped).
4. Author PR-M0, sessions A–E (ESP tab 6); self-review; submit.
5. User decides ED-07…09; separately authorizes the M0 build (ED-06).
6. PR-M1 → PR-M2 → PR-M3 → PR-M4 → PR-M6 → PR-M5, each reviewed and merged before the next is opened.

## Latest artifact versions

| Artifact | Version |
|---|---|
| PRD | v1.0, 21 Oct 2026 |
| Technical Architecture & Implementation Plan | v1.0, 21 Oct 2026 |
| API Reference | generated 2026-10-13 |
| Design canvas | v27 (+ OI-13 local fix in exported boards) |
| Final Design Gate doc | 22 Oct 2026 outcome recorded (exported 8 tabs) |
| Engineering Specification Plan | 22 Oct 2026 draft, Proposed (exported 13 tabs) |
| Planning Assessment | v0.3 (G0) |
| Dataset | sd-2026.10.20-01 |
| detectors | detectors-1.1 |

## Completion criteria for the current milestone (M0 specifications)

- [ ] ESP approved
- [ ] Migration PR merged into `main`
- [x] ED-03 decided (Option A, scoped, 2026-10-22)
- [ ] ED-01, ED-02, ED-04, ED-05, ED-06 decided
- [ ] Repository write path agreed (ED-01)
- [ ] PR-M0 items 1–12 drafted and self-reviewed (ESP tab 6 checklist)
- [ ] PR-M0 reviewed and merged by the user; CF-0 frozen

Last reviewed: **2026-10-22** · Next required user approval: **merge of the migration PR**, then **ESP + ED-01, ED-02, ED-04, ED-05, ED-06**
