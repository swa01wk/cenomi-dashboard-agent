# Engineering specification inventory

Coding should start only after 16 documents, 7 milestone plans and 10 kinds of machine-readable artefacts exist. Two documents are new since v0.3: PROACTIVE\_INTELLIGENCE.md, because DX6 is too large for AGENT\_ARCHITECTURE.md, and DESIGN\_SYSTEM.md, which records the DX1–DX3 tokens, states and components. Each document is “Cursor-ready” when Composer can implement from it without making an architectural choice.

## Documents (docs/)

| Order | Document | What it fixes | Design inputs | Cursor-ready when |
| --- | --- | --- | --- | --- |
| 1 | DECISIONS.md + adr/ | The consolidated register and ADR-001…018 | Decision register tab | Every decision has a status and an ADR where needed |
| 2 | PRODUCT\_SPEC.md | Scope freeze, personas, screens, journeys, glossary, out of scope | DX1, DX2; PRD journeys; DXD-01–20 | Every card and journey has acceptance criteria |
| 3 | KPI\_CATALOG.md + metric YAML | Every parity, corrected, derived and new metric with SQL semantics, bands, caveats, parity class; unavailable concepts; numeric policy | DX2 notes, DX3 parity, DXD-80, KPI tab | YAML validates; each metric has a micro-fixture spec |
| 4 | DATABASE\_SCHEMA.md | Tables, enums, constraints, indexes, schemas and grants, as-of history route, ingested\_at | DR-013, 022, 046, 047; DXD-80, 88 | Every column typed, every enum listed |
| 5 | ARCHITECTURE.md | Topology, module map, pinned stack, security model (AccessScope), observability, performance budget, repo layout | Architecture tab; DR-019–021, 027 | Each package has responsibilities, interfaces and forbidden dependencies |
| 6 | API\_CONTRACTS.md + JSON Schemas | Envelope, errors, metric query/result (analysis\_result.v1), card view-models, records paging, insights API | DXD-26, 36, 55–59; DX6 API | Schemas generate TypeScript types and zod |
| 7 | SYNTHETIC\_DATA\_STRATEGY.md | Latent model, lifecycles, scenario manifest (S1–S9, N1–N11, TA §5.3), cohorts, invariants, micro fixtures, reset | DXD-81, 82; KPI tab | Every scenario has machine-checkable assertions |
| 8 | AGENT\_ARCHITECTURE.md | State machine, plan schema, DAG executor, budgets, analytical state, fact tokens, verifier, clarification and impact policy | DX4; DR-031, 032; DXD-31–38 | Transition tables complete; prompt templates versioned |
| 9 | AGENT\_TOOLS.md | Tool schemas, limits, errors, golden examples; get\_linked\_cohort | DX4 tools; GDQ-09 | Every tool has input/output schema and a golden example |
| 10 | AGUI\_INTEGRATION.md | Event mapping, run identity, state shape, CUSTOM payloads, reconnect, frontend tool | DX4-AGUI; DXD-40; GDQ-11 | Sequence diagrams per journey; SDK version pinned |
| 11 | GENERATIVE\_UI.md + component schemas | Registry with the PRD mapping, presentation schema, policy P1–P6, validator, states, sizes, selection | DX5; DXD-41–62; GDQ-02 | Every kind has schema, fallback and a fixture |
| 12 | DESIGN\_SYSTEM.md (new) | Tokens, typography, chart palette roles, state vocabulary, focus and selection styles, responsive rules | DX1–DX3; DXD-01, 07, 16, 19, 24 | Tokens exported; components listed with states |
| 13 | PROACTIVE\_INTELLIGENCE.md (new) | detectors-1.1, scoring, deduplication, lifecycle, privacy, runner protocol, delivery, inbox | DX6 v2; DXD-63–93 | Detector configuration validates; runner tests R1–R13 specified |
| 14 | EVALUATION\_PLAN.md | Test taxonomy, fixture tiers, benchmark composition (150+), scoring (DR-036), thresholds, performance method | DX4–DX6 tests; goldens | Benchmark schema plus 20 seed questions per category |
| 15 | STATUS.md (plans/) | Live status, open decisions, gate results | This gate | — |
| 16 | AGENTS.md (repo root) | Repo map, commands, conventions, where specs live | All | — |

## Milestone plans (plans/)

M0\_FOUNDATION, M1\_DATABASE\_AND\_SEEDING, M2\_KPI\_AND\_DASHBOARD, M3\_AGENT\_RUNTIME, M4\_AGUI\_AND\_GENERATIVE\_UI, M5\_EVALUATION and M6\_PROACTIVE\_INTELLIGENCE. Each follows the project template: objective, scope, assumptions, decisions, requirements, components, data, contracts, data flow, files, dependency graph, task cards, acceptance criteria, tests, risks and definition of done. If GDQ-01 A is chosen, each plan also marks its five-day slice tasks.

## Machine-readable artefacts

| Artefact | Location | Source of truth |
| --- | --- | --- |
| Metric definitions and SQL templates | packages/metrics/definitions/*.yaml, queries/*.sql | YAML validated by a Pydantic model |
| Unavailable concepts | packages/metrics/unavailable\_concepts.yaml | YAML |
| Contracts: selection\_ref.v1, analysis\_result.v1, cenomi.presentation.v1 (+ one schema per kind), insight.v1, evidence envelope | packages/contracts/schemas/\*.json | Generated from Pydantic (DR-028) |
| TypeScript types and zod | packages/contracts/src/generated | Generated; CI drift check |
| Detector configuration | packages/insights/detectors-1.1.yaml | YAML, versioned |
| Scenario manifest and cohorts | data/scenarios/\*.yaml | YAML with assertions |
| Micro fixtures with expected values | tests/fixtures/metrics/\<metric\_id>/ | Hand-authored |
| Benchmark questions | tests/agent-evals/benchmark/\*.yaml | Hand-authored |
| AG-UI event fixtures | tests/agui/fixtures/\*.jsonl | Recorded and reviewed |
| Design tokens | packages/viz/tokens.json | From DESIGN\_SYSTEM.md |

## Cursor enablement

- `.cursor/rules/*.mdc`: no arithmetic in prompts or text; no SQL outside packages/metrics/queries; every query carries the scope fragment; never trust client context for authorization; no raw HTML from model output; contracts are generated; every task ships its tests; “overdue” never appears in generated text.
- Task cards inside each plan, each sized for one Composer session: goal, files, contracts referenced, steps, acceptance tests, out of scope, done checklist.

**Writing order:** documents 1–7 first (they unblock M1 and M2), then 8–13, then 14 and the plans. Under GDQ-01 A, the five-day slice needs documents 1–6, 8, 10, 11 and 13 complete, plus slice task cards in M0–M4 and M6.
