# M0 Implementation Handoff — Cursor Composer 2.5

| | |
|---|---|
| Version | 1.3 · 2026-10-23. Adds HC-6 and HC-7 (ROADMAP A-29), the M0-T03 and M0-T07 kickoff prompts (§9, §10) and the review-then-PR workflow. Version 1.2 added lockfile serialization, protection verification and the M0-T01 kickoff; 1.1 applied HC-1 to HC-5 (A-27); 1.0 (2026-10-22) was delivered outside the repository |
| Nature | **Non-normative.** A sequencing and orientation guide. It restates no contract. If it disagrees with a specification, the specification wins (AGENTSMD-R003) |
| Baseline | `main` from PR #3's squash commit onward: spec set **0.1.1** (CF-0 frozen at `4515031`, contract files unchanged) |
| Build state | **Not authorized.** The owner authorizes Cursor separately, after protection stage P1 is applied and verified (ADR-0015 §3) |

---

## 1. Prerequisites (owner)

| # | Action | Blocks |
|---|---|---|
| O-1 | ✅ PR #3 (corrections, spec set 0.1.1) approved and merged | — |
| O-2 | **Apply protection stage P1** on `main` (DEVENV §8.4, DEVENV-R056): (a) a ruleset targeting `main` with enforcement **active** and an **empty bypass list**, requiring a PR (0 approvals), resolved conversations, and blocking force pushes and deletion; (b) repository merge settings: squash only (disable merge commits and rebase merging), delete head branches; (c) the companion settings table. **Verify without pushing:** record the ruleset ID, `bypass_actors: []`, `current_user_can_bypass` = `never`, the `GET /repos/swa01wk/cenomi-dashboard-agent/rules/branches/main` output, the merge settings and `updated_at` in STATUS | The first card merge |
| O-3 | Give Cursor the explicit M0 build authorization, pointing it at `AGENTS.md`, `.cursor/rules/` and this guide | Everything |
| O-4 | *Optional:* GDQ-12 configuration as a local secret | Spike item L1 only |
| O-4a | *Recommended:* give Composer a fine-grained personal access token for this repository only, with Contents and Pull requests write and **no Administration** permission (DEVENV-R056) | — |
| O-5 | **Apply P2** (`ci/summary` required, strict) as soon as M0-T07 has merged and `ci/summary` is `success` on `main`; verify it the same way as P1 | Every merge after M0-T07 |

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

