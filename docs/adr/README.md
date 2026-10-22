# Architecture Decision Records

ADRs record engineering decisions that are not already fixed by a DR or DXD entry in the design baseline. An ADR cites the decision IDs it rests on rather than restating them. Process: [ADR-0001](0001-record-architecture-decisions.md).

**Status values.**

| Status | Meaning |
|---|---|
| Proposed | Written in a specification PR. If the underlying decision (ED, D or GDQ) is already approved, the ADR says so; the ADR text itself becomes Accepted when its PR merges |
| Accepted | Merged by the project owner |
| Superseded | Replaced by a later ADR, which is named. Never deleted |
| Rejected | Kept with the reason |

## Index

| ADR | Title | Rests on | Status | PR |
|---|---|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions; specifications delivered by pull request | ED-01 (approved 2026-10-22); supersedes DR-035 | Proposed — decision approved | PR-M0 |
| [0002](0002-repository-structure-and-sources-of-truth.md) | Repository structure, single sources of truth and slice planning | DR-034 (docs part superseded), ED-03 (approved, scope unchanged), ED-04 (approved) | Proposed — decisions approved | PR-M0 |
| [0003](0003-technology-stack-and-version-pinning.md) | Technology stack and version pinning | DR-027, DR-007, DXD-61; ED-10 (proposed) | Proposed | PR-M0 |
| [0004](0004-contract-pipeline-and-bootstrap-rule.md) | Contract pipeline, bootstrap rule and wire conventions | DR-028 | Proposed | PR-M0 |
| [0005](0005-backend-modular-monolith.md) | Backend as a modular monolith; agent in-process | ED-02 (approved 2026-10-22) | Proposed — decision approved | PR-M0 |
| [0006](0006-database-roles-schemas-and-ownership.md) | Database roles, schemas, `snap` schema and schema ownership | DR-013, DR-021, DR-029; D-01 (approved 2026-10-22) | Proposed — decisions approved | PR-M0 |
| 0007 | Metric registry, SQL templates and the as_of parameter | DR-004, 030, 042 | Reserved | PR-M1 |
| 0008 | AccessScope authorization model | DR-019, 020; DXD-38, 56, 85 | Reserved | PR-M1 |
| 0009 | LLM adapter, primary and fallback, replay provider (conforms to ADR-0017) | DR-014, 015; GDQ-12; ED-08 | Reserved | PR-M3 |
| 0010 | AG-UI version pin and event mapping | DR-016, 017; GDQ-11; ED-10 | Reserved | PR-M4 |
| 0011 | ECharts 5.6.0, verification gate and fallbacks | DR-007; DXD-21, 23, 61; GDQ-06, 07 | Reserved | PR-M2 |
| 0012 | Materialized as-of snapshots | DXD-80; GDQ-03; D-01 | Reserved | PR-M1 |
| 0013 | Insight runner protocol and idempotency | DXD-86 and related | Reserved | PR-M6 |
| 0014 | Evaluation scoring | DR-036; ED-11 | Reserved | PR-M5 |
| [0015](0015-engineering-delivery-workflow-and-ci.md) | Engineering delivery workflow, CI scope and build authorization | ED-05, ED-06 (approved 2026-10-22); delivery model, P1/P2 protection and EXC-001 (conditional) approved 2026-10-22 | Proposed — decisions approved | PR-M0 |
| [0016](0016-poc-sign-in-and-session.md) | POC sign-in: fixture principals and a signed session cookie | ED-07 (approved 2026-10-22) | Proposed — decision approved | PR-M0 |
| [0017](0017-model-determinism-in-tests.md) | Model determinism in tests: mock, replay and controlled live evaluation | ED-08 (approved 2026-10-22) | Proposed — decision approved | PR-M0 |
| [0018](0018-styling-approach.md) | Styling: CSS Modules with generated design-token variables | ED-09 (approved 2026-10-22) | Proposed — decision approved | PR-M0 |

ADR-0015 to ADR-0018 are new. They are numbered after the reserved range so that ADR-0007 to ADR-0014 keep the numbers the approved plan gave them. ED-08's decision is recorded in ADR-0017 now; ADR-0009 keeps its reserved scope (the adapter design) and must conform to it. ED-09's decision is recorded in ADR-0018; the token set stays in DESIGN_SYSTEM (PR-M2).

Template: Title · Status · Date · Decision IDs · Context · Options considered · Decision · Consequences · Verification.
