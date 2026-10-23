# ADR-0005 — Backend as a modular monolith; agent in-process

| | |
|---|---|
| Status | **Accepted** — PR-M0 merged 2026-10-22 at `4515031` (recorded 2026-10-23). The underlying decision **ED-02 Option A was approved by the project owner on 2026-10-22**. |
| Date | 2026-10-22 |
| Decision IDs | ED-02 (approved), DR-013, DR-016, DR-037; supersedes the service split in TA §11 |

## Context

TA §11 sketched separate `services/api` and `services/agent` deployables linked over internal HTTP. The approved architecture (GD architecture tab) requires:
- one metric service;
- one AccessScope check on every read;
- an AG-UI SSE stream carrying run events from the agent runtime.

A network boundary between api and agent would add a second authorization surface, a second trace hop and a streaming relay, with no benefit for a local Docker Compose POC (DR-037).

## Decision

The backend is **one FastAPI deployable (`api`)**, a Python 3.12 package `cenomi` with these modules:

| Module | Responsibility |
|---|---|
| `core` | Settings, logging, telemetry, error classes, clock (`as_of`) |
| `contracts` | Pydantic contract models |
| `db` | Engines, pools, table metadata, role checks |
| `auth` | Sessions, principals, AccessScope |
| `semantic` | Metric registry loader and validator |
| `analytics` | Metric executor, SQL templates, derivations, dataset store |
| `api` | FastAPI app factory and REST routers |
| `agent` | Run state machine, planner, DAG executor, tools, verifier, LLM adapter |
| `presentation` | Composer, policy, validator |
| `agui` | AG-UI endpoint, event mapping, state sync |
| `insights` | Detectors, runner, outbox, inbox service |
| `seed` | Generator, snapshots, verification; command-line only |

The agent runtime runs **in-process** on the asyncio event loop. Long work is bounded by the agent budgets (AGENT_ARCHITECTURE, PR-M3), not by process isolation.

Module boundaries are enforced in CI by **import-linter** using the dependency rules in ARCHITECTURE.md §5.2. They cover these concerns:
- business APIs;
- KPI semantics;
- query execution;
- agent orchestration;
- analytical tools;
- evidence verification;
- AG-UI streaming;
- GenUI validation;
- proactive intelligence;
- authentication and authorization;
- persistence;
- observability.

No microservice, message broker, cache server or background worker is introduced:
- Redis is excluded by DR-029.
- Insight evaluation is a replay command, not a scheduler (DR-005).

## Options considered

| Option | Summary | Outcome |
|---|---|---|
| A | Modular monolith, agent in-process, boundaries enforced in code | **Approved (ED-02 A)** |
| B | Separate api and agent services over internal HTTP (TA §11) | Not chosen |

## Consequences

- One process to trace, authorize and stream from.
- The agent could be split out later without changing a contract, because modules talk only through their public interfaces (ARCHITECTURE.md §5).
- A CPU-heavy or blocking call inside the agent would stall the event loop. Mitigations:
  - database calls are async (psycopg 3 async);
  - any CPU-bound step uses `asyncio.to_thread`;
  - per-run budgets cap wall-clock time.

## Verification

AT-M0-T03-04: import-linter passes on the module skeleton, and a deliberate forbidden import fails it (negative test). The check is part of GATE-M0-03.
