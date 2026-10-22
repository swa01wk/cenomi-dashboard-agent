# 4 · Engineering specification inventory

The specifications are 17 documents (including AGENTS.md), 10 plan files and a set of machine-readable specs, plus the ADRs. They are delivered as seven milestone PRs. The first six (M0, M1, M2, M3, M4, M6) must be merged before slice day 1. The M5 PR can follow during or after the slice, because the slice’s 20 benchmark questions use the evaluation case schema that ships with M3.

**Cursor-ready**, for every document, means: no TBD in a normative section; every interface typed and versioned; every requirement carries an acceptance test ID; open questions are listed separately and none blocks implementation; and every design reference points to a frozen artifact version.

## PR-M0 · Foundation (writing order 1–12)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 1 | docs/adr/0001–0006 | ADR process, repo and sources of truth, stack, contract pipeline, backend topology, DB roles and schemas | DR-013, 021, 027, 028, 029, 034; ED-01–03 | Each ADR has context, decision, consequences and status | M |
| 2 | docs/reference/ | Frozen copies of PRD, TA, API Reference; exports of the GD doc and reconciliation | Authoritative documents 1–3, 5–7 | Files byte-identical to sources, README lists versions | S |
| 3 | docs/design/DESIGN\_BASELINE.md | Index of DX1–DX6 boards, canvas version 27, screenshots per board, what each board is normative for | DX1–DX6 | Every board referenced by a later spec has an entry | S |
| 4 | docs/design/DECISION\_REGISTER.md | The 141 decisions with 22 Oct statuses and final definitions | GD register | Statuses match the GD doc | M |
| 5 | docs/product/PRODUCT\_SPEC.md | Scope freeze, personas and roles, screens, card inventory, journeys index (J, K, E2E), glossary, out of scope | PRD; DX1, DX2; DXD-01–20 | Every card and journey has acceptance criteria and a test ID | L |
| 6 | docs/architecture/ARCHITECTURE.md | Runtime processes and boundaries, module map with forbidden dependencies, security model (AccessScope, roles, uniform refusals), observability, performance budgets | GD architecture tab; DR-019–021 | Each module lists responsibility, public interface and forbidden imports | L |
| 7 | docs/architecture/DEVELOPMENT\_ENVIRONMENT.md | Compose services, env catalogue, make targets, DB init, seed entry points, test commands, CI jobs | DR-037; Local development tab | A clean clone can be brought up from the document alone | M |
| 8 | specs/contracts (bootstrap) | error\_envelope, principal, scope\_decision schemas | DR-020, 028 | Schemas validate their examples | S |
| 9 | AGENTS.md and .cursor/rules | Repo map, commands, where specs live, coding rules (tab 5) | All | Each rule is testable or lintable | S |
| 10 | plans/ROADMAP.md | This plan’s milestones, freezes and timeline | Tabs 1–3 | Matches tab 1 | S |
| 11 | plans/M0\_FOUNDATION.md | M0 task cards T01–T10 with acceptance tests | Tab 6 | Each card fits one Composer session | M |
| 12 | plans/STATUS.md | Live status (ADR and STATUS tab) | — | Template filled | S |

## PR-M1 · Data and semantics (13–21)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 13 | docs/architecture/DATABASE\_SCHEMA.md | Tables, columns, enums, keys, indexes, grains, lineage (DR-022), schemas and grants, snapshot tables, ingested\_at | DR-013, 022, 046, 047; DXD-80, 88 | Every column typed, every enum listed, every index justified by a query | L |
| 14 | specs/metrics/\*.yaml + unavailable\_concepts.yaml + relationships.yaml | Every metric’s population, filters, measure, bands, time basis, null policy, kind, parity class, caveats, version | DX2 notes, DX3 parity, DXD-80, KPI tab | YAML validates against the metric schema; each metric names its micro fixture | L |
| 15 | docs/contracts/KPI\_CATALOG.md | Generated tables from the YAML plus hand-written semantics, caveats and parity notes | Item 14 | Generator output committed; no value restated by hand | M |
| 16 | specs/authorization/permissions.yaml | Roles, permissions, card ↔ permission, scope kinds, fixture principals | DR-019, 020; DXD-38, 56, 85 | Every card and endpoint maps to one permission | S |
| 17 | docs/architecture/SYNTHETIC\_DATA\_STRATEGY.md | Latent model, lifecycles, volumes, seasonality, missing data, reset, determinism | DR-033, 043; DXD-81, 82 | Every generator rule has a property test named | L |
| 18 | specs/scenarios/\*.yaml | S1–S9, N1–N11, TA §5.3 mapping, golden cohorts with assertions | DX6; KPI tab | Every scenario has machine-checkable assertions | M |
| 19 | tests/fixtures/golden/canonical\_figures.yaml + micro-fixture specs | Expected values for sd-2026.10.20-01; micro fixtures for the slice metrics | KPI tab; Golden data tab | Each value cites its metric, scope and as\_of | M |
| 20 | docs/adr/0007, 0008, 0012 | Metric registry and as\_of parameter; AccessScope; snapshot materialization | DR-004, 030; GDQ-03 | Accepted | S |
| 21 | plans/M1\_DATA.md | Task cards, slice cards tagged | Tab 3 | — | M |

## PR-M2 · Analytics API and dashboards (22–26)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 22 | docs/contracts/API\_CONTRACTS.md + specs/contracts | metric\_query, analysis\_result.v1 (with calc records and coverage), card view-models, filter options, records page, selection\_ref.v1, errors | DXD-26, 36, 55–59 | Schemas generate TS and zod; every endpoint has request, response and error examples | L |
| 23 | docs/design/DESIGN\_SYSTEM.md + specs/design/tokens.json | Tokens, type, palette roles, state vocabulary, focus and selection, responsive rules, HTML visuals | DX1–DX3; DXD-01, 07, 16, 19, 24; DR-008 | Tokens export to CSS variables; every component lists its states | M |
| 24 | Card specifications (in PRODUCT\_SPEC appendix) | Per card: metrics, filters, chart primitive, interactions, empty and error states, drilldown | DX2, DX3; API Reference | Each card has a parity test and a records-total test | M |
| 25 | docs/adr/0011 | ECharts 5.6.0 pin, verification gate, fallbacks | DR-007; DXD-21, 23, 61; GDQ-06, 07 | Accepted | S |
| 26 | plans/M2\_METRICS\_AND\_DASHBOARDS.md | Task cards | Tab 3 | — | M |

## PR-M3 · Agent runtime (27–31)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 27 | docs/architecture/AGENT\_ARCHITECTURE.md | State and transition tables, AnalysisPlan, validator rules, DAG executor, budgets, analytical state, fact tokens, verifier, clarification, history and resume, prompt templates (versioned) | DX4; DR-031, 032; DXD-31–38 | Transition table complete; every prompt template versioned and tested | L |
| 28 | docs/contracts/AGENT\_TOOLS.md + tool schemas + tests/fixtures/tools | All tool schemas, limits, errors, golden examples; get\_linked\_cohort | DX4 tools; GDQ-09 | Every tool has input and output schema and one golden example | M |
| 29 | Evaluation case schema v1 + 20 slice questions | Case format with deterministic expectations only | DX4–DX6 tests | Each case validates; expected facts cite canonical figures | S |
| 30 | docs/adr/0009 | LLM adapter, primary and fallback, replay provider | DR-014, 015; GDQ-12 | Accepted | S |
| 31 | plans/M3\_AGENT\_RUNTIME.md | Task cards | Tab 3 | — | M |

## PR-M4 · AG-UI and generative UI (32–35)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 32 | docs/architecture/AGUI\_INTEGRATION.md + event fixture specs | Event mapping on AG-UI 1.0, run identity, state shape, CUSTOM payloads, frontend tool, reconnect, cancellation | DX4-AGUI; DR-016, 017; DXD-40; spike report | Sequence diagram per journey; SDK versions pinned | M |
| 33 | docs/design/GENERATIVE\_UI.md + specs/genui + presentation schemas | Registry (15 kinds plus GDQ-02 variants), composition policy P1–P6, validator, states, sizes, View as | DX5; DXD-41–62; GDQ-02 | Every kind has schema, fallback and fixture | L |
| 34 | docs/adr/0010 | AG-UI 1.0 pin and mapping | ED-10 | Accepted | S |
| 35 | plans/M4\_AGUI\_AND\_GENUI.md | Task cards | Tab 3 | — | M |

## PR-M6 · Proactive intelligence and the slice plan (36–40)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 36 | docs/architecture/PROACTIVE\_INTELLIGENCE.md | Detectors, scoring, dedup, lifecycle, privacy, runner protocol, delivery, inbox, feedback ordering | DX6 v2; DXD-63–93; GDQ-05, 08 | Runner tests R1–R13 and K1–K12 specified | L |
| 37 | specs/detectors/detectors-1.1.yaml + insight.v1 schema | Thresholds and versions; insight contract | DX6 | Configuration validates; thresholds recorded in evidence | S |
| 38 | tests/fixtures/insights (full and slice replay goldens) | Expected insights, versions and hashes | DX6 replay | Hashes reproducible | S |
| 39 | docs/adr/0013 | Runner protocol and idempotency | DXD-86 | Accepted | S |
| 40 | plans/M6\_PROACTIVE\_INTELLIGENCE.md + plans/SLICE\_FIVE\_DAY.md | Task cards; slice ordering across M0–M4, M6 | Tab 2 | Every slice card exists in its milestone plan | M |

## PR-M5 · Evaluation (41–43)

| # | Path | Fixes | Design inputs | Cursor-ready when | Size |
| --- | --- | --- | --- | --- | --- |
| 41 | docs/architecture/EVALUATION\_PLAN.md | Test taxonomy, fixture tiers, benchmark composition (150+), scoring, thresholds, performance method | DR-036; Golden data tab | Thresholds numeric; scoring reproducible | M |
| 42 | tests/agent-evals/benchmark | 20 seed cases per category | EVAL-01–06 | Cases validate | M |
| 43 | docs/adr/0014 + plans/M5\_EVALUATION.md | Scoring decision; task cards | DR-036 | Accepted | S |

## Review loop per PR

1. I draft the PR’s files and check each against the PRD traceability rows and the decision register.
2. The PR (or file set, per ED-01) goes to you with a checklist: scope unchanged, decisions cited, Cursor-ready criteria met, open questions listed.
3. You comment; I revise in the same PR.
4. You approve and merge. I update STATUS.md, and the PR’s contract freeze takes effect.

I may draft the next PR while you review the current one; the next PR is opened only after the current one is merged.
