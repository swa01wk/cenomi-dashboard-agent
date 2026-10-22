# ADR-0003 — Technology stack and version pinning

| | |
|---|---|
| Status | Proposed (becomes Accepted when PR-M0 merges) |
| Date | 2026-10-22 |
| Decision IDs | DR-027 (approved, GDQ-10), DR-007 and DXD-61 (verification pending), DR-016, ED-09 (proposed), ED-10 (proposed) |

## Context

DR-027 fixed the stack at the Final Design Gate. Exact versions are pinned by lockfiles at the M0 scaffold. ESP tab 8 recorded version lines checked on 22 Oct 2026. GDQ-06 and DXD-21 forbid treating design test doubles as runtime evidence. Part 13 §9 of the 22 Oct approval asks for supported versions, licences and compatibility assumptions to be recorded together with the real-library verification tests.

## Decision

### 1. Stack and version lines

| Layer | Choice | Line pinned at scaffold | Basis |
|---|---|---|---|
| Backend language | CPython | 3.12.x | DR-027 |
| API | FastAPI on uvicorn | latest 0.x release ≥ 14 days old | DR-027 |
| Models | Pydantic v2, pydantic-settings | 2.x | DR-027, DR-028 |
| SQL | SQLAlchemy **Core** 2.0.x (no ORM); async engine | 2.0.x | DR-027 |
| Driver | psycopg 3 | 3.x | DR-027 |
| Migrations | Alembic | 1.x | DR-027 |
| Python tooling | uv; ruff; mypy (strict); import-linter; pytest, pytest-asyncio, hypothesis, pytest-cov, pytest-xdist | current lines | DR-027 |
| CLI | Python standard library `argparse` (no CLI framework) | — | Keeps the dependency set closed |
| Telemetry | OpenTelemetry SDK (FastAPI and SQLAlchemy instrumentation); JSON logs | current | DR-027 |
| Web runtime | Node.js LTS; pnpm through Corepack | 22.x; pnpm version pinned in `packageManager` | DR-027 |
| Web framework | Next.js App Router; React | 16.x; 19.x | DR-027 |
| Web data | TanStack Query v5; zod | v5; v4 | DR-027 |
| Web tooling | TypeScript (strict); ESLint flat config with a boundaries plugin; Prettier; Vitest with Testing Library; Playwright; axe-core | current lines | DR-027 |
| Styling | CSS Modules plus CSS variables generated from `specs/design/tokens.json` | — | **ED-09, still Proposed** (alternative: Tailwind). M0 builds no styled component beyond the shell; see M0-T04 |
| Charts | Apache ECharts | **5.6.0 exactly** | DR-007, DXD-61. 6.x not adopted under the freeze |
| AG-UI | `ag-ui-protocol` (Python); `@ag-ui/core` and `@ag-ui/client` (TS) | **Not pinned until ED-10 is decided.** The M0 spike runs against 1.0.x | DR-016, ED-10 |
| Database | PostgreSQL | 16.x (image pinned by minor tag and digest) | DR-027 |
| Containers | Docker Compose v2 | — | DR-037 |

### 2. Pin policy

- At the M0 scaffold, each dependency takes the newest release that is at least **14 days old** within the approved line.
- `uv.lock` and `pnpm-lock.yaml` are committed.
- CI installs only from lockfiles (`uv sync --locked`, `pnpm install --frozen-lockfile`).
- Docker base images and GitHub Actions are pinned by digest or commit SHA.
- During the POC, upgrades happen only through a CR, except security patches flagged by the `ci/security` job.
- A security patch upgrade is still a PR with its own CI run.

### 3. Facts verified on 2026-10-22 (this session)

| Fact | Result | Source |
|---|---|---|
| `ag-ui-protocol` 1.0.0 | Released 17 Sep 2026; requires Python ≥ 3.9; MIT licence | PyPI mirror |
| AG-UI TS packages | `@ag-ui/core`, `@ag-ui/client`, `@ag-ui/encoder` 1.0.0 (17 Sep 2026) and 1.0.1 (29 Sep 2026); zod is a **peer dependency** | Published migration write-up |
| AG-UI 1.0 events | Interrupts end a run with `RUN_FINISHED.outcome = {type: "interrupt", interrupts: [...]}`; the only other outcome is `success`; errors go through `RUN_ERROR`; resume is a new run carrying a `resume` array | AG-UI interrupts documentation |
| AG-UI 1.0 extras | Adds `protocolVersion`; custom fields placed directly on events are stripped, and `metadata` is the sanctioned place for custom data | Published migration write-up |
| Next.js 16 | Requires Node.js ≥ 20.9 (Node 22 satisfies it); Turbopack is the default bundler; `next lint` is removed (ESLint is run directly); `middleware` is renamed `proxy` | Next.js 16 upgrade guide |
| Apache ECharts 5.6.0 | Released 28 Dec 2024; Apache License 2.0 (ASF project) | ASF release catalogue |

**Correction to the ESP.** ESP tab 8 states that AG-UI 1.0 "adds `outcome: "cancelled"`". The 1.0 documentation found on 2026-10-22 lists only `success` and `interrupt` outcomes, with errors reported through `RUN_ERROR`. The approved DX4 design already maps Stop to `RUN_ERROR` with code `CANCELLED` (DX4-AGUI), so the design is unaffected. The M0 spike must confirm the actual behaviour (spike item A11, ARCHITECTURE §8.4). ED-10 stays Proposed.

### 4. Licences

The direct dependencies are permissive or weak-copyleft:

| Licence | Packages |
|---|---|
| MIT | FastAPI, Pydantic, SQLAlchemy, Alembic, Next.js, React, TanStack Query, zod, Vitest, AG-UI |
| Apache-2.0 | ECharts, Playwright |
| MPL-2.0 | axe-core |
| PostgreSQL Licence | PostgreSQL |
| LGPL-3.0 | psycopg 3, used unmodified as a library |

- The `ci/security` job produces a licence report on every run.
- GPL-family and AGPL licences fail the job unless an ADR accepts them.

### 5. Compatibility assumptions and the tests that verify them

| ID | Assumption | Verified by | When |
|---|---|---|---|
| CA-01 | ECharts 5.6.0 renders every DX3 chart within the DX3 thresholds | M0-T08 harness: DX3 gallery self-test on a local, version-pinned ECharts 5.6.0 asset | M0 gate (recorded); mandatory pass or fallback by the M2 exit (GDQ-06) |
| CA-02 | AG-UI 1.0 SDKs support the DX4 event mapping (assumptions A1–A8 plus A9–A14) | M0-T09 spike report | M0 gate; final at M4 exit |
| CA-03 | The `@ag-ui/core` zod peer range accepts the project's zod 4 line | M0-T09 spike (A13) | M0 |
| CA-04 | Next.js rewrites stream Server-Sent Events from `/agui/*` without buffering | M0-T09 spike (A14) | M0 |
| CA-05 | The zod 4 output of the in-repo generator validates the same instances as the JSON Schemas | M0-T05 contract tests (ADR-0004) | M0 |
| CA-06 | psycopg 3 async with SQLAlchemy Core 2.0 supports per-pool `statement_timeout` and read-only sessions | M0-T02 integration test | M0 |

## Consequences

- Deterministic installs, and identical tooling locally and in CI.
- ED-09 and ED-10 can still change their rows without reopening this ADR. Each produces a short follow-up ADR (ED-09 → DSYS ADR in PR-M2; ED-10 → ADR-0010).

## Verification

- `make doctor` reports the toolchain versions against `.python-version`, `.nvmrc`, `packageManager` and the lockfiles.
- `ci/static` fails on a lockfile mismatch.
- GATE-M0-07 records CA-01 to CA-06.
