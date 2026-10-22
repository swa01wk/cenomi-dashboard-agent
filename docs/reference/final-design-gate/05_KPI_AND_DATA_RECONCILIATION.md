# KPI and synthetic data reconciliation

All 12 Admin cards and the Tenant card groups keep the V2 business semantics from the API Reference: status sets, denominators, bands and chart forms. Every intentional difference is a security fix, a determinism fix or a time-zone normalization under DR-001/002/006, and is shown on the card. Chart fidelity is “exact” or “close” for all 15 visuals, but only on a test double: none has run on real ECharts yet.

## Dashboard parity against the V2 references

| Card | V2 semantics kept | Intentional difference (basis) | Chart parity (DX3) | ECharts run |
| --- | --- | --- | --- | --- |
| Properties | Three tiles, occupancy meter by units, 1-decimal % | All-region admins see totals (V2 returned empty) · DR-001, DR-020 | Exact (HTML) | Not needed |
| KPI tiles | Expiring, active with grace and superseded, pending-sales status set | Overlap and pending-set caveats shown · DR-002 | Exact (HTML) | Not needed |
| Lease requests | Donut, unit type / source switch, top 4 + Other, year | Shares use the displayed total (legacy bug fixed) · DR-001 | Exact | Pending |
| Sales funnel | Four-stage flow, live counts, signed/unsigned lists, 4 filters | “Other statuses” line; one Riyadh calendar; mall filter intersected with access · DR-006, 008, 018 | Exact (HTML) | Not needed |
| Action required | Latest three unread, badge, type pills | Deterministic latest row per group · DR-001 | Exact (HTML) | Not needed |
| Pending approvals | Three half gauges, bands 0–6 … 31+, captions, 90% banner, region/mall | Band counts printed; server aggregation; explained empty scope · DR-020 | Close (arc and caps to compare) | Pending |
| Pending amendments | Type × week heatmap, rows oldest first, quintile shading, future-dated in 4 wk+ | Riyadh year/month (V2 mixed UTC) · DR-006 | Exact | Pending |
| Service requests | Treemap Inquiry / Work permits / Complaints, tile = approved + in process + rejected, permit strip | Lease-less requests counted; case-insensitive region; drilldown reconciles · DR-001 | Close (tile positions differ) | Required (or HTML fallback, GDQ-07) |
| Fit-out and handover | Four rings, ring = reviewed ÷ (received + remaining + reviewed), callout | Zero denominator shows a dash; insights use active-only rows · DR-002 | Close | Pending |
| Fit-out drawings | Stacked bars per discipline | “Approved includes rejected” stated · DR-002 | Exact | Pending |
| Drawing document status | Stacked A–D by mall, discipline switch, chart ↔ table | One mall hierarchy across fit-out cards · DR-047 | Close | Pending |
| Unit discrepancy | Diverging bars, latest report per mall per month, pending only in totals | Riyadh months (V2 UTC); shared scale · DR-006 | Exact | Pending |
| Tenant overview tiles | Leases, units, brands, documents, open requests, sales, requests, profile, payments | All tiles limited to permitted leases; server-side open count; payments Unavailable · DR-019, 020 | Exact (HTML) | Not needed |
| Tenant reported sales | Monthly columns, submitted + approved, month of period end | Excluded submissions named · DR-001 | Exact | Pending |
| Tenant service requests | Donut by status, treemap by category | No 200-row truncation · DR-001 | Close | Pending / Required |
| Tenant documents, events, opportunities | Grouped links, merged feed, mall list | Server de-duplication; no mall map · DXD-13 | Exact (HTML) | Not needed |

The eight PRD §5 caveats are each visible on a card. They still need named exposing rows in the seed manifest (MET-04).

## Canonical figures and cross-phase discrepancies

These are the snapshot values every phase must show for dataset sd-2026.10.20-01 at as\_of 20 Oct 2026. All of them were recomputed from the prototype data and then searched for across the 31 boards; no board now contradicts them.

| KPI and scope | Canonical value | Where shown |
| --- | --- | --- |
| Pending approvals, all regions | 232 pending; 92 waiting 31+ days | DX2, DX6 |
| Pending approvals, Central | 130 pending; 62 waiting 31+ days | DX2, DX4, DX6 |
| Pending approvals, Rawdah Point Mall | 71 pending (32 proposals, 23 contracts, 16 leases); 41 waiting 31+ days (19, 15, 7) = 66.1% of Central, 57.7% of its own pending | DX1, DX2, DX4, DX6 |
| Pending amendments, Central | 25 in 4 wk+ (all types); renewals 18 (Rawdah 9, Sandstone 6, Qasr 3); oldest Rawdah renewal 171 days | DX2, DX3, DX4, DX5, DX6 |
| Unit discrepancy, September | 18 of 25 malls reported; 87 mismatched of 3,000 checked (2.9%); Gulf Gate 11 of 142 (7.7%) | DX2, DX4, DX6 |
| Vacancy | Central 408 of 3,420 units (11.9%); all regions 1,026 of 8,140 (12.6%); Mirage Commons 58 of 299 (19.4%) | DX2, DX4, DX6 |
| Tenant lease T-31206 | Reported sales January–September 2026 SAR 2,424,000; September SAR 241,800 (+7.5% on September 2025); 2 documents to upload; 0 requests in Action required (the company has 2) | DX2, DX4, DX5, DX6 |

DX4 already reconciled “41” (all types waiting 31+ days) against “32” (proposals of all ages) at Rawdah Point (DXD-34). DX6 refinement 1 found 21 more discrepancies. Thirteen came from the DX1 placeholders, the DX6 v1 scenario data and a DX2 fixture; eight were definition or naming gaps.

| ID | Where | Finding | Resolution |
| --- | --- | --- | --- |
| C1–C3 | DX1 shell insight | “41 of 71” dated 30 Sep (the series shows 32 then); a share (22% → 58%) where DX6 uses a count; “Central median 19%” (recomputed 45.0%, 6 malls under 10 pending) | DX1 now shows the canonical insights; shares need a denominator ≥ 10 |
| C4, C5, C7 | DX1, DX5 sample, DX6 text | “older than 31 days” (the band is ≥ 31); “overdue” implies an SLA that does not exist; “waiting” hides that contracts and leases count from their last change | Label “waiting 31+ days (1m+)”; “overdue” is banned in generated text; age basis stated |
| C6 | DX6 history | V2 approvals are live; a weekly history is a new metric | Three as-of metrics (DXD-80), equal to parity at as\_of |
| C8–C10 | INS-090, INS-101, INS-103 | Rules and dates disagreed with a replay of the declared history | Regenerated by the detector replay (DXD-82) |
| C11 | Renewal history | The fixed DX4 record ages need 6 resolved renewals in the window at Rawdah | Required seed cohort |
| C12 | S6 / T-201 | “No prior-year data” is false; the dip is seasonal | No insight (N9); confirm GDQ-04 |
| C13 | S7 / T-202 | Company-wide count used for one lease | Lease-scoped action items (DXD-93) |
| C14–C16 | INS-104, INS-107 | False “no lease-expiry data” hypothesis; run id mismatch; “no earlier history” limitation | Corrected texts and versions |
| C17–C20 | DR-005, DX6 contract | Calendar mismatch; unnamed coverage thresholds; ambiguous D4; strict D6 | DXD-75, 89 |
| C21 | DX2 drilldown | Random record fixtures | M2 sources records from the seed |

## Synthetic data model, history and golden scenarios

The declared history is now provably consistent with the seeded snapshot. A record-level construction reproduces every DX2 card value by type and band, and every weekly and monthly series used by the detectors. All 51 reconciliation checks pass, and two replays give the same hash.

**Data model decisions carried into DATABASE\_SCHEMA.md**

- One data version, sd-2026.10.20-01, with as\_of 2026-10-20 (Tuesday). Transactional history runs from 2024-01-01 (DR-003, DR-004).
- 3 regions and 25 malls (Central 10, Eastern 7, Western 8). Ages are counted in Asia/Riyadh calendar days.
- Business data is read-only in schema core. Application state lives in agent and insights. Scenario manifests live in seed\_meta, which the agent role cannot read.
- Detector inputs carry ingested\_at, so checkpoints read only what was known at the time (late September reports arrive on 19 Oct).
- The as-of history comes from the generator’s own lifecycle events, as a snapshot table (GDQ-03 A) or as status history (B).

**Golden-data invariants (DXD-81)**, checked in M1 and M5:

| ID | Invariant | Result today |
| --- | --- | --- |
| GI-01 | Records reproduce every DX2 card value by type and band | 11 of 11 |
| GI-02 | Every declared series ends on the 20 Oct snapshot | 19 of 19 |
| GI-03 | Every series value is reproduced from record lifecycles | 13 of 13 |
| GI-04, GI-07 | Ageing and band boundaries exactly as the V2 SQL (≥ 31 days approvals, ≥ 28 days amendments; contracts and leases from last change) | By construction |
| GI-05 | Region = Σ malls at every checkpoint (Central 61 on 13 Oct, 62 on 20 Oct) | Pass |
| GI-06 | Shares use one checkpoint; denominator ≥ 10 | Pass |
| GI-09 | Tenant-audience facts come from the tenant’s lease only | Pass |
| GI-10 | A “no baseline” claim must be true of the dataset | Pass |
| GI-11 | Rows are visible only to checkpoints after ingestion | Pass |
| GI-12 | Replaying all detectors produces exactly the declared 42 candidates | Pass |
| GI-13 | Two replays are byte-identical | Pass |
| GI-14 | Every number in an insight equals its series value at its labelled checkpoint (43 texts) | Pass |
| GI-15, GI-16 | Vacancy and coverage totals add up (408 of 3,420; 18 + 7 = 25) | Pass |

**Seed requirements found by the reconstruction:** Rawdah Point needs 15 pending approvals aged ≥ 122 days and 6 renewal amendments that reached 4 wk+ and were resolved in the window. Qasr Plaza needs 7 approvals resolved in the window, and Sandstone needs 7 resolved renewals. These cohorts go into the golden scenario manifest.

**Golden scenarios:** S1–S9 must produce their insights with the stated versions, bands and audiences. N1–N11 must produce no notification and log the stated decision. The DX6 Scenarios board holds the full list. The eleven TA §5.3 scenarios (for example approval\_backlog\_mall\_a, future\_dated\_amendment, tenant\_scope\_boundary) still need mapping onto these cases in SYNTHETIC\_DATA\_STRATEGY.md.
