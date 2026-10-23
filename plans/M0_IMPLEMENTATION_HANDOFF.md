# M0 Implementation Handoff — Cursor Composer 2.5

| | |
|---|---|
| Version | 1.1 · 2026-10-23. Version 1.0 (2026-10-22) was delivered outside the repository. 1.1 applies corrections HC-1 to HC-5 (ROADMAP A-27) |
| Nature | **Non-normative.** A sequencing and orientation guide. It restates no contract. If it disagrees with a specification, the specification wins (AGENTSMD-R003) |
| Baseline | `main` @ `4515031` (PR-M0, spec set 0.1.0, CF-0 frozen), plus the M0 corrections PR (spec set 0.1.1) once the owner merges it |
| Build state | **Not authorized.** The owner authorizes Cursor separately, after the corrections PR is merged and protection stage P1 is applied (ADR-0015 §3) |

---

## 1. Prerequisites (owner)

| # | Action | Blocks |
|---|---|---|
| O-1 | Merge the M0 corrections PR (`docs/m0-implementation-corrections`) | The build authorization |
| O-2 | **Apply protection stage P1** on `main`: the DEVENV §8.4 stage table, plus the "settings applied together with P1" table | The first card merge |
| O-3 | Give Cursor the explicit M0 build authorization, pointing it at `AGENTS.md`, `.cursor/rules/` and this guide | Everything |
| O-4 | *Optional:* GDQ-12 configuration as a local secret | Spike item L1 only |
| O-5 | **Apply P2** (`ci/summary` required, strict) as soon as M0-T07 has merged and `ci/summary` is `success` on `main` | Every merge after M0-T07 |

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
O-1 corrections merged → O-2 P1 applied → O-3 authorized
Wave 0  T01                         merge under P1 + EXC-001
        ├─ T09 spike (parallel, any time)
        └─ T07 authoring starts; draft PR rebased after each bootstrap merge (EXC-001 C4)
Wave 1  T03 → T11 → T10              strictly sequential, P1 + EXC-001
Wave 2  T07: own run ci/summary success + trace-report CARD= for T01/T03/T11/T10 (C5a)
        merge → ci/summary success on main (C5b) → O-5 apply P2
Wave 3  T02 ║ T05 ║ T08              parallel lanes under P2 (DEVENV-R055 for shared files)
Wave 4  T06                          after T05
Wave 5  T04                          after T02 and T06
Gate    milestone-gate.yml → GATE-M0-01…14 → owner approval
```

**Must be sequential:** T01 → T03 → T11 → T10 → T07 → P2. Also T05 → T06 → T04, and T02 → T04 (T04 adds the `web` service to the Compose file that T02 creates).

**May run in parallel:**
- T09 with everything, after T01.
- T07 *authoring* with T03, T11 and T10. It *merges* only after T10.
- T02, T05 and T08 with each other. Their authoring may start once their merge dependencies are on `main`; they merge only after P2.
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
- **Parallel lanes (DEVENV-R055).** T05 and T08 both touch `pnpm-lock.yaml`. T02, T05 and T08 each touch their own `Makefile` recipes. The PR that merges second rebases onto `main` and regenerates; each PR names the other.

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

- [ ] M0 corrections PR merged; STATUS shows spec set 0.1.1
- [ ] P1 applied on `main`; verified by attempting a direct push, which must be rejected
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
