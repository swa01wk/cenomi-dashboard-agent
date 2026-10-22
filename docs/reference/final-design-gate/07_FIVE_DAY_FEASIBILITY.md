# Five-day implementation feasibility

## Full scope against five days

**Verdict:** the full approved scope does not fit in five working days. It is about 166 focused hours. One developer working with Cursor Composer has about 40–50 productive hours in five days. Even the reduced core from DXD-74, together with the D8 amendment, is about 100 hours.

The estimates assume that the specifications listed in the previous tab are complete before day 1, so Composer implements rather than designs. They include writing tests, but not rework caused by design changes made during the week.

| Workstream | Full scope (h) | Reduced core (h) | Five-day slice (h) | What the slice keeps |
| --- | --- | --- | --- | --- |
| Foundation: repo, CI, Docker, contracts generation | 6 | 6 | 4 | Monorepo, Postgres container, generated types |
| Schema and migrations | 6 | 6 | (in seed) | Tables the slice needs only |
| Seed, scenarios, golden cohorts | 16 | 12 | 8 | Central region, S1/S2/S4 cohorts, GI invariants |
| Metric engine and catalog | 12 | 10 | 4 | 6 metrics: approvals, amendments, vacancy, unit discrepancy, coverage, tenant actions |
| Admin dashboard (12 cards) | 16 | 12 | 5 | 4 cards: approvals, amendments, unit discrepancy, properties |
| Tenant dashboard | 8 | 6 | (D8 only) | Action required list for T-31206 |
| Agent tools | 8 | 6 | 3 | describe, get\_metric, compare, get\_records, derive |
| Agent runtime: state machine, DAG, verifier | 16 | 12 | 8 | Linear plans of up to 3 steps, verifier, fact tokens |
| AG-UI integration | 6 | 5 | 3 | Run stream, state sync, chart selection to agent |
| Generative UI registry and validator | 20 | 10 | 5 | 5 kinds: kpi, bar, table, insight, unavailable |
| Proactive intelligence | 28.5 | 16.5 | 6 | D2 and D8, a manually triggered runner, inbox list and detail |
| Evaluation and tests | 14 | 8 | 3 | Golden metric tests, 20 benchmark questions, 3 E2E journeys |
| Integration and hardening | 10 | 6 | (spread) | — |
| **Total** | **166.5** | **\~101.5** | **\~49** |  |

## Options

| Option | What happens | Five-day outcome | Full scope reached | Trade-off |
| --- | --- | --- | --- | --- |
| **A — Vertical slice, then continue (recommended)** | Days 1–5 build one thin end-to-end path through every layer. Remaining scope follows in about 15 more working days | A demonstrable slice: chart → agent → validated GenUI answer → proactive insight, all on one metric service | About 20 working days | Nothing is cut from the design; the full demo comes later |
| B — Cut scope permanently | Freeze the POC at the slice | Same as A | Never | Loses L4 breadth, D1/D5/D6, most parity cards and most of the evaluation suite |
| C — Two developers in parallel | Split data and metrics from agent and UI after day 1 | Reduced core in about 10–12 days | About 12–14 days | Contract-first discipline required; integration risk on days 3–4 |

**Preconditions for any option:** the specification documents are complete and approved; an LLM API key and model choice are fixed (GDQ-12); real ECharts rendering is checked on day 1 (GDQ-06); no new design work starts during the build.

## What five days can deliver

Under Option A, each day ends with an exit check that uses the canonical figures, so a failed day is visible at once rather than at the demo.

*(The embedded slice diagram in the original doc is superseded by the day plan in the Engineering Specification Plan: see [`plans/proposed/engineering-specification-plan/diagram_five_day_slice.png`](../../../plans/proposed/engineering-specification-plan/diagram_five_day_slice.png).)*

The slice proves the riskiest design claims: one metric service feeds both the charts and the agent; the LLM never computes a number; GenUI payloads are validated; a chart selection scopes the conversation; and a proactive insight carries its evidence. It does not prove breadth: 8 of the 12 admin cards, most of the tenant dashboard, D1 and D3–D7, the DAG executor's parallel branches, and the 150-question benchmark follow in the remaining 15 or so working days.

If day 2's exit check fails, the plan stops and the seed or metric definitions are fixed before any agent work starts. Everything after day 2 depends on those numbers.

Correction (22 Oct): the day-5 check names INS-101, the D2 insight on Rawdah approvals waiting 31+ days. The slice has no D6, so INS-101 is not merged into INS-107 as it is in the full replay.
