# ADR-0006 — Database roles, schemas, the `snap` schema and schema ownership

| | |
|---|---|
| Status | Proposed. **D-01 Option A** (dedicated `snap` schema) was approved by the project owner on 2026-10-22; the role and schema separation rests on approved DR-013, DR-021 and DR-029. This ADR becomes Accepted when PR-M0 merges |
| Date | 2026-10-22 |
| Decision IDs | D-01 (approved), DR-013, DR-021, DR-029, DR-003, DR-033, GDQ-03, DXD-80, DXD-81, DXD-88 |
| Closes | Restoration gaps G-1 (snapshot schema) and G-4 (agent and insight schema ownership) |

## Context

- Business data is read-only to the application (DR-013).
- There is no row-level security. Instead, a mandatory scope fragment, a lint and a read-only role apply (DR-021).
- Conversation and run state live in schema `agent` and insight state in `insights`; there is no Redis (DR-029).
- GDQ-03 makes as-of history a set of materialized snapshots written by the seed and reconciled to the parity metrics at `as_of`.
- The GD architecture named `core`, `meta`, `agent`, `insights` and `seed_meta`. Where snapshots live was open until D-01.
- M0 creates the roles and the empty schemas (task card M0-T02), so the schema list and the grant matrix must be fixed in M0, not in PR-M1.

## Decision

### 1. Schemas

All six schemas are owned by `cenomi_owner` and created empty by the M0 baseline migration.

| Schema | Holds | Tables specified in | Tables first migrated in | Writer role | Reader roles |
|---|---|---|---|---|---|
| `core` | Business data (read-only to the app) | DATABASE_SCHEMA.md (PR-M1) | M1 | `cenomi_seed` | `cenomi_reader` |
| `meta` | Data versions (dataset id, `as_of`, seed hash, generator version, `ingested_at` rules) | DATABASE_SCHEMA.md (PR-M1) | M1 | `cenomi_seed` | `cenomi_reader` |
| `snap` | Materialized as-of metric snapshots (D-01) | DATABASE_SCHEMA.md + ADR-0012 (PR-M1) | M1 | `cenomi_seed` | `cenomi_reader` |
| `seed_meta` | Scenario manifests, cohort labels, exposing-row labels | DATABASE_SCHEMA.md (PR-M1) | M1 | `cenomi_seed` | **None of the application roles** (DATA-06); read only by `cenomi_seed` in `seed verify` and tests |
| `agent` | Threads, runs, run events (ledger), answer versions, facts, datasets, analytical state | AGENT_ARCHITECTURE.md + DATABASE_SCHEMA.md amendment (PR-M3) | M3 | `cenomi_app` | `cenomi_app` |
| `insights` | Evaluation runs, candidates, insights and versions, instances, triage state, outbox, feedback | PROACTIVE_INTELLIGENCE.md + DATABASE_SCHEMA.md amendment (PR-M6) | M6 slice part (before M5, allowed by DR-010 for the thin slice) | `cenomi_app` | `cenomi_app` |

**Ownership and sequencing rule (G-4).**
- No table is created in `agent` or `insights` before the specification PR that freezes its owning contract (CF-3 for `agent`, CF-5 for `insights`) has merged.
- PR-M1 creates no tables in those schemas. This amends the ESP M1 deliverable list (`plans/ROADMAP.md` amendment A-07).

### 2. The `snap` schema (D-01)

| # | Rule | Basis |
|---|---|---|
| a | **Producer.** Snapshots are written only by `cenomi seed`, in the same run that writes `core`, from the generator's own lifecycle events. Never by the API, the agent or the insight runner | GDQ-03 |
| b | **Binding.** Every snapshot row carries `dataset_id` (foreign key to `meta`), `metric_id`, `metric_version` and an Asia/Riyadh `checkpoint_date`. The full key and column list is fixed in PR-M1 | — |
| c | **Immutability.** Rows are never updated after the dataset is published. Corrected or late data produces a new dataset version | DXD-88 |
| d | **Reconciliation invariant.** At `checkpoint_date = as_of`, each `.asof` metric equals its parity metric, run by the analytics executor over `core`, for every mall and every region | GDQ-03, DXD-80 |
| e | **Lineage.** Every series value is reproducible from `core` record lifecycles | GI-03 |
| f | **Access.** `snap` is read only through the metric executor's SQL templates for `.asof` metrics. No other module reads `snap` directly | DR-030 |

The reconciliation invariant (d) is an M1 gate check. Lineage (e) is checked in M1 and M5.

### 3. Roles and grants

| Role | Login | Granted | Explicitly denied | Used by |
|---|---|---|---|---|
| `cenomi_owner` | yes | Owns all six schemas; DDL | — | `make db-upgrade` / `migrate` service only. Never by `api` or `seed` at run time |
| `cenomi_seed` | yes | USAGE; SELECT, INSERT, UPDATE, DELETE, TRUNCATE on all tables and sequences in `core`, `meta`, `snap`, `seed_meta` | No USAGE on `agent`, `insights` | `seed` service, `make seed*`, `seed verify`, test fixtures that need scenario labels |
| `cenomi_reader` | yes | USAGE; SELECT on `core`, `meta`, `snap`. Role defaults: `default_transaction_read_only = on`, `statement_timeout = 5000` (ms) | No USAGE on `seed_meta`, `agent`, `insights`; no write anywhere | The metric executor's connection pool (the only business-data reader) |
| `cenomi_app` | yes | USAGE; SELECT, INSERT, UPDATE, DELETE on tables and USAGE on sequences in `agent`, `insights` | No USAGE on `core`, `meta`, `snap`, `seed_meta` | Conversation, run and insight state |

Further rules:
- `PUBLIC` has its privileges on the `public` schema and the database revoked. CONNECT is granted only to the four roles.
- `ALTER DEFAULT PRIVILEGES FOR ROLE cenomi_owner IN SCHEMA <schema>` mirrors the grants above, so tables added by later migrations inherit them without a grant statement.
- Roles are cluster objects. They are created by the idempotent bootstrap script `infra/postgres/bootstrap/roles.sql`, executed by `make db-init` (local and CI) and by the Compose `db` init hook, using the PostgreSQL superuser of a **local or CI** database only.
- Schemas, grants and default privileges are created by the first Alembic revision, run as `cenomi_owner`.
- Passwords come from environment variables. `.env.example` holds development-only placeholder values. No real credential is committed.

### 4. Migration rules (summary; full text in ARCHITECTURE.md §7)

- One linear Alembic history, append-only after merge.
- A fresh-database upgrade runs in every CI database job.
- `alembic check` reports no drift between `tables.py` and the migrated database.
- Every revision implements `downgrade()`. Downgrades are exercised only by the milestone-gate workflow on an ephemeral database, never by ordinary CI.
- The POC recovery strategy is forward-fix plus `make seed-reset` on local and test databases: business data is regenerable by the seed, and `agent` and `insights` state is disposable in the POC.

## Options considered (D-01)

| Option | Summary | Outcome |
|---|---|---|
| A | Dedicated `snap` schema, written by the seed, read by `cenomi_reader` | **Approved** |
| B | Snapshots stored in `meta` | Not chosen: it mixes data-version bookkeeping with metric data, and it widens what `meta` grants must cover |

## Consequences

- The reader role can never write. The app role can never read business tables directly, so every business number passes through the executor.
- An agent or insight feature that needs a table must wait for its contract freeze. This is intended.

## Verification

| Check | Test |
|---|---|
| Six schemas exist; grants match §3; `cenomi_reader` cannot write; `cenomi_app` cannot read `core`; nobody but `cenomi_seed` and `cenomi_owner` can read `seed_meta` | AT-M0-T02-02 to AT-M0-T02-06 |
| Snapshot reconciliation | M1 gate |
