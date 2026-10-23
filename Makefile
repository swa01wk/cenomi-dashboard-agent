# Root Makefile — target contract: specs/engineering/make_targets.yaml (M0-T01)
SHELL := /bin/bash
.RECIPEPREFIX := >
.DEFAULT_GOAL := help

export BROWSERS ?= 1
export VOLUMES ?= 0
export CONFIRM ?=
export SERVICE ?=
export FOLLOW ?= 1
export DB ?= dev
export REV ?=
export SCOPE ?= full
export IF_EMPTY ?= 0
export SUITE ?= all
export K ?=
export FILTER ?=
export SET ?= slice
export RECORD ?= 0
export GREP ?=
export PROJECT ?=
export KEEP_UP ?= 0
export JOB ?=
export GATE ?=
export CARD ?=

INVOKE := python3 scripts/make/invoke.py

# ----------------------------------------------------------------- environment
help: ## List every target with its one-line summary, grouped as in this file.
> @$(INVOKE) help

doctor: ## Verify the local toolchain and configuration against the pinned versions.
> @$(INVOKE) doctor

setup: ## First-time setup — doctor, create .env from .env.example if absent, install dependencies.
> @$(INVOKE) setup

install: ## Install locked dependencies for backend and web (no lockfile changes).
> @$(INVOKE) install

up: ## Build and start db, api and web; bootstrap roles and migrate the dev database; wait until healthy.
> @$(INVOKE) up

down: ## Stop the stack. Data volumes are kept unless VOLUMES=1 CONFIRM=yes.
> @$(INVOKE) down

logs: ## Follow container logs (JSON lines for api).
> @$(INVOKE) logs

clean: ## Remove local build outputs and caches. Never removes dependencies, data volumes, .env or committed files.
> @$(INVOKE) clean

# ----------------------------------------------------------------- database
db-init: ## Create the four roles and the cenomi_dev / cenomi_test databases if missing (idempotent).
> @$(INVOKE) db-init

db-upgrade: ## Apply Alembic migrations to head as cenomi_owner.
> @$(INVOKE) db-upgrade

db-current: ## Print the current Alembic revision and whether it is head.
> @$(INVOKE) db-current

db-check: ## Detect drift between tables.py metadata and the migrated database (alembic check) and verify roles and grants.
> @$(INVOKE) db-check

db-history: ## Print the migration history.
> @$(INVOKE) db-history

db-downgrade: ## Downgrade to a named revision. Never run by `make check` or `make ci`.
> @$(INVOKE) db-downgrade

# ----------------------------------------------------------------- synthetic_data
seed: ## Generate the deterministic dataset, snapshots and seed hash into an empty, migrated database; then verify.
> @$(INVOKE) seed

seed-reset: ## Drop and recreate the target database, migrate, seed and verify.
> @$(INVOKE) seed-reset

seed-verify: ## Run golden invariants, canonical figures and snapshot reconciliation against a seeded database (read-only).
> @$(INVOKE) seed-verify

# ----------------------------------------------------------------- backend
backend-format: ## Rewrite backend code formatting and import order (writes files).
> @$(INVOKE) backend-format

backend-lint: ## Static checks — ruff lint, ruff format check, import-linter module boundaries, SQL safety lint.
> @$(INVOKE) backend-lint

backend-typecheck: ## mypy in strict mode over backend/src and scripts.
> @$(INVOKE) backend-typecheck

backend-test: ## Backend pytest suites — unit, and integration against cenomi_test.
> @$(INVOKE) backend-test

# ----------------------------------------------------------------- frontend
frontend-format: ## Rewrite web and package formatting with Prettier (writes files).
> @$(INVOKE) frontend-format

frontend-lint: ## ESLint (flat config, boundaries, no-danger) and Prettier check across apps and packages.
> @$(INVOKE) frontend-lint

frontend-typecheck: ## TypeScript strict type check of every TS package (tsc --noEmit).
> @$(INVOKE) frontend-typecheck

frontend-test: ## Vitest unit and component tests for apps/web and packages.
> @$(INVOKE) frontend-test

frontend-build: ## Production build of apps/web (next build) and packages.
> @$(INVOKE) frontend-build

# ----------------------------------------------------------------- agent
agent-test-mock: ## Agent runtime tests with the scripted mock model provider (no network, no recordings).
> @$(INVOKE) agent-test-mock

agent-test-replay: ## Golden analytical cases on the replay provider against a seeded cenomi_test.
> @$(INVOKE) agent-test-replay

agent-test-live: ## Live-model evaluation with budgets. Never part of check or ci.
> @$(INVOKE) agent-test-live

# ----------------------------------------------------------------- contracts_and_integration
codegen: ## Regenerate every GENERATED artefact (writes files).
> @$(INVOKE) codegen

contracts-check: ## Verify generated artefacts are current, schemas use the allowed subset, examples validate, and Pydantic exports equal the bootstrap schemas.
> @$(INVOKE) contracts-check

specs-check: ## Validate specifications and engineering metadata (structure, IDs, links, frozen references, make/CI parity).
> @$(INVOKE) specs-check

integration-test: ## Cross-component tests — API contracts against the app and database, authorization boundaries, and (from M4) AG-UI event fixtures and tool execution.
> @$(INVOKE) integration-test

e2e: ## Playwright journeys with axe-core against the Compose stack (real PostgreSQL; replay model provider from M3).
> @$(INVOKE) e2e

# ----------------------------------------------------------------- verification
trace-report: ## Build the requirement → test trace report from milestone plans and test reports.
> @$(INVOKE) trace-report

security-check: ## Secret scan, dependency audit and licence report.
> @$(INVOKE) security-check

echarts-gate: ## Run the DX3 gallery self-test on a local, version-pinned ECharts 5.6.0 (GDQ-06) and record the result.
> @$(INVOKE) echarts-gate

replay: ## Insight checkpoint replay to as_of and golden comparison.
> @$(INVOKE) replay

# ----------------------------------------------------------------- full_validation
check: ## Fast, non-destructive pre-PR validation. Needs no running database.
> @$(INVOKE) check

ci: ## Stable CI entry point. Runs the targets of one CI job (JOB=…) or of every job, as declared in specs/engineering/ci_checks.yaml.
> @$(INVOKE) ci

.PHONY: help doctor setup install up down logs clean db-init db-upgrade db-current db-check db-history db-downgrade seed seed-reset seed-verify backend-format backend-lint backend-typecheck backend-test frontend-format frontend-lint frontend-typecheck frontend-test frontend-build agent-test-mock agent-test-replay agent-test-live codegen contracts-check specs-check integration-test e2e trace-report security-check echarts-gate replay check ci
