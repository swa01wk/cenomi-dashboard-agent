# M0 Implementation Handoff — Cursor Composer 2.5

| | |
|---|---|
| Version | 1.7 · 2026-10-25. Records the build state after M0-T02 and CR-003/CR-004, and adds the prompts for every remaining M0 card: M0-T05 (§13), M0-T08 (§14), M0-T06 (§15), M0-T04 (§16) and the M0-T09 spike (§17), with CR-005, plus the run order to GATE-M0 (§18). 1.6 · 2026-10-24. §11 renderer bullet updated for HC-10. 1.5 · 2026-10-23. Adds the DEF-0001 security-patch prompt (§12; CR-002, EXC-002) and the M0-T10 rebase step. 1.4 · 2026-10-23. Adds the M0-T10 kickoff prompt (§11) with CR-001 (HC-8 tooling suite, HC-9 manual ATs). 1.3 · 2026-10-23. Adds HC-6 and HC-7 (ROADMAP A-29), the M0-T03 and M0-T07 kickoff prompts (§9, §10) and the review-then-PR workflow. Version 1.2 added lockfile serialization, protection verification and the M0-T01 kickoff; 1.1 applied HC-1 to HC-5 (A-27); 1.0 (2026-10-22) was delivered outside the repository |
| Nature | **Non-normative.** A sequencing and orientation guide. It restates no contract. If it disagrees with a specification, the specification wins (AGENTSMD-R003) |
| Baseline | `main` @ `e1db045` (PR #32), spec set **0.1.8**. The PR that adds this version also brings CR-005 (spec set **0.1.9**), which the M0-T08, M0-T04 and M0-T09 prompts check for |
| Build state | **In progress** (authorized 2026-10-23). Merged: M0-T01, T03, T11, T10, T07, T02 (6 of 11). P1 and P2 (`ci/summary` required, strict) in force; EXC-001 expired. `plans/STATUS.md` is authoritative |

---

## 1. Prerequisites (owner)

| # | Action | Blocks |
|---|---|---|
| O-1 | ✅ PR #3 (corrections, spec set 0.1.1) approved and merged | — |
| O-2 | ✅ (2026-10-23, ruleset 25699552) **Apply protection stage P1** on `main` (DEVENV §8.4, DEVENV-R056): (a) a ruleset targeting `main` with enforcement **active** and an **empty bypass list**, requiring a PR (0 approvals), resolved conversations, and blocking force pushes and deletion; (b) repository merge settings: squash only (disable merge commits and rebase merging), delete head branches; (c) the companion settings table. **Verify without pushing:** record the ruleset ID, `bypass_actors: []`, `current_user_can_bypass` = `never`, the `GET /repos/swa01wk/cenomi-dashboard-agent/rules/branches/main` output, the merge settings and `updated_at` in STATUS | The first card merge |
| O-3 | ✅ (2026-10-23) Give Cursor the explicit M0 build authorization, pointing it at `AGENTS.md`, `.cursor/rules/` and this guide | Everything |
| O-4 | *Optional:* GDQ-12 configuration as a local secret | Spike item L1 only |
| O-4a | *Recommended:* give Composer a fine-grained personal access token for this repository only, with Contents and Pull requests write and **no Administration** permission (DEVENV-R056) | — |
| O-5 | ✅ (2026-10-24T20:08:01Z) **Apply P2** (`ci/summary` required, strict) as soon as M0-T07 has merged and `ci/summary` is `success` on `main`; verify it the same way as P1 | Every merge after M0-T07 |

---

## 2. Cards and dependencies (from `plans/M0_FOUNDATION.md` v1.2, field 6)

| Card | Title | h | Merge depends on | ATs | Merges under |
|---|---|---|---|---|---|
| M0-T01 | Repository scaffold, toolchain, Makefile contract | 1.5 | — | 7 | P1 + EXC-001 |
| M0-T03 | Backend skeleton | 2.0 | T01 | 10 | P1 + EXC-001 |
| M0-T11 | Test harness, traceability markers, CI reporting | 1.0 | T01, T03 | 8 | P1 + EXC-001 |
| M0-T10 | Governance automation | 1.5 | T01, T11 | 7 | P1 + EXC-001 |
| M0-T07 | GitHub Actions workflows | 1.5 | T01, T03, T10, T11 | 8 | P1 (own run green) |
| M0-T02 | Compose (db, migrate, seed, api, otel), PostgreSQL bootstrap, migrations | 1.5 | T01, T03, T11 | 11 | P2 |
| M0-T05 | Contract pipeline (CF-0) | 1.5 | T01, T03 | 6 | P2 |
| M0-T08 | ECharts 5.6.0 verification harness | 1.0 | T01, T11 | 5 | P2 |
| M0-T06 | Dev sign-in, sessions, AccessScope interface (API level) | 1.0 | T03, T05 | 7 | P2 |
| M0-T04 | Web shell, sign-in journeys, Compose `web` service | 1.5 | T01, T02, T05, T06, T11 | 12 | P2 |
| M0-T09 | AG-UI 1.0 verification spike (throwaway) | 2.5 | T01 | 4 (manual) | Report via a docs PR |

**85 acceptance tests**, about 15.5 h (HC-7 added the Make recipes). The graph is acyclic; the T04 ↔ T06 cycle was removed by HC-2.

```
T01 ──┬─▶ T03 ──┬─▶ T11 ──┬─▶ T10 ──▶ T07 ══(P2)══╗
      │         │         ├─▶ T08 ◀═════════════════╣
      │         │         └─▶ T02 ◀═════════════════╣
      │         └─▶ T05 ◀═══════════════════════════╝
      │               └─▶ T06 ──▶ T04 ◀── T02, T11
      └─▶ T09 (spike; report via docs PR)
──▶ merge dependency (field 6)      ══▶ process gate: merges only after T07 + P2
```

---

## 3. Execution order

```
O-2 P1 applied and verified → O-3 authorized
Wave 0  T01                         merge under P1 + EXC-001
        ├─ T09 spike (parallel, any time)
        └─ T07 authoring starts; draft PR rebased after each bootstrap merge (EXC-001 C4)
Wave 1  T03 → T11 → T10              strictly sequential, P1 + EXC-001
Wave 2  T07: own run ci/summary success + trace-report CARD= for T01/T03/T11/T10 (C5a)
        merge → ci/summary success on main (C5b) → O-5 apply P2
Wave 3  T02 ║ T05 → T08             branches in parallel under P2; T05 and T08 PRs serialized
                                     (pnpm-lock.yaml, DEVENV-R055 (a)): merge T05, then rebase T08 onto main,
                                     regenerate the lockfile, re-run make install / make check / field-14 targets
Wave 4  T06                          after T05
Wave 5  T04                          after T02 and T06
Gate    milestone-gate.yml → GATE-M0-01…14 → owner approval
```

**Must be sequential:** T01 → T03 → T11 → T10 → T07 → P2. Also T05 → T06 → T04, and T02 → T04 (T04 adds the `web` service to the Compose file that T02 creates).

**May run in parallel:**
- T09 with everything, after T01.
- T07 *authoring* with T03, T11 and T10. It *merges* only after T10.
- T02, T05 and T08 as *branches*. Their authoring may start once their merge dependencies are on `main`; they merge only after P2. Only one PR changing `pnpm-lock.yaml` may be open at a time, so T08's PR opens after T05 merges (DEVENV-R055 (a)).
- T02 with T06.

---

## 4. Shared-file ownership (DEVENV §8.6)

- **Most specific path wins (DEVENV-R053).** An exact path beats a pattern, and a longer literal prefix beats a shorter one. Broad globs never cover files another card names.
- **Lockfiles (DEVENV-R052).** A card that introduces a dependency it names regenerates `pnpm-lock.yaml` or `backend/uv.lock` and edits only its own package manifest. Lockfiles are never hand-edited. A clean `make install` must leave `git status` clean.
- **Composition points (DEVENV-R054):**
  - `Makefile` recipes of the card's own targets: T02, T05, T08, T10;
  - the `web` service in `docker-compose.yml`: T04;
  - the router registration in `create_app()`: T06;
  - the health provider binding and the `db` CLI sub-command: T02;
  - the `pytest_plugins` entry in `backend/tests/conftest.py`: T02;
  - the `[tool.pytest.ini_options]` section in `backend/pyproject.toml`: T11.

  No M0 card changes `.github/workflows/**` after T07, or `.env.example` after T01.
- **Parallel lanes (DEVENV-R055).**
  - **Lockfiles:** at most one open PR, draft or ready, per lockfile. T05 opens and merges first. T08 keeps its `echarts` change on its branch, then rebases onto the updated `main`, regenerates `pnpm-lock.yaml` with pnpm, re-runs `make install`, `make check` and its field-14 targets, and only then opens its PR.
  - **Makefile recipes** (T02, T05, T08): open PRs may overlap, because they change disjoint targets; each PR names the others, and later PRs rebase.

---

## 5. Responsibilities by area

| Area | Cards | Normative source |
|---|---|---|
| Makefile | T01 builds all 40 targets and the result helper. Each M0 target has exactly one owner card that replaces its stub (M0 plan §3 target-owner table, HC-7): T02 db/stack, T03 backend-*, T04 frontend-* and `e2e`, T05 `codegen`, `contracts-check`, `integration-test`, T07 `ci`, T08 `echarts-gate`, T10 `specs-check`, `trace-report`, `security-check` | `make_targets.yaml`; DEVENV §5; ARCH §10.8 |
| Docker Compose | T02 (db, migrate, seed, api, otel; `backend/Dockerfile` from T03); T04 (`web` service and `apps/web/Dockerfile`) | DEVENV §6 (R016, R017) |
| Database | T02: roles, six empty schemas, revision 0001, guards DG-1…DG-5 | ADR-0006; ARCH §7 |
| Backend | T03 skeleton and core; T05 contracts; T06 auth and session routes; T02 `cenomi.db` | ARCH §5, §9; ADR-0005; ADR-0016 |
| Frontend | T04 shell, routes, data client, boundaries, provisional `shell.css`, sign-in browser journeys; T11 test configuration | ARCH §6; PRODUCT_SPEC §3; ADR-0018 |
| Agent interfaces | T03: empty agent packages and the `LLM_MODE` setting (`off`, `replay`, `live`). T11: agent markers. T07: guarded `eval-live.yml`. T09: the spike report. **No runtime, provider or AG-UI code in M0** | ARCH §8; ADR-0017; DEVENV-R004 |
| Tests | Each card's field 15, tagged with AT IDs; T11 frameworks; T10 `trace-report` | ARCH §10; AGENTSMD-R007, R008 |
| CI | T07: 15 jobs, `ci/summary` fail-closed, no secrets in PR workflows, images built but not pushed | `ci_checks.yaml`; DEVENV §7; ADR-0015 |

---

## 6. EXC-001 compensating controls (bootstrap cards T01, T03, T11, T10)

| Condition | Control |
|---|---|
| C1 | PR number, branch and title entered in the STATUS EXC-001 log when the PR opens |
| C2 | Every available local validation pasted before merge: `make check`, the field-14 targets and the AT results; `make trace-report CARD=…` once T10 exists |
| C3 | Squash SHA and the controls actually applied logged after the merge |
| C4 | T07 drafted early and rebased after each bootstrap merge, as non-required Actions evidence |
| C5 | (a) The T07 PR run shows all four cards' `trace-report` results `PASSED`. (b) The first `ci/summary` run on `main` after T07 is `success`. Both run URLs are logged |
| C6 | GATE-M0-10 fails without C5 and a complete log |
| C7 | No other card merges before P2; no expansion without a new owner-approved exception |

---

## 7. Composer readiness checklist

- [x] PR #3 merged; spec set 0.1.1
- [ ] P1 applied on `main` and verified **through the rules API**, never by a test push (DEVENV-R056); evidence in STATUS
- [ ] Owner's M0 build authorization recorded in STATUS
- [ ] Composer opened at the repository root with `AGENTS.md` and `.cursor/rules/*.mdc` loaded
- [ ] One card per Composer session and per branch; branch names follow `id_conventions.yaml`, for example `chore/m0-t01-repo-scaffold`
- [ ] Composer reads all 20 fields of the card and every spec and contract named in fields 2 and 11
- [ ] Composer touches only field-13 paths plus the DEVENV-R052 and R054 exceptions; anything else means stop and report
- [ ] Every AT is a tagged test and `PASSED`; nothing is marked `NOT_APPLICABLE` by hand
- [ ] PR template fully filled in, with `make check` output, shared files listed, and screenshots for UI cards
- [ ] Bootstrap PRs follow EXC-001 C1–C3
- [ ] The owner merges (squash); Composer never merges or changes settings

**Kick-off prompt (per card):**

> Implement task card **M0-Txx** from `plans/M0_FOUNDATION.md` on branch `<branch>` from the latest `main`. Follow `AGENTS.md` and `.cursor/rules/`. Read all 20 fields, then every spec and contract in fields 2 and 11. Touch only field-13 paths, plus lockfiles for dependencies the card names (DEVENV-R052) and the listed composition points (DEVENV-R054). Implement every field-15 acceptance criterion as a test carrying its AT ID. Add nothing the card does not name. On any ambiguity, conflict or out-of-scope path: stop and report in the PR. Finish with `make check`, the field-14 targets and `make trace-report CARD=M0-Txx` (once M0-T10 exists), and fill every PR template section.

---

## 8. M0-T01 — exact kickoff prompt

M0-T01 is ready: its 20 fields are complete; its contracts (`make_targets.yaml`, DEVENV §3–§4, ARCH §10.8) are frozen in CF-0; its last-line format is aligned with `make_targets.yaml`; its completion gate states the EXC-001 evidence. Branch: `chore/m0-t01-repo-scaffold`. Merges under P1 + EXC-001.

> You are implementing task card **M0-T01 — Repository scaffold, toolchain and Makefile contract** for the Cenomi Dashboard Intelligence Agent POC. The owner has authorized the M0 build (see `plans/STATUS.md`); if STATUS does not show that authorization, stop and report.
>
> 1. Create branch `chore/m0-t01-repo-scaffold` from the latest `main`.
> 2. Read, in this order: `AGENTS.md`; `.cursor/rules/*.mdc`; `plans/M0_FOUNDATION.md` §2, §3 and the full M0-T01 card (all 20 fields); `specs/engineering/make_targets.yaml` (normative: exact 40 targets, order, arguments, exit codes, result vocabulary and the `<RESULT>: <target> — <reason>` last line); `specs/engineering/spec_set.yaml`; `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` §2–§5 and §8.6; `docs/architecture/ARCHITECTURE.md` §10.8 (ARCH-R101–R105); ADR-0003 (versions and pin policy).
> 3. Implement only field 5 "In" and fields 7–8: root configuration files; the uv workspace in `backend/` with exactly the field-7 dependencies; the pnpm workspace with empty `apps/web`, `packages/contracts-ts` and `packages/viz` skeletons and exactly the field-8 dev tooling; committed lockfiles; `.env.example` with every DEVENV §4 variable and recognisably fake placeholders; the root `Makefile` with all 40 targets in YAML order, the result helper appending to `tests/reports/status.jsonl`, `make help` generated from `##` comments; `scripts/make/` helpers; `scripts/tools.lock`. Targets owned by later cards are stubs that report `NOT_IMPLEMENTED` within the build window; targets with `active_from` later than M0 report `NOT_APPLICABLE`.
> 4. Touch only the field-13 paths. No application code, Compose, workflows, migrations or extra dependencies. Versions follow DEVENV-R004: the newest release at least 14 days old within the approved line.
> 5. Write `tests/tooling/test_make_contract.py` with one test per acceptance criterion **AT-M0-T01-01 … AT-M0-T01-07**, each tagged `@pytest.mark.trace("AT-M0-T01-0n", reqs=[…])` as AGENTSMD-R007 requires. M0-T11 later registers the marker and its plugin; until then pytest only warns. Do not build the plugin here.
> 6. Run locally and paste the output into the PR: `make install` (clean clone; `git status` stays clean), `make doctor`, `make help`, `make check`, and `uv run pytest tests/tooling/test_make_contract.py -v`. This is EXC-001 condition C2; there is no CI yet.
> 7. Open the PR titled `M0-T01: Repository scaffold, toolchain and Makefile contract`, filling every section of the PR template in DEVENV §8.2 (the template file itself arrives with M0-T10). State that the PR merges under P1 + EXC-001, list each dependency with its reason and licence, and list the shared files created.
> 8. If anything is ambiguous, conflicts with a specification, or needs a path outside field 13: stop and report in the PR. Never resolve it yourself, never weaken a test, never merge, and never change repository settings.

---

## Workflow from M0-T03 on (owner, 2026-10-23)

1. The owner creates the card branch from the latest `main` and runs the Composer prompt.
2. Composer implements, runs the local validation and commits. **Composer does not push or open the PR.**
3. The owner pushes the branch from a local terminal.
4. The architect (Claude) reviews the pushed code against the card. If fixes are needed, the architect provides a fix prompt; otherwise the architect opens the PR with the full description: the 15 template sections, the EXC-001 C2 evidence where applicable, and the review result.
5. The owner merges with **Squash and merge**, keeping the PR title `M<n>-T<nn>: …` as the squash title (DEVENV-R038).
6. The architect records EXC-001 log entries (bootstrap cards) through a documentation PR.
7. **Since P2 (2026-10-24):** every PR needs a green, up-to-date `ci/summary` before merge. STATUS entries, defect records and specification changes go through documentation PRs, because `main` is protected. The owner may share local logs with `gh run view <id> --log-failed` when CI fails, since the architect's environment cannot download Actions logs.

---

## 9. M0-T03 — kickoff prompt

**Prerequisite:** the HC-6/HC-7 documentation PR (spec set 0.1.2) is merged. Branch: `feat/m0-t03-backend-skeleton`. Merges under P1 + EXC-001.

> You are implementing task card **M0-T03 — Backend skeleton: modules, core, errors, health and logging** for the Cenomi Dashboard Intelligence Agent POC. The M0 build is authorized (`plans/STATUS.md`). If STATUS does not show spec set 0.1.2, stop and report.
>
> 1. Work on branch `feat/m0-t03-backend-skeleton`, created from the latest `main`. M0-T01 is already merged.
> 2. Read, in this order: `AGENTS.md`; `.cursor/rules/*.mdc` (especially `10-backend.mdc`); `plans/M0_FOUNDATION.md` §3 (including the Make target-owner table) and the full M0-T03 card (all 20 fields); `docs/architecture/ARCHITECTURE.md` §5 (R002–R034, including the routes and the error, request-ref, settings and CLI conventions), §9 and §13 (R096–R099); ADR-0004 and ADR-0005; `specs/contracts/health_report.v1.schema.json`, `dataset_descriptor.v1.schema.json`, `error_envelope.v1.schema.json` and `error_codes.v1.yaml`; `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` §4 (variables) and §8.6 (DEVENV-R052–R055); `specs/engineering/make_targets.yaml` (the `backend-format`, `backend-lint`, `backend-typecheck` and `backend-test` entries).
> 3. Implement field 5 "In", field 7 and the field-12 tasks:
>    - the `cenomi` package under `backend/src/cenomi/` with the 12 modules, each with a README (ARCH-R004);
>    - `core`: settings with the ARCH-R026 startup validation, JSON logging with redaction, OpenTelemetry, errors, clock and ids;
>    - the `api` app factory `create_app()`, the routers `health` and `dataset`, the exception handlers and the request-ref middleware;
>    - the `cenomi` console script with argparse at `cenomi.cli.main:main` (ARCH-R034);
>    - `backend/.importlinter` (ARCH-R006/R007); `scripts/lint/sql_safety.py`; `backend/Dockerfile` (non-root, uv);
>    - the health check calls a `check_database()` provider through the health wiring; M0-T02 binds the real implementation later, and the tests use a test double (AT-M0-T03-02, -03).
> 4. Do **not** create `backend/src/cenomi/db/`, `auth/` or `contracts/` content (M0-T02, T06, T05). Responses must validate against the JSON schemas in `specs/contracts/`; validate them in tests with `jsonschema`, not with Pydantic contract models.
> 5. Shared files, and only in these ways (DEVENV-R054, HC-6):
>    - in `backend/pyproject.toml`: `[build-system]` with `uv_build` within the pinned uv minor line; `[tool.uv] package = true`; `[tool.uv.build-backend] module-name = "cenomi"`; `[project.scripts] cenomi = "cenomi.cli.main:main"`; `[tool.ruff]` and `[tool.mypy]` (strict). Do not touch `required-version` or `exclude-newer`. Add no dependency outside card field 7 (all were installed by M0-T01).
>    - in the root `Makefile`, through `scripts/make/`: replace only the stubs of `backend-format`, `backend-lint`, `backend-typecheck` and `backend-test` with the YAML behaviour. `backend-test` writes JUnit to `tests/reports/backend/`.
>    - If `uv lock` must change, regenerate it with uv (DEVENV-R052); never edit it by hand. If `uv_build` cannot be resolved under the `exclude-newer` cutoff, stop and report.
> 6. Write the field-14 tests for **AT-M0-T03-01 … AT-M0-T03-10**, each tagged `@pytest.mark.trace("AT-M0-T03-nn", reqs=[…])`. Expected values come from the contracts and specs, never from the code under test (AGENTSMD-R008).
> 7. Run locally and save the output (EXC-001 C2): `make install && git status --porcelain`, `make doctor`, `make backend-lint`, `make backend-typecheck`, `make backend-test SUITE=unit`, `make backend-test SUITE=integration`, `make check`, `uv run --directory backend lint-imports`, and `uv run cenomi --help`.
> 8. Commit with messages starting `M0-T03:`. **Do not push and do not open a PR.** The owner pushes, and the architect reviews and opens the PR.
> 9. If anything is ambiguous, conflicts with a specification, or needs a path outside field 13 and the HC-6 sections: stop and report. Never resolve it yourself, never weaken a test, never merge, and never change repository settings.

---

## 10. M0-T07 — draft kickoff prompt (EXC-001 C4)

M0-T07 may be **authored now**, in parallel with M0-T03, M0-T11 and M0-T10, on its own branch. It is pushed as a **draft PR** and rebased onto `main` after each bootstrap merge. It merges only after M0-T10, when its own run shows `ci/summary` `success` and `trace-report CARD=…` `PASSED` for M0-T01, T03, T11 and T10 (AT-M0-T07-02). Then the owner applies P2. Branch: `chore/m0-t07-ci-workflows`.

> You are implementing task card **M0-T07 — GitHub Actions workflows** as an early draft (EXC-001 condition C4). The M0 build is authorized (`plans/STATUS.md`).
>
> 1. Work on branch `chore/m0-t07-ci-workflows`, created from the latest `main`. Rebase it onto `main` whenever a bootstrap card (M0-T03, M0-T11, M0-T10) merges.
> 2. Read: `AGENTS.md`; `.cursor/rules/*.mdc`; the full M0-T07 card; `specs/engineering/ci_checks.yaml` (normative: jobs, needs, targets, timeouts, path categories, required checks, fail-closed rules); `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` §7 (DEVENV-R018–R031, R047–R050) and §8.4; `docs/architecture/ARCHITECTURE.md` §10.8 (ARCH-R101–R105); ADR-0015.
> 3. Implement field 5 "In" and the field-12 tasks:
>    - `.github/workflows/ci.yml`, `milestone-gate.yml` and `eval-live.yml` (guarded; `agent-test-live` reports `NOT_APPLICABLE` until M3);
>    - `.github/actions/setup/action.yml`;
>    - `scripts/ci/changes.py` (path classification from `ci_checks.yaml`, with no third-party filter action);
>    - `scripts/ci/summary.py`, using M0-T11's report parsers in `scripts/ci/reports.py` once they exist; do not write that file yourself;
>    - the `ci` Make recipe (HC-7).
>
>    Pin every action by full commit SHA with the tag in a comment. Set top-level `permissions: contents: read`. Use `pull_request`, never `pull_request_target`. No secrets in `ci.yml`. Images are built, never pushed.
> 4. Touch only field-13 paths and the `ci` recipe. Do not change any other workflow-adjacent setting. Never configure repository protection; P2 is the owner's action after this card merges.
> 5. Write the field-14 tests for **AT-M0-T07-01 … AT-M0-T07-08**, each tagged with its AT ID. AT-M0-T07-07 is recorded manually at the gate.
> 6. Until M0-T10 and M0-T11 are on `main`, some jobs report `NOT_IMPLEMENTED` and `ci/summary` may fail on the draft. That is expected; record what you observe.
> 7. Commit with messages starting `M0-T07:`. **Do not push and do not open a PR.** The owner pushes, and the architect reviews and opens it as a draft.
> 8. If anything is ambiguous or conflicts with a specification: stop and report.

---

## 11. M0-T10 — kickoff prompt

**Prerequisites:** M0-T11 merged, and the CR-001 documentation PR (spec set 0.1.3) merged. Branch: `chore/m0-t10-governance-automation`. Merges under P1 + EXC-001.

> You are implementing task card **M0-T10 — Governance automation: templates, specs-check, trace report, renderers** for the Cenomi Dashboard Intelligence Agent POC. The M0 build is authorized (`plans/STATUS.md`). If STATUS does not show spec set 0.1.3, stop and report. Work in /Users/swa/dev/cenomi-dashboard-agent on branch `chore/m0-t10-governance-automation` from the latest main (M0-T01, T03 and T11 are merged).
>
> 1. Read, in order: AGENTS.md; .cursor/rules/*.mdc; plans/M0_FOUNDATION.md §3 (including the Make target-owner table) and the full M0-T10 card (all 20 fields, v1.3); `specs/engineering/make_targets.yaml` (`specs-check`, `trace-report`, `security-check` and `backend-test` entries); `specs/engineering/engineering.schema.json` (including `gateReport` and `manualResults`); `specs/traceability/id_conventions.yaml`; docs/architecture/ARCHITECTURE.md §10.8 and §12 (ARCH-R083, R094, R095, R101–R105); docs/architecture/DEVELOPMENT_ENVIRONMENT.md §5, §7, §8.2 (DEVENV-R035, PR template), §8.6 and §9 (triage classes); docs/design/DECISION_REGISTER.md §1–§2; ADR-0002 §3; ADR-0003 §4.
> 2. Implement field 5 "In" and the field-12 tasks:
>    - `.github/pull_request_template.md` with exactly the 15 sections of DEVENV-R035, and `.github/ISSUE_TEMPLATE/defect.yml` (`DEF-` title, exactly the 9 triage classes of DEVENV §9, a `blocking` checkbox).
>    - `scripts/specs/check.py`: every check listed under `specs-check` in `make_targets.yaml`, including schema validation of the engineering YAMLs, SHA256SUMS of the frozen paths, ADR headings and index, ID uniqueness and family match, 20-row task cards, relative links, `make help` vs YAML and workflow job names vs `ci_checks.yaml` (skip that comparison, reporting it as `NOT_APPLICABLE`, only while `.github/workflows/ci.yml` does not exist on main), the banned-term lint, `plans/gates/M<n>-manual-results.json` against `manualResults` when present, and the gate-mode checks. Each sub-check gets a positive and a negative fixture. Negative fixtures live under `tests/tooling/specs_check/fixtures/`; for AT-M0-T10-07 build a temporary tree in `tmp_path` that mirrors `tests/fixtures/` instead of committing anything outside field 13. A crashing check exits 1 with its name; it never silently passes.
>    - `scripts/trace/report.py`: reads the AT IDs from field 15 of the milestone plans, and the results from JUnit (use `scripts/ci/reports.py` from M0-T11) and `tests/reports/status.jsonl`. It writes `tests/reports/trace/trace.json` and `trace.md` in the ARCH §10.8 vocabulary. An unknown or malformed ID always exits 1. `CARD=` and `GATE=` follow `make_targets.yaml`. **HC-9:** ATs marked *manual* in field 15 are excluded from `CARD` checks and listed separately; in `GATE` mode a manual AT without a result in `plans/gates/M<n>-manual-results.json` fails.
>    - `scripts/docs/render_engineering_tables.py` reproduces the generated tables between the `BEGIN/END GENERATED` markers in DEVELOPMENT_ENVIRONMENT §5.2 and §7.2 from the YAMLs, byte for byte. `scripts/docs/render_register.py` checks DECISION_REGISTER §2 against the frozen export `docs/reference/final-design-gate/03_DECISION_REGISTER.md` and the status changes listed in DECISION_REGISTER §1 (**HC-10**, AT-M0-T10-03; never copy register content into code). Both come with drift checks. If either cannot be reproduced deterministically from repository content, stop and report; do not edit the specification text to fit.
>    - Make recipes, through `scripts/make/invoke.py` only for these targets: `specs-check` (`GATE`), `trace-report` (`CARD`, `GATE`), `security-check`, and the **`SUITE=tooling` branch of `backend-test`** (CR-001: `pytest tests/tooling` with JUnit to `tests/reports/backend/junit-tooling.xml`; leave the unit and integration branches unchanged).
>    - `security-check`: gitleaks (working tree locally; full history when `GITHUB_ACTIONS=true`), `uv run pip-audit` (fail on high or critical vulnerabilities with a fix available), `pnpm audit --audit-level high`, and a licence report. For Python use the standard library `importlib.metadata`; for Node use `pnpm licenses list --json`. GPL-family and AGPL licences fail unless an ADR accepts them (ADR-0003 §4 accepts psycopg's LGPL-3.0). Add no new dependency.
> 3. Touch only field-13 paths and those recipe branches. Do not change specification content. If a check finds a real defect in the current specs, stop and report it with file and line.
> 4. Write the field-14 tests for **AT-M0-T10-01 … AT-M0-T10-07**, each tagged `@pytest.mark.trace("AT-M0-T10-nn", reqs=[…])`.
> 5. Run and save the full output to `tests/reports/m0-t10-local-verification.log` (EXC-001 C2), starting from a committed, clean tree:
>    - `make install && git status --porcelain`; `make doctor`; `make backend-lint`; `make backend-typecheck`;
>    - `make backend-test SUITE=unit`; `make backend-test SUITE=integration`; `make backend-test SUITE=tooling`;
>    - `make specs-check`; `make check`; `make security-check`;
>    - `make trace-report CARD=M0-T01`; `make trace-report CARD=M0-T03`; `make trace-report CARD=M0-T11`; `make trace-report CARD=M0-T10`;
>    - finally `git status --porcelain` (must be empty).
> 6. Commit with messages starting `M0-T10:`. Do not push and do not open a PR.
> 7. If anything is ambiguous, conflicts with a specification, or needs a path outside field 13 and the listed recipe branches: stop and report. Never weaken a test, never merge, never change repository settings.

---

## 12. DEF-0001 — security-patch prompt (CR-002, EXC-002)

**Prerequisites:** the documentation PR recording CR-002 and EXC-002 merged (STATUS lists CR-002 as approved). Branch: `fix/def-0001-security-advisories` from the latest `main`. Merges under P1 + EXC-002, **before** M0-T10. Afterwards M0-T10 is rebased onto `main`, its verification log is re-run from a clean tree, and its branch is force-pushed with lease.

> You are fixing defect **DEF-0001** (GitHub issue #15) for the Cenomi Dashboard Intelligence Agent POC: two dependency advisories already on `main`, `certifi` in `backend/uv.lock` and transitive `handlebars` (through `eslint-plugin-boundaries`) in `pnpm-lock.yaml`. If `plans/STATUS.md` does not list CR-002 and EXC-002 as approved, stop and report. Work in /Users/swa/dev/cenomi-dashboard-agent on branch `fix/def-0001-security-advisories` from the latest main.
>
> 1. Read: AGENTS.md; .cursor/rules/*.mdc; docs/adr/0003-technology-stack-and-version-pinning.md §2; docs/architecture/DEVELOPMENT_ENVIRONMENT.md DEVENV-R004, DEVENV-R052, §8.4 (EXC-002) and the §8.6 rows for `backend/pyproject.toml` and `pnpm-workspace.yaml` (CR-002); plans/STATUS.md CR-002.
> 2. Before changing anything, run `uv run --project backend pip-audit` and `pnpm audit --audit-level high` and keep their full output. For each finding note the advisory ID, severity, affected range and fixed or patched version. (`make security-check` is not on main yet; it arrives with M0-T10.)
> 3. **certifi.** Take the lowest fixed version from the pip-audit output (expected 2026.10.19) and its PyPI upload time. Under `[tool.uv]` in `backend/pyproject.toml` add `exclude-newer-package = { certifi = "<the day after the upload date>T00:00:00Z" }`, with a comment line above it: `# CR-002 / DEF-0001 security patch (ADR-0003 §2, <advisory ID>); remove when exclude-newer passes this date`. Do not change `exclude-newer`, `required-version` or anything else in the file. Then run `uv lock --project backend --upgrade-package certifi`. The `backend/uv.lock` diff may change only the `certifi` entry (version, source, hashes) and the lock's recorded resolver options for this override.
> 4. **handlebars.** Take the lowest patched version from the `pnpm audit` output. Check with `pnpm why handlebars` that it satisfies the version range declared by the package that depends on it. If it does not, or if it is a new major version, stop and report. Add to `pnpm-workspace.yaml`, after `packages:`:
>    ```yaml
>    # CR-002 / DEF-0001 security patch (ADR-0003 §2, <advisory ID>)
>    overrides:
>      handlebars: "<exact patched version>"
>    ```
>    Then run `pnpm install` to regenerate `pnpm-lock.yaml`, and afterwards `pnpm install --frozen-lockfile`. The lockfile diff may change only the `overrides` record and the `handlebars` entries.
> 5. Touch only `backend/pyproject.toml` (the one entry), `backend/uv.lock`, `pnpm-workspace.yaml` (the one block) and `pnpm-lock.yaml`. Never edit a lockfile by hand. No other dependency may be added, removed or upgraded (DEVENV-R052 (e)). If the package managers change anything else, stop and report with the diff.
> 6. Run and save the full output to `tests/reports/def-0001-local-verification.log`, starting from a committed, clean tree:
>    - `make install && git status --porcelain`; `make doctor`;
>    - `uv lock --project backend --check`; `pnpm install --frozen-lockfile`;
>    - `uv run --project backend pip-audit`; `pnpm audit --audit-level high` (both must report no remaining finding at high or above with a fix available);
>    - `make backend-lint`; `make backend-typecheck`; `make backend-test SUITE=unit`; `make backend-test SUITE=integration`;
>    - `uv run --project backend pytest tests/tooling -q`; `make check`;
>    - `git diff --stat origin/main...HEAD` (exactly the four files);
>    - finally `git status --porcelain` (must be empty).
>    Also report the licence of each patched version (expected: certifi MPL-2.0, handlebars MIT).
> 7. Commit with the message `DEF-0001: patch certifi and handlebars advisories (CR-002)`. Do not push and do not open a PR. Never weaken a test, never merge, never change repository settings.

**After the patch merges, rebase M0-T10:**

```bash
git checkout chore/m0-t10-governance-automation
git fetch origin && git rebase origin/main
```

Re-run the full M0-T10 verification list (§11 step 5) from a clean tree, overwriting `tests/reports/m0-t10-local-verification.log`. `make security-check` must now pass. Then run `git push --force-with-lease`.

---

## 13. M0-T05 — kickoff prompt

**Prerequisites:** PR #32 merged (spec set 0.1.8: CR-003 report paths; CR-004 error registry and GENERATED schemas). Branch: `feat/m0-t05-contract-pipeline`. Merges under P2. It is the first open PR that changes `pnpm-lock.yaml`.

You are implementing **one task card: M0-T05**. The approved specification decides all behaviour. Do not make architectural or product decisions. If something below conflicts with the spec, or the spec is silent on something you need, **stop and report**; do not guess.

### 0. Preconditions (check these before writing anything)

1. Work in `/Users/swa/dev/cenomi-dashboard-agent`, **not** a `~/Desktop` copy. The owner has already created branch `feat/m0-t05-contract-pipeline` from the latest `main`. Check:
   ```
   git branch --show-current                           # must print feat/m0-t05-contract-pipeline
   grep '^version' specs/engineering/spec_set.yaml     # must print version: "0.1.8" or later
   ```
   If either check fails, stop. A version below 0.1.8 means PR #32 (CR-003, CR-004) is not on your base.
2. Read in full before coding:
   - `plans/M0_FOUNDATION.md`: card **M0-T05** (all 20 fields) and the §3 target-owner table.
   - `docs/adr/0004-contract-pipeline-and-bootstrap-rule.md`, **as amended by CR-004**: the bootstrap rule, the allowed subset, the generators and the wire conventions.
   - The six CF-0 files in `specs/contracts/`.
   - `specs/engineering/make_targets.yaml`: targets `codegen`, `contracts-check` and `integration-test`.
   - `docs/architecture/DEVELOPMENT_ENVIRONMENT.md`: DEVENV-R004 (pin policy), R013 (status reporting), R052 (manifests and lockfiles), R054 (shared files), R055 (lockfile serialization).
   - `plans/ROADMAP.md`: A-35 (CR-003) and A-36 (CR-004).

### 1. Files you may change (field 13 plus approved deviations)

- `backend/src/cenomi/contracts/**`
- `scripts/codegen/**`
- `packages/contracts-ts/**`. For `package.json`, only the dependency, `exports` and `scripts` entries, per DEVENV-R052.
- `tests/contract/**`, including `tests/contract/fixtures/**`.
- The five bootstrap schema files `specs/contracts/*.v1.schema.json`, and **only by running `make codegen`** (CR-004). Never hand-edit them after the conversion. **`specs/contracts/error_codes.v1.yaml` is not yours; do not touch it.**
- `Makefile` / `scripts/make/invoke.py`: only the `codegen`, `contracts-check` and `integration-test` recipes. Replace their NOT_IMPLEMENTED stubs (HC-7).
- CR-003:
  - the three report paths in `DEFAULT_JUNIT_REL` (`scripts/trace/report.py`);
  - `JOB_JUNIT` and `JUNIT_PRODUCER_TARGET` (`scripts/ci/job_junit.py`);
  - JUnit staging and upload steps for `ci/contracts` and `ci/integration` in `.github/workflows/ci.yml`.
- Lockfiles and manifests for the dependencies below (DEVENV-R052): `pnpm-lock.yaml`, `backend/pyproject.toml` dependency entries, `backend/uv.lock`.

Anything else, including `backend/src/cenomi/core/**`, `api/**`, `db/**`, `specs/engineering/**` and `ci_checks.yaml`, is **out of bounds**. Stop and report if you think you need it.

### 2. Tasks

#### Task 1: Models (`backend/src/cenomi/contracts/`)

- Write one module per contract: `error_envelope`, `principal`, `scope_decision`, `health_report`, `dataset_descriptor`.
- Use Pydantic v2 with `ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")`, and serialize by alias.
- Model the schemas as they are. **No schema has `null`**: an optional property is expressed only by being absent from `required` (ADR-0004 §4 g, absent ≠ null). Do not emit `type: [..., "null"]` or `anyOf`.
- The `scope` definition is owned by `scope_decision.v1`. `principal.v1` must reference it as `scope_decision.v1.schema.json#/$defs/scope`, exactly as the bootstrap file does.
- Each model carries the same `title`, `description` and `examples` as its bootstrap file, via `json_schema_extra` or `Field(...)`. The normalized comparison does not ignore `examples`.
- Do not rewire the existing API envelope code (`cenomi.api.envelope`, M0-T03). That is out of scope.

#### Task 2: Exporter and normalizer (`scripts/codegen/export_schemas.py`)

- Export with `model_json_schema(by_alias=True, mode="serialization")`, using a **custom `GenerateJsonSchema` subclass** (in `cenomi.contracts`) so the export is already inside the ADR-0004 subset. That means:
  - no `default`, `discriminator`, `anyOf` or `allOf`;
  - `$defs` names and `$ref` layout matching the bootstrap;
  - the cross-file `$ref` above;
  - `additionalProperties: false` on every object.
- **The normalizer may only:**
  - sort keys;
  - drop the `title` and `description` *keywords*;
  - drop the root `x-generated-from`.

  It keeps `$id`. It must **not** drop a *property* that happens to be named `title` or `description`, so normalize by schema position, not by key name. It must not rewrite anything else. Shape the export in the generator, not in the normalizer; a liberal normalizer makes AT-01 vacuous.
- On a mismatch, report the JSON path of the first difference (field 16).
- Writes go to a temp directory and are then swapped in. A generator failure leaves committed files untouched (field 16).

#### Task 3: Subset checker (`scripts/codegen/subset.py` or similar)

Implement ADR-0004 §2 exactly:
- the allowed keywords only;
- `additionalProperties: false` mandatory on every object;
- `format` limited to date, date-time and uuid;
- `oneOf` only with a `const` discriminator property;
- `$ref` only to `#/$defs/...` or to a relative file in `specs/contracts/`;
- `$schema` is draft 2020-12, and `$id` has the form `https://cenomi.local/contracts/<name>.v<major>.schema.json`;
- at least one `examples` entry;
- `x-generated-from` allowed at the root only (CR-004).

Examples are validated with `jsonschema.Draft202012Validator`, **with format checking on**. Use a referencing registry that resolves the relative file refs. Add `rfc3339-validator` (DEVENV-R052) so `date-time` is really checked.

Negative fixtures go in `tests/contract/fixtures/subset/`: at least `anyOf`, an open object and `format: email`. Add more if useful (`allOf`, `patternProperties`, a missing `examples`, an external URL `$ref`).

#### Task 4: TypeScript types

- Use `json-schema-to-typescript` as an exact devDependency of `packages/contracts-ts`, the newest release at least 14 days old (DEVENV-R004).
- Output goes to `packages/contracts-ts/src/types/<name>.v1.ts`.
- Use a fixed GENERATED banner with no timestamps or absolute paths. Cross-file refs resolve to imports, or are inlined deterministically. Pick one and keep it.

#### Task 5: Zod generator (`scripts/codegen/zod_from_schema.ts`)

- Use zod 4.x as an exact dependency of `packages/contracts-ts`.
- Cover **exactly the subset** and throw on anything else.
- Objects use `z.strictObject` (or `.strict()`) (field 17). Optional properties use `.optional()`.
- `enum`, `const`, `pattern` (`new RegExp(p, "u")`; JSON Schema patterns are unanchored search, as in Python's `re.search`), lengths, bounds, item counts, integer, and the three formats.
- `oneOf` with a const discriminator becomes `z.discriminatedUnion`. Local `$defs` become named consts. Cross-file refs become imports.
- Output goes to `packages/contracts-ts/src/zod/<name>.v1.ts` with the GENERATED banner, plus an `index.ts`. Add package `exports` for `types` and `zod`.
- Run it with Node 22's built-in type stripping (`node scripts/codegen/zod_from_schema.ts`). Use erasable TS syntax only, and do not add `tsx`/`ts-node`.

#### Task 6: Equivalence tests (AT-06, CA-05)

- Python (part of `make codegen`) writes a deterministic, GENERATED case corpus, for example `packages/contracts-ts/src/zod/__fixtures__/equivalence.cases.json`. For every schema it holds:
  - every example;
  - a generated set of invalid mutations, each recorded with jsonschema's verdict.

  Mutations, as applicable:
  - an unknown property at each object level;
  - each required property removed;
  - the wrong JSON type per property;
  - a value outside the `enum`, and a `const` violation;
  - a `pattern` miss;
  - a format violation;
  - `min`/`max` boundaries ±1, including length and items;
  - `null` where not allowed;
  - a wrong discriminator.

  Seed the generator so it is deterministic. Assert that each schema yields at least one accepted and many rejected cases.
- `packages/contracts-ts/src/zod/equivalence.test.ts` (Vitest) asserts that zod's verdict equals the recorded verdict for every case.
- A pytest test asserts the corpus is current: recompute the verdicts with jsonschema and compare.
- **A disagreement is fixed in the generator, never by dropping or excluding a case.**

#### Task 7: Registry scan (AT-05, `tests/contract/test_error_registry.py`)

- Statically scan (AST) `backend/src/cenomi/**` for `CenomiError` subclasses and their `code=` literals, and for direct `CenomiError(code=...)` calls.
- Read `specs/contracts/error_codes.v1.yaml` at runtime and assert both directions:
  - every raised code is listed with `status: active`;
  - every `active` code with `channel: http` is raised by some subclass.
- **Never copy registry contents into code.**
- Add a negative self-test: a fixture module raising an unknown code, and one leaving an active code unraised, make the scanner fail.
- After CR-004 this must pass on today's code. `QUERY_TIMEOUT` is active in M0. `PAYLOAD_TOO_LARGE` and `UNSUPPORTED_MEDIA_TYPE` are `reserved` until M0-T06.

#### Task 8: Make recipes (via `scripts/make/invoke.py`)

Behaviour is exactly as in `make_targets.yaml`, with DEVENV-R013 status lines.

- **`codegen`:** export the schemas, writing each `specs/contracts/<name>.v1.schema.json` with the root `x-generated-from` (the model's dotted path, for example `cenomi.contracts.principal.Principal`). Then generate the TS types, the zod schemas and the equivalence corpus. Serialize JSON as `json.dumps(..., sort_keys=True, indent=2, ensure_ascii=False) + "\n"`. Exit 1 on generator failure. It never edits non-generated files.
- **`contracts-check`:**
  - run codegen into a temp directory and diff it against the committed files, listing each stale file;
  - run the subset and example checks;
  - compare each model with its bootstrap copy;
  - run `uv run pytest tests/contract -m 'not db'` → `tests/reports/contracts/junit-contracts.xml`;
  - run Vitest for `packages/contracts-ts` → `tests/reports/contracts/junit-contracts-vitest.xml`.

  It needs no database.
- **`integration-test`:** prerequisite `db-upgrade DB=test`. Run `uv run pytest tests/contract tests/security -m 'not agent_live'` against `cenomi_test`, with the app in-process, → `tests/reports/integration/junit-integration-test.xml`. Skip a directory that does not exist yet (`tests/security` arrives with M0-T06).
- `tests/contract` sits at the repository root. Run pytest with the backend config the way the tooling suite does (`-c pyproject.toml --rootdir=.. --confcutdir=..`), so markers and `--strict-markers` apply.

#### Task 9: CR-003 report wiring

- Add the three paths to `DEFAULT_JUNIT_REL`.
- `JOB_JUNIT`:
  - `"ci/contracts"`: `junit-contracts.xml`, `junit-contracts-vitest.xml`;
  - `"ci/integration"`: `junit-integration-test.xml`.
- `JUNIT_PRODUCER_TARGET`:
  - `junit-contracts.xml` and `junit-contracts-vitest.xml` → `contracts-check`;
  - `junit-integration-test.xml` → `integration-test`.
- In `ci.yml`, add the stage-and-upload steps to `ci/contracts` and `ci/integration`, copying the `ci/backend` pattern: artefacts `junit-ci-contracts` and `junit-ci-integration`, `if: always()`, `if-no-files-found: ignore`. The summary's basename staging must keep working; all basenames stay unique.
- Existing tests such as `assert_job_junit_covers_default` must still pass.

#### Task 10: GENERATED conversion (CR-004). Order matters.

1. **First**, copy the five hand-written schema files **verbatim** (byte-identical) to `tests/contract/fixtures/bootstrap/`. Commit that on its own, so the review can confirm the bytes match `main`.
2. Then run `make codegen`, which rewrites the five `specs/contracts/*.v1.schema.json`.
3. From then on, the subset check, example validation and TS/zod generation all read the generated files.
4. AT-01 compares exports with the **bootstrap copies**.

### 3. Tests and ATs

Every pytest test carries `@pytest.mark.trace("AT-M0-T05-0N", reqs=[...])`. Every Vitest test name contains `[AT-M0-T05-06]`, following the `tests/e2e/support/axe.spec.ts` convention. File names come from field 14.

- **AT-01** `test_bootstrap_equivalence.py`: each export equals its bootstrap copy under normalization. Include a negative self-test: a mutated model is reported, with the JSON path.
- **AT-02** `test_codegen_idempotent.py`: run codegen twice into two temp directories; both outputs are identical and equal the committed files.
- **AT-03**: edit a copy of a GENERATED file (TS, zod and schema) **in a temp copy**; the drift check fails and names the file.
  - **Do not run `make contracts-check` or `make codegen` from inside a test.** `contracts-check` runs pytest, so calling it from a test would recurse. Call the same Python entry points the recipes use.
  - Never modify the real working tree in a test.
- **AT-04** `test_subset.py`: the negative fixtures are rejected, each with the right reason; all five real schemas pass.
- **AT-05** `test_error_registry.py`: as in Task 7.
- **AT-06**: `equivalence.test.ts`, plus the corpus-current pytest test.

No skips. A missing prerequisite fails with a clear message.

### 4. Verification (run all of these, in order, and paste the full output)

```
make install
make codegen && git status --porcelain            # after the conversion commit: empty
make codegen && git status --porcelain            # second run: still empty (AT-02)
make contracts-check
make up && make integration-test
make check
make ci JOB=contracts
make ci JOB=integration
make trace-report CARD=M0-T05                     # AT-M0-T05-01..06 all PASSED
git diff --stat main...HEAD
for f in error_envelope principal scope_decision health_report dataset_descriptor; do
  git show main:specs/contracts/$f.v1.schema.json | cmp - tests/contract/fixtures/bootstrap/$f.v1.schema.json && echo "$f bootstrap-identical"
done
```

Do not commit anything under `tests/reports/`, and commit no secrets.

### 5. Commit and report

- Commits:
  1. the bootstrap copies;
  2. the implementation;
  3. the GENERATED conversion (codegen output only).

  Each carries `Co-authored-by: Cursor <cursoragent@cursor.com>`.
- **Do not push and do not open a PR.** The owner pushes, and the architect reviews and opens the PR.
- Report:
  - each AT and its result;
  - the dependency versions you chose, with release dates (14-day rule);
  - every file outside §1 you touched (there should be none);
  - any spec question you hit and stopped on.


---

## 14. M0-T08 — kickoff prompt

**Prerequisites:** M0-T05 merged (lockfile serialization, DEVENV-R055 (a)) and CR-005 merged (spec set 0.1.9). Branch: `feat/m0-t08-echarts-gate`. Merges under P2. AT-M0-T08-05 is the architect's manual STATUS record of the result.

You are implementing **one task card: M0-T08**. The approved specification decides all behaviour. If something below conflicts with the spec, or the spec is silent on something you need, **stop and report**; do not guess.

### 0. Preconditions

- Work in `/Users/swa/dev/cenomi-dashboard-agent`.
- The owner creates branch `feat/m0-t08-echarts-gate` from the latest `main` **after M0-T05 has merged**. Only one open PR may change `pnpm-lock.yaml` at a time (DEVENV-R055 (a)).
- Check:
  ```
  git branch --show-current                         # feat/m0-t08-echarts-gate
  grep '^version' specs/engineering/spec_set.yaml   # version: "0.1.9" or later (CR-005)
  git log --oneline -20 | grep 'M0-T05:'            # M0-T05 is on main
  ```
  If any check fails, stop.
- Read in full:
  - `plans/M0_FOUNDATION.md`: card **M0-T08** (all 20 fields, including the CR-005 task 7 and field 13).
  - `specs/engineering/make_targets.yaml`: targets `echarts-gate` and `e2e`.
  - `specs/engineering/ci_checks.yaml`: job `ci/echarts-gate`.
  - `docs/architecture/DEVELOPMENT_ENVIRONMENT.md`: DEVENV-R004, R052, R054 (the `ci.yml` row) and R055.
  - `docs/design/DESIGN_BASELINE.md`: DBASE-R003 and R004.
  - `docs/design/baseline/boards/DX3-Gallery.dc.html`, read only, to find the self-test button, the result rows, the summary counts, the treemap metrics and the "Test double, not ECharts" / "ECharts did not load" texts.
  - `playwright.config.ts` (M0-T11's; **do not edit it**).
  - ROADMAP A-37.

### 1. Files you may change

- `packages/viz/package.json`: the dependency `"echarts": "5.6.0"` exactly. Then regenerate `pnpm-lock.yaml` with pnpm (never by hand).
- `tests/e2e/echarts-gate/**`: the spec and any helper, such as the static server and the result parser.
- The `echarts-gate` recipe, via `scripts/make/invoke.py`. Replace only its stub.
- CR-005:
  - `tests/reports/echarts/junit-echarts-gate.xml` added to `DEFAULT_JUNIT_REL` (`scripts/trace/report.py`);
  - `JOB_JUNIT["ci/echarts-gate"]` and `JUNIT_PRODUCER_TARGET["junit-echarts-gate.xml"] = "echarts-gate"` (`scripts/ci/job_junit.py`);
  - in `.github/workflows/ci.yml`, job `ci/echarts-gate` only: a step `make install BROWSERS=1` before `make ci JOB=echarts-gate`, copied from `ci/e2e`, and the "Stage job JUnit artefacts" plus `junit-ci-echarts-gate` upload steps, copied from `ci/e2e`.

**Never write to `docs/design/baseline/**`.** Nothing else is in scope, including `playwright.config.ts`, `apps/web` and `packages/viz` source.

### 2. Behaviour

1. **Static server.** A minimal Node `http` server, started by the spec, bound to `127.0.0.1` on an ephemeral port, serving `docs/design/baseline/boards/` **read-only**:
   - GET and HEAD only;
   - no directory listing;
   - path traversal rejected.
2. **Network isolation** (AT-01, field 17):
   - Route every request that is not to the local server. The cdnjs URL `…/echarts/5.6.0/echarts.min.js` is fulfilled from `node_modules/echarts/dist/echarts.min.js`, resolved from `packages/viz` so the locked copy is used.
   - Every other external request is **aborted** and recorded.
   - The test asserts:
     - no request reached a non-local host;
     - the served file contains the version string `5.6.0`;
     - the page evaluates `echarts.version === "5.6.0"`.
3. **Self-test** (AT-02):
   - Click "Run self-test" and wait for completion, with a bounded timeout and no fixed sleeps.
   - Parse every result row (area, name, detail, status), the pass/fail/n.a. counts and the treemap metrics (area CV, order, aspect versus reference).
   - Write `tests/reports/echarts/result.json` and a human-readable `result.txt`.
   - Assert that the row count equals the board's own count and that the counts add up.
4. **Harness failure detection** (AT-03): fail if the page shows "Test double, not ECharts" or "ECharts did not load". Prove it with a negative test: route the ECharts URL to a stub script, or block it, and assert the harness reports the failure.
5. **Board integrity** (AT-04): record the SHA-256 of every file under `docs/design/baseline/boards/` before and after the run and assert they are unchanged. They must also match `docs/handoff/SHA256SUMS`.
6. **Informational in M0** (field 16, `make_targets.yaml`):
   - A chart that fails its threshold does **not** fail the spec or the recipe. It is recorded in `result.json`.
   - Only a harness failure (board not loading, ECharts not loaded, self-test not completing) fails.
   - The M2 blocking rule is not implemented now; leave a clearly named constant or comment pointing at GDQ-06.
7. **Tag and project** (CR-005):
   - The spec title, or its `tag` option, carries `@echarts-gate`, and each test name contains its AT ID, for example `[AT-M0-T08-01]`.
   - The recipe runs `pnpm exec playwright test tests/e2e/echarts-gate --project=desktop` with JUnit at `tests/reports/echarts/junit-echarts-gate.xml`. Override the reporter from the command line or with the `PLAYWRIGHT_JUNIT_OUTPUT_FILE` environment variable, and confirm it really lands there.
   - It must not overwrite `tests/reports/e2e/junit-playwright.xml`.
   - (`make e2e`, built later by M0-T04, excludes `@echarts-gate`.)
8. **Recipe:**
   - `make echarts-gate` exits 0 in M0 when the harness ran, whatever the chart results.
   - It exits 1 on a harness failure.
   - It prints the DEVENV-R013 status line.

### 3. Verification (paste all output)

```
make install BROWSERS=1 && git status --porcelain       # clean after the lockfile commit
make echarts-gate
cat tests/reports/echarts/result.txt
ls -l tests/reports/echarts/
make check
make ci JOB=echarts-gate
make trace-report CARD=M0-T08                           # AT-M0-T08-01..04 PASSED; AT-05 listed as manual
sha256sum -c <(grep 'docs/design/baseline/boards/' docs/handoff/SHA256SUMS)
git diff --stat main...HEAD
```

Also paste:
- the summary from `result.txt`: the counts, plus any failing chart with its metric and threshold. AT-M0-T08-05 is the architect's manual STATUS record, and any failing chart gets its DXD-23 fallback listed for PR-M2;
- the ECharts version and its integrity hash from `pnpm-lock.yaml`.

### 4. Commit and report

- Commit with messages starting `M0-T08:` and `Co-authored-by: Cursor <cursoragent@cursor.com>`.
- **Do not push and do not open a PR.**
- Report:
  - each AT and its result;
  - every file outside §1 you touched (there should be none);
  - every external request the board attempted, with its host and whether it was aborted.


---

## 15. M0-T06 — kickoff prompt

**Prerequisites:** M0-T05 merged. Branch: `feat/m0-t06-dev-sign-in`. May be built in parallel with M0-T08 (it does not change `pnpm-lock.yaml`). Merges under P2. It reactivates `PAYLOAD_TOO_LARGE` and `UNSUPPORTED_MEDIA_TYPE` (CR-004).

You are implementing **one task card: M0-T06**. The approved specification decides all behaviour. If something below conflicts with the spec, or the spec is silent on something you need, **stop and report**; do not guess.

### 0. Preconditions

- Work in `/Users/swa/dev/cenomi-dashboard-agent`.
- The owner creates branch `feat/m0-t06-dev-sign-in` from the latest `main` after **M0-T05 has merged**. M0-T06 needs the `cenomi.contracts` models. It may run in parallel with M0-T08, because it does not touch `pnpm-lock.yaml`.
- Check:
  ```
  git branch --show-current                         # feat/m0-t06-dev-sign-in
  grep '^version' specs/engineering/spec_set.yaml   # version: "0.1.8" or later
  ls backend/src/cenomi/contracts/                  # principal and scope_decision models exist
  ```
  If any check fails, stop.
- Read in full:
  - `plans/M0_FOUNDATION.md`: card **M0-T06** (all 20 fields, including the CR-004 additions in fields 5, 7, 12, 13 and 15).
  - `docs/architecture/ARCHITECTURE.md`:
    - §5.4, the route table;
    - §5.5, errors;
    - ARCH-R014, R015, R016, R026 (case e), R045, R046;
    - §9: ARCH-R077 to R082, including the fixture-principal table and the fingerprint rule.
  - `docs/adr/0016-poc-sign-in-and-session.md`.
  - `specs/contracts/principal.v1.schema.json`, `scope_decision.v1.schema.json`, `error_envelope.v1.schema.json` and `error_codes.v1.yaml`.
  - `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` §4 (`AUTH_MODE`, `SESSION_SECRET`, `SESSION_TTL_MINUTES`, `API_MAX_BODY_BYTES`) and DEVENV-R052 and R054.
  - ROADMAP A-36 (CR-004).

### 1. Files you may change (field 13 plus the CR-004 deviations)

- `backend/src/cenomi/auth/**`
- `backend/src/cenomi/api/routers/session.py`, and the `session` router registration in `cenomi.api.app.create_app()`
- `tests/fixtures/principals.yaml`
- `backend/tests/unit/auth/**`, `backend/tests/integration/api/test_session.py` and `tests/security/test_scope_deny_by_default.py`
- CR-004:
  - `backend/src/cenomi/api/middleware/body_guard.py`, and its registration in `create_app()`;
  - the `PayloadTooLarge` and `UnsupportedMediaType` subclasses in `backend/src/cenomi/core/errors.py`, appended to the existing hierarchy without changing existing classes;
  - the `API_MAX_BODY_BYTES` field in `backend/src/cenomi/core/settings.py`;
  - the single line `API_MAX_BODY_BYTES=1048576` in `.env.example`;
  - `backend/tests/integration/api/test_body_guard.py`;
  - in `specs/contracts/error_codes.v1.yaml`, only for `PAYLOAD_TOO_LARGE` and `UNSUPPORTED_MEDIA_TYPE`: `status: reserved` → `status: active`, and delete the sentence "Reserved until M0-T06 enforces it and sets status active (CR-004)." from each `meaning`.

Nothing else. If `tests/contract` (M0-T05) or the generated schemas need a change, stop and report.

### 2. Behaviour

1. **Fixtures** (task 1, ARCH-R078):
   - `tests/fixtures/principals.yaml` holds at least the five principals of the ARCH-R078 table, with exactly those roles, grants and keys.
   - Each also has the `displayName` and `persona` that `principal.v1` and the dev principals list require: `admin` for the admin roles, `tenant` for the tenant roles; use the enum values in `principal.v1`.
   - `permissions` is `[]` in M0, as the `principal.v1` description says.
   - `sessionExpiresAt` is not in the fixture. `/me` and sign-in fill it from the session's `expiresAt`.
   - The loader validates every entry against the `cenomi.contracts` principal fields, excluding `sessionExpiresAt`. Every `/me` and sign-in response validates against the full `principal.v1`.
   - An invalid file refuses startup with the validation error (field 16).
2. **Session cookie** (task 2, ARCH-R045, ADR-0016):
   - The cookie is `cenomi_session`: HMAC-SHA-256 with stdlib `hmac`, compared with `hmac.compare_digest`.
   - The payload holds **exactly** `principalId`, `issuedAt` and `expiresAt`, with TTL from `SESSION_TTL_MINUTES`.
   - Attributes: `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure` **when the request is HTTPS** (ARCH-R045).
   - Never log the cookie value.
   - Tampered, expired, malformed and unknown-principal cookies all give 401 `UNAUTHENTICATED`.
3. **Routes** (task 3, §5.4):
   - `GET /api/v1/me` returns `principal.v1`; 401 without a valid session.
   - `GET /api/v1/auth/dev/principals` returns a list of `{principalId, displayName, persona, role}`.
   - `POST /api/v1/auth/dev/sign-in` with `{principalId}` returns `principal.v1` and sets the cookie. An unknown `principalId` gives 404 `NOT_AVAILABLE` (uniform, field 16).
   - `POST /api/v1/auth/sign-out` returns 204 and clears the cookie.
   - The two dev routes are **mounted only** when `AUTH_MODE=dev_fixture`; otherwise they return the API's 404 envelope.
   - Grants are always resolved from the fixture on the backend, on every request (ED-07 A).
   - A role, grant or scope supplied in a header, query parameter or body never changes `/me` or `authorize`. Unknown query parameters and body fields are rejected with 400 `VALIDATION_ERROR` (ARCH-R014); headers are ignored.
4. **AccessScope** (tasks 4 and 5, ARCH-R079 to R081):
   - `authorize(principal, requested | None)` returns the scope-decision model.
   - Supports `ALL` and same-kind intersections only; a cross-kind request returns `empty` with reason `hierarchy_unresolved`.
   - It never widens. `ALL` comes only from an explicit `ALL` grant.
   - The fingerprint is `sfp_` + the first 32 hex characters of SHA-256 over canonical JSON (keys sorted, arrays sorted, no whitespace).
   - Debug logs carry `outcome` and `scopeFingerprint`; authenticated request logs carry `principalId` (field 18).
5. **Request-body guard** (CR-004; field 7 has the exact rules):
   - Applies to `/api/v1` POST, PUT and PATCH requests that carry a body.
   - A missing or non-`application/json` media type gives 415. Parameters such as `charset=utf-8` are allowed.
   - A `Content-Length` above `API_MAX_BODY_BYTES` gives 413 before the body is read.
   - A streamed body that grows past the limit gives 413.
   - `API_MAX_BODY_BYTES` defaults to 1048576, minimum 1024, validated at startup.
   - Both errors go through the existing `CenomiError` handler as `error_envelope.v1`.
   - Sign-out with no body is not refused.

### 3. Tests (field 15; each pytest test tagged `@pytest.mark.trace("AT-M0-T06-0N", reqs=[...])`)

- **AT-01 to AT-07**, exactly as written in field 15.
  - AT-05 is table-driven with the six named cases, and every decision validates against `scope_decision.v1`.
  - AT-06 is a Hypothesis property test: never broader than the grants; `ALL` only if granted; the fingerprint stable under key and array reordering.
- **AT-08 and AT-09** (CR-004), exactly as written. For AT-09:
  - set `API_MAX_BODY_BYTES=1024` through test settings;
  - send one request with `Content-Length: 1025`, and one chunked body over 1024 bytes without `Content-Length`;
  - validate both responses against `error_envelope.v1`.
- After the registry edit, run M0-T05's `tests/contract/test_error_registry.py` (AT-M0-T05-05). It must pass with both codes active and raisable.
- Expected values come from the specs and fixtures, never from the code under test. No skips.

### 4. Verification (paste all output)

```
make install && git status --porcelain
make backend-lint && make backend-typecheck
make backend-test SUITE=unit
make backend-test SUITE=integration
make up && make integration-test           # includes tests/security and tests/contract
make contracts-check                       # registry test still green
make check
make ci JOB=backend
make ci JOB=integration
make trace-report CARD=M0-T06              # AT-M0-T06-01..09 PASSED
make trace-report CARD=M0-T05              # still all PASSED
curl -si -X POST localhost:8000/api/v1/auth/dev/sign-in -H 'Content-Type: application/json' -d '{"principalId":"p_central_manager"}' | sed -n '1,15p'
git diff --stat main...HEAD
```

In the curl output, redact the cookie value before pasting. Show only its attributes.

### 5. Commit and report

- Commit with messages starting `M0-T06:` and `Co-authored-by: Cursor <cursoragent@cursor.com>`.
- **Do not push and do not open a PR.**
- Report:
  - each AT and its result;
  - every file outside §1 you touched (there should be none);
  - any spec question you stopped on.


---

## 16. M0-T04 — kickoff prompt

**Prerequisites:** M0-T02, M0-T05, M0-T06 and M0-T08 merged; CR-005 merged. Branch: `feat/m0-t04-web-shell`. Merges under P2. It implements the last M0 Make targets, so it also fixes DEF-0006 (CR-005).

You are implementing **one task card: M0-T04**, the last M0 build card. The approved specification decides all behaviour. If something below conflicts with the spec, or the spec is silent on something you need, **stop and report**; do not guess.

### 0. Preconditions

- Work in `/Users/swa/dev/cenomi-dashboard-agent`.
- The owner creates branch `feat/m0-t04-web-shell` from the latest `main` once **M0-T02, M0-T05, M0-T06 and M0-T08 have all merged**. M0-T08 must merge first because both cards change `pnpm-lock.yaml` (DEVENV-R055 (a)).
- Check:
  ```
  git branch --show-current                         # feat/m0-t04-web-shell
  grep '^version' specs/engineering/spec_set.yaml   # version: "0.1.9" or later (CR-005)
  git log --oneline -40 | grep -E 'M0-T0(5|6|8):'   # all three present
  ls packages/contracts-ts/src/zod/                 # generated zod from M0-T05
  ```
  If any check fails, stop.
- Read in full:
  - `plans/M0_FOUNDATION.md`: card **M0-T04** (all 20 fields, including CR-005 tasks 13 and 14 and fields 13 and 20).
  - `docs/architecture/ARCHITECTURE.md` §6: the route map table §6.2, ARCH-R035 to R046 and R053 to R055, and the state rules in §6.5.
  - `docs/product/PRODUCT_SPEC.md`: PSPEC-R002, R004 and R007.
  - `docs/adr/0016-poc-sign-in-and-session.md` and `docs/adr/0018-styling-approach.md`.
  - `specs/engineering/make_targets.yaml`: the `frontend-*`, `e2e` and `up` targets.
  - `docs/architecture/DEVELOPMENT_ENVIRONMENT.md` §4, §6 (DEVENV-R016, R017) and §8.6 (R052 to R055).
  - `playwright.config.ts` and `apps/web/vitest.config.ts` (M0-T11's; **do not edit**).
  - ROADMAP A-37 (CR-005) and GitHub issue #29 (DEF-0006).
  - The DX1/DX2 design boards named in field 2, for the shell layout and the error states only. Build nothing beyond the shell.

### 1. Files you may change

- `apps/web/**`, except `apps/web/package.json` and `apps/web/vitest.config.ts`. For `package.json`, change only dependencies and scripts, per DEVENV-R052.
- `tests/e2e/shell/**`, `tests/tooling/test_web_boundaries.py` and `tests/tooling/test_compose_web.py`.
- Composition points:
  - the `web` service block in `docker-compose.yml`;
  - the `frontend-format`, `frontend-lint`, `frontend-typecheck`, `frontend-test`, `frontend-build` and `e2e` recipes (via `scripts/make/invoke.py`);
  - the `lint`, `typecheck`, `test` and `build` scripts of the package manifests (DEVENV-R052).

The ESLint flat config, with its boundaries rules, goes in `apps/web/eslint.config.mjs`. No root config exists, and creating one is out of scope.
- `pnpm-lock.yaml`, regenerated by pnpm only.
- **DEF-0006** (CR-005): the AT-M0-T01-04 test in `tests/tooling/test_make_contract.py`, plus a test-only hook in `scripts/make/invoke.py` only if the synthetic target needs one.

Dependencies follow ADR-0003 and DEVENV-R004: exact pins, newest release at least 14 days old within each line.
- Next.js 16.x, React 19.x and TanStack Query v5.
- zod 4.x, the same version as `packages/contracts-ts`.
- `@cenomi/contracts-ts` as a workspace dependency.

No Tailwind (ED-09). Use one minimal shell style sheet; tokens arrive in M2.

### 2. Behaviour (fields 5, 8, 12, 16, 17)

- **Routes.** Every route of ARCHITECTURE §6.2, built with the `(app)` and `(auth)` groups.
  - `/` redirects by persona: `admin` → `/admin`, `tenant` → `/tenant`.
  - Every other app route renders the shell and a placeholder: "Delivered in M<n>", with the milestone taken from the §6.2 table.
- **Shell.** Rail with Dashboard, Workspace and Insights; it becomes a bottom tab bar below 820 px (breakpoints 1280 and 820). The top bar shows the persona and a disabled bell. The synthetic-data banner reads exactly `SYNTHETIC DATA · AS OF 20 OCT 2026`, formatted from `GET /api/v1/dataset`.
  - If the dataset call fails, the banner shows `SYNTHETIC DATA` with "as of" unavailable. **Never show a fabricated date.**
  - The demo persona switch (ARCH-R040) appears only when `/api/v1/auth/dev/principals` is available.
- **Data client** (`lib/api/client.ts`):
  - same-origin only;
  - every response is parsed with the **generated** zod schemas from `@cenomi/contracts-ts`; no hand-written contract types;
  - a non-2xx response is parsed as `error_envelope.v1`;
  - a parse failure becomes an `INTERNAL` error carrying the `requestRef`, and nothing from that response is rendered (AT-06);
  - failed calls are logged to the console with the `requestRef`.

  `lib/api/queryKeys.ts` keys start with `[principalId, datasetId, …]` (ARCH-R042).
- **Session.** `(app)/layout.tsx` only redirects a 401 to `/sign-in` (ARCH-R046). The web makes no authorization decision and never reads the cookie (ARCH-R045). Sign-out and persona switch clear the whole query cache and the session-stored shell state (AT-07).
- **No data fetching in Server Components.** No `NEXT_PUBLIC_*` secrets, no HTML from responses, and no `dangerouslySetInnerHTML`.
- **`next.config`.**
  - Rewrites `/api/*` and `/agui/*` to `API_INTERNAL_URL`.
  - Headers on every response: `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin` and `Content-Security-Policy: frame-ancestors 'none'`.
- **ESLint boundaries.** `features/` may not import `app/`; `echarts` may only be imported in `packages/viz`; `react/no-danger` is on. Negative fixtures prove each rule (AT-05).
- **Error states.** If the API is down, the banner area and pages show the error state with Retry and the `requestRef` (DX2 States 5).
- **`apps/web/Dockerfile` and the Compose `web` service** (DEVENV-R016, R017):
  - non-root;
  - port bound to `127.0.0.1:3000`;
  - health check `GET /`;
  - `API_INTERNAL_URL=http://api:8000`;
  - depends on api being healthy.

  Then `make up` serves the shell at http://localhost:3000. The CI `ci/images` job starts building the web image automatically once the Dockerfile exists (HC-11).
- **Make recipes:**
  - **`frontend-test`:** `pnpm -r test`, with JUnit at `tests/reports/frontend/junit-vitest.xml` (CR-005).
  - **`frontend-build`:** `pnpm -r build`.
  - **`e2e`**, per `make_targets.yaml` as amended by CR-005:
    1. run `make setup` when `.env` is absent;
    2. start the stack with `CENOMI_ENV=test` against `cenomi_test`;
    3. wait for health;
    4. run `pnpm exec playwright test --grep-invert @echarts-gate`, with JUnit at `tests/reports/e2e/junit-playwright.xml`;
    5. collect the api logs to `tests/reports/e2e/api-logs.jsonl`;
    6. stop the stack unless `KEEP_UP=1`.

    Honour the `GREP` and `PROJECT` arguments. Once `e2e` is implemented, CI's HC-12 harness-only step stops by itself, and the full run includes `tests/e2e/support`.
- **DEF-0006.** When no M0 stub target remains, AT-M0-T01-04's test must still exercise the stub path: a synthetic target, run through the same code path `scripts/make/invoke.py` uses for stubs, prints `NOT_IMPLEMENTED: <target> — …` and writes its `status.jsonl` record. Do not reference `e2e` or any real target.

### 3. Tests (field 14; AT IDs in names or markers)

- Each test from field 14, mapped to **AT-M0-T04-01 … -12** exactly as written in field 15.
- Playwright runs on the three projects (desktop 1440×900, tablet 1024×768, phone 390×844).
- AT-09 uses M0-T11's axe helper.
- AT-10 asserts `document.cookie` never contains `cenomi_session`.
- AT-11 signs in as each ARCH-R078 fixture principal and checks the persona landing; signing out returns to `/sign-in`.
- AT-12 (`test_compose_web.py`) follows the pattern of M0-T02's `tests/tooling/test_compose.py`, including `make setup` when `.env` is absent. It asserts:
  - web healthy (`GET /` returns 200 or 307);
  - the port is bound to 127.0.0.1 only;
  - the container user is non-root.
- AT-05 and AT-12 are tooling-suite tests and run in `ci/specs` (CR-005).
- Expected values come from the specs, never from the code under test. No skips.

### 4. Verification (paste all output)

```
make install BROWSERS=1 && git status --porcelain
make frontend-lint && make frontend-typecheck
make frontend-test && make frontend-build
make down; docker volume ls | grep cenomi        # then remove the cenomi volumes for a clean-volume run
make up                                          # db, api and web healthy; prints http://localhost:3000
make e2e
make backend-test SUITE=tooling                  # includes test_web_boundaries, test_compose_web and the DEF-0006 test
make check
make ci JOB=frontend
make ci JOB=e2e
make ci JOB=images
make trace-report CARD=M0-T04                    # AT-M0-T04-01..12 PASSED
make trace-report CARD=M0-T01                    # still PASSED (DEF-0006)
git diff --stat main...HEAD
```

- Save screenshots of the signed-in shell at 1440, 1024 and 390 px wide to attach to the PR (field 20). Do not commit them under `tests/reports/`.
- Do not commit anything under `tests/reports/`, and commit no secrets.

### 5. Commit and report

- Commit with messages starting `M0-T04:` and `Co-authored-by: Cursor <cursoragent@cursor.com>`.
- **Do not push and do not open a PR.**
- Report:
  - each AT and its result;
  - the dependency versions you chose, with release dates;
  - every file outside §1 you touched (there should be none);
  - any spec question you stopped on.


---

## 17. M0-T09 — spike prompt

**Prerequisites:** CR-005 merged (it gives the report PR ownership of `tests/tooling/test_no_agui_dependency.py`). Branches: `spike/m0-t09-agui-spike` (never merged) and `docs/m0-t09-agui-spike-report` (docs PR). May run at any time. AT-M0-T09-01 to -03 are manual reviews by the architect and the owner.

You are running **one task card: M0-T09**. It is a spike: throwaway code whose only lasting output is a report. The approved specification decides what to verify. If the spec is silent on something you need, **stop and report**; do not guess.

It can run at any time, in parallel with every other card.

### 0. Two branches, two purposes

| Branch | Created by the owner from | Contains | Merged? |
|---|---|---|---|
| `spike/m0-t09-agui-spike` | latest `main` | throwaway server, client, Next.js rewrite app and recorded streams | **Never** (ARCH-R075) |
| `docs/m0-t09-agui-spike-report` | latest `main`, after the spike is finished | only `docs/architecture/spikes/AGUI_SPIKE_REPORT.md` and `tests/tooling/test_no_agui_dependency.py` (CR-005) | Yes, by docs PR |

Check:
```
git branch --show-current                         # spike/m0-t09-agui-spike
grep '^version' specs/engineering/spec_set.yaml   # version: "0.1.9" or later (CR-005)
```
If either check fails, stop.

Read in full:
- `plans/M0_FOUNDATION.md`: card **M0-T09** (all 20 fields).
- `docs/architecture/ARCHITECTURE.md`: §8.4, which holds ARCH-R075 and R076, the A1–A14 and L1 table, and R108. Also read §8.6 for the provisional event mapping the spike checks.
- The board `docs/design/baseline/boards/DX4-AGUI.dc.html` (read only): the event → state table, run identity and idempotency.
- `docs/adr/0003-technology-stack-and-version-pinning.md`, the AG-UI row and CA-02 to CA-04.
- `docs/design/DECISION_REGISTER.md`, ED-10.
- ROADMAP A-13.

### 1. Spike branch (any path, but keep it isolated)

- Put everything under `spikes/agui/`, with its **own** Python environment and its **own** `package.json` and lockfile, outside the pnpm workspace and the uv workspace. Even on the spike branch, the root `backend/uv.lock`, `pnpm-lock.yaml`, `pnpm-workspace.yaml` and `backend/pyproject.toml` must stay byte-identical to `main`. Check this with `git diff main -- backend/uv.lock pnpm-lock.yaml pnpm-workspace.yaml backend/pyproject.toml`, which must be empty. Use `pnpm install --ignore-workspace` inside `spikes/agui/`, so pnpm never touches the root workspace, and give the Python side its own `pyproject.toml` and virtual environment.
- SDKs:
  - Python: `ag-ui-protocol` 1.0.x.
  - TS: `@ag-ui/core`, `@ag-ui/client` and `@ag-ui/encoder` at **1.0.0 and 1.0.1** (ADR-0003). Run the client scenarios on both and record any difference.
  - zod: the project's zod 4 line, the same version as `packages/contracts-ts`, for A13.
- **Server:** a minimal FastAPI SSE agent that emits scripted events, every one with `seq` and the run identifiers under `metadata` (task 1).
- **Client:** a minimal TS client with a reducer that records every received event (task 2).
- **A14:** a minimal Next.js 16 app with an `/agui/*` rewrite to the spike server, to time SSE through the rewrite.
- **Scenarios** (task 3), each producing a recorded JSONL stream under `spikes/agui/evidence/`:
  1. normal run;
  2. stream drop and replay;
  3. Stop and cancel (A11: client abort plus `RUN_ERROR` code `CANCELLED`);
  4. frontend-tool interrupt (A8, A12);
  5. clarification as an `input_required` interrupt;
  6. 64 KB CUSTOM payload and a 200-row table (A6);
  7. protocol-version negotiation (A9);
  8. zod peer check (A13);
  9. SSE through the Next.js rewrite, with time to first event (A14).
- **L1:** one minimal provider call, only if the GDQ-12 configuration is in your local `.env`. Otherwise record "not measured". **Never commit or print the key**, and never put it in the report (field 17).
- Commit freely on the spike branch, with messages starting `M0-T09 spike:`. Do not push unless the owner asks; the branch is never merged either way.

### 2. Report (task 4): `docs/architecture/spikes/AGUI_SPIKE_REPORT.md`

The sections follow ARCH-R076 exactly:
1. **Versions tested:** exact versions of every SDK, Python, Node, Next.js and zod, and the protocol version negotiated (AT-02).
2. **Results:** one row per item **A1 … A14 and L1**, each `pass`, `fail` or `adjusted`, with evidence: a short JSONL excerpt or the test output, quoted inline (AT-01). Do not link to spike-branch files; the branch is not merged.
3. **Deviations from DX4-AGUI**, with the recommended mapping for each (AT-03).
4. **Recommendation on ED-10** (Option A: AG-UI 1.0; Option B: last 0.x), with reasons (AT-03). If an SDK cannot be installed, say so and evaluate Option B (field 16).
5. **Open risks for PR-M4**, including which ARCH-R108 elements are affected (AT-03).

A failed item does not fail M0. Report it with a mapping (ARCH-R076). Keep evidence excerpts short; no secrets and no full payload dumps.

### 3. Docs branch (task 5)

Run `git switch main && git pull`, then the owner creates `docs/m0-t09-agui-spike-report`. Add only:
- the report;
- `tests/tooling/test_no_agui_dependency.py`, marked `@pytest.mark.trace("AT-M0-T09-04", reqs=["ARCH-R075"])`. It fails if `backend/uv.lock`, `backend/pyproject.toml`, `pnpm-lock.yaml` or any workspace `package.json` mentions an `ag-ui` / `@ag-ui/` package. Read the files at test time; hard-code no lockfile content. Include a negative self-test on a temporary copy that contains a fake `@ag-ui/core` entry.

### 4. Verification (paste all output)

On the spike branch:
```
git diff main -- backend/uv.lock pnpm-lock.yaml pnpm-workspace.yaml backend/pyproject.toml   # empty
ls spikes/agui/evidence/
```

On the docs branch:
```
git diff --stat main...HEAD                  # exactly the two files
make backend-test SUITE=tooling              # includes test_no_agui_dependency
make specs-check                             # report links and IDs valid
make check
make trace-report CARD=M0-T09                # AT-04 PASSED; AT-01..03 listed as manual
```

### 5. Report back

- **Do not push and do not open a PR.** The owner pushes the docs branch, and the architect reviews the report (AT-01 to AT-03 are manual reviews) and opens the docs PR.
- Report:
  - the result table (A1–A14, L1);
  - the versions;
  - the ED-10 recommendation, in one line;
  - anything you could not test, and why.

---

## 18. Run order to GATE-M0

| Step | Work | Starts when | Merge condition |
|---|---|---|---|
| 1 | M0-T05 (§13) | now | green `ci/summary`; `trace-report CARD=M0-T05` all `PASSED`; then STATUS marks CF-0 frozen with the GENERATED schema hashes |
| 2a | M0-T08 (§14) | M0-T05 merged | green `ci/summary`; AT-01 to AT-04 `PASSED`; the architect records AT-05 and the ECharts result in STATUS |
| 2b | M0-T06 (§15) | M0-T05 merged; in parallel with 2a | green `ci/summary`; AT-01 to AT-09 `PASSED`; AT-M0-T05-05 still `PASSED` |
| 3 | M0-T04 (§16) | M0-T06 and M0-T08 merged | green `ci/summary`; AT-01 to AT-12 `PASSED`; DEF-0006 closed; screenshots in the PR |
| any | M0-T09 spike (§17) | now | report docs PR reviewed; AT-04 `PASSED` |
| gate | `milestone-gate.yml` for M0 on the final `main` commit; GATE-M0-01 to -14 (`plans/M0_FOUNDATION.md`); manual results in `plans/gates/M0-manual-results.json`; owner approval | all of the above merged | owner approves GATE-M0 |

For each card: the owner creates the branch and runs the prompt; Composer commits without pushing; the owner pushes and shares the verification output; the architect reviews and either returns a fix prompt or opens the PR; the owner merges with **Squash and merge**; the architect records the merge in STATUS through a docs PR. PR-M1 specification authoring runs alongside, so slice day 1 is not blocked (ED-06 A).
