# Open issues and risk register

## Open issues

These are open items that are not decisions. The twelve decisions (GDQ-01 to GDQ-12) are on the Design review report tab. “Architect” means me during specification writing; “Developer” means the person implementing with Cursor Composer.

| ID | Issue | Source | Owner | Closed by | Blocks |
| --- | --- | --- | --- | --- | --- |
| OI-01 | Real ECharts rendering of the DX3 gallery is unverified here; the sandbox cannot reach cdnjs or npm | DX3; trace PAR-A03…T04 | You (GDQ-06) | Self-test result, or the M2 exit gate | Final DR-007 |
| OI-02 | axe-core and screen-reader checks have only run as structural smoke checks | GUI-06, NFR-02 | Developer | M4 exit gate on the real build | Nothing before M4 |
| OI-03 | Gauge arc fidelity for pending approvals needs a real render | PAR-A06 | Developer | M2 exit gate | Nothing before M2 |
| OI-04 | DX2 drilldown record fixtures are random, so the row form does not equal the card total (C21) | KPI tab; PAR-X03 | Architect | Seed manifest in SYNTHETIC\_DATA\_STRATEGY.md; records generated from cohorts | M2 drilldown tests |
| OI-05 | The eight dashboard caveats need named exposing rows in the seed | MET-04 | Architect | Seed manifest | KPI\_CATALOG.md sign-off |
| OI-06 | Technical Architecture §5.3 scenarios are not yet mapped to S1–S9 and N1–N11 | DATA-04/05 | Architect | Scenario manifest | M1 plan |
| OI-07 | No clarification journey was designed; only the clarification state exists | L4-CLAR | Architect | AGENT\_ARCHITECTURE.md: policy plus 3 golden dialogues | M3 plan |
| OI-08 | Business-impact answers are limited because no revenue or rent metric exists | L4-BIZ | Architect | KPI\_CATALOG.md unavailable-concept entry and agent wording | Nothing |
| OI-09 | The 150-question benchmark is not yet written | EVAL-01–06 | Architect, then developer | EVALUATION\_PLAN.md (20 seed questions per category), completed in M5 | M5 |
| OI-10 | Secret-scanning of logs and events has no test yet | SEC-06/07 | Architect | M3 test card | M3 exit |
| OI-11 | Latency targets are specified but unmeasured | NFR-01 | Developer | M5 performance run | M5 exit |
| OI-12 | The AG-UI SDK version and event names are unchecked against the pinned release | AGUI-01/02 | Developer (GDQ-11) | M0 spike or M4 | AGUI\_INTEGRATION.md final |
| OI-13 | The DX5 GenUI board wording change (“overdue” removed) is saved locally but not republished to the canvas | DX6 refinement 1 | Architect | Next canvas publish | Nothing |
| OI-14 | KPI\_CATALOG.md and the metric YAML do not exist yet; design notes are their only source | MET-02/03 | Architect | Specification phase, document 3 | M1 and M2 |
| OI-15 | The prospective-tenant journey is deferred | PAR-T08 | You | Post-POC backlog | Nothing |

## Risk register

L and I are likelihood and impact (H high, M medium, L low). The top three are R-01, R-02 and R-04.

| ID | Risk | L | I | Mitigation | Early signal |
| --- | --- | --- | --- | --- | --- |
| R-01 | The approved scope does not fit five days and is squeezed instead of sequenced | H | H | GDQ-01 Option A; slice task cards marked in each plan; no new design during the build | Day 2 exit check missed |
| R-02 | Seed and metric numbers drift from the canonical figures and goldens | M | H | GI invariants in CI; replay hash; micro fixtures per metric; seed version in every evidence record | Any GI check failing |
| R-03 | Real ECharts output differs from the DX3 model (gauge arcs, treemap labels, heatmap density) | M | M | GDQ-06 self-test; HTML fallbacks already designed for funnel and treemap; the M2 gate | Self-test thresholds missed |
| R-04 | The LLM produces ungrounded numbers or causal wording | M | H | Fact tokens; the verifier rejects any number without a source; banned-term lint (“overdue”, causal verbs); benchmark scoring | Verifier rejection rate above 5% |
| R-05 | The AG-UI SDK changes events or state semantics | M | M | Pin the version; a 2–3 h spike (GDQ-11); keep an adapter layer in cenomi\_agui | Spike fails |
| R-06 | A tenant sees another tenant’s data through the agent, an insight or a shared summary | L | H | AccessScope on every query; uniform refusals; K7, K11 and J8/J10 tests; scope re-checked on every read | Any authorization test failing |
| R-07 | Proactive detectors are noisy or miss the planted scenarios | M | M | detectors-1.1 thresholds versioned and recorded in evidence; N1–N11 counterexamples; replay before release | A counterexample fires |
| R-08 | Runner duplicates notifications or publishes partial runs | L | M | run\_key, claim leases, one-transaction publish, outbox key; tests R1–R13 | Duplicate outbox rows |
| R-09 | Composer makes architectural choices where specifications are thin | M | M | Cursor-ready criteria per document; .cursor/rules; task cards with acceptance tests; review per milestone | PR touches files outside its card |
| R-10 | Agent latency is too high for interactive use | M | M | Budgets per state; cached metric results by scope and data version; two candidate models (GDQ-12) | p95 above the NFR-01 target in M3 |
| R-11 | GenUI validator rejects too many payloads and answers fall back to text | M | L | Server-side composition from validated results; fallback to table; fixtures per kind | Fallback rate above 10% |
| R-12 | Readers mistake the synthetic data for real Cenomi figures | L | M | Synthetic marking on every screen and export (DATA-06/07) | Missing banner in a screenshot |
| R-13 | Late design changes reopen approved decisions | M | M | This gate freezes the register; changes go through STATUS.md with an ADR | New ADR during the build week |
| R-14 | One developer is a single point of failure | M | H | Specifications and task cards complete before day 1; Option C if a second developer is available | Any day lost |
