# STATUS — Cenomi Dashboard Intelligence Agent POC

Updated: 2026-10-22 (PR-M0 = [PR #2](https://github.com/swa01wk/cenomi-dashboard-agent/pull/2), revision 2 after the owner's review: ROADMAP A-19…A-24).

| | |
|---|---|
| Baseline | DX1–DX6 (canvas v27 + OI-13 local wording fix); Final Design Gate 2026-10-22 |
| Dataset | `sd-2026.10.20-01` (`as_of` 2026-10-20; insight replay hash `82fde5250960761d`; runner reference_hash `c1e36ced42cebecc`) — **not yet seeded** |
| Specification set | 0.1.0, proposed in PR-M0 |

> Status vocabulary:
>
> | Status | Meaning |
> |---|---|
> | **Approved** | Decided by the project owner |
> | **In review** | Open PR awaiting the owner |
> | **Proposed** | Drafted, awaiting approval |
> | **Not started** | — |
> | **Pending verification** | Approved; a real-runtime check is owed |
> | **Open** | Needs a decision |
>
> Nothing is marked complete unless it was approved. This file is the only place progress is recorded (ADR-0002). The handoff files in `docs/handoff/` are a point-in-time record of 22 Oct 2026 and are not updated.

## Current phase and milestone

| | |
|---|---|
| Phase | **Specification authoring** — M0 specifications in review |
| Current milestone | **M0 Foundation**: specifications **In review** (PR-M0 = PR #2, branch `docs/m0-foundation-specs`); build **Not started, not authorized** |
| Migration | **Complete.** PR #1 merged into `main` on 2026-10-22 at `d5db7f3`; 214/214 handoff hashes verified |
| Engineering Specification Plan | **Approved 2026-10-22**, subject to the owner's refinements. Recorded as `plans/ROADMAP.md` v1.0 with amendments A-01 to A-18, plus A-19 to A-24 from the owner's review of PR #2. The proposed draft is kept unchanged in `plans/proposed/` |
| Next gate | Owner merges PR-M0 (CF-0) → decides ED-07, ED-08, ED-09 (exact Option A texts in `docs/design/DECISION_REGISTER.md` §5.1) → approves EXC-001 → applies protection stage P1 → explicit M0 build authorization |
| Implementation | **Not started.** No application code, migrations, packages, CI or Makefile exist |

## Completed and approved work

| Item | Date | Evidence |
|---|---|---|
| G0 planning assessment (v0.1 → v0.3) and decision register DR-001…047 | 21–22 Oct 2026 | `docs/reference/planning-history/PLANNING_ASSESSMENT_v0.3.md` |
| DX1–DX6 design (DX3, DX4 and DX6 conditionally approved; verification pending as below) | Oct 2026 | `docs/design/baseline/`; `docs/design/DESIGN_BASELINE.md` |
| Final Design Gate: Conditional Go; GDQ-01…12 = Option A; DXD-80…93 approved; scope frozen | 22 Oct 2026 | `docs/reference/final-design-gate/01_…`, `03_…` |
| ED-03 Option A (scoped): frozen reference copies and design exports stored in the repository | 22 Oct 2026 | PR #1 |
| Documentation migration merged (PR #1) | 22 Oct 2026 | `main` @ `d5db7f3` |
| Project restoration and engineering readiness assessment accepted | 22 Oct 2026 | Owner's approval message, 22 Oct 2026 |
| **Engineering Specification Plan approved** (with refinements) | 22 Oct 2026 | `plans/ROADMAP.md` §1–§2 |
| **ED-01 A, ED-02 A, ED-04 A, ED-05 A, ED-06 A, D-01 A approved**; DR-035 superseded by ED-01 | 22 Oct 2026 | ADR-0001, 0002, 0005, 0006, 0015 (in PR-M0); `docs/design/DECISION_REGISTER.md` §5 |

## Milestones

| Milestone | Specs PR | Spec state | Build state | Slice cards | Gate | Blocked by |
|---|---|---|---|---|---|---|
| M0 Foundation | PR-M0 (items 1–12) | **In review** | Not started — not authorized | All M0 cards except M0-T09 (built before slice day 1, ED-06 A) | GATE-M0-01…14 (`plans/M0_FOUNDATION.md` §6) | PR-M0 merge; ED-07, ED-08, ED-09; EXC-001; protection P1; build authorization |
| M1 Data | PR-M1 (13–21) | Not started | Not started | Days 1–2 | Seed hash reproducible; GI 51/51; canonical figures; snapshots = parity | PR-M0 merged (CF-0) |
| M2 Metrics and dashboards | PR-M2 (22–26) | Not started | Not started | Days 2–3 | Golden tests; card = records totals; ECharts gate | PR-M1 (CF-1) |
| M3 Agent runtime | PR-M3 (27–31) | Not started | Not started | Day 3 | Verifier; J1–J10 on replay; budgets | PR-M2 (CF-2); GDQ-12 configuration |
| M4 AG-UI and GenUI | PR-M4 (32–35) | Not started | Not started | Day 4 | AG-UI fixtures; every kind has schema, fallback and fixture | PR-M3 (CF-3); ED-10; spike report |
| M6 Proactive intelligence (spec written 6th) | PR-M6 (36–40) | Not started | Not started (full build after the M5 gate) | Day 5 | Replay hash; S1–S9 / N1–N11; R1–R13; K1–K12 | PR-M4 (CF-4); **full build: M5 gate (DR-010)** |
| M5 Evaluation (spec written 7th) | PR-M5 (41–43) | Not started | Not started | Day 5 (20 questions) | 150+ scored; thresholds; latency | PR-M6 (CF-5); ED-11 / DR-036 |

| Order | Sequence |
|---|---|
| Specification writing | **M0, M1, M2, M3, M4, M6, M5** |
| Implementation dependency | **M0 → M1 → M2 → M3 → M4 → M5 → M6** (the complete M6 only after the M5 gate) |

## Contract freezes

| CF | Contracts | Frozen in | Date | Version |
|---|---|---|---|---|
| CF-0 Toolchain | Repository layout; `error_envelope.v1`, `error_codes.v1`, `principal.v1`, `scope_decision.v1`, `health_report.v1`, `dataset_descriptor.v1`; codegen pipeline and schema subset; `specs/engineering/*`; ID conventions; CI check names | PR-M0 | **In review** | 1 |
| CF-1 Data | Tables (`core`, `meta`, `snap`, `seed_meta`); enums; metric YAML; permissions; scenarios; canonical figures | PR-M1 | — | — |
| CF-2 Analytics | metric query, `analysis_result.v1`, card view-models, records, `selection_ref.v1`, tokens | PR-M2 | — | — |
| CF-3 Agent | AnalysisPlan, tool schemas, AnswerDraft, fact tokens, evidence envelope, LLM adapter, thread and run contracts, `agent` tables, evaluation case schema v1 | PR-M3 | — | — |
| CF-4 Presentation | `cenomi.presentation.v1`, per-kind schemas, composition policy, AG-UI mapping, state shape, run endpoints | PR-M4 | — | — |
| CF-5 Insights | `insight.v1`, detector configuration schema, runner protocol, inbox API, `insights` tables | PR-M6 | — | — |
| CF-6 Evaluation | Benchmark composition, scoring (needs DR-036) | PR-M5 | — | — |

## Specifications

| # | Path | State | PR | Open questions |
|---|---|---|---|---|
| 1 | `docs/adr/0001`–`0006`, `0015`; `docs/adr/README.md` | In review | PR-M0 | — |
| 2 | `docs/reference/` (frozen copies) | Committed (PR #1); hash check specified in `make specs-check` | PR #1 / PR-M0 | — |
| 3 | `docs/design/DESIGN_BASELINE.md` | In review | PR-M0 | — |
| 4 | `docs/design/DECISION_REGISTER.md` | In review | PR-M0 | — |
| 5 | `docs/product/PRODUCT_SPEC.md` | In review | PR-M0 | OQ-PSPEC-01 |
| 6 | `docs/architecture/ARCHITECTURE.md` | In review | PR-M0 | OQ-ARCH-01, 02, 03 |
| 7 | `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` | In review | PR-M0 | Depends on ED-07, ED-08, ED-09 |
| 8 | `specs/contracts/` bootstrap (6 files); `specs/engineering/` (4 files); `specs/traceability/id_conventions.yaml` | In review | PR-M0 | — |
| 9 | `AGENTS.md`, `.cursor/rules/*.mdc` (7 files) | In review | PR-M0 | — |
| 10 | `plans/ROADMAP.md` | In review (records the approved ESP) | PR-M0 | — |
| 11 | `plans/M0_FOUNDATION.md` (M0-T01…T11, 83 acceptance tests, GATE-M0-01…14) | In review | PR-M0 | — |
| 12 | `plans/STATUS.md` | This file | PR-M0 | — |
| 13–21 | DATABASE_SCHEMA, metric YAML (including the Properties set, ROADMAP A-09; T-31206 action items, A-10), KPI_CATALOG, permissions, SYNTHETIC_DATA_STRATEGY, scenarios, golden fixtures, ADR 0007/0008/0012, M1 plan | Not started | PR-M1 | OI-04, 05, 06, 14 |
| 22–26 | API_CONTRACTS, DESIGN_SYSTEM + tokens, card specs (PRODUCT_SPEC Appendix A), ADR-0011, M2 plan | Not started | PR-M2 | ECharts result; ED-09 |
| 27–31 | AGENT_ARCHITECTURE, AGENT_TOOLS, evaluation case schema + 20 questions, ADR-0009, DATABASE_SCHEMA amendment (`agent`), M3 plan | Not started | PR-M3 | OI-07, OI-10, OQ-ARCH-01 |
| 32–35 | AGUI_INTEGRATION, GENERATIVE_UI, ADR-0010, M4 plan | Not started | PR-M4 | ED-10; spike report; OQ-ARCH-02, 03 |
| 36–40 | PROACTIVE_INTELLIGENCE, detectors-1.1 + `insight.v1`, insight fixtures, ADR-0013, DATABASE_SCHEMA amendment (`insights`), M6 plan + SLICE_FIVE_DAY | Not started | PR-M6 | OQ-PSPEC-01 |
| 41–43 | EVALUATION_PLAN (benchmark, scoring, thresholds, performance — test taxonomy now in ARCHITECTURE, A-04), benchmark, ADR-0014 + M5 plan | Not started | PR-M5 | DR-036 / ED-11; OI-09 |

## Decisions

**Approved:**
- GDQ-01…GDQ-12, Option A (2026-10-22)
- DXD-80…93
- The 17 batch defaults with final definitions (GDQ-10)
- The scope freeze
- ED-03 Option A, scoped (2026-10-22)
- **The ESP, with refinements (2026-10-22)**
- **ED-01 A, ED-02 A, ED-04 A, ED-05 A, ED-06 A and D-01 A (2026-10-22)**
- DR-035 superseded by ED-01

**Remaining (not approved):**

| ID | Decision | Recommended | Needed before | Owner |
|---|---|---|---|---|
| **ED-07** | POC sign-in: dev fixture principal with a signed httpOnly cookie (exact text: DECISION_REGISTER §5.1) | A | **M0 build** | Owner |
| **ED-08** | Model determinism: mock, replay in CI, live manual only (exact text: DECISION_REGISTER §5.1; the approved test requirements already require this behaviour) | A | **M0 build** | Owner |
| **ED-09** | Styling: CSS Modules plus token CSS variables (exact text: DECISION_REGISTER §5.1) | A | **M0 build** | Owner |
| ED-10 | AG-UI 1.0 pin (spike to confirm; see the correction in ROADMAP A-13) | A | PR-M4 | Owner |
| ED-11 | DR-036 evaluation scoring | A | PR-M5 | Owner |
| DR-036 | Evaluation scoring (the register's only open decision) | via ED-11 | PR-M5 | Owner |

**Configuration (not decisions):**
- GDQ-12: provider, primary and fallback model names, API key. Needed before slice day 3; optional for the M0 spike item L1. Stored as a secret, never committed.
- Live-evaluation credentials (`LIVE_EVAL_LLM_API_KEY`), separate from development keys.

## Exceptions (DEVENV-R051)

| ID | Scope | Reason | Compensating controls | Expires | State |
|---|---|---|---|---|---|
| EXC-001 | Merges of M0-T01, M0-T03, M0-T11 and M0-T10 under protection stage P1, before `ci/summary` exists | These cards build the tooling CI runs; GitHub cannot require a check that has never reported | Each PR pastes local `make check` output and its AT results. The M0-T07 PR's CI must show `trace-report CARD=…` all `PASSED` for the four cards before stage P2 is enabled | When stage P2 is in force | **Proposed — awaiting the owner's approval** |

## Open questions (non-blocking)

| ID | Question | Default | Decide in | Owner |
|---|---|---|---|---|
| OQ-ARCH-01 | Where the evidence envelope and fact-token verifier live, so that `insights` does not depend on `agent` | `insights` may import `cenomi.agent.evidence` only | PR-M3 | Architect |
| OQ-ARCH-02 | Full script CSP with nonces | Baseline headers only | PR-M4 | Architect |
| OQ-ARCH-03 | AG-UI interrupt outcome vs the DX4 A8 fallback for filter proposals and clarification | DX4-AGUI stands | PR-M4 (after spike) | Architect |
| OQ-PSPEC-01 | Bell visibility for the tenant persona | Tenant reaches the inbox from the rail | PR-M6 | Architect, owner if it changes design |

## Verification gates

| Gate | Status | Evidence |
|---|---|---|
| ECharts 5.6.0 real-runtime verification (GDQ-06; DR-007, DXD-21, DXD-61) | **Pending verification**. Mandatory. Harness M0-T08 (local pinned asset); informational in M0–M1; pass or DXD-23 fallback required by the M2 exit | DX3 gallery ran on a test double only |
| AG-UI spike against the 1.0 SDKs (GDQ-11; DR-017, DXD-40) | **Pending verification**. M0-T09; items A1–A14, L1 | Not run. Note the ESP tab 8 "cancelled outcome" claim is not supported by the 1.0 documentation (ROADMAP A-13) |
| Model configuration (GDQ-12) | **Open (configuration)** | Not supplied |
| axe-core and screen reader on the real build (GUI-06, NFR-02; OI-02; DXD-24, DXD-39) | Pending: M2 and M4 exits | Structural smoke only |
| Latency NFR-01 (OI-11) | Pending: M5 | Not measured |

## Change requests

| CR | Date | Summary | Cites | Decision |
|---|---|---|---|---|
| — | — | None raised. The refinements of 22 Oct 2026 were approved together with the ESP and are recorded as ROADMAP amendments, not as CRs | — | — |

## Blockers and risks

| ID | Blocker or risk | Owner | Since | Next action |
|---|---|---|---|---|
| B-01 | ~~ESP not approved~~ — **resolved 2026-10-22** | — | — | — |
| B-02 | ~~ED-01, 02, 04, 05, 06 undecided~~ — **resolved 2026-10-22** | — | — | — |
| B-03 | ~~Migration PR not merged~~ — **resolved 2026-10-22** (`d5db7f3`) | — | — | — |
| B-04 | OI-13: the DX5-GenUI "overdue" wording fix exists in the exported boards only | Architect | 2026-10-22 | Exported boards are authoritative; no action |
| B-05 | PR-M0 awaiting owner review and merge | Owner | 2026-10-22 | Review PR-M0 |
| B-06 | ED-07, ED-08, ED-09 undecided (block the M0 build, not the M0 specs) | Owner | 2026-10-22 | Pick values |
| B-07 | `main` has no branch protection. Stage P1 (DEVENV §8.4) is required before the first implementation PR merges, and P2 right after M0-T07 merges. Required approving reviews must be 0, because PRs are authored under the owner's account and GitHub forbids self-approval; the owner's merge is the approval (DEVENV-R039) | Owner | 2026-10-22 | Apply P1 before authorizing the M0 build; approve or reject EXC-001 |
| R-01 | Scope squeezed into five days | Owner, Architect | GD | Keep slice and full scope separate (ROADMAP §8) |
| R-02 | Seed or metric drift from the canonical figures | Developer | GD | GI invariants and replay hash in CI |
| R-04 | Ungrounded numbers or causal wording | Developer | GD | Fact tokens, verifier, banned-term lint |
| R-09 | Composer makes architectural choices where specifications are thin | Architect | GD | Cursor-ready criteria; AGENTS.md; 20-field task cards; stop-and-report rule |
| R-14 | Single developer | Owner | GD | Specifications complete before slice day 1 |

The full risk register is in `docs/reference/final-design-gate/08_OPEN_ISSUES_AND_RISKS.md`.

## Next tasks (dependency order)

1. Owner reviews PR-M0 (`docs/m0-foundation-specs`). Claude revises it in the same PR on comments. The owner merges, and CF-0 is recorded as frozen.
2. Owner decides ED-07, ED-08 and ED-09. Claude records each in an ADR (DSYS ADR for ED-09 in PR-M2; ADR-0009 groundwork for ED-08).
3. Owner approves or rejects EXC-001 and applies protection stage P1 (DEVENV §8.4) before the first implementation PR merges. P2 follows immediately after M0-T07 merges.
4. Owner explicitly authorizes the M0 build (ADR-0015 §3). Composer implements M0-T01…T11 one card per PR; the M0-T09 spike report merges through a docs PR.
5. In parallel with the M0 build, once PR-M0 has merged: Claude authors PR-M1 (`docs/m1-…`).
6. GATE-M0 runs on the merged `main` commit; owner approves the M0 verification report.

## Latest artifact versions

| Artifact | Version |
|---|---|
| PRD | v1.0, 21 Oct 2026 |
| Technical Architecture & Implementation Plan | v1.0, 21 Oct 2026 |
| API Reference | Generated 2026-10-13 |
| Design canvas | v27 (+ OI-13 local fix in exported boards) |
| Final Design Gate doc | 22 Oct 2026 outcome recorded (exported 8 tabs) |
| Engineering Specification Plan | 22 Oct 2026 draft → **approved** as `plans/ROADMAP.md` v1.0 |
| Specification set | 0.1.0 (PR-M0, in review) |
| Planning Assessment | v0.3 (G0) |
| Dataset | `sd-2026.10.20-01` |
| Detectors | detectors-1.1 |

## Completion criteria for the current milestone (M0 specifications)

- [x] ESP approved (2026-10-22, with refinements)
- [x] Migration PR merged into `main` (`d5db7f3`)
- [x] ED-01, ED-02, ED-03, ED-04, ED-05, ED-06, D-01 decided
- [x] Repository write path agreed (ED-01 A)
- [x] PR-M0 items 1–12 drafted and self-reviewed (consistency audit in the PR description)
- [ ] PR-M0 reviewed and merged by the owner; CF-0 frozen

Last reviewed: **2026-10-22**. Next required owner action: **review PR-M0**, then **decide ED-07, ED-08 and ED-09**.
