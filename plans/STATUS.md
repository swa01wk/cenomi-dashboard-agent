# STATUS — Cenomi Dashboard Intelligence Agent POC

Updated: 2026-10-24. **M0 build in progress; all EXC-001 bootstrap cards merged.** Merged: M0-T01 (`75a2fed`, PR #6), M0-T03 (`0027aae`, PR #9), M0-T11 (`386f017`, PR #12) and M0-T10 (`5dae0a5`, PR #18) under P1 + EXC-001; DEF-0001 security patch (`6e813b3`, PR #16) under P1 + EXC-002. Spec set **0.1.5** at `7544885` (HC-10, PR #17). **Next:** M0-T07 (CI workflows, draft PR #11) rebased and completed; then P2. P1 in force (ruleset `25699552`).

| | |
|---|---|
| Baseline | DX1–DX6 (canvas v27 + OI-13 local wording fix); Final Design Gate 2026-10-22 |
| Dataset | `sd-2026.10.20-01` (`as_of` 2026-10-20; insight replay hash `82fde5250960761d`; runner reference_hash `c1e36ced42cebecc`) — **not yet seeded** |
| Specification set | **0.1.7** (HC-12, ROADMAP A-34) in review; **0.1.6** at `795695e` (HC-11, ROADMAP A-33); **0.1.5** at `7544885` (HC-10, ROADMAP A-32); **0.1.4** at `c582535` (CR-002/EXC-002, ROADMAP A-31); **0.1.3** at `3c182cf` (CR-001, ROADMAP A-30); 0.1.2 at `ccdc276` (HC-6, HC-7); 0.1.1 at `77c9c10`; 0.1.0 at `4515031` (CF-0) |

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
| Phase | **M0 build** (authorized 2026-10-23); spec set 0.1.6 (0.1.7 in review) |
| Current milestone | **M0 Foundation**: specifications **approved and merged** (PR #2, squash `4515031`, 2026-10-22T15:59:58Z). Corrections HC-1 to HC-5 and the clarifications merged at `77c9c10` (PR #3, spec set 0.1.1). P1 in force. Build **authorized 2026-10-23**, not yet started (first card M0-T01) |
| Migration | **Complete.** PR #1 merged into `main` on 2026-10-22 at `d5db7f3`; 214/214 handoff hashes verified |
| Engineering Specification Plan | **Approved 2026-10-22**, subject to the owner's refinements. Recorded as `plans/ROADMAP.md` v1.0 with amendments A-01 to A-18, plus A-19 to A-24 from the owner's review of PR #2, A-25 and A-26 from the owner's approvals, and A-27 (corrections HC-1 to HC-5). The proposed draft is kept unchanged in `plans/proposed/` |
| Next gate | M0-T07 (CI workflows, draft PR #11): rebase onto `main`, add the CR-001 `ci/specs` steps, merge under P1 once its own run shows `ci/summary` `success` (it is not covered by EXC-001). That run is also EXC-001 C5 (a) and EXC-002 C5 (a). Then the owner applies P2 |
| Implementation | **M0 in progress.** Merged: M0-T01 (`75a2fed`), M0-T03 (`0027aae`), M0-T11 (`386f017`), M0-T10 (`5dae0a5`); DEF-0001 patch (`6e813b3`). In progress: M0-T07 (draft PR #11). Remaining after M0-T07: M0-T02, M0-T05, M0-T08, M0-T06, M0-T04, M0-T09 spike |

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
| **M0 specification package approved**, including the revision 2 corrections (`4df9b1b`) | 22 Oct 2026 | Owner's approval message, 22 Oct 2026 21:19 IST |
| **ED-07 A, ED-08 A, ED-09 A approved**, with the owner's added requirements | 22 Oct 2026 | ADR-0016, 0017, 0018; DECISION_REGISTER §5.1 |
| **Two-stage protection policy P1/P2 approved**; 0 required approving reviews accepted; manual review and explicit milestone approval retained | 22 Oct 2026 | DEVENV §8.4; ADR-0015 §5 |
| **EXC-001 approved conditionally** (conditions C1–C7) | 22 Oct 2026 | DEVENV §8.4; Exceptions below |
| **PR #2 approved for merge into `main`**, subject to verification | 22 Oct 2026 | Owner's approval message, 22 Oct 2026 21:19 IST |
| **PR-M0 merged** (squash on the owner's instruction after verification): `main` @ **`4515031`**, tree identical to PR head `946fcee`; ADR-0001…0006 and ADR-0015…0018 Accepted | 22 Oct 2026 | PR #2; `git log` |
| **CF-0 frozen** at `4515031` (versions below) | 22 Oct 2026 | ROADMAP §3.2 |
| **Corrections HC-1 to HC-5 approved** (M0 dependencies, acceptance gates, lockfile rule, file ownership) | 23 Oct 2026 | Owner's approval message, 23 Oct 2026 09:29 IST; ROADMAP A-27 |
| **Operational clarifications approved**: lockfile serialization (DEVENV-R055 (a)); protection availability and non-destructive verification (DEVENV-R056). **PR #3 approved for merge**; spec set 0.1.1 approved | 23 Oct 2026 | Owner's approval message, 23 Oct 2026 09:58 IST; ROADMAP A-28 |
| **PR #3 merged**: `main` @ **`77c9c10`** (squash of `88d2b74`, tree identical); spec set 0.1.1 accepted by the owner | 23 Oct 2026 | PR #3; owner's message, 23 Oct 2026 10:11 IST |
| **Protection stage P1 applied** by the owner (web UI) **and verified** through read-only API calls (ruleset `25699552`) | 23 Oct 2026 | "Repository protection" section below |
| **M0 build authorized** for Cursor Composer 2.5 (ADR-0015 §3; `plans/M0_FOUNDATION.md` §8 conditions 1–4 met: spec set merged, ED-07/08/09 decided, P1 in force with EXC-001 approved, Composer directed to `AGENTS.md` and `.cursor/rules/`) | 23 Oct 2026 | Owner's message, 23 Oct 2026 10:46 IST: "lets start with cursor implementation" |
| **M0-T01 merged** (PR #6, `75a2fed`); EXC-001 log entry recorded (PR #7) | 23 Oct 2026 | EXC-001 log below |
| **HC-6 approved**: M0-T03 may change the packaging, ruff and mypy sections of `backend/pyproject.toml`. **HC-7** (an owner for each of the 33 M0 Make targets) is proposed in the same PR and approved by merging it | 23 Oct 2026 | Owner's answer, 23 Oct 2026 13:04 IST; ROADMAP A-29 |
| **HC-8 and HC-9 approved** (tooling suite in `ci/specs`; manual-AT results file) and recorded as **CR-001** with the `import-linter` wording fix | 23 Oct 2026 | Owner's answers, 23 Oct 2026 23:20 IST; ROADMAP A-30 |
| **M0-T11 merged** (PR #12, `386f017`) and **CR-001 merged** (PR #13, `3c182cf`; spec set 0.1.3); EXC-001 log entry and CR-001 hashes recorded | 23 Oct 2026 | EXC-001 log and CF-0 section below |
| **CR-002 and EXC-002 approved**: one security-patch PR for DEF-0001 (`certifi`, `handlebars`; pre-existing on `main`, found by M0-T10's `security-check`) merges under P1 before M0-T10 | 23 Oct 2026 | Owner's answer, 23 Oct 2026 23:55 IST ("Separate patch PR first"); ROADMAP A-31; [DEF-0001](https://github.com/swa01wk/cenomi-dashboard-agent/issues/15) |
| **DEF-0001 patch merged** (PR #16, `6e813b3`), **HC-10 merged** (PR #17, `7544885`, spec set 0.1.5) and **M0-T10 merged** (PR #18, `5dae0a5`): all four EXC-001 bootstrap cards are in; EXC-001 and EXC-002 log entries recorded | 23–24 Oct 2026 | EXC-001 and EXC-002 logs below |

### CF-0 contract freeze (exact versions at `4515031`)

Specification set **0.1.0** (`specs/engineering/spec_set.yaml`). Hash = first 16 hex characters of the file's SHA-256 at `4515031`.

| File | Contract ID / schema | Hash |
|---|---|---|
| `specs/contracts/error_envelope.v1.schema.json` | `error_envelope.v1` | `7c622c005e30dfab` |
| `specs/contracts/error_codes.v1.yaml` | `cenomi.error_codes.v1` | `aea8f3e21881258d` |
| `specs/contracts/principal.v1.schema.json` | `principal.v1` | `c40cd9d39126d25a` |
| `specs/contracts/scope_decision.v1.schema.json` | `scope_decision.v1` | `35c1410ed2ec493d` |
| `specs/contracts/health_report.v1.schema.json` | `health_report.v1` | `c9c74101b712ab35` |
| `specs/contracts/dataset_descriptor.v1.schema.json` | `dataset_descriptor.v1` | `e7b470e6045cafe5` |
| `specs/engineering/make_targets.yaml` | `cenomi.make_targets.v1` (40 targets) | `21966e0b5d044534` |
| `specs/engineering/ci_checks.yaml` | `cenomi.ci_checks.v1` (15 jobs) | `00b5d68f9b52f641` |
| `specs/engineering/engineering.schema.json` | `engineering.schema.json` | `327ee65ba5f2e405` |
| `specs/engineering/spec_set.yaml` | `cenomi.spec_set.v1`, version 0.1.0 | `874a00a336b2fc61` |
| `specs/traceability/id_conventions.yaml` | `cenomi.id_conventions.v1` | `3656fda0f48e335b` |

The M0 corrections PR changes none of the contract files. Its only change to a CF-0 file is in `spec_set.yaml`: the version (0.1.0 → 0.1.1, required by that file's own patch rule for corrections) and the document list (the handoff is added). Every other CF-0 file is byte-identical. **CR-001 (2026-10-23)** amends `make_targets.yaml` (`backend-test SUITE=tooling`, `backend-lint` command), `ci_checks.yaml` (`ci/specs`) and `engineering.schema.json` (`manualResults`); the hashes above are those of `4515031`.

**CF-0 as amended by CR-001** (merged at `3c182cf`, PR #13, spec set 0.1.3). Files not listed are unchanged from `4515031`.

| File | Change | Hash at `3c182cf` |
|---|---|---|
| `specs/engineering/make_targets.yaml` | `backend-test SUITE=tooling`; `backend-lint` runs `import-linter lint` | `6daa6a4cd01d2cda` |
| `specs/engineering/ci_checks.yaml` | `ci/specs` installs browsers and runs `backend-test` with `SUITE=tooling` | `c1b270e160d701a9` |
| `specs/engineering/engineering.schema.json` | `manualResults`; optional `gateReport.manualResults`; `SUITE` in job env | `679f81ed9f69075c` |
| `specs/engineering/spec_set.yaml` | version 0.1.3 (later versions: 0.1.4 at `c582535`, CR-002; 0.1.5 at `7544885`, HC-10) | `b9aadc55b002ec15` |

## Milestones

| Milestone | Specs PR | Spec state | Build state | Slice cards | Gate | Blocked by |
|---|---|---|---|---|---|---|
| M0 Foundation | PR-M0 (items 1–12), merged `4515031`; PR #3 (corrections) | **Approved** (0.1.1) | **Authorized 2026-10-23** — not started | All M0 cards except M0-T09 (built before slice day 1, ED-06 A) | GATE-M0-01…14 (`plans/M0_FOUNDATION.md` §6) | Build authorization |
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
| CF-0 Toolchain | Repository layout; `error_envelope.v1`, `error_codes.v1`, `principal.v1`, `scope_decision.v1`, `health_report.v1`, `dataset_descriptor.v1`; codegen pipeline and schema subset; `specs/engineering/*`; ID conventions; CI check names | PR-M0 | **Frozen** 2026-10-22 (`4515031`); amended by CR-001 (2026-10-23) | 1 (+CR-001) |
| CF-1 Data | Tables (`core`, `meta`, `snap`, `seed_meta`); enums; metric YAML; permissions; scenarios; canonical figures | PR-M1 | — | — |
| CF-2 Analytics | metric query, `analysis_result.v1`, card view-models, records, `selection_ref.v1`, tokens | PR-M2 | — | — |
| CF-3 Agent | AnalysisPlan, tool schemas, AnswerDraft, fact tokens, evidence envelope, LLM adapter, thread and run contracts, `agent` tables, evaluation case schema v1 | PR-M3 | — | — |
| CF-4 Presentation | `cenomi.presentation.v1`, per-kind schemas, composition policy, AG-UI mapping, state shape, run endpoints | PR-M4 | — | — |
| CF-5 Insights | `insight.v1`, detector configuration schema, runner protocol, inbox API, `insights` tables | PR-M6 | — | — |
| CF-6 Evaluation | Benchmark composition, scoring (needs DR-036) | PR-M5 | — | — |

## Specifications

| # | Path | State | PR | Open questions |
|---|---|---|---|---|
| 1 | `docs/adr/0001`–`0006`, `0015`; `docs/adr/README.md` | Merged (`4515031`) | PR-M0 | — |
| 2 | `docs/reference/` (frozen copies) | Committed (PR #1); hash check specified in `make specs-check` | PR #1 / PR-M0 | — |
| 3 | `docs/design/DESIGN_BASELINE.md` | Merged (`4515031`) | PR-M0 | — |
| 4 | `docs/design/DECISION_REGISTER.md` | Merged (`4515031`) | PR-M0 | — |
| 5 | `docs/product/PRODUCT_SPEC.md` | Merged (`4515031`); 1.0.1 approved (PR #3) | PR-M0; PR #3 | OQ-PSPEC-01 |
| 6 | `docs/architecture/ARCHITECTURE.md` | Merged (`4515031`) | PR-M0 | OQ-ARCH-01, 02, 03 |
| 7 | `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` | Merged (`4515031`); 1.1 approved (DEVENV-R052–R056; PR #3) | PR-M0; PR #3 | — |
| 8 | `specs/contracts/` bootstrap (6 files); `specs/engineering/` (4 files); `specs/traceability/id_conventions.yaml` | **Merged and frozen (CF-0)**, `4515031` | PR-M0 | — |
| 9 | `AGENTS.md`, `.cursor/rules/*.mdc` (7 files) | Merged (`4515031`) | PR-M0 | — |
| 10 | `plans/ROADMAP.md` | Merged (`4515031`); A-27, A-28 approved (PR #3) | PR-M0; PR #3 | — |
| 11 | `plans/M0_FOUNDATION.md` (M0-T01…T11, GATE-M0-01…14): 1.0 with 83 acceptance tests merged; 1.1 with 85 approved (HC-1 to HC-5; PR #3) | Merged (`4515031`); 1.1 approved | PR-M0; PR #3 | — |
| 11b | `plans/M0_IMPLEMENTATION_HANDOFF.md` (non-normative sequencing guide for Composer) | Approved (PR #3) | M0 corrections | — |
| 11a | `docs/adr/0016`, `0017`, `0018` (ED-07, ED-08, ED-09) | Merged (`4515031`) | PR-M0 | — |
| 12 | `plans/STATUS.md` | This file | PR-M0 | — |
| 13–21 | DATABASE_SCHEMA, metric YAML (including the Properties set, ROADMAP A-09; T-31206 action items, A-10), KPI_CATALOG, permissions, SYNTHETIC_DATA_STRATEGY, scenarios, golden fixtures, ADR 0007/0008/0012, M1 plan | Not started | PR-M1 | OI-04, 05, 06, 14 |
| 22–26 | API_CONTRACTS, DESIGN_SYSTEM + tokens, card specs (PRODUCT_SPEC Appendix A), ADR-0011, M2 plan | Not started | PR-M2 | ECharts result; tokens per ADR-0018 |
| 27–31 | AGENT_ARCHITECTURE, AGENT_TOOLS, evaluation case schema + 20 questions, ADR-0009, DATABASE_SCHEMA amendment (`agent`), M3 plan | Not started | PR-M3 | OI-07, OI-10, OQ-ARCH-01 |
| 32–35 | AGUI_INTEGRATION, GENERATIVE_UI, ADR-0010, M4 plan | Not started | PR-M4 | ED-10; spike report; OQ-ARCH-02, 03 |
| 36–40 | PROACTIVE_INTELLIGENCE, detectors-1.1 + `insight.v1`, insight fixtures, ADR-0013, DATABASE_SCHEMA amendment (`insights`), M6 plan + SLICE_FIVE_DAY | Not started | PR-M6 | OQ-PSPEC-01 |
| 41–43 | EVALUATION_PLAN (benchmark, scoring, thresholds, performance — test taxonomy now in ARCHITECTURE, A-04), benchmark, ADR-0014 + M5 plan | Not started | PR-M5 | DR-036 / ED-11; OI-09 |

## Decisions

**Approved:**
- **HC-12** (2026-10-24): until M0-T04 implements `make e2e`, `ci/e2e` runs the Playwright harness specs in `tests/e2e/support` directly, so AT-M0-T11-05 is proven in CI. The earlier local `PASSED` for that AT came from an ad-hoc run's report file, not from a Make target (ARCH-R103, ROADMAP A-34)
- **HC-11** (2026-10-24): during the build window, the `ci/images` web image build records `NOT_IMPLEMENTED` while `apps/web/Dockerfile` (M0-T04) is absent; outside the window it fails (ARCH-R103, ROADMAP A-33)
- **HC-10** (2026-10-24): DECISION_REGISTER §2 is consistency-checked by M0-T10, not regenerated; the register data stays only in DECISION_REGISTER.md (ROADMAP A-32)
- GDQ-01…GDQ-12, Option A (2026-10-22)
- DXD-80…93
- The 17 batch defaults with final definitions (GDQ-10)
- The scope freeze
- ED-03 Option A, scoped (2026-10-22)
- **The ESP, with refinements (2026-10-22)**
- **ED-01 A, ED-02 A, ED-04 A, ED-05 A, ED-06 A and D-01 A (2026-10-22)**
- DR-035 superseded by ED-01
- **ED-07 A** (2026-10-22): fixture-user sign-in with signed httpOnly session cookies, limited to `dev`, `test` and `ci`; production fails closed; authorization and grants always enforced and validated on the backend (ADR-0016)
- **ED-08 A** (2026-10-22): scripted mock for unit tests, recorded replay for CI, separate controlled live evaluations; missing recordings fail rather than trigger live calls (ADR-0017)
- **ED-09 A** (2026-10-22): CSS Modules with shared design tokens and generated colour and spacing variables; Ink & Violet preserved (ADR-0018)
- **Protection policy P1/P2** with 0 required approving reviews (2026-10-22)
- **EXC-001**, conditionally, with conditions C1–C7 (2026-10-22)

**Remaining (not approved):**

| ID | Decision | Recommended | Needed before | Owner |
|---|---|---|---|---|
| ED-10 | AG-UI 1.0 pin (spike to confirm; see the correction in ROADMAP A-13) | A | PR-M4 | Owner |
| ED-11 | DR-036 evaluation scoring | A | PR-M5 | Owner |
| DR-036 | Evaluation scoring (the register's only open decision) | via ED-11 | PR-M5 | Owner |

**Configuration (not decisions):**
- GDQ-12: provider, primary and fallback model names, API key. Needed before slice day 3; optional for the M0 spike item L1. Stored as a secret, never committed.
- Live-evaluation credentials (`LIVE_EVAL_LLM_API_KEY`), separate from development keys.

## Repository protection (DEVENV §8.4, DEVENV-R056)

**Stage P1: applied and verified 2026-10-23.** The owner applied it through the GitHub web UI; Claude's own attempts were refused by the session's network proxy, so nothing was changed through it. Verification used read-only REST calls only, with no push to `main`. It ran at 2026-10-23 ≈ 05:14 UTC against `main` @ `77c9c10`.

| Check | Expected (DEVENV §8.4) | Observed |
|---|---|---|
| Repository; default branch; visibility | `swa01wk/cenomi-dashboard-agent`; `main`; public (unchanged) | As expected |
| Ruleset | One branch ruleset on `main` | ID **`25699552`**, "P1 main protection (DEVENV §8.4)", target `branch`, include `refs/heads/main`, exclude none |
| Enforcement | `active` | `active` |
| Bypass list | Empty | `bypass_actors: []` |
| Owner's token can bypass | `never` | `current_user_can_bypass: never` |
| Pull request required | Yes; 0 approvals; conversation resolution | `pull_request`: `required_approving_review_count: 0`, `required_review_thread_resolution: true`; stale-dismissal, code-owner, last-push and extra-approval options all `false`; `allowed_merge_methods: [squash]` |
| Force pushes blocked | Yes | `non_fast_forward` |
| Deletion blocked | Yes | `deletion` |
| Required status checks (P2) | **Not yet** | None (no `required_status_checks` rule) |
| Rules effective on `main` (`GET /rules/branches/main`) | The three rules above | `deletion`, `non_fast_forward`, `pull_request`, all from ruleset `25699552`; branch reports `protected: true` |
| Repository merge settings | Squash only; delete head branches | `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false`, `delete_branch_on_merge: true`; `allow_auto_merge: false` (unchanged) |
| Ruleset timestamps | Recorded for GATE-M0-10 | `created_at` 2026-10-23T05:12:06.119Z; `updated_at` **2026-10-23T05:12:06.154Z** |

Any later change to the ruleset or merge settings must be recorded here with its reason. GATE-M0-10 compares `updated_at` and the live settings with this record. The "settings applied together with P1" table (Actions pinning policy, secret scanning and push protection, Dependabot alerts, `live-eval` environment) was outside the 2026-10-23 authorization and is **not applied**; it remains an owner action. **Stage P2:** not applied, by design, until M0-T07 merges.

## Exceptions (DEVENV-R051)

| ID | Scope | Reason | Compensating controls | Expires | State |
|---|---|---|---|---|---|
| EXC-001 | Merges of exactly the M0-T01, M0-T03, M0-T11 and M0-T10 PRs under protection stage P1, before `ci/summary` exists | These cards build the tooling CI runs; GitHub cannot require a check that has never reported | Conditions C1–C7 (DEVENV §8.4): PRs documented; every available local validation before merge; merge SHA and controls recorded; M0-T07 authored early as a draft PR (C4, `plans/M0_FOUNDATION.md` §3); retroactive GitHub Actions verification once CI exists; that verification required before GATE-M0; no expansion without approval | When stage P2 is in force | **Approved conditionally, 2026-10-22** |
| EXC-002 | Merge of exactly one security-patch PR, `fix/def-0001-security-advisories` (DEF-0001, CR-002), under P1 before `ci/summary` exists | ADR-0003 §2 requires a CI run for a security patch, but CI arrives with M0-T07, whose `ci/security` cannot pass while the advisories are open | EXC-001 C1–C3 and C6 unchanged (EXC-002 log below); C5 = M0-T07 PR run with `ci/security` `success`, then the first `ci/summary` on `main` (DEVENV §8.4) | On merge of that PR, or when P2 is in force | **Approved, 2026-10-23; expired on merge** (`6e813b3`, 2026-10-23T18:48:25Z); C5 pending |

**EXC-001 log (conditions C1, C3 and C5).** Filled in as each PR opens and merges. GATE-M0-10 checks that it is complete. From 2026-10-23 on, the architect reviews each pushed card branch and opens its PR with the full description, including the C2 evidence, before the owner merges. Squash titles keep the PR title `M<n>-T<nn>: …` (DEVENV-R038).

| Card | PR | Branch | Local validations pasted (C2) | Merge SHA (C3) | Compensating controls applied (C3) | Retroactive CI verification (C5) |
|---|---|---|---|---|---|---|
| M0-T01 | [#6](https://github.com/swa01wk/cenomi-dashboard-agent/pull/6) | `chore/m0-t01-repo-scaffold` | Partial at merge time: verbatim local output for `108f733` (`make install` clean, `doctor`, `help`, `check`, 7/7 ATs) and Cursor's reported green run for `5abf172`. The PR had an empty description when merged; the evidence was added afterwards (2026-10-23) | **`75a2fed`** (squash title "Chore/m0 t01 repo scaffold (#6)", not the DEVENV-R038 format; PR title corrected afterwards) | Architect review before merge, with 4 findings fixed in `5abf172` (pin policy, AT-07 no skip, no-op scripts removed, targets drift test); tree verified identical to the reviewed commit | Pending (C5) |
| M0-T03 | [#9](https://github.com/swa01wk/cenomi-dashboard-agent/pull/9) | `feat/m0-t03-backend-skeleton` | Yes: owner's log at 2026-10-23T07:54:52Z on `d7a7020` (`make install` clean; doctor; backend-lint; backend-typecheck; backend-test unit 10/10 and integration 5/5; `make check`; 11 tooling tests), pasted in PR §8 | **`0027aae`** (squash title in DEVENV-R038 format) | Architect review with 7 findings fixed in `d7a7020`; independent ruff, format and SQL-safety re-run on the export; tree verified identical to the reviewed commit. Accepted: formatting-only edits to M0-T01's `scripts/make/**`, needed because `backend-lint` covers `scripts/` | Pending (C5) |
| M0-T11 | [#12](https://github.com/swa01wk/cenomi-dashboard-agent/pull/12) | `test/m0-t11-test-harness` | Yes: owner's run on `6e78f7a`, clean tree before and after (`make install` clean; doctor; backend-lint; backend-typecheck; backend-test unit 10 and integration 5; `make check`; tooling suite 29 passed including AT-M0-T01-01; `quarantine_expiry.py` passed), pasted in PR §8. An earlier run made before the commit was discarded | **`386f017`** (squash title in DEVENV-R038 format) | Architect review before the PR was opened; tree of `386f017` verified identical to the reviewed head `6e78f7a`. Its bootstrap ATs run under `backend-test SUITE=tooling` once M0-T10 and M0-T07 implement CR-001 | Pending (C5) |
| M0-T10 | [#18](https://github.com/swa01wk/cenomi-dashboard-agent/pull/18) | `chore/m0-t10-governance-automation` | Yes: owner's full handoff §11 step-5 run at `f18d860` (install clean; doctor; lint; typecheck; unit 10, integration 5, tooling 104; specs-check; `make check`; security-check; `trace-report CARD=` T01 7, T03 10, T11 8, T10 7 PASSED; clean tree), plus a re-run at the final `6ccc14e` (tooling 106, lint, typecheck, security-check), pasted in PR §8 | **`5dae0a5`** (squash title in DEVENV-R038 format) | Three architect review rounds before the PR (vacuous AT tests, manual-AT detection, register data in code resolved by HC-10, invalid defect form, licence and pip-audit defects, gate-mode gaps); tree of `5dae0a5` verified identical to the reviewed `6ccc14e`. Accepted: `scripts/__init__.py` (outside field 13, needed by M0-T03's mypy run) and every fixable pip-audit finding blocking (PyPI data has no severity) | Pending (C5) |
| C5 (a): M0-T07 PR run, `trace-report CARD=…` for all four | — | — | — | — | — | — |
| C5 (b): first `ci/summary` run on `main` after M0-T07 merges | — | — | — | — | — | — |

**EXC-002 log (conditions C1, C3 and C5).**

| PR | Branch | Local validations pasted (C2) | Merge SHA (C3) | Compensating controls applied (C3) | Retroactive CI verification (C5) |
|---|---|---|---|---|---|
| [#16](https://github.com/swa01wk/cenomi-dashboard-agent/pull/16) | `fix/def-0001-security-advisories` | Yes: owner's run on `38d4e57` (baseline and post-patch audits; install clean; doctor; lock checks; lint; typecheck; unit 10, integration 5, tooling 29; `make check`; four-file diff; clean tree), pasted in PR §8 | **`6e813b3`** (squash title `DEF-0001: …`) | Architect review; squash diff verified identical to the reviewed `38d4e57`; exact upstream pin of `handlebars` 4.7.9 by `@boundaries/elements` overridden to 4.7.10 with the rationale recorded in the PR; [DEF-0001](https://github.com/swa01wk/cenomi-dashboard-agent/issues/15) closed. EXC-002 expired on this merge | Pending: (a) M0-T07 PR run `ci/security`; (b) first `ci/summary` on `main` |

## Open questions (non-blocking)

| ID | Question | Default | Decide in | Owner |
|---|---|---|---|---|
| OQ-ARCH-01 | Where the evidence envelope and fact-token verifier live, so that `insights` does not depend on `agent` | `insights` may import `cenomi.agent.evidence` only | PR-M3 | Architect |
| OQ-ARCH-02 | Full script CSP with nonces | Baseline headers only | PR-M4 | Architect |
| OQ-ARCH-03 | AG-UI interrupt outcome vs the DX4 A8 fallback for filter proposals and clarification | DX4-AGUI stands | PR-M4 (after spike) | Architect |
| OQ-PSPEC-01 | Bell visibility for the tenant persona | Tenant reaches the inbox from the rail | PR-M6 | Architect, owner if it changes design |
| OQ-DEVENV-01 | ~~`lint-imports` vs `import-linter lint` wording~~ | **Resolved by CR-001** (2026-10-23) | — | — |

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
| CR-002 | 2026-10-23 | Security patch before CI (DEF-0001, ADR-0003 §2): a security-patch PR may add one `exclude-newer-package` entry under `[tool.uv]` for the package it patches (`certifi`, fix newer than `exclude-newer`), and one exact-version `overrides` entry in `pnpm-workspace.yaml` for a transitive package (`handlebars`); both lockfiles regenerated per DEVENV-R052. Each entry cites the CR and advisory; the `certifi` entry is removed when `exclude-newer` next moves past it. Changes no CF-0 contract (`spec_set.yaml` version only) | ROADMAP A-31; DEVENV §8.4 (EXC-002), §8.6 | **Approved** by the owner 2026-10-23 |
| CR-001 | 2026-10-23 | Amends CF-0 (`make_targets.yaml`, `ci_checks.yaml`, `engineering.schema.json`): (1) `backend-test SUITE=tooling` runs `tests/tooling` in `ci/specs` with browsers (HC-8); (2) manual-AT results go in `plans/gates/M<n>-manual-results.json` (`manualResults`), excluded from `CARD`, required in `GATE` (HC-9); (3) `backend-lint` runs `import-linter lint` (OQ-DEVENV-01) | ROADMAP A-30; ARCH-R083; M0-T07, M0-T10 | **Approved** by the owner 2026-10-23 (HC-8, HC-9) |

## Blockers and risks

| ID | Blocker or risk | Owner | Since | Next action |
|---|---|---|---|---|
| B-01 | ~~ESP not approved~~ — **resolved 2026-10-22** | — | — | — |
| B-02 | ~~ED-01, 02, 04, 05, 06 undecided~~ — **resolved 2026-10-22** | — | — | — |
| B-03 | ~~Migration PR not merged~~ — **resolved 2026-10-22** (`d5db7f3`) | — | — | — |
| B-04 | OI-13: the DX5-GenUI "overdue" wording fix exists in the exported boards only | Architect | 2026-10-22 | Exported boards are authoritative; no action |
| B-05 | ~~PR-M0 awaiting owner review~~ — **merged 2026-10-22** (`4515031`) | — | — | — |
| B-08 | ~~M0 corrections PR awaiting review~~ — **approved 2026-10-23** (PR #3) | — | — | — |
| B-06 | ~~ED-07, ED-08, ED-09 undecided~~ — **resolved 2026-10-22** (Option A) | — | — | — |
| B-07 | ~~`main` has no branch protection~~ — **P1 applied 2026-10-23 by the owner and verified** (evidence below). P2 is still to be applied immediately after M0-T07 merges; it is verified the same way (DEVENV-R056) | Owner | 2026-10-22 | Apply P2 after M0-T07 |
| R-01 | Scope squeezed into five days | Owner, Architect | GD | Keep slice and full scope separate (ROADMAP §8) |
| R-02 | Seed or metric drift from the canonical figures | Developer | GD | GI invariants and replay hash in CI |
| R-04 | Ungrounded numbers or causal wording | Developer | GD | Fact tokens, verifier, banned-term lint |
| R-09 | Composer makes architectural choices where specifications are thin | Architect | GD | Cursor-ready criteria; AGENTS.md; 20-field task cards; stop-and-report rule |
| R-14 | Single developer | Owner | GD | Specifications complete before slice day 1 |

The full risk register is in `docs/reference/final-design-gate/08_OPEN_ISSUES_AND_RISKS.md`.

## Next tasks (dependency order)

1. ✅ ED-07, ED-08 and ED-09 decided (Option A) and recorded in ADR-0016, ADR-0017 and ADR-0018. EXC-001 approved conditionally; P1/P2 policy approved.
2. ✅ PR-M0 merged (`4515031`); CF-0 frozen. HC-1 to HC-5 approved 2026-10-23.
2a. ✅ PR #3 approved (spec set 0.1.1).
3. ✅ Protection stage P1 applied and verified 2026-10-23 (ruleset `25699552`). P2 follows immediately after M0-T07 merges, verified the same way.
4. ✅ Owner authorized the M0 build on 2026-10-23 (ADR-0015 §3). Composer implements M0-T01…T11 one card per PR, following the M0 implementation handoff; the M0-T09 spike report merges through a docs PR. The EXC-001 log above is filled in as the bootstrap PRs merge.
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
| Specification set | **0.1.7** in review (HC-12); **0.1.6** at `795695e` (HC-11); **0.1.5** at `7544885` (HC-10); **0.1.4** at `c582535` (CR-002); **0.1.3** at `3c182cf` (CR-001); 0.1.2 at `ccdc276`; 0.1.1 at `77c9c10`; 0.1.0 at `4515031` (CF-0) |
| Planning Assessment | v0.3 (G0) |
| Dataset | `sd-2026.10.20-01` |
| Detectors | detectors-1.1 |

## Completion criteria for the current milestone (M0 specifications)

- [x] ESP approved (2026-10-22, with refinements)
- [x] Migration PR merged into `main` (`d5db7f3`)
- [x] ED-01, ED-02, ED-03, ED-04, ED-05, ED-06, D-01 decided
- [x] Repository write path agreed (ED-01 A)
- [x] PR-M0 items 1–12 drafted and self-reviewed (consistency audit in the PR description)
- [x] PR-M0 reviewed and approved for merge by the owner (2026-10-22)
- [x] ED-07, ED-08, ED-09 decided (Option A, 2026-10-22)
- [x] PR-M0 merged (`4515031`); CF-0 frozen
- [x] Corrections HC-1 to HC-5 approved (2026-10-23)
- [x] M0 corrections approved and merged (PR #3, `77c9c10`, spec set 0.1.1)
- [x] Protection stage P1 applied and verified (ruleset `25699552`, 2026-10-23)
- [x] Owner's M0 build authorization (2026-10-23, 10:46 IST)

Last reviewed: **2026-10-23**. Next: M0-T07 draft, then M0-T11 → M0-T10. `active_milestone` stays `M0` (ARCH-R103).
