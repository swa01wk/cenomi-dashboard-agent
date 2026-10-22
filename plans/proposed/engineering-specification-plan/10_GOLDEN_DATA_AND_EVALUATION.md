# Golden data and evaluation cases

Correctness is proven at six tiers, from hand-checked rows up to full journeys. Every tier reads its expected values from tests/fixtures, never from literals in test code. The acceptance reference is dataset sd-2026.10.20-01 with as\_of 2026-10-20.

## Fixture tiers

| Tier | What it proves | Location | Written in | First needed |
| --- | --- | --- | --- | --- |
| T0 Micro fixtures | Each metric’s SQL on a few hand-built rows, including every boundary and caveat | tests/fixtures/metrics/\<metric\_id>/{rows.yaml, expected.json} | PR-M1 (slice metrics), M2 cards (rest) | Slice day 2 |
| T1 Golden figures and invariants | The macro seed reproduces the canonical figures and GI invariants 51/51 | tests/fixtures/golden/canonical\_figures.yaml, invariants.yaml | PR-M1 | Slice day 2 |
| T2 Scenario assertions | S1–S9 signals present, N1–N11 counterexamples present, TA §5.3 cases mapped | specs/scenarios/ | PR-M1 | M1 gate |
| T3 Analytical cases | Agent answers: facts, tools, components, labels, refusals | tests/agent-evals/{slice, benchmark}/\*.yaml | PR-M3 (schema + 20), PR-M5 (150+) | Slice day 5 |
| T4 Detector and runner cases | Detector rules, replay goldens, runner idempotency | tests/fixtures/insights/, backend/tests/insights | PR-M6 | Slice day 5 |
| T5 End-to-end journeys | Screens, AG-UI, GenUI and isolation together | tests/e2e/ | Each milestone PR | Slice day 5 |

## Canonical figures (T1 acceptance reference)

| Item | Expected | Metric |
| --- | --- | --- |
| All-regions approvals | 232 pending; 92 waiting 31+ days | approvals.pending\_by\_delay v1 |
| Central approvals | 130 pending; 62 waiting 31+ | approvals.pending\_by\_delay v1 |
| Rawdah Point Mall approvals | 71 pending (proposals 32, contracts 23, leases 16); 41 waiting 31+ (19, 15, 7) = 66.1% of Central’s 62 and 57.7% of Rawdah’s pending | approvals.pending\_by\_delay v1 |
| Central amendments 4 wk+ | 25 all types; renewals 18 (Rawdah 9, Sandstone 6, Qasr 3); oldest 171 days | amendments.pending\_by\_age\_band v1 |
| Unit discrepancy | 18 of 25 malls reported; 87 of 3,000 units mismatched = 2.9%; Gulf Gate 11 of 142 = 7.7%, robust z 15.9 | unit\_discrepancy.units v1 |
| Vacancy | Central 408 of 3,420; all regions 1,026 of 8,140 = 12.6%; Mirage Commons 58 of 299 = 19.4% | units.vacant v1 |
| Tenant T-31206 (Lumen Home) | SAR 2,424,000 Jan–Sep; September SAR 241,800, +7.5% year on year; 2 documents to upload; 0 service requests in Action required (the company has 2) | tenant\_sales.reported\_monthly v1, tenant\_action\_items.open v1 |
| As-of snapshots | Each .asof metric at 2026-10-20 equals its parity metric for every mall and region (GDQ-03) | approvals.pending\_by\_delay.asof, amendments.pending\_by\_age\_band.asof, units.vacant.asof |

## Expected SQL outputs (T0 and T1)

Each metric gets one expected-output file per canonical scope: portfolio, each region, the golden malls and the golden lease. The file records the inputs and the full result, not only the headline number.

```json
{
  "metric": "approvals.pending_by_delay", "version": 1,
  "dataset": "sd-2026.10.20-01", "as_of": "2026-10-20",
  "scope": {"region": "Central", "mall": "Rawdah Point Mall"},
  "rows": [{"type": "proposal", "band": "31+", "count": 19}],
  "totals": {"pending": 71, "waiting_31_plus": 41},
  "coverage": {"status": "complete"}
}
```

Boundary cases every approvals micro fixture must hold: ages of 6, 7, 13, 14, 20, 21, 30 and 31 days at as\_of in Asia/Riyadh; proposals aged from pms\_created\_at, contracts and leases from pms\_last\_modified\_at; future and NULL timestamps dropped; an empty scope returns an empty result. Amendments add the 28-day boundary and the parity rule that future-dated rows count as 4 wk+.

## Analytical cases (T3)

```yaml
id: S-AI02-003
category: AI-02            # retrieve with inherited filters
persona: central_manager
context:
  filters: {region: Central}
  selection_ref: {card: pending_approvals, mall: Rawdah Point Mall}
question: How many of these are waiting 31+ days, and what share of Central is that?
expect:
  facts:
    - {metric: approvals.pending_by_delay, scope: {mall: Rawdah Point Mall}, band: "31+", value: 41}
    - {derived: share, value: 66.1, unit: percent, decimals: 1}
  tools_include: [get_metric, derive]
  kinds_include: [kpi, bar]
  labels: [Observed, Derived]
  forbid_terms: [overdue]
  forbid_untraced_numbers: true
  authorization: allowed
```

The slice’s 20 cases: AI-01 explain (2), AI-02 retrieve (4), AI-03 derive (3), AI-04 compare (2), AI-06 follow-up context (2), AI-07 statement labels (1), AI-08 unavailable or partial (2), AI-09 provenance (1), AI-10 isolation (3). The M5 benchmark extends every EVAL and L3/L4 category to 150+ cases, with scoring under DR-036.

## Detector and runner cases (T4)

| Group | Cases | Expected |
| --- | --- | --- |
| Detector rules on micro series | D1 share, value and parent limits; D2 window, increases, no decrease, net and 10% rules; D3 decreases; D4a and D4b; D5 90% and 80% coverage; D7 13-month history; D8 7- and 14-day urgency | Fires exactly at the configured boundary and not one step before |
| Slice replay | D2 and D8 only, checkpoints to 2026-10-20 | INS-101 and T-202 with their versions; slice hash recorded |
| Full replay | detectors-1.1, all checkpoints | INS-107, T-202, INS-105, INS-105C, INS-104, INS-106, INS-103, INS-101 (merged, 7 versions), INS-090 (resolved 22 Sep); hash equals the DX6 replay\_hash |
| Scenarios | S1–S9 and N1–N11 | Signals fire; counterexamples stay quiet |
| Runner | R1–R13 plus duplicated triggers, concurrent evaluations, crash recovery, role changes, insight-version changes, notification suppression, private threads, stale evidence | One publish per run\_key; one notification per insight version and recipient; no later checkpoint overwritten |

## End-to-end journeys (T5)

E2E-S1 to E2E-S3 (slice); DX4 J1–J10; DX5 View as and table fallback; DX6 K1–K12; one parity journey per dashboard card (card total equals records total). Every journey runs in CI on the replay provider; the live-model run is manual (ED-08).
