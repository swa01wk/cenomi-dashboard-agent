# Single sources of truth

Every concern has exactly one canonical source. Everything else is generated from it, or cites it by path. CI regenerates each derived artefact and fails on any difference, so a hand edit in the wrong place cannot survive a PR.

| Concern | Canonical source | Derived from it (committed, GENERATED) | Consumers | CI guard |
| --- | --- | --- | --- | --- |
| Database schema | backend/src/cenomi/db/tables.py (SQLAlchemy Core metadata). Until M1 is built, DATABASE\_SCHEMA.md is normative | Alembic migrations (reviewed); docs/architecture/generated/schema.md | Executor, seed, migrations | `alembic check` shows no pending diff; migrate-from-empty test; schema doc drift |
| Metric meaning | specs/metrics/\<metric\_id>.yaml | KPI\_CATALOG.md tables; the metric list in the tool catalogue | Registry loader (dashboards, tools, detectors), seed verify | YAML schema validation; every metric has a SQL template and a micro fixture |
| Metric calculation | backend/src/cenomi/analytics/queries/\<metric\_id>.sql, run only by the executor | — | Dashboard API, agent tools, detectors, snapshot reconciliation | Golden metric tests; scope-fragment lint; no-SQL-elsewhere lint |
| Expected values | tests/fixtures/golden/ (canonical\_figures.yaml, metrics/\<metric\_id>/\*) | — | Golden tests, benchmark cases, E2E assertions | Tests read the files; no expected number appears as a literal in test code |
| Analytical results | Pydantic AnalysisResult in cenomi/contracts | specs/contracts/analysis\_result.v1.schema.json; TS and zod in packages/contracts-ts | API, tools, agent, presentation, web | Contract drift check |
| Tool schemas | Pydantic input and output models per tool in cenomi/agent/tools | specs/contracts/tools/\*.schema.json; the tool catalogue sent to the model | Planner, DAG executor, evaluation | Drift check; every tool has a golden example in tests/fixtures/tools |
| AG-UI events | Standard events: the pinned AG-UI 1.0 SDK types. Cenomi payloads (CUSTOM cenomi.presentation.v1, activity plan, state shape): Pydantic | Payload schemas; recorded streams in tests/fixtures/agui/\*.jsonl | api AG-UI endpoint, web client hooks | Every recorded stream validates against both SDKs and the payload schemas |
| Component payloads | Pydantic presentation models (one discriminated union member per kind); allowlist, variants and fallbacks in specs/genui/registry.yaml; rules in specs/genui/composition\_policy.yaml | Per-kind schemas and zod | Composer, server validator, client renderer | Registry and union agree (test); every kind fixture validates; unknown kinds are refused |
| Authorization | specs/authorization/permissions.yaml (roles, permissions, card and endpoint mapping, scope kinds); fixture principals in tests/fixtures/principals.yaml | Permission table in ARCHITECTURE.md | AccessScope only | Every route declares a permission (test); isolation suite |
| Detector configuration | specs/detectors/detectors-1.1.yaml | Thresholds quoted in evidence records | Detectors, insight evidence | Config validation; the replay hash changes only with a new config version |
| Scenarios and cohorts | specs/scenarios/ | Seed manifest report | Seed generator, golden tests | Scenario assertion tests |
| Design tokens | specs/design/tokens.json | CSS variables; TS constants | packages/viz, apps/web | Token drift check |
| Decisions | docs/adr/ and docs/design/DECISION\_REGISTER.md | ADR index | Every spec (cites IDs) | ADR index regenerated |

## Contract bootstrap rule

DR-028 makes Pydantic the source of every contract, but no code exists while the specifications are written. So each contract is first authored by hand as its JSON Schema in specs/contracts. When the milestone is built, the Pydantic model must export exactly that schema (normalized comparison in CI). From then on the Pydantic model is the only place to edit, and the schema file is regenerated. ADR-0004 records this.

## Versioning

- Contract files carry their major version in the name (analysis\_result.v1). A breaking change creates v2 alongside v1, under a CR. An optional field may be added to v1 under a CR.
- Metric definitions carry a version; a change in semantics creates a new version, and evidence records which version produced each number.
- The dataset is identified by its ID (sd-2026.10.20-01) and seed hash. Any change to the generator that changes the hash is a CR and updates the golden fixtures in the same PR.
