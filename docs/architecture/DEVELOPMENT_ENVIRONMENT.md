# DEVELOPMENT_ENVIRONMENT — toolchain, Makefile, Compose, CI and delivery workflow

| | |
|---|---|
| Document code | DEVENV (requirement IDs `DEVENV-Rnnn`) |
| Version | 1.1 · 2026-10-23 · M0 corrections PR (HC-3 Compose note; HC-4 DEVENV-R052; HC-5 §8.6, DEVENV-R053–R055; DEVENV-R055 lockfile serialization and DEVENV-R056 protection verification, owner clarifications of 2026-10-23); 1.2 · HC-6 (DEVENV-R054 `pyproject` sections for M0-T03), HC-7 (Makefile row) and DEVENV-R001 wording; 1.3 · CR-001 (`backend-test SUITE=tooling` in `ci/specs`; `import-linter lint`), tables re-rendered; 1.4 · CR-002 (security-patch exceptions for `certifi` and `handlebars`, ADR-0003 §2) and EXC-002 (§8.4); 1.5 · 2026-10-25 · CR-004 (`API_MAX_BODY_BYTES` in §4; M0-T06 `.env.example` line in DEVENV-R054); 1.6 · 2026-10-25 · CR-005 (DEVENV-R054 `ci.yml` exceptions for M0-T05 and M0-T08). 1.0 merged in PR-M0 (`4515031`) |
| Status | Normative since PR-M0 merged (`4515031`); version 1.1 amendments in review |
| Rests on | DR-027, DR-037, ED-01, ED-05, ED-06 (approved); ED-07, ED-08, ED-09 (approved 2026-10-22; ADR-0016, ADR-0017, ADR-0018); ADR-0003, ADR-0004, ADR-0006, ADR-0015 |
| Machine-readable sources | `specs/engineering/make_targets.yaml`, `specs/engineering/ci_checks.yaml`, `specs/engineering/spec_set.yaml` — the YAML wins on any conflict with this prose |

**Goal.** A clean clone becomes a running, verified stack with `make setup` then `make up`. Local machines and CI run the same Make targets with the same pinned toolchain, so a green `make check` and `make ci` locally predict a green pull request.

---

## 1. Scope

This document covers:
- prerequisites;
- dependency installation and locking;
- environment configuration;
- the root Makefile contract;
- Docker Compose;
- GitHub Actions CI;
- branch, pull-request and merge policy;
- repository settings;
- CI reporting;
- failure triage;
- the daily development loop.

It does not cover:

| Topic | Where it is covered |
|---|---|
| Module boundaries, database ownership, testing architecture | ARCHITECTURE |
| Business tables | DATABASE_SCHEMA |
| Agent budget values | AGENT_ARCHITECTURE |

---

## 2. Prerequisites

| Tool | Version | Why |
|---|---|---|
| Docker Engine with Compose v2 | Current stable | Runs `db`, `api`, `web`, `migrate`, `seed` |
| GNU Make | ≥ 4 | Single entry point |
| uv | Pinned in `backend/pyproject.toml` `[tool.uv] required-version` | Python toolchain and lockfile |
| Python | 3.12.x (`.python-version`; uv installs it) | DR-027 |
| Node.js | 22.x LTS (`.nvmrc`; `engines.node` `>=22 <23`) | DR-027; Next.js 16 requires ≥ 20.9 |
| pnpm | Exact version in root `package.json` `packageManager`, activated by Corepack | DR-027 |
| gitleaks | Pinned version documented in `scripts/tools.lock` | Secret scan (`security-check`) |

**DEVENV-R001** `make doctor` checks the toolchain and exits 3 on any mismatch. The checks are those of `specs/engineering/make_targets.yaml`, target `doctor`, which wins on any difference. The M0-T01 implementation also verifies the gitleaks version pinned in `scripts/tools.lock` and the exact uv version.

---

## 3. Dependencies, locking and reproducibility

| # | Rule |
|---|---|
| **DEVENV-R002** | **Python.** One uv workspace rooted at `backend/`; `pyproject.toml` with `requires-python = "==3.12.*"`. Runtime and development groups are separate. `uv.lock` is committed. Installs always use `uv sync --locked`. CI also runs `uv lock --check`. Adding or upgrading a dependency is a PR that changes `pyproject.toml` and `uv.lock` together and states why |
| **DEVENV-R003** | **Node.** One pnpm workspace (`pnpm-workspace.yaml`: `apps/*`, `packages/*`). `pnpm-lock.yaml` is committed. Installs always use `pnpm install --frozen-lockfile`. The pnpm version is fixed by `packageManager` and Corepack. `.npmrc` sets `engine-strict=true` |
| **DEVENV-R004** | **Pin policy** (ADR-0003 §2). At the M0 scaffold, take the newest release ≥ 14 days old within the approved line. ECharts is exactly `5.6.0`. AG-UI is not added to the product workspace until ED-10 is decided (the spike uses its own throwaway lockfile). Later upgrades go through a CR, except security patches |
| **DEVENV-R005** | **Containers.** Base images are pinned by minor tag **and** digest: `python:3.12-slim@sha256:…`, `node:22-bookworm-slim@sha256:…`, `postgres:16.<minor>@sha256:…`. The same `postgres` digest is used by Compose and the CI service container |
| **DEVENV-R006** | **GitHub Actions** are pinned by full commit SHA, with the release tag in a trailing comment. Runners use the label `ubuntu-24.04` |
| **DEVENV-R007** | **Playwright browsers** are installed by `make install BROWSERS=1` at the version implied by the locked `@playwright/test`. CI caches them by that version |
| **DEVENV-R008** | **Local and CI parity.** CI jobs call only Make targets, plus the few `extra_steps` in `ci_checks.yaml`. No job contains a test command that a developer cannot run with `make ci JOB=<job>` |
| **DEVENV-R052** | **Lockfile and manifest updates by feature cards** (HC-4, approved 2026-10-23). A card whose approved scope introduces or changes a dependency may update the applicable manifest and lockfile even when its field 13 does not list them. A dependency qualifies if the card names it, or if ADR-0003 fixes it for a deliverable the card names. Files: dependency entries in `backend/pyproject.toml` with `backend/uv.lock`; the `package.json` of the package the card delivers, with the root `pnpm-lock.yaml`. Conditions: (a) lockfiles are regenerated by the package manager (`uv add` or `uv lock`; `pnpm add` or `pnpm install`), never edited or merged by hand; on a conflict, rebase onto `main` and regenerate; (b) versions follow DEVENV-R004 and the ADR-0003 pins; (c) the PR lists each added or changed dependency, why it is needed and its licence (DEVENV-R002; `make security-check` licence audit); (d) installation stays reproducible: `make install` on a clean clone leaves `git status` clean, and the `ci/static` lockfile validation (`uv lock --check`, frozen pnpm install) passes; (e) no other dependency is added, removed or upgraded as a side effect |

---

## 4. Environment configuration

**DEVENV-R009** `.env.example` lists every variable below, with a safe development default or an empty value. `make setup` copies it to `.env` when `.env` does not exist. `.env` is git-ignored. Real secrets live only in the developer's `.env` and in GitHub Actions secrets. The `.env.example` placeholders are recognisably fake (`change-me-dev-only-…`) and allow-listed for gitleaks by exact path.

| Group | Variable | Default in `.env.example` | Required when | Secret | Read by | From |
|---|---|---|---|---|---|---|
| Runtime | `CENOMI_ENV` | `dev` | Always; one of `dev`, `test`, `ci` | no | api, CLI, guards | M0 |
| Database | `DATABASE_URL_ADMIN` | `postgresql://postgres:change-me-dev-only-admin@localhost:5432/postgres` | `db-init`, `seed-reset` | yes | CLI only | M0 |
| Database | `DATABASE_URL_OWNER` | `postgresql://cenomi_owner:change-me-dev-only-owner@localhost:5432/cenomi_dev` | Migrations | yes | migrate | M0 |
| Database | `DATABASE_URL_SEED` | `postgresql://cenomi_seed:change-me-dev-only-seed@localhost:5432/cenomi_dev` | Seeding, verify | yes | seed, tests | M0 (role), M1 (use) |
| Database | `DATABASE_URL_READER` | `postgresql://cenomi_reader:change-me-dev-only-reader@localhost:5432/cenomi_dev` | api | yes | api | M0 |
| Database | `DATABASE_URL_APP` | `postgresql://cenomi_app:change-me-dev-only-app@localhost:5432/cenomi_dev` | api | yes | api | M0 |
| Database | `DB_READER_POOL_SIZE` / `DB_APP_POOL_SIZE` | `10` / `5` | — | no | api | M0 |
| Database | `DB_READER_STATEMENT_TIMEOUT_MS` | `5000` | — | no | api | M0 |
| Dataset | `CENOMI_DATASET_ID` | `sd-2026.10.20-01` | Always | no | api, seed | M0 |
| Dataset | `CENOMI_AS_OF` | `2026-10-20` | Always | no | api, seed | M0 |
| Dataset | `CENOMI_TZ` | `Asia/Riyadh` | Always | no | api, seed | M0 |
| Dataset | `CENOMI_SEED` | Value fixed in SYNTHETIC_DATA_STRATEGY (PR-M1) | Seeding | no | seed | M1 |
| Auth | `AUTH_MODE` | `dev_fixture` (ED-07 A, approved; ADR-0016) | Always | no | api | M0 |
| Auth | `SESSION_SECRET` | Empty (`make setup` generates 48 random bytes into `.env`) | Always; ≥ 32 bytes | yes | api | M0 |
| Auth | `SESSION_TTL_MINUTES` | `480` | — | no | api | M0 |
| API | `API_MAX_BODY_BYTES` | `1048576` (1 MiB; minimum 1024) | — | no | api | M0 (M0-T06, CR-004) |
| Model | `LLM_MODE` | `off` (M0–M2), then `replay` | Always; `off`, `replay` or `live` | no | api, harness | M0 (`off`), M3 |
| Model | `LLM_PROVIDER`, `LLM_PRIMARY_MODEL`, `LLM_FALLBACK_MODEL` | Empty (GDQ-12) | `LLM_MODE=live` | no | api, harness | M3 |
| Model | `LLM_API_KEY` | Empty | `LLM_MODE=live` | yes | api | M3 |
| Model | `LLM_REPLAY_DIR` | `tests/fixtures/llm-replay` | `LLM_MODE=replay` | no | api, harness | M3 (ED-08) |
| Agent | `AGENT_MAX_STEPS`, `AGENT_MAX_SECONDS`, `AGENT_MAX_TOKENS` | Values fixed in AGENT_ARCHITECTURE (PR-M3) | M3+ | no | api | M3 |
| Live eval | `LIVE_EVAL_LLM_API_KEY`, `LIVE_EVAL_MAX_CASES`, `LIVE_EVAL_MAX_TOKENS`, `LIVE_EVAL_MAX_COST_USD` | Empty | `agent-test-live` | key: yes | harness | M3 |
| Telemetry | `OTEL_EXPORTER` | `console` (CI: `none`) | — | no | api | M0 |
| Telemetry | `OTEL_EXPORTER_OTLP_ENDPOINT` | Empty | `OTEL_EXPORTER=otlp` | no | api | M0 |
| Telemetry | `LOG_LEVEL` | `INFO` | — | no | api, CLI | M0 |
| Web | `API_INTERNAL_URL` | `http://api:8000` (Compose), `http://localhost:8000` (host) | Always | no | web (server side) | M0 |

**DEVENV-R010** The Make variable `DB=dev|test` selects the database. The CLI replaces the database name in the role URLs with `cenomi_<DB>`, so one `.env` serves both. Guards DG-1 to DG-5 (ARCH-R064) are applied to the resulting URL.

---

## 5. Makefile contract

### 5.1 Conventions

| # | Rule |
|---|---|
| **DEVENV-R011** | The root `Makefile` is the only supported developer and CI interface. Its targets, arguments, prerequisites, behaviour, failure codes and safety rules are exactly those of `specs/engineering/make_targets.yaml`. `make help` prints the targets in that file's order, and `make specs-check` fails if they differ |
| **DEVENV-R012** | Exit codes: `0` success; `1` check or test failure; `2` refused by a guard or bad arguments; `3` missing prerequisite |
| **DEVENV-R013** | **Result reporting.** Every target reports exactly one result in the ARCHITECTURE §10.8 vocabulary and appends it to `tests/reports/status.jsonl`. **A target whose `active_from` is later than `active_milestone` reports `NOT_APPLICABLE`** (milestone rule) and exits 0. **A target that is due but still a stub reports `NOT_IMPLEMENTED`**; it exits 0 only inside the build window of ARCH-R103 and 1 otherwise. Neither result ever satisfies an acceptance test, and `ci/summary` lists both. In gate mode (`GATE=M<n>`), every target with `active_from ≤ M<n>` must report `PASSED` |
| **DEVENV-R014** | **Safety.** `check` is non-destructive and needs no database. `ci` may recreate only `cenomi_test`. `db-downgrade`, `seed-reset` and `down VOLUMES=1` are destructive: they call the guards of ARCH-R064 and require `CONFIRM=yes` or interactive confirmation. `db-downgrade` and `agent-test-live` are never run by `check` or `ci` |
| **DEVENV-R015** | Targets contain orchestration only (calls to `uv run cenomi …`, `uv run pytest …`, `pnpm …`, `docker compose …`, or scripts in `scripts/`). Logic lives in code that has tests |

### 5.2 Target reference

Rendered from `specs/engineering/make_targets.yaml`. The YAML wins on conflict. M0-T10 adds the renderer and a drift check.

<!-- BEGIN GENERATED: make_targets (source: specs/engineering/make_targets.yaml) -->
**Environment and development**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `help` | M0 | no | List every target with its one-line summary, grouped as in this file. | — | Never fails. | no | — |
| `doctor` | M0 | no | Verify the local toolchain and configuration against the pinned versions. | — | Exit 3 naming each mismatch. | no | `ci/static` |
| `setup` | M0 | no | First-time setup — doctor, create .env from .env.example if absent, install dependencies. | — | Stops at the first failing step. | no | — |
| `install` | M0 | no | Install locked dependencies for backend and web (no lockfile changes). | `BROWSERS` (1) | Exit 1 if a lockfile is out of date with its manifest; never rewrites a lockfile. | no | `all` |
| `up` | M0 | no | Build and start db, api and web; bootstrap roles and migrate the dev database; wait until healthy. | — | Exit 1 with the failing service's last 50 log lines. | no | `ci/e2e` |
| `down` | M0 | no | Stop the stack. Data volumes are kept unless VOLUMES=1 CONFIRM=yes. | `VOLUMES` (0); `CONFIRM` (—) | Exit 2 if VOLUMES=1 without CONFIRM=yes. | no | `ci/e2e` |
| `logs` | M0 | no | Follow container logs (JSON lines for api). | `SERVICE` (—); `FOLLOW` (1) | Exit 3 if the stack is not running. | no | `ci/e2e` |
| `clean` | M0 | no | Remove local build outputs and caches. Never removes dependencies, data volumes, .env or committed files. | — | Never fails on missing paths. | no | — |

**Database**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `db-init` | M0 | no | Create the four roles and the cenomi_dev / cenomi_test databases if missing (idempotent). *Safety:* Guards DG-1, DG-3, DG-5. Never run against a non-local host. | `DB` (dev) | Exit 2 if guards DG-1, DG-3 or DG-5 fail (ARCH-R064); exit 3 if the server is unreachable. | no | `ci/backend`, `ci/database`, `ci/integration`, `ci/e2e` |
| `db-upgrade` | M0 | no | Apply Alembic migrations to head as cenomi_owner. *Safety:* Guards DG-1, DG-2, DG-3. Non-destructive by rule (ARCH-R061); a revision that drops data must be called out in its PR. | `DB` (dev) | Exit 1 on any migration error; the transaction of the failing revision is rolled back. | no | `ci/backend`, `ci/database`, `ci/integration`, `ci/e2e` |
| `db-current` | M0 | no | Print the current Alembic revision and whether it is head. | `DB` (dev) | Exit 1 if not at head. | no | `ci/database` |
| `db-check` | M0 | no | Detect drift between tables.py metadata and the migrated database (alembic check) and verify roles and grants. | `DB` (test) | Exit 1 on drift or a grant mismatch. | no | `ci/database` |
| `db-history` | M0 | no | Print the migration history. | — | Never fails unless Alembic configuration is broken (exit 1). | no | — |
| `db-downgrade` | M0 | **yes** | Downgrade to a named revision. Never run by `make check` or `make ci`. *Safety:* Guards DG-1 to DG-5. Used by milestone-gate.yml on an ephemeral database only (ARCH-R060). | `REV` (—); `DB` (dev); `CONFIRM` (—) | Exit 2 if REV is empty, CONFIRM is not yes, or a guard fails. | no | — |

**Synthetic data**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `seed` | M1 | no | Generate the deterministic dataset, snapshots and seed hash into an empty, migrated database; then verify. *Safety:* Guards DG-1 to DG-3 and DG-5. | `DB` (dev); `SCOPE` (full); `IF_EMPTY` (0) | Exit 2 if the database already holds a dataset and IF_EMPTY=0 (use seed-reset); exit 1 if verification fails. | no | — |
| `seed-reset` | M1 | **yes** | Drop and recreate the target database, migrate, seed and verify. *Safety:* Guards DG-1 to DG-5 (ARCH-R064). CI passes CONFIRM=yes with CENOMI_ENV=ci and DB=test only. | `DB` (dev); `SCOPE` (full); `CONFIRM` (—) | Exit 2 if a guard fails; exit 1 if any later step fails. | no | `ci/database`, `ci/integration`, `ci/e2e` |
| `seed-verify` | M1 | no | Run golden invariants, canonical figures and snapshot reconciliation against a seeded database (read-only). | `DB` (dev) | Exit 1 listing each failed check. | no | `ci/database` |

**Backend**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `backend-format` | M0 | no | Rewrite backend code formatting and import order (writes files). | — | Exit 1 only if a file cannot be parsed. | no | — |
| `backend-lint` | M0 | no | Static checks — ruff lint, ruff format check, import-linter module boundaries, SQL safety lint. | — | Exit 1 listing every violation. | yes | `ci/static` |
| `backend-typecheck` | M0 | no | mypy in strict mode over backend/src and scripts. | — | Exit 1 on any type error. | yes | `ci/static` |
| `backend-test` | M0 | no | Backend pytest suites — unit, and integration against cenomi_test. | `SUITE` (all); `K` (—) | Exit 1 on any failed test; exit 3 if SUITE needs the database and it is unreachable. | yes (`SUITE=unit`) | `ci/backend`, `ci/specs` |

**Frontend**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `frontend-format` | M0 | no | Rewrite web and package formatting with Prettier (writes files). | — | Exit 1 only if a file cannot be parsed. | no | — |
| `frontend-lint` | M0 | no | ESLint (flat config, boundaries, no-danger) and Prettier check across apps and packages. | — | Exit 1 listing every violation. | yes | `ci/static` |
| `frontend-typecheck` | M0 | no | TypeScript strict type check of every TS package (tsc --noEmit). | — | Exit 1 on any type error. | yes | `ci/static` |
| `frontend-test` | M0 | no | Vitest unit and component tests for apps/web and packages. | `FILTER` (—) | Exit 1 on any failed test. | yes | `ci/frontend` |
| `frontend-build` | M0 | no | Production build of apps/web (next build) and packages. | — | Exit 1 on a build error. | no | `ci/frontend` |

**Agent**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `agent-test-mock` | M3 | no | Agent runtime tests with the scripted mock model provider (no network, no recordings). | — | Exit 1 on any failed test. | no | `ci/agent` |
| `agent-test-replay` | M3 | no | Golden analytical cases on the replay provider against a seeded cenomi_test. | `SET` (slice) | Exit 1 on any failed deterministic check. | no | `ci/agent` |
| `agent-test-live` | M3 | no | Live-model evaluation with budgets. Never part of check or ci. *Safety:* Spends money. Separate credentials. Manual only. | `SET` (slice); `RECORD` (0) | Exit 2 if a control is missing; exit 1 if the run cannot complete; quality results are reported, not pass/fail, until EVALUATION_PLAN sets thresholds (PR-M5). | no | — |

**Contracts and integration**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `codegen` | M0 | no | Regenerate every GENERATED artefact (writes files). | — | Exit 1 if a generator fails; never edits non-generated files. | no | — |
| `contracts-check` | M0 | no | Verify generated artefacts are current, schemas use the allowed subset, examples validate, and Pydantic exports equal the bootstrap schemas. | — | Exit 1 listing each stale or invalid file. | yes | `ci/contracts` |
| `specs-check` | M0 | no | Validate specifications and engineering metadata (structure, IDs, links, frozen references, make/CI parity). | `GATE` (—) | Exit 1 listing each finding with file and line. | yes | `ci/specs` |
| `integration-test` | M0 | no | Cross-component tests — API contracts against the app and database, authorization boundaries, and (from M4) AG-UI event fixtures and tool execution. | — | Exit 1 on any failed test. | no | `ci/integration` |
| `e2e` | M0 | no | Playwright journeys with axe-core against the Compose stack (real PostgreSQL; replay model provider from M3). | `GREP` (—); `PROJECT` (—); `KEEP_UP` (0) | Exit 1 on any failed journey or serious/critical axe violation. | no | `ci/e2e` |

**Verification**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `trace-report` | M0 | no | Build the requirement → test trace report from milestone plans and test reports. | `CARD` (—); `GATE` (—) | Always exit 1 for unknown or malformed IDs. With CARD or GATE: also exit 1 for any in-scope AT that is FAILED, NOT_IMPLEMENTED or SKIPPED. | no | `ci/specs`, `ci/summary` |
| `security-check` | M0 | no | Secret scan, dependency audit and licence report. | — | Exit 1 listing each finding (secret values are redacted). | no | `ci/security` |
| `echarts-gate` | M0 | no | Run the DX3 gallery self-test on a local, version-pinned ECharts 5.6.0 (GDQ-06) and record the result. | — | M0–M1: exit 0 and record the result (informational). From M2: exit 1 if any ECharts row fails and the DXD-23 fallback is not recorded for that chart (GDQ-06, DXD-21). | no | `ci/echarts-gate` |
| `replay` | M6 | no | Insight checkpoint replay to as_of and golden comparison. | `SET` (slice) | Exit 1 on any difference. | no | `ci/integration` |

**Full validation**

| Target | Active from | Destructive | Summary | Arguments (default) | Failure | In `check` | CI jobs |
|---|---|---|---|---|---|---|---|
| `check` | M0 | no | Fast, non-destructive pre-PR validation. Needs no running database. | — | Exit status of the first failing target. | no | — |
| `ci` | M0 | no | Stable CI entry point. Runs the targets of one CI job (JOB=…) or of every job, as declared in specs/engineering/ci_checks.yaml. | `JOB` (—) | Exit status of the first failing target; prints the job and target. | no | `all` |

Full behaviour steps and prerequisites per target are in the YAML (`behaviour`, `prerequisites`).
<!-- END GENERATED: make_targets -->

### 5.3 What `make check` and `make ci` run

| Target | Runs | Needs | May change state |
|---|---|---|---|
| `make check` | `backend-lint` → `backend-typecheck` → `frontend-lint` → `frontend-typecheck` → `contracts-check` → `specs-check` → `backend-test SUITE=unit` → `frontend-test` | Installed dependencies only | Nothing (writes only `tests/reports/`) |
| `make ci` | Every job in `ci_checks.yaml` with `make_ci: true`, in dependency order; `make ci JOB=backend` runs one job | Docker for the database, e2e and image-related jobs | Recreates `cenomi_test` only (from M1) |

### 5.4 Mapping from the proposed ESP command list (ROADMAP amendment A-02)

| ESP tab 11 command | Approved target |
|---|---|
| `make up` / `make down` | Unchanged |
| `make db-reset` | `make seed-reset` |
| `make seed-slice` | `make seed SCOPE=slice` / `make seed-reset SCOPE=slice` |
| `make codegen` | Unchanged |
| `make lint` / `make typecheck` | `backend-lint`, `frontend-lint`, `backend-typecheck`, `frontend-typecheck` (aggregated by `make check`) |
| `make test` | `backend-test`, `frontend-test`, `integration-test` |
| `make test-e2e` | `make e2e` |
| `make replay` | Unchanged (active from M6) |
| `make eval` / `make eval-live` | `make agent-test-replay SET=…` / `make agent-test-live SET=…` |

Targets added beyond the approved list, each for a stated need: `db-init`, `codegen`, `trace-report`, `security-check`, `echarts-gate`, `replay`, `frontend-format`.

---

## 6. Docker Compose

**DEVENV-R016** `docker-compose.yml` defines these services. Image digests follow DEVENV-R005.

| Service | Image | Profile | Depends on | Health check | Notes |
|---|---|---|---|---|---|
| `db` | `postgres:16.<minor>@sha256:…` | default | — | `pg_isready` | Named volume `cenomi_pg`. `infra/postgres/bootstrap/roles.sql` mounted read-only and executed by `make db-init` (also mounted into `/docker-entrypoint-initdb.d/` for first start). Port 5432 bound to `127.0.0.1` only |
| `migrate` | `api` image | `setup` | `db` healthy | — | Command `alembic upgrade head` as `cenomi_owner`; exits |
| `seed` | `api` image | `setup` | `migrate` completed | — | Command `cenomi seed run --if-empty` (M1); exits non-zero on verify failure |
| `api` | `backend/Dockerfile` (python 3.12 slim + uv, non-root user) | default | `db` healthy | `GET /api/v1/health/live` | Uvicorn with one worker (in-process agent, ADR-0005). Port 8000 bound to `127.0.0.1` |
| `web` | `apps/web/Dockerfile` (node 22 slim, non-root, `next start` from the build output) | default | `api` healthy | `GET /` returns 200 or 307 | Rewrites `/api/*` and `/agui/*` to `API_INTERNAL_URL`. Port 3000 bound to `127.0.0.1` |
| `otel` (trace viewer) | Pinned image chosen in M0-T02 | `observability` | — | — | Off by default (ARCH-R099) |

The `web` service is added to `docker-compose.yml` by M0-T04, and the other services by M0-T02 (HC-3; DEVENV-R054). Until M0-T04 merges, `make up` starts the services that exist; the full behaviour of `make up` in `make_targets.yaml` is verified once both cards have merged (AT-M0-T02-01, AT-M0-T04-12).

**DEVENV-R017** Containers run as non-root users. No service mounts the Docker socket. No secret is baked into an image: `.env` is supplied at run time through `env_file`.

---

## 7. GitHub Actions CI

### 7.1 Workflows (ADR-0015)

| File | Trigger | Role |
|---|---|---|
| `.github/workflows/ci.yml` | `pull_request` to `main`; `push` to `main`; `workflow_call` | All validation jobs; the single required check `ci/summary` |
| `.github/workflows/milestone-gate.yml` | `workflow_dispatch` (inputs: milestone, sha) | Reuses `ci.yml` on a chosen `main` commit; adds the migration round-trip, gate-mode `specs-check` and `trace-report`, milestone-specific suites, and the verification report |
| `.github/workflows/eval-live.yml` | `workflow_dispatch` | Live-model evaluation from the protected `live-eval` environment, with budgets |
| `.github/actions/setup/action.yml` | Composite action | Checkout, uv with cache keyed by `uv.lock`, Node via `.nvmrc`, Corepack pnpm with the store cache keyed by `pnpm-lock.yaml`, `make install` |

**DEVENV-R018** There are no other workflow files. A new workflow needs an ADR.

### 7.2 Jobs

Rendered from `specs/engineering/ci_checks.yaml`. The YAML wins on conflict.

<!-- BEGIN GENERATED: ci_jobs (source: specs/engineering/ci_checks.yaml) -->
| Job (stable name) | Runs when (PR) | Needs | Make targets | Timeout (min) | Blocking | Purpose |
|---|---|---|---|---|---|---|
| `ci/changes` | `always` | — | — | 5 | yes | Compute, for every job, whether it is applicable to this change, with the reasons; publish the result as job outputs and tests/reports/ci/applicability.json. |
| `ci/static` | `not docs_only` | `ci/changes` | `doctor`, `backend-lint`, `backend-typecheck`, `frontend-lint`, `frontend-typecheck` | 15 | yes | Formatting, lint, type checks, lockfile validation, toolchain check, quarantine expiry. |
| `ci/specs` | `always` | `ci/changes` | `backend-test`, `specs-check`, `trace-report` | 15 | yes | Repository tooling and harness tests (backend-test SUITE=tooling, CR-001); specification and engineering-metadata validation; non-gate trace report. |
| `ci/contracts` | `backend or frontend or shared_contract` | `ci/changes` | `contracts-check` | 10 | yes | Generated artefacts current; schema subset; examples valid; Pydantic = schema. |
| `ci/security` | `always` | `ci/changes` | `security-check` | 15 | yes | Secret scan (full history), dependency audit, licence report. |
| `ci/backend` | `backend or database or agent or tests or shared_contract` | `ci/static` | `db-init`, `db-upgrade`, `backend-test` | 20 | yes | Backend unit and integration tests against PostgreSQL 16. |
| `ci/database` | `database or backend or shared_contract` | `ci/static` | `db-init`, `db-upgrade`, `db-current`, `db-check`, `seed-reset`, `seed-verify` | 25 | yes | Fresh migration, drift check, grants; from M1 deterministic seed, verify, snapshot reconciliation, KPI goldens. |
| `ci/frontend` | `frontend or shared_contract` | `ci/static` | `frontend-test`, `frontend-build` | 20 | yes | Vitest unit and component tests; production build. |
| `ci/agent` | `agent or backend or database or shared_contract` | `ci/static` | `agent-test-mock`, `agent-test-replay` | 20 | yes | Mock-model runtime tests and replay golden evaluations (active from M3). |
| `ci/integration` | `backend or frontend or database or agent or tests or shared_contract` | `ci/backend` | `db-init`, `db-upgrade`, `integration-test`, `replay` | 25 | yes | API contract, authorization boundaries, cross-module integration; AG-UI event fixtures (M4); slice replay golden (M6). |
| `ci/e2e` | `backend or frontend or database or agent or tests or shared_contract` | `ci/backend`, `ci/frontend` | `e2e` | 30 | yes | Playwright journeys with axe-core on the Compose stack (real PostgreSQL; replay model from M3). |
| `ci/echarts-gate` | `frontend or shared_contract` | `ci/static` | `echarts-gate` | 15 | from M2 | DX3 gallery self-test on pinned ECharts 5.6.0 (GDQ-06). Informational in M0–M1; blocking from M2. |
| `ci/images` | `backend or frontend or shared_contract` | `ci/static` | extra steps only | 25 | yes | Build the api and web Docker images (no push, ED-05). |
| `ci/quarantine` | `always` | `ci/changes` | extra steps only | 15 | no | Run quarantined tests and report them; never blocks (ARCH-R088). |
| `ci/summary` | `always` | `ci/changes`, `ci/static`, `ci/specs`, `ci/contracts`, `ci/security`, `ci/backend`, `ci/database`, `ci/frontend`, `ci/agent`, `ci/integration`, `ci/e2e`, `ci/echarts-gate`, `ci/images` | `trace-report` | 5 | yes | The single required check. Aggregates results, enforces skip rules, publishes the human-readable CI report. |

Required check: `ci/summary`. Runner `ubuntu-24.04`.
<!-- END GENERATED: ci_jobs -->

### 7.3 Triggering and path-aware execution

**DEVENV-R019** On pull requests, `ci/changes` classifies changed files into the path categories of `ci_checks.yaml`. Each job runs when its `runs_when` expression is true.

| Change type | Jobs that run |
|---|---|
| Every pull request | `ci/changes`, `ci/specs`, `ci/security`, `ci/quarantine`, `ci/summary` |
| Backend (`backend/**`) | `ci/static`, `ci/contracts`, `ci/backend`, `ci/database`, `ci/agent`, `ci/integration`, `ci/e2e`, `ci/images` |
| Frontend (`apps/web/**`, `packages/**`) | `ci/static`, `ci/contracts`, `ci/frontend`, `ci/integration`, `ci/e2e`, `ci/echarts-gate`, `ci/images` |
| Database (migrations, `db`, `seed`, metric YAML, scenarios, golden fixtures) | `ci/static`, `ci/backend`, `ci/database`, `ci/agent`, `ci/integration`, `ci/e2e` |
| Agent (agent and agui modules, eval cases, tool and AG-UI fixtures) | `ci/static`, `ci/backend`, `ci/agent`, `ci/integration`, `ci/e2e` |
| Specification-only (only `docs/**`, `plans/**`, root `*.md`, `.cursor/**`) | Only the "every pull request" set |
| Shared contract (`specs/**`, contracts, codegen and other scripts, Makefile, Compose, `.github/**`, lockfiles and manifests, `infra/**`, `.env.example`) | **Every job** |
| Push to `main`; milestone gate | **Every job**, regardless of paths |

The rationale for the shared-contract row: a shared change can affect several components, and its consumers are never skipped (ARCH-R093).

**DEVENV-R020** `ci/summary` is the only required check, and it **fails closed**. The exact rules are in `ci_checks.yaml` under `ci/summary.rules`. In summary, it passes only when all of the following hold:
- every applicable blocking job concluded `success` (failed, cancelled, timed-out, missing and every other conclusion fail it);
- every `skipped` job was genuinely not applicable;
- its own job list is complete;
- no report contains a result that the vocabulary rules make blocking.

Path optimization therefore cannot hide a failure.

**Fail-closed applicability (how a job is judged applicable).**

| # | Rule |
|---|---|
| **DEVENV-R047** | Applicability is computed once per run by `ci/changes` from the full PR diff against its merge base and the `path_categories` of `ci_checks.yaml`, and published as `tests/reports/ci/applicability.json`. On push to `main` and in the milestone gate, every job is applicable |
| **DEVENV-R048** | Uncertainty resolves towards running checks. If the diff cannot be computed, every job is applicable. A changed file that matches no category (other than `tests`) and is not specification-only is treated as a shared-contract change, so every job is applicable |
| **DEVENV-R049** | **Shared-contract consumers.** Any change to a `shared_contract` path (`specs/**`, `backend/src/cenomi/contracts/**`, `packages/contracts-ts/**`, `scripts/**`, `Makefile`, Compose files, `.github/**`, `infra/**`, `.env.example`, manifests and lockfiles, toolchain pins) makes **every** job applicable. The POC does not keep a per-contract consumer list, because a missed consumer would be a silent failure. Running every consumer is the simple fail-closed choice, and the cost is bounded by §7.5 |
| **DEVENV-R050** | `ci/summary` does not trust `ci/changes` alone. It recomputes applicability with the same library and fails on any disagreement, or if `ci/changes` did not succeed. It also fails if any job declared in `ci_checks.yaml` is absent from the run |

### 7.4 Reliability

| # | Concern | Rule |
|---|---|---|
| **DEVENV-R021** | Job dependencies | As in `needs` (§7.2). Fast checks (`ci/static`, `ci/specs`, `ci/contracts`, `ci/security`) start first; database, integration and E2E jobs wait for `ci/static` |
| **DEVENV-R022** | Timeouts | Every job sets `timeout-minutes` from `ci_checks.yaml`. Steps that start services wait with explicit health checks, never sleeps |
| **DEVENV-R023** | Resources | Jobs run on the standard GitHub-hosted runner. Pytest uses `-n auto` with per-worker test databases (`cenomi_test_gw<N>`, ARCH-R065). Playwright uses one worker in CI to keep the shared Compose stack deterministic |
| **DEVENV-R024** | Caching | uv cache keyed by `uv.lock`; pnpm store keyed by `pnpm-lock.yaml`; Playwright browsers keyed by the Playwright version; Docker layers through the buildx GitHub Actions cache; Next.js build cache keyed by the lockfile plus source hash. No cache holds test results or seeded databases |
| **DEVENV-R025** | Concurrency | One run per PR; a new push cancels the PR's in-progress run. Runs on `main` are never cancelled |
| **DEVENV-R026** | Isolation and fixtures | Every job starts from a fresh service database. From M1, jobs that need data run `make seed-reset DB=test CONFIRM=yes` (deterministic, hash-checked). Tests never depend on another job's state |
| **DEVENV-R027** | Secrets | Workflows use `permissions: contents: read` unless a step needs more. `ci.yml` uses **no secrets** and runs on `pull_request`, never `pull_request_target`, so fork PRs get no credentials. Only `eval-live.yml` reads `LIVE_EVAL_LLM_API_KEY`, through the protected `live-eval` environment |
| **DEVENV-R028** | Stable names | Job `name:` values equal `ci_checks.yaml` exactly. Renaming one is a CR, because branch protection depends on the name |
| **DEVENV-R029** | Artefact retention | Pull requests: 14 days. `main`: 30 days. Milestone gate: 90 days |

### 7.5 CI time budgets

| Path | Budget (p50) | Reason |
|---|---|---|
| `ci/static` + `ci/specs` + `ci/contracts` | ≤ 5 min | Fast feedback on every PR |
| `ci/backend`, `ci/frontend` | ≤ 10 min each | Unit plus module integration |
| `ci/database` (M1+) | ≤ 15 min | Includes the full deterministic seed |
| `ci/e2e` | ≤ 20 min | Compose stack plus journeys |
| Whole PR pipeline | ≤ 25 min wall clock | Keeps one-card PRs practical |

**DEVENV-R030** A budget overrun does not fail CI. It is reported in the CI summary and reviewed at the next milestone gate. Checks are never removed to meet a budget; a slow suite is split or sharded instead.

### 7.6 CI reporting

**DEVENV-R031** `ci/summary` writes `$GITHUB_STEP_SUMMARY` and uploads `tests/reports/ci-summary.md`.

**What the summary contains:**

| # | Item |
|---|---|
| 1 | Commit SHA |
| 2 | Specification-set version (`spec_set.yaml`) |
| 3 | Dataset ID and seed hash (from M1; "not seeded" before) |
| 4 | Each job with its applicability (and reason), conclusion and duration; every target or test reported `NOT_APPLICABLE` (with its rule), `NOT_IMPLEMENTED` or `SKIPPED` (with its reason) |
| 5 | Backend, frontend and integration test counts (passed, failed, skipped, quarantined) from JUnit |
| 6 | Agent mock and replay results (M3+) |
| 7 | Database invariant and canonical-figure results (M1+) |
| 8 | Contract and specification check results |
| 9 | Playwright results, with links to traces and screenshots of failures |
| 10 | Accessibility findings by severity |
| 11 | Evaluation metrics (M3+) |
| 12 | Coverage percentages (informational, ARCH-R091) |
| 13 | ECharts gate result |
| 14 | The trace-report excerpt for the cards touched by the PR |
| 15 | `requestRef`s seen in failing E2E tests |

**What it never contains:** secrets, environment values, result rows, prompts or model output. Business values appear only as golden-test identifiers and pass or fail.

**Milestone gate report.** `milestone-gate.yml` assembles `tests/reports/gate/M<n>/report.md` as described in RMAP-R010.

---

## 8. Branch, pull-request and merge policy

### 8.1 Branching

| # | Rule |
|---|---|
| **DEVENV-R032** | The integration baseline is the verified default branch `main`. Every independently testable task card is implemented on its own branch created from the latest `main`, named `feat\|fix\|test\|chore/m<n>-t<nn>-<slug>` (for example `feat/m0-t03-backend-skeleton`). Specification milestones use `docs/m<n>-<slug>`. The M0 AG-UI spike uses `spike/m0-t09-agui-spike` and is never merged. Defect fixes outside a card use `fix/def-<nnnn>-<slug>`. Patterns: `specs/traceability/id_conventions.yaml`, family `branch` |
| **DEVENV-R033** | Branches are short-lived: one card, normally merged within two working days. Long-lived integration branches are not used. If a card cannot finish in that window, it is split in its milestone plan; scope never grows on the branch |
| **DEVENV-R034** | **Stacked PRs.** Allowed only when a card depends on another card's unmerged PR. The dependent PR targets the prerequisite branch, both descriptions name each other, and the prerequisite merges first. The dependent PR is then rebased onto `main` and re-validated before merge. Otherwise, wait for the prerequisite |

### 8.2 Pull-request contents

**DEVENV-R035** Every PR description has these 15 sections. A section that does not apply says "N/A" with a reason. M0-T10 creates `.github/pull_request_template.md` with exactly these headings.

| # | Section |
|---|---|
| 1 | Feature ID and title (task card ID, or "Specification PR-M<n>", or `DEF-nnnn`) |
| 2 | Requirement and specification references (IDs) |
| 3 | Scope of changes |
| 4 | Implementation summary |
| 5 | Files and modules affected, and confirmation they are within the card's file ownership |
| 6 | Acceptance criteria (the card's AT IDs, each ticked when its test passes) |
| 7 | Tests added or updated (paths and AT IDs) |
| 8 | Local validation (`make check` and relevant targets, with results) |
| 9 | CI results (link to the run; filled once CI completes) |
| 10 | Screenshots for UI changes (desktop, tablet, phone where relevant) |
| 11 | API, schema and migration impact (contracts touched, version bumps, migrations and their reversibility) |
| 12 | Security considerations (authorization, secrets, input handling) |
| 13 | Known limitations and deferred items |
| 14 | Rollback and recovery notes |
| 15 | Dependencies on other PRs |

A specification PR uses the same headings, with the ESP tab 6 self-review checklist in section 6.

### 8.3 Merge policy

| # | Rule |
|---|---|
| **DEVENV-R036** | No direct commits to `main`. Every change arrives by PR |
| **DEVENV-R037** | No merge while `ci/summary` is failing or pending. Before `ci/summary` exists (until M0-T07 merges), the only allowed merges are those covered by an approved exception (EXC-001, §8.4) |
| **DEVENV-R038** | Squash merge. The squash title is `<card-id>: <title>` (or `docs: …` for specification PRs) |
| **DEVENV-R039** | Review is required. **Only the project owner approves and merges** (ADR-0001). Composer and Claude never merge. PRs are opened under the owner's GitHub account, and GitHub does not allow an author to approve their own PR. The owner's approval is therefore given by the owner merging the PR after review, not by a GitHub "approving review" (§8.4) |
| **DEVENV-R040** | All review conversations are resolved before merge |
| **DEVENV-R041** | The branch is validated against the latest `main` (rebased or merged-in, with a fresh CI run) before merge |
| **DEVENV-R042** | No force-push to `main`, and no rewriting of published history. Force-pushing a feature branch before review is allowed |
| **DEVENV-R043** | Completed milestone evidence (gate reports, ADRs, STATUS entries) is never deleted |

### 8.4 Repository protection (an M0 implementation requirement; specified, not applied by Claude)

**DEVENV-R044** Branch protection and the required-check rules are **an M0 implementation requirement, not a gate-time formality**. As of 2026-10-22, `main` has **no protection**. Applying it needs the project owner, or the owner's explicit authorization to Claude. Claude does not change repository administration settings during documentation work, and does not change them at all without that authorization.

The protection is applied in two stages, because the required check `ci/summary` cannot exist until M0-T07 has merged. GitHub blocks a PR forever on a required check that never reports.

| Stage | When it must be in force | Setting (ruleset on `main`, no bypass actors) |
|---|---|---|
| **P1 — before any implementation PR merges** | Before the first M0 task-card PR merges. A condition of the M0 build authorization (`plans/M0_FOUNDATION.md` §8) | Require a pull request before merging. **Required approving reviews: 0** (see DEVENV-R039; all PRs are authored by the owner's account). Require conversation resolution. Block force pushes. Block deletion. Allow squash merge only (enforced in the repository merge settings, DEVENV-R056), and delete head branches after merge |
| **P2 — required check** | Immediately after the M0-T07 PR merges and `ci/summary` has reported `success` on `main`; before any further PR merges | P1, plus: require status check `ci/summary`, strict (branch up to date with `main`) |

Settings applied together with P1:

| Setting | Value |
|---|---|
| Actions | Allow only actions pinned by SHA (or the owner's allow-list); default workflow token permission read-only; fork PRs get no secrets |
| Environment `live-eval` | Required reviewer: the project owner; deployment branches limited to `main` and this repository's branches; secret `LIVE_EVAL_LLM_API_KEY` stored only here. May be created when M3 starts |
| Secret scanning and push protection | Enabled (the repository is public) |
| Dependabot alerts | Enabled. Dependabot **version-update PRs** disabled; upgrades follow the CR rule of ADR-0003 |

**DEVENV-R051** **Exceptions.** A merge that the rules above would not allow is permitted only under an exception approved by the owner. The exception is recorded as `EXC-nnn` in `plans/STATUS.md` with:
- the scope (which PRs or cards);
- the reason;
- the compensating controls;
- an expiry condition;
- the approval date.

An unrecorded deviation fails GATE-M0-10.

**EXC-001 (Approved conditionally by the owner on 2026-10-22).** The PRs of exactly four cards, M0-T01, M0-T03, M0-T11 and M0-T10, which build the tooling that CI itself runs, may merge under stage P1 before `ci/summary` exists. The owner's seven conditions apply, numbered EXC-001/C1 to C7:

| # | Condition (owner, 2026-10-22) | How it is met |
|---|---|---|
| C1 | Document the exact affected feature PRs | Scope is the four card PRs only. Each PR number, branch and title is entered in the EXC-001 log in `plans/STATUS.md` when the PR opens |
| C2 | Run every available local validation before merging | Before merge, the PR pastes the output of `make check` and of every target named in the card's field 14 that exists at that point, plus the card's AT results. From the M0-T10 merge onward, `make trace-report CARD=<card>` is included |
| C3 | Record each merge SHA and its compensating controls | After merge, the squash SHA and the controls actually applied are entered in the EXC-001 log |
| C4 | Investigate whether M0-T07 can be introduced earlier | Finding and adopted mitigation: `plans/M0_FOUNDATION.md` §3 "EXC-001 condition C4" |
| C5 | Revalidate all exception-covered changes through GitHub Actions once CI is available | (a) The M0-T07 PR run shows `trace-report CARD=…` all `PASSED` for the four cards (AT-M0-T07-02). (b) The first `ci/summary` run on `main` after M0-T07 merges concludes `success`. Both run URLs are entered in the EXC-001 log |
| C6 | Successful retroactive verification is required before the M0 exit gate | GATE-M0-10 fails unless C5 (a) and (b) succeeded and the EXC-001 log is complete |
| C7 | No expansion of EXC-001 without additional approval | Any other card, PR or rule deviation needs a new owner-approved exception (`EXC-002`, …) |

EXC-001 expires when P2 is in force. M0-T07 itself is not covered by EXC-001: it merges under P1 after its own PR run shows `ci/summary` `success`.

**EXC-002 (Approved by the owner on 2026-10-23).** Exactly one security-patch PR (defect [DEF-0001](https://github.com/swa01wk/cenomi-dashboard-agent/issues/15), branch `fix/def-0001-security-advisories`, CR-002) may merge under stage P1 before `ci/summary` exists. It patches the two advisories reported by `make security-check` on M0-T10's branch: `certifi` in `backend/uv.lock` and `handlebars` (transitive, through `eslint-plugin-boundaries`) in `pnpm-lock.yaml`. Reason: ADR-0003 §2 requires a security patch to have its own CI run, but CI exists only after M0-T07 merges, and M0-T07's own `ci/security` job cannot pass while the advisories are open. The PR changes only `backend/pyproject.toml` (one `exclude-newer-package` entry), `backend/uv.lock`, `pnpm-workspace.yaml` (one `overrides` entry) and `pnpm-lock.yaml`, each lockfile regenerated per DEVENV-R052 (a), (d) and (e). Conditions: EXC-001 C1–C3 and C6 apply unchanged, with entries in the EXC-002 log in `plans/STATUS.md`; C5 is met by (a) the M0-T07 PR run showing `ci/security` `success` and (b) the first `ci/summary` run on `main` after M0-T07 merges concluding `success`. EXC-002 expires when the PR merges or when P2 is in force, whichever comes first. Any further patch before P2 needs a new exception.

**Approval of the protection policy (2026-10-22).** The owner approved the two-stage policy P1/P2 above, accepted **0 required approving reviews** for the single-developer workflow, and retained manual review and explicit milestone approval as project requirements. P1 must be applied before the first implementation PR merges. No existing security control may be weakened. Applying the settings remains the owner's action (DEVENV-R044).

**DEVENV-R056** **Protection availability, enforcement and verification** (verified 2026-10-23).

- *Availability.* The repository is **public** and owned by the personal account `swa01wk`. Rulesets, classic branch protection and required status checks are all available for public repositories on GitHub Free. P1 and P2 can therefore be enforced with no plan change and no change of visibility.
- *Form.* P1 and P2 are one repository **ruleset** targeting `main`, with **an empty bypass list**. GitHub grants bypass only to actors added to that list. Classic branch protection may be used instead, but only with "Do not allow bypassing the above settings" selected.
- *Squash only.* "Squash only" is enforced in the repository's merge settings: merge commits and rebase merging are disabled. A ruleset's merge-method restriction is not relied on, because it does not override the repository-wide settings.
- *Non-destructive verification.* No push to `main` is ever attempted as a test. After applying P1, the owner, or Claude with read-only API calls, records in STATUS:
  - the ruleset ID, `enforcement: active` and `bypass_actors: []`;
  - `current_user_can_bypass` for the owner's token, which is expected to be `never`; any other value is reported before the first card merges;
  - the rules returned by `GET /repos/{owner}/{repo}/rules/branches/main`;
  - the repository merge settings;
  - the ruleset's `updated_at`.

  P2 is verified the same way, plus the required check `ci/summary` in strict mode.
- *Residual limitation.* On a personal-account repository the owner holds admin rights, and admins can edit, disable or delete rulesets. GitHub offers no setting that prevents this. While the ruleset is active with an empty bypass list, the owner's pushes and merges are subject to it, but the owner can switch it off. Compensating controls:
  1. Only the owner changes repository settings (DEVENV-R044). Claude and Composer never do (AGENTSMD-R019).
  2. **Recommended:** Composer and other automation push with a fine-grained personal access token scoped to this repository, with Contents and Pull requests write and **no Administration permission**, so their credentials cannot change protection.
  3. Any change to the ruleset or merge settings after P1 is recorded in STATUS with its reason. GATE-M0-10 compares the ruleset's `updated_at` and current settings with those records.
- *Stronger separation, if ever needed* (each requires the owner's approval; neither is needed for M0): transfer the repository to an organization, where organization ownership can be separated from repository administration; or run automation through a GitHub App or a second account without admin rights. Making the repository private would **remove** rulesets and branch protection on GitHub Free, so visibility must not change without a plan decision.

### 8.5 Commit messages

**DEVENV-R045** Commit messages on branches are free-form but start with the card ID (for example `M0-T03: add health checks`). The squash commit follows DEVENV-R038. No commit contains secrets, real credentials or production data.

### 8.6 File ownership and shared files (HC-5, approved 2026-10-23)

**DEVENV-R053** **Most-specific path wins.** Field 13 of each task card assigns paths. When two cards' paths overlap, the more specific path decides ownership, whatever the merge order:
- an exact file path is more specific than any pattern;
- between patterns, the one with the longer literal prefix is more specific.

Broad directory ownership (for example M0-T03's `/backend/src/cenomi/**` or M0-T04's `/apps/web/**`) never covers a file or module that another card names explicitly. A card changes a file owned by another card only through the permissions of DEVENV-R052 or DEVENV-R054, through a `fix/` PR, or with the owner's approval.

**DEVENV-R054** **Shared configuration files and composition points.** The files below have one primary owner. Other cards may change them only in the stated way, and the PR's "Files and modules affected" section names each shared file it touches.

| Shared file or composition point | Primary owner (M0) | Permitted changes by other cards |
|---|---|---|
| `Makefile` | M0-T01 | Replace the stub recipe of a target the card implements (the M0 target-owner table in `plans/M0_FOUNDATION.md` §3, HC-7; also named in the card's field 12) with a call into its own scripts or CLI. Target names, order, arguments, help text and the result helper never change (`make_targets.yaml` is CF-0) |
| `backend/pyproject.toml` | M0-T01 | Dependency entries (DEVENV-R052, any card). The `[tool.pytest.ini_options]` section (M0-T11). **M0-T03 (HC-6):** `[build-system]` (`uv_build` within the pinned uv minor line), `[tool.uv] package = true`, `[tool.uv.build-backend]` (module `cenomi` under `src/`), `[project.scripts] cenomi = "cenomi.cli.main:main"` (ARCH-R034), `[tool.ruff]` with its sub-tables, and `[tool.mypy]`. `required-version` and `exclude-newer` stay with M0-T01 and change only through a change request. **CR-002:** a security-patch PR (ADR-0003 §2) may add a per-package `exclude-newer-package` entry under `[tool.uv]` for exactly the package it patches, with a comment citing the CR and the advisory; the entry is removed when `exclude-newer` next moves past its date |
| `backend/uv.lock`, `pnpm-lock.yaml` | M0-T01 | Regenerated per DEVENV-R052 |
| `apps/web/package.json`, `packages/contracts-ts/package.json` | M0-T01 | Dependencies and scripts of the delivering card (M0-T04, M0-T05) per DEVENV-R052 |
| `packages/viz/package.json` | M0-T08 (exact path) | — |
| `package.json` (root), `.env.example`, `pnpm-workspace.yaml` | M0-T01 | None in M0, except that a security-patch PR (ADR-0003 §2, **CR-002**) may add an exact-version entry under `overrides:` in `pnpm-workspace.yaml` for a transitive package it patches, with a comment citing the CR and the advisory. **M0-T06 (CR-004):** adds the single line `API_MAX_BODY_BYTES=1048576` to `.env.example`. `.env.example` otherwise already lists every DEVENV §4 variable; a missing variable is a specification defect, so stop and report |
| `docker-compose.yml` | M0-T02 | M0-T04 adds the `web` service block (HC-3) |
| `cenomi.api.app.create_app()` (router registration) | M0-T03 | M0-T06 registers the `session` router |
| Health wiring (the `check_database` provider used by the health router) | M0-T03 | M0-T02 binds the real `cenomi.db.health.check_database()` |
| `cenomi` CLI entry point | M0-T03 | M0-T02 registers the `db` sub-command |
| `backend/tests/conftest.py` | M0-T11 | M0-T02 adds the `pytest_plugins` entry for `backend/tests/fixtures/db.py` |
| `.github/workflows/**`, `.github/actions/**` | M0-T07 | None in M0, except in `ci.yml`: **M0-T05 (CR-003)** adds the JUnit staging and upload steps of `ci/contracts` and `ci/integration`; **M0-T08 (CR-005)** adds the Playwright browser install step and the JUnit staging and upload steps of `ci/echarts-gate`, each copying the existing pattern of the other jobs. Every job of `ci_checks.yaml` already calls its Make targets. A card whose target is not run stops and reports |

**DEVENV-R055** **Shared files in parallel work** (clarified by the owner on 2026-10-23). Parallel implementation *branches* are allowed. Pull requests that touch the same shared file are coordinated as follows:

| Case | Rule |
|---|---|
| **(a) Lockfiles** (`pnpm-lock.yaml`, `backend/uv.lock`) | At most **one open pull request, draft or ready, changes a given lockfile at a time**. A second branch that needs the same lockfile keeps its dependency change local and opens its PR only after the first has merged. It then rebases onto the updated `main`, regenerates the lockfile with the package manager (never merging it by hand), and re-runs `make install`, `make check` and the card's field-14 targets before asking for review |
| **(b) Other shared files and composition points** (DEVENV-R054) | Two open PRs may change the same file only in disjoint, permitted parts, for example the recipes of different Make targets, and only when each PR's "Dependencies on other PRs" section names the other. The PR that merges second rebases onto `main`, resolves conflicts only within its own permitted changes and re-runs CI |

In M0 Wave 3, M0-T05 and M0-T08 both change `pnpm-lock.yaml`, so they are serialized under (a). M0-T05 goes first, because it is on the critical path to M0-T06 and M0-T04. The `Makefile` recipes of M0-T02, M0-T05 and M0-T08 fall under (b). `docker-compose.yml` (M0-T02, then M0-T04) is already ordered by M0-T04's dependency on M0-T02.

---

## 9. Failure triage

**DEVENV-R046** Every CI or gate failure is classified into exactly one class and handled as below. A tracked defect is a GitHub issue titled `DEF-nnnn: …` with the class label and, if it blocks a gate, the label `blocking`. Flaky tests follow ARCH-R088; they are never auto-retried into a pass, and never skipped without a quarantine record.

| Class (label) | Signal | Owner | First action |
|---|---|---|---|
| `triage:test-failure` | A test fails deterministically on the PR | Card implementer | Fix within the card; if it is outside the card, stop and report |
| `triage:contract-mismatch` | `contracts-check` diff; schema validation; consumer suite failure after a contract change | Card implementer; architect if the contract is frozen | Never edit a GENERATED file. Change the source, or raise a CR for a frozen contract |
| `triage:kpi-discrepancy` | Golden metric test, GI invariant, canonical figure or snapshot reconciliation failure | Developer, with architect review | Stop dependent work (slice day 2 rule). Compare against `tests/fixtures/golden`; never change an expected value without a CR |
| `triage:authorization` | Isolation, scope-tampering or uniform-refusal test failure | Developer; owner informed | Treated as `blocking` |
| `triage:grounding` | Verifier rejection rate, untraced number, banned term or causal wording in agent output | Developer (M3+) | Inspect the run ledger by `runId`; fix the prompt template, tool or verifier; never relax the verifier |
| `triage:ui-rendering` | Component test, Playwright visual or interaction step, axe violation | Developer | Use the Playwright trace and screenshots; check the component's state vocabulary |
| `triage:ci-infrastructure` | Runner, cache, network or service-container failure unrelated to the change | Developer | Re-run once. If it recurs, open a DEF with logs; never mark it as a test pass |
| `triage:live-model-variability` | A live-evaluation difference not reproducible on replay | Architect (M5) | Record in the evaluation report; never gate an ordinary PR on it |
| `triage:flaky` | A test passes and fails on the same commit | Developer | Quarantine per ARCH-R088, or fix immediately |

---

## 10. Daily loop

1. `git switch main && git pull`, then create the card's branch (DEVENV-R032).
2. `make up` (first time: `make setup` first).
3. Implement within the card's file ownership.
4. Run `make check`; run the card's integration or E2E targets.
5. Push, open the PR with the template filled, and wait for `ci/summary`.
6. Address review. The owner merges.

---

## 11. Acceptance mapping (M0)

| Requirements | Verified by |
|---|---|
| DEVENV-R001–R015 | M0-T01, M0-T02, M0-T10 |
| DEVENV-R016, R017 | M0-T02, M0-T03, M0-T04 |
| DEVENV-R018–R031, R047–R050 | M0-T07, M0-T11 |
| DEVENV-R032–R045, R051 | M0-T10; GATE-M0-10 |
| DEVENV-R052 | M0-T01 (AT-M0-T01-01 clean-install check), `ci/static` lockfile validation; review |
| DEVENV-R053–R055 | Review (PR template section 5); M0 task-card field 13 |
| DEVENV-R056 | GATE-M0-10 (rules API evidence in STATUS) |
| DEVENV-R046 | M0-T10 (issue template) |
