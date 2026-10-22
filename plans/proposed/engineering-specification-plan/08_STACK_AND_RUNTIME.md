# Stack and runtime boundaries

The stack is DR-027 as approved, with version lines fixed now and exact patch versions pinned by lockfiles at M0. Two newer releases are deliberately not adopted under the freeze: ECharts 6.x (DXD-61 pins 5.6.0) and Node 24 (DR-027 says Node 22, which is supported through the POC). AG-UI reached 1.0 in September 2026, after DR-016/017 were written, so ED-10 asks you to confirm the 1.0 pin.

**Pin policy (ADR-0003):** at the M0 scaffold, each dependency takes the newest release that is at least 14 days old within the approved line. uv.lock and pnpm-lock.yaml are committed. Docker images are pinned by minor tag and digest. Upgrades during the POC happen only through a CR, except security patches.

## Stack and version lines

Versions checked Oct 22, 2026; the scaffold re-checks them.

| Layer | Choice | Line to pin | Latest seen | Basis |
| --- | --- | --- | --- | --- |
| Backend language | Python | 3.12.x | — | DR-027 |
| API framework | FastAPI on uvicorn | 0.15x | 0.158.1, 21 Oct 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/fastapi)) | DR-027 |
| Models and validation | Pydantic v2, pydantic-settings | 2.x | 2.14.1, 11 Oct 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/pydantic)) | DR-027, 028 |
| SQL | SQLAlchemy Core (no ORM) | 2.0.x | 2.0.55 and 2.1.6, Oct 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/sqlalchemy)) | DR-027; 2.0 is the conservative line |
| Driver | psycopg 3 | 3.x | 3.3.6, 18 Sep 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/psycopg)) | DR-027 |
| Migrations | Alembic | 1.x | 1.20.0, 11 Sep 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/alembic)) | DR-027 |
| AG-UI server | ag-ui-protocol | 1.0.x | 1.0.0, 17 Sep 2026 ([PyPI mirror](https://simple-repository.app.cern.ch/project/ag-ui-protocol)) | DR-016, 017; ED-10 |
| LLM access | Provider SDK behind the cenomi adapter, plus a replay provider | per GDQ-12 | — | DR-014, 015; ED-08 |
| Python tooling | uv, ruff, mypy, import-linter, pytest, pytest-asyncio, hypothesis | current | — | DR-027 |
| Telemetry | OpenTelemetry SDK with FastAPI and SQLAlchemy instrumentation; JSON logs | current | — | DR-027 |
| Web runtime | Node.js LTS, pnpm | 22.x | — | DR-027 |
| Web framework | Next.js App Router, React | 16.x, React 19 | 16.4.2, 21 Oct 2026 ([versio.io](https://www.versio.io/en/product-release-end-of-life-eol-vercel-nextjs.html)) | DR-027 |
| Web data | TanStack Query v5, zod | v5, v4 | — | DR-027 |
| AG-UI client | @ag-ui/client, @ag-ui/core | 1.x | AG-UI 1.0 frozen Sep 2026 ([announcement](https://github.com/ag-ui-protocol/ag-ui/discussions/2792), [CopilotKit blog](https://www.copilotkit.ai/blog/ag-ui-1.0)) | DR-016; ED-10 |
| Charts | Apache ECharts | 5.6.0 exactly | 6.1.0, 19 May 2026 ([ASF catalog](https://release-catalog.apache.org/echarts/6.1.0/index.html)); not adopted | DR-007; DXD-61 |
| Styling | CSS Modules and CSS variables generated from tokens.json | — | — | ED-09 |
| Contract codegen | Pydantic → JSON Schema 2020-12 → json-schema-to-typescript and a JSON Schema → zod generator | current | zod 4 compatibility checked in M0-T05 | DR-028 |
| Web tooling | TypeScript strict, ESLint with a boundaries plugin, Prettier, Vitest, Playwright, axe-core | current | — | DR-027 |
| Database | PostgreSQL | 16.x | 16.14 was the newest 16 minor in June 2026 ([Instaclustr](https://www.instaclustr.com/education/postgresql/postgres-versions-supported-releases-eol-dates-upgrades/)) | DR-027 |

AG-UI 1.0 matters to two designed behaviours. Runs can now end with `outcome: "cancelled"`, which maps to DXD-40 cancellation. Successful runs can name pending frontend tool calls, which fits propose\_dashboard\_filters (DR-025). The M0 spike checks both.

## Runtime processes and boundaries

| Process | Technology | Owns | Must never |
| --- | --- | --- | --- |
| web (:3000) | Next.js 16 on Node 22 | Rendering, routing, client state, chart primitives, GenUI renderers, AG-UI client; proxies /api/\* and /agui/\* to api | Query the database, compute a metric, call an LLM, decide authorization, render model-written HTML |
| api (:8000) | FastAPI on uvicorn, Python 3.12 | REST routes, AG-UI SSE endpoint, agent runtime in-process (asyncio), LLM adapter, AccessScope, metric executor, insight service | Let model output reach SQL; build SQL by string concatenation; serve UI |
| db (:5432) | PostgreSQL 16 | Schemas core (business, read-only to the app), meta (data versions, as in the GD architecture), snap (as-of snapshots, proposed), seed\_meta (labels, hidden from the agent), agent, insights | Be reached by web |
| migrate (one-shot) | Alembic in the api image | Schema changes, as cenomi\_owner | Run at api start-up implicitly |
| seed (one-shot) | cenomi seed in the api image | Deterministic data, snapshots and the seed hash, as cenomi\_seed | Run against a database that has not been reset |
| insight replay (command) | cenomi insights replay in the api image | Checkpoint replay up to as\_of (DR-005, DXD-75) | Run as a background scheduler |

## Database roles

| Role | Can | Cannot |
| --- | --- | --- |
| cenomi\_owner | DDL on all schemas (migrations only) | Be used by api or seed at run time |
| cenomi\_seed | Write core, meta, snap, seed\_meta | Write agent or insights |
| cenomi\_reader | SELECT on core, meta and snap; used by the metric executor’s pool | Read seed\_meta; write anything |
| cenomi\_app | Read and write agent and insights; used for conversation and insight state | Read core, snap or seed\_meta directly; every business number goes through the reader pool |

core, meta, agent, insights and seed\_meta come from the GD architecture; snap is a new proposal (the snapshots could instead live in meta). DATABASE\_SCHEMA.md finalizes the names; the separation itself follows DR-013, DR-021 and DR-029.
