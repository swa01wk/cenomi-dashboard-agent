# M0 Implementation Handoff — Cursor Composer 2.5

| | |
|---|---|
| Version | 1.2 · 2026-10-23. Version 1.0 (2026-10-22) was delivered outside the repository. 1.1 applies corrections HC-1 to HC-5 (ROADMAP A-27). 1.2 adds the owner's operational clarifications (A-28): lockfile serialization, protection verification and the M0-T01 kickoff |
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

## 2. Cards and dependencies (from `plans/M0_FOUNDATION.md` v1.1, field 6)

| Card | Title | h | Merge depends on | ATs | Merges under |
|---|---|---|---|---|---|
| M0-T01 | Repository scaffold, toolchain, Makefile contract | 1.5 | — | 7 | P1 + EXC-001 |
| M0-T03 | Backend skeleton | 1.5 | T01 | 10 | P1 + EXC-001 |
| M0-T11 | Test harness, traceability markers, CI reporting | 1.0 | T01, T03 | 8 | P1 + EXC-001 |
| M0-T10 | Governance automation | 1.0 | T01, T11 | 7 | P1 + EXC-001 |
| M0-T07 | GitHub Actions workflows | 1.5 | T01, T03, T10, T11 | 8 | P1 (own run green) |
| M0-T02 | Compose (db, migrate, seed, api, otel), PostgreSQL bootstrap, migrations | 1.5 | T01, T03, T11 | 11 | P2 |
| M0-T05 | Contract pipeline (CF-0) | 1.5 | T01, T03 | 6 | P2 |
| M0-T08 | ECharts 5.6.0 verification harness | 1.0 | T01, T11 | 5 | P2 |
| M0-T06 | Dev sign-in, sessions, AccessScope interface (API level) | 1.0 | T03, T05 | 7 | P2 |
| M0-T04 | Web shell, sign-in journeys, Compose `web` service | 1.0 | T01, T02, T05, T06, T11 | 12 | P2 |
| M0-T09 | AG-UI 1.0 verification spike (throwaway) | 2.5 | T01 | 4 (manual) | Report via a docs PR |

**85 acceptance tests**, about 14 h. The graph is acyclic; the T04 ↔ T06 cycle was removed by HC-2.

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
| Makefile | T01 builds all 40 targets and the result helper; T02, T05, T08 and T10 replace their own stubs | `make_targets.yaml`; DEVENV §5; ARCH §10.8 |
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

