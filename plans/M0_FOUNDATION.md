# M0_FOUNDATION — milestone plan

| | |
|---|---|
| Milestone | M0 Foundation |
| Version | 1.1 · 2026-10-23 · M0 corrections PR: HC-1 to HC-5 (ROADMAP A-27). 1.0 merged in PR-M0 (`4515031`) |
| Specification state | 1.0 approved and merged (PR #2, `4515031`); 1.1 corrections in review. Progress lives only in `plans/STATUS.md` |
| Build state | **Not authorized.** See §8 for the exact conditions |
| Freezes | CF-0 (ROADMAP §3.2) |
| Normative inputs | ARCHITECTURE, DEVELOPMENT_ENVIRONMENT, PRODUCT_SPEC §3 and §6.4, ADR-0001 to ADR-0006, ADR-0015 to ADR-0018, `specs/contracts/*` (CF-0), `specs/engineering/*`, `specs/traceability/id_conventions.yaml` |
| Delivery class | Every M0 card is `slice` except M0-T09, which is `full`: the AG-UI spike is pre-slice evidence for PR-M4. Under ED-06 A, M0 is built before slice day 1 (ROADMAP §8) |

---

## 1. Objective and scope

M0 delivers the seams every later milestone plugs into:
- a reproducible toolchain behind one Makefile contract;
- a Compose stack with the database roles and the six empty schemas;
- backend and web skeletons that enforce module boundaries, error contracts, the security boundary, and structured logging;
- the contract pipeline proven on the CF-0 contracts;
- dev sign-in with the AccessScope interface (deny by default);
- CI with stable required checks and reporting;
- the test harness with traceability;
- the ECharts verification harness;
- a throwaway AG-UI spike with its report.

**Not in M0** (ARCHITECTURE §1):
- business tables, metrics or seed data (M1–M2);
- agent code, model providers and AG-UI product code (M3–M4);
- dashboards beyond the shell (M2);
- insights (M6).

---

## 2. Prerequisites

| Prerequisite | Needed by | State |
|---|---|---|
| PR-M0 approved and merged (CF-0 frozen) | All cards | In review |
| Owner's explicit authorization to begin the M0 build (ED-06 A) | All cards | Not given |
| ED-07 (sign-in) decided (decision text: DECISION_REGISTER §5.1) | M0-T06, M0-T04 (`/sign-in`) | **Approved 2026-10-22**, Option A (ADR-0016) |
| ED-08 (model determinism) decided (DECISION_REGISTER §5.1) | M0-T07 (`eval-live.yml` skeleton), M0-T11 (`LLM_MODE` values) | **Approved 2026-10-22**, Option A (ADR-0017) |
| ED-09 (styling) decided (DECISION_REGISTER §5.1) | M0-T04 (shell styling) | **Approved 2026-10-22**, Option A (ADR-0018) |
| GDQ-12 configuration (provider, models, key) | M0-T09 item L1 only; if absent, L1 is recorded "not measured" | Not supplied |
| Repository protection stage **P1** (DEVENV §8.4) | Before the first card PR merges | Policy approved 2026-10-22 (0 required approving reviews accepted); **not yet applied** (owner action) |
| **EXC-001** (pre-CI bootstrap merges of M0-T01, T03, T11, T10; DEVENV-R051) approved, or another approved way to merge them | Merges of those four cards | **Approved conditionally 2026-10-22**, conditions C1–C7 (DEVENV §8.4) |
| Repository protection stage **P2** (`ci/summary` required) | Immediately after M0-T07 merges, before any further merge | Policy approved 2026-10-22; applied after M0-T07 merges |

---

## 3. Build sequence (one developer)

```
Bootstrap (merged under P1 + EXC-001):  M0-T01 → M0-T03 → M0-T11 → M0-T10
CI in force (merged under P1, then P2):  M0-T07  ── P2 enabled ──▶  M0-T02 → M0-T05 → M0-T06 → M0-T04 → M0-T08
M0-T09 (spike branch) at any point after M0-T01; its report merges through a docs PR (under P2 once in force)
```

**Why this order.** CI is brought up as early as possible, so that every card after M0-T07 merges with `ci/summary` required.

| Card | Merges under | Notes |
|---|---|---|
| M0-T01, M0-T03, M0-T11, M0-T10 | Stage P1 with EXC-001 | They build the tooling CI runs. Each PR pastes local `make check` output and its AT results |
| M0-T07 | Stage P1 | Its own PR run must show `ci/summary` `success`, including `trace-report CARD=…` for the four bootstrap cards |
| Every later card | Stage P2 | Until a card merges, its targets report `NOT_IMPLEMENTED` within the build window (ARCH-R103); its own ATs must be `PASSED` on its PR (ARCH-R105) |

**EXC-001 condition C4: can M0-T07 come earlier?** Investigated 2026-10-22.

- *Finding.* M0-T07 cannot merge, with its acceptance tests passing, before all four bootstrap cards. AT-M0-T07-02 needs `trace-report` (M0-T10). `scripts/ci/summary.py` needs the report parsers (M0-T11), and M0-T11 needs the backend test configuration (M0-T03). Every job runs Make targets (M0-T01). Four exception-covered merges is therefore the minimum without re-scoping cards.
- *Adopted mitigation, within the approved card scope.* Authoring of M0-T07 starts as soon as M0-T01 merges, in parallel with M0-T03, M0-T11 and M0-T10. Its PR is opened as a **draft** on `main` and rebased after each bootstrap merge. GitHub Actions then runs the real workflows against each merged bootstrap card early, as non-required evidence, and the M0-T07 PR is ready for review the moment M0-T10 merges. The unverified window shrinks from "after all four cards" to "between each bootstrap merge and the next draft run".
- *Not adopted (would need the owner's approval).* Splitting a minimal CI smoke workflow out of M0-T07 into a separate card before M0-T03. It adds a merge and a card. Its runs could not include `trace-report`, so it would not remove any of the four exceptions.

**Effort (focused hours).**

| T01 | T02 | T03 | T04 | T05 | T06 | T07 | T08 | T09 | T10 | T11 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.5 | 1.5 | 1.5 | 1.0 | 1.5 | 1.0 | 1.5 | 1.0 | 2.5 | 1.0 | 1.0 | **≈ 14** |

---

## 4. Task cards

Every card follows the 20-field standard (RMAP-R007). The format is machine-checked by `make specs-check` (AT-M0-T10-06): one level-3 heading per card, followed by one table whose rows are numbered 1–20.

### M0-T01 — Repository scaffold, toolchain and Makefile contract

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T01 |
| 2 | Requirement references | DEVENV-R001–R015; ARCH-R004; RMAP-R006; ADR-0002, ADR-0003; DR-027, DR-037 |
| 3 | Owning milestone | M0 |
| 4 | Objective | A clean clone installs deterministically from lockfiles and exposes the full Makefile target contract. Every target reports its result in the ARCHITECTURE §10.8 vocabulary |
| 5 | Scope and exclusions | **In:** root configuration files; uv workspace in `backend/`; pnpm workspace (`apps/web`, `packages/contracts-ts`, `packages/viz`) with empty package skeletons; lockfiles; `.env.example`; the root `Makefile` implementing all 40 targets of `specs/engineering/make_targets.yaml`; `scripts/make/` helpers; `scripts/tools.lock`. **Out:** application code (T03, T04), Compose (T02), workflows (T07) |
| 6 | Dependencies | §2 prerequisites |
| 7 | Backend deliverables | `backend/pyproject.toml`: `requires-python ==3.12.*`. Runtime deps for M0 only: fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy (2.0.x), psycopg (3.x), alembic, opentelemetry-sdk with the FastAPI and SQLAlchemy instrumentation. Dev group: ruff, mypy, import-linter, pytest, pytest-asyncio, pytest-xdist, pytest-cov, pytest-socket, hypothesis, httpx, jsonschema, pyyaml, pip-audit. Also `uv.lock` and `[tool.uv] required-version` |
| 8 | Frontend deliverables | Root `package.json` (`packageManager`, `engines.node`), `pnpm-workspace.yaml`, `.npmrc` (`engine-strict=true`), package manifests, `pnpm-lock.yaml`. Dev tooling: typescript, eslint (flat config) with a boundaries plugin, prettier, vitest, @testing-library/react, jsdom, @playwright/test, @axe-core/playwright |
| 9 | Agent deliverables | N/A — no agent code in M0 |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | `specs/engineering/make_targets.yaml` (exact target set, arguments, exit codes, result reporting); ARCHITECTURE §10.8; DEVENV §4 variable catalogue |
| 12 | Implementation tasks | 1. Root files: `.gitignore` (`.env`, `tests/reports/`, build outputs), `.editorconfig`, `.python-version`, `.nvmrc`. 2. uv workspace and lock. 3. pnpm workspace and lock. 4. `.env.example` with every DEVENV §4 variable and recognisably fake placeholders. 5. Makefile: one rule per target in YAML order; arguments as Make variables; result helper reading `active_milestone` from `specs/engineering/spec_set.yaml` and appending to `tests/reports/status.jsonl` (ARCH-R102); exit-code conventions. 6. `make help` generated from Makefile `##` comments in YAML order. 7. Tooling tests |
| 13 | File and module ownership | `/Makefile`, `/scripts/make/**`, `/scripts/tools.lock`, `/.gitignore`, `/.editorconfig`, `/.python-version`, `/.nvmrc`, `/.npmrc`, `/package.json`, `/pnpm-workspace.yaml`, `/pnpm-lock.yaml`, `/.env.example`, `/backend/pyproject.toml`, `/backend/uv.lock`, `/apps/web/package.json`, `/packages/*/package.json`, `/tests/tooling/test_make_contract.py` |
| 14 | Test cases | `tests/tooling/test_make_contract.py` (pytest, subprocess `make`): AT-M0-T01-01 to 07 |
| 15 | Acceptance criteria | **AT-M0-T01-01** `make install` on a clean clone succeeds and leaves `git status` clean (no lockfile change). **AT-M0-T01-02** `make doctor` exits 0 on a conforming toolchain and 3 when a PATH shim reports Node 20. **AT-M0-T01-03** `make help` lists exactly the targets of `make_targets.yaml`, in order. **AT-M0-T01-04** With `active_milestone: M0`: every target with `active_from` > M0 reports `NOT_APPLICABLE`, naming the milestone rule, in `status.jsonl` and exits 0; a stubbed M0 target reports `NOT_IMPLEMENTED` and exits 0, but exits 1 with `GATE=M0`; with `active_milestone` set to M1 in a test copy, a stubbed M0 target exits 1; no target reports `PASSED` without executing. **AT-M0-T01-05** `make down VOLUMES=1` without `CONFIRM=yes`, and `make db-downgrade` without `REV`, exit 2. **AT-M0-T01-06** `make check` passes on the skeleton while no database is reachable. **AT-M0-T01-07** `.env.example` contains every DEVENV §4 variable, and gitleaks reports nothing in it except the allow-listed placeholders |
| 16 | Failure and recovery scenarios | Lockfile out of date → `install` exits 1 and never rewrites it. Missing tool → exit 3 with the tool named. Partial install → re-run `make install` (idempotent) |
| 17 | Security requirements | No secret in any committed file. `.env` is git-ignored. Placeholders are allow-listed by exact path only |
| 18 | Observability requirements | Each Make target prints the commands it runs and a final `OK <target>` or `FAIL <target> (exit n)` line |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–07 pass in CI (`ci/static`, `ci/specs`); `make check` green; PR merged |

### M0-T02 — Compose stack, PostgreSQL bootstrap and migration framework

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T02 |
| 2 | Requirement references | ADR-0006; ARCH-R002, R032, R033, R056–R065; DEVENV-R005, R010, R016, R017; DATA-06; SEC-01; CA-06 |
| 3 | Owning milestone | M0 |
| 4 | Objective | `make up` starts db and api on a clean volume (the `web` service is added by M0-T04; HC-3). The four roles and six empty schemas exist with exactly the ADR-0006 grants. Alembic works, and destructive operations are guarded |
| 5 | Scope and exclusions | **In:** `docker-compose.yml` (db, migrate, seed, api, otel profile; the `web` service is added by M0-T04, HC-3); `infra/postgres/bootstrap/roles.sql`; `cenomi.db` (engines, guards, role verification); `cenomi db init` and `cenomi db verify-roles`; Alembic configuration; revision `0001_m0_schemas_and_grants`; database Make targets. **Out:** any table in any schema; seed logic (M1). The `seed` service is defined and reports `NOT_APPLICABLE` (active from M1) |
| 6 | Dependencies | M0-T01, M0-T03 (package skeleton, `cenomi.core`, health router), M0-T11 (`backend/tests/conftest.py`, where this card registers its fixture plugin) |
| 7 | Backend deliverables | `cenomi.db.engines` (async reader and app engines; ARCH-R032 settings); `cenomi.db.guards` (DG-1 to DG-5, ARCH-R064); `cenomi.db.health.check_database()` (used by T03); CLI sub-commands `db init` and `db verify-roles`; `backend/alembic.ini`; `backend/migrations/env.py` (owner URL, `version_table_schema=public`); revision 0001 |
| 8 | Frontend deliverables | N/A |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | Also the test-database fixtures: a per-xdist-worker `cenomi_test_gw<N>` created from a migrated template, and transaction rollback for state-writing tests (ARCH-R065), as a pytest plugin `backend/tests/fixtures/db.py`, which this card registers in M0-T11's `backend/tests/conftest.py` (composition point, DEVENV-R054). Roles `cenomi_owner`, `cenomi_seed`, `cenomi_reader`, `cenomi_app`. Databases `cenomi_dev` and `cenomi_test`. Schemas `core`, `meta`, `snap`, `seed_meta`, `agent`, `insights`. Grants and default privileges exactly per ADR-0006 §3; reader role defaults `default_transaction_read_only=on`, `statement_timeout=5000`; PUBLIC revoked; SELECT on `public.alembic_version` for the reader. No tables |
| 11 | Interfaces and contracts | ADR-0006; ARCHITECTURE §5.8, §7; `make_targets.yaml` database group |
| 12 | Implementation tasks | 1. `roles.sql`, idempotent (`DO $$ … IF NOT EXISTS …`). 2. Guards with table-driven unit tests. 3. `db init`: superuser connection; create roles and databases; revoke PUBLIC. 4. Alembic environment and revision 0001. 5. Engines. 6. `verify-roles`, using `has_*_privilege` functions only. 7. Compose services with pinned digests, 127.0.0.1 port bindings and non-root users. 8. Make targets `db-*` and `up`/`down`/`logs` wiring |
| 13 | File and module ownership | `/docker-compose.yml`, `/infra/postgres/**`, `/backend/alembic.ini`, `/backend/migrations/**`, `/backend/src/cenomi/db/**`, `/backend/src/cenomi/cli/db.py`, `/backend/tests/unit/db/**`, `/backend/tests/integration/db/**`, `/backend/tests/fixtures/db.py`, `/backend/tests/integration/api/test_health_db.py`, `/tests/tooling/test_compose.py`. Composition points (DEVENV-R054): the `db-*`, `up`, `down` and `logs` recipes in `/Makefile`; the `pytest_plugins` entry in `/backend/tests/conftest.py`; the `check_database` provider binding in `cenomi.api` health wiring; the `db` sub-command registration in the `cenomi` CLI entry point |
| 14 | Test cases | `backend/tests/unit/db/test_guards.py`; `backend/tests/integration/db/test_roles_and_grants.py`; `test_migrations.py`; `test_pool_settings.py`; `tests/tooling/test_compose.py` |
| 15 | Acceptance criteria | **AT-M0-T02-01** On a clean volume `make up` ends with db and api healthy and revision 0001 applied (web: AT-M0-T04-12, HC-3). **AT-M0-T02-02** The six schemas exist, owned by `cenomi_owner`, with no tables. **AT-M0-T02-03** `cenomi_reader`: sessions are read-only; `statement_timeout` is 5000; inserting into an owner-created probe table in `core` fails; no USAGE on `seed_meta`, `agent`, `insights`. **AT-M0-T02-04** `cenomi_app`: no USAGE on `core`, `meta`, `snap`, `seed_meta`; can insert into an owner-created probe table in `agent` without an explicit GRANT (default privileges). **AT-M0-T02-05** Only `cenomi_seed` and `cenomi_owner` can read an owner-created probe table in `seed_meta`. **AT-M0-T02-06** A table created later by the owner in `core` is readable by `cenomi_reader` with no extra GRANT. **AT-M0-T02-07** Each guard DG-1 to DG-5 refuses its failing case with exit 2 (table-driven). **AT-M0-T02-08** `make db-init` twice is idempotent; `make db-check DB=test` passes after `db-upgrade`. **AT-M0-T02-09** (CA-06) Through the reader pool, `SELECT pg_sleep(6)` is cancelled by the statement timeout and surfaces as a typed error. **AT-M0-T02-10** The published ports of db and api bind to 127.0.0.1 only; the api container runs as non-root (web: AT-M0-T04-12, HC-3). **AT-M0-T02-11** Against a migrated `cenomi_test`: `GET /api/v1/health` returns 200 `ok` and validates against `health_report.v1`, with every required check `pass` and `dataset` `skipped`; it returns 503 `fail` when the reader URL points to a closed port; it returns 503 `fail` when `alembic_version` is not at head |
| 16 | Failure and recovery scenarios | db not ready → `up` waits on the health check (no sleeps) and fails after 120 s with the db logs. A failed migration rolls back its revision and exits 1. A corrupted local volume → `make down VOLUMES=1 CONFIRM=yes`, then `make up` |
| 17 | Security requirements | Superuser credentials only in the local and CI `DATABASE_URL_ADMIN`. The `api` container never receives owner, seed or admin URLs. Guards protect every destructive path. Probe tables are created and dropped inside test transactions |
| 18 | Observability requirements | CLI commands log JSON (ARCH-R096) with `service=cli`, the role used (never the password) and the guard outcomes |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–11 pass in `ci/backend`, `ci/database`, `ci/e2e`; `make db-check` green; PR merged |

### M0-T03 — Backend skeleton: modules, core, errors, health and logging

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T03 |
| 2 | Requirement references | ADR-0005; ARCH-R002, R004–R016, R019–R031, R034, R096–R099; SEC-06; NFR-03 |
| 3 | Owning milestone | M0 |
| 4 | Objective | A FastAPI modular monolith with all 12 module packages, enforced boundaries, configuration validation, the error envelope, request references, JSON logs with tracing, and the health and dataset endpoints |
| 5 | Scope and exclusions | **In:** `cenomi` package skeleton (12 modules, each with a README per ARCH-R004); `core` (settings, logging, telemetry, errors, clock, ids); `api` app factory; routers `health` and `dataset`; exception handlers; request-ref middleware; `backend/.importlinter`; `scripts/lint/sql_safety.py`; `backend/Dockerfile`. **Out:** sessions and `/me` (T06); contract export (T05) |
| 6 | Dependencies | M0-T01 |
| 7 | Backend deliverables | Routes `GET /api/v1/health/live`, `GET /api/v1/health`, `GET /api/v1/dataset` (ARCHITECTURE §5.4); handlers for `CenomiError`, request validation (400) and unhandled exceptions (500); middleware adding `X-Request-Ref` and `Cache-Control: no-store` and propagating `traceparent`; the `cenomi` console script with argparse |
| 8 | Frontend deliverables | N/A |
| 9 | Agent deliverables | N/A. `cenomi.agent`, `agui`, `presentation`, `insights`, `semantic`, `analytics` and `seed` contain only `__init__.py` and a README |
| 10 | Database and data requirements | The health router calls `cenomi.db.health.check_database()`, which M0-T02 implements. M0-T03 ships the router and its interface, and tests it against a test double; the real-database health tests are AT-M0-T02-11. No schema changes |
| 11 | Interfaces and contracts | `health_report.v1`, `dataset_descriptor.v1`, `error_envelope.v1`, `error_codes.v1.yaml` |
| 12 | Implementation tasks | 1. Package tree and READMEs. 2. Import-linter contracts encoding ARCH-R006/R007. 3. Settings with startup validation. 4. JSON log formatter with redaction. 5. OpenTelemetry setup (console, otlp or none). 6. Error hierarchy and handlers. 7. Request-ref middleware. 8. Health and dataset routers. 9. SQL safety lint. 10. Dockerfile (non-root, uv) |
| 13 | File and module ownership | `/backend/src/cenomi/**` except `db/**` (T02), `auth/**` (T06) and `contracts/**` (T05); `/backend/.importlinter`; `/backend/Dockerfile`; `/scripts/lint/sql_safety.py`; `/backend/tests/unit/{core,api}/**`; `/backend/tests/integration/api/**` except the files named by M0-T02 and M0-T06; `/tests/tooling/test_import_boundaries.py`; `/tests/tooling/test_sql_safety_lint.py`. Owns the composition points `cenomi.api.app.create_app()` (router registration), the health wiring and the `cenomi` CLI entry point (DEVENV-R054) |
| 14 | Test cases | `backend/tests/unit/core/test_settings.py`, `test_logging.py`; `backend/tests/unit/api/test_errors.py`; `backend/tests/integration/api/test_health.py`, `test_dataset.py`; `tests/tooling/test_import_boundaries.py`; `tests/tooling/test_sql_safety_lint.py` |
| 15 | Acceptance criteria | **AT-M0-T03-01** Startup is refused, with a clear message, for each invalid configuration case a, b, c, e and f of ARCH-R026 (table-driven). **AT-M0-T03-02** With `check_database()` replaced by a test double reporting every required check `pass`, `GET /api/v1/health` returns 200 `ok`, the body validates against `health_report.v1`, and `dataset` is `skipped`. **AT-M0-T03-03** With the test double reporting `db_reader` `fail`, or a check exceeding 2 s, it returns 503 `fail`. **AT-M0-T03-04** `lint-imports` passes; a temporary forbidden import (analytics → agent) makes it fail. **AT-M0-T03-05** Every non-2xx response is a valid `error_envelope.v1` whose `requestRef` equals `X-Request-Ref`. An unknown query parameter gives 400 `VALIDATION_ERROR` whose details do not contain the submitted value; status 422 never occurs. **AT-M0-T03-06** An unhandled exception gives 500 `INTERNAL` with the generic message; the stack trace appears in the log line carrying the same `requestRef` and never in the body. **AT-M0-T03-07** Log lines are JSON with the ARCH-R096 base fields; `SecretStr` values and URL passwords are redacted. **AT-M0-T03-08** `GET /api/v1/dataset` returns a valid `dataset_descriptor.v1` with `source: config`, `state: declared`. **AT-M0-T03-09** The SQL safety lint flags an f-string passed to `text()` in a negative fixture. **AT-M0-T03-10** An incoming `traceparent` trace ID appears as `traceId` in the request's log lines |
| 16 | Failure and recovery scenarios | Database down at start → the API starts and health reports `fail` (ARCH-R002). A check exceeding 2 s fails without hanging the request. A misconfiguration exits non-zero before binding the port |
| 17 | Security requirements | No stack trace, SQL or secret in responses. Unknown parameters rejected. `Cache-Control: no-store`. Startup refuses an unsafe `AUTH_MODE`/`CENOMI_ENV` combination |
| 18 | Observability requirements | ARCH-R096 fields on every request log; the `event` names `request_completed` and `request_failed`; health check durations in the report |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–10 pass in `ci/static` and `ci/backend`; PR merged |

### M0-T04 — Web shell: routes, layouts, data client and boundaries

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T04 |
| 2 | Requirement references | ARCH-R001, R035–R046, R053–R055; PSPEC-R002, R004, R007; DXD-01, 07, 09, 19; DATA-07; NFR-02; ED-07 (approved, ADR-0016); ED-09 (approved, ADR-0018); ARCH-R045 and E2E-SHELL-02, E2E-SHELL-03 (with AT-M0-T04-10, -11, moved from M0-T06 by HC-2; references kept on both cards); DEVENV-R016, R017 (with AT-M0-T04-12, moved from M0-T02 by HC-3) |
| 3 | Owning milestone | M0 |
| 4 | Objective | The Next.js shell renders the fixed route map with the synthetic banner, persona-aware navigation and responsive structure. It fetches data only through the typed same-origin client and enforces web boundaries |
| 5 | Scope and exclusions | **In:** `apps/web` App Router routes (ARCHITECTURE §6.2) with placeholders; `(app)` and `(auth)` layouts; rail and bottom tab bar; banner from `/api/v1/dataset`; `/sign-in` UI calling the T06 dev routes; `lib/api` client with zod parsing; TanStack Query provider and key factory; `ShellState` context; error and not-available states; rewrites; security headers; ESLint boundaries; `apps/web/Dockerfile`; the Compose `web` service (DEVENV-R016), added to `docker-compose.yml` (HC-3). **Out:** dashboards, cards, panel content, inspector content (M2/M4); design tokens (PR-M2) — the shell uses a minimal style sheet replaced by the token CSS in M2 |
| 6 | Dependencies | M0-T01, M0-T02 (`docker-compose.yml`, for the `web` service), M0-T05 (generated zod), M0-T06 (session API), M0-T11 (Vitest and Playwright configuration); ED-07 and ED-09 decided |
| 7 | Backend deliverables | N/A |
| 8 | Frontend deliverables | Routes `/sign-in`, `/`, `/admin`, `/tenant`, `/workspace`, `/workspace/[threadId]`, `/insights`, `/insights/[insightId]`; shell components (rail, top bar with persona and a disabled bell, banner); placeholder component "Delivered in M<n>"; `lib/api/client.ts`; `lib/api/queryKeys.ts`; `lib/state/shell.tsx`; `next.config` rewrites (`/api/*`, `/agui/*` → `API_INTERNAL_URL`) and headers; ESLint configuration |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | `principal.v1`, `dataset_descriptor.v1`, `error_envelope.v1` (generated zod from T05); ARCHITECTURE §6 |
| 12 | Implementation tasks | 1. App Router tree and layouts. 2. API client and query provider. 3. Session redirect logic (401 → `/sign-in`). 4. Banner and rail with responsive breakpoints (1280, 820). 5. Sign-in picker. 6. Placeholders. 7. Rewrites and headers. 8. ESLint boundaries and `react/no-danger`. 9. Vitest and Playwright tests. 10. Dockerfile. 11. Compose `web` service (port bound to 127.0.0.1, non-root, health check `GET /`) |
| 13 | File and module ownership | `/apps/web/**` except `/apps/web/package.json` (M0-T01; dependency changes per DEVENV-R052) and `/apps/web/vitest.config.ts` (M0-T11); `/tests/e2e/shell/**` (including `auth.spec.ts`, moved from M0-T06 by HC-2); `/tests/tooling/test_web_boundaries.py`; `/tests/tooling/test_compose_web.py`. Composition point (DEVENV-R054): the `web` service block in `/docker-compose.yml` |
| 14 | Test cases | Vitest: `apps/web/src/lib/api/client.test.ts`, `apps/web/src/lib/state/shell.test.tsx`; Playwright: `tests/e2e/shell/shell.spec.ts` (E2E-SHELL-01, E2E-NAV-01), `tests/e2e/shell/responsive.spec.ts` (E2E-RESP-01…03), `tests/e2e/shell/auth.spec.ts` (AT-M0-T04-10, -11; E2E-SHELL-02, E2E-SHELL-03); `tests/tooling/test_web_boundaries.py` (negative lint fixtures); `tests/tooling/test_compose_web.py` (AT-M0-T04-12) |
| 15 | Acceptance criteria | **AT-M0-T04-01** (E2E-SHELL-01) A signed-out visit to any route lands on `/sign-in`, showing the banner "SYNTHETIC DATA · AS OF 20 OCT 2026" from `/api/v1/dataset`. **AT-M0-T04-02** (E2E-NAV-01) Every route in ARCHITECTURE §6.2 renders the shell and its placeholder names the delivering milestone. **AT-M0-T04-03** (E2E-RESP-01…03) A rail at 1440 × 900 and 1024 × 768; a bottom tab bar at 390 × 844; the banner visible in all three. **AT-M0-T04-04** `/api/v1/health` is reachable through the web origin; `/agui/v1/anything` returns the API's 404 envelope, proving the rewrite. **AT-M0-T04-05** Negative lint fixtures fail: `features/` importing `app/`; `echarts` imported outside `packages/viz`; `dangerouslySetInnerHTML`. **AT-M0-T04-06** The API client turns a response that fails zod parsing into an `INTERNAL` error carrying the `requestRef` and renders nothing from it. **AT-M0-T04-07** Sign-out clears the TanStack Query cache and session-stored shell state. **AT-M0-T04-08** Responses carry `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin` and `Content-Security-Policy: frame-ancestors 'none'`. **AT-M0-T04-09** axe-core reports no serious or critical violations on `/sign-in` and the signed-in shell. **AT-M0-T04-10** (moved from AT-M0-T06-03 by HC-2; ARCH-R045) After signing in through `/sign-in`, `document.cookie` in the browser never contains the session (Playwright). **AT-M0-T04-11** (E2E-SHELL-02, E2E-SHELL-03; moved from M0-T06, formerly its eighth AT, by HC-2) Signing in as each fixture principal lands on `/admin` or `/tenant` by persona; signing out returns to `/sign-in`. **AT-M0-T04-12** (moved from AT-M0-T02-01 and AT-M0-T02-10 by HC-3; DEVENV-R016, R017) On a clean volume `make up` ends with web healthy (`GET /` returns 200 or 307) and the shell served at http://localhost:3000; the web port binds to 127.0.0.1 only and the web container runs as non-root |
| 16 | Failure and recovery scenarios | API down → banner area and pages show the error state with Retry and the `requestRef` (DX2 States 5). Dataset call fails → the banner still shows "SYNTHETIC DATA" with "as of" unavailable, never a fabricated date |
| 17 | Security requirements | No secret or `NEXT_PUBLIC_*` secret. No authorization decisions in web. No data fetching in Server Components. No HTML from responses |
| 18 | Observability requirements | Client logs (console) of failed calls include the `requestRef`. Playwright captures network logs (T11) |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–12 pass in `ci/frontend` and `ci/e2e`; screenshots attached to the PR at three widths; PR merged |

### M0-T05 — Contract pipeline (CF-0)

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T05 |
| 2 | Requirement references | ADR-0004; ARCH-R015, R092, R093; DR-028; CA-05 |
| 3 | Owning milestone | M0 |
| 4 | Objective | Pydantic models export exactly the CF-0 bootstrap schemas. TypeScript types and zod 4 schemas are generated deterministically, and CI fails on drift |
| 5 | Scope and exclusions | **In:** `cenomi.contracts` models for `error_envelope.v1`, `principal.v1`, `scope_decision.v1`, `health_report.v1`, `dataset_descriptor.v1`; `scripts/codegen/export_schemas.py` (normalization); `json-schema-to-typescript` wiring; in-repo `scripts/codegen/zod_from_schema.ts`; `packages/contracts-ts`; `make codegen` and `make contracts-check`; the schema-subset checker; the error-code registry test. **Out:** later contracts |
| 6 | Dependencies | M0-T01, M0-T03 |
| 7 | Backend deliverables | Pydantic v2 models with `alias_generator=to_camel`, `populate_by_name=True`, `extra="forbid"`; serialization by alias |
| 8 | Frontend deliverables | `packages/contracts-ts/src/types/*` and `src/zod/*` (GENERATED headers); package exports |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | The six CF-0 files in `specs/contracts/`; ADR-0004 §2 subset |
| 12 | Implementation tasks | 1. Models. 2. Exporter and normalizer (sorted keys; ignore `title`/`description`; compare `$id`). 3. Subset checker. 4. TS generation. 5. Zod generator for the subset. 6. Equivalence tests. 7. Registry scan. 8. Make targets |
| 13 | File and module ownership | `/backend/src/cenomi/contracts/**`, `/scripts/codegen/**`, `/packages/contracts-ts/**` except `package.json` (M0-T01; dependency changes per DEVENV-R052), `/tests/contract/**`. Composition point (DEVENV-R054): the `codegen` and `contracts-check` recipes in `/Makefile` |
| 14 | Test cases | `tests/contract/test_bootstrap_equivalence.py`, `test_subset.py`, `test_error_registry.py`, `test_codegen_idempotent.py`; `packages/contracts-ts/src/zod/equivalence.test.ts` |
| 15 | Acceptance criteria | **AT-M0-T05-01** Each model's export equals its bootstrap schema under normalized comparison. **AT-M0-T05-02** `make codegen` run twice produces no diff. **AT-M0-T05-03** Editing a GENERATED file makes `make contracts-check` fail. **AT-M0-T05-04** The subset checker rejects negative fixtures using `anyOf`, an open object, and an unsupported `format`. **AT-M0-T05-05** Every code raised by backend `CenomiError` subclasses is in `error_codes.v1.yaml` with `status: active`, and every active code is raisable. **AT-M0-T05-06** (CA-05) For every schema, every example and a generated set of invalid mutations are accepted or rejected identically by `jsonschema` and the generated zod schema |
| 16 | Failure and recovery scenarios | A generator failure leaves committed files untouched (writes to a temp directory, then swaps). A schema/model mismatch reports the JSON path of the first difference |
| 17 | Security requirements | Generated validators reject unknown fields (`additionalProperties: false`, zod `.strict()`) |
| 18 | Observability requirements | N/A — build-time tooling; diffs printed to CI logs |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–06 pass in `ci/contracts`; PR merged; CF-0 marked frozen in STATUS |

### M0-T06 — Dev sign-in, sessions and the AccessScope interface

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T06 |
| 2 | Requirement references | ARCH-R016, R026 (case e), R045, R046, R077–R082; DR-019, DR-020; DXD-38, DXD-85; SEC-02, SEC-03; ED-07 (approved 2026-10-22, ADR-0016) |
| 3 | Owning milestone | M0 |
| 4 | Objective | Fixture principals can sign in through a signed httpOnly cookie. `/api/v1/me` returns the principal, and `AccessScope.authorize` implements deny by default and narrow-only semantics for the CF-0 contract |
| 5 | Scope and exclusions | **In:** `tests/fixtures/principals.yaml` (ARCH-R078); `cenomi.auth.session` (stdlib `hmac` SHA-256 signed cookie `cenomi_session`: principal ID, issued-at, expiry; TTL from `SESSION_TTL_MINUTES`); `current_principal` dependency; routes `/api/v1/me`, `/api/v1/auth/dev/principals`, `/api/v1/auth/dev/sign-in`, `/api/v1/auth/sign-out`; `cenomi.auth.scope.AccessScope` and the fingerprint. **Out:** permissions matrix and hierarchy resolution (PR-M1, ADR-0008); passwords and identity providers |
| 6 | Dependencies | M0-T03, M0-T05; ED-07 decided |
| 7 | Backend deliverables | As in Scope; dev routes mounted only when `AUTH_MODE=dev_fixture` |
| 8 | Frontend deliverables | N/A (the `/sign-in` UI is M0-T04) |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | None; principals are read from the fixture file. Business keys are provisional until CF-1 |
| 11 | Interfaces and contracts | `principal.v1`, `scope_decision.v1`, `error_envelope.v1` |
| 12 | Implementation tasks | 1. Fixture loader with schema validation. 2. Cookie signing and verification (constant-time compare). 3. Dependencies and routes. 4. `authorize()` for ALL and same-kind intersections; `hierarchy_unresolved` for cross-kind. 5. Canonical JSON fingerprint. 6. Tests, including property tests |
| 13 | File and module ownership | `/backend/src/cenomi/auth/**`, `/backend/src/cenomi/api/routers/session.py`, `/tests/fixtures/principals.yaml`, `/backend/tests/unit/auth/**`, `/backend/tests/integration/api/test_session.py`, `/tests/security/test_scope_deny_by_default.py`. Composition point (DEVENV-R054): the `session` router registration in `cenomi.api.app.create_app()`. `/tests/e2e/shell/auth.spec.ts` moved to M0-T04 (HC-2) |
| 14 | Test cases | As in field 13 (unit, integration, security). The browser journeys are in M0-T04 (AT-M0-T04-10, -11) |
| 15 | Acceptance criteria | **AT-M0-T06-01** `GET /api/v1/me` without a cookie returns 401 `UNAUTHENTICATED`. **AT-M0-T06-02** Dev sign-in sets an httpOnly, `SameSite=Lax`, `Path=/` cookie, and `/me` returns a valid `principal.v1` for each fixture principal. The decoded cookie payload holds exactly `principalId`, `issuedAt` and `expiresAt`; a header, query parameter or body field naming a role, grant or scope does not change `/me` or the `authorize` result (ED-07 A: grants resolved on the backend on every request). **AT-M0-T06-03** A tampered or expired cookie gives 401 `UNAUTHENTICATED` (HTTP level; the browser assertion is AT-M0-T04-10, HC-2). **AT-M0-T06-04** With `AUTH_MODE` not `dev_fixture`, the dev routes return 404. **AT-M0-T06-05** Table-driven `authorize` cases: `p_no_grants` → `empty`/`no_grants`; central manager without a request → `allow`/`no_request_full_grant`; requesting `eastern` → `empty`/`requested_outside_grant`; requesting `central` → `allow`; portfolio admin requesting a region → `allow`; a REGIONS grant with a MALLS request → `empty`/`hierarchy_unresolved`. Every decision validates against `scope_decision.v1`. **AT-M0-T06-06** Hypothesis property: for random grants and requests, `effective` is never broader than the grants, `ALL` never appears unless granted, and the fingerprint is stable under key and array reordering. **AT-M0-T06-07** Sign-out returns 204, clears the cookie, and the next `/me` returns 401. |
| 16 | Failure and recovery scenarios | Unknown `principalId` at dev sign-in → 404 `NOT_AVAILABLE` (uniform). Fixture file invalid → startup refused with the validation error |
| 17 | Security requirements | Constant-time signature check; ≥ 32-byte secret; no session data in localStorage; `authorize` never widens; uniform refusals; dev routes unavailable outside dev, test and ci |
| 18 | Observability requirements | Logs `principalId` on authenticated requests; never the cookie value. `authorize` logs `outcome` and `scopeFingerprint` at debug level |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–07 pass in `ci/backend` and `ci/integration`; PR merged |

### M0-T07 — GitHub Actions workflows

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T07 |
| 2 | Requirement references | ADR-0015; DEVENV-R018–R031, R047–R051; ARCH-R101–R105; `specs/engineering/ci_checks.yaml`; ED-05 |
| 3 | Owning milestone | M0 |
| 4 | Objective | CI runs every job of `ci_checks.yaml` with stable names and path-aware triggering that never skips shared-contract consumers. One required check aggregates the results; images build without push; the gate and live-evaluation workflows exist |
| 5 | Scope and exclusions | **In:** `.github/workflows/ci.yml`, `milestone-gate.yml`, `eval-live.yml` (guarded skeleton that runs `make agent-test-live`, which reports `NOT_APPLICABLE` until M3); `.github/actions/setup/action.yml`; `scripts/ci/changes.py` (path classification from `ci_checks.yaml`, so there is no third-party filter action); `scripts/ci/summary.py` (skip rules and report assembly, using T11's report parsers). **Out:** repository settings (owner action, DEVENV §8.4) |
| 6 | Dependencies | M0-T01, M0-T03, M0-T10 (`specs-check`, `trace-report`), M0-T11 (report parsers). Jobs whose targets belong to later cards run and report `NOT_IMPLEMENTED` within the build window |
| 7 | Backend deliverables | N/A |
| 8 | Frontend deliverables | N/A |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | PostgreSQL service containers pinned to the same digest as Compose (DEVENV-R005) |
| 11 | Interfaces and contracts | `ci_checks.yaml` (jobs, needs, targets, timeouts, required checks, path categories, retention) |
| 12 | Implementation tasks | 1. Setup composite action with caches. 2. `ci.yml` jobs and `needs` per YAML; `workflow_call`. 3. `changes.py` with tests. 4. `summary.py` with tests. 5. `milestone-gate.yml` with round-trip, gate-mode checks and report artefact. 6. `eval-live.yml` with environment and guards. 7. SHA-pin every action; top-level `permissions: contents: read` |
| 13 | File and module ownership | `/.github/workflows/**`, `/.github/actions/**`, `/scripts/ci/**` except `/scripts/ci/reports.py` (M0-T11), `/tests/tooling/ci/**`. After this card merges, no other M0 card changes `/.github/workflows/**` (DEVENV-R054) |
| 14 | Test cases | `tests/tooling/ci/test_changes.py`, `test_summary.py`, `test_workflow_policy.py` |
| 15 | Acceptance criteria | **AT-M0-T07-01** Workflow job names equal `ci_checks.yaml`. **AT-M0-T07-02** On this card's own PR and on `main` after it merges, `ci/summary` concludes `success`. The summary lists targets of not-yet-merged M0 cards as `NOT_IMPLEMENTED` and M1+ targets as `NOT_APPLICABLE`, and `trace-report CARD=…` shows every AT of M0-T01, T03, T11 and T10 `PASSED` (EXC-001 compensating control). **AT-M0-T07-03** `changes.py` fixtures: a docs-only change selects only the always-run jobs; a change under `specs/**` selects every job; a frontend-only change does not select `ci/database`; a changed file matching no category selects every job; an uncomputable diff selects every job. **AT-M0-T07-04** `summary.py` fixtures, each yielding the stated outcome: **Fails:** a blocking job concluding `failure`, `cancelled`, `timed_out`, `neutral` or with no result; a job skipped while applicable; a disagreement between `ci/changes` and the summary's recomputed applicability; a failed `ci/changes`; a job of `ci_checks.yaml` missing from the run; a `FAILED` record in `status.jsonl`; `NOT_IMPLEMENTED` for a target whose `active_from` is earlier than `active_milestone`; a card branch whose `trace-report CARD=…` is not all `PASSED`. **Passes:** an allowed skip of a non-applicable job; `NOT_IMPLEMENTED` inside the build window. **Non-blocking:** `ci/echarts-gate` while `active_milestone` < M2. **AT-M0-T07-05** Policy lint: every action is SHA-pinned; default permissions are read-only; `ci.yml` references no secrets, sets `LLM_MODE=replay` for every job that declares `LLM_MODE` (ED-08 A), and uses `pull_request`, not `pull_request_target`. `scripts/ci/check_branch_name.py` accepts `feat/m0-t03-backend-skeleton` and `docs/m0-foundation-specs` and rejects `feature/foo`. **AT-M0-T07-06** `ci/images` builds both images and contains no registry login or push step. **AT-M0-T07-07** A `milestone-gate.yml` dispatch with `milestone=M0` on `main` uploads `tests/reports/gate/M0/report.md` (run once at the gate; *manual trigger*, result recorded). **AT-M0-T07-08** `eval-live.yml` refuses to run when the `live-eval` environment or the budget inputs are missing (guard script test) |
| 16 | Failure and recovery scenarios | Runner or network failure → re-run once (triage `ci-infrastructure`). Cache corruption → caches are keyed by lockfile hash and are disposable |
| 17 | Security requirements | No secrets in PR workflows; fork PRs have no credentials; live-eval secret only in the protected environment; SHA-pinned actions |
| 18 | Observability requirements | `ci-summary.md` per DEVENV-R031 (M0-applicable sections); artefacts per retention policy |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–06 and 08 pass; AT-07 recorded at the gate; PR merged |

### M0-T08 — ECharts 5.6.0 verification harness (GDQ-06)

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T08 |
| 2 | Requirement references | GDQ-06; DR-007; DXD-21, DXD-23, DXD-61; DBASE-R003, DBASE-R004; CA-01; OI-01, OI-03 |
| 3 | Owning milestone | M0 |
| 4 | Objective | The DX3 gallery self-test runs in CI on a local, version-pinned ECharts 5.6.0, and its result is recorded. It is informational in M0–M1 and becomes a blocking gate from M2 |
| 5 | Scope and exclusions | **In:** `echarts@5.6.0` (exact) in `packages/viz`; Playwright harness serving `docs/design/baseline/boards/` read-only; a route intercept mapping the cdnjs URL `…/echarts/5.6.0/echarts.min.js` to the locked local file; extraction of result rows; `tests/reports/echarts/result.json` and `result.txt`; `make echarts-gate`. **Out:** product charts (M2); fallback implementation (DXD-23, M2) |
| 6 | Dependencies | M0-T01, M0-T11 |
| 7 | Backend deliverables | N/A |
| 8 | Frontend deliverables | `packages/viz/package.json` dependency `echarts: 5.6.0`; `tests/e2e/echarts-gate/echarts-gate.spec.ts` |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | The DX3 gallery self-test output (rows of area, name, detail, status; summary counts); treemap thresholds (area CV ≤ 5 %, order ≥ 90 %, aspect ≤ 1.25 × reference) |
| 12 | Implementation tasks | 1. Add the pinned dependency. 2. Static server on the boards directory. 3. Route intercept. 4. Click "Run self-test", wait for the result, parse it. 5. Write the JSON and text output. 6. The `echarts-gate` recipe in `/Makefile` (composition point, DEVENV-R054). The `ci/echarts-gate` job already exists from M0-T07 |
| 13 | File and module ownership | `/packages/viz/package.json` (with `/pnpm-lock.yaml` per DEVENV-R052), `/tests/e2e/echarts-gate/**`. Composition point (DEVENV-R054): the `echarts-gate` recipe in `/Makefile` |
| 14 | Test cases | `tests/e2e/echarts-gate/echarts-gate.spec.ts` |
| 15 | Acceptance criteria | **AT-M0-T08-01** The page reports `echarts.version === "5.6.0"`, loaded from the local lockfile copy; no request leaves for cdnjs or any other host. **AT-M0-T08-02** The self-test completes, and `result.json` contains every row, the pass/fail/n.a. counts and the treemap metrics. **AT-M0-T08-03** The harness fails if the board shows "Test double, not ECharts" or "ECharts did not load". **AT-M0-T08-04** The board files' SHA-256 values are unchanged after the run. **AT-M0-T08-05** (*manual record*) The result is summarized in STATUS.md § Verification gates. If any chart fails its threshold, the DXD-23 fallback decision for that chart is listed for PR-M2 |
| 16 | Failure and recovery scenarios | A failing chart does not fail M0. It is recorded and carried to PR-M2 (ADR-0011). A harness failure (board not loading) does fail `echarts-gate` |
| 17 | Security requirements | No network egress during the test; the board is served read-only from the repository |
| 18 | Observability requirements | `result.json` uploaded as an artefact every run (`artifacts_always`) |
| 19 | Delivery class | slice (the slice's day-1 mandatory gate runs this harness) |
| 20 | Completion gate | ATs 01–04 pass in `ci/echarts-gate`; AT-05 recorded; PR merged |

### M0-T09 — AG-UI 1.0 verification spike (throwaway)

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T09 |
| 2 | Requirement references | GDQ-11; DR-016, DR-017; DXD-40; ARCH-R075, R076; ED-10 (Proposed); CA-02, CA-03, CA-04; OI-12; ROADMAP A-13 |
| 3 | Owning milestone | M0 |
| 4 | Objective | Verify the DX4-AGUI assumptions A1–A8 and the 1.0 questions A9–A14 (plus latency sample L1) against the AG-UI 1.0 SDKs, so PR-M4 is written from verified facts |
| 5 | Scope and exclusions | **In:** throwaway minimal FastAPI SSE agent using `ag-ui-protocol` 1.0.x; minimal TS client using `@ag-ui/client` 1.x behind a Next.js rewrite; scripted events covering every item; the report `docs/architecture/spikes/AGUI_SPIKE_REPORT.md`. **Out:** any merge of spike code; any AG-UI dependency in the product workspace |
| 6 | Dependencies | M0-T01. GDQ-12 configuration is optional (L1 only) |
| 7 | Backend deliverables | Spike only, on branch `spike/m0-t09-agui-spike` (never merged) |
| 8 | Frontend deliverables | Spike only |
| 9 | Agent deliverables | Spike only; L1 uses one minimal provider call when configured |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | DX4-AGUI board (event → state table, run identity, idempotency); ARCHITECTURE §8.4 report structure |
| 12 | Implementation tasks | 1. Spike server emitting each event type with `seq` in `metadata`. 2. Client reducer printing received events. 3. Scenarios: normal run; stream drop and replay; Stop and cancel; frontend-tool interrupt; clarification as an `input_required` interrupt; 64 KB CUSTOM payload; protocol-version negotiation; zod peer check; SSE through the Next.js rewrite with timing. 4. Write the report with evidence excerpts. 5. Open a docs PR with the report only |
| 13 | File and module ownership | Spike branch: any path. Main: `/docs/architecture/spikes/AGUI_SPIKE_REPORT.md` only |
| 14 | Test cases | The spike's scripted scenarios (evidence in the report); `tests/tooling/test_no_agui_dependency.py` on `main` |
| 15 | Acceptance criteria | **AT-M0-T09-01** (*manual review*) The report has a result row with evidence for every item A1–A14 and L1. **AT-M0-T09-02** (*manual review*) It records the exact SDK versions tested and the protocol version negotiated. **AT-M0-T09-03** (*manual review*) It gives a recommendation on ED-10, a recommended mapping for every deviation from DX4-AGUI, and the open risks for PR-M4. **AT-M0-T09-04** On `main`, neither `uv.lock` nor `pnpm-lock.yaml` contains an `ag-ui` package, and the spike branch is not merged |
| 16 | Failure and recovery scenarios | A failed item is reported with a proposed mapping; it does not fail M0 (ARCH-R076). An SDK that cannot be installed → reported, with the ED-10 Option B evaluation |
| 17 | Security requirements | Live key only from the developer's `.env`; never committed; never in the report |
| 18 | Observability requirements | Recorded event streams (JSONL excerpts) in the report as evidence |
| 19 | Delivery class | full (pre-slice evidence for PR-M4) |
| 20 | Completion gate | The report is merged through a docs PR and reviewed by the owner; AT-04 passes |

### M0-T10 — Governance automation: templates, specs-check, trace report, renderers

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T10 |
| 2 | Requirement references | ADR-0001, ADR-0002; ARCH-R094, R095, R101–R105; DEVENV-R011, R013, R035, R046; RMAP-R007, R010; DREG-R001, R002; DBASE-R001 |
| 3 | Owning milestone | M0 |
| 4 | Objective | Specifications, IDs, frozen references and the Make and CI contracts are machine-checked. PRs and defects follow templates. Rendered tables cannot drift |
| 5 | Scope and exclusions | **In:** `.github/pull_request_template.md` (exactly the 15 sections of DEVENV-R035); `.github/ISSUE_TEMPLATE/defect.yml` (`DEF-` title, the 9 triage classes, a `blocking` checkbox); `scripts/specs/check.py` (every check listed under `specs-check` in `make_targets.yaml`); `scripts/trace/report.py`; `scripts/docs/render_register.py` and `render_engineering_tables.py`, which reproduce the PR-M0 renders exactly; verification that `.cursor/rules/*.mdc` and `AGENTS.md` exist and cite valid IDs. **Out:** changes to the content of specifications |
| 6 | Dependencies | M0-T01, M0-T11 (JUnit annotations consumed by `trace-report`) |
| 7 | Backend deliverables | Python scripts under `scripts/` (typed, tested) |
| 8 | Frontend deliverables | N/A |
| 9 | Agent deliverables | N/A |
| 10 | Database and data requirements | N/A |
| 11 | Interfaces and contracts | `specs/engineering/*`; `specs/traceability/id_conventions.yaml`; `docs/handoff/SHA256SUMS`; the task-card format of this plan (§4 heading and 20-row table) |
| 12 | Implementation tasks | 1. Templates. 2. `specs-check` sub-checks, each with a negative fixture. 3. `trace-report`. 4. Renderers and drift checks. 5. Make target wiring |
| 13 | File and module ownership | `/.github/pull_request_template.md`, `/.github/ISSUE_TEMPLATE/**`, `/scripts/specs/**`, `/scripts/trace/**`, `/scripts/docs/**`, `/tests/tooling/specs_check/**`, `/tests/tooling/trace/**`, `/tests/tooling/test_renderers.py`. Composition point (DEVENV-R054): the `specs-check`, `trace-report` and renderer recipes in `/Makefile` |
| 14 | Test cases | `tests/tooling/specs_check/test_*.py` (one per sub-check, positive and negative); `tests/tooling/trace/test_report.py`; `tests/tooling/test_renderers.py` |
| 15 | Acceptance criteria | **AT-M0-T10-01** `make specs-check` passes on `main`, and each sub-check fails on its negative fixture. **AT-M0-T10-02** A modified copy of a frozen reference file is detected by the SHA-256 check. **AT-M0-T10-03** The rendered tables in DEVELOPMENT_ENVIRONMENT §5.2, §7.2 and DECISION_REGISTER §2 equal the renderer output byte for byte. **AT-M0-T10-04** `trace-report` cases: an unknown ID fails in every mode; an AT ID with no executed test is reported `NOT_IMPLEMENTED`; a skipped test is reported `SKIPPED`; with `CARD=M0-T03`, any of that card's ATs not `PASSED` fails; with `GATE=M0`, any AT of M0 not `PASSED` fails; `trace.json` and `trace.md` are produced. **AT-M0-T10-05** The PR template has exactly the 15 headings, and the defect template offers exactly the 9 triage classes. **AT-M0-T10-06** Every card in `plans/M*_*.md` has rows 1–20 and one delivery class; a negative fixture with a missing row fails. **AT-M0-T10-07** The banned-term lint flags "overdue" in a negative fixture under `tests/fixtures` and ignores `specs/engineering/` |
| 16 | Failure and recovery scenarios | A check that crashes reports exit 1 with the check name; it never silently passes |
| 17 | Security requirements | Scripts read the repository only; no network |
| 18 | Observability requirements | Findings are printed as `file:line: CODE message` and summarized in `ci-summary.md` |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–07 pass in `ci/specs`; PR merged |

### M0-T11 — Test harness, traceability markers and CI reporting

| # | Field | Content |
|---|---|---|
| 1 | Feature ID | M0-T11 |
| 2 | Requirement references | ARCH-R083–R091, R094, R096, R098, R101, R102, R104; DEVENV-R023, R031; ROADMAP A-04, A-20 |
| 3 | Owning milestone | M0 |
| 4 | Objective | Every test framework is configured once: deterministic, isolated, traceable to AT IDs, and producing the reports CI and the gates consume |
| 5 | Scope and exclusions | **In:** root and backend `pytest` configuration (strict markers: `unit`, `integration`, `db`, `contract`, `security`, `agent_mock`, `agent_replay`, `agent_live`, `slow`, `trace`, `quarantine`); a `trace` marker plugin writing AT and requirement IDs into JUnit properties; `pytest-socket` blocking non-local network; a derandomized Hypothesis CI profile; `TZ=UTC`; per-worker test databases; Vitest configuration with a JUnit reporter and `[AT-…]` title parsing; Playwright configuration (projects `desktop` 1440 × 900, `tablet` 1024 × 768, `phone` 390 × 844; trace, screenshot and video on failure; network log capture; `X-Request-Ref` extraction; axe helper); quarantine marker plus `scripts/lint/quarantine_expiry.py`; report parsers used by `scripts/ci/summary.py`; READMEs in `tests/`. **Out:** product tests (owned by each card) |
| 6 | Dependencies | M0-T01, M0-T03 |
| 7 | Backend deliverables | `backend/pyproject.toml` `[tool.pytest.ini_options]`; `backend/tests/conftest.py`; `tests/conftest.py`; `scripts/testing/pytest_trace.py` |
| 8 | Frontend deliverables | `apps/web/vitest.config.ts`; `playwright.config.ts`; `tests/e2e/support/{axe.ts,network.ts,trace.ts}` |
| 9 | Agent deliverables | N/A (markers reserved for M3) |
| 10 | Database and data requirements | N/A here. The per-worker test-database fixtures need the database engines and guards, so they are delivered by M0-T02 as `backend/tests/fixtures/db.py`; M0-T02 adds its registration to this card's `backend/tests/conftest.py` (composition point, DEVENV-R054) |
| 11 | Interfaces and contracts | `specs/traceability/id_conventions.yaml`; JUnit XML; `tests/reports/**` layout |
| 12 | Implementation tasks | 1. Pytest configuration and plugins. 2. Database fixtures. 3. Vitest configuration. 4. Playwright configuration and support. 5. Quarantine marker and expiry lint. 6. Report parsers. 7. READMEs |
| 13 | File and module ownership | `/backend/tests/conftest.py`, `/tests/conftest.py`, `/tests/README.md`, `/tests/e2e/support/**`, `/playwright.config.ts`, `/apps/web/vitest.config.ts`, `/scripts/testing/**`, `/scripts/lint/quarantine_expiry.py`, `/scripts/ci/reports.py`, `/tests/tooling/harness/**`; in `/backend/pyproject.toml` (owned by M0-T01), the `[tool.pytest.ini_options]` section only (DEVENV-R054) |
| 14 | Test cases | `tests/tooling/harness/test_trace_marker.py`, `test_quarantine.py`, `test_network_block.py`, `test_reports.py`; `tests/e2e/support/axe.spec.ts` |
| 15 | Acceptance criteria | **AT-M0-T11-01** `@pytest.mark.trace("AT-…", reqs=[…])` writes the IDs into JUnit properties; an unregistered marker fails collection. **AT-M0-T11-02** Vitest and Playwright titles starting `[AT-M0-…]` appear with that ID in JUnit. **AT-M0-T11-03** A quarantine marker without `defect` or `expires` fails collection; an expired quarantine makes `quarantine_expiry.py` exit 1. **AT-M0-T11-04** A deliberately failing Playwright fixture test leaves a trace, screenshot and network log, and its `requestRef`s are extracted. **AT-M0-T11-05** The axe helper fails on a fixture page with a serious violation. **AT-M0-T11-06** `ci-summary.md` built from fixture reports contains every M0-applicable section of DEVENV-R031, including "Dataset: not seeded". **AT-M0-T11-07** A unit test attempting an outbound connection to a non-local host fails (`pytest-socket`), and CI runs with `TZ=UTC` and the derandomized Hypothesis profile. **AT-M0-T11-08** Report parsers map JUnit pass, failure, error and skipped to `PASSED`, `FAILED`, `FAILED` and `SKIPPED`, and read `status.jsonl`. A `pytest.skip` inside an acceptance test is reported `SKIPPED`, never `PASSED`. An unparseable or missing expected report is `FAILED` |
| 16 | Failure and recovery scenarios | A worker database left behind is dropped at session start (only names matching `cenomi_test_gw*`, under guard DG-2) |
| 17 | Security requirements | Reports never include environment values or secrets; network blocked in unit tests |
| 18 | Observability requirements | JUnit for every suite; artefacts per DEVENV-R029 |
| 19 | Delivery class | slice |
| 20 | Completion gate | ATs 01–08 pass in `ci/backend`, `ci/frontend`, `ci/e2e`; PR merged |

---

## 5. M0 test and acceptance plan

| Area (ARCHITECTURE §10.2) | M0 coverage | Cards |
|---|---|---|
| A Backend | Settings, errors, envelope, request refs, health, dataset, session, AccessScope (unit, integration, property) | T03, T05, T06 |
| B Database | Fresh migration, grants, default privileges, pool settings, guards, drift | T02 |
| C Frontend | Client parsing, state reset, boundaries, build, headers, axe | T04 |
| D Playwright | E2E-SHELL-01…03, E2E-NAV-01, E2E-RESP-01…03 (all in M0-T04 since HC-2) | T04 |
| E–I | Not applicable in M0 (UG applicability, ROADMAP §7.2) | — |
| Tooling | Make contract, CI classifier and summary, specs-check, trace-report, renderers, harness | T01, T07, T10, T11 |
| Verification gates | ECharts run (CA-01); AG-UI spike (CA-02 to CA-04) | T08, T09 |

All 85 acceptance tests are listed in the cards: AT-M0-T01-01 … AT-M0-T11-08 (83 before the HC-2 and HC-3 corrections; the assertion map is in ROADMAP A-27). Manual ones are AT-M0-T07-07, AT-M0-T08-05 and AT-M0-T09-01 to 03; their results are recorded in the gate report.

---

## 6. Exit gate (GATE-M0)

Run with `milestone-gate.yml` (`milestone=M0`) on the merged `main` commit. Every check cites the universal criteria it satisfies (ROADMAP §7.1). Universal criteria not applicable to M0 are UG-05, UG-08, UG-11 and UG-12 (ROADMAP §7.2).

| Check | Requirement | UG |
|---|---|---|
| GATE-M0-01 | Clean-clone reproducibility: on a fresh runner, `make setup` then `make up` serves the shell at :3000 with the synthetic banner, and `/api/v1/health` is `ok` | UG-01, UG-03, UG-04 |
| GATE-M0-02 | `make check` green; CI green on `main` for the gate commit, including the shell Playwright journeys | UG-03, UG-04, UG-06 |
| GATE-M0-03 | Module boundaries enforced (backend and web) with negative tests (AT-M0-T03-04, AT-M0-T04-05) | UG-02 |
| GATE-M0-04 | CF-0 contracts: Pydantic equals schema; codegen idempotent; drift detection proven (AT-M0-T05-01…06) | UG-02 |
| GATE-M0-05 | `make specs-check GATE=M0` passes: frozen-reference hashes, ID conventions, Make and CI parity, card structure; every M0 target reports `PASSED` (none `NOT_IMPLEMENTED`); `report.json` validates against `gateReport` | UG-15, UG-17 |
| GATE-M0-06 | CI baseline: all jobs present with stable names; `ci/summary` semantics proven (AT-M0-T07-01…06) | UG-18 |
| GATE-M0-07 | Compatibility assumptions recorded: CA-01 (ECharts result in STATUS), CA-02 to CA-04 (spike report reviewed), CA-05, CA-06 | UG-12 (recording only), UG-15 |
| GATE-M0-08 | Database roles and grants (AT-M0-T02-02…06) and deny-by-default AccessScope (AT-M0-T06-05, -06) | UG-07, UG-09 |
| GATE-M0-09 | ADR-0001 to ADR-0006 and ADR-0015 to ADR-0018 Accepted; DECISION_REGISTER current; STATUS reflects the actual state | UG-15, UG-16 |
| GATE-M0-10 | Repository protection stages P1 and P2 (DEVENV §8.4) are in force, and P1 was in force before the first card PR merged. Every merge outside the rules is covered by an owner-approved `EXC-nnn` in STATUS.md (EXC-001 expired when P2 took effect). The EXC-001 log is complete (PR numbers, merge SHAs, local validations, compensating controls; conditions C1–C3), and its retroactive GitHub Actions verification succeeded (condition C5: the M0-T07 PR run and the first `ci/summary` run on `main` after M0-T07; condition C6). An unrecorded deviation, or a missing or failed retroactive verification, fails this check | UG-10 |
| GATE-M0-11 | `make security-check` green: gitleaks over the full history, audits and licences | UG-10 |
| GATE-M0-12 | Observability: JSON logs with `requestRef` and `traceId`; redaction test (AT-M0-T03-07, -10) | UG-13 |
| GATE-M0-13 | `make trace-report GATE=M0`: every automated AT-M0 ID is `PASSED` (none `NOT_IMPLEMENTED`, `SKIPPED` or quarantined), and each manual AT has a recorded result | UG-01, UG-17 |
| GATE-M0-14 | The verification report (`report.json` per RMAP-R010) records: merged commit SHA; approved spec-set version and its PR; dataset `not_seeded`; fixture-set hash; `ci/summary` and every job's conclusion; per-suite results (backend unit and integration, frontend, integration, Playwright E2E; agent mock and replay `NOT_APPLICABLE` under the milestone rule); defects (no open `blocking`); approved exceptions (EXC-001); deferred items. The owner approves it | UG-14, UG-18, UG-19, UG-20 |

---

## 7. Five-day slice classification for M0

| Class | Cards |
|---|---|
| slice | M0-T01, M0-T02, M0-T03, M0-T04, M0-T05, M0-T06, M0-T07, M0-T08, M0-T10, M0-T11 |
| full | M0-T09 (pre-slice evidence for PR-M4) |
| deferred | None |

Under ED-06 A these are built before slice day 1. The slice's day-1 GDQ-06 gate is the M0-T08 harness run.

---

## 8. Conditions for authorizing M0 implementation

The owner's explicit authorization to begin M0 implementation is needed after **all** of the following hold:

1. PR-M0 (this specification set) is approved and merged, and CF-0 is recorded as frozen in STATUS.md.
2. ✅ **ED-07** (sign-in), **ED-08** (model determinism in tests) and **ED-09** (styling) are decided and recorded in ADRs: Option A for all three, approved 2026-10-22 (ADR-0016, ADR-0017, ADR-0018). These are the three decisions the ESP marks "needed before M0 build".
3. Repository protection stage **P1** is in force (DEVENV §8.4; policy approved 2026-10-22, **application pending**), and **EXC-001** is approved for the four bootstrap cards (✅ approved conditionally 2026-10-22, conditions C1–C7). Stage P2 must then be enabled as soon as M0-T07 merges.
4. Composer is pointed at `AGENTS.md` and `.cursor/rules/`, and works one card per branch (DEVENV-R032).

**Not required to start M0** (each has a later deadline):

| Item | When it is needed |
|---|---|
| ED-10 | PR-M4 |
| ED-11 / DR-036 | PR-M5 |
| GDQ-12 configuration | Slice day 3 (only L1 of the spike uses it) |
| Repository protection stage P2 | Immediately after M0-T07 merges (verified at GATE-M0-10) |

---

## 9. Risks specific to M0

| Risk | Mitigation |
|---|---|
| Next.js rewrites buffer SSE (CA-04) | Spike item A14. If confirmed, PR-M4 specifies a route handler that streams instead of a rewrite |
| In-repo zod generator gaps (CA-05) | The restricted schema subset plus the equivalence tests in AT-M0-T05-06 |
| GitHub service containers cannot run the init hook | Roles are created by `make db-init` in both Compose and CI (ADR-0006 §3) |
| AG-UI 1.0 field stripping (A10) breaks the DX4 `seq` assumption | Spike evidence; PR-M4 maps `seq` into `metadata` |
| Scope creep in shell work | Placeholders only; dashboards are M2 cards |
