# Local development and CI

One command brings up a clean stack, and one command resets the data to the canonical dataset. CI runs the same commands, so a green local run predicts a green PR. Everything runs locally under Docker Compose; there is no cloud deployment (DR-037).

## Commands (Makefile)

| Command | Does | Used by |
| --- | --- | --- |
| `make up` / `make down` | Build and start db, api, web; stop them | Daily work |
| `make db-reset` | Drop and recreate the database, run migrations as cenomi\_owner, seed sd-2026.10.20-01 as cenomi\_seed, run `cenomi seed verify` (GI invariants, canonical figures, snapshot reconciliation) and print the seed hash | Daily work, CI |
| `make seed-slice` | Same, but the Central region only, for slice development | Slice days 1–2 |
| `make codegen` | Export Pydantic schemas, regenerate TS and zod, tokens CSS, KPI\_CATALOG tables, the schema reference | Before every commit that touches contracts |
| `make lint` / `make typecheck` | ruff, import-linter, SQL scope lint, banned-term lint, ESLint, Prettier; mypy, tsc | CI |
| `make test` | Backend unit and integration, Vitest, contract and golden tests | CI |
| `make test-e2e` | Playwright journeys against the compose stack with the replay provider | CI |
| `make replay` | Insight replay to as\_of (slice or full detector set) | M6, slice day 5 |
| `make eval` | Benchmark on the replay provider; `make eval-live` uses the configured model | M5 |

## Docker Compose

| Service | Image | Notes |
| --- | --- | --- |
| db | postgres:16 (minor and digest pinned) | infra/postgres/init creates the four roles and the schemas; data volume can be wiped by `make db-reset` |
| migrate | api image, profile `setup` | `alembic upgrade head`; exits |
| seed | api image, profile `setup` | Generator, snapshots, verify; exits non-zero if any invariant fails |
| api | backend/Dockerfile (python 3.12 slim + uv) | Waits for db health; reader and app connection pools |
| web | apps/web/Dockerfile (node 22 + pnpm) | Rewrites /api/\* and /agui/\* to api |

An optional `observability` profile adds a local trace viewer; it is off by default.

## Environment configuration

.env.example lists every variable with a safe default; real values live in an untracked .env and in GitHub secrets.

| Group | Variables |
| --- | --- |
| Database | DATABASE\_URL\_OWNER, DATABASE\_URL\_SEED, DATABASE\_URL\_READER, DATABASE\_URL\_APP |
| Dataset | CENOMI\_DATASET\_ID=sd-2026.10.20-01, CENOMI\_AS\_OF=2026-10-20, CENOMI\_SEED (value fixed in SYNTHETIC\_DATA\_STRATEGY.md), CENOMI\_TZ=Asia/Riyadh |
| Auth | SESSION\_SECRET, AUTH\_MODE=dev\_fixture (ED-07) |
| Model | LLM\_PROVIDER, LLM\_PRIMARY\_MODEL, LLM\_FALLBACK\_MODEL, LLM\_API\_KEY, LLM\_MODE=replay or live, LLM\_REPLAY\_DIR |
| Agent budgets | AGENT\_MAX\_STEPS, AGENT\_MAX\_SECONDS, AGENT\_MAX\_TOKENS (defaults from AGENT\_ARCHITECTURE.md) |
| Telemetry | OTEL\_EXPORTER (console or otlp), LOG\_LEVEL |
| Web | API\_INTERNAL\_URL (server-side rewrite target) |

The api refuses to start with LLM\_MODE=live and no key, and never logs or streams a secret (SEC-06).

## Database initialization and seeding

1. infra/postgres/init (first start only) creates cenomi\_owner, cenomi\_seed, cenomi\_reader and cenomi\_app, plus the schemas and default privileges.
2. migrate applies Alembic migrations generated from tables.py.
3. seed runs the deterministic generator with the fixed seed, writes business data, as-of snapshots and seed\_meta, then records the dataset ID and seed hash.
4. verify runs the GI invariants, the canonical-figure checks and the snapshot reconciliation. Any failure fails the command.

Two resets on any machine produce the same hash. The reset time is measured in M1 and recorded in STATUS.md.

## GitHub CI

| Job | Runs | Blocks merge |
| --- | --- | --- |
| lint | ruff, import-linter, scope and banned-term lints, ESLint, Prettier, mypy, tsc | Yes |
| contracts | `make codegen` then `git diff --exit-code` | Yes |
| backend | Postgres 16 service; migrate; seed; pytest unit, integration, golden and security | Yes |
| frontend | Vitest; `next build` | Yes |
| e2e | Compose stack; Playwright journeys; axe-core; replay provider | Yes |
| echarts-gate | DX3 gallery self-test on ECharts 5.6.0; uploads results (GDQ-06) | Yes from M2 |
| security | gitleaks secret scan; pip-audit and pnpm audit (high severity fails) | Yes |
| images | Build the api and web images (no push) | Yes |
| eval-live | Benchmark on the live model; needs the LLM secret; manual trigger only | No |

CI runs on every PR and on main. main is protected: required checks, one approval (yours), squash merge. Branches are named after task cards, for example `m2/t07-approvals-card`. Per ED-05 there is no registry push and no deployment.
