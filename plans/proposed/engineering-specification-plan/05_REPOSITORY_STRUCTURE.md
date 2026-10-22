# 5 · Proposed repository structure

The repository has one rule: each fact has one home. specs/ holds the machine-readable truth that code and tests read. docs/ explains it in prose and links to it. Code implements it. Generated files are committed, marked GENERATED, and drift-checked in CI. This layout keeps your requested folders and supersedes the docs part of DR-034 (ADR-0002).

```text
cenomi-dashboard-agent/
├─ AGENTS.md                      repo map, commands, rules for Cursor
├─ README.md                      quick start
├─ Makefile                       one entry point for every command
├─ docker-compose.yml             db, api, web, migrate, seed
├─ .env.example                   every variable, no secrets
├─ .cursor/rules/*.mdc            enforced coding rules
├─ .github/workflows/             ci.yml, eval-live.yml (manual)
│
├─ docs/
│  ├─ product/       PRODUCT_SPEC.md (scope, personas, screens, cards, journeys, glossary)
│  ├─ architecture/  ARCHITECTURE.md, DEVELOPMENT_ENVIRONMENT.md, DATABASE_SCHEMA.md,
│  │                 SYNTHETIC_DATA_STRATEGY.md, AGENT_ARCHITECTURE.md, AGUI_INTEGRATION.md,
│  │                 PROACTIVE_INTELLIGENCE.md, EVALUATION_PLAN.md, generated/ (schema reference)
│  ├─ design/        DESIGN_BASELINE.md, DECISION_REGISTER.md, DESIGN_SYSTEM.md,
│  │                 GENERATIVE_UI.md, baseline/ (DX1–DX6 board screenshots)
│  ├─ contracts/     API_CONTRACTS.md, AGENT_TOOLS.md, KPI_CATALOG.md (prose over specs/)
│  ├─ adr/           README.md (index), 0001-…md …
│  └─ reference/     PRD, TA plan, API Reference, GD exports (frozen; ED-03)
│
├─ specs/                         machine-readable, normative, read by code or tests
│  ├─ metrics/       <metric_id>.yaml, unavailable_concepts.yaml, relationships.yaml
│  ├─ authorization/ permissions.yaml
│  ├─ scenarios/     manifest.yaml, cohorts/*.yaml
│  ├─ detectors/     detectors-1.1.yaml
│  ├─ genui/         registry.yaml, composition_policy.yaml
│  ├─ design/        tokens.json
│  └─ contracts/     *.schema.json (bootstrap by hand, then GENERATED from Pydantic)
│
├─ plans/          ROADMAP.md, SLICE_FIVE_DAY.md, M0_FOUNDATION.md … M6_PROACTIVE_INTELLIGENCE.md, STATUS.md
│
├─ backend/                       Python 3.12, uv
│  ├─ pyproject.toml, uv.lock
│  ├─ src/cenomi/
│  │  ├─ core/          settings, logging, telemetry, errors
│  │  ├─ contracts/     Pydantic models (source of specs/contracts after M0)
│  │  ├─ db/            engine, tables.py (SQLAlchemy Core metadata), roles
│  │  ├─ auth/          principals, sessions, AccessScope, permission loader
│  │  ├─ semantic/      metric registry loader and validator (reads specs/metrics)
│  │  ├─ analytics/     executor, queries/*.sql, scope fragment, derivations, datasets
│  │  ├─ api/           FastAPI app and routers (dashboard, metrics, records, insights, auth)
│  │  ├─ agent/         state machine, planner, DAG, tools, facts, verifier, llm/
│  │  ├─ presentation/  composer, policy, validator
│  │  ├─ agui/          AG-UI endpoint, event mapping, state sync
│  │  ├─ insights/      detectors, runner, outbox, inbox service
│  │  └─ seed/          generator, scenarios, snapshots, verify
│  ├─ migrations/    Alembic
│  └─ tests/         unit/ and integration/ per module
│
├─ apps/web/                      Next.js 16, TypeScript strict
│  └─ src/  app/ (routes)  features/ (dashboard, agent-panel, workspace, inbox, inspector)
│        genui/ (registry, renderers)  agui/ (client hooks)  lib/ (api client, query hooks)
│
├─ packages/
│  ├─ contracts-ts/  GENERATED TypeScript types and zod schemas
│  └─ viz/           chart primitives (ECharts wrappers, HTML visuals, treemap), token CSS
│
├─ tests/
│  ├─ fixtures/      golden/, metrics/<metric_id>/, principals.yaml, tools/, agui/, presentation/, insights/
│  ├─ e2e/           Playwright journeys (J, K, E2E-S)
│  ├─ agent-evals/   benchmark/, slice/, harness config
│  ├─ contract/      schema and event-fixture validation
│  ├─ security/      isolation, injection, secret scanning
│  └─ performance/   latency runs
│
├─ infra/          docker/ (Dockerfiles), postgres/init/ (roles, schemas)
└─ scripts/        codegen, schema export, catalog generation, seed verification
```

## Ownership rules

| Concern | Lives only in | Never duplicated in |
| --- | --- | --- |
| What a metric means | specs/metrics/\*.yaml | KPI\_CATALOG.md (generated tables), prompts, frontend code |
| How a metric is computed | backend/src/cenomi/analytics/queries/\*.sql | Tools, detectors, frontend; they all call the executor |
| Contract shapes | Pydantic in cenomi/contracts → specs/contracts → packages/contracts-ts | Hand-written TS types, docs tables |
| Who may see what | specs/authorization/permissions.yaml, enforced by AccessScope | Route handlers, prompts, the client |
| Expected values | tests/fixtures/golden | Test code literals, docs prose (docs link to the file) |
| Decisions | docs/adr and docs/design/DECISION\_REGISTER.md | Code comments, plans (plans cite IDs) |
| Progress | plans/STATUS.md | Milestone plans (they hold scope and cards, not status) |

## Rules enforced in Cursor and CI

- No SQL outside analytics/queries; every query file carries the scope fragment (CI lint).
- No arithmetic or numbers in prompt templates or model-facing text except fact tokens (lint plus verifier).
- No raw HTML, URL or code from model output reaches the UI (renderer accepts registry kinds only).
- Generated files are never edited by hand; CI regenerates and fails on any diff.
- Module boundaries are checked by import-linter (backend) and ESLint boundaries (web). For example, agent may import analytics, but analytics never imports agent.
- “overdue” never appears in generated text, templates or fixtures for approvals (lint).
- Each task card ships its tests in the same PR.
